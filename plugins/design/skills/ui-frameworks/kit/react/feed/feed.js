// @ts-check
/**
 * feed.js: a feed, a list of articles that grows as the user reads, for React (docs/specs/targets.md; rules J72
 * and J73 of docs/specs/patterns.md).
 *
 * The root is a <div role="feed">: no native element is a feed. A role the author passes wins, as on the Web
 * Component. `loading` is rendered as `aria-busy="true"`, so it is in the server markup and in the DOM as soon as
 * the render returns.
 *
 * Its articles are the author's child elements with the article role, native article elements among them. It
 * finds them in the DOM, as the Web Component does, and writes on them, only where they differ, after each render
 * and on each change in its subtree: `tabindex="0"` where the author gave none, `aria-posinset` and
 * `aria-setsize`. No article renders these.
 *
 * Its keys go through React's onKeyDown on the root: PageDown and PageUp move focus from article to article,
 * Control+End and Control+Home move it to the first focusable element after or before the feed. A key whose
 * default is already prevented, by a feed nested in an article whose handler React calls first, is left alone.
 * onMore(event) is called when focus reaches the last article, once for each set of articles (J73), with the
 * focus event.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import { role } from '../../components/feed/feed.props.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   loading?: boolean,
 *   onMore?: (event: import('react').FocusEvent<HTMLDivElement>) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} FeedProps
 */

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
  const r = el.getAttribute('role');
  return r === null ? el.localName === 'article' : r.trim().split(/\s+/)[0] === 'article';
};

/** @param {Element} el Whether focus can land on an element in the page: what Control+End and Control+Home look for. */
const focusable = (el) => {
  const html = /** @type {HTMLElement} */ (el);
  if (!(html.tabIndex >= 0) || el.matches(':disabled') || el.closest('[inert]')) return false;
  return html.checkVisibility({ visibilityProperty: true });
};

/** The feed's articles: its child elements with the article role. @param {HTMLElement} root */
const articlesOf = (root) => /** @type {HTMLElement[]} */ ([...root.children].filter(isArticle));

/**
 * The article an event happened in, among this feed's own.
 * @param {HTMLElement} root @param {EventTarget | null} target
 */
const articleOf = (root, target) => {
  if (!(target instanceof Element)) return null;
  for (let el = /** @type {Element | null} */ (target); el && el !== root; el = el.parentElement) {
    if (el.parentElement === root && isArticle(el)) return /** @type {HTMLElement} */ (el);
  }
  return null;
};

/**
 * Moves focus to the first focusable element after the feed, or the last one before it, in document order. An
 * element inside the feed, or one that holds the feed, is neither.
 * @param {HTMLElement} root @param {boolean} after
 */
const leave = (root, after) => {
  const all = [...root.ownerDocument.querySelectorAll('*')].filter((el) => !root.contains(el) && !el.contains(root));
  const side = all.filter((el) => !!(root.compareDocumentPosition(el) & (after ? Node.DOCUMENT_POSITION_FOLLOWING : Node.DOCUMENT_POSITION_PRECEDING)));
  const target = after ? side.find(focusable) : side.reverse().find(focusable);
  /** @type {HTMLElement | undefined} */ (target)?.focus();
};

/** @param {FeedProps} props */
function FeedRoot({ loading = false, onMore, onKeyDown, onFocus, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  /** Whether onMore was called for the articles as they are now, and the articles as the last sync saw them. */
  const asked = useRef(/** @type {{ done: boolean, seen: Element[] }} */ ({ done: false, seen: [] }));

  /** Makes each article focusable and numbers it. Writes nothing when it already is. */
  const sync = useCallback(() => {
    const el = root.current;
    if (!el) return;
    const articles = articlesOf(el);
    articles.forEach((article, i) => {
      if (!article.hasAttribute('tabindex')) article.setAttribute('tabindex', '0');
      put(article, 'aria-posinset', String(i + 1));
      put(article, 'aria-setsize', String(articles.length));
    });
    // A changed set may ask for more again (J73).
    const { seen } = asked.current;
    if (articles.length !== seen.length || articles.some((article, i) => article !== seen[i])) asked.current.done = false;
    asked.current.seen = articles;
  }, []);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, attributes: true, subtree: true, attributeFilter: ['role'] });
    return () => observer.disconnect();
  }, [sync]);
  // After each render, in the same commit: the author's articles may have changed with it.
  useLayoutEffect(sync);
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** @param {import('react').KeyboardEvent<HTMLDivElement>} event */
  const keys = (event) => {
    onKeyDown?.(event);
    const el = /** @type {HTMLDivElement} */ (root.current);
    if (event.nativeEvent.defaultPrevented || event.altKey || event.metaKey || event.shiftKey) return;
    const article = articleOf(el, event.target);
    if (!article) return;
    if (!event.ctrlKey && (event.key === 'PageDown' || event.key === 'PageUp')) {
      event.preventDefault();
      const articles = articlesOf(el);
      articles[articles.indexOf(article) + (event.key === 'PageDown' ? 1 : -1)]?.focus();
    } else if (event.ctrlKey && (event.key === 'End' || event.key === 'Home')) {
      event.preventDefault();
      leave(el, event.key === 'End');
    }
  };

  /** Focus reached the last article: the page may add more, once for each set of articles (J73). @param {import('react').FocusEvent<HTMLDivElement>} event */
  const focus = (event) => {
    onFocus?.(event);
    const el = /** @type {HTMLDivElement} */ (root.current);
    const articles = articlesOf(el);
    const article = articleOf(el, event.target);
    if (!article || article !== articles[articles.length - 1] || asked.current.done) return;
    asked.current.done = true;
    onMore?.(event);
  };

  return createElement('div', /** @type {any} */ ({
    role, ...rest, ref: setRef, 'data-ui': 'feed', 'aria-busy': loading ? 'true' : undefined, onKeyDown: keys, onFocus: focus,
  }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Feed = /* @__PURE__ */ Object.assign(FeedRoot, { kitRole: role, displayName: 'Feed' });
