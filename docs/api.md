# API inicial

Base URL: `/api/v1/`

## Healthcheck

- `GET /health/`

## Places

- `GET /places/`
- `GET /places/{slug}/`

### Query params soportados en `GET /places/`

- `category`: slug de categoría
- `subcategory`: slug de subcategoría
- `search`: texto libre sobre nombre, resumen y dirección
- `commune`
- `region`
- `is_open_24_7`
- `is_emergency_service`
- `verified_only`
- `lat`
- `lng`
- `radius_km`

Si se envían `lat` y `lng`, la respuesta anota distancia aproximada en kilómetros. Si además se envía `radius_km`, el queryset se limita a ese radio.

## Lost pets

- `GET /lost-pets/reports/`
- `POST /lost-pets/reports/`

### Payload base para crear un reporte

```json
{
  "pet_name": "Luna",
  "species": "dog",
  "breed": "Mestiza",
  "sex": "female",
  "color_description": "Negra con pecho blanco",
  "distinctive_marks": "Collar rojo",
  "last_seen_at": "2026-03-11T19:30:00-03:00",
  "last_seen_latitude": -33.4489,
  "last_seen_longitude": -70.6693,
  "last_seen_address": "Parque Forestal, Santiago",
  "reporter_name": "Ana Soto",
  "reporter_phone": "+56912345678",
  "reporter_email": "ana@example.com",
  "is_reward_offered": false
}
```
