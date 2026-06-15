import { CupElement } from '../cup-element.js';

class CupCalendarRow extends CupElement {
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
    const row = data.row || {};
    const slots = Array.isArray(data.slots) ? data.slots : [];
    const personId = row.personId || '';
    const fullName = row.fullName || row.label || '';
    const label = row.label || fullName;
    const canDrive = row.canDrive !== false;

    this.className = 'cup-calendar-row-host';
    this.innerHTML = `
      <div class="cup-calendar-row">
        <button class="cup-calendar-row___label" type="button" data-gpid="${personId}" aria-label="${this._escape(fullName)} profile">
          <span class="cup-calendar-row___pulse" id="hap-${personId}"></span>
          <span class="cup-calendar-row___name">${this._escape(label)}</span>
          ${canDrive ? '' : '<span class="cup-calendar-row___note" aria-hidden="true">P</span>'}
        </button>
        <div class="cup-calendar-row___slots" id="row-${personId}">
          ${slots.map((slot) => {
            const classes = CupElement.classList(
              'cup-calendar-row___slot',
              slot.half ? 'cup-calendar-row___slot--half' : null
            );
            const labelText = slot.label || `slot ${slot.index + 1}`;
            return `<button class="${classes}" type="button" data-pid="${personId}" data-s="${slot.index}" aria-label="${this._escape(fullName)} ${this._escape(labelText)}"></button>`;
          }).join('')}
        </div>
      </div>
    `;
  }

  _escape(text) {
    const probe = document.createElement('div');
    probe.textContent = text;
    return probe.innerHTML;
  }
}

customElements.define('cup-calendar-row', CupCalendarRow);
export { CupCalendarRow };