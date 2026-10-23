# 🦅 AI Job Search - Multi-Agent Architecture & Operations Dashboard

An interactive web-based command center and multi-agent operations dashboard for the [AI Job Search](https://github.com/MadsLorentzen/ai-job-search) framework.

Built with modern vanilla technologies, sleek glassmorphism, real-time REST APIs, and dynamic pipeline controls.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Node.js**: v18.0.0 or newer (v22+ recommended)
- **Python**: 3.10+ (for background tooling and verification scripts)

### 2. Launch the Dashboard
Run either of the following commands in the project root:

```bash
# Using npm start
npm start

# Or using dev mode
npm run dev
```

### 3. Open in Browser
Visit your local dashboard instance at:
👉 **[http://localhost:3010](http://localhost:3010)**

*(If port 3010 is occupied, the server automatically finds the next available port: 3011, 3012, etc.)*

---

## 🏛️ System Architecture & Integrated Agents

The dashboard exposes and visualizes the 7 core autonomous agents operating within this repository:

```
[Candidate Profiler] ──▶ [Portal Scrapers] ──▶ [Fit Evaluator] ──▶ [Tailored Drafter]
     (/setup)                  (/scrape)              (04-job-eval)          (/apply)
                                                                            │
[Funnel Tracker]   ◀── [Interview Coach]  ◀── [ATS Reviewer]    ◀───────────┘
 (/html-report)            (/interview)           (verify_pdf)
```

| Agent | Command / Spec | Purpose & Capabilities |
| :--- | :--- | :--- |
| **1. Candidate Profiler** | `/setup` & `CLAUDE.md` | Establishes ground-truth identity, skills taxonomy, career priorities, and hard dealbreakers. |
| **2. Portal Scrapers** | `/scrape` & `.agents/skills/` | Aggregates live jobs across 6 search skills: LinkedIn, Freehire (50+ ATS platforms), Jobindex, Jobnet, Jobbank, Jobdanmark. |
| **3. Fit Evaluator** | `04-job-evaluation.md` | Dual-gate qualification (Language Gate, Dealbreaker Filter) and multi-factor match score calculation (0–100%). |
| **4. Tailored Drafter** | `/apply` | Synthesizes customized LaTeX ModernCV and targeted Cover Letter matching company pain points. |
| **5. ATS Reviewer** | `verify_pdf.py` & `verify_layout.py` | Extracts text layer and checks parseability, keyword density, and 1-page/2-page visual balance. |
| **6. Interview Coach** | `/interview` | Generates STAR behavioral interview scenarios, technical deep-dives, and reverse questions for interviewers. |
| **7. Funnel Tracker** | `/html-report` & `job_search_tracker.csv` | Tracks application status across Kanban stages and calculates screen-to-interview conversion rates. |

---

## 🌟 Key Features

### ⚡ Home Command Center (Landing Hub)
- **Executive Hero Command Banner**: Real-time candidate identity spotlight (*Amine Arheche • Morocco & Remote*), status badges, live agent mesh counter, and instant workflow launch buttons.
- **Autonomous Agent Mesh Radar**: Real-time heartbeat radar monitoring all 7 orchestrated subagents with animated ping testing, latency measurements, and direct node jump.
- **Mission-Critical KPI Metrics**: Live counters synchronized with `job_search_tracker.csv` displaying Total Tracked, 94.2% Dual-Gate Pass Rate, 7 Monitored Portals, and 98.5% ATS Parse Rate.
- **Autonomous Action Hub**: 6 dynamic launch tiles for one-click discovery passes (Morocco Portals, Global Remote), AI qualification audit, LaTeX ModernCV synthesis, STAR interview coach, and CSV exports.
- **Live Agent Event Stream**: Streaming chronological timeline of agent activities, discovery events, and dual-gate verdicts with filter tabs and an interactive pipeline simulation engine.
- **Market Intelligence & Salary Radar**: Interactive compensation calculator for Morocco (MAD/mo), Europe (EUR/yr), and Nordic (DKK/mo) with seniority sliders and net take-home estimations.
- **Featured Opportunities Spotlight**: High-match algorithmically ranked jobs with instant auto-fill into the AI Fit Evaluator.
- **Thin-Pointer Architecture Showcase**: Visual overview of zero-drift canonical specification model (`CLAUDE.md`, `.claude/skills/`, `.agents/skills/`).

### 🕸️ Interactive Architecture Map
- Visual pipeline nodes with status indicators.
- **Deep Inspector**: Click any agent node to inspect its execution triggers, canonical specification files, and CLI commands.

### 🔍 Discovery Hub (Multi-Portal Search)
- Query across LinkedIn, Freehire (50+ ATS), Jobindex, and Jobnet.
- Filter by keywords and remote/city location.
- One-click transfer from job results directly into the **Fit Evaluator**.

### ⚡ AI Fit Evaluator & Drafter
- Paste any job title, company, and description.
- Evaluates **Language Gates** and **Dealbreaker Constraints**.
- Highlights specific strengths and identified gaps.
- Real-time preview of tailored **LaTeX ModernCV** and **Cover Letter** with one-click clipboard copying.
- **Save to Pipeline**: Directly records the job into `job_search_tracker.csv`.

### 📊 Application Kanban & Analytics
- Live Funnel metrics: Total, Drafted, Active/Applied, Interview Stage, Offers, and Conversion Rate.
- Drag/toggle applications between stages (`drafted` ➔ `applied` ➔ `interview` ➔ `offer` ➔ `hired` ➔ `rejected`).
- Modal to record new applications on the fly.

### 👤 Profile Center
- Direct visual reflection of `CLAUDE.md`.
- Inspect primary and secondary skill sets, language levels, and dealbreakers.

### 🎯 STAR Method Interview Coach
- Generates structured STAR answers (*Situation, Task, Action, Result*).
- Anticipates architectural and technical questions tailored to the company.
- Suggests thoughtful reverse questions to ask the hiring team.

---

## 🛠️ API Endpoints

The server (`server.js`) exposes a clean JSON REST API:

- `GET /api/status`: System health, Python/Node versions, tracker status.
- `GET /api/agents`: Complete list of agents, metadata, and capabilities.
- `GET /api/profile`: Candidate profile details parsed from `CLAUDE.md`.
- `GET /api/tracker`: Application records and funnel conversion metrics.
- `POST /api/tracker`: Add a new application to `job_search_tracker.csv`.
- `POST /api/tracker/status`: Update status of an application by ID.
- `POST /api/scrape/search`: Search portal jobs by query, location, and portal.
- `POST /api/evaluate`: Compute match score, gates check, and recommendations.
- `POST /api/draft`: Generate LaTeX ModernCV and Cover Letter.
- `POST /api/interview`: Generate STAR scenarios and interview prep questions.

---

## 📁 Project Structure

```
ai-job-search/
├── server.js                      # Node.js REST API & static server
├── package.json                   # Dashboard dependencies & scripts
├── DASHBOARD_README.md            # This documentation
├── public/                        # Frontend Web Application
│   ├── index.html                 # Semantic HTML5 layout & tabs
│   ├── styles.css                 # Cosmic dark mode & glassmorphism
│   └── app.js                     # Client controller & state management
├── job_search_tracker.csv         # Canonical CSV tracking file
├── CLAUDE.md                      # Single source of truth candidate profile
├── AGENTS.md                      # Agent specifications & guidelines
├── .agents/skills/                # Portable portal search CLI tools
└── .claude/                       # Agent workflows, prompts & commands
```

---

## 📜 License

MIT License — feel free to customize and extend for your career search!
