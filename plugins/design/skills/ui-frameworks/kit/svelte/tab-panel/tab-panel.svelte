<script lang="ts">
  // tab-panel.svelte: the content one tab shows, for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div role="tabpanel">, in the Tab order unless the author gives another tabindex. The tabs element
  // decides whether it is hidden, gives it an id when the author gave none, and names it after its tab when the
  // author named it neither with aria-label nor with aria-labelledby (G4, A2). It registers with the nearest tabs
  // element as it is created, so one with no value has its position among the panels as its value.
  import { getContext, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';
  import { TABS, type TabsContext, type TabsEntry } from '../tabs/tabs.context.js';
  import { role, tabindex } from '../../components/tab-panel/tab-panel.props.js';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    value?: string;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { value, id, ref = $bindable(null), children, ...rest }: Props = $props();

  const tabs = getContext<TabsContext | undefined>(TABS);
  const entry: TabsEntry = {
    get value() { return value; },
    get id() { return id ?? undefined; },
  };
  tabs?.add('tabpanel', entry);
  $effect(() => () => tabs?.remove('tabpanel', entry));

  const own = $derived(value ?? (tabs ? tabs.valueOf('tabpanel', entry) : ''));
  const shown = $derived(tabs ? tabs.hasTab(tabs.value()) && tabs.value() === own : true);
  const named = $derived(rest['aria-label'] !== undefined || rest['aria-labelledby'] !== undefined);

  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<!-- svelte-ignore a11y_no_noninteractive_tabindex: a tab panel is in the Tab order, as the APG pattern asks -->
<div
  {tabindex}
  {...rest}
  bind:this={ref}
  {role}
  data-ui="tab-panel"
  id={id ?? tabs?.panelId(own)}
  aria-labelledby={named || !tabs?.hasTab(own) ? rest['aria-labelledby'] : tabs.tabId(own)}
  hidden={!shown}
>{@render children?.()}</div>
