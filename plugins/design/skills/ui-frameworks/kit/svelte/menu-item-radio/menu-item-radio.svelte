<script lang="ts">
  // menu-item-radio.svelte: a menu item that is one choice of a group, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="menuitemradio">, which has no native checked or disabled state, so they are written
  // as aria-checked and aria-disabled (X2). It mounts press, as the Web Component does, so Enter and Space click
  // it. A click turns it on, never off: `checked` is $bindable, so `bind:checked` follows the user and a plain
  // `checked` only starts it. In a menu group it adds itself to the group through the family's context; when the
  // user chooses it, the group turns its other radio items off, in the same flush, before onchange(true, event)
  // is called (J22, G5). value is written on the root, for the author to read. As the React menu item radio.
  import { flushSync, getContext, untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { press } from '../../behaviours/press.js';
  import { GROUP, type MenuGroupEntry, type MenuGroupState } from '../menu-group/menu-group.context.js';
  import { role } from '../../components/menu-item-radio/menu-item-radio.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'role' | 'onchange'> & {
    /** This is the chosen item of its group: `bind:checked` follows the user, a plain `checked` only starts it. */
    checked?: boolean;
    /** What the choice stands for; written on the root, for the author to read. */
    value?: string;
    /** It cannot be chosen or focused. */
    disabled?: boolean;
    /** Called once when the user chooses the item, with true and the click, once the group shows it. */
    onchange?: (checked: boolean, event: MouseEvent) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { checked = $bindable(false), value, disabled = false, onchange, ref = $bindable(null), children, ...rest }: Props = $props();
  const group = getContext<MenuGroupState | null | undefined>(GROUP);
  const entry: MenuGroupEntry = { off: () => { checked = false; } };
  // A div has no value in Svelte's types, so it is spread.
  const authored = $derived({ value });

  $effect(() => untrack(() => group?.add(entry)));
  // A native listener, so it runs before the menu's, which may close the menu (J22); the author's onclick, in
  // rest, still runs.
  $effect(() => untrack(() => {
    const el = ref!;
    const off = new AbortController();
    el.addEventListener('click', (event) => {
      if (disabled || checked) return;
      checked = true;
      group?.choose(entry);
      // The group's other items are written before onchange is called, so a listener reads them up to date.
      flushSync();
      onchange?.(true, event);
    }, { signal: off.signal });
    return () => off.abort();
  }));

  // In the browser Svelte gives a spread `value` to a div as a property, which it only keeps as an expando; the
  // server writes the attribute. The author reads the attribute, so it is written here too; a value that goes
  // back to undefined takes Svelte's other path, which removes the attribute.
  $effect(() => {
    const root = untrack(() => ref);
    if (value !== undefined && value !== null && root && root.getAttribute('value') !== String(value)) root.setAttribute('value', String(value));
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<div
  {...rest}
  bind:this={ref}
  {role}
  data-ui="menu-item-radio"
  {...authored}
  aria-checked={String(checked) as 'true' | 'false'}
  aria-disabled={disabled ? 'true' : undefined}
  {@attach (el) => press(el, { disabled: () => disabled })}
>{@render children?.()}</div>
