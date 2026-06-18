"""Self-contained HTML game UI served by SchedulingGameHttpServer at GET /."""

# Date used for the game day (all ISO start_time values use this date).
GAME_DATE = "2026-06-15"

GAME_UI_HTML: str = """\
<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Family Chaos — Scheduling Game</title>
<link rel="stylesheet" href="/cup-ui/cup.css">
<script type="module" src="/cup-ui/cup.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f1117;--surf:#1a1d27;--surf2:#242838;--border:#2e3248;
  --accent:#7c6af7;--accent2:#f7931e;--text:#e2e8f0;--muted:#6b7280;
  --danger:#ef4444;--success:#22c55e;--warn:#f59e0b;
  /* Bridge game palette → cup tokens so the calendar inherits the dark theme */
  --cup-color-bg:#0f1117;
  --cup-color-surface:#1a1d27;
  --cup-color-surface-alt:#242838;
  --cup-color-border:#2e3248;
  --cup-color-fg:#e2e8f0;
  --cup-color-secondary:#6b7280;
  --cup-color-primary:#7c6af7;
}
html,body{height:100%;overflow:hidden}
body{background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,sans-serif;font-size:13px;display:flex;flex-direction:column}
/* header */
header{background:var(--surf);border-bottom:1px solid var(--border);padding:8px 14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;flex-shrink:0}
.logo{font-size:16px;font-weight:800;color:var(--accent);flex:1;min-width:150px}
.badge{background:var(--surf2);border:1px solid var(--border);border-radius:5px;padding:2px 8px;font-size:11px;color:var(--muted)}
.btn{padding:6px 12px;border-radius:6px;border:1px solid transparent;font-size:12px;font-weight:700;cursor:pointer;transition:all .12s;white-space:nowrap}
.btn-p{background:var(--accent);color:#fff}.btn-p:hover{background:#6859e0}
.btn-g{background:#16a34a;color:#fff}.btn-g:hover{background:#15803d}
.btn-o{background:var(--surf2);color:var(--text);border-color:var(--border)}.btn-o:hover{background:var(--border)}
.btn:disabled{opacity:.4;cursor:not-allowed}
/* workspace */
.ws{display:flex;flex:1;min-height:0;overflow:hidden}
/* left panel */
#left{width:272px;min-width:220px;background:var(--surf);border-right:1px solid var(--border);display:flex;flex-direction:column;flex-shrink:0}
.tabs{display:flex;border-bottom:1px solid var(--border);flex-shrink:0}
.tab{flex:1;padding:8px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);cursor:pointer;text-align:center;border-bottom:2px solid transparent;transition:all .12s}
.tab.on{color:var(--accent);border-bottom-color:var(--accent)}
.tab-body{overflow-y:auto;flex:1}
/* task cards */
.tc{padding:9px 11px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .1s;user-select:none}
.tc:hover{background:var(--surf2)}
.tc.sel{background:rgba(124,106,247,.15);border-left:3px solid var(--accent);padding-left:8px}
.tc.done{opacity:.38;pointer-events:none}
.tn{font-weight:600;font-size:12px;line-height:1.3;margin-bottom:4px;display:flex;align-items:center;gap:5px;flex-wrap:wrap}
.ics-badge{background:rgba(247,147,30,.2);color:var(--accent2);border:1px solid rgba(247,147,30,.35);border-radius:3px;font-size:9px;padding:1px 4px;font-weight:700;flex-shrink:0}
.tm{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:2px}
.tm span{background:var(--surf2);border-radius:3px;padding:1px 5px;font-size:10px;color:var(--muted)}
.tm .for-who{color:#a78bfa;background:rgba(167,139,250,.12);font-weight:600}
.tm .res{color:var(--accent2)}
.tc-notes{font-size:10px;color:var(--muted);line-height:1.6;margin-top:5px;padding-top:5px;border-top:1px solid var(--border);display:none}
.tc.sel .tc-notes{display:block}
/* task tooltip — override shared nowrap so long text wraps inside the card */
.cup-cal-tooltip .cup-cal-ev-card___title{white-space:normal;overflow:visible;text-overflow:unset}
.cup-cal-tooltip .cup-cal-ev-card___text{white-space:normal;overflow:visible;text-overflow:unset;overflow-wrap:anywhere;word-break:break-word}
/* people cards */
.pc{padding:10px 12px;border-bottom:1px solid var(--border);cursor:pointer;user-select:none;transition:background .1s}
.pc:hover{background:var(--surf2)}
.pc.act{background:rgba(124,106,247,.1);border-left:3px solid var(--accent);padding-left:9px}
.pc-head{display:flex;align-items:center;gap:5px;margin-bottom:2px}
.pc-name{font-weight:700;font-size:12px;flex:1}
.age-badge{background:var(--surf2);border:1px solid var(--border);border-radius:10px;font-size:10px;padding:1px 6px;color:var(--muted)}
.pc-occ{font-size:10px;color:var(--muted);margin-bottom:2px}
.pc-sched{font-size:10px;color:var(--muted);margin-bottom:2px}
.pc-drive{font-size:10px;margin-bottom:2px}
.dy{color:var(--success)}.dn{color:var(--danger)}
.pc-detail{display:none;margin-top:5px;padding-top:5px;border-top:1px solid var(--border)}
.pc.act .pc-detail{display:block}
.pc-bio{font-size:10px;color:var(--muted);line-height:1.6;margin-bottom:5px}
.pc-likes{font-size:10px;color:var(--muted)}.pc-likes em{color:var(--accent);font-style:normal}
.pc-load{font-size:10px;color:var(--muted);margin-top:4px}
/* grid area — sized container, cup-calendar fills it (mirrors .demo-cal-wrap in cup-calendar-demo.html) */
#grid-area{flex:1;min-height:0;min-width:0;overflow:hidden;border:1px solid var(--cup-color-border,var(--border));background:var(--cup-color-surface,var(--surf));display:flex;flex-direction:column}
#game-cal{flex:1;min-height:0;height:100%}
.hint{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:10px;color:var(--muted);text-align:center;padding:32px}
.hint p{font-size:15px;color:var(--text);font-weight:600}
.hint small{font-size:12px;max-width:300px;line-height:1.5}
/* Override cup-calendar resource label style to match game theme */
.cup-tg-h___label,.cup-tg___col-header{background:var(--surf)}
.cup-tg___resource-label{color:var(--text);font-size:11px;font-weight:600}
.cup-tg___resource-label:hover{background:var(--surf2)}
/* Contact card (matches cup-calendar-demo.html #contact-cards) */
.cc-card{display:flex;flex-direction:column;gap:0;min-width:260px;max-width:300px;font-size:12px;line-height:1.5;color:var(--cup-color-on-surface,var(--text))}
.cc-header{display:flex;align-items:flex-start;gap:12px;padding:14px 14px 10px}
.cc-avatar{width:48px;height:48px;border-radius:50%;flex-shrink:0;object-fit:cover}
.cc-name{font-size:14px;font-weight:700;color:var(--cup-color-on-surface,var(--text));line-height:1.2}
.cc-role{font-size:11px;color:var(--cup-color-secondary,var(--muted));margin-top:1px}
.cc-status-row{display:flex;align-items:center;gap:5px;margin-top:5px}
.cc-status-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.cc-status-label{font-size:10px;font-weight:600;letter-spacing:.03em}
.cc-bio{padding:8px 14px 10px;font-size:11px;color:var(--cup-color-secondary,var(--muted));line-height:1.5;border-top:1px solid rgba(255,255,255,.07)}
.cc-body{border-top:1px solid rgba(255,255,255,.07);padding:8px 14px 4px;display:grid;gap:5px}
.cc-row{display:flex;align-items:flex-start;gap:8px}
.cc-icon{flex-shrink:0;width:14px;text-align:center;opacity:.7;line-height:1.5}
.cc-text{color:var(--cup-color-secondary,var(--muted));flex:1;min-width:0;overflow-wrap:anywhere;word-break:break-word;white-space:normal}
.cc-footer{border-top:1px solid rgba(255,255,255,.07);padding:7px 14px 10px;display:flex;align-items:center;justify-content:space-between}
.cc-event-bar{display:flex;align-items:center;gap:6px}
.cc-event-dots{display:flex;gap:3px}
.cc-event-dot{width:6px;height:6px;border-radius:50%;background:var(--cup-color-primary,var(--accent));opacity:.35}
.cc-event-dot--filled{opacity:1}
.cc-event-count{font-size:10px;color:var(--cup-color-secondary,var(--muted))}
/* person overlay */
#pov{display:none;position:fixed;z-index:100;background:var(--surf);border:1px solid var(--border);border-radius:10px;padding:18px 18px 14px;width:288px;box-shadow:0 8px 30px rgba(0,0,0,.6);max-height:76vh;overflow-y:auto}
.pov-close{position:absolute;top:10px;right:12px;cursor:pointer;color:var(--muted);font-size:18px;background:none;border:none;line-height:1;padding:0}
.pov-name{font-size:15px;font-weight:800;color:var(--text);margin-bottom:1px}
.pov-sub{font-size:11px;color:var(--muted);margin-bottom:10px}
.pov-sec{margin-top:9px}
.pov-lbl{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:3px}
.pov-val{font-size:11px;color:var(--text);line-height:1.6}
/* results */
#results{background:var(--surf);border-top:1px solid var(--border);padding:10px 14px;max-height:160px;overflow-y:auto;flex-shrink:0}
#results h3{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:6px}
.citem{background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.22);border-radius:5px;padding:6px 10px;margin-bottom:4px;font-size:11px;color:#fca5a5;line-height:1.5}
.valid-msg{color:var(--success);font-weight:700;font-size:13px}
.info{color:var(--muted);font-size:11px;margin-top:5px}
.toast{position:fixed;bottom:20px;right:20px;background:#1a2035;border:1px solid var(--border);border-radius:8px;padding:9px 14px;font-size:12px;z-index:999;max-width:280px;line-height:1.4;pointer-events:none}
.toast.err{border-color:var(--danger);color:#fca5a5}
</style>
</head>
<body>
<header>
  <span class="logo" id="app-title">&#128197; Family Chaos</span>
  <span class="badge" id="app-status">Ready to play</span>
  <span class="badge" id="pbadge" style="display:none">0/12 scheduled</span>
  <input type="file" id="ics-input" accept=".ics" style="display:none">
  <button class="btn btn-o" id="btn-ics" disabled onclick="document.getElementById('ics-input').click()" title="Import events from a Google Calendar .ics export">&#128197; Import .ics</button>
  <button class="btn btn-p" id="btn-new" onclick="startGame()">New Game</button>
  <button class="btn btn-g" id="btn-sim" disabled onclick="runSim()">&#9654; Simulate</button>
</header>
<div class="ws">
  <div id="left">
    <div class="tabs">
      <div class="tab on" id="tab-tasks" onclick="switchTab('tasks')">Tasks</div>
      <div class="tab" id="tab-people" onclick="switchTab('people')">People</div>
    </div>
    <div class="tab-body" id="tasks-panel">
      <p style="padding:14px;color:var(--muted);font-size:11px;line-height:1.7">
        Press <strong style="color:var(--text)">New Game</strong> to load the Smith family scenario.
        Select a task, then click a slot to place it. Click a placed block to pick it up and move it. Press Esc to deselect.
      </p>
    </div>
    <div class="tab-body" id="people-panel" style="display:none">
      <p style="padding:14px;color:var(--muted);font-size:11px;line-height:1.7">
        Press <strong style="color:var(--text)">New Game</strong> to meet the Smith family.
        Click any person card to expand their profile.
      </p>
    </div>
  </div>
  <div id="grid-area">
    <div class="hint" id="grid-hint">
      <p>Press New Game to begin</p>
      <small>Schedule tasks across family members. Select a task in the left panel, then click a time slot on the calendar to assign it. Drag placed events to reschedule. Press Simulate to check for conflicts.</small>
    </div>
    <cup-calendar id="game-cal" style="display:none"></cup-calendar>
  </div>
</div>
<div id="results" style="display:none"></div>
<div id="pov">
  <button class="pov-close" id="pov-close">&#10005;</button>
  <div id="pov-content"></div>
</div>
<script>
const DATE = '2026-06-15';
const SH = 7, EH = 23, SMIN = 30;
const EH_LABEL = (EH - 12) + ' PM';

const S = {
  id: null, people: [], tasks: [], allTasks: [],
  sched: {}, conflicts: new Set(), simDone: false,
  selTask: null, tab: 'tasks', icsTasks: [],
};

// ── helpers ───────────────────────────────────────────────────────────────────
function taskById(id) { return S.allTasks.find(t => t.task_id === id); }
function personById(id) { return S.people.find(p => p.person_id === id); }
function firstName(p) { return p ? p.name.replace(/ \\(.*?\\)$/, '').trim() : ''; }

// ── Contact card helpers (mirror cup-calendar-demo.html buildContactCard) ─────
const _CC_PALETTE = ['#7c3aed','#0ea5e9','#10b981','#f59e0b','#ec4899','#ef4444','#06b6d4','#8b5cf6','#22c55e','#f43f5e'];
function ccColorFor(id) {
  const s = String(id || '');
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return _CC_PALETTE[h % _CC_PALETTE.length];
}
function ccInitials(name) {
  return String(name || '').split(/\\s+/).map(w => w[0] || '').join('').slice(0, 2).toUpperCase();
}
function ccHumanizeLocation(loc) {
  if (!loc) return 'Unknown';
  return String(loc).replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
}
function slotMin(s) { return SH * 60 + s * SMIN; }
function slotIso(s) {
  const m = slotMin(s);
  return DATE + 'T' + String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0') + ':00';
}
function slotLabel(s) {
  const m = slotMin(s), h = Math.floor(m / 60), mn = m % 60;
  return (h > 12 ? h - 12 : h) + ':' + String(mn).padStart(2, '0') + (h < 12 ? 'a' : 'p');
}
function escH(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ── game lifecycle ────────────────────────────────────────────────────────────
async function startGame() {
  const btn = document.getElementById('btn-new');
  btn.disabled = true; btn.textContent = 'Loading\u2026';
  Object.assign(S, { id: null, people: [], tasks: [], allTasks: [], sched: {},
    conflicts: new Set(), simDone: false, selTask: null, icsTasks: [] });
  try {
    const r = await fetch('/game/new', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ difficulty: 'normal' })
    });
    const d = await r.json();
    S.id = d.session_id; S.people = d.people; S.tasks = d.tasks; S.allTasks = [...d.tasks];
    document.getElementById('app-status').textContent = 'Family Chaos \u2014 Normal';
    document.getElementById('pbadge').style.display = '';
    document.getElementById('btn-sim').disabled = false;
    document.getElementById('btn-ics').disabled = false;
    document.getElementById('results').style.display = 'none';
    document.getElementById('ics-input').onchange = onICSFile;
    await initCalendar();
    renderAll();
    toast('Game started! Select a task, then click a time slot to schedule it.', false);
  } catch (e) {
    toast('Failed to start: ' + e.message, true);
  } finally {
    btn.disabled = false; btn.textContent = 'New Game';
  }
}

function renderAll() {
  renderTaskPanel();
  renderPeoplePanel();
  syncCalendar();
  updateBadge();
}

// ── tabs ──────────────────────────────────────────────────────────────────────
function switchTab(tab) {
  S.tab = tab;
  document.getElementById('tab-tasks').className = 'tab' + (tab === 'tasks' ? ' on' : '');
  document.getElementById('tab-people').className = 'tab' + (tab === 'people' ? ' on' : '');
  document.getElementById('tasks-panel').style.display = tab === 'tasks' ? '' : 'none';
  document.getElementById('people-panel').style.display = tab === 'people' ? '' : 'none';
}

// ── task panel ────────────────────────────────────────────────────────────────
function renderTaskPanel() {
  if (!S.allTasks.length) return;
  const html = S.allTasks.map(t => {
    const done = !!S.sched[t.task_id];
    const sel = S.selTask === t.task_id;
    const forP = t.for_person_id ? personById(t.for_person_id) : null;
    const forStr = forP ? firstName(forP) : null;
    let meta = '';
    if (forStr) meta += '<span class="for-who">For: ' + escH(forStr) + '</span>';
    meta += '<span>&#128205; ' + escH(t.location || 'home') + '</span>';
    meta += '<span>&#9201; ' + t.duration_minutes + 'm</span>';
    if (t.travel_minutes > 0) meta += '<span>&#128663; ~' + t.travel_minutes + 'min travel</span>';
    if (t.resource_id) meta += '<span class="res">&#128666; ' + escH(t.resource_id) + '</span>';
    const icsBadge = t.is_ics ? '<span class="ics-badge">ICS</span>' : '';
    const doneCheck = done ? ' \u2713' : '';
    return '<div class="tc' + (done ? ' done' : '') + (sel ? ' sel' : '') +
      '" data-tid="' + t.task_id + '">' +
      '<div class="tn">' + escH(t.description) + doneCheck + icsBadge + '</div>' +
      '<div class="tm">' + meta + '</div>' +
      '</div>';
  }).join('');
  const panel = document.getElementById('tasks-panel');
  panel.innerHTML = html;
  panel.querySelectorAll('[data-tid]').forEach(el => {
    el.addEventListener('click', () => pickTask(el.dataset.tid));
    bindTaskTooltip(el);
  });
}

// Task tooltip — reuses cup-calendar's event-detail card markup so the
// task hover matches the event pill tooltip exactly.
const _TASK_TIP = { el: null, showT: null, hideT: null, owner: null };
function _clearTaskTipTimers() {
  if (_TASK_TIP.showT) { clearTimeout(_TASK_TIP.showT); _TASK_TIP.showT = null; }
  if (_TASK_TIP.hideT) { clearTimeout(_TASK_TIP.hideT); _TASK_TIP.hideT = null; }
}
function _removeTaskTip() {
  _clearTaskTipTimers();
  if (_TASK_TIP.el) { _TASK_TIP.el.remove(); _TASK_TIP.el = null; }
  _TASK_TIP.owner = null;
}
function taskTooltipHtml(t) {
  const forP = t.for_person_id ? personById(t.for_person_id) : null;
  const rows = [];
  rows.push('<div class="cup-cal-ev-card___row">'
    + '<span class="cup-cal-ev-card___icon">🕐</span>'
    + '<span class="cup-cal-ev-card___text">' + t.duration_minutes + ' min'
    + (t.travel_minutes > 0 ? ' <span class="cup-cal-ev-card___dim">(+' + t.travel_minutes + ' min travel)</span>' : '')
    + '</span></div>');
  if (forP) {
    rows.push('<div class="cup-cal-ev-card___row">'
      + '<span class="cup-cal-ev-card___icon">👤</span>'
      + '<span class="cup-cal-ev-card___text">For ' + escH(firstName(forP)) + '</span>'
      + '</div>');
  }
  if (t.location) {
    rows.push('<div class="cup-cal-ev-card___row">'
      + '<span class="cup-cal-ev-card___icon">📍</span>'
      + '<span class="cup-cal-ev-card___text">' + escH(ccHumanizeLocation(t.location)) + '</span>'
      + '</div>');
  }
  if (t.resource_id) {
    rows.push('<div class="cup-cal-ev-card___row">'
      + '<span class="cup-cal-ev-card___icon">🚚</span>'
      + '<span class="cup-cal-ev-card___text">' + escH(ccHumanizeLocation(t.resource_id)) + '</span>'
      + '</div>');
  }
  if (t.notes) {
    rows.push('<div class="cup-cal-ev-card___row cup-cal-ev-card___row--desc">'
      + '<span class="cup-cal-ev-card___icon">📝</span>'
      + '<span class="cup-cal-ev-card___text">' + escH(t.notes) + '</span>'
      + '</div>');
  }
  const badges = t.is_ics
    ? '<div class="cup-cal-ev-card___badges"><span class="cup-cal-ev-card___badge cup-cal-ev-card___badge--normal">ICS</span></div>'
    : '';
  return '<div class="cup-cal-ev-card">'
    + '<div class="cup-cal-ev-card___head">'
    +   '<span class="cup-cal-ev-card___stripe" style="background:var(--accent)"></span>'
    +   '<div class="cup-cal-ev-card___title-wrap">'
    +     '<span class="cup-cal-ev-card___title">' + escH(t.description) + '</span>'
    +     badges
    +   '</div>'
    + '</div>'
    + '<div class="cup-cal-ev-card___body">' + rows.join('') + '</div>'
    + '</div>';
}
function _showTaskTip(card, t) {
  if (_TASK_TIP.el) _TASK_TIP.el.remove();
  const tip = document.createElement('div');
  tip.className = 'cup-cal-tooltip';
  tip.innerHTML = taskTooltipHtml(t);
  document.body.appendChild(tip);
  const pr  = card.getBoundingClientRect();
  const tr  = tip.getBoundingClientRect();
  const gap = 8;
  let left  = pr.right + gap;
  if (left + tr.width > window.innerWidth - 8) left = pr.left - tr.width - gap;
  if (left < 8) left = 8;
  let top   = pr.top;
  if (top + tr.height > window.innerHeight - 8) top = window.innerHeight - tr.height - 8;
  if (top < 8) top = 8;
  tip.style.top  = top  + 'px';
  tip.style.left = left + 'px';
  tip.addEventListener('mouseenter', _clearTaskTipTimers);
  tip.addEventListener('mouseleave', () => { _TASK_TIP.hideT = setTimeout(_removeTaskTip, 120); });
  _TASK_TIP.el = tip;
  _TASK_TIP.owner = card;
}
function bindTaskTooltip(card) {
  const tid = card.dataset.tid;
  card.addEventListener('mouseenter', () => {
    _clearTaskTipTimers();
    if (_TASK_TIP.owner === card && _TASK_TIP.el) return;
    const t = taskById(tid);
    if (!t) return;
    const delay = _TASK_TIP.el ? 0 : 300;
    _TASK_TIP.showT = setTimeout(() => _showTaskTip(card, t), delay);
  });
  card.addEventListener('mouseleave', () => {
    _clearTaskTipTimers();
    _TASK_TIP.hideT = setTimeout(_removeTaskTip, 140);
  });
}

// ── people panel ──────────────────────────────────────────────────────────────
function renderPeoplePanel() {
  if (!S.people.length) return;
  const html = S.people.map(p => {
    const driveEl = p.can_drive
      ? '<span class="dy">&#9989; Can drive</span>'
      : '<span class="dn">&#10006; Needs a driver</span>';
    const pd = p.primary_driver_id ? personById(p.primary_driver_id) : null;
    const pdStr = pd ? ' \u2014 usually ' + escH(firstName(pd)) : '';
    const tasksFor = S.allTasks.filter(t => t.for_person_id === p.person_id);
    const schedFor = tasksFor.filter(t => S.sched[t.task_id]);
    const loadN = Object.values(S.sched).filter(e => e.person_id === p.person_id).length;
    return '<div class="pc" data-pid="' + p.person_id + '">' +
      '<div class="pc-head">' +
      '<span class="pc-name">' + escH(p.name) + '</span>' +
      (p.age > 0 ? '<span class="age-badge">' + p.age + '</span>' : '') +
      '</div>' +
      (p.occupation ? '<div class="pc-occ">' + escH(p.occupation) + '</div>' : '') +
      (p.work_schedule ? '<div class="pc-sched">&#128336; ' + escH(p.work_schedule) + '</div>' : '') +
      '<div class="pc-drive">' + driveEl + pdStr + '</div>' +
      '<div class="pc-detail">' +
      (p.bio ? '<div class="pc-bio">' + escH(p.bio) + '</div>' : '') +
      (p.likes ? '<div class="pc-likes">Enjoys: <em>' + escH(p.likes) + '</em></div>' : '') +
      (loadN > 0 ? '<div class="pc-load">Assigned: ' + loadN + ' task(s)' +
        (tasksFor.length ? ' | ' + schedFor.length + '/' + tasksFor.length + ' personal tasks scheduled' : '') +
        '</div>' : '') +
      '</div></div>';
  }).join('');
  const panel = document.getElementById('people-panel');
  panel.innerHTML = html;
  panel.querySelectorAll('[data-pid]').forEach(el => {
    el.addEventListener('click', () => {
      el.classList.toggle('act');
      const det = el.querySelector('.pc-detail');
      if (det) det.style.display = el.classList.contains('act') ? 'block' : 'none';
    });
  });
}

// ── cup-calendar integration ──────────────────────────────────────────────────
let _calReady = false;

async function initCalendar() {
  await customElements.whenDefined('cup-calendar');
  _calReady = true;
  const cal = document.getElementById('game-cal');
  cal.style.display = '';
  cal.style.height = '100%';
  const hint = document.getElementById('grid-hint');
  if (hint) hint.style.display = 'none';

  cal.setOption('view', 'resourceTimeline');
  cal.setOption('slotMinTime', String(SH).padStart(2, '0') + ':00');
  cal.setOption('slotMaxTime', String(EH).padStart(2, '0') + ':00');
  cal.setOption('slotDuration', '00:30:00');
  cal.setOption('editable', true);
  cal.setOption('showTooltips', true);
  cal.setOption('showEventModal', false);

  cal.setResources(S.people.map(p => ({
    id: p.person_id,
    title: p.name.replace(/ \\(.*?\\)$/, '').trim() + (!p.can_drive ? ' \\u24c5' : ''),
  })));

  cal.setOption('resourceClick', ({ resourceId }) => showPOV(resourceId));

  cal.setOption('resourceTooltip', ({ resourceId }) => {
    const p = personById(resourceId);
    if (!p) return null;
    const pd = p.primary_driver_id ? personById(p.primary_driver_id) : null;
    const taskLoad = Object.values(S.sched).filter(e => e.person_id === resourceId).length;
    const tasksFor = S.allTasks.filter(t => t.for_person_id === resourceId);
    const schedFor = tasksFor.filter(t => S.sched[t.task_id]);

    const name = firstName(p);
    const initials = ccInitials(name);
    const color = ccColorFor(p.person_id);
    const roleText = p.occupation ? p.occupation + (p.age > 0 ? ' \u00b7 age ' + p.age : '') : '';
    const driveColor = p.can_drive ? '#22c55e' : '#f59e0b';
    const driveLabel = p.can_drive
      ? 'Available to drive'
      : 'Needs transport' + (pd ? ' \u00b7 ' + escH(firstName(pd)) : '');

    const avatarSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">'
      + '<circle cx="24" cy="24" r="24" fill="' + color + '"/>'
      + '<text x="24" y="30" text-anchor="middle" font-family="system-ui,sans-serif" font-size="16" font-weight="700" fill="white">' + escH(initials) + '</text>'
      + '</svg>';
    const avatarSrc = 'data:image/svg+xml;base64,' + btoa(avatarSvg);

    const dotsMax = 5;
    const filled  = Math.min(dotsMax, taskLoad);
    const dotsHtml = Array.from({ length: dotsMax }, (_, i) =>
      '<span class="cc-event-dot' + (i < filled ? ' cc-event-dot--filled' : '') + '"></span>'
    ).join('');
    const personalStr = tasksFor.length
      ? ' \u00b7 ' + schedFor.length + '/' + tasksFor.length + ' personal'
      : '';

    const bioHtml = p.bio ? '<div class="cc-bio">' + escH(p.bio) + '</div>' : '';
    const driverRow = pd
      ? '<div class="cc-row"><span class="cc-icon">&#x1F697;</span><span class="cc-text">Driver: ' + escH(firstName(pd)) + '</span></div>'
      : '';
    const likesRow = p.likes
      ? '<div class="cc-row"><span class="cc-icon">&#x2764;&#xFE0F;</span><span class="cc-text">' + escH(p.likes) + '</span></div>'
      : '';

    return '<div class="cc-card">'
      + '<div class="cc-header">'
      +   '<img class="cc-avatar" src="' + avatarSrc + '" alt="' + escH(initials) + '" width="48" height="48">'
      +   '<div style="min-width:0;flex:1">'
      +     '<div class="cc-name">' + escH(name) + '</div>'
      +     (roleText ? '<div class="cc-role">' + escH(roleText) + '</div>' : '')
      +     '<div class="cc-status-row">'
      +       '<span class="cc-status-dot" style="background:' + driveColor + '"></span>'
      +       '<span class="cc-status-label" style="color:' + driveColor + '">' + driveLabel + '</span>'
      +     '</div>'
      +   '</div>'
      + '</div>'
      + bioHtml
      + '<div class="cc-body">'
      +   '<div class="cc-row"><span class="cc-icon">&#x1F3E0;</span><span class="cc-text">' + escH(ccHumanizeLocation(p.home_location)) + '</span></div>'
      +   (p.work_schedule ? '<div class="cc-row"><span class="cc-icon">&#x1F551;</span><span class="cc-text">' + escH(p.work_schedule) + '</span></div>' : '')
      +   driverRow
      +   likesRow
      + '</div>'
      + '<div class="cc-footer">'
      +   '<div class="cc-event-bar">'
      +     '<div class="cc-event-dots">' + dotsHtml + '</div>'
      +     '<span class="cc-event-count">' + taskLoad + ' task' + (taskLoad === 1 ? '' : 's') + personalStr + '</span>'
      +   '</div>'
      + '</div>'
      + '</div>';
  });

  cal.setOption('dateClick', ({ resourceId, mins }) => {
    const slot = Math.floor((mins - SH * 60) / SMIN);
    assignSlot(resourceId, slot);
  });

  cal.setOption('eventClick', ({ event }) => {
    pickupEvent(String(event.id));
  });

  cal.setOption('eventDrop', ({ event, newStart, newResourceId }) => {
    const tid = String(event.id);
    const task = taskById(tid);
    if (!task) return;
    const slot = Math.floor((newStart - SH * 60) / SMIN);
    if (isOccupied(newResourceId, slot, task.duration_minutes, tid)) {
      toast('That slot is already occupied.', true);
      syncCalendar();
      return;
    }
    S.sched[tid] = { person_id: newResourceId, slot };
    S.simDone = false;
    S.conflicts = new Set();
    document.getElementById('results').style.display = 'none';
    renderTaskPanel(); renderPeoplePanel(); updateBadge(); syncCalendar();
    const body = {
      task_id: tid, person_id: newResourceId,
      start_time: slotIso(slot), duration_minutes: task.duration_minutes,
      location: task.location,
    };
    if (task.resource_id) body.resource_id = task.resource_id;
    fetch('/game/' + S.id + '/schedule', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    }).then(r => r.json()).then(d => {
      if (!d.ok) toast('Could not move event: ' + (d.error || '?'), true);
    }).catch(e => toast('Error: ' + e.message, true));
  });

  syncCalendar();
}

function syncCalendar() {
  if (!_calReady) return;
  const cal = document.getElementById('game-cal');
  if (!cal) return;
  const events = [];
  for (const [tid, ev] of Object.entries(S.sched)) {
    const task = taskById(tid);
    if (!task) continue;
    const isCon = S.conflicts.has(tid);
    const color = isCon ? '#ef4444' : (S.simDone ? '#22c55e' : (task.is_ics ? '#f7931e' : '#7c6af7'));
    events.push({
      id: tid,
      title: task.description,
      startMins: slotMin(ev.slot),
      durationMins: task.duration_minutes,
      resourceId: ev.person_id,
      color,
      description: task.notes || '',
    });
  }
  cal.setEvents(events);
}

// ── task interaction ──────────────────────────────────────────────────────────
function pickTask(id) {
  if (S.sched[id]) return;
  S.selTask = S.selTask === id ? null : id;
  renderTaskPanel();
}

function pickupEvent(tid) {
  delete S.sched[tid];
  S.selTask = tid;
  S.simDone = false;
  S.conflicts = new Set();
  renderTaskPanel(); renderPeoplePanel(); syncCalendar(); updateBadge();
  document.getElementById('results').style.display = 'none';
  toast('Picked up \u2014 click a new slot to place, or Esc to cancel.');
}

async function assignSlot(personId, slot) {
  if (!S.selTask) { toast('Select a task from the left panel first.'); return; }
  const tid = S.selTask;
  const task = taskById(tid);
  if (!task || S.sched[tid]) return;
  const wSlots = Math.ceil(task.duration_minutes / SMIN);
  const maxSlot = (EH - SH) * 60 / SMIN;
  if (slot + wSlots > maxSlot) { toast('Task extends past ' + EH_LABEL + ' \u2014 pick an earlier slot.', true); return; }
  if (isOccupied(personId, slot, task.duration_minutes)) {
    toast('That person is already busy at that time.', true); return;
  }
  try {
    const body = {
      task_id: tid, person_id: personId, start_time: slotIso(slot),
      duration_minutes: task.duration_minutes, location: task.location,
    };
    if (task.resource_id) body.resource_id = task.resource_id;
    const r = await fetch('/game/' + S.id + '/schedule', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    const d = await r.json();
    if (!d.ok) { toast('Could not schedule: ' + (d.error || '?'), true); return; }
    S.sched[tid] = { person_id: personId, slot };
    S.selTask = null; S.conflicts = new Set(); S.simDone = false;
    renderTaskPanel(); renderPeoplePanel(); syncCalendar(); updateBadge();
    document.getElementById('results').style.display = 'none';
  } catch (e) { toast('Error: ' + e.message, true); }
}

function isOccupied(personId, slot, durationMin, excludeTid) {
  const w = Math.ceil(durationMin / SMIN);
  for (const [tid, ev] of Object.entries(S.sched)) {
    if (excludeTid && tid === excludeTid) continue;
    if (ev.person_id !== personId) continue;
    const t = taskById(tid);
    const ew = Math.ceil((t ? t.duration_minutes : 30) / SMIN);
    if (slot < ev.slot + ew && slot + w > ev.slot) return true;
  }
  return false;
}

// ── person overlay ────────────────────────────────────────────────────────────
function showPOV(personId) {
  const p = personById(personId);
  if (!p) return;
  const pd = p.primary_driver_id ? personById(p.primary_driver_id) : null;
  const loadN = Object.values(S.sched).filter(e => e.person_id === personId).length;
  const tasksFor = S.allTasks.filter(t => t.for_person_id === personId);
  const schedFor = tasksFor.filter(t => S.sched[t.task_id]);
  const driveStr = p.can_drive ? '\u2705 Licensed driver' : '\u274c Cannot drive \u2014 needs transport';
  const pdStr = pd ? '<br>Primary driver: ' + escH(pd.name) : '';
  document.getElementById('pov-content').innerHTML =
    '<div class="pov-name">' + escH(p.name) + '</div>' +
    '<div class="pov-sub">' + escH(p.occupation || '') +
      (p.age > 0 ? ' &mdash; age ' + p.age : '') + '</div>' +
    (p.work_schedule ? '<div class="pov-sec"><div class="pov-lbl">Schedule</div><div class="pov-val">' + escH(p.work_schedule) + '</div></div>' : '') +
    (p.bio ? '<div class="pov-sec"><div class="pov-lbl">Background</div><div class="pov-val">' + escH(p.bio) + '</div></div>' : '') +
    '<div class="pov-sec"><div class="pov-lbl">Driver Status</div><div class="pov-val">' + driveStr + pdStr + '</div></div>' +
    (p.likes ? '<div class="pov-sec"><div class="pov-lbl">Enjoys</div><div class="pov-val">' + escH(p.likes) + '</div></div>' : '') +
    '<div class="pov-sec"><div class="pov-lbl">Today\\'s Load</div><div class="pov-val">' +
    loadN + ' task(s) assigned to them' +
    (tasksFor.length ? '<br>' + schedFor.length + ' of ' + tasksFor.length + ' personal tasks scheduled' : '') +
    '</div></div>';
  const ov = document.getElementById('pov');
  ov.style.top = '76px'; ov.style.right = '16px'; ov.style.left = 'auto';
  ov.style.display = 'block';
}

document.getElementById('pov-close').addEventListener('click', () => {
  document.getElementById('pov').style.display = 'none';
});
document.addEventListener('click', e => {
  const ov = document.getElementById('pov');
  if (ov.style.display !== 'none' && !ov.contains(e.target) && !e.target.closest('[data-gpid]')) {
    ov.style.display = 'none';
  }
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && S.selTask) {
    S.selTask = null;
    renderTaskPanel();
    toast('Deselected \u2014 task not placed.');
  }
});

// ── simulation ────────────────────────────────────────────────────────────────
function fmtConflict(c) {
  const type = c.type || '';
  if (type === 'double_booking') {
    const p = personById(c.person_id);
    const ta = taskById(c.task_a), tb = taskById(c.task_b);
    return '<b>Double booking:</b> ' + escH(p ? p.name : c.person_id) +
      ' has \u201c' + escH(ta ? ta.description : c.task_a) +
      '\u201d and \u201c' + escH(tb ? tb.description : c.task_b) + '\u201d overlapping.';
  }
  if (type === 'travel_buffer') {
    const p = personById(c.person_id);
    const ta = taskById(c.from_task), tb = taskById(c.to_task);
    return '<b>Travel gap:</b> ' + escH(p ? p.name : c.person_id) +
      ' needs 30+ min between \u201c' + escH(ta ? ta.description : c.from_task) +
      '\u201d and \u201c' + escH(tb ? tb.description : c.to_task) + '\u201d (different locations).';
  }
  if (type === 'resource_conflict') {
    const ta = taskById(c.task_a), tb = taskById(c.task_b);
    return '<b>Resource conflict:</b> \u201c' + escH(ta ? ta.description : c.task_a) +
      '\u201d and \u201c' + escH(tb ? tb.description : c.task_b) +
      '\u201d both need <em>' + escH(c.resource_id) + '</em> at the same time.';
  }
  return escH(JSON.stringify(c));
}

async function runSim() {
  if (!S.id) return;
  const btn = document.getElementById('btn-sim');
  btn.disabled = true; btn.textContent = 'Running\u2026';
  try {
    const r = await fetch('/game/' + S.id + '/simulate', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}'
    });
    const d = await r.json();
    const panel = document.getElementById('results');
    panel.style.display = '';
    S.simDone = true;
    if (d.is_valid) {
      S.conflicts = new Set();
      panel.innerHTML = '<h3>Simulation Result</h3>' +
        '<div class="valid-msg">\u2713 Schedule is valid \u2014 no conflicts!</div>' +
        '<div class="info">' + d.scheduled_count + ' event(s) checked across ' + S.people.length + ' people.</div>';
    } else {
      S.conflicts = new Set();
      (d.conflicts || []).forEach(c => {
        if (c.task_a) S.conflicts.add(c.task_a);
        if (c.task_b) S.conflicts.add(c.task_b);
        if (c.from_task) S.conflicts.add(c.from_task);
        if (c.to_task) S.conflicts.add(c.to_task);
      });
      const items = (d.conflicts || []).map(c => '<div class="citem">\u26a0 ' + fmtConflict(c) + '</div>').join('');
      panel.innerHTML = '<h3>Simulation Result \u2014 ' + (d.conflicts || []).length + ' Conflict(s)</h3>' +
        items + '<div class="info">Conflicting tasks highlighted in red. Reschedule and simulate again.</div>';
    }
    syncCalendar();
  } catch (e) { toast('Simulation error: ' + e.message, true); }
  finally { btn.disabled = false; btn.textContent = '\u25b6 Simulate'; }
}

// ── ICS import ────────────────────────────────────────────────────────────────
function onICSFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => processICS(e.target.result);
  reader.readAsText(file);
  event.target.value = '';
}

function processICS(text) {
  const events = parseICS(text);
  if (!events.length) { toast('No VEVENT blocks found in this .ics file.', true); return; }
  const added = events.map((ev, i) => ({
    task_id: 'ics_' + Date.now() + '_' + i,
    description: ev.summary,
    duration_minutes: Math.max(15, Math.min(ev.duration, 480)),
    location: ev.location || 'home',
    resource_id: null, for_person_id: null, travel_minutes: 0,
    notes: (ev.description ? ev.description + ' ' : '') + '[Imported from Google Calendar]',
    is_ics: true,
  }));
  S.icsTasks = [...S.icsTasks, ...added];
  S.allTasks = [...S.tasks, ...S.icsTasks];
  renderTaskPanel(); updateBadge();
  toast(added.length + ' event(s) imported. Select from task panel to schedule.', false);
}

function parseICS(text) {
  const events = [];
  const norm = text.split('\\r\\n').join('\\n').split('\\r').join('\\n');
  const blocks = norm.split('BEGIN:VEVENT');
  for (let i = 1; i < blocks.length; i++) {
    const lines = blocks[i].split('\\n');
    const get = key => {
      const line = lines.find(l => l.startsWith(key + ':') || l.startsWith(key + ';'));
      if (!line) return null;
      const idx = line.indexOf(':');
      return idx >= 0 ? line.slice(idx + 1).trim() : null;
    };
    const dtstart = get('DTSTART'), dtend = get('DTEND');
    let duration = 60;
    if (dtstart && dtend) {
      const clean = s => {
        const d = s.replace(/Z$/, '');
        if (d.length === 8) return d.slice(0, 4) + '-' + d.slice(4, 6) + '-' + d.slice(6);
        return d.slice(0, 4) + '-' + d.slice(4, 6) + '-' + d.slice(6, 8) + 'T' + d.slice(9, 11) + ':' + d.slice(11, 13) + ':' + d.slice(13, 15);
      };
      const ms = new Date(clean(dtend)) - new Date(clean(dtstart));
      if (!isNaN(ms) && ms > 0) duration = Math.round(ms / 60000);
    }
    const summary = get('SUMMARY');
    if (!summary && !dtstart) continue;
    events.push({
      summary: summary || 'Imported event',
      location: get('LOCATION') || 'home',
      description: get('DESCRIPTION') || '',
      duration,
    });
  }
  return events;
}

// ── misc ──────────────────────────────────────────────────────────────────────
function updateBadge() {
  const n = Object.keys(S.sched).length;
  document.getElementById('pbadge').textContent = n + '/' + S.allTasks.length + ' scheduled';
}

function toast(msg, err) {
  const el = document.createElement('div');
  el.className = 'toast' + (err ? ' err' : '');
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3200);
}
</script>
</body>
</html>"""
