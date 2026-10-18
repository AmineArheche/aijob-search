import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.gemini_drafter import (
    check_anti_hallucination,
    draft_application,
    generate_cover_latex,
    generate_cv_latex,
    sanitize_filename_token,
)
from tools.verify_pdf import verify_pdf


class TestGeminiDrafter(unittest.TestCase):
    def test_sanitize_filename_token(self):
        self.assertEqual(sanitize_filename_token("ALTEN MAROC"), "alten_maroc")
        self.assertEqual(
            sanitize_filename_token("Développeur Python IA"),
            "développeur_python_ia",
        )
        self.assertEqual(
            sanitize_filename_token("Support N2 - Casablanca / Remote"),
            "support_n2_casablanca_remote",
        )

    def test_anti_hallucination_rules(self):
        # Clean text
        ok, issues = check_anti_hallucination("J'apporte une solide expérience en Python.")
        self.assertTrue(ok)
        self.assertEqual(len(issues), 0)

        # Banned em-dash
        ok, issues = check_anti_hallucination("Expérience professionnelle — Développeur")
        self.assertFalse(ok)
        self.assertTrue(any("em-dash" in i for i in issues))

        # Forbidden cliche
        ok, issues = check_anti_hallucination("I believe I am a great fit for your team.")
        self.assertFalse(ok)
        self.assertTrue(any("great fit" in i for i in issues))

    def test_cv_latex_generation(self):
        latex = generate_cv_latex("Développeur Python IA", "ALTEN MAROC")
        self.assertIn("Amine", latex)
        self.assertIn("Arheche", latex)
        self.assertIn("moderncv", latex)
        self.assertIn("banking", latex)
        self.assertIn("ISTA Ifrane", latex)
        self.assertIn("CISCO", latex)
        self.assertIn("Concentrix", latex)
        # Verify no em-dash
        self.assertNotIn("—", latex)

    def test_cover_latex_generation(self):
        latex = generate_cover_latex("Développeur Python IA", "ALTEN MAROC")
        self.assertIn("Amine Arheche", latex)
        self.assertIn("ALTEN MAROC", latex)
        self.assertIn("documentclass[]{cover}", latex)
        self.assertIn("Aminearheche@gmail.com", latex)
        self.assertNotIn("—", latex)

    def test_end_to_end_generation_and_pdf_verification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_cv_pdf = Path(tmpdir) / "test_cv.pdf"
            tmp_cover_pdf = Path(tmpdir) / "test_cover.pdf"

            from tools.gemini_drafter import generate_cv_pdf_reportlab, generate_cover_pdf_reportlab

            generate_cv_pdf_reportlab(tmp_cv_pdf, "Développeur Python IA", "ALTEN MAROC")
            generate_cover_pdf_reportlab(tmp_cover_pdf, "Développeur Python IA", "ALTEN MAROC")

            self.assertTrue(tmp_cv_pdf.is_file())
            self.assertTrue(tmp_cover_pdf.is_file())

            # Verify CV PDF: exactly 2 pages, ascii dates
            extractor_cv, text_cv, pages_cv = verify_pdf(tmp_cv_pdf, expected_pages=2, ascii_dates=True, min_chars=100)
            self.assertEqual(pages_cv, 2)
            self.assertIn("Amine Arheche", text_cv)
            self.assertIn("Python", text_cv)

            # Verify Cover PDF: exactly 1 page, ascii dates
            extractor_cov, text_cov, pages_cov = verify_pdf(tmp_cover_pdf, expected_pages=1, ascii_dates=True, min_chars=100)
            self.assertEqual(pages_cov, 1)
            self.assertIn("Amine Arheche", text_cov)
            self.assertIn("ALTEN MAROC", text_cov)


if __name__ == "__main__":
    unittest.main()
