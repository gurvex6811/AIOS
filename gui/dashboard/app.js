/**
 * AIOS Memory Dashboard — app.js
 * Connects to Nexus API at localhost:11435
 * All data is local. Zero external calls.
 */

const API = 'http://localhost:11435';

// ── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadGoals();
  loadDecisions();
  loadTimeline();
  startEmotionPolling();
});

// Auto-reload aura CSS every 5 seconds
setInterval(() => {
  const link = document.getElementById('aura-live');
  if (link) {
    const href = link.href.split('?')[0];
    link.href = href + '?t=' + Date.now();
  }
}, 5000);

// ── Stats ────────────────────────────────────────────────
async function loadStats() {
  try {
    const r = await fetch(`${API}/api/status`);
    if (!r.ok) return;
    const d = await r.json();
    setEl('memCount',     d.memory?.total ?? '—');
    setEl('goalCount',    d.goals?.active ?? '—');
    setEl('projectCount', d.projects?.active ?? '—');
    setEl('decisionCount',d.decisions?.total ?? '—');
  } catch {
    // Nexus offline — show placeholder
    ['memCount','goalCount','projectCount','decisionCount']
      .forEach(id => setEl(id, '—'));
  }
}

// ── Memory Search ─────────────────────────────────────────
async function searchMemory() {
  const q = document.getElementById('memSearch').value.trim();
  if (!q) return;
  const container = document.getElementById('memResults');
  container.innerHTML = '<div class="mem-item"><span class="mem-icon">⦿…</span><div class="mem-content"><div class="mem-title">Searching…</div></div></div>';
  try {
    const r = await fetch(`${API}/api/memories?q=${encodeURIComponent(q)}&limit=10`);
    const d = await r.json();
    renderMemories(container, d.results ?? []);
  } catch {
    container.innerHTML = nexusOffline();
  }
}

document.getElementById('memSearch')?.addEventListener('keydown', e => {
  if (e.key === 'Enter') searchMemory();
});

function renderMemories(container, mems) {
  if (!mems.length) {
    container.innerHTML = '<div style="color:var(--text-muted);font-size:13px;padding:12px">No memories found.</div>';
    return;
  }
  const TYPE_ICONS = {
    conversation: '💬', goal: '🎯', project: '🛠️',
    task: '✓', fact: 'ℹ️', decision: '✶', file: '📄'
  };
  container.innerHTML = mems.map(m => `
    <div class="mem-item">
      <span class="mem-icon">${TYPE_ICONS[m.type] || '💾'}</span>
      <div class="mem-content">
        <div class="mem-title">${esc(m.summary || m.content?.slice(0, 80) || '')}</div>
        <div class="mem-meta">
          <span>📅 ${(m.created_at || '').slice(0,10)}</span>
          <span>🎯 ${(m.importance || 0).toFixed(1)}</span>
          ${m.project ? `<span>🛠️ ${esc(m.project)}</span>` : ''}
        </div>
      </div>
      <span class="mem-tag">${(m.type || 'memory').toUpperCase()}</span>
    </div>
  `).join('');
}

// ── Goals ─────────────────────────────────────────────────
async function loadGoals() {
  const container = document.getElementById('goalsList');
  try {
    const r = await fetch(`${API}/api/goals`);
    const d = await r.json();
    const goals = d.goals ?? [];
    if (!goals.length) {
      container.innerHTML = '<div style="color:var(--text-muted);font-size:13px">No active goals. Add one below.</div>';
      return;
    }
    container.innerHTML = goals.map(g => `
      <div class="mem-item">
        <span class="mem-icon">🎯</span>
        <div class="mem-content">
          <div class="mem-title">${esc(g.description || g.title || '')}</div>
          <div class="mem-meta"><span>📅 ${(g.created_at||'').slice(0,10)}</span></div>
        </div>
        <span class="mem-tag">GOAL</span>
      </div>
    `).join('');
  } catch {
    container.innerHTML = nexusOffline();
  }
}

async function addGoal() {
  const input = document.getElementById('goalInput');
  const text = input.value.trim();
  if (!text) return;
  try {
    await fetch(`${API}/api/goals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description: text })
    });
    input.value = '';
    loadGoals();
    loadStats();
  } catch {
    alert('Nexus offline — start with: nexus start');
  }
}

// ── Decisions ────────────────────────────────────────────
async function loadDecisions() {
  const container = document.getElementById('decisionsList');
  try {
    const r = await fetch(`${API}/api/decisions?limit=5`);
    const d = await r.json();
    const items = d.decisions ?? [];
    if (!items.length) {
      container.innerHTML = '<div style="color:var(--text-muted);font-size:13px">No decision forks yet.</div>';
      return;
    }
    container.innerHTML = items.map(dec => `
      <div class="mem-item">
        <span class="mem-icon">✶</span>
        <div class="mem-content">
          <div class="mem-title">${esc(dec.title || dec.decision || '')}</div>
          <div class="mem-meta">
            <span>📅 ${(dec.created_at||'').slice(0,10)}</span>
            ${dec.emotion ? `<span>${dec.emotion}</span>` : ''}
          </div>
        </div>
        <span class="mem-tag">FORK</span>
      </div>
    `).join('');
  } catch {
    container.innerHTML = nexusOffline();
  }
}

// ── Timeline ─────────────────────────────────────────────
async function loadTimeline() {
  const container = document.getElementById('timeline-container');
  try {
    const r = await fetch(`${API}/api/memories?sort=recent&limit=12`);
    const d = await r.json();
    const mems = d.results ?? [];
    if (!mems.length) {
      container.innerHTML = '<div style="color:var(--text-muted);font-size:13px">Timeline will appear as you use AIOS.</div>';
      return;
    }
    container.innerHTML = mems.map(m => `
      <div class="tl-node">
        <span class="tl-dot"></span>
        <span class="tl-date">${(m.created_at||'').slice(0,10)}</span>
        <span class="tl-content">${esc(m.summary || m.content?.slice(0,120) || '')}</span>
      </div>
    `).join('');
  } catch {
    container.innerHTML = '<div style="color:var(--text-muted);font-size:13px">Start Nexus to see your memory timeline.</div>';
  }
}

// ── Emotion Polling ───────────────────────────────────────
function startEmotionPolling() {
  const poll = async () => {
    try {
      const r = await fetch(`${API}/api/status`);
      if (!r.ok) return;
      const d = await r.json();
      const state = d.emotion?.state || 'neutral';
      const emoji = d.emotion?.emoji || '😐';
      setEl('emotionLabel', `${emoji} ${capitalize(state)}`);
      document.documentElement.dataset.emotion = state;
    } catch {}
  };
  poll();
  setInterval(poll, 8000);
}

// ── Privacy ─────────────────────────────────────────────
async function exportData() {
  try {
    const r = await fetch(`${API}/api/privacy/export`);
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aios_data_export_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  } catch {
    alert('Nexus offline');
  }
}

function eraseData() {
  if (confirm('Are you sure? This will schedule full memory erasure (GDPR Article 17). You will be asked to confirm again in the CLI.')) {
    fetch(`${API}/api/privacy/erase`, { method: 'POST' })
      .then(() => alert('Erasure scheduled. Run: nexus privacy forget --confirm'))
      .catch(() => alert('Nexus offline'));
  }
}

// ── Utils ────────────────────────────────────────────────
function setEl(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function nexusOffline() {
  return `<div class="mem-item">
    <span class="mem-icon">⚡</span>
    <div class="mem-content">
      <div class="mem-title">Nexus is offline</div>
      <div class="mem-meta">Start with: <code>nexus start</code></div>
    </div>
  </div>`;
}
