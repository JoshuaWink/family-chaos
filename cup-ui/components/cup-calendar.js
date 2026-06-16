import { CupElement } from '../cup-element.js';

// ── Internal time utilities ───────────────────────────────────────
// Parse "HH:MM:SS" or "HH:MM" duration/time strings → total minutes
function _parseTimeMins(str) {
  if (!str) return 0;
  const parts = String(str).split(':').map(Number);
  return (parts[0] || 0) * 60 + (parts[1] || 0) + Math.floor((parts[2] || 0) / 60);
}

// Format minutes-from-midnight as "7:00 AM" style
function _minsToLabel(mins) {
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  const ampm = h < 12 ? 'AM' : 'PM';
  const h12 = h % 12 === 0 ? 12 : h % 12;
  return m === 0 ? `${h12} ${ampm}` : `${h12}:${String(m).padStart(2, '0')} ${ampm}`;
}

// Parse ISO date string or Date → { date, startMins } where startMins = mins from midnight
function _parseEventTime(val) {
  if (!val) return null;
  const d = (val instanceof Date) ? val : new Date(val);
  if (isNaN(d.getTime())) return null;
  return { date: d, startMins: d.getHours() * 60 + d.getMinutes() };
}

// How many slot-units does a duration span?
function _durationToSlots(durationMins, slotDurMins) {
  return Math.max(1, Math.ceil(durationMins / slotDurMins));
}

// ── CupCalendar — root host, data store, view router ─────────────
class CupCalendar extends CupElement {
  constructor() {
    super();
    // ── option store ──────────────────────────────────────────────
    this._opts = {
      view:           'timeline',      // 'timeline' | 'timeGridDay' | 'timeGridWeek'
      date:           null,            // current date (Date or ISO string, null = today)
      slotMinTime:    '07:00',         // first visible time
      slotMaxTime:    '23:00',         // last visible time  
      slotDuration:   '00:15:00',      // slot granularity
      editable:       false,
      // legacy timeline-mode dimensions (kept for Family Chaos compat)
      nameWidth:      176,
      slotWidth:      26,
      rowHeight:      46,
      // callbacks
      eventClick:     null,
      eventDrop:      null,
      eventResize:    null,
      dateClick:      null,
      resourceClick:  null,
    };
    this._events    = [];   // array of plain event objects
    this._resources = [];   // array of plain resource objects
    // ── legacy slot-index data (Family Chaos compat) ───────────────
    this._legacyData = null;
  }

  // ── Legacy API (Family Chaos — slot-index data model) ────────────
  // Keep .data = {...} working so Family Chaos doesn't need to change right now.
  set data(value) {
    this._legacyData = value || null;
    if (this.isConnected) this._scheduleRender();
  }
  get data() { return this._legacyData; }

  // ── Modern API ───────────────────────────────────────────────────
  setOption(key, value) {
    this._opts[key] = value;
    if (this.isConnected) this._scheduleRender();
  }

  getOption(key) { return this._opts[key]; }

  // Events
  addEvent(eventObj) {
    const ev = { ...eventObj, id: eventObj.id ?? `ev-${Date.now()}-${Math.random().toString(36).slice(2)}` };
    this._events.push(ev);
    if (this.isConnected) this._scheduleRender();
    return ev;
  }

  getEventById(id) {
    const ev = this._events.find(e => e.id === id) || null;
    if (!ev) return null;
    // Return a thin proxy with setProp helper
    const self = this;
    return {
      ...ev,
      setProp(prop, val) { ev[prop] = val; self._scheduleRender(); },
      setExtendedProp(prop, val) {
        ev.extendedProps = ev.extendedProps || {};
        ev.extendedProps[prop] = val;
        self._scheduleRender();
      },
      remove() { self.removeEvent(ev.id); },
    };
  }

  removeEvent(id) {
    this._events = this._events.filter(e => e.id !== id);
    if (this.isConnected) this._scheduleRender();
  }

  getEvents() { return [...this._events]; }

  // Resources
  setResources(resources) {
    this._resources = Array.isArray(resources) ? resources : [];
    if (this.isConnected) this._scheduleRender();
  }

  getResources() { return [...this._resources]; }

  // Navigation
  changeView(viewType) { this.setOption('view', viewType); }

  next() {
    const d = this._currentDate();
    d.setDate(d.getDate() + 7);
    this._opts.date = d;
    if (this.isConnected) this._scheduleRender();
  }

  prev() {
    const d = this._currentDate();
    d.setDate(d.getDate() - 7);
    this._opts.date = d;
    if (this.isConnected) this._scheduleRender();
  }

  today() {
    this._opts.date = new Date();
    if (this.isConnected) this._scheduleRender();
  }

  _currentDate() {
    if (this._opts.date instanceof Date) return new Date(this._opts.date);
    if (this._opts.date) return new Date(this._opts.date);
    return new Date();
  }

  // ── Derived slot geometry ─────────────────────────────────────────
  _slotGeometry() {
    const minMins  = _parseTimeMins(this._opts.slotMinTime);
    const maxMins  = _parseTimeMins(this._opts.slotMaxTime);
    const durMins  = _parseTimeMins(this._opts.slotDuration) || 15;
    const count    = Math.ceil((maxMins - minMins) / durMins);
    const slots    = [];
    for (let i = 0; i < count; i++) {
      const mins    = minMins + i * durMins;
      const mOfHr   = mins % 60;
      const isHour  = mOfHr === 0;
      const isHalf  = mOfHr === 30;
      slots.push({
        index: i,
        mins,
        label: isHour ? _minsToLabel(mins) : (isHalf ? '·' : ''),
        minor: !isHour && !isHalf,
        half:  isHalf,
        hour:  isHour,
      });
    }
    return { minMins, maxMins, durMins, count, slots };
  }

  // ── Main render ───────────────────────────────────────────────────
  render() {
    // If legacy slot-index data is set, delegate to legacy renderer
    if (this._legacyData) {
      this._renderLegacy();
      return;
    }

    const view = this._opts.view;
    if (view === 'timeGridDay' || view === 'timeGridWeek') {
      this._renderTimeGrid();
    } else {
      this._renderTimelineModern();
    }
  }

  // ── Legacy renderer — preserves exact Family Chaos slot-index behaviour ──
  _renderLegacy() {
    const data     = this._legacyData || {};
    const rows     = Array.isArray(data.rows)  ? data.rows  : [];
    const slots    = Array.isArray(data.slots) ? data.slots : [];
    const label    = data.label    || 'Calendar';
    const nameWidth = data.nameWidth ?? 176;
    const slotWidth = data.slotWidth ?? 26;
    const rowHeight = data.rowHeight ?? 46;

    this.style.setProperty('--cup-calendar-name-width',  `${nameWidth}px`);
    this.style.setProperty('--cup-calendar-slot-width',  `${slotWidth}px`);
    this.style.setProperty('--cup-calendar-row-height',  `${rowHeight}px`);
    this.className = 'cup-calendar-host';
    this.setAttribute('role', 'grid');
    this.setAttribute('aria-label', label);

    this.innerHTML = `
      <section class="cup-calendar">
        <div class="cup-calendar___head" aria-hidden="true">
          <div class="cup-calendar___name-spacer"></div>
          ${slots.map((slot) => {
            const cls = CupElement.classList(
              'cup-calendar___tick',
              slot.minor ? 'cup-calendar___tick--minor' : null,
              slot.half  ? 'cup-calendar___tick--half'  : null,
            );
            return `<div class="${cls}" data-slot-index="${slot.index}">${this._escape(slot.label || '')}</div>`;
          }).join('')}
        </div>
        ${rows.map((_, i) => `<cup-calendar-row data-row-index="${i}"></cup-calendar-row>`).join('')}
      </section>`;

    this.querySelectorAll('cup-calendar-row').forEach((rowEl, i) => {
      rowEl.data = { row: rows[i], slots };
    });
  }

  // ── Modern timeline renderer (resources as rows, time horizontal) ──
  _renderTimelineModern() {
    const geo       = this._slotGeometry();
    const resources = this._resources;
    const nameW     = this._opts.nameWidth;
    const slotW     = this._opts.slotWidth;
    const rowH      = this._opts.rowHeight;

    this.style.setProperty('--cup-calendar-name-width', `${nameW}px`);
    this.style.setProperty('--cup-calendar-slot-width', `${slotW}px`);
    this.style.setProperty('--cup-calendar-row-height', `${rowH}px`);
    this.className = 'cup-calendar-host';
    this.setAttribute('role', 'grid');

    const headTicks = geo.slots.map((slot) => {
      const cls = CupElement.classList(
        'cup-calendar___tick',
        slot.minor ? 'cup-calendar___tick--minor' : null,
        slot.half  ? 'cup-calendar___tick--half'  : null,
      );
      return `<div class="${cls}" data-slot-index="${slot.index}" data-mins="${slot.mins}">${this._escape(slot.label)}</div>`;
    }).join('');

    this.innerHTML = `
      <section class="cup-calendar">
        <div class="cup-calendar___head" aria-hidden="true">
          <div class="cup-calendar___name-spacer"></div>
          ${headTicks}
        </div>
        ${resources.map((_, i) => `<cup-calendar-row data-row-index="${i}"></cup-calendar-row>`).join('')}
      </section>`;

    this.querySelectorAll('cup-calendar-row').forEach((rowEl, i) => {
      rowEl.data = { row: resources[i], slots: geo.slots };
    });
  }

  // ── TimeGrid renderer (vertical time axis, Google Calendar style) ──
  _renderTimeGrid() {
    const geo       = this._slotGeometry();
    const view      = this._opts.view;
    const date      = this._currentDate();
    const editable  = this._opts.editable;
    const slotH     = 48; // px per hour — matches --cup-cal-hour-height
    const gutterW   = 72;
    const durPerPx  = 60 / slotH; // mins per pixel

    // Build day columns
    const days = view === 'timeGridWeek' ? this._weekDays(date) : [date];

    // Build hourly dividers from slotMinTime to slotMaxTime
    const minMins = geo.minMins;
    const maxMins = geo.maxMins;
    const totalH  = ((maxMins - minMins) / 60) * slotH;

    // Hour gutter labels
    const hourLabels = [];
    for (let m = minMins; m < maxMins; m += 60) {
      const pct = ((m - minMins) / 60) * slotH;
      hourLabels.push(`<div class="cup-tg___hour-label" style="top:${pct}px">${this._escape(_minsToLabel(m))}</div>`);
    }

    // Grid lines (hour + half-hour)
    const gridLines = [];
    for (let m = minMins; m < maxMins; m += 30) {
      const top  = ((m - minMins) / 60) * slotH;
      const half = (m % 60) === 30;
      gridLines.push(`<div class="cup-tg___line${half ? ' cup-tg___line--half' : ''}" style="top:${top}px"></div>`);
    }

    // Day column headers
    const colHeaders = days.map(d => {
      const isToday = this._isToday(d);
      return `<div class="cup-tg___col-header${isToday ? ' cup-tg___col-header--today' : ''}">
        <span class="cup-tg___weekday">${this._weekdayShort(d)}</span>
        <span class="cup-tg___date-num${isToday ? ' cup-tg___date-num--today' : ''}">${d.getDate()}</span>
      </div>`;
    }).join('');

    // Now-line position
    const now       = new Date();
    const nowMins   = now.getHours() * 60 + now.getMinutes();
    const nowTop    = ((nowMins - minMins) / 60) * slotH;
    const showNow   = nowMins >= minMins && nowMins < maxMins;
    const nowOnDay  = view === 'timeGridWeek'
      ? days.findIndex(d => this._isToday(d))
      : (this._isToday(days[0]) ? 0 : -1);

    // Event pills per column
    const colCells = days.map((d, colIndex) => {
      const dateStr = this._toDateStr(d);
      const dayEvents = this._events.filter(ev => {
        const s = _parseEventTime(ev.start);
        return s && this._toDateStr(s.date) === dateStr;
      });

      const pills = dayEvents.map(ev => {
        const s = _parseEventTime(ev.start);
        const e = _parseEventTime(ev.end);
        if (!s) return '';
        const topPx   = ((s.startMins - minMins) / 60) * slotH;
        const durMins = e ? (e.startMins - s.startMins) : 60;
        const htPx    = Math.max(20, (durMins / 60) * slotH - 2);
        const bg      = ev.backgroundColor || '';
        return `<cup-calendar-event
          data-event-id="${this._escape(String(ev.id))}"
          label="${this._escape(ev.title || '')}"
          style="top:${topPx}px;height:${htPx}px;${bg ? `--cup-event-bg:${bg};` : ''}"
          ${editable ? 'draggable' : ''}
        ></cup-calendar-event>`;
      }).join('');

      const nowLineHtml = (showNow && colIndex === nowOnDay)
        ? `<div class="cup-tg___now-circle" style="top:${nowTop - 5}px"></div>
           <div class="cup-tg___now-line"   style="top:${nowTop}px"></div>`
        : '';

      const slotButtons = geo.slots.map(slot =>
        `<button class="cup-tg___slot-btn" type="button"
          data-date="${dateStr}" data-mins="${slot.mins}"
          aria-label="${_minsToLabel(slot.mins)} ${dateStr}"></button>`
      ).join('');

      return `<div class="cup-tg___col" style="height:${totalH}px">
        ${slotButtons}
        ${gridLines.join('')}
        ${nowLineHtml}
        ${pills}
      </div>`;
    }).join('');

    this.className = 'cup-calendar-host cup-calendar-host--tg';
    this.setAttribute('role', 'grid');
    this.setAttribute('aria-label', 'Calendar');

    this.innerHTML = `
      <section class="cup-tg">
        <div class="cup-tg___toolbar-slot"></div>
        <div class="cup-tg___col-headers">
          <div class="cup-tg___gutter-spacer"></div>
          ${colHeaders}
        </div>
        <div class="cup-tg___body-wrap">
          <div class="cup-tg___gutter" style="height:${totalH}px">
            ${hourLabels.join('')}
          </div>
          <div class="cup-tg___cols">
            ${colCells}
          </div>
        </div>
      </section>`;

    // Bind slot clicks → dateClick callback
    const dateClickCb = this._opts.dateClick;
    if (dateClickCb) {
      this.querySelectorAll('.cup-tg___slot-btn').forEach(btn => {
        btn.addEventListener('click', (jsEvent) => {
          dateClickCb({
            date:    btn.dataset.date,
            mins:    Number(btn.dataset.mins),
            jsEvent,
            view:    { type: this._opts.view },
          });
        });
      });
    }

    // Bind event clicks → eventClick callback
    const eventClickCb = this._opts.eventClick;
    if (eventClickCb) {
      this.querySelectorAll('cup-calendar-event').forEach(el => {
        el.addEventListener('click', (jsEvent) => {
          const ev = this._events.find(e => String(e.id) === el.dataset.eventId);
          if (ev) eventClickCb({ event: ev, el, jsEvent, view: { type: this._opts.view } });
        });
      });
    }
  }

  // ── Date helpers ──────────────────────────────────────────────────
  _weekDays(date) {
    const d   = new Date(date);
    const day = d.getDay(); // 0=Sun
    d.setDate(d.getDate() - day);
    return Array.from({ length: 7 }, (_, i) => {
      const x = new Date(d);
      x.setDate(d.getDate() + i);
      return x;
    });
  }

  _isToday(date) {
    const t = new Date();
    return date.getDate() === t.getDate() &&
           date.getMonth() === t.getMonth() &&
           date.getFullYear() === t.getFullYear();
  }

  _toDateStr(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  _weekdayShort(date) {
    return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()];
  }

  _escape(text) {
    const probe = document.createElement('div');
    probe.textContent = String(text ?? '');
    return probe.innerHTML;
  }
}

customElements.define('cup-calendar', CupCalendar);
export { CupCalendar };