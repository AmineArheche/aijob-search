#!/usr/bin/env python3
"""
Unit tests for the personalized actualisation and greeting feature for Amine Arheche.
Validates:
1. HTML markup for personal welcome pill, actualiser button, actualiser modal, and footer crest.
2. CSS styling definitions for modal, pulse ring, and crest bar.
3. Client-side app.js logic for Morocco time calculation, audio chime, and keyboard shortcuts.
4. Server.js sync endpoint and candidate profile integration.
"""

import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPersonalActualise(unittest.TestCase):
    """Test suite for personal touch actualisation features."""

    def setUp(self):
        self.index_html_path = REPO_ROOT / 'public' / 'index.html'
        self.styles_css_path = REPO_ROOT / 'public' / 'styles.css'
        self.app_js_path = REPO_ROOT / 'public' / 'app.js'
        self.server_js_path = REPO_ROOT / 'server.js'

        self.assertTrue(self.index_html_path.exists(), "public/index.html must exist")
        self.assertTrue(self.styles_css_path.exists(), "public/styles.css must exist")
        self.assertTrue(self.app_js_path.exists(), "public/app.js must exist")
        self.assertTrue(self.server_js_path.exists(), "server.js must exist")

        self.index_html = self.index_html_path.read_text(encoding='utf-8')
        self.styles_css = self.styles_css_path.read_text(encoding='utf-8')
        self.app_js = self.app_js_path.read_text(encoding='utf-8')
        self.server_js = self.server_js_path.read_text(encoding='utf-8')

    def test_header_greeting_elements_exist(self):
        """Header contains personal greeting pill, text, and Casablanca/Fes clock."""
        self.assertIn('id="headerGreetingPill"', self.index_html)
        self.assertIn('id="headerGreetingText"', self.index_html)
        self.assertIn('id="headerCasablancaClock"', self.index_html)
        self.assertIn('Amine', self.index_html)
        self.assertIn('Fès (GMT+1)', self.index_html)

    def test_actualiser_button_exists(self):
        """Header contains master actualiser action button with icon and keyboard tooltip."""
        self.assertIn('id="btnActualiserPlatform"', self.index_html)
        self.assertIn('id="actualiserIcon"', self.index_html)
        self.assertIn('Actualiser la plateforme', self.index_html)

    def test_actualiser_modal_markup(self):
        """Actualisation modal contains title, Fes time chip, progress fill, integrity list, and console."""
        self.assertIn('id="actualiserModal"', self.index_html)
        self.assertIn('id="modalGreetingTitle"', self.index_html)
        self.assertIn('id="modalCasablancaTime"', self.index_html)
        self.assertIn('id="modalSyncProgressFill"', self.index_html)
        self.assertIn('id="modalSyncBadge"', self.index_html)
        self.assertIn('id="modalConsoleLogs"', self.index_html)
        self.assertIn('CLAUDE.md', self.index_html)
        self.assertIn('job_search_tracker.csv', self.index_html)

    def test_footer_personal_crest_exists(self):
        """Footer includes Amine Arheche personal crest with qualifications and Moroccan flag."""
        self.assertIn('footer-personal-crest-bar', self.index_html)
        self.assertIn('Amine Arheche', self.index_html)
        self.assertIn('ISTA Ifrane', self.index_html)
        self.assertIn('CISCO Python', self.index_html)

    def test_styles_contain_actualiser_and_crest_rules(self):
        """Styles.css contains dedicated classes for the actualiser modal and footer crest."""
        self.assertIn('.actualiser-modal-box', self.styles_css)
        self.assertIn('.actualiser-greeting-card', self.styles_css)
        self.assertIn('.sync-progress-bar', self.styles_css)
        self.assertIn('.sync-progress-fill', self.styles_css)
        self.assertIn('.footer-personal-crest-bar', self.styles_css)
        self.assertIn('personalPulseRing', self.styles_css)

    def test_app_js_greeting_and_actualise_functions(self):
        """App.js contains time calculation, greeting updater, audio chime, and actualiserPlatform."""
        self.assertIn('function getMoroccoTimeInfo()', self.app_js)
        self.assertIn('function updatePersonalGreetingUi', self.app_js)
        self.assertIn('async function actualiserPlatform', self.app_js)
        self.assertIn('function playActualiseChime()', self.app_js)
        self.assertIn("Africa/Casablanca", self.app_js)

    def test_app_js_keyboard_shortcuts(self):
        """App.js binds 'a', 'A', 'r', 'R' keys to actualiserPlatform."""
        self.assertIn("e.key === 'a' || e.key === 'A' || e.key === 'r' || e.key === 'R'", self.app_js)

    def test_server_js_sync_endpoint(self):
        """Server.js contains /api/sync/actualise endpoint and candidate profile helper."""
        self.assertIn('/api/sync/actualise', self.server_js)
        self.assertIn('parseProfile', self.server_js)
        self.assertIn('getPersonalizedGreeting', self.server_js)
        self.assertIn('Africa/Casablanca', self.server_js)


if __name__ == '__main__':
    unittest.main()
