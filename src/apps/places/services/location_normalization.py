import ast
import re
from pathlib import Path

from django.utils.text import slugify


def _normalize_text(value: str) -> str:
    return slugify(value or "").replace("-", " ")


def _load_known_communes() -> tuple[dict[str, str], dict[str, str]]:
    constants_path = (
        Path(__file__).resolve().parents[4]
        / "frontend"
        / "src"
        / "lib"
        / "constants"
        / "chile-locations.ts"
    )
    if not constants_path.exists():
        constants_path = (
            Path(__file__).resolve().parents[5]
            / "frontend"
            / "src"
            / "lib"
            / "constants"
            / "chile-locations.ts"
        )
    if not constants_path.exists():
        return {}, {}

    text = constants_path.read_text(encoding="utf-8")
    aliases: dict[str, str] = {}
    commune_to_region: dict[str, str] = {}

    for match in re.finditer(r'region:\s*"(.*?)",\s*communes:\s*\[(.*?)\]', text, re.S):
        region = match.group(1)
        communes = ast.literal_eval(f"[{match.group(2)}]")
        for commune in communes:
            aliases.setdefault(_normalize_text(commune), commune)
            commune_to_region[commune] = region

    return aliases, commune_to_region


REGION_ALIASES: dict[str, str] = {
    "arica y parinacota": "Región de Arica y Parinacota",
    "region de arica y parinacota": "Región de Arica y Parinacota",
    "tarapaca": "Región de Tarapacá",
    "region de tarapaca": "Región de Tarapacá",
    "antofagasta": "Región de Antofagasta",
    "region de antofagasta": "Región de Antofagasta",
    "atacama": "Región de Atacama",
    "region de atacama": "Región de Atacama",
    "coquimbo": "Región de Coquimbo",
    "region de coquimbo": "Región de Coquimbo",
    "valparaiso": "Región de Valparaíso",
    "region de valparaiso": "Región de Valparaíso",
    "region metropolitana": "Región Metropolitana",
    "region metropolitana de santiago": "Región Metropolitana",
    "metropolitana de santiago": "Región Metropolitana",
    "santiago metropolitan region": "Región Metropolitana",
    "metropolitana": "Región Metropolitana",
    "o higgins": "Región del Libertador O'Higgins",
    "ohiggins": "Región del Libertador O'Higgins",
    "libertador o higgins": "Región del Libertador O'Higgins",
    "region del libertador o higgins": "Región del Libertador O'Higgins",
    "region del libertador bernardo o higgins": "Región del Libertador O'Higgins",
    "maule": "Región del Maule",
    "region del maule": "Región del Maule",
    "nuble": "Región de Ñuble",
    "region de nuble": "Región de Ñuble",
    "biobio": "Región del Biobío",
    "region del biobio": "Región del Biobío",
    "la araucania": "Región de La Araucanía",
    "region de la araucania": "Región de La Araucanía",
    "los rios": "Región de Los Ríos",
    "region de los rios": "Región de Los Ríos",
    "los lagos": "Región de Los Lagos",
    "region de los lagos": "Región de Los Lagos",
    "aysen": "Región de Aysén",
    "region de aysen": "Región de Aysén",
    "magallanes": "Región de Magallanes y la Antártica Chilena",
    "magallanes y la antartica chilena": "Región de Magallanes y la Antártica Chilena",
    "region de magallanes": "Región de Magallanes y la Antártica Chilena",
    "region de magallanes y la antartica chilena": "Región de Magallanes y la Antártica Chilena",
}

KNOWN_COMMUNES, COMMUNE_TO_REGION = _load_known_communes()
INVALID_COMMUNE_TOKENS = (
    "avenida",
    "av ",
    "avda",
    "calle",
    "camino",
    "pasaje",
    "ruta",
    "parque",
    "plaza",
    "condominio",
    "edificio",
    "torre",
    "kilometro",
    "km",
    "sector",
)


def normalize_region_name(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    return REGION_ALIASES.get(_normalize_text(raw), raw)


def normalize_commune_name(value: str, expected_region: str = "") -> str:
    raw = (value or "").strip()
    
    raw_no_digits = re.sub(r'\d+', '', raw).strip()
    normalized = _normalize_text(raw_no_digits)
    
    if not raw_no_digits or not normalized or normalized == "chile":
        return ""
    if any(token in normalized for token in INVALID_COMMUNE_TOKENS):
        return ""
        
    canonical = KNOWN_COMMUNES.get(normalized, "")
    if not canonical:
        return ""
        
    if expected_region:
        c_region = COMMUNE_TO_REGION.get(canonical, "")
        if c_region and normalize_region_name(c_region) != normalize_region_name(expected_region):
            return ""
            
    return canonical


def extract_address_component(components: list[dict], kind: str) -> str:
    for comp in components:
        if kind in comp.get("types", []):
            return comp.get("long_name", "")
    return ""


def detect_commune_from_address(address: str, expected_region: str = "") -> tuple[str, str]:
    """
    Intenta inferir comuna y región desde un texto (formatted_address, raw_address).
    """
    tokens = [token.strip() for token in (address or "").split(",") if token.strip()]
    if not tokens:
        return "", ""

    commune = ""
    region = ""

    for token in tokens:
        normalized = _normalize_text(token)
        if not normalized or normalized == "chile":
            continue

        canonical_region = REGION_ALIASES.get(normalized)
        if canonical_region and not region:
            region = canonical_region
            continue

        canonical_commune = normalize_commune_name(token, expected_region)
        if canonical_commune and not commune:
            commune = canonical_commune

    return commune, region


def detect_commune_for_imported_record(record) -> dict:
    google = record.raw_payload.get("google", {})
    meta = record.raw_payload.get("meta", {})
    address_comps = google.get("address_components", [])
    
    expected_region = normalize_region_name(meta.get("region_target", ""))
    if not expected_region:
        expected_region = normalize_region_name(extract_address_component(address_comps, "administrative_area_level_1"))
    
    # 1. Por Address Components
    commune = extract_address_component(address_comps, "locality")
    if commune:
        normalized_c = normalize_commune_name(commune, expected_region)
        if normalized_c:
            return {
                "commune": normalized_c,
                "region": normalize_region_name(extract_address_component(address_comps, "administrative_area_level_1")),
                "source": "google.address_components.locality",
                "confidence": "high",
                "needs_review": False
            }
            
    commune = extract_address_component(address_comps, "administrative_area_level_3")
    if commune:
        normalized_c = normalize_commune_name(commune, expected_region)
        if normalized_c:
            return {
                "commune": normalized_c,
                "region": normalize_region_name(extract_address_component(address_comps, "administrative_area_level_1")),
                "source": "google.address_components.administrative_area_level_3",
                "confidence": "high",
                "needs_review": False
            }
            
    commune = extract_address_component(address_comps, "administrative_area_level_2")
    if commune:
        normalized_c = normalize_commune_name(commune, expected_region)
        if normalized_c:
            return {
                "commune": normalized_c,
                "region": normalize_region_name(extract_address_component(address_comps, "administrative_area_level_1")),
                "source": "google.address_components.administrative_area_level_2",
                "confidence": "high",
                "needs_review": False
            }

    # 2. Por formatted address
    formatted = google.get("formatted_address", "")
    commune, region = detect_commune_from_address(formatted, expected_region)
    if commune:
        return {
            "commune": commune,
            "region": region or normalize_region_name(extract_address_component(address_comps, "administrative_area_level_1")),
            "source": "google.formatted_address",
            "confidence": "high",
            "needs_review": False
        }

    # 3. Por raw address
    raw = record.raw_address
    commune, region = detect_commune_from_address(raw, expected_region)
    if commune:
        return {
            "commune": commune,
            "region": region or normalize_region_name(extract_address_component(address_comps, "administrative_area_level_1")),
            "source": "record.raw_address",
            "confidence": "high",
            "needs_review": False
        }
        
    # 4. Fallback commune_target
    target = meta.get("commune_target", "")
    normalized_target = normalize_commune_name(target, expected_region)
    if normalized_target:
        return {
            "commune": normalized_target,
            "region": normalize_region_name(meta.get("region_target", "")),
            "source": "meta.commune_target_fallback",
            "confidence": "low",
            "needs_review": True
        }
        
    return {
        "commune": "",
        "region": "",
        "source": "not_found",
        "confidence": "none",
        "needs_review": True
    }


def detect_commune_for_place(place) -> dict:
    meta = place.metadata or {}
    expected_region = normalize_region_name(meta.get("region_target", "")) or normalize_region_name(place.region)
    
    # 1. Check formatted address
    commune, region = detect_commune_from_address(place.formatted_address, expected_region)
    if commune:
        return {
            "commune": commune,
            "region": region or place.region,
            "source": "place.formatted_address",
            "confidence": "high",
            "needs_review": False
        }
        
    # 2. Check street_address
    commune, region = detect_commune_from_address(place.street_address, expected_region)
    if commune:
        return {
            "commune": commune,
            "region": region or place.region,
            "source": "place.street_address",
            "confidence": "high",
            "needs_review": False
        }
        
    # 3. Fallback commune_target if exists in metadata
    target = meta.get("commune_target", "")
    normalized_target = normalize_commune_name(target, expected_region)
    if normalized_target:
        return {
            "commune": normalized_target,
            "region": place.region,
            "source": "meta.commune_target_fallback",
            "confidence": "low",
            "needs_review": True
        }
        
    return {
        "commune": place.commune, # Lo actual
        "region": place.region,
        "source": "place.current_commune",
        "confidence": "low",
        "needs_review": True
    }
