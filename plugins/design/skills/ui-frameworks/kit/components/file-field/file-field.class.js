// @ts-check
/**
 * file-field.class.js: the file field's class. Importing it defines no element; file-field.js does that.
 *
 * The root is a plain element, not a form control (D14): the author's native file input, the child marked
 * data-part="input", carries the files, the name and the validity, is visible and works with no script (J118).
 * The field never creates, moves or wraps it. It disables the input while it is disabled itself (J120), and it
 * takes files dropped on it (J119): while files are dragged over it the root has `data-drag`; a drop gives the
 * input the files it would take (the first one only without `multiple`, and only the kinds `accept` names) and
 * dispatches `input`, then `change`, on the input.
 *
 * Rules: docs/specs/patterns.md, J118 to J121.
 */
import { UIElement } from '../../foundation/element.js';
import { props } from './file-field.props.js';

/** Whether a drag carries files. @param {DragEvent} event */
const hasFiles = (event) => !!event.dataTransfer && Array.from(event.dataTransfer.types ?? []).includes('Files');

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

export class UIFileField extends UIElement {
  static props = props;

  /**
   * Whether a file is one the `accept` list names: an extension (".pdf"), an exact type ("application/pdf") or a
   * type family ("image/*"), compared without regard to case. An empty list names everything.
   * @param {File} file @param {string} accept
   */
  static accepts(file, accept) {
    const tokens = accept.split(',').map((token) => token.trim().toLowerCase()).filter(Boolean);
    if (!tokens.length) return true;
    // File.type is lower case already, whatever the page wrote.
    const name = file.name.toLowerCase(), type = file.type;
    return tokens.some((token) => token.startsWith('.') ? name.endsWith(token)
      : token.endsWith('/*') ? type.startsWith(token.slice(0, -1))
      : type === token);
  }

  /**
   * The files an input would take from a drop of `files`.
   * @param {File[]} files @param {HTMLInputElement} input
   */
  static taken(files, input) {
    const kept = files.filter((file) => UIFileField.accepts(file, input.getAttribute('accept') ?? ''));
    return input.multiple ? kept : kept.slice(0, 1);
  }

  /** @type {WeakSet<HTMLInputElement>} The inputs this field disabled, so that it never enables one the author disabled. */
  #disabledHere = new WeakSet();

  /** The author's input, looked up each time (P6). @returns {HTMLInputElement | null} */
  #input() { return this.querySelector(':scope > input[data-part="input"]'); }

  /** Whether files can be dropped now. */
  #open() {
    const input = this.#input();
    return !!input && !input.disabled && !(/** @type {any} */ (this).disabled);
  }

  /** Brings the input's disabled state in step, and ends a drag the field can no longer take. */
  #sync() {
    const self = /** @type {any} */ (this);
    const input = this.#input();
    if (input) {
      if (self.disabled && !input.disabled) { input.disabled = true; this.#disabledHere.add(input); }
      else if (!self.disabled && this.#disabledHere.has(input)) { input.disabled = false; this.#disabledHere.delete(input); }
    }
    if (!this.#open()) this.removeAttribute('data-drag');
    // The root paints disabled when its input is, whoever disabled it, and invalid when its input is (J120, J121).
    put(this, 'aria-disabled', input?.disabled ? 'true' : null);
    put(this, 'invalid', input && (input.matches(':user-invalid') || input.getAttribute('aria-invalid') === 'true') ? '' : null);
  }

  /** @param {string} name */
  changed(name) {
    if (name === 'disabled' && this.isConnected) this.#sync();
  }

  connected() {
    /** @param {DragEvent} event */
    const over = (event) => {
      if (!hasFiles(event)) return;
      // Prevented even while disabled, so the page never navigates to the file; nothing is marked or taken.
      event.preventDefault();
      if (!this.#open()) { if (event.dataTransfer) event.dataTransfer.dropEffect = 'none'; return; }
      if (event.dataTransfer) event.dataTransfer.dropEffect = 'copy';
      this.setAttribute('data-drag', '');
    };
    this.listen(this, 'dragenter', over);
    this.listen(this, 'dragover', over);
    this.listen(this, 'dragleave', (/** @type {DragEvent} */ event) => {
      const to = event.relatedTarget;
      if (to instanceof Node && this.contains(to)) return;
      if (!to) {
        // Some engines give no relatedTarget: a point inside the field is a move between its children.
        const r = this.getBoundingClientRect();
        if (event.clientX > r.left && event.clientX < r.right && event.clientY > r.top && event.clientY < r.bottom) return;
      }
      this.removeAttribute('data-drag');
    });
    this.listen(this, 'drop', (/** @type {DragEvent} */ event) => {
      this.removeAttribute('data-drag');
      if (!hasFiles(event)) return;
      event.preventDefault();
      const input = this.#input();
      if (!input || !this.#open()) return;
      const files = UIFileField.taken(Array.from(event.dataTransfer?.files ?? []), input);
      if (!files.length) return;
      const list = new DataTransfer();
      for (const file of files) list.items.add(file);
      input.files = list.files;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });

    // The input's own events bring the invalid mark in step; invalid does not bubble.
    this.listen(this, 'change', () => this.#sync());
    this.listen(this, 'invalid', () => this.#sync(), { capture: true });
    this.listen(this.ownerDocument, 'reset', () => queueMicrotask(() => this.#sync()), { capture: true });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects. It sees an input that arrives, is replaced, or is disabled by the author.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'disabled', 'required', 'accept', 'multiple', 'aria-invalid'] });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
