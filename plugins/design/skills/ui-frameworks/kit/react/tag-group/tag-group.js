// @ts-check
/**
 * tag-group.js: the tag group for React (docs/specs/targets.md). A plain module that calls createElement; no build step.
 *
 * The root is a <div role="group">. Its focus stops are the remove controls of its tags: the author's elements
 * marked data-part="remove" inside a direct child. It mounts roving focus as the Web Component does, so one of
 * them is the Tab stop and the arrow keys, Home and End move among them without wrapping (J115).
 *
 * The group never removes a tag. A press on a remove control, and Delete or Backspace on one (React's onKeyDown),
 * dispatch `remove` on the group, bubbling, with the tag in `detail.tag`, and call `onRemove(tag, event)` with the
 * same event: one dispatch, so the page may listen with either (J116). When the tag that held focus leaves the group
 * the group moves focus to the control of the tag that followed it, else the one before, else the group, which takes
 * tabindex="-1" only for that moment. The page removes the tag by rendering without it; the group sees the node
 * leave, so it does not matter how the page removes it.
 *
 * A disabled group takes no focus and dispatches nothing: it renders aria-disabled="true" and inert (J117). The
 * `disabled` prop is not rendered as an attribute: aria-disabled is what the group's role allows (X2).
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { role } from '../../components/tag-group/tag-group.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'role'> & {
 *   disabled?: boolean,
 *   onRemove?: (tag: HTMLElement, event: CustomEvent<{ tag: HTMLElement }>) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} TagGroupProps
 */

const REMOVE = '[data-part="remove"]';
/** @param {Element} el */
const off = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

/** @param {TagGroupProps} props */
function TagGroupRoot({ disabled = false, onRemove, onClick, onKeyDown, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ disabled, onRemove });
  latest.current = { disabled, onRemove };

  /** The tag, a direct child of the group, that holds `el`. @param {Element | null} el @returns {HTMLElement | null} */
  const tagOf = (el) => {
    const group = root.current;
    let at = el;
    while (at && at.parentElement !== group) at = at.parentElement;
    return /** @type {HTMLElement | null} */ (at);
  };
  /** The remove controls of the group, in document order: those inside a direct child. @returns {HTMLElement[]} */
  const controls = () => /** @type {HTMLElement[]} */ ([...(root.current?.children ?? [])].flatMap((tag) => [...tag.querySelectorAll(REMOVE)]));
  /** Asks the page to remove the tag of a control. @param {Element} control */
  const ask = (control) => {
    if (latest.current.disabled || off(control)) return;
    const tag = tagOf(control);
    if (!tag) return;
    const event = new CustomEvent('remove', { detail: { tag }, bubbles: true, cancelable: true });
    /** @type {HTMLDivElement} */ (root.current).dispatchEvent(event);
    latest.current.onRemove?.(tag, event);
  };

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const stop = rovingFocus(el, {
      items: () => /** @type {HTMLElement[]} */ ([...el.children].flatMap((tag) => [...tag.querySelectorAll(REMOVE)])),
      skip: (item) => latest.current.disabled || off(item),
      wrap: false,
    });

    /** The tag, a direct child, that holds the focus; null while focus is elsewhere. @type {Element | null} */
    let held = null;
    let tabindex = false;
    /** The first remove control of the tags from `from` on, in `step` direction, that is still in the group. @param {Node | null} from @param {'nextSibling' | 'previousSibling'} step */
    const walk = (from, step) => {
      for (let at = from; at; at = at[step]) {
        if (at.parentNode !== el) return null;
        const control = /** @type {Element} */ (at).querySelector?.(REMOVE);
        if (control && !off(control)) return /** @type {HTMLElement} */ (control);
      }
      return null;
    };
    const focusSelf = () => {
      if (!el.hasAttribute('tabindex')) { el.setAttribute('tabindex', '-1'); tabindex = true; }
      el.focus();
    };

    const abort = new AbortController();
    const listen = { signal: abort.signal };
    el.addEventListener('focusin', (event) => { held = tagOf(/** @type {Element} */ (event.target)); }, listen);
    el.addEventListener('focusout', (event) => {
      if (tabindex && event.target === el) { el.removeAttribute('tabindex'); tabindex = false; }
      const to = event.relatedTarget;
      if (to instanceof Node) { held = null; return; }
      // Focus that leaves with nowhere to go is either a click on nothing or the removal of the focused tag, and
      // an engine may report the second before the tag has left. The observer settles that in a microtask; a tag
      // still in the group after a task, with focus outside, was a plain blur.
      setTimeout(() => { if (held?.parentNode === el && !el.contains(document.activeElement)) held = null; });
    }, listen);

    const observer = new MutationObserver((records) => {
      const was = held;
      if (!was || was.parentNode === el) return;
      const record = records.find((r) => [...r.removedNodes].includes(was));
      held = null;
      const next = walk(record?.nextSibling ?? null, 'nextSibling')
        ?? walk(record?.previousSibling ?? null, 'previousSibling')
        ?? [...el.children].flatMap((tag) => [...tag.querySelectorAll(REMOVE)]).find((control) => !off(control));
      if (next) /** @type {HTMLElement} */ (next).focus();
      else focusSelf();
    });
    observer.observe(el, { childList: true });
    return () => { stop(); abort.abort(); observer.disconnect(); };
  }, []);
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'tag-group',
    'aria-disabled': disabled ? 'true' : undefined,
    inert: disabled || /** @type {any} */ (rest).inert ? true : undefined,
    onClick: (/** @type {import('react').MouseEvent<HTMLDivElement>} */ event) => {
      onClick?.(event);
      const control = event.target instanceof Element ? event.target.closest(REMOVE) : null;
      if (control && controls().includes(/** @type {HTMLElement} */ (control))) ask(control);
    },
    onKeyDown: (/** @type {import('react').KeyboardEvent<HTMLDivElement>} */ event) => {
      onKeyDown?.(event);
      if (event.key !== 'Delete' && event.key !== 'Backspace') return;
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      const at = controls().find((control) => control === event.target);
      if (!at) return;
      event.preventDefault();
      ask(at);
    },
  }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const TagGroup = /* @__PURE__ */ Object.assign(TagGroupRoot, { kitRole: role, displayName: 'TagGroup' });
