// ========================================================
// AI JOB SEARCH - MULTI-AGENT ARCHITECTURE DASHBOARD
// Client-side Application Logic
// ========================================================

const state = {
  currentTab: 'architecture',
  agents: [],
  tracker: { applications: [], stats: {} },
  profile: null,
  activeAgent: null,
  currentDocs: { latexCV: '', coverLetter: '' },
  activeDocType: 'cv'
};

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initEventListeners();
  loadInitialData();
});

// Tab Switching
function initTabs() {
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.getAttribute('data-tab');
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      const activeContent = document.getElementById(`tab-${target}`);
      if (activeContent) activeContent.classList.add('active');
      state.currentTab = target;

      if (target === 'tracker') {
        loadTrackerData();
      }
    });
  });
}

// Initial Data Fetching
async function loadInitialData() {
  try {
    const [statusRes, agentsRes, trackerRes, profileRes] = await Promise.all([
      fetch('/api/status').then(r => r.json()).catch(() => null),
      fetch('/api/agents').then(r => r.json()).catch(() => []),
      fetch('/api/tracker').then(r => r.json()).catch(() => ({ applications: [], stats: {} })),
      fetch('/api/profile').then(r => r.json()).catch(() => null)
    ]);

    // Update Status Pills
    if (statusRes) {
      if (statusRes.nodeVersion) document.getElementById('nodeVersionLabel').textContent = statusRes.nodeVersion;
      if (statusRes.pythonInstalled) document.getElementById('pythonStatusLabel').textContent = statusRes.pythonInstalled.split(' ')[1] || 'Ready';
    }

    // Agents
    state.agents = agentsRes;
    document.getElementById('agentsCountLabel').textContent = `${agentsRes.length} Online`;
    renderMiniAgentsList();
    if (agentsRes.length > 0) {
      selectAgent('agent-drafter');
    }

    // Tracker
    state.tracker = trackerRes;
    renderTracker();

    // Profile
    state.profile = profileRes;
    renderProfile();

    // Run default scraper query
    runScraperQuery();

  } catch (err) {
    console.error('Failed to load initial dashboard data:', err);
  }
}

// Render Mini Agents in sidebar
function renderMiniAgentsList() {
  const container = document.getElementById('miniAgentsList');
  if (!container) return;
  container.innerHTML = state.agents.map(a => `
    <div class="agent-mini-card" onclick="selectAgent('${a.id}')">
      <div class="agent-mini-info">
        <strong>${a.name}</strong>
        <span>${a.command} &bull; ${a.category}</span>
      </div>
      <span class="status-badge ${a.status === 'Active' ? 'status-live' : ''}">${a.status}</span>
    </div>
  `).join('');
}

// Select an Agent for Deep Inspector
window.selectAgent = function(agentId) {
  const agent = state.agents.find(a => a.id === agentId);
  if (!agent) return;
  state.activeAgent = agent;

  document.querySelectorAll('.arch-node').forEach(node => {
    node.classList.remove('active-flow');
  });

  const inspectorName = document.getElementById('inspectorName');
  const inspectorCategory = document.getElementById('inspectorCategory');
  const inspectorDesc = document.getElementById('inspectorDesc');
  const inspectorSpec = document.getElementById('inspectorSpec');
  const inspectorCapabilities = document.getElementById('inspectorCapabilities');
  const inspectorCommand = document.getElementById('inspectorCommand');

  inspectorName.textContent = agent.name;
  inspectorCategory.textContent = agent.category;
  inspectorDesc.textContent = agent.description;
  inspectorSpec.innerHTML = `<code>${agent.specFile}</code>`;
  inspectorCommand.innerHTML = `<code>${agent.command}</code>`;

  inspectorCapabilities.innerHTML = agent.capabilities.map(c => `
    <span class="skill-tag skill-cyan">${c}</span>
  `).join('');
};

// Scraper Hub
async function runScraperQuery() {
  const query = document.getElementById('scraperQueryInput').value;
  const location = document.getElementById('scraperLocationInput').value;
  const portal = document.getElementById('scraperPortalSelect').value;

  const resultsGrid = document.getElementById('scraperJobsGrid');
  resultsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-muted);">Scanning ${portal} index...</div>`;

  try {
    const res = await fetch('/api/scrape/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, portal, location })
    });
    const data = await res.json();
    document.getElementById('scraperResultsCount').textContent = `${data.total} Live Roles Found`;

    resultsGrid.innerHTML = data.results.map(job => `
      <div class="job-card">
        <div>
          <div class="job-card-top">
            <div>
              <span class="job-card-company">${job.company}</span>
              <h4 class="job-card-title">${job.title}</h4>
            </div>
            <span class="score-badge">${job.matchScore}%</span>
          </div>
          <div class="job-card-meta">
            <span>📍 ${job.location}</span>
            <span>💼 ${job.type}</span>
            <span>🌐 ${job.portal}</span>
          </div>
          <p class="job-card-desc">${job.description}</p>
          <div class="tags-container" style="margin-bottom: 1rem;">
            ${job.tags.map(t => `<span class="skill-tag">${t}</span>`).join('')}
          </div>
        </div>
        <div class="job-card-footer">
          <span class="job-salary">💰 ${job.salary}</span>
          <button class="btn btn-primary btn-sm" onclick="sendJobToEvaluator('${encodeURIComponent(job.title)}', '${encodeURIComponent(job.company)}', '${encodeURIComponent(job.description)}')">
            Evaluate & Apply ➔
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    resultsGrid.innerHTML = `<div style="color: var(--accent-red); padding: 1rem;">Scraper query failed: ${err.message}</div>`;
  }
}

// Send selected job to evaluator tab
window.sendJobToEvaluator = function(encTitle, encCompany, encDesc) {
  const title = decodeURIComponent(encTitle);
  const company = decodeURIComponent(encCompany);
  const desc = decodeURIComponent(encDesc);

  document.getElementById('evalTitleInput').value = title;
  document.getElementById('evalCompanyInput').value = company;
  document.getElementById('evalDescInput').value = desc;

  // Switch to evaluator tab
  const evalTabBtn = document.querySelector('.nav-tab[data-tab="evaluator"]');
  if (evalTabBtn) evalTabBtn.click();

  // Run evaluation directly
  runJobEvaluation();
};

// Run Fit Evaluation
async function runJobEvaluation() {
  const title = document.getElementById('evalTitleInput').value;
  const company = document.getElementById('evalCompanyInput').value;
  const description = document.getElementById('evalDescInput').value;

  try {
    const res = await fetch('/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, company, description })
    });
    const evalData = await res.json();

    document.getElementById('evalScoreBadge').textContent = `${evalData.score}% MATCH`;
    document.getElementById('gateLangText').textContent = evalData.languageGate;
    document.getElementById('gateDealText').textContent = evalData.dealbreakerCheck;

    const strengthsList = document.getElementById('evalStrengthsList');
    strengthsList.innerHTML = evalData.strengths.map(s => `<li>${s}</li>`).join('');

    const gapsList = document.getElementById('evalGapsList');
    gapsList.innerHTML = evalData.gaps.map(g => `<li>${g}</li>`).join('');

    document.getElementById('evalRecText').textContent = evalData.recommendation;
  } catch (err) {
    console.error('Fit evaluation failed:', err);
  }
}

// Draft LaTeX CV and Cover Letter
async function draftApplicationDocuments() {
  const title = document.getElementById('evalTitleInput').value;
  const company = document.getElementById('evalCompanyInput').value;
  const description = document.getElementById('evalDescInput').value;

  try {
    const res = await fetch('/api/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, company, description })
    });
    const docs = await res.json();
    state.currentDocs = docs;

    const previewArea = document.getElementById('documentsPreviewArea');
    previewArea.style.display = 'block';
    updateDocumentPreview();
    previewArea.scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    console.error('Draft documents failed:', err);
  }
}

function updateDocumentPreview() {
  const codeBox = document.getElementById('documentCodeDisplay');
  if (state.activeDocType === 'cv') {
    codeBox.textContent = state.currentDocs.latexCV;
  } else {
    codeBox.textContent = state.currentDocs.coverLetter;
  }
}

// Tracker functions
async function loadTrackerData() {
  try {
    const res = await fetch('/api/tracker');
    const data = await res.json();
    state.tracker = data;
    renderTracker();
  } catch (err) {
    console.error('Failed to load tracker:', err);
  }
}

function renderTracker() {
  const stats = state.tracker.stats || {};
  document.getElementById('metricTotal').textContent = stats.total || 0;
  document.getElementById('metricDrafted').textContent = stats.drafted || 0;
  document.getElementById('metricApplied').textContent = stats.applied || 0;
  document.getElementById('metricInterview').textContent = stats.interview || 0;
  document.getElementById('metricOffer').textContent = stats.offer || 0;
  document.getElementById('metricConversion').textContent = `${stats.conversionRate || 0}%`;

  const drafted = [];
  const applied = [];
  const interview = [];
  const offer = [];

  (state.tracker.applications || []).forEach(app => {
    if (app.status === 'drafted') drafted.push(app);
    else if (app.status === 'applied') applied.push(app);
    else if (app.status === 'interview') interview.push(app);
    else offer.push(app);
  });

  document.getElementById('colCountDrafted').textContent = drafted.length;
  document.getElementById('colCountApplied').textContent = applied.length;
  document.getElementById('colCountInterview').textContent = interview.length;
  document.getElementById('colCountOffer').textContent = offer.length;

  renderKanbanColumn('colCardsDrafted', drafted);
  renderKanbanColumn('colCardsApplied', applied);
  renderKanbanColumn('colCardsInterview', interview);
  renderKanbanColumn('colCardsOffer', offer);
}

function renderKanbanColumn(containerId, apps) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (apps.length === 0) {
    container.innerHTML = `<div style="text-align: center; color: var(--text-dim); font-size: 0.8rem; padding: 1.5rem 0;">No applications in this stage</div>`;
    return;
  }

  container.innerHTML = apps.map(a => `
    <div class="kanban-card">
      <div class="kcard-company">${a.company}</div>
      <div class="kcard-role">${a.role}</div>
      <div class="kcard-meta">
        <span>📅 ${a.date}</span>
        <span>⭐ Fit: ${a.fit_rating}/5</span>
      </div>
      <select class="status-select-mini" onchange="changeAppStatus(${a.id}, this.value)">
        <option value="drafted" ${a.status === 'drafted' ? 'selected' : ''}>Drafted</option>
        <option value="applied" ${a.status === 'applied' ? 'selected' : ''}>Applied</option>
        <option value="interview" ${a.status === 'interview' ? 'selected' : ''}>Interview</option>
        <option value="offer" ${a.status === 'offer' ? 'selected' : ''}>Offer</option>
        <option value="hired" ${a.status === 'hired' ? 'selected' : ''}>Hired</option>
        <option value="rejected" ${a.status === 'rejected' ? 'selected' : ''}>Rejected</option>
      </select>
    </div>
  `).join('');
}

window.changeAppStatus = async function(id, newStatus) {
  try {
    const res = await fetch('/api/tracker/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, status: newStatus })
    });
    const updated = await res.json();
    state.tracker = updated;
    renderTracker();
  } catch (err) {
    console.error('Failed to update status:', err);
  }
};

// Render Profile
function renderProfile() {
  if (!state.profile) return;
  const p = state.profile;
  const profName = document.getElementById('profName');
  const profHeadline = document.getElementById('profHeadline');
  const profLocation = document.getElementById('profLocation');

  if (profName) profName.value = p.name;
  if (profHeadline) profHeadline.value = p.title;
  if (profLocation) profLocation.value = p.location;
}

// Generate STAR Interview Coach
async function runInterviewCoach() {
  const company = document.getElementById('coachCompanyInput').value;
  const role = document.getElementById('coachRoleInput').value;
  const output = document.getElementById('interviewPrepOutput');

  output.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 1.5rem;">Generating tailored STAR scenarios and technical talking points for ${company}...</div>`;

  try {
    const res = await fetch('/api/interview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company, role })
    });
    const data = await res.json();

    output.innerHTML = `
      <div class="star-card">
        <h3 class="panel-title" style="margin-bottom: 1rem;">STAR Behavioral Scenarios (${data.company})</h3>
        ${data.starQuestions.map(q => `
          <div style="margin-bottom: 1.5rem;">
            <div class="star-question">❓ "${q.question}"</div>
            <div class="star-grid">
              <div class="star-col">
                <strong>Situation</strong>
                <p>${q.starFramework.situation}</p>
              </div>
              <div class="star-col">
                <strong>Task</strong>
                <p>${q.starFramework.task}</p>
              </div>
              <div class="star-col">
                <strong>Action</strong>
                <p>${q.starFramework.action}</p>
              </div>
              <div class="star-col">
                <strong>Result</strong>
                <p>${q.starFramework.result}</p>
              </div>
            </div>
          </div>
        `).join('')}

        <div style="margin-top: 2rem;">
          <h4 class="block-title">Technical Deep Dives to Anticipate</h4>
          <ul class="eval-list" style="margin-bottom: 1.5rem;">
            ${data.technicalDeepDives.map(t => `<li>${t}</li>`).join('')}
          </ul>

          <h4 class="block-title">Smart Reverse Questions to Ask the Hiring Team</h4>
          <ul class="eval-list" style="color: var(--accent-cyan);">
            ${data.reverseQuestionsToAsk.map(r => `<li>"${r}"</li>`).join('')}
          </ul>
        </div>
      </div>
    `;
  } catch (err) {
    output.innerHTML = `<div style="color: var(--accent-red);">Failed to generate interview prep: ${err.message}</div>`;
  }
}

// Event Listeners setup
function initEventListeners() {
  // Scraper button
  const btnScraper = document.getElementById('btnRunScraper');
  if (btnScraper) btnScraper.addEventListener('click', runScraperQuery);

  // Evaluator buttons
  const btnEval = document.getElementById('btnEvaluateJob');
  if (btnEval) btnEval.addEventListener('click', runJobEvaluation);

  const btnDraft = document.getElementById('btnDraftDocs');
  if (btnDraft) btnDraft.addEventListener('click', draftApplicationDocuments);

  // Document tab toggle
  const tabShowCv = document.getElementById('tabShowCv');
  const tabShowCover = document.getElementById('tabShowCover');
  if (tabShowCv && tabShowCover) {
    tabShowCv.addEventListener('click', () => {
      state.activeDocType = 'cv';
      tabShowCv.classList.add('active');
      tabShowCover.classList.remove('active');
      updateDocumentPreview();
    });
    tabShowCover.addEventListener('click', () => {
      state.activeDocType = 'cover';
      tabShowCover.classList.add('active');
      tabShowCv.classList.remove('active');
      updateDocumentPreview();
    });
  }

  // Copy document button
  const btnCopy = document.getElementById('btnCopyDocument');
  if (btnCopy) {
    btnCopy.addEventListener('click', () => {
      const code = document.getElementById('documentCodeDisplay').textContent;
      navigator.clipboard.writeText(code).then(() => {
        btnCopy.innerHTML = `<span>✔ Copied!</span>`;
        setTimeout(() => {
          btnCopy.innerHTML = `<span>📋 Copy to Clipboard</span>`;
        }, 2000);
      });
    });
  }

  // Save to Tracker from Evaluator
  const btnSaveFromEval = document.getElementById('btnSaveToTrackerFromEval');
  if (btnSaveFromEval) {
    btnSaveFromEval.addEventListener('click', async () => {
      const company = document.getElementById('evalCompanyInput').value;
      const role = document.getElementById('evalTitleInput').value;
      const payload = {
        company,
        role,
        sector: 'Software & Platform',
        status: 'applied',
        fit_rating: '5',
        notes: 'Directly evaluated & tailored via AI Job Search Agent Dashboard'
      };
      await fetch('/api/tracker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      btnSaveFromEval.innerHTML = `<span>✔ Saved to Pipeline!</span>`;
      setTimeout(() => {
        btnSaveFromEval.innerHTML = `<span>➕ Save Directly to Application Tracker</span>`;
      }, 2500);
      loadTrackerData();
    });
  }

  // Modal open / close
  const modal = document.getElementById('addAppModal');
  const btnOpenModal = document.getElementById('btnOpenAddModal');
  const btnCloseModal = document.getElementById('btnCloseAddModal');
  const btnCancelModal = document.getElementById('btnCancelAddModal');
  const btnSubmitModal = document.getElementById('btnSubmitAddModal');

  if (btnOpenModal && modal) {
    btnOpenModal.addEventListener('click', () => { modal.style.display = 'flex'; });
    btnCloseModal.addEventListener('click', () => { modal.style.display = 'none'; });
    btnCancelModal.addEventListener('click', () => { modal.style.display = 'none'; });

    btnSubmitModal.addEventListener('click', async () => {
      const company = document.getElementById('modalCompany').value;
      const role = document.getElementById('modalRole').value;
      const sector = document.getElementById('modalSector').value;
      const status = document.getElementById('modalStatus').value;
      const fit_rating = document.getElementById('modalFit').value;
      const notes = document.getElementById('modalNotes').value;

      if (!company || !role) {
        alert('Please specify at least company name and role title');
        return;
      }

      await fetch('/api/tracker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company, role, sector, status, fit_rating, notes })
      });

      modal.style.display = 'none';
      loadTrackerData();
    });
  }

  // Interview Coach button
  const btnInterview = document.getElementById('btnGenerateInterviewPrep');
  if (btnInterview) btnInterview.addEventListener('click', runInterviewCoach);
}
