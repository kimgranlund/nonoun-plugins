// @ts-check
/**
 * option.class.js: the class of one option of a listbox. Importing it defines no element; option.js does that.
 *
 * The root has the option role. It keeps aria-selected and aria-disabled in step with its own attributes. It has
 * no tabindex and never takes focus: its listbox keeps focus and names the highlighted option. It does not know
 * its listbox, which writes its `selected` and `data-highlighted` attributes, and `data-focus` while it has focus.
 *
 * Rules: docs/specs/patterns.md, J27 to J29.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { props, role } from './option.props.js';

export class UIOption extends UIElement {
  static props = props;
  static role = role;

  connected() {
    const self = /** @type {any} */ (this);
    this.effect(() => setAttr(this, 'aria-selected', String(self.selected)));
    this.effect(() => setAttr(this, 'aria-disabled', self.disabled ? 'true' : null));
  }
}
