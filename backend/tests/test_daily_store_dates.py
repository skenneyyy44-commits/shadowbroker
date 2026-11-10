"""Date input compatibility for the persistent daily store."""
import os
import tempfile
import unittest
from datetime import date, datetime
from unittest.mock import patch

from analytics.daily_store import DailySnapshot, date_id, load_daily, save_daily


class DailyStoreDateTests(unittest.TestCase):
    def test_date_datetime_and_string_load_the_same_snapshot(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"GT_DAILY_STORE_DIR": directory}):
            save_daily(DailySnapshot(date="2026-11-10", last_updated_at="saved"))
            for value in ("2026-11-10", date(2026, 11, 10), datetime(2026, 11, 10, 18, 30)):
                with self.subTest(value=value):
                    self.assertEqual(date_id(value), "2026-11-10")
                    self.assertEqual(load_daily(value).last_updated_at, "saved")
            self.assertIsNone(load_daily("2026-11-09"))

    def test_invalid_dates_are_rejected_before_file_access(self):
        for value in ("2026-02-30", "../secret", "not-a-date"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                load_daily(value)


if __name__ == "__main__":
    unittest.main()
