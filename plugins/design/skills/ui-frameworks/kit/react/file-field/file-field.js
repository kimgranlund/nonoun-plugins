// @ts-check
/**
 * file-field.js: the file field for React (docs/specs/targets.md). A plain module that calls createElement; no build step.
 *
 * The root is a <div>, a plain element and not a form control (D14): the author's native file input, the child
 * marked data-part="input", carries the files, the name and the validity, is visible and works with no script
 * (J118). The component finds it in the DOM and never renders, clones, moves or wraps it. As the Web Component
 * does, it disables the input while the field is disabled (J120) and marks the root `aria-disabled` whenever the
 * input is disabled, whoever disabled it, and `invalid` while the input is (J121). It takes files dropped on it
 * (J119): while files are dragged over it the root has `data-drag`; a drop gives the input the files it would take
 * (the first only without `multiple`, and only the kinds `accept` names) and dispatches `input`, then `change`, on
 * the input, which React's onInput and onChange on the author's input hear. A drag is kept from navigating the
 * page even on a disabled field.
 *
 * Those writes are made in the DOM, as events arrive, so a listener sees them in the same task. The server
 * markup carries `disabled` of the prop, which the recipe selects; `aria-disabled` and `invalid` follow once the
 * input is known, as they do on the Web Component once it is defined (U2).
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   disabled?: boolean,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} FileFieldProps
 */

/** Whether a drag carries files. @param {DragEvent} event */
const hasFiles = (event) => !!event.dataTransfer && Array.from(event.dataTransfer.types ?? []).includes('Files');

/**
 * Sets or removes an attribute, only when it differs. An observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/**
 * Whether a file is one the `accept` list names: an extension (".pdf"), an exact type ("application/pdf") or a type
 * family ("image/*"), compared without regard to case. An empty list names everything.
 * @param {File} file @param {string} accept
 */
const accepts = (file, accept) => {
  const tokens = accept.split(',').map((token) => token.trim().toLowerCase()).filter(Boolean);
  if (!tokens.length) return true;
  const name = file.name.toLowerCase(), type = file.type;
  return tokens.some((token) => token.startsWith('.') ? name.endsWith(token)
    : token.endsWith('/*') ? type.startsWith(token.slice(0, -1))
    : type === token);
};

/** The files an input would take from a drop of `files`. @param {File[]} files @param {HTMLInputElement} input */
const taken = (files, input) => {
  const kept = files.filter((file) => accepts(file, input.getAttribute('accept') ?? ''));
  return input.multiple ? kept : kept.slice(0, 1);
};

/** @param {FileFieldProps} props */
export function FileField({ disabled = false, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef(disabled);
  latest.current = disabled;
  /** @type {import('react').RefObject<(() => void) | null>} */
  const sync = useRef(null);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    /** The inputs this field disabled, so that it never enables one the author disabled. */
    const disabledHere = new WeakSet();
    /** The author's input, looked up each time (P6). @returns {HTMLInputElement | null} */
    const input = () => el.querySelector(':scope > input[data-part="input"]');
    /** Whether files can be dropped now. */
    const open = () => {
      const field = input();
      return !!field && !field.disabled && !latest.current;
    };

    const update = () => {
      const field = input();
      if (field) {
        if (latest.current && !field.disabled) { field.disabled = true; disabledHere.add(field); }
        else if (!latest.current && disabledHere.has(field)) { field.disabled = false; disabledHere.delete(field); }
      }
      if (!open()) el.removeAttribute('data-drag');
      // The root paints disabled when its input is, whoever disabled it, and invalid when its input is (J120, J121).
      put(el, 'aria-disabled', field?.disabled ? 'true' : null);
      put(el, 'invalid', field && (field.matches(':user-invalid') || field.getAttribute('aria-invalid') === 'true') ? '' : null);
    };
    sync.current = update;

    const off = new AbortController();
    const listen = { signal: off.signal };
    /** @param {Event} raw */
    const over = (raw) => {
      const event = /** @type {DragEvent} */ (raw);
      if (!hasFiles(event)) return;
      // Prevented even while disabled, so the page never navigates to the file; nothing is marked or taken.
      event.preventDefault();
      if (!open()) { if (event.dataTransfer) event.dataTransfer.dropEffect = 'none'; return; }
      if (event.dataTransfer) event.dataTransfer.dropEffect = 'copy';
      el.setAttribute('data-drag', '');
    };
    el.addEventListener('dragenter', over, listen);
    el.addEventListener('dragover', over, listen);
    el.addEventListener('dragleave', (raw) => {
      const event = /** @type {DragEvent} */ (raw);
      const to = event.relatedTarget;
      if (to instanceof Node && el.contains(to)) return;
      if (!to) {
        // Some engines give no relatedTarget: a point inside the field is a move between its children.
        const r = el.getBoundingClientRect();
        if (event.clientX > r.left && event.clientX < r.right && event.clientY > r.top && event.clientY < r.bottom) return;
      }
      el.removeAttribute('data-drag');
    }, listen);
    el.addEventListener('drop', (raw) => {
      const event = /** @type {DragEvent} */ (raw);
      el.removeAttribute('data-drag');
      if (!hasFiles(event)) return;
      event.preventDefault();
      const field = input();
      if (!field || !open()) return;
      const files = taken(Array.from(event.dataTransfer?.files ?? []), field);
      if (!files.length) return;
      const list = new DataTransfer();
      for (const file of files) list.items.add(file);
      field.files = list.files;
      field.dispatchEvent(new Event('input', { bubbles: true }));
      field.dispatchEvent(new Event('change', { bubbles: true }));
    }, listen);

    // The input's own events bring the invalid mark in step; invalid does not bubble.
    el.addEventListener('change', update, listen);
    el.addEventListener('invalid', update, { capture: true, signal: off.signal });
    el.ownerDocument.addEventListener('reset', () => queueMicrotask(() => { if (!off.signal.aborted) update(); }), { capture: true, signal: off.signal });

    // The observer sees an input that arrives, is replaced, or is disabled by the author.
    const observer = new MutationObserver(update);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'disabled', 'required', 'accept', 'multiple', 'aria-invalid'] });
    update();
    return () => { off.abort(); observer.disconnect(); sync.current = null; };
  }, []);
  // The prop and the author's own markup can change at any render: bring the input and the mirrors in step.
  useLayoutEffect(() => { sync.current?.(); });
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'file-field', disabled: disabled ? true : undefined }), children);
}
