import { CupElement } from '../cup-element.js';

class CupCalendar extends CupElement {
  constructor() {
    super();
    this._data = null;
  }

  set data(value) {
    this._data = value || null;
    if (this.isConnected) this._scheduleRender();
  }

  get data() {
    return this._data;
  }

  render() {
    const data = this._data || {};
    const rows = Array.isArray(data.rows) ? data.rows : [];
    const slots = Array.isArray(data.slots) ? data.slots : [];
    const label = data.label || 'Calendar';
    const nameWidth = data.nameWidth || 176;
    const slotWidth = data.slotWidth || 26;
    const rowHeight = data.rowHeight || 46;

    this.style.setProperty('--cup-calendar-name-width', `${nameWidth}px`);
    this.style.setProperty('--cup-calendar-slot-width', `${slotWidth}px`);
    this.style.setProperty('--cup-calendar-row-height', `${rowHeight}px`);
    this.className = 'cup-calendar-host';
    this.setAttribute('role', 'grid');
    this.setAttribute('aria-label', label);

    this.innerHTML = `
      <section class="cup-calendar">
        <div class="cup-calendar___head" aria-hidden="true">
          <div class="cup-calendar___name-spacer"></div>
          ${slots.map((slot) => {
            const classes = CupElement.classList(
              'cup-calendar___tick',
              slot.minor ? 'cup-calendar___tick--minor' : null,
              slot.half ? 'cup-calendar___tick--half' : null
            );
            return `<div class="${classes}" data-slot-index="${slot.index}">${this._escape(slot.label || '')}</div>`;
          }).join('')}
        </div>
        ${rows.map((row, index) => `<cup-calendar-row data-row-index="${index}"></cup-calendar-row>`).join('')}
      </section>
    `;

    this.querySelectorAll('cup-calendar-row').forEach((rowEl, index) => {
      rowEl.data = { row: rows[index], slots };
    });
  }

  _escape(text) {
    const probe = document.createElement('div');
    probe.textContent = text;
    return probe.innerHTML;
  }
}

customElements.define('cup-calendar', CupCalendar);
export { CupCalendar };