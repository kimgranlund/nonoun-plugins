<script lang="ts">
  // tabs.svelte: the element that holds a tab list and its panels, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // It coordinates the tab list, the tabs and the panels through context (tabs.context.js); it writes nothing into
  // the DOM itself. Each tab and panel registers with it as it is created, in document order, so a tab or a panel
  // with no value has its position among its kind as its value. `value` is $bindable: `bind:value` holds it, a
  // plain `value` only starts it. With neither, it is the value of the first tab that is not disabled (G9), on the
  // server and in the browser alike. A tab has no `selected` (D121): on the server a tab knows only the tabs before
  // it, so a later tab could not have said so in time; the value says it in one pass.
  //
  // onchange(value, event) is called when the user selects another tab, after the tabs and the panels are up to
  // date (G5). It is not called when the value prop changes.
  import { flushSync, setContext, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { TABS, type TabsContext, type TabsEntry, type TabsKind } from './tabs.context.js';
  import { props as spec } from '../../components/tabs/tabs.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children' | 'onchange'> & {
    value?: string;
    activation?: 'automatic' | 'manual';
    onchange?: (value: string, event: Event) => void;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { value = $bindable(), activation, onchange, ref = $bindable(null), children, ...rest }: Props = $props();

  const uid = $props.id();
  let tabs: TabsEntry[] = $state.raw([]);
  let panels: TabsEntry[] = $state.raw([]);

  const listOf = (kind: TabsKind) => (kind === 'tab' ? tabs : panels);
  const valueOf = (kind: TabsKind, entry: TabsEntry) => entry.value ?? String(listOf(kind).indexOf(entry));
  const find = (kind: TabsKind, v: string) => listOf(kind).find((e) => valueOf(kind, e) === v);
  /** An id made of a value. */
  const safe = (v: string) => v.replace(/[^\w-]/g, '_');

  // The first value: no fallback to a disabled tab, so that a disabled first tab is not selected in the server
  // markup before the tabs after it are known.
  const first = () => {
    const tab = tabs.find((t) => !t.disabled);
    return tab ? valueOf('tab', tab) : '';
  };
  // A function, not $derived: on the server a derived keeps the value it first had, before the later tabs register.
  const current = () => value ?? first();
  const mode = $derived((spec.activation as { values: readonly string[] }).values.includes(activation ?? '') ? activation as 'automatic' | 'manual' : 'automatic');

  setContext<TabsContext>(TABS, {
    value: current,
    activation: () => mode,
    choose(next, event) {
      if (next === current()) return;
      value = next;
      // The tabs and the panels are up to date before onchange is called (G5).
      flushSync();
      onchange?.(next, event);
    },
    add(kind, entry) {
      if (kind === 'tab') tabs = [...tabs, entry];
      else panels = [...panels, entry];
    },
    remove(kind, entry) {
      if (kind === 'tab') tabs = tabs.filter((e) => e !== entry);
      else panels = panels.filter((e) => e !== entry);
    },
    valueOf,
    tabId: (v) => find('tab', v)?.id ?? `${uid}-tab-${safe(v)}`,
    panelId: (v) => find('tabpanel', v)?.id ?? `${uid}-panel-${safe(v)}`,
    // With none of a kind registered yet, as on the server while the tabs render, every value may name one.
    hasTab: (v) => !tabs.length || !!find('tab', v),
    hasPanel: (v) => !panels.length || !!find('tabpanel', v),
  });

  // data-ready one frame after the root is in the page, as on every Web Component (L6).
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<div {...rest} bind:this={ref} data-ui="tabs">{@render children?.()}</div>
