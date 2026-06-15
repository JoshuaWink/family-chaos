"""Self-contained HTML game UI served by SchedulingGameHttpServer at GET /."""

# Date used for the game day (all ISO start_time values use this date).
GAME_DATE = "2026-06-15"

GAME_UI_HTML: str = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Family Chaos — Scheduling Game</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f1117;--surf:#1a1d27;--surf2:#242838;--border:#2e3248;
  --accent:#7c6af7;--accent2:#f7931e;--text:#e2e8f0;--muted:#6b7280;
  --danger:#ef4444;--success:#22c55e;--warn:#f59e0b;
  --slot-w:44px;--row-h:46px;--name-w:176px;
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
/* grid */
#grid-area{flex:1;overflow:auto;min-height:0;min-width:0}
.hint{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:10px;color:var(--muted);text-align:center;padding:32px}
.hint p{font-size:15px;color:var(--text);font-weight:600}
.hint small{font-size:12px;max-width:300px;line-height:1.5}
.grid-wrap{padding:10px 14px;min-width:max-content}
.g-head{display:flex;padding-left:var(--name-w)}
.g-tlabel{width:var(--slot-w);font-size:9px;color:var(--muted);text-align:center;flex-shrink:0;padding-bottom:3px;border-right:1px solid var(--surf2)}
.g-row{display:flex;border-bottom:1px solid var(--border);height:var(--row-h)}.g-row:last-child{border-bottom:none}
.g-name{width:var(--name-w);min-width:var(--name-w);display:flex;align-items:center;gap:5px;padding:0 8px;font-size:11px;font-weight:600;border-right:1px solid var(--border);background:var(--surf);flex-shrink:0;cursor:pointer;height:100%;transition:background .1s}
.g-name:hover{background:var(--surf2)}
.g-name-text{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hap{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--muted);transition:background .3s}
.nd{font-size:9px;color:var(--danger);flex-shrink:0;cursor:default}
.g-slots{display:flex;position:relative;height:100%;flex:1}
.g-slot{width:var(--slot-w);height:100%;border-right:1px solid var(--surf2);flex-shrink:0;transition:background .1s;cursor:pointer}
.g-slot:hover{background:rgba(124,106,247,.12)}.g-slot.blocked{cursor:default;pointer-events:none}
.ev{position:absolute;top:3px;height:calc(100% - 6px);background:var(--accent);border-radius:4px;display:flex;align-items:center;padding:0 6px;font-size:9px;font-weight:700;white-space:nowrap;overflow:hidden;z-index:2;pointer-events:none;border:1px solid rgba(255,255,255,.1)}
.ev.conflict{background:var(--danger)}.ev.ok{background:var(--success)}
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
        Select a task, then click a time slot in the grid to assign it.
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
      <small>Schedule 12 tasks across 10 family members and helpers. Select a task in the panel, click a person&#39;s time slot to assign it, then Simulate to check for conflicts. Click person names in the grid to see full profiles.</small>
    </div>
  </div>
</div>
<div id="results" style="display:none"></div>
<div id="pov">
  <button class="pov-close" id="pov-close">&#10005;</button>
  <div id="pov-content"></div>
</div>
<script>
const DATE = '2026-06-15';
const SH = 7, EH = 21, SMIN = 30;
const SLOTS = (EH - SH) * 60 / SMIN;
const SW = 44;

const S = {
  id: null, people: [], tasks: [], allTasks: [],
  sched: {}, conflicts: new Set(), simDone: false,
  selTask: null, tab: 'tasks', icsTasks: [],
};

// ── helpers ───────────────────────────────────────────────────────────────────
function taskById(id) { return S.allTasks.find(t => t.task_id === id); }
function personById(id) { return S.people.find(p => p.person_id === id); }
function firstName(p) { return p ? p.name.replace(/ \\(.*?\\)$/, '').trim() : ''; }
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
  renderGrid();
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
    const notesDiv = t.notes ? '<div class="tc-notes">' + escH(t.notes) + '</div>' : '';
    return '<div class="tc' + (done ? ' done' : '') + (sel ? ' sel' : '') +
      '" data-tid="' + t.task_id + '">' +
      '<div class="tn">' + escH(t.description) + doneCheck + icsBadge + '</div>' +
      '<div class="tm">' + meta + '</div>' +
      notesDiv + '</div>';
  }).join('');
  const panel = document.getElementById('tasks-panel');
  panel.innerHTML = html;
  panel.querySelectorAll('[data-tid]').forEach(el => {
    el.addEventListener('click', () => pickTask(el.dataset.tid));
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

// ── grid ──────────────────────────────────────────────────────────────────────
function renderGrid() {
  const area = document.getElementById('grid-area');
  if (!S.people.length) return;
  const hint = document.getElementById('grid-hint');
  if (hint) hint.style.display = 'none';
  let h = '<div class="grid-wrap">';
  h += '<div class="g-head"><div style="width:var(--name-w);flex-shrink:0"></div>';
  for (let s = 0; s < SLOTS; s++) {
    h += '<div class="g-tlabel">' + (s % 2 === 0 ? slotLabel(s) : '') + '</div>';
  }
  h += '</div>';
  for (const p of S.people) {
    const noDriver = !p.can_drive ? '<span class="nd" title="Cannot drive">P</span>' : '';
    h += '<div class="g-row">';
    h += '<div class="g-name" data-gpid="' + p.person_id + '">' +
      '<span class="hap" id="hap-' + p.person_id + '" title="Workload indicator"></span>' +
      '<span class="g-name-text">' + escH(p.name.replace(/ \\(.*?\\)$/, '')) + '</span>' +
      noDriver + '</div>';
    h += '<div class="g-slots" id="row-' + p.person_id + '">';
    for (let s = 0; s < SLOTS; s++) {
      h += '<div class="g-slot" data-pid="' + p.person_id + '" data-s="' + s + '"></div>';
    }
    h += '</div></div>';
  }
  h += '</div>';
  area.innerHTML = h;
  area.querySelectorAll('[data-gpid]').forEach(el => {
    el.addEventListener('click', e => { e.stopPropagation(); showPOV(el.dataset.gpid); });
  });
  area.querySelectorAll('[data-s]').forEach(el => {
    el.addEventListener('click', () => assignSlot(el.dataset.pid, +el.dataset.s));
  });
  refreshOverlays();
}

function refreshOverlays() {
  document.querySelectorAll('.ev').forEach(e => e.remove());
  document.querySelectorAll('.g-slot').forEach(el => el.classList.remove('blocked'));
  for (const [tid, ev] of Object.entries(S.sched)) {
    const task = taskById(tid);
    if (!task) continue;
    const row = document.getElementById('row-' + ev.person_id);
    if (!row) continue;
    const wSlots = Math.ceil(task.duration_minutes / SMIN);
    const isCon = S.conflicts.has(tid);
    const cls = 'ev' + (isCon ? ' conflict' : (S.simDone ? ' ok' : ''));
    const block = document.createElement('div');
    block.className = cls;
    block.style.left = (ev.slot * SW) + 'px';
    block.style.width = (wSlots * SW - 2) + 'px';
    const label = task.description.length > 20 ? task.description.slice(0, 18) + '\u2026' : task.description;
    block.textContent = label;
    block.title = task.description + ' (' + task.duration_minutes + 'm)';
    row.appendChild(block);
    for (let s = ev.slot; s < ev.slot + wSlots && s < SLOTS; s++) {
      const sl = row.querySelector('[data-s="' + s + '"]');
      if (sl) sl.classList.add('blocked');
    }
  }
  updateHappiness();
}

// ── task interaction ──────────────────────────────────────────────────────────
function pickTask(id) {
  if (S.sched[id]) return;
  S.selTask = S.selTask === id ? null : id;
  renderTaskPanel();
}

async function assignSlot(personId, slot) {
  if (!S.selTask) { toast('Select a task from the left panel first.'); return; }
  const tid = S.selTask;
  const task = taskById(tid);
  if (!task || S.sched[tid]) return;
  const wSlots = Math.ceil(task.duration_minutes / SMIN);
  if (slot + wSlots > SLOTS) { toast('Task extends past 9 PM \u2014 pick an earlier slot.', true); return; }
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
    renderTaskPanel(); renderPeoplePanel(); refreshOverlays(); updateBadge();
    document.getElementById('results').style.display = 'none';
  } catch (e) { toast('Error: ' + e.message, true); }
}

function isOccupied(personId, slot, durationMin) {
  const w = Math.ceil(durationMin / SMIN);
  for (const [tid, ev] of Object.entries(S.sched)) {
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

// ── happiness ─────────────────────────────────────────────────────────────────
function updateHappiness() {
  S.people.forEach(p => {
    const dot = document.getElementById('hap-' + p.person_id);
    if (!dot) return;
    const n = Object.values(S.sched).filter(e => e.person_id === p.person_id).length;
    if (n === 0) { dot.style.background = 'var(--muted)'; dot.title = 'No tasks assigned yet'; }
    else if (n <= 2) { dot.style.background = 'var(--success)'; dot.title = 'Reasonable workload (' + n + ' tasks)'; }
    else if (n <= 4) { dot.style.background = 'var(--warn)'; dot.title = 'Getting busy (' + n + ' tasks)'; }
    else { dot.style.background = 'var(--danger)'; dot.title = 'Heavy workload! (' + n + ' tasks)'; }
  });
}

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
    refreshOverlays();
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
