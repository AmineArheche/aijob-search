"""Unit and integration tests for Home Command Center Dashboard architecture.

Verifies structural markup in public/index.html, style definitions in public/styles.css,
client-side logic in public/app.js, and backend endpoints in server.js.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "public" / "index.html"
APP_JS = REPO_ROOT / "public" / "app.js"
STYLES_CSS = REPO_ROOT / "public" / "styles.css"
SERVER_JS = REPO_ROOT / "server.js"


class HomeCommandCenterMarkupTests(unittest.TestCase):
    """Verifies public/index.html contains all Home Command Center components."""

    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8")

    def test_nav_tab_home_exists_and_active(self):
        self.assertIn('data-tab="home"', self.html)
        self.assertIn('id="tabNavHome"', self.html)
        self.assertIn('Command Center', self.html)
        self.assertIn('pulse-dot-badge', self.html)

    def test_hero_banner_markup(self):
        self.assertIn('class="home-hero-banner"', self.html)
        self.assertIn('class="hero-ambient-glow"', self.html)
        self.assertIn('Amine Arheche', self.html)
        self.assertIn('Fès, Morocco & Remote EU/Global', self.html)
        self.assertIn('hero-main-title', self.html)
        self.assertIn('hero-gradient-text', self.html)
        self.assertIn('id="heroAgentsCount"', self.html)
        self.assertIn('id="heroPortalsCount"', self.html)

    def test_agent_mesh_radar_markup(self):
        self.assertIn('class="agent-mesh-radar-panel"', self.html)
        self.assertIn('class="radar-beacon-dot"', self.html)
        self.assertIn('id="radarMeshSummary"', self.html)
        self.assertIn('id="radarAvgLatency"', self.html)
        self.assertIn('id="btnPingAgentMesh"', self.html)
        self.assertIn('AGENT-01', self.html)
        self.assertIn('AGENT-07', self.html)

    def test_kpi_cards_markup(self):
        self.assertIn('class="home-metrics-grid"', self.html)
        self.assertIn('id="kpiPipelineTotal"', self.html)
        self.assertIn('id="kpiGatePassRate"', self.html)
        self.assertIn('id="kpiPortalsActive"', self.html)
        self.assertIn('id="kpiAtsParseRate"', self.html)

    def test_quick_action_hub_markup(self):
        self.assertIn('class="home-quick-actions-panel"', self.html)
        self.assertIn("triggerQuickAction('scrape-casablanca')", self.html)
        self.assertIn("triggerQuickAction('scrape-remote')", self.html)
        self.assertIn("triggerQuickAction('evaluate-sample')", self.html)
        self.assertIn("triggerQuickAction('draft-latex')", self.html)
        self.assertIn("triggerQuickAction('start-interview')", self.html)
        self.assertIn("triggerQuickAction('export-csv')", self.html)

    def test_event_stream_markup(self):
        self.assertIn('class="home-activity-stream-panel"', self.html)
        self.assertIn('id="activityFilterPills"', self.html)
        self.assertIn('id="btnSimulatePipeline"', self.html)
        self.assertIn('id="activityStreamTimeline"', self.html)

    def test_salary_radar_markup(self):
        self.assertIn('class="home-salary-radar-panel"', self.html)
        self.assertIn('id="salaryRegionToggles"', self.html)
        self.assertIn('id="salaryRoleSelect"', self.html)
        self.assertIn('id="salarySeniorityRange"', self.html)
        self.assertIn('id="salaryMedianAmount"', self.html)

    def test_spotlight_markup(self):
        self.assertIn('class="home-spotlight-panel"', self.html)
        self.assertIn('class="spotlight-cards-grid"', self.html)
        self.assertIn('loadJobToEvaluator', self.html)

    def test_thin_pointer_markup(self):
        self.assertIn('class="home-thin-pointer-panel"', self.html)
        self.assertIn('Thin-Pointer Architecture', self.html)
        self.assertIn('CLAUDE.md', self.html)
        self.assertIn('.claude/skills/', self.html)
        self.assertIn('.agents/skills/', self.html)


class HomeCommandCenterStyleTests(unittest.TestCase):
    """Verifies public/styles.css contains required styling rules."""

    @classmethod
    def setUpClass(cls):
        cls.css = STYLES_CSS.read_text(encoding="utf-8")

    def test_hero_and_radar_styles(self):
        self.assertIn('.home-hero-banner', self.css)
        self.assertIn('.hero-ambient-glow', self.css)
        self.assertIn('.agent-mesh-radar-panel', self.css)
        self.assertIn('.radar-beacon-dot', self.css)
        self.assertIn('@keyframes radarBeacon', self.css)

    def test_kpi_and_action_styles(self):
        self.assertIn('.home-metrics-grid', self.css)
        self.assertIn('.home-kpi-card', self.css)
        self.assertIn('.home-quick-actions-panel', self.css)
        self.assertIn('.quick-action-tile', self.css)

    def test_salary_and_spotlight_styles(self):
        self.assertIn('.home-salary-radar-panel', self.css)
        self.assertIn('.salary-progress-track', self.css)
        self.assertIn('.salary-marker', self.css)
        self.assertIn('.home-spotlight-panel', self.css)
        self.assertIn('.spotlight-job-card', self.css)


class HomeCommandCenterLogicTests(unittest.TestCase):
    """Verifies public/app.js and server.js logic."""

    @classmethod
    def setUpClass(cls):
        cls.app_js = APP_JS.read_text(encoding="utf-8")
        cls.server_js = SERVER_JS.read_text(encoding="utf-8")

    def test_app_js_home_state_and_functions(self):
        self.assertIn("currentTab: 'home'", self.app_js)
        self.assertIn("initHomeCommandCenter", self.app_js)
        self.assertIn("bindAgentRadarEvents", self.app_js)
        self.assertIn("initSalaryRadarCalculator", self.app_js)
        self.assertIn("triggerQuickAction", self.app_js)
        self.assertIn("loadJobToEvaluator", self.app_js)
        self.assertIn("'0': 'home'", self.app_js)
        self.assertIn("'h': 'home'", self.app_js)

    def test_server_js_overview_and_salary_endpoints(self):
        self.assertIn("pathname === '/api/home/overview'", self.server_js)
        self.assertIn("pathname === '/api/events/recent'", self.server_js)
        self.assertIn("pathname === '/api/market/salaries'", self.server_js)


if __name__ == '__main__':
    unittest.main()
