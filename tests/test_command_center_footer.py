"""Tests for the interactive Command Center Dashboard footer and telemetry integration.

Validates structural markup, CSS design tokens, JavaScript event handlers,
and backend telemetry endpoints.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "public" / "index.html"
APP_JS = REPO_ROOT / "public" / "app.js"
STYLES_CSS = REPO_ROOT / "public" / "styles.css"
SERVER_JS = REPO_ROOT / "server.js"


class CommandCenterFooterMarkupTests(unittest.TestCase):
    """Verifies public/index.html contains all footer architecture and modals."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_footer_container_exists(self):
        self.assertIn('<footer class="app-footer">', self.html)
        self.assertIn('class="footer-telemetry-strip"', self.html)
        self.assertIn('class="footer-grid"', self.html)
        self.assertIn('class="footer-bottom-bar"', self.html)

    def test_telemetry_strip_elements(self):
        self.assertIn('id="stripMeshStatus"', self.html)
        self.assertIn('id="footerMoroccoClock"', self.html)
        self.assertIn('id="footerUtcClock"', self.html)
        self.assertIn('id="footerUptimeVal"', self.html)
        self.assertIn('id="footerMemoryVal"', self.html)
        self.assertIn('id="btnFooterPaletteTrigger"', self.html)
        self.assertIn('id="btnFooterArchCopy"', self.html)

    def test_brand_and_candidate_chips(self):
        self.assertIn("Amine Arheche", self.html)
        self.assertIn("Aminearheche@gmail.com", self.html)
        self.assertIn("+212 720819047", self.html)
        self.assertIn("DTS Digital Dev", self.html)
        self.assertIn("CISCO Python Certified", self.html)

    def test_navigation_shortcuts_markup(self):
        self.assertIn('class="kbd-tab-hint">1</span>', self.html)
        self.assertIn('class="kbd-tab-hint">6</span>', self.html)
        self.assertIn('class="footer-nav-shortcut-cue"', self.html)

    def test_discovery_skills_mesh_badges(self):
        self.assertIn("badge-rekrute", self.html)
        self.assertIn("badge-moncallcenter", self.html)
        self.assertIn("badge-freehire", self.html)
        self.assertIn("badge-linkedin", self.html)
        self.assertIn("badge-nordic", self.html)
        self.assertIn("HTML Scraper", self.html)
        self.assertIn("REST Aggregator", self.html)

    def test_footer_action_buttons(self):
        self.assertIn('id="btnBackToTop"', self.html)
        self.assertIn('id="btnRefreshHealth"', self.html)
        self.assertIn('id="btnFooterExportCsv"', self.html)
        self.assertIn('id="btnFooterShortcuts"', self.html)

    def test_footer_interactive_modals(self):
        self.assertIn('id="shortcutsModal"', self.html)
        self.assertIn('id="notifyModal"', self.html)
        self.assertIn('id="toastContainer"', self.html)


class CommandCenterFooterScriptTests(unittest.TestCase):
    """Verifies public/app.js implements all footer handlers, timers, and shortcuts."""

    @classmethod
    def setUpClass(cls):
        cls.js = APP_JS.read_text(encoding="utf-8")

    def test_script_contains_footer_functions(self):
        self.assertIn("function initFooterControls()", self.js)
        self.assertIn("function initFooterClocks()", self.js)
        self.assertIn("function fetchFooterTelemetry(", self.js)
        self.assertIn("function initKeyboardShortcuts()", self.js)
        self.assertIn("function initFooterModalsAndActions()", self.js)
        self.assertIn("function showToast(", self.js)

    def test_timezones_configured(self):
        self.assertIn("Africa/Casablanca", self.js)
        self.assertIn("timeZone: 'UTC'", self.js)

    def test_keyboard_shortcuts_mapped(self):
        self.assertIn("'1': 'architecture'", self.js)
        self.assertIn("'6': 'interview'", self.js)
        self.assertIn("e.key === 'k' || e.key === 'K'", self.js)
        self.assertIn("e.key === 't' || e.key === 'T'", self.js)
        self.assertIn("e.key === 'p' || e.key === 'P'", self.js)
        self.assertIn("e.key === '?'", self.js)


class CommandCenterFooterStylesTests(unittest.TestCase):
    """Verifies public/styles.css includes footer design tokens and responsive media queries."""

    @classmethod
    def setUpClass(cls):
        cls.css = STYLES_CSS.read_text(encoding="utf-8")

    def test_css_classes_exist(self):
        self.assertIn(".app-footer", self.css)
        self.assertIn(".footer-telemetry-strip", self.css)
        self.assertIn(".cand-contact-chips", self.css)
        self.assertIn(".cred-badge", self.css)
        self.assertIn(".kbd-tab-hint", self.css)
        self.assertIn(".shortcuts-modal-box", self.css)
        self.assertIn(".toast-container", self.css)
        self.assertIn(".toast-message", self.css)

    def test_responsive_media_queries(self):
        self.assertIn("@media (max-width: 1120px)", self.css)
        self.assertIn("@media (max-width: 720px)", self.css)
        self.assertIn("@media (max-width: 640px)", self.css)


class ServerTelemetryEndpointTests(unittest.TestCase):
    """Verifies server.js implements the required telemetry and download routes."""

    @classmethod
    def setUpClass(cls):
        cls.server = SERVER_JS.read_text(encoding="utf-8")

    def test_status_endpoint_returns_diagnostics(self):
        self.assertIn("pathname === '/api/status'", self.server)
        self.assertIn("uptimeFormatted", self.server)
        self.assertIn("memoryHeapMb", self.server)
        self.assertIn("agentsCount: 7", self.server)

    def test_export_csv_endpoint(self):
        self.assertIn("pathname === '/api/export/csv'", self.server)
        self.assertIn("text/csv; charset=utf-8", self.server)
        self.assertIn('attachment; filename="job_search_tracker.csv"', self.server)

    def test_telemetry_ping_and_notify_endpoints(self):
        self.assertIn("pathname === '/api/telemetry/ping'", self.server)
        self.assertIn("pathname === '/api/notify/test'", self.server)


if __name__ == "__main__":
    unittest.main()
