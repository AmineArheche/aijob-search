import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.sync_tracker import (
    CANONICAL_STATUSES,
    calculate_funnel_stats,
    normalize_key,
    read_tracker_rows,
    sync_applications_with_tracker,
    update_row_status,
    write_tracker_rows,
)


class TestSyncTracker(unittest.TestCase):
    def test_canonical_statuses(self):
        self.assertIn("drafted", CANONICAL_STATUSES)
        self.assertIn("applied", CANONICAL_STATUSES)
        self.assertIn("interview", CANONICAL_STATUSES)
        self.assertIn("offer", CANONICAL_STATUSES)
        self.assertIn("hired", CANONICAL_STATUSES)
        self.assertIn("rejected", CANONICAL_STATUSES)
        self.assertIn("no_response", CANONICAL_STATUSES)
        self.assertIn("offer_declined", CANONICAL_STATUSES)
        self.assertIn("withdrawn", CANONICAL_STATUSES)

    def test_normalize_key(self):
        self.assertEqual(normalize_key("ALTEN MAROC", "Développeur Python"), "altenmaroc_développeurpython")
        self.assertEqual(normalize_key("Alkimiy", "Support N2"), "alkimiy_supportn2")

    def test_funnel_stats_calculation(self):
        sample_rows = [
            {"status": "drafted"},
            {"status": "applied"},
            {"status": "interview"},
            {"status": "offer"},
            {"status": "rejected"},
        ]
        stats = calculate_funnel_stats(sample_rows)
        self.assertEqual(stats["total"], 5)
        self.assertEqual(stats["drafted"], 1)
        self.assertEqual(stats["applied"], 1)
        self.assertEqual(stats["interview"], 1)
        self.assertEqual(stats["offer"], 1)
        self.assertEqual(stats["rejected"], 1)
        # 2 interview/offer out of 4 submitted = 50.0%
        self.assertEqual(stats["conversion_rate"], 50.0)

    def test_update_row_status_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_csv = Path(tmpdir) / "test_tracker.csv"
            initial_rows = [
                {
                    "date": "2026-10-18",
                    "company": "ALTEN MAROC",
                    "sector": "Tech",
                    "role": "Développeur Python IA",
                    "role_type": "full-time",
                    "channel": "portal",
                    "status": "drafted",
                    "contact_person": "HR",
                    "fit_rating": "5",
                    "notes": "Test note",
                    "cv_file": "",
                    "cover_letter_file": "",
                    "source": "rekrute",
                    "deadline": "",
                }
            ]
            with patch("tools.sync_tracker.TRACKER_PATH", test_csv):
                write_tracker_rows(initial_rows)

                # Update with valid status
                ok = update_row_status("ALTEN", "applied", notes="Passed human gate")
                self.assertTrue(ok)
                rows = read_tracker_rows()
                self.assertEqual(rows[0]["status"], "applied")
                self.assertIn("Passed human gate", rows[0]["notes"])

                # Update with invalid status
                with self.assertRaises(ValueError):
                    update_row_status("ALTEN", "invalid_status_xyz")


if __name__ == "__main__":
    unittest.main()
