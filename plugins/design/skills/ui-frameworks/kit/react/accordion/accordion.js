// @ts-check
/**
 * accordion.js: the element that stacks disclosures, for React (docs/specs/targets.md; rule J11 of
 * docs/specs/patterns.md).
 *
 * The root is a <div> with no role; its recipe stacks its children with a hairline between them. Its
 * disclosures are its child elements, whatever they are: one nested deeper belongs to whatever holds it. They are
 * of another family, so with `single` it finds them in the DOM, as the Web Component does: when one of them gains
 * `open`, from the user or from a script, it removes `open` from the others through their own author attribute
 * (G3), and a React disclosure follows that write. It renders no attribute a disclosure writes.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   single?: boolean,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} AccordionProps
 */

/** @param {AccordionProps} props */
export function Accordion({ single = false, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef(single);
  latest.current = single;

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const observer = new MutationObserver((records) => {
      if (!latest.current) return;
      /** @type {Element | null} The last child that gained open and still has it. */
      let opened = null;
      for (const r of records) {
        const target = /** @type {Element} */ (r.target);
        if (target.parentElement === el && r.oldValue === null && target.hasAttribute('open')) opened = target;
      }
      if (!opened) return;
      // Removing an attribute that is absent changes nothing and is not recorded, so this writes only what differs.
      for (const child of el.children) if (child !== opened) child.removeAttribute('open');
    });
    observer.observe(el, { subtree: true, attributes: true, attributeFilter: ['open'], attributeOldValue: true });
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'accordion', 'data-single': single ? '' : undefined }), children);
}
