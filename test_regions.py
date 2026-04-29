from apps.places.services.location_normalization import detect_commune_from_address

tests = [
    "Plaza de Armas, Puente Alto, Coquimbo, Chile", # If region is RM, should ignore Coquimbo and take Puente Alto
    "Calle La Florida 123, Antofagasta, Chile", # If region is RM, should ignore Antofagasta and take La Florida
    "Av. José Pedro Alessandri 1799, Ñuñoa, Santiago", # Should detect Ñuñoa
    "Calle Curicó 123, Santiago", # Should detect Santiago (Curicó is Maule)
    "Calle Pozo Almonte, Santiago", # Should detect Santiago
]

print("With expected_region = Región Metropolitana")
for t in tests:
    print(f"Address: {t}")
    print(f"Result: {detect_commune_from_address(t, 'Región Metropolitana')}")
    print("-")

print("Without expected_region")
for t in tests:
    print(f"Address: {t}")
    print(f"Result: {detect_commune_from_address(t)}")
    print("-")
