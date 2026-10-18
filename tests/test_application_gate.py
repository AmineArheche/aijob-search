import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.application_gate import (
    generate_form_fields_text,
    record_human_approval,
    sanitize_token,
)


class TestApplicationGate(unittest.TestCase):
    def test_sanitize_token(self):
        self.assertEqual(sanitize_token("ALTEN MAROC"), "alten_maroc")
        self.assertEqual(sanitize_token("Développeur Python IA"), "développeur_python_ia")

    def test_form_fields_content(self):
        text = generate_form_fields_text("Développeur Python IA", "ALTEN MAROC", "Fès")
        self.assertIn("ALTEN MAROC", text)
        self.assertIn("Amine Arheche", text)
        self.assertIn("Aminearheche@gmail.com", text)
        self.assertIn("+212 720819047", text)
        self.assertIn("ISTA Ifrane", text)
        self.assertIn("Python Essentials", text)
        self.assertIn("NOTE TO SELF", text)

    def test_human_approval_recording(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_log_path = Path(tmpdir) / "app_log.json"
            initial_data = {
                "applications": {
                    "alten_test": {
                        "company": "ALTEN",
                        "status": "READY_FOR_HUMAN_APPROVAL",
                        "human_decision": "PENDING",
                    }
                }
            }
            test_log_path.write_text(json.dumps(initial_data), encoding="utf-8")

            with patch("tools.application_gate.APPLICATIONS_LOG_PATH", test_log_path):
                # Approve
                ok = record_human_approval("alten_test", approved=True, notes="Looks perfect")
                self.assertTrue(ok)
                data = json.loads(test_log_path.read_text(encoding="utf-8"))
                self.assertEqual(data["applications"]["alten_test"]["human_decision"], "APPROVED")
                self.assertEqual(data["applications"]["alten_test"]["status"], "APPROVED_BY_USER")
                self.assertEqual(data["applications"]["alten_test"]["notes"], "Looks perfect")

                # Reject unknown app
                self.assertFalse(record_human_approval("unknown_app", approved=False))


if __name__ == "__main__":
    unittest.main()
