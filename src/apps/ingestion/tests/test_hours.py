from datetime import datetime

from django.test import SimpleTestCase

from apps.places.services.hours import (
    is_schedule_open_now,
    normalize_google_opening_hours,
)


class NormalizeGoogleOpeningHoursTests(SimpleTestCase):
    def test_returns_empty_schedule_when_no_data(self):
        result = normalize_google_opening_hours(None)
        assert result["monday"] == []
        assert result["sunday"] == []

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


class IsScheduleOpenNowTests(SimpleTestCase):
    def test_open_now_inside_range(self):
        schedule = {
            "monday": [{"open": "09:00", "close": "18:00"}],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": [],
        }

        dt = datetime(2026, 4, 13, 10, 30)  # lunes
        assert is_schedule_open_now(schedule, tz_name="America/Santiago", dt=dt) is True

    def test_closed_now_outside_range(self):
        schedule = {
            "monday": [{"open": "09:00", "close": "18:00"}],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": [],
        }

        dt = datetime(2026, 4, 13, 20, 0)  # lunes
        assert is_schedule_open_now(schedule, tz_name="America/Santiago", dt=dt) is False