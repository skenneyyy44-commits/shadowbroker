"""Date input compatibility for the persistent daily store."""
import os
import tempfile
import unittest
from datetime import date, datetime
from unittest.mock import patch

# Loading the package also starts unrelated analytics imports. Exercise this
# dependency-free persistence module in isolation.
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "daily_store_regression", Path(__file__).resolve().parents[1] / "analytics" / "daily_store.py"
)
_store = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _store
_spec.loader.exec_module(_store)
DailySnapshot = _store.DailySnapshot
date_id = _store.date_id
load_daily = _store.load_daily
save_daily = _store.save_daily


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
