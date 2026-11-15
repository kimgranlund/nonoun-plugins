// @ts-check
/**
 * tree-item.class.js: the class of one item of a tree. Importing it defines no element; tree-item.js does that.
 *
 * The root has the treeitem role. It keeps aria-selected and aria-disabled in step with its own attributes, and
 * aria-expanded with `expanded`, but only while it has a group: its child marked `data-part="group"`, to which it
 * gives the group role when the author gave none. It names itself after its child marked `data-part="label"`,
 * with aria-labelledby, unless the author named it: without that, its name would include the text of every item
 * in its group. The label gets an id only when it has none.
 *
 * It does not know its tree. The tree writes its `selected`, `expanded`, `tabindex`, `aria-level`,
 * `aria-setsize` and `aria-posinset`, and listens for its keys and clicks. The recipe alone shows and hides the
 * group, from `expanded`, so the state is right before anything is defined.
 *
 * Rules: docs/specs/patterns.md, J32 to J34.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { props, role } from './tree-item.props.js';

const GROUP = ':scope > [data-part="group"]';
const LABEL = ':scope > [data-part="label"]';
/** For the ids this class gives to a label that has none. */
let serial = 0;

/**
 * Sets or removes an attribute, only when it differs. An observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

export class UITreeItem extends UIElement {
  static props = props;
  static role = role;

  /** @type {string | null} The aria-labelledby value this element wrote, so that it never replaces an author's. */
  #named = null;

  /** Brings aria-expanded, the group's role and the item's name in step with its children. */
  #sync() {
    const self = /** @type {any} */ (this);
    const group = this.querySelector(GROUP);
    put(this, 'aria-expanded', group ? String(self.expanded) : null);
    if (group && !group.hasAttribute('role')) group.setAttribute('role', 'group');

    // A name the author gave stays (A2). One this element gave follows the label.
    const name = this.getAttribute('aria-labelledby');
    if (name !== null && name !== this.#named) return;
    const label = this.hasAttribute('aria-label') ? null : this.querySelector(LABEL);
    if (label && !label.id) label.id = `${this.localName}-label-${++serial}`;
    this.#named = label ? label.id : null;
    put(this, 'aria-labelledby', this.#named);
  }

  /** @param {string} name */
  changed(name) {
    // The tree opens an item and reads the result in the same task (J32).
    if (name === 'expanded' && this.isConnected) this.#sync();
  }

  connected() {
    const self = /** @type {any} */ (this);
    this.effect(() => setAttr(this, 'aria-selected', String(self.selected)));
    this.effect(() => setAttr(this, 'aria-disabled', self.disabled ? 'true' : null));

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects. It sees a group or a label come, go, or change its id.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true, attributes: true, subtree: true, attributeFilter: ['data-part', 'id', 'aria-label', 'aria-labelledby'] });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
