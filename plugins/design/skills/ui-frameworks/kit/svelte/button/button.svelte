<script lang="ts">
  // button.svelte: the button for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a native <button>, so the platform submits and resets the form, gives the submitter, and makes
  // this the form's default button: the Web Component needs a hidden submit part for that (D19), this does not.
  // The press behaviour is mounted as on the Web Component, so Enter activates at key down and Space at key up,
  // once, with data-active while the key is held (F8 to F10).
  import type { Snippet } from 'svelte';
  import type { HTMLButtonAttributes } from 'svelte/elements';
  import { press } from '../../behaviours/press.js';
  import { props as spec } from '../../components/button/button.props.js';

  type Props = Omit<HTMLButtonAttributes, 'type' | 'children'> & {
    variant?: 'neutral' | 'primary' | 'ghost';
    type?: 'button' | 'submit' | 'reset';
    /** The root, for `bind:ref`. */
    ref?: HTMLButtonElement | null;
    children?: Snippet;
  };

  let { variant, type, value, name, disabled = false, ref = $bindable(null), children, ...rest }: Props = $props();

  /** An enum prop's value, or its default when the value is not one of the manifest's. */
  const pick = (prop: string, given: unknown): string => {
    const p = spec[prop] as { values: readonly string[], default: string };
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };

  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  $effect(() => {
    const root = ref;
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<button
  {...rest}
  bind:this={ref}
  data-ui="button"
  data-variant={pick('variant', variant)}
  type={pick('type', type) as 'button' | 'submit' | 'reset'}
  {value}
  {name}
  {disabled}
  {@attach (el) => press(el, { disabled: () => el.matches(':disabled') })}
>{@render children?.()}</button>
