<script lang="ts">
  // option.svelte: one option of a listbox, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="option">, which has no native selected or disabled state, so both are ARIA
  // (aria-selected, aria-disabled; X2). It never takes focus: its listbox keeps focus and names the highlighted
  // option. It renders `value` as an attribute, since its listbox, and a combobox or a select holding the listbox,
  // read the value from the DOM, as on the Web Component. As the React option.
  //
  // It renders none of the attributes that its listbox, or a combobox or a select of another family, writes on it:
  // selected, hidden, id (unless the author gives one), data-highlighted and data-focus. So it need not know whether
  // it is held. aria-selected is its own, as on the Web Component: it is rendered once, from a constant (its listbox's
  // value when that is known, or else its own `selected` prop), so that the server markup paints the selection, and
  // Svelte never writes it again; it is then kept in step with the `selected` attribute in the DOM, whoever writes
  // it. A `selected` prop that changes later is written into the DOM, as a script would set it, and the listbox
  // takes it as its value.
  import { getContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { LISTBOX, type ListboxContext, type ListboxEntry } from '../listbox/listbox.context.js';
  import { role } from '../../components/option/option.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'role'> & {
    value?: string;
    selected?: boolean;
    disabled?: boolean;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { value, selected = false, disabled = false, ref = $bindable(null), children, ...rest }: Props = $props();

  const box = getContext<ListboxContext | undefined>(LISTBOX);
  const start = untrack(() => selected);
  const entry: ListboxEntry = { get value() { return value; }, selected: start };
  box?.add(entry);
  $effect(() => () => box?.remove(entry));
  // The first value only, a constant: afterwards the DOM decides, so Svelte never writes aria-selected again.
  const first = untrack(() => (box?.given() ? value !== undefined && box.chosen().includes(value) : start));
  // A div has no value of its own, and Svelte sets `value` as a property: the server renders the attribute from the
  // spread, and in the browser it is written as the attribute, as the checkbox writes its value.
  const valued = $derived(value === undefined ? {} : { value });
  const keep = (el: HTMLDivElement) => {
    if (value === undefined) el.removeAttribute('value');
    else if (el.getAttribute('value') !== value) el.setAttribute('value', value);
  };

  // aria-selected follows the selected attribute, whoever writes it.
  $effect(() => {
    const el = ref!;
    const observer = new MutationObserver(() => {
      const on = String(el.hasAttribute('selected'));
      if (el.getAttribute('aria-selected') !== on) el.setAttribute('aria-selected', on);
    });
    observer.observe(el, { attributes: true, attributeFilter: ['selected'] });
    return () => observer.disconnect();
  });
  // A selected prop that changes after the first render acts as a script that sets the attribute.
  let was = start;
  $effect(() => {
    const now = selected;
    const el = ref!;
    untrack(() => {
      if (was === now) return;
      was = now;
      if (now) el.setAttribute('selected', '');
      else el.removeAttribute('selected');
    });
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<div
  {...rest}
  bind:this={ref}
  {role}
  data-ui="option"
  {...valued}
  {@attach keep}
  aria-selected={first ? 'true' : 'false'}
  aria-disabled={disabled ? 'true' : undefined}
>{@render children?.()}</div>
