from apps.places.services.location_normalization import detect_commune_from_address

tests = [
    "Av. Américo Vespucio 271, 9061087 Pudahuel, Santiago, Región Metropolitana, Chile",
    "Av Colón Sur 899, 8070937 San Bernardo, Santiago, Región Metropolitana, Chile",
    "Av. José Pedro Alessandri 1799, Ñuñoa, Santiago",
    "Av. 3 Pte. 184, Maipú, Santiago",
    "C. Portal la Hacienda 6215, Peñalolén, Santiago",
    "Portugal 48, Santiago",
    "Santiago, Región Metropolitana",
    "Santiago Metropolitan Region, Chile",
    "Av. Providencia 1234, Santiago Metropolitan Region, Chile"
]

for t in tests:
    print(f"Address: {t}")
    print(f"Result: {detect_commune_from_address(t)}")
    print("-")
