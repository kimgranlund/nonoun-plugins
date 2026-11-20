<script lang="ts">
  // feed.svelte: a feed, a list of articles that grows as the user reads, for Svelte (docs/specs/targets.md, V1 to
  // V7; rules J72 and J73 of docs/specs/patterns.md).
  //
  // The root is a <div role="feed">: no native element is a feed. A role the author passes wins, as on the Web
  // Component and the React feed. `loading` is rendered as `aria-busy="true"`, so it is in the server markup and in
  // the DOM as soon as Svelte flushes.
  //
  // Its articles are the author's child elements with the article role, native article elements among them. It
  // finds them in the DOM, as the Web Component does, and writes on them, only where they differ, in an effect after
  // mount and on each change in its subtree: `tabindex="0"` where the author gave none, `aria-posinset` and
  // `aria-setsize`. No article renders these. The author's markup re-renders without this component, so after the
  // first mount every write comes from the observer, in a microtask of the same task.
  //
  // Its keys go through onkeydown on the root: PageDown and PageUp move focus from article to article, Control+End
  // and Control+Home move it to the first focusable element after or before the feed. A key whose default is already
  // prevented, by a feed nested in an article whose handler Svelte's delegation calls first, is left alone.
  // onmore(event) is called when focus reaches the last article, once for each set of articles (J73), with the
  // focusin event: focus does not bubble, so the root listens for focusin, and an author's onfocusin is called too.
  import { untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { role } from '../../components/feed/feed.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    loading?: boolean;
    /** Focus reached the last article: the page may add more. */
    onmore?: (event: FocusEvent) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { loading = false, onmore, onkeydown, onfocusin, ref = $bindable(null), children, ...rest }: Props = $props();

  /** Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };

  /** Whether an element is an article: the article role, or a native article with no other role. */
  const isArticle = (el: Element) => {
    const r = el.getAttribute('role');
    return r === null ? el.localName === 'article' : r.trim().split(/\s+/)[0] === 'article';
  };

  /** Whether focus can land on an element in the page: what Control+End and Control+Home look for. */
  const focusable = (el: Element) => {
    const html = el as HTMLElement;
    if (!(html.tabIndex >= 0) || el.matches(':disabled') || el.closest('[inert]')) return false;
    return html.checkVisibility({ visibilityProperty: true });
  };

  /** The feed's articles: its child elements with the article role. */
  const articlesOf = (root: HTMLElement) => [...root.children].filter(isArticle) as HTMLElement[];

  /** The article an event happened in, among this feed's own. */
  const articleOf = (root: HTMLElement, target: EventTarget | null) => {
    if (!(target instanceof Element)) return null;
    for (let el: Element | null = target; el && el !== root; el = el.parentElement) {
      if (el.parentElement === root && isArticle(el)) return el as HTMLElement;
    }
    return null;
  };

  /**
   * Moves focus to the first focusable element after the feed, or the last one before it, in document order. An
   * element inside the feed, or one that holds the feed, is neither.
   */
  const leave = (root: HTMLElement, after: boolean) => {
    const all = [...root.ownerDocument.querySelectorAll('*')].filter((el) => !root.contains(el) && !el.contains(root));
    const side = all.filter((el) => !!(root.compareDocumentPosition(el) & (after ? Node.DOCUMENT_POSITION_FOLLOWING : Node.DOCUMENT_POSITION_PRECEDING)));
    const target = after ? side.find(focusable) : side.reverse().find(focusable);
    (target as HTMLElement | undefined)?.focus();
  };

  /** Whether onmore was called for the articles as they are now, and the articles as the last sync saw them. */
  const asked: { done: boolean, seen: Element[] } = { done: false, seen: [] };

  /** Makes each article focusable and numbers it. Writes nothing when it already is. */
  const sync = (el: HTMLElement) => {
    const articles = articlesOf(el);
    articles.forEach((article, i) => {
      if (!article.hasAttribute('tabindex')) article.setAttribute('tabindex', '0');
      put(article, 'aria-posinset', String(i + 1));
      put(article, 'aria-setsize', String(articles.length));
    });
    // A changed set may ask for more again (J73).
    if (articles.length !== asked.seen.length || articles.some((article, i) => article !== asked.seen[i])) asked.done = false;
    asked.seen = articles;
  };

  const setup = (el: HTMLDivElement) => {
    const observer = new MutationObserver(() => sync(el));
    observer.observe(el, { childList: true, attributes: true, subtree: true, attributeFilter: ['role'] });
    sync(el);
    return () => observer.disconnect();
  };

  // Mounted once. `ref` is read untracked: a rerun would start the observer again whenever a parent re-reads its
  // binding.
  $effect(() => untrack(() => (ref ? setup(ref) : undefined)));

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });

  const keys = (event: KeyboardEvent & { currentTarget: EventTarget & HTMLDivElement }) => {
    onkeydown?.(event);
    const el = ref as HTMLDivElement;
    if (event.defaultPrevented || event.altKey || event.metaKey || event.shiftKey) return;
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

  /** Focus reached the last article: the page may add more, once for each set of articles (J73). */
  const focus = (event: FocusEvent & { currentTarget: EventTarget & HTMLDivElement }) => {
    onfocusin?.(event);
    const el = ref as HTMLDivElement;
    const articles = articlesOf(el);
    const article = articleOf(el, event.target);
    if (!article || article !== articles[articles.length - 1] || asked.done) return;
    asked.done = true;
    onmore?.(event);
  };
</script>

<div
  {role}
  {...rest}
  bind:this={ref}
  data-ui="feed"
  aria-busy={loading ? 'true' : undefined}
  onkeydown={keys}
  onfocusin={focus}
>{@render children?.()}</div>
