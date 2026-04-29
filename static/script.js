// Notification Dropdown Functionality

// Toggle notification dropdown and load notifications
function toggleNotifDropdown() {
  const dropdown = document.getElementById('notif-dropdown');
  dropdown.classList.toggle('show');
  
  if (dropdown.classList.contains('show')) {
    loadNotifications();
  }
}

// Load notifications when dropdown is opened
function loadNotifications() {
  const dropdown = document.getElementById('notif-dropdown');
  
  // Check if dropdown is being shown
  if (!dropdown.classList.contains('show')) {
    return;
  }
  
  fetch('/notifications/api/get/')
    .then(response => response.json())
    .then(data => {
      const notificationsList = document.getElementById('notifications-list');
      
      if (data.notifications.length === 0) {
        notificationsList.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--text3);">No notifications</div>';
        return;
      }
      
      notificationsList.innerHTML = data.notifications.map(notif => `
        <div class="notif-item" data-notif-id="${notif.id}" onclick="markNotificationRead(event, ${notif.id})">
          <div class="notif-dot ${notif.is_read ? 'read' : ''}"></div>
          <div>
            <div class="notif-text">${escapeHtml(notif.message)}</div>
            <div class="notif-time">${notif.created_at}</div>
          </div>
        </div>
      `).join('');
    })
    .catch(error => console.error('Error loading notifications:', error));
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// Mark a single notification as read
function markNotificationRead(event, notificationId) {
  event.preventDefault();
  
  fetch(`/notifications/${notificationId}/read/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Update the notification item in the UI
      const notifItem = document.querySelector(`[data-notif-id="${notificationId}"]`);
      if (notifItem) {
        notifItem.querySelector('.notif-dot').classList.add('read');
      }
      
      // Update notification count
      updateNotificationCount();
    }
  })
  .catch(error => console.error('Error marking notification as read:', error));
}

// Mark all notifications as read
function markAllNotificationsRead() {
  fetch('/notifications/api/mark-all-read/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Mark all items as read in the UI
      document.querySelectorAll('.notif-dot').forEach(dot => {
        dot.classList.add('read');
      });
      
      // Update notification count
      document.getElementById('notif-count').textContent = '0';
    }
  })
  .catch(error => console.error('Error marking all notifications as read:', error));
}

// Update notification count
function updateNotificationCount() {
  fetch('/notifications/unread-count/')
    .then(response => response.json())
    .then(data => {
      document.getElementById('notif-count').textContent = data.count;
    })
    .catch(error => console.error('Error updating notification count:', error));
}

// Get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Refresh notifications periodically (every 30 seconds)
setInterval(function() {
  const dropdown = document.getElementById('notif-dropdown');
  if (dropdown && dropdown.classList.contains('show')) {
    loadNotifications();
  }
  updateNotificationCount();
}, 30000);

// Initialize notification count on page load
document.addEventListener('DOMContentLoaded', function() {
  updateNotificationCount();
});
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