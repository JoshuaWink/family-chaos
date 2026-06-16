import { CupElement } from '../cup-element.js';

// ── CupCalendarEvent — positioned event pill (timeline + timegrid) ──
// Attributes: label, kind, tone, state, hidden, draggable
// CSS vars: --cup-event-bg (per-event background override)
//
// Timeline usage (absolute, positioned by parent via style.left/width):
//   const el = document.createElement('cup-calendar-event');
//   el.setAttribute('label', 'Stand-up');
//   el.setAttribute('kind', 'event');
//   el.setAttribute('tone', 'normal');
//   el.style.left  = '104px';
//   el.style.width = '50px';
//   container.appendChild(el);
//
// TimeGrid usage (absolute, positioned by cup-calendar via style.top/height):
//   <cup-calendar-event label="Standup" style="top:72px;height:46px"></cup-calendar-event>
//
// Drag-to-move fires CustomEvent 'cup-event-dragend' with { eventId, deltaSlots, deltaMinutes }
// Drag-to-resize fires CustomEvent 'cup-event-resize' with { eventId, newDurationMins }
//
class CupCalendarEvent extends CupElement {
  static get observedAttributes() {
    return ['label', 'kind', 'tone', 'state', 'hidden', 'draggable'];
  }

  connectedCallback() {
    this._slottedText = this.textContent.trim();
    super.connectedCallback();
    this._bindDrag();
  }

  render() {
    const label    = this.attr('label') || this._slottedText || '';
    const kind     = this.attr('kind')  || 'event';
    const tone     = this.attr('tone')  || 'normal';
    const state    = this.attr('state') || '';
    const hidden   = this.bool('hidden');
    const canDrag  = this.getAttribute('draggable') === 'true' ||
                     this.hasAttribute('draggable');

    const cls = CupElement.classList(
      'cup-cal-event',
      `cup-cal-event--${kind}`,
      tone  ? `cup-cal-event--${tone}`  : null,
      state ? `cup-cal-event--${state}` : null,
      hidden   ? 'cup-cal-event--hidden'   : null,
      canDrag  ? 'cup-cal-event--draggable': null,
    );

    this.className = 'cup-cal-event-host';
    this.innerHTML = `
      <div class="${cls}" role="button" tabindex="0">
        <span class="cup-cal-event___label">${this._escape(label)}</span>
        ${canDrag ? '<span class="cup-cal-event___resize-handle" aria-hidden="true"></span>' : ''}
      </div>`;
  }

  // ── Pointer-based drag-to-move ──────────────────────────────────
  _bindDrag() {
    let startX, startY, startLeft, startTop, dragging = false;

    const onPointerDown = (e) => {
      // Ignore resize-handle — handled separately
      if (e.target.classList.contains('cup-cal-event___resize-handle')) return;
      if (this.getAttribute('draggable') !== 'true' && !this.hasAttribute('draggable')) return;
      e.preventDefault();
      dragging  = true;
      startX    = e.clientX;
      startY    = e.clientY;
      startLeft = this.offsetLeft;
      startTop  = this.offsetTop;
      this.setPointerCapture(e.pointerId);
      this.classList.add('cup-cal-event--dragging');
    };

    const onPointerMove = (e) => {
      if (!dragging) return;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      this.style.left = `${startLeft + dx}px`;
      this.style.top  = `${startTop  + dy}px`;
    };

    const onPointerUp = (e) => {
      if (!dragging) return;
      dragging = false;
      this.classList.remove('cup-cal-event--dragging');
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      this.dispatchEvent(new CustomEvent('cup-event-dragend', {
        bubbles: true, composed: true,
        detail: { eventId: this.dataset.eventId, deltaX: dx, deltaY: dy },
      }));
    };

    this.addEventListener('pointerdown', onPointerDown);
    this.addEventListener('pointermove', onPointerMove);
    this.addEventListener('pointerup',   onPointerUp);

    // ── Resize handle drag ────────────────────────────────────────
    let resizing = false, resizeStartY = 0, resizeStartH = 0;

    this.addEventListener('pointerdown', (e) => {
      if (!e.target.classList.contains('cup-cal-event___resize-handle')) return;
      e.preventDefault();
      e.stopPropagation();
      resizing     = true;
      resizeStartY = e.clientY;
      resizeStartH = this.offsetHeight;
      this.setPointerCapture(e.pointerId);
      this.classList.add('cup-cal-event--resizing');
    });

    this.addEventListener('pointermove', (e) => {
      if (!resizing) return;
      const dy      = e.clientY - resizeStartY;
      const newH    = Math.max(20, resizeStartH + dy);
      this.style.height = `${newH}px`;
    });

    this.addEventListener('pointerup', (e) => {
      if (!resizing) return;
      resizing = false;
      this.classList.remove('cup-cal-event--resizing');
      const dy   = e.clientY - resizeStartY;
      const newH = Math.max(20, resizeStartH + dy);
      this.dispatchEvent(new CustomEvent('cup-event-resize', {
        bubbles: true, composed: true,
        detail: { eventId: this.dataset.eventId, newHeightPx: newH },
      }));
    });
  }

  _escape(text) {
    const probe = document.createElement('div');
    probe.textContent = String(text ?? '');
    return probe.innerHTML;
  }
}

customElements.define('cup-calendar-event', CupCalendarEvent);
export { CupCalendarEvent };
