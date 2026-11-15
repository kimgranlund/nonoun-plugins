// @ts-check
/**
 * accordion.class.js: the class of the element that stacks disclosures. Importing it defines no element;
 * accordion.js does that.
 *
 * It has no role and paints nothing; the recipe stacks its children with a hairline between them. Its
 * disclosures are its child elements, whatever their tag: one nested deeper belongs to whatever holds it (J11).
 * With `single`, when one of them gains `open`, from the user or from a script, it removes `open` from the
 * others, through their own author attribute (G3). An observer on its subtree, filtered to `open`, tells it.
 *
 * Rules: docs/specs/patterns.md, J11.
 */
import { UIElement } from '../../foundation/element.js';
import { props, role, tabindex } from './accordion.props.js';

export class UIAccordion extends UIElement {
  static props = props;
  static role = role;
  static tabindex = tabindex;

  /**
   * Closes every child but the one that opened last, when the accordion is single.
   * @param {MutationRecord[]} records
   */
  #opened(records) {
    if (!this.hasAttribute('single')) return;
    /** @type {Element | null} The last child that gained open and still has it. */
    let opened = null;
    for (const r of records) {
      const el = /** @type {Element} */ (r.target);
      if (el.parentElement === this && r.oldValue === null && el.hasAttribute('open')) opened = el;
    }
    if (!opened) return;
    // Removing an attribute that is absent changes nothing and is not recorded, so this writes only what differs.
    for (const child of this.children) if (child !== opened) child.removeAttribute('open');
  }

  connected() {
    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver((records) => this.#opened(records));
      observer.observe(this, { subtree: true, attributes: true, attributeFilter: ['open'], attributeOldValue: true });
      return () => observer.disconnect();
    });
  }
}
