# Opening Hours Normalization & Open Now Calculation

## Problem
Google Places no entrega `opening_hours` con una forma completamente consistente.

Los problemas principales de este sprint fueron:

- El payload crudo podía venir con `periods` normales de apertura/cierre por día.
- Algunos negocios 24/7 llegaban con un patrón especial: un único bloque con `open` y sin `close`.
- Sin una normalización estable, el sistema no podía calcular de forma confiable si una ficha estaba abierta o cerrada.
- El frontend y la API pública necesitaban una fuente consistente para exponer horarios y badges operativos.

## Solution
La solución se apoyó en dos capas de almacenamiento y un servicio de cálculo:

- `opening_hours_raw`: conserva exactamente el payload entregado por la fuente externa.
- `opening_hours_normalized`: guarda una estructura interna estable, independiente de la forma original de Google.
- `timezone_name`: fija la zona horaria usada para calcular apertura/cierre.

La estrategia de normalización es:

- ignorar `weekday_text` para la lógica,
- no depender de `open_now`,
- transformar `periods` a un esquema de 7 días,
- dividir bloques overnight en dos tramos,
- representar 24/7 como `00:00 -> 23:59` en cada día.

Luego, el cálculo operativo se hace sobre la estructura normalizada y la zona horaria del lugar.

## Edge Cases Covered
- 24/7 con payload Google que omite `close`
- Bloques overnight que cruzan medianoche
- Periods incompletos o con datos inválidos
- Horarios vacíos o ausentes

## Architecture
### `promote_places.py`
La promoción desde staging a `Place` toma el payload crudo de Google, normaliza horarios y persiste:

- horario crudo,
- horario normalizado,
- zona horaria,
- bandera `is_open_24_7`.

También aplica una heurística simple para marcar negocios que efectivamente lucen 24/7.

### `hours.py`
La lógica de horarios vive en un servicio especializado:

- `normalize_google_opening_hours()`
- `is_schedule_open_now()`
- `is_place_open_now()`

Esto evita mezclar parsing, heurísticas y cálculo temporal dentro del command de ingestión o en serializers.

### `Place.is_open_now_at()`
El modelo expone un método pequeño que delega al servicio de horarios.
Así mantenemos una interfaz limpia para API, admin y cualquier lógica futura sin duplicar comportamiento.

## Limitations
- No hay soporte para feriados ni horarios excepcionales.
- No se procesan special hours ni cierres temporales.
- La zona horaria sigue fija al contexto Chile por defecto (`America/Santiago`).

## Next Steps
- Calcular `next_opening_time`
- Detectar `closing_soon`
- Exponer badges frontend más expresivos
- Integrar schema SEO para horarios estructurados
