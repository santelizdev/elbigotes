from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase

from apps.places.models import Place
from apps.places.services.hours import (
    build_empty_schedule,
    is_place_open_now,
    is_schedule_open_now,
    normalize_google_opening_hours,
)


class NormalizeGoogleOpeningHoursTests(SimpleTestCase):
    def test_returns_full_empty_schedule_when_no_data(self):
        result = normalize_google_opening_hours(None)

        assert result == build_empty_schedule()

    def test_normalizes_simple_same_day_period(self):
        opening_hours = {
            "periods": [
                {
                    "open": {"day": 1, "time": "0900"},
                    "close": {"day": 1, "time": "1800"},
                }
            ]
        }

        result = normalize_google_opening_hours(opening_hours)

        assert result["monday"] == [{"open": "09:00", "close": "18:00"}]
        assert result["tuesday"] == []
        assert set(result.keys()) == {
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        }

    def test_splits_overnight_period(self):
        opening_hours = {
            "periods": [
                {
                    "open": {"day": 1, "time": "2200"},
                    "close": {"day": 2, "time": "0200"},
                }
            ]
        }

        result = normalize_google_opening_hours(opening_hours)

        assert result["monday"] == [{"open": "22:00", "close": "23:59"}]
        assert result["tuesday"] == [{"open": "00:00", "close": "02:00"}]

    def test_normalizes_google_24_7_period_without_close(self):
        opening_hours = {
            "periods": [
                {
                    "open": {"day": 0, "time": "0000"},
                }
            ],
            "open_now": True,
            "weekday_text": ["Abierto las 24 horas"],
        }

        result = normalize_google_opening_hours(opening_hours)

        for day in (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ):
            assert result[day] == [{"open": "00:00", "close": "23:59"}]

    def test_skips_invalid_periods_without_crashing(self):
        opening_hours = {
            "periods": [
                None,
                {},
                {"open": {"day": 1}},
                {"open": {"day": 1, "time": "0900"}, "close": {"day": 1, "time": "bad"}},
                {"open": {"day": 1, "time": "1000"}, "close": {"day": 1, "time": "1200"}},
            ]
        }

        result = normalize_google_opening_hours(opening_hours)

        assert result["monday"] == [{"open": "10:00", "close": "12:00"}]
        assert result["tuesday"] == []


class IsScheduleOpenNowTests(SimpleTestCase):
    def test_empty_schedule_returns_false(self):
        assert is_schedule_open_now({}, tz_name="America/Santiago") is False

    def test_open_now_inside_same_day_range(self):
        schedule = {
            **build_empty_schedule(),
            "monday": [{"open": "09:00", "close": "18:00"}],
        }

        dt = datetime(2026, 4, 13, 10, 30)
        assert is_schedule_open_now(schedule, tz_name="America/Santiago", dt=dt) is True

    def test_closed_now_outside_same_day_range(self):
        schedule = {
            **build_empty_schedule(),
            "monday": [{"open": "09:00", "close": "18:00"}],
        }

        dt = datetime(2026, 4, 13, 20, 0)
        assert is_schedule_open_now(schedule, tz_name="America/Santiago", dt=dt) is False

    def test_open_now_for_overnight_split_schedule(self):
        schedule = {
            **build_empty_schedule(),
            "monday": [{"open": "22:00", "close": "23:59"}],
            "tuesday": [{"open": "00:00", "close": "02:00"}],
        }

        dt = datetime(2026, 4, 14, 1, 30)
        assert is_schedule_open_now(schedule, tz_name="America/Santiago", dt=dt) is True

    def test_respects_timezone_name_when_datetime_is_aware(self):
        dt_utc = datetime(2026, 1, 15, 15, 0, tzinfo=ZoneInfo("UTC"))
        local_dt = dt_utc.astimezone(ZoneInfo("America/Santiago"))
        local_day = local_dt.strftime("%A").lower()
        schedule = build_empty_schedule()
        schedule[local_day] = [
            {
                "open": local_dt.strftime("%H:%M"),
                "close": (local_dt.replace(minute=min(local_dt.minute + 5, 59))).strftime("%H:%M"),
            }
        ]

        assert is_schedule_open_now(schedule, tz_name="America/Santiago", dt=dt_utc) is True
        assert is_schedule_open_now(schedule, tz_name="UTC", dt=dt_utc) is False


class IsPlaceOpenNowTests(SimpleTestCase):
    def test_place_open_now_returns_true_for_24_7_flag(self):
        place = Place(
            name="Siempre Abierto",
            slug="siempre-abierto",
            is_open_24_7=True,
            opening_hours_normalized={},
            timezone_name="America/Santiago",
        )

        assert is_place_open_now(place) is True

    def test_place_open_now_returns_true_for_normalized_24_7_schedule(self):
        place = Place(
            name="Google 24 7",
            slug="google-24-7",
            is_open_24_7=False,
            opening_hours_normalized=normalize_google_opening_hours(
                {"periods": [{"open": {"day": 0, "time": "0000"}}]}
            ),
            timezone_name="America/Santiago",
        )

        dt = datetime(2026, 4, 13, 12, 0)
        assert is_place_open_now(place, dt=dt) is True
        assert place.is_open_now_at(dt=dt) is True

    def test_place_open_now_returns_false_with_empty_schedule(self):
        place = Place(
            name="Sin Horario",
            slug="sin-horario",
            is_open_24_7=False,
            opening_hours_normalized={},
            timezone_name="America/Santiago",
        )

        dt = datetime(2026, 4, 13, 12, 0)
        assert is_place_open_now(place, dt=dt) is False
        assert place.is_open_now_at(dt=dt) is False
