// ===== STATE =====
let currentPage = 'global-dashboard';
let currentMode = localStorage.getItem('tf-mode') || 'beginner';
let currentTheme = localStorage.getItem('tf-theme') || 'dark';
let draggedTaskId = null;
let onboardingStep = 0;
const onboardingSteps = [
  { icon: '🚀', title: 'Welcome to TaskFlow!', desc: 'Your intelligent project management workspace. Let\'s get you set up in just a few steps.' },
  { icon: '⊞', title: 'Organize with Kanban', desc: 'Drag tasks between columns — Backlog, To Do, In Progress, Testing, Done. Visual clarity at a glance.' },
  { icon: '⟳', title: 'Work in Sprints', desc: 'A Sprint is a focused 1–2 week work cycle. Group your tasks into sprints and track progress automatically.' },
  { icon: '✅', title: 'You\'re all set!', desc: 'Explore your dashboard, create your first task, and collaborate with your team. TaskFlow is ready!' }
];

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
  applyTheme(currentTheme);
  applyMode(currentMode);
  drawCharts();
  buildGitGraph();
  const seen = localStorage.getItem('tf-onboarding-done');
  if (!seen) {
    setTimeout(() => {
      document.getElementById('onboarding-overlay').classList.add('open');
    }, 600);
  }
  document.addEventListener('click', e => {
    if (!e.target.closest('#notif-dropdown') && !e.target.closest('.icon-btn')) {
      document.getElementById('notif-dropdown').classList.remove('open');
    }
    document.querySelectorAll('.dropdown-menu.open').forEach(m => {
      if (!m.closest('.dropdown').contains(e.target)) m.classList.remove('open');
    });
  });
});

// ===== NAVIGATION =====
function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const pageEl = document.getElementById(page);
  if (pageEl) pageEl.classList.add('active');
  const navEl = document.querySelector(`[data-page="${page}"]`);
  if (navEl) navEl.classList.add('active');
  const titles = {
    'global-dashboard': 'Dashboard',
    'projects': 'Projects',
    'kanban': 'Kanban Board',
    'sprints': 'Sprints',
    'team': 'Team',
    'tasks': 'Task Detail',
    'chat': 'Chat',
    'files': 'Files',
    'analytics': 'Analytics',
    'timeline': 'Timeline',
    'roles': 'Roles & Permissions',
    'billing': 'Billing',
    'settings': 'Settings'
  };
  document.getElementById('breadcrumb-current').textContent = titles[page] || page;
  currentPage = page;
  if (page === 'analytics') setTimeout(drawCharts, 50);
}

// ===== SIDEBAR TOGGLE =====
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('collapsed');
}

// ===== THEME =====
function setTheme(theme) {
  applyTheme(theme);
  localStorage.setItem('tf-theme', theme);
}
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  currentTheme = theme;
  document.querySelectorAll('.theme-dot').forEach(d => d.classList.remove('active'));
  const dot = document.querySelector(`.theme-dot.${theme}`);
  if (dot) dot.classList.add('active');
}

// ===== MODE =====
function setMode(mode) {
  applyMode(mode);
  localStorage.setItem('tf-mode', mode);
}
function applyMode(mode) {
  currentMode = mode;
  document.body.classList.toggle('beginner-mode', mode === 'beginner');
  document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(mode === 'beginner' ? 'beginner-btn' : 'pro-btn').classList.add('active');
  // Show/hide beginner tips
  document.querySelectorAll('.beginner-tip').forEach(tip => {
    tip.classList.toggle('hidden', mode !== 'beginner');
  });
}
function toggleBeginnerFromSettings() {
  const tog = document.getElementById('beginner-toggle');
  tog.classList.toggle('on');
  setMode(tog.classList.contains('on') ? 'beginner' : 'pro');
}

// ===== NOTIFICATIONS =====
function toggleNotifDropdown() {
  document.getElementById('notif-dropdown').classList.toggle('open');
}

// ===== MODALS =====
function openModal(id) {
  document.getElementById(id).classList.add('open');
}
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
    document.getElementById('notif-dropdown').classList.remove('open');
  }
});
// Close modal on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', function(e) {
    if (e.target === this) this.classList.remove('open');
  });
});

// ===== KANBAN DRAG & DROP =====
function dragStart(e, taskId) {
  draggedTaskId = taskId;
  setTimeout(() => document.getElementById(taskId).classList.add('dragging'), 0);
  e.dataTransfer.effectAllowed = 'move';
}
function allowDrop(e) {
  e.preventDefault();
  e.currentTarget.classList.add('drag-over');
}
function dropTask(e, colName) {
  e.preventDefault();
  e.currentTarget.classList.remove('drag-over');
  if (!draggedTaskId) return;
  const card = document.getElementById(draggedTaskId);
  if (!card) return;
  const oldCol = card.dataset.col;
  card.dataset.col = colName;
  e.currentTarget.appendChild(card);
  card.classList.remove('dragging');
  updateColCounts();
  draggedTaskId = null;
  // Visual feedback
  card.style.animation = 'none';
  card.offsetHeight;
  card.style.animation = 'fadeIn 0.2s ease';
}
document.addEventListener('dragend', () => {
  document.querySelectorAll('.task-card').forEach(c => c.classList.remove('dragging'));
  document.querySelectorAll('.kanban-cards').forEach(c => c.classList.remove('drag-over'));
  draggedTaskId = null;
});
document.querySelectorAll('.kanban-cards').forEach(c => {
  c.addEventListener('dragleave', () => c.classList.remove('drag-over'));
});
function updateColCounts() {
  const cols = ['backlog', 'todo', 'inprogress', 'testing', 'done'];
  cols.forEach(col => {
    const count = document.getElementById(`cards-${col}`)?.querySelectorAll('.task-card').length || 0;
    const el = document.getElementById(`count-${col}`);
    if (el) el.textContent = count;
  });
}

// ===== TASK CREATION =====
function createTask() {
  const title = document.querySelector('#new-task-modal .form-input').value.trim();
  if (!title) return;
  const card = document.createElement('div');
  card.className = 'task-card';
  card.innerHTML = `<div class="task-card-header"><div class="task-title">${title}</div><div class="task-priority-dot priority-medium"></div></div><div class="task-footer"><div class="task-tags"><span class="tag tag-medium">Medium</span></div><div class="task-meta"><div class="task-avatars"><div class="task-avatar" style="background:linear-gradient(135deg,#6c63ff,#e91e8c)">JD</div></div></div></div>`;
  const newId = 'task-' + Date.now();
  card.id = newId;
  card.dataset.col = 'todo';
  card.draggable = true;
  card.addEventListener('dragstart', e => { draggedTaskId = newId; e.dataTransfer.effectAllowed = 'move'; });
  document.getElementById('cards-todo').appendChild(card);
  updateColCounts();
  closeModal('new-task-modal');
  document.querySelector('#new-task-modal .form-input').value = '';
}

// ===== SUBTASK TOGGLE =====
function toggleSubtask(el) {
  el.classList.toggle('done');
  const label = el.nextElementSibling;
  if (el.classList.contains('done')) { el.textContent = '✓'; label.classList.add('done'); }
  else { el.textContent = ''; label.classList.remove('done'); }
}

// ===== SETTINGS PANELS =====
function switchSettingsPanel(name, el) {
  document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
  document.querySelectorAll('.settings-panel').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('panel-' + name).classList.add('active');
}

// ===== CHAT =====
function sendChatMsg() {
  const input = document.getElementById('chat-main-input');
  const msg = input.value.trim();
  if (!msg) return;
  const container = document.querySelector('#chat .chat-messages');
  const el = document.createElement('div');
  el.className = 'chat-msg me';
  el.innerHTML = `<div><div class="chat-bubble me">${msg}</div><div class="chat-time">Just now</div></div><div class="user-avatar" style="flex-shrink:0">JD</div>`;
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
  input.value = '';
}

// ===== ONBOARDING =====
function nextOnboarding() {
  onboardingStep++;
  if (onboardingStep >= onboardingSteps.length) {
    skipOnboarding();
    return;
  }
  updateOnboardingStep();
}
function updateOnboardingStep() {
  const step = onboardingSteps[onboardingStep];
  document.getElementById('ob-icon').textContent = step.icon;
  document.getElementById('ob-title').textContent = step.title;
  document.getElementById('ob-desc').textContent = step.desc;
  document.querySelectorAll('.step-dot').forEach((d, i) => d.classList.toggle('active', i === onboardingStep));
  const isLast = onboardingStep === onboardingSteps.length - 1;
  document.getElementById('ob-next').textContent = isLast ? 'Start Building →' : 'Next →';
}
function skipOnboarding() {
  document.getElementById('onboarding-overlay').classList.remove('open');
  localStorage.setItem('tf-onboarding-done', '1');
}

// ===== CHARTS (Pure Canvas) =====
function drawCharts() {
  drawBurndown();
  drawPie();
  drawVelocity();
  drawCFD();
}

function drawBurndown() {
  const canvas = document.getElementById('burndownChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth || 500;
  canvas.height = 180;
  const W = canvas.width, H = canvas.height;
  const pad = 40;
  ctx.clearRect(0, 0, W, H);

  const ideal = [25,22,19,16,13,10,8,6,4,2,0];
  const actual = [25,23,21,18,17,14,12,10,8,7,null,null];
  const labels = ['Mar 1','2','3','4','5','6','7','8','9','10','11','12','13','14'];
  const maxV = 28;

  const sx = i => pad + (i / (labels.length - 1)) * (W - pad * 2);
  const sy = v => H - pad - (v / maxV) * (H - pad * 2);

  // Grid
  const style = getComputedStyle(document.documentElement);
  const gridColor = currentTheme === 'light' ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.06)';
  const textColor = currentTheme === 'light' ? '#4a5070' : '#5c6080';
  for (let i = 0; i <= 5; i++) {
    const y = pad + (i / 5) * (H - pad * 2);
    ctx.beginPath(); ctx.strokeStyle = gridColor; ctx.lineWidth = 1;
    ctx.moveTo(pad, y); ctx.lineTo(W - pad, y); ctx.stroke();
    ctx.fillStyle = textColor; ctx.font = '10px DM Sans,sans-serif'; ctx.textAlign = 'right';
    ctx.fillText(Math.round(maxV - i * maxV / 5), pad - 6, y + 3);
  }

  // Ideal line
  ctx.beginPath(); ctx.strokeStyle = 'rgba(155,89,182,0.5)'; ctx.lineWidth = 2; ctx.setLineDash([6,4]);
  ideal.forEach((v, i) => {
    const x = sx(i * (labels.length - 1) / (ideal.length - 1)), y = sy(v);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke(); ctx.setLineDash([]);

  // Actual line
  const actualData = actual.filter(v => v !== null);
  ctx.beginPath(); ctx.strokeStyle = '#6c63ff'; ctx.lineWidth = 2.5;
  actualData.forEach((v, i) => {
    const x = sx(i * (labels.length - 1) / (actual.length - 1)), y = sy(v);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke();

  // Area fill
  ctx.beginPath(); ctx.fillStyle = 'rgba(108,99,255,0.1)';
  actualData.forEach((v, i) => {
    const x = sx(i * (labels.length - 1) / (actual.length - 1)), y = sy(v);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  const lastX = sx((actualData.length - 1) * (labels.length - 1) / (actual.length - 1));
  ctx.lineTo(lastX, H - pad); ctx.lineTo(sx(0), H - pad); ctx.closePath(); ctx.fill();

  // Dots
  actualData.forEach((v, i) => {
    const x = sx(i * (labels.length - 1) / (actual.length - 1)), y = sy(v);
    ctx.beginPath(); ctx.fillStyle = '#6c63ff'; ctx.arc(x, y, 4, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.fillStyle = currentTheme === 'light' ? '#fff' : '#1c1e28'; ctx.arc(x, y, 2, 0, Math.PI * 2); ctx.fill();
  });

  // Labels
  ctx.fillStyle = textColor; ctx.font = '10px DM Sans,sans-serif'; ctx.textAlign = 'center';
  [0, 4, 7, 10].forEach(i => ctx.fillText(labels[i], sx(i), H - 4));
}

function drawPie() {
  const canvas = document.getElementById('pieChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth || 500;
  canvas.height = 180;
  const W = canvas.width, H = canvas.height;
  const cx = W * 0.4, cy = H / 2, r = Math.min(cx, cy) - 20;
  ctx.clearRect(0, 0, W, H);

  const data = [
    { label: 'Done', value: 18, color: '#2ecc71' },
    { label: 'In Progress', value: 7, color: '#f39c12' },
    { label: 'To Do', value: 3, color: '#3498db' },
    { label: 'Backlog', value: 5, color: '#5c6080' },
    { label: 'Testing', value: 2, color: '#9b59b6' }
  ];
  const total = data.reduce((s, d) => s + d.value, 0);
  let angle = -Math.PI / 2;
  data.forEach(d => {
    const slice = (d.value / total) * Math.PI * 2;
    ctx.beginPath(); ctx.fillStyle = d.color;
    ctx.moveTo(cx, cy); ctx.arc(cx, cy, r, angle, angle + slice);
    ctx.closePath(); ctx.fill();
    angle += slice;
  });
  // Center hole (donut)
  ctx.beginPath(); ctx.fillStyle = currentTheme === 'light' ? '#fff' : '#1c1e28';
  ctx.arc(cx, cy, r * 0.55, 0, Math.PI * 2); ctx.fill();
  // Center text
  ctx.fillStyle = currentTheme === 'light' ? '#1a1c2e' : '#e8eaf6';
  ctx.font = 'bold 18px Syne,sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('35', cx, cy - 6);
  ctx.font = '10px DM Sans,sans-serif'; ctx.fillStyle = '#5c6080';
  ctx.fillText('Total Tasks', cx, cy + 10);
  // Legend
  const lx = W * 0.75, ly = (H - data.length * 22) / 2;
  data.forEach((d, i) => {
    ctx.fillStyle = d.color; ctx.fillRect(lx, ly + i * 22, 10, 10);
    ctx.fillStyle = currentTheme === 'light' ? '#4a5070' : '#9da3c8';
    ctx.font = '11px DM Sans,sans-serif'; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
    ctx.fillText(`${d.label} (${d.value})`, lx + 14, ly + i * 22 + 10);
  });
}

function drawVelocity() {
  const canvas = document.getElementById('velocityChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth || 500;
  canvas.height = 180;
  const W = canvas.width, H = canvas.height;
  const pad = { l: 40, r: 20, t: 20, b: 30 };
  ctx.clearRect(0, 0, W, H);

  const data = [
    { sprint: 'S7', pts: 22 }, { sprint: 'S8', pts: 25 }, { sprint: 'S9', pts: 28 },
    { sprint: 'S10', pts: 32 }, { sprint: 'S11', pts: 28 }, { sprint: 'S12', pts: 34 }
  ];
  const maxV = 40;
  const barW = (W - pad.l - pad.r) / data.length * 0.55;
  const gap = (W - pad.l - pad.r) / data.length;
  const gridColor = currentTheme === 'light' ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.06)';
  const textColor = currentTheme === 'light' ? '#4a5070' : '#5c6080';

  // Grid
  for (let i = 0; i <= 4; i++) {
    const y = pad.t + (i / 4) * (H - pad.t - pad.b);
    ctx.beginPath(); ctx.strokeStyle = gridColor; ctx.lineWidth = 1;
    ctx.moveTo(pad.l, y); ctx.lineTo(W - pad.r, y); ctx.stroke();
    ctx.fillStyle = textColor; ctx.font = '10px DM Sans,sans-serif'; ctx.textAlign = 'right';
    ctx.fillText(Math.round(maxV - i * maxV / 4), pad.l - 6, y + 3);
  }

  data.forEach((d, i) => {
    const x = pad.l + i * gap + (gap - barW) / 2;
    const bh = (d.pts / maxV) * (H - pad.t - pad.b);
    const y = H - pad.b - bh;
    // Bar gradient
    const grad = ctx.createLinearGradient(0, y, 0, H - pad.b);
    const isLast = i === data.length - 1;
    grad.addColorStop(0, isLast ? '#6c63ff' : 'rgba(108,99,255,0.7)');
    grad.addColorStop(1, isLast ? 'rgba(108,99,255,0.3)' : 'rgba(108,99,255,0.15)');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.roundRect ? ctx.roundRect(x, y, barW, bh, [4, 4, 0, 0]) : ctx.rect(x, y, barW, bh);
    ctx.fill();
    // Value
    ctx.fillStyle = currentTheme === 'light' ? '#1a1c2e' : '#e8eaf6';
    ctx.font = 'bold 11px DM Sans,sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(d.pts, x + barW / 2, y - 4);
    // Label
    ctx.fillStyle = textColor; ctx.font = '10px DM Sans,sans-serif';
    ctx.fillText(d.sprint, x + barW / 2, H - 4);
  });
}

function drawCFD() {
  const canvas = document.getElementById('cfdChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth || 500;
  canvas.height = 180;
  const W = canvas.width, H = canvas.height;
  const pad = 40;
  ctx.clearRect(0, 0, W, H);

  const days = 14;
  const layers = [
    { label: 'Done', color: 'rgba(46,204,113,0.7)', data: [0,1,2,4,6,8,10,12,13,15,16,17,17,18] },
    { label: 'Testing', color: 'rgba(155,89,182,0.7)', data: [0,0,1,1,2,2,3,3,4,4,5,5,5,5] },
    { label: 'In Progress', color: 'rgba(243,156,18,0.7)', data: [1,2,3,3,3,4,5,5,5,6,7,7,7,7] },
    { label: 'To Do', color: 'rgba(52,152,219,0.7)', data: [5,5,5,5,5,5,5,4,4,4,3,3,3,3] },
    { label: 'Backlog', color: 'rgba(92,96,128,0.5)', data: [19,17,14,12,9,6,2,1,1,0,0,0,0,0] }
  ];

  const maxV = 25;
  const sx = i => pad + (i / (days - 1)) * (W - pad * 2);
  const sy = v => H - pad - (v / maxV) * (H - pad * 2);

  // Stacked areas
  const cumulative = Array(days).fill(0);
  layers.reverse().forEach(layer => {
    ctx.beginPath();
    const prevCum = [...cumulative];
    layer.data.forEach((v, i) => { cumulative[i] += v; });
    cumulative.forEach((v, i) => {
      i === 0 ? ctx.moveTo(sx(i), sy(v)) : ctx.lineTo(sx(i), sy(v));
    });
    for (let i = days - 1; i >= 0; i--) ctx.lineTo(sx(i), sy(prevCum[i]));
    ctx.closePath();
    ctx.fillStyle = layer.color;
    ctx.fill();
  });

  // Axis labels
  const textColor = currentTheme === 'light' ? '#4a5070' : '#5c6080';
  ctx.fillStyle = textColor; ctx.font = '10px DM Sans,sans-serif'; ctx.textAlign = 'center';
  [0, 4, 8, 13].forEach(i => ctx.fillText(`Mar ${i + 1}`, sx(i), H - 4));
}

// ===== GIT GRAPH =====
function buildGitGraph() {
  const container = document.getElementById('git-graph');
  if (!container) return;
  const W = container.offsetWidth || 600;
  const commits = [
    { x: 0.05, y: 0.5, branch: 'main' }, { x: 0.15, y: 0.5, branch: 'main' },
    { x: 0.25, y: 0.3, branch: 'feature' }, { x: 0.3, y: 0.5, branch: 'main' },
    { x: 0.4, y: 0.3, branch: 'feature' }, { x: 0.5, y: 0.7, branch: 'hotfix' },
    { x: 0.55, y: 0.5, branch: 'main' }, { x: 0.65, y: 0.3, branch: 'feature' },
    { x: 0.7, y: 0.5, branch: 'main' }, { x: 0.8, y: 0.5, branch: 'main' },
    { x: 0.9, y: 0.5, branch: 'main' }, { x: 0.95, y: 0.5, branch: 'main' }
  ];
  const colors = { main: '#6c63ff', feature: '#e91e8c', hotfix: '#f39c12' };
  // Render as canvas inside
  const canvas = document.createElement('canvas');
  canvas.width = W; canvas.height = 120;
  canvas.style.width = '100%'; canvas.style.height = '120px';
  container.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  // Draw main line
  ctx.beginPath(); ctx.strokeStyle = '#6c63ff'; ctx.lineWidth = 2;
  ctx.moveTo(commits[0].x * W, 60); ctx.lineTo(commits[11].x * W, 60); ctx.stroke();
  // Draw feature branch
  ctx.beginPath(); ctx.strokeStyle = '#e91e8c'; ctx.lineWidth = 1.5; ctx.setLineDash([4,3]);
  ctx.moveTo(commits[1].x * W, 60);
  ctx.lineTo(commits[2].x * W, 36);
  ctx.lineTo(commits[4].x * W, 36);
  ctx.lineTo(commits[5].x * W, 60);
  ctx.stroke(); ctx.setLineDash([]);
  // Draw hotfix branch
  ctx.beginPath(); ctx.strokeStyle = '#f39c12'; ctx.lineWidth = 1.5; ctx.setLineDash([4,3]);
  ctx.moveTo(commits[3].x * W, 60);
  ctx.quadraticCurveTo(commits[4].x * W, 84, commits[5].x * W, 84);
  ctx.lineTo(commits[6].x * W, 60);
  ctx.stroke(); ctx.setLineDash([]);
  // Draw commit dots
  commits.forEach(c => {
    const x = c.x * W;
    const y = c.branch === 'main' ? 60 : c.branch === 'feature' ? 36 : 84;
    ctx.beginPath(); ctx.fillStyle = colors[c.branch] || '#6c63ff'; ctx.arc(x, y, 6, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.fillStyle = '#1c1e28'; ctx.arc(x, y, 3, 0, Math.PI * 2); ctx.fill();
  });
  // Labels
  ctx.fillStyle = '#5c6080'; ctx.font = '10px DM Mono,monospace'; ctx.textAlign = 'center';
  ctx.fillStyle = '#6c63ff'; ctx.fillText('main', commits[11].x * W + 10, 75);
  ctx.fillStyle = '#e91e8c'; ctx.fillText('feature/auth', commits[4].x * W, 22);
  ctx.fillStyle = '#f39c12'; ctx.fillText('hotfix', commits[5].x * W - 10, 100);
}

// ===== RESPONSIVE CHART RESIZE =====
window.addEventListener('resize', () => {
  if (currentPage === 'analytics') drawCharts();
});