// @ts-check
/**
 * progress.class.js: the progress's class. Importing it defines no element; progress.js does that.
 *
 * The root has the progressbar role. Its aria-valuemin and aria-valuemax follow min and max, and its aria-valuenow
 * follows value, held between min and max (J96). A root with no value attribute is indeterminate: it carries no
 * aria-valuenow and no share, and its fill is the recipe's moving run. With a value, one more binding hands the
 * value's share of the range, a number from 0 to 1, to the recipe as the private custom property --_share on the
 * root's own inline style (J97, J18). That is the one style a class writes.
 *
 * The run is the recipe's (progress.css): the class only leaves the root without a value attribute.
 *
 * A number prop reads a missing value as 0, so the prop alone cannot tell "none" from 0. The root therefore has its
 * own `value` accessor: a number, including 0, writes the attribute (a determinate progress); null or undefined
 * removes it (an indeterminate one); anything else goes to the prop as it is.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { signal } from '../../foundation/signals.js';
import { props, parts, role, tabindex } from './progress.props.js';

export class UIProgress extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  /** Whether the root has a value attribute: a number prop cannot tell "0" from "none", the attribute can. */
  #has = signal(false);

  constructor() {
    super();
    const inherited = /** @type {PropertyDescriptor} */ (Object.getOwnPropertyDescriptor(Object.getPrototypeOf(this), 'value'));
    Object.defineProperty(this, 'value', {
      configurable: true,
      get: () => inherited.get?.call(this),
      set: (/** @type {unknown} */ next) => {
        if (next === null || next === undefined) { this.removeAttribute('value'); return; }
        inherited.set?.call(this, next);
        // 0 is the prop's default, which the prop writes as no attribute; here it is a value.
        if (!this.hasAttribute('value') && !Number.isNaN(+/** @type {any} */ (next)) && String(next).trim() !== '') this.setAttribute('value', String(+/** @type {any} */ (next)));
      },
    });
  }

  /** @param {string} name */
  changed(name) {
    if (name === 'value') this.#has.value = this.hasAttribute('value');
  }

  connected() {
    const self = /** @type {any} */ (this);
    this.#has.value = this.hasAttribute('value');
    /** The range as it is used: max is never below min, and the value is held inside. */
    const range = () => {
      const min = /** @type {number} */ (self.min);
      const max = Math.max(/** @type {number} */ (self.max), min);
      const value = Math.min(Math.max(/** @type {number} */ (self.value), min), max);
      return { min, max, value };
    };
    this.effect(() => setAttr(this, 'aria-valuemin', String(range().min)));
    this.effect(() => setAttr(this, 'aria-valuemax', String(range().max)));
    this.effect(() => setAttr(this, 'aria-valuenow', this.#has.value ? String(range().value) : null));
    this.effect(() => {
      if (!this.#has.value) return;
      const { min, max, value } = range();
      this.style.setProperty('--_share', String(max > min ? (value - min) / (max - min) : 0));
      return () => this.style.removeProperty('--_share');
    });
  }
}
