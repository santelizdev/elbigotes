import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
from pathlib import Path
import re
import ast

def _load_known_communes():
    constants_path = (
        Path("/Users/delorean/elbigotes")
        / "frontend"
        / "src"
        / "lib"
        / "constants"
        / "chile-locations.ts"
    )
    text = constants_path.read_text(encoding="utf-8")
    aliases: dict[str, str] = {}
    commune_to_region: dict[str, str] = {}

    for match in re.finditer(r'region:\s*"(.*?)",\s*communes:\s*\[(.*?)\]', text, re.S):
        region = match.group(1)
        communes = ast.literal_eval(f"[{match.group(2)}]")
        for commune in communes:
            from django.utils.text import slugify
            aliases.setdefault(slugify(commune).replace("-", " "), commune)
            commune_to_region[commune] = region

    return aliases, commune_to_region

aliases, c2r = _load_known_communes()
print("Aliases:", len(aliases))
print("C2R:", len(c2r))
print("Puente Alto region:", c2r.get("Puente Alto"))
print("Coquimbo region:", c2r.get("Coquimbo"))
