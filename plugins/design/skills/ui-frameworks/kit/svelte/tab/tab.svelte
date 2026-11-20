<script lang="ts">
  // tab.svelte: one tab, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a native <button role="tab" type="button">: the native disabled state takes it out of focus and out
  // of the pointer's reach (G8). It mounts press, as the Web Component does, so Enter and Space click it; a click
  // selects it, and with automatic activation so does focus (G7). The tab list's roving focus writes its tabindex.
  // It registers with the nearest tabs element as it is created, so one with no value has its position among the
  // tabs as its value.
  //
  // There is no `selected` prop (D121). On the server Svelte renders in one pass, so a later tab marked selected is
  // not known when the first tab renders, and the first paint showed the wrong tab and panel. `value` on the tabs
  // element says the same thing in one pass; with none, the first tab that is not disabled is selected. A `selected`
  // passed anyway is a type error and does not reach the root.
  import { getContext, type Snippet } from 'svelte';
  import type { HTMLButtonAttributes } from 'svelte/elements';
  import { press } from '../../behaviours/press.js';
  import { TABS, type TabsContext, type TabsEntry } from '../tabs/tabs.context.js';
  import { role } from '../../components/tab/tab.props.js';

  type Props = Omit<HTMLButtonAttributes, 'value' | 'type' | 'children' | 'selected'> & {
    value?: string;
    disabled?: boolean;
    /** The root, for `bind:ref`. */
    ref?: HTMLButtonElement | null;
    children?: Snippet;
  };

  let { value, disabled = false, id, onclick, onfocus, ref = $bindable(null), children, ...rest }: Props = $props();

  const tabs = getContext<TabsContext | undefined>(TABS);
  const entry: TabsEntry = {
    get value() { return value; },
    get disabled() { return disabled; },
    get id() { return id ?? undefined; },
  };
  tabs?.add('tab', entry);
  $effect(() => () => tabs?.remove('tab', entry));

  const own = $derived(value ?? (tabs ? tabs.valueOf('tab', entry) : ''));
  const isSelected = $derived(tabs ? tabs.hasTab(own) && tabs.value() === own : false);
  // The rest, less a `selected` that arrives in spite of the type (D121).
  const attrs = $derived.by(() => {
    const { selected: _, ...other } = rest as typeof rest & { selected?: unknown };
    return other;
  });

  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<button
  {...attrs}
  bind:this={ref}
  type="button"
  {role}
  data-ui="tab"
  id={id ?? tabs?.tabId(own)}
  aria-selected={String(isSelected) as 'true' | 'false'}
  aria-controls={tabs?.hasPanel(own) ? tabs.panelId(own) : undefined}
  {disabled}
  onclick={(event) => {
    onclick?.(event);
    if (!event.defaultPrevented && !disabled) tabs?.choose(own, event);
  }}
  onfocus={(event) => {
    onfocus?.(event);
    if (!event.defaultPrevented && !disabled && tabs?.activation() === 'automatic') tabs.choose(own, event);
  }}
  {@attach (el) => press(el, { disabled: () => el.disabled })}
>{@render children?.()}</button>
