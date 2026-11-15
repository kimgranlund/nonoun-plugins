// @ts-check
/**
 * meter.class.js: the meter's class. Importing it defines no element; meter.js does that.
 *
 * The root has the meter role. Its aria-valuemin, aria-valuemax and aria-valuenow follow min, max and value (J17),
 * with the value held between min and max, and a max that is not above min treated as min. One more binding hands
 * the value's share of the range, a number from 0 to 1, to the recipe as the private custom property --_share on the
 * root's own inline style (J18). That is the one style a class writes.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { props, parts, role, tabindex } from './meter.props.js';

export class UIMeter extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  connected() {
    const self = /** @type {any} */ (this);
    /** The range as it is used: max is never below min, and the value is held inside. */
    const range = () => {
      const min = /** @type {number} */ (self.min);
      const max = Math.max(/** @type {number} */ (self.max), min);
      const value = Math.min(Math.max(/** @type {number} */ (self.value), min), max);
      return { min, max, value };
    };
    this.effect(() => setAttr(this, 'aria-valuemin', String(range().min)));
    this.effect(() => setAttr(this, 'aria-valuemax', String(range().max)));
    this.effect(() => setAttr(this, 'aria-valuenow', String(range().value)));
    this.effect(() => {
      const { min, max, value } = range();
      this.style.setProperty('--_share', String(max > min ? (value - min) / (max - min) : 0));
      return () => this.style.removeProperty('--_share');
    });
  }
}
