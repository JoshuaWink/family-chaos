import { CupElement } from '../cup-element.js';

class CupCalendarBlock extends CupElement {
  static get observedAttributes() {
    return ['label', 'kind', 'tone', 'state', 'hidden'];
  }

  connectedCallback() {
    this._slottedText = this.textContent.trim();
    super.connectedCallback();
  }

  render() {
    const label = this.attr('label') || this._slottedText || '';
    const kind = this.attr('kind') || 'event';
    const tone = this.attr('tone') || 'normal';
    const state = this.attr('state') || '';
    const hidden = this.bool('hidden');

    const classes = CupElement.classList(
      'cup-calendar-block',
      `cup-calendar-block--${kind}`,
      tone ? `cup-calendar-block--${tone}` : null,
      state ? `cup-calendar-block--${state}` : null,
      hidden ? 'cup-calendar-block--hidden' : null
    );

    this.className = 'cup-calendar-block-host';
    this.innerHTML = `<div class="${classes}">${this._escape(label)}</div>`;
  }

  _escape(text) {
    const probe = document.createElement('div');
    probe.textContent = text;
    return probe.innerHTML;
  }
}

customElements.define('cup-calendar-block', CupCalendarBlock);
export { CupCalendarBlock };