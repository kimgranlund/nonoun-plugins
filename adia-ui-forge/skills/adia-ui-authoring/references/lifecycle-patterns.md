# Lifecycle Patterns — Listeners, Timers, Observers, Popovers

Deep dive on symmetric `connected()` / `disconnected()` in AdiaUI components. Read when adding any side effect (listener, timer, observer, popover) to a component, or when inheriting from `AdiaFormElement`.

## The symmetry rule

Every side effect set up in `connected()` has a matching teardown in `disconnected()`. The teardown is authored at the same time as the setup, not later — if you leave `disconnected()` for tomorrow, tomorrow won't happen.

```javascript
class AdiaWidget extends AdiaElement {
  static properties = { /* ... */ };
  static template = () => null;

  #buttonEl = null;

  #onButtonClick = (e) => {
    this.dispatchEvent(new CustomEvent('widget-click', { bubbles: true }));
  };

  connected() {
    this.#buttonEl = this.querySelector('button');
    this.#buttonEl?.addEventListener('click', this.#onButtonClick);
  }

  disconnected() {
    this.#buttonEl?.removeEventListener('click', this.#onButtonClick);
    this.#buttonEl = null;
  }
}
```

Four things happen in `disconnected()`:

1. Remove the listener (reference equality via the `#onButtonClick` field).
2. Null the DOM reference (`this.#buttonEl = null`).
3. [Not shown] Clear any timers.
4. [Not shown] Disconnect any observers.

## Stable handlers — `#field` arrows, never inline arrows

`removeEventListener(type, handler)` requires reference equality on `handler`. Inline arrows create a fresh function every time:

```javascript
// WRONG — the inline arrow is a new function every render
this.#buttonEl.addEventListener('click', (e) => this.doThing(e));
// Later: removeEventListener can't match — no reference equality.

// RIGHT — stable reference via private field
#onButtonClick = (e) => this.doThing(e);
// connected:
this.#buttonEl.addEventListener('click', this.#onButtonClick);
// disconnected:
this.#buttonEl.removeEventListener('click', this.#onButtonClick);
```

The `#` prefix keeps the handler private to the class (can't be accidentally used as a public API). The arrow function form auto-binds `this`.

**Historical bugs this pattern prevents:**

- `cot.js:116` — summary click handler as inline arrow. Couldn't be removed; fixed by promoting to `#onSummaryClick`.
- Generic pattern across ~35 components in the audit cycle — all promoted to stable fields.

## Ephemeral DOM with inline arrows — the tolerance rule

There's ONE exception: inline arrows on DOM elements that are guaranteed to be fully detached + GC'd before the next re-render.

```javascript
// Tolerated: row is built fresh per render, parent's innerHTML
// replacement detaches the old subtree, GC collects both the
// node AND its listener.
#renderRows() {
  this.#container.innerHTML = '';
  for (const item of this.items) {
    const row = document.createElement('div');
    row.addEventListener('click', (e) => this.#onRowClick(item, e));
    this.#container.appendChild(row);
  }
}
```

**This is tolerated but not preferred.** If anything about the lifetime changes — if someone adds a `row.remove()` that leaves a cached reference, or converts to incremental DOM updates — the listeners stop getting GC'd and become leaks.

The safer pattern is event delegation on the stable parent:

```javascript
// Preferred — one listener on the parent, reads data-attributes
connected() {
  this.#container.addEventListener('click', this.#onContainerClick);
}

#onContainerClick = (e) => {
  const row = e.target.closest('[data-row-id]');
  if (!row) return;
  const item = this.items.find(i => i.id === row.dataset.rowId);
  this.#onRowClick(item, e);
};

disconnected() {
  this.#container.removeEventListener('click', this.#onContainerClick);
}
```

One listener, always removable, survives DOM churn.

## Timers — `setInterval`, `setTimeout`

Store the handle, clear it in `disconnected()`:

```javascript
#timerInterval = null;
#finishTimer = null;

connected() {
  this.#timerInterval = setInterval(() => this.#tick(), 1000);
}

disconnected() {
  if (this.#timerInterval != null) {
    clearInterval(this.#timerInterval);
    this.#timerInterval = null;
  }
  if (this.#finishTimer != null) {
    clearTimeout(this.#finishTimer);
    this.#finishTimer = null;
  }
}
```

The null-guard is defensive; `clearInterval(null)` is actually a no-op but the guard makes the "was it created?" intent explicit.

## Observers — ResizeObserver, MutationObserver, IntersectionObserver

Every observer has `.disconnect()`:

```javascript
#resizeObserver = null;

connected() {
  this.#resizeObserver = new ResizeObserver(() => this.#handleResize());
  this.#resizeObserver.observe(this);
}

disconnected() {
  this.#resizeObserver?.disconnect();
  this.#resizeObserver = null;
}
```

**Historical bug:** `chart.js` had TWO `disconnected()` methods — the second one silently overrode the first. The first had the `ResizeObserver.disconnect()` call; the second didn't. Chart listeners leaked until a production repro surfaced it.

**Lesson:** a class must declare `disconnected()` exactly once. If you need to add teardown, edit the existing method. Duplicate method names silently shadow — no error, no warning.

## `AdiaFormElement` — `super` discipline

Form-participating components inherit `ElementInternals` wiring from `AdiaFormElement`. That wiring only works if `super.connected()` and `super.disconnected()` are called:

```javascript
import { AdiaFormElement } from '../../core/form.js';

class AdiaInput extends AdiaFormElement {
  static properties = {
    ...AdiaFormElement.properties,
    placeholder: { type: String, default: '', reflect: true },
  };

  #inputEl = null;

  #onInput = () => this.syncValue(this.#inputEl?.value ?? '');

  connected() {
    super.connected(); // MUST — registers ElementInternals, form association
    this.#inputEl = this.querySelector('input');
    this.#inputEl?.addEventListener('input', this.#onInput);
  }

  disconnected() {
    super.disconnected(); // MUST — unregisters form participation
    this.#inputEl?.removeEventListener('input', this.#onInput);
    this.#inputEl = null;
  }
}
```

Omit `super.connected()` and the component won't participate in form submission — the field value is never collected, no validation fires, no form-reset handler runs. It's a silent failure; you only find out when form submission misses the field.

## Popovers, tooltips, document-level overlays

When a component creates elements OUTSIDE its own subtree (attached to `document.body`, or triggered via the Popover API), those elements don't GC with the component. Explicit cleanup is required:

```javascript
#tooltipEl = null;

#showTooltip(anchor) {
  this.#tooltipEl = document.createElement('div');
  this.#tooltipEl.popover = 'auto';
  document.body.appendChild(this.#tooltipEl);
  this.#tooltipEl.showPopover();
}

disconnected() {
  if (this.#tooltipEl) {
    this.#tooltipEl.remove(); // detaches from body
    this.#tooltipEl = null;
  }
}
```

Same rule for popovers anchored via CSS anchor-positioning, `<dialog>` elements appended to body, and any DOM node escaping the component's subtree.

## Global document listeners

Some components need to listen on `document` or `window` (e.g., a dropdown that closes on click-outside, a keyboard shortcut handler).

```javascript
#onDocumentClick = (e) => {
  if (!this.contains(e.target)) this.close();
};

#onDocumentKeydown = (e) => {
  if (e.key === 'Escape') this.close();
};

open() {
  document.addEventListener('click', this.#onDocumentClick);
  document.addEventListener('keydown', this.#onDocumentKeydown);
}

close() {
  document.removeEventListener('click', this.#onDocumentClick);
  document.removeEventListener('keydown', this.#onDocumentKeydown);
}

disconnected() {
  // Defensive: if component is ripped out while open, ensure global
  // listeners don't outlive it.
  document.removeEventListener('click', this.#onDocumentClick);
  document.removeEventListener('keydown', this.#onDocumentKeydown);
}
```

The `close()` method handles the happy path; `disconnected()` handles the rude-removal case.

## Pointer capture

For drag interactions, `setPointerCapture` + `releasePointerCapture`. Release in both the up handler AND as a defensive clear in `disconnected()`:

```javascript
#dragging = false;
#activePointerId = null;

#onPointerDown = (e) => {
  this.#dragging = true;
  this.#activePointerId = e.pointerId;
  this.setPointerCapture(e.pointerId);
  this.addEventListener('pointermove', this.#onPointerMove);
  this.addEventListener('pointerup', this.#onPointerUp);
};

#onPointerUp = (e) => {
  this.#dragging = false;
  this.releasePointerCapture(e.pointerId);
  this.removeEventListener('pointermove', this.#onPointerMove);
  this.removeEventListener('pointerup', this.#onPointerUp);
};

disconnected() {
  if (this.#activePointerId != null) {
    this.releasePointerCapture(this.#activePointerId);
  }
  this.removeEventListener('pointerdown', this.#onPointerDown);
  this.removeEventListener('pointermove', this.#onPointerMove);
  this.removeEventListener('pointerup', this.#onPointerUp);
}
```

## DOM-reference nulling — why it matters

A cached DOM reference (`this.#fooEl`) held by the component class keeps the referenced element alive for GC purposes, along with its own subtree. When the component is removed from the DOM, the old tree hangs around in memory until the component itself is garbage-collected.

Nulling the refs in `disconnected()` releases them eagerly:

```javascript
disconnected() {
  // ... remove listeners ...
  this.#inputEl = null;
  this.#buttonEl = null;
  this.#previewEl = null;
  this.#fileInput = null;
}
```

Especially important for components that are attached/detached frequently (modals, toasts, drawers) — each incarnation leaks its old subtree into memory if refs aren't released.

## Anti-patterns to watch for

- **Inline arrow + `removeEventListener`** — the listener isn't really being removed. Silent leak.
- **Forgot to create `disconnected()`** — if `connected()` adds side effects, `disconnected()` must exist. No exceptions.
- **Two `disconnected()` methods in the same class** — the second silently wins; the first's cleanup is lost.
- **`super.connected()` missing in `AdiaFormElement` subclass** — form participation silently fails.
- **Popover / tooltip never cleaned up** — stays in `document.body` forever.
- **Observer recreated on every render** — re-observing without disconnecting first leaks observer refs.
- **Timer fired after component removed** — not cleared in `disconnected()`, fires on a dead component. Can cause null-deref crashes or phantom re-renders.
