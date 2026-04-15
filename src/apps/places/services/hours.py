from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from django.utils import timezone


DAY_NAMES = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

GOOGLE_DAY_INDEX_TO_NAME = {
    0: "sunday",
    1: "monday",
    2: "tuesday",
    3: "wednesday",
    4: "thursday",
    5: "friday",
    6: "saturday",
}


def build_empty_schedule() -> dict:
    """
    Retorna una estructura de horario vacía y consistente.
    """
    return {day: [] for day in DAY_NAMES}


def build_all_day_schedule() -> dict:
    """
    Retorna una estructura 24/7 explícita para los siete días.

    Usamos 23:59 como cierre para representar "todo el día" sin depender
    de horas especiales como 24:00, que no siempre son cómodas de parsear
    ni consistentes entre fuentes.
    """
    return {
        day: [{"open": "00:00", "close": "23:59"}]
        for day in DAY_NAMES
    }


def normalize_hhmm(value: str | None) -> str | None:
    """
    Convierte strings tipo '0900' de Google a '09:00'.

    Si el valor no es válido, retorna None.
    """
    if not value or len(value) != 4 or not value.isdigit():
        return None
    return f"{value[:2]}:{value[2:]}"


def normalize_google_opening_hours(opening_hours: dict | None) -> dict:
    """
    Normaliza opening_hours de Google Places a un formato interno estable.

    Formato de salida:
    {
        "monday": [{"open": "09:00", "close": "18:00"}],
        "tuesday": [],
        ...
    }

    Consideraciones:
    - Google suele traer periods con open.day/open.time y close.day/close.time.
    - Si una franja cruza medianoche, se divide en dos:
      lunes 22:00 -> martes 02:00 se convierte en:
      monday: 22:00-23:59
      tuesday: 00:00-02:00
    - Si el lugar es 24/7 y la fuente no trae close convencional, intentamos
      representar el día como 00:00-23:59 para todos los días.
    """
    schedule = build_empty_schedule()

    if not isinstance(opening_hours, dict) or not opening_hours:
        return schedule

    periods = opening_hours.get("periods") or []
    if not isinstance(periods, list) or not periods:
        return schedule

    # Google a veces representa negocios 24/7 con un único período que trae
    # solo "open" y omite "close". Si no tratamos este caso explícitamente,
    # la normalización queda vacía y todo el cálculo posterior falla.
    if len(periods) == 1:
        first_period = periods[0] if isinstance(periods[0], dict) else {}
        open_info = first_period.get("open") if isinstance(first_period, dict) else None
        close_info = first_period.get("close") if isinstance(first_period, dict) else None
        if isinstance(open_info, dict) and not close_info:
            return build_all_day_schedule()

    for period in periods:
        if not isinstance(period, dict):
            continue

        open_info = period.get("open") if isinstance(period.get("open"), dict) else {}
        close_info = period.get("close") if isinstance(period.get("close"), dict) else {}

        open_day_idx = open_info.get("day")
        open_time_raw = open_info.get("time")
        close_day_idx = close_info.get("day")
        close_time_raw = close_info.get("time")

        open_day = GOOGLE_DAY_INDEX_TO_NAME.get(open_day_idx)
        close_day = GOOGLE_DAY_INDEX_TO_NAME.get(close_day_idx)
        open_time = normalize_hhmm(open_time_raw)
        close_time = normalize_hhmm(close_time_raw)

        # Caso defensivo: si falta información crítica, omitir la franja.
        if not open_day or not open_time:
            continue

        # Si no hay cierre no intentamos inventar una franja. El único caso
        # donde sí construimos 24/7 es el patrón especial manejado arriba.
        if not close_day or not close_time:
            continue

        # Mismo día: franja simple
        if open_day == close_day:
            # Si Google devuelve 00:00 a 00:00 en mismo día, eso no es útil.
            # Lo tratamos como franja inválida salvo que quieras una regla distinta.
            if open_time != close_time:
                schedule[open_day].append({
                    "open": open_time,
                    "close": close_time,
                })
            continue

        # Cruce de medianoche o cambio de día:
        # dividimos la franja en dos bloques.
        schedule[open_day].append({
            "open": open_time,
            "close": "23:59",
        })
        schedule[close_day].append({
            "open": "00:00",
            "close": close_time,
        })

    # Ordenar bloques por hora de apertura para consistencia.
    for day in DAY_NAMES:
        blocks = [
            block
            for block in schedule.get(day, [])
            if isinstance(block, dict) and block.get("open") and block.get("close")
        ]
        schedule[day] = sorted(blocks, key=lambda block: block["open"])

    return schedule


def parse_hhmm_to_time(value: str) -> time | None:
    """
    Convierte 'HH:MM' a datetime.time.

    Si el valor es inválido, retorna None para que los consumidores puedan
    omitir el bloque sin reventar el cálculo completo.
    """
    if not isinstance(value, str) or ":" not in value:
        return None

    try:
        hour, minute = value.split(":")
        parsed = time(hour=int(hour), minute=int(minute))
    except (TypeError, ValueError):
        return None

    return parsed


def get_local_now(tz_name: str = "America/Santiago", dt: datetime | None = None) -> datetime:
    """
    Retorna datetime aware en la zona horaria indicada.
    Si dt es None, usa timezone.now().
    Si dt viene naive, se asume que ya está en la tz dada.
    """
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("America/Santiago")

    if dt is None:
        return timezone.now().astimezone(tz)

    if timezone.is_naive(dt):
        return dt.replace(tzinfo=tz)

    return dt.astimezone(tz)


def is_schedule_open_now(
    normalized_schedule: dict | None,
    tz_name: str = "America/Santiago",
    dt: datetime | None = None,
) -> bool:
    """
    Evalúa si un horario normalizado está abierto en el instante dado.
    """
    if not isinstance(normalized_schedule, dict) or not normalized_schedule:
        return False

    local_now = get_local_now(tz_name=tz_name, dt=dt)
    day_name = DAY_NAMES[local_now.weekday()]
    current_time = local_now.time()

    blocks = normalized_schedule.get(day_name, [])
    if not isinstance(blocks, list) or not blocks:
        return False

    for block in blocks:
        if not isinstance(block, dict):
            continue

        open_value = block.get("open")
        close_value = block.get("close")
        if not open_value or not close_value:
            continue

        open_time = parse_hhmm_to_time(open_value)
        close_time = parse_hhmm_to_time(close_value)
        if open_time is None or close_time is None:
            continue

        if open_time <= current_time <= close_time:
            return True

    return False


def is_place_open_now(place, dt: datetime | None = None) -> bool:
    """
    Calcula si un Place está abierto ahora.

    Prioridades:
    - Si is_open_24_7 = True, retorna True.
    - Si hay horario normalizado, lo evalúa.
    - Si no hay horario, retorna False.
    """
    if getattr(place, "is_open_24_7", False):
        return True

    schedule = getattr(place, "opening_hours_normalized", None) or {}
    tz_name = getattr(place, "timezone_name", "America/Santiago") or "America/Santiago"

    return is_schedule_open_now(schedule, tz_name=tz_name, dt=dt)
