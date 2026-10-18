import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.push_notifier import (
    dispatch_job_notification,
    format_job_message,
    load_config,
    load_notified_keys,
    save_notified_key,
    scan_and_notify_shortlist,
)


class TestPushNotifier(unittest.TestCase):
    def test_load_config_defaults(self):
        config = load_config()
        self.assertIn("channel", config)
        self.assertIn("min_score", config)
        self.assertIsInstance(config["min_score"], int)

    def test_format_job_message(self):
        job = {
            "title": "Développeur Python IA",
            "company": "ALTEN MAROC",
            "location": "Fes (Maroc)",
            "rank_score": 87,
            "rank_verdict": "Strong Fit",
            "url": "https://example.com/job/123",
            "strengths": ["Python certifié CISCO", "Localisation Fès"],
            "gaps": ["Azure à consolider"],
        }
        title, body = format_job_message(job)
        self.assertIn("ALTEN MAROC", title)
        self.assertIn("87/100", title)
        self.assertIn("Développeur Python IA", body)
        self.assertIn("Points forts", body)
        self.assertIn("Python certifié CISCO", body)
        self.assertIn("Points d'attention", body)
        self.assertIn("https://example.com/job/123", body)

    def test_dispatch_dry_run(self):
        job = {
            "title": "Support N2",
            "company": "ALTEN MAROC",
            "location": "Fes (Maroc)",
            "rank_score": 83,
            "rank_verdict": "Strong Fit",
        }
        res = dispatch_job_notification(job, dry_run=True)
        self.assertTrue(res["success"])
        self.assertIn("DRY RUN", res["message"])
        self.assertEqual(res["score"], 83)

    def test_deduplication_storage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = Path(tmpdir) / "notified.json"
            with patch("tools.push_notifier.NOTIFIED_JOBS_PATH", test_path):
                self.assertEqual(len(load_notified_keys()), 0)
                save_notified_key("job-key-1")
                save_notified_key("job-key-2")
                keys = load_notified_keys()
                self.assertIn("job-key-1", keys)
                self.assertIn("job-key-2", keys)
                self.assertEqual(len(keys), 2)

    @patch("urllib.request.urlopen")
    def test_send_ntfy_mock(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        config = {
            "channel": "ntfy",
            "ntfy_topic": "test_topic",
            "telegram_token": "",
            "telegram_chat_id": "",
            "min_score": 70,
        }
        job = {
            "title": "Agent Réseau",
            "company": "CGI",
            "rank_score": 73,
            "rank_verdict": "Good Fit",
            "url": "https://example.com/job/456",
        }
        res = dispatch_job_notification(job, config=config, dry_run=False)
        self.assertTrue(res["success"])
        self.assertIn("ntfy.sh", res["message"])


if __name__ == "__main__":
    unittest.main()
