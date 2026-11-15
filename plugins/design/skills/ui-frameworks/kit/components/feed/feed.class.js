// @ts-check
/**
 * feed.class.js: the class of the feed, a list of articles that grows as the user reads. Importing it defines
 * no element; feed.js does that.
 *
 * The root has the feed role. Its articles are the author's child elements with the article role, native
 * article elements among them. The feed makes each one focusable where the author gave it no tabindex, and
 * numbers them with aria-posinset and aria-setsize; an observer on its children keeps the numbers right as
 * articles are added and removed. PageDown and PageUp move focus from article to article, Control+End and
 * Control+Home move it out of the feed. When focus reaches the last article the feed dispatches `more`, once
 * for each set of articles.
 *
 * Rules: docs/specs/patterns.md, J72 and J73.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { props, role } from './feed.props.js';

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/** @param {Element} el Whether an element is an article: the article role, or a native article with no other role. */
const isArticle = (el) => {
  const role = el.getAttribute('role');
  return role === null ? el.localName === 'article' : role.trim().split(/\s+/)[0] === 'article';
};

/** @param {Element} el Whether focus can land on an element in the page: what Control+End and Control+Home look for. */
const focusable = (el) => {
  const html = /** @type {HTMLElement} */ (el);
  if (!(html.tabIndex >= 0) || el.matches(':disabled') || el.closest('[inert]')) return false;
  return html.checkVisibility({ visibilityProperty: true });
};

export class UIFeed extends UIElement {
  static props = props;
  static role = role;

  /** Whether `more` was dispatched for the articles as they are now. */
  #asked = false;
  /** The articles as the last sync saw them, so that `more` can be allowed again when they change. @type {Element[]} */
  #seen = [];

  /** The feed's articles: its child elements with the article role. */
  #articles() { return /** @type {HTMLElement[]} */ ([...this.children].filter(isArticle)); }

  /** Makes each article focusable and numbers it. Writes nothing when it already is. */
  #sync() {
    const articles = this.#articles();
    articles.forEach((article, i) => {
      if (!article.hasAttribute('tabindex')) article.setAttribute('tabindex', '0');
      put(article, 'aria-posinset', String(i + 1));
      put(article, 'aria-setsize', String(articles.length));
    });
    // A changed set may ask for more again (J73).
    if (articles.length !== this.#seen.length || articles.some((article, i) => article !== this.#seen[i])) this.#asked = false;
    this.#seen = articles;
  }

  /**
   * The article an event happened in, among this feed's own.
   * @param {EventTarget | null} target
   */
  #articleOf(target) {
    if (!(target instanceof Element)) return null;
    for (let el = /** @type {Element | null} */ (target); el && el !== this; el = el.parentElement) {
      if (el.parentElement === this && isArticle(el)) return /** @type {HTMLElement} */ (el);
    }
    return null;
  }

  /**
   * Moves focus to the first focusable element after the feed, or the last one before it, in document order.
   * An element inside the feed, or one that holds the feed, is neither.
   * @param {boolean} after
   */
  #leave(after) {
    const all = [...this.ownerDocument.querySelectorAll('*')].filter((el) => !this.contains(el) && !el.contains(this));
    const side = all.filter((el) => !!(this.compareDocumentPosition(el) & (after ? Node.DOCUMENT_POSITION_FOLLOWING : Node.DOCUMENT_POSITION_PRECEDING)));
    const target = after ? side.find(focusable) : side.reverse().find(focusable);
    /** @type {HTMLElement | undefined} */ (target)?.focus();
  }

  /** @param {string} name */
  changed(name) {
    // A script that sets loading reads aria-busy in the same task (J73).
    if (name === 'loading' && this.isConnected) setAttr(this, 'aria-busy', /** @type {any} */ (this).loading ? 'true' : null);
  }

  connected() {
    this.changed('loading');

    this.listen(this, 'keydown', (event) => {
      if (event.defaultPrevented || event.altKey || event.metaKey || event.shiftKey) return;
      const article = this.#articleOf(event.target);
      if (!article) return;
      if (!event.ctrlKey && (event.key === 'PageDown' || event.key === 'PageUp')) {
        event.preventDefault();
        const articles = this.#articles();
        const next = articles[articles.indexOf(article) + (event.key === 'PageDown' ? 1 : -1)];
        next?.focus();
      } else if (event.ctrlKey && (event.key === 'End' || event.key === 'Home')) {
        event.preventDefault();
        this.#leave(event.key === 'End');
      }
    });

    // Focus reached the last article: the page may add more, once for each set of articles (J73).
    this.listen(this, 'focusin', (event) => {
      const articles = this.#articles();
      const article = this.#articleOf(event.target);
      if (!article || article !== articles[articles.length - 1] || this.#asked) return;
      this.#asked = true;
      this.emit('more');
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true, attributes: true, subtree: true, attributeFilter: ['role'] });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
