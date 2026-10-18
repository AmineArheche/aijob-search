"""Tests for tools/gmail_alert_reader.py."""

import json
import tempfile
import unittest
from pathlib import Path

from tools.gmail_alert_reader import (
    DEFAULT_LABEL,
    extract_jobs_from_email_html,
    load_seen_jobs,
    merge_jobs,
)


class TestGmailAlertReader(unittest.TestCase):
    def test_extract_jobs_from_email_html(self):
        sample_html = """
        <html>
          <body>
            <h2>Nouvelles alertes emploi</h2>
            <div>
              <a href="https://ma.indeed.com/viewjob?jk=1234567890abcdef&from=ja&utm_source=alert">
                Développeur Python chez Alten Maroc
              </a>
            </div>
            <div>
              <a href="https://www.linkedin.com/jobs/view/987654321/?trackingId=xyz">
                Conseiller Support Technique - Concentrix
              </a>
            </div>
            <div>
              <a href="https://ma.indeed.com/privacy?utm_source=alert">
                Confidentialité et Conditions
              </a>
            </div>
          </body>
        </html>
        """
        jobs = extract_jobs_from_email_html(sample_html, "2026-10-18")
        self.assertEqual(len(jobs), 2)
        
        job1 = jobs[0]
        self.assertIn("Développeur Python", job1["title"])
        self.assertEqual(job1["company"], "Alten Maroc")
        self.assertEqual(job1["url"], "https://ma.indeed.com/viewjob?jk=1234567890abcdef&from=ja")
        
        job2 = jobs[1]
        self.assertIn("Conseiller Support Technique", job2["title"])
        self.assertEqual(job2["company"], "Concentrix")
        self.assertIn("https://www.linkedin.com/jobs/view/987654321/", job2["url"])

    def test_merge_jobs_and_deduplication(self):
        seen_data = {"seen": {}}
        jobs = [
            {
                "title": "Développeur Full Stack",
                "company": "Tech Maroc",
                "url": "https://ma.indeed.com/viewjob?jk=aaa111",
                "posted_date": "2026-10-17",
            },
            {
                "title": "Développeur Full Stack",
                "company": "Tech Maroc",
                "url": "https://ma.indeed.com/viewjob?jk=aaa111",  # duplicate URL
                "posted_date": "2026-10-18",
            },
        ]
        
        added, dups = merge_jobs(seen_data, jobs, "2026-10-18")
        self.assertEqual(added, 1)
        self.assertEqual(dups, 1)
        self.assertEqual(len(seen_data["seen"]), 1)
        
        # Verify schema
        key = list(seen_data["seen"].keys())[0]
        entry = seen_data["seen"][key]
        self.assertEqual(entry["title"], "Développeur Full Stack")
        self.assertEqual(entry["company"], "Tech Maroc")
        self.assertEqual(entry["portal"], "gmail-alerts")
        self.assertEqual(entry["source"], "cli")
        self.assertEqual(entry["status"], "new")

    def test_load_seen_jobs_handles_missing_file(self):
        missing = Path("non_existent_seen_jobs_12345.json")
        loaded = load_seen_jobs(missing)
        self.assertIn("seen", loaded)
        self.assertEqual(loaded["seen"], {})


if __name__ == "__main__":
    unittest.main()
