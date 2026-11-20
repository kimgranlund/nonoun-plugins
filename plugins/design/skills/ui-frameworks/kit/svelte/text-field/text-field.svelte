<script lang="ts">
  // text-field.svelte: the text field for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <span>, a plain element and not a form control (D14): the author's native input, the child marked
  // data-part="input", carries the name, the value, the type and every constraint, and takes part in the form by
  // itself. It is the author's child, in the `children` snippet: the component finds it in the DOM and never renders,
  // clones, moves or wraps it. As the Web Component and the React text field do, it disables the input while the
  // field is disabled (and never enables one the author disabled), focuses the input on a press anywhere else in the
  // field, writes aria-invalid on the input once the user is due to be told (F5: after the input's first `change` or
  // `invalid` event, until a form reset), and mirrors `invalid` and `readonly` onto the root for the recipe (J47 to
  // J49). Those writes are made in the DOM, in an effect after mount and at each event, so a listener sees them in
  // the same task; none of them is rendered, so the server markup carries `disabled` and the input's own readonly,
  // which the recipe's conditions already select (J77, U2).
  //
  // `disabled` is the one prop of the manifest; every other prop goes to the root.
  import { untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes, MouseEventHandler } from 'svelte/elements';

  type Props = Omit<HTMLAttributes<HTMLSpanElement>, 'children'> & {
    disabled?: boolean;
    /** The root, for `bind:ref`. */
    ref?: HTMLSpanElement | null;
    children?: Snippet;
  };

  let { disabled = false, onmousedown, ref = $bindable(null), children, ...rest }: Props = $props();

  /** What a press on one of them is for: the field leaves it alone. */
  const INTERACTIVE = 'a[href], button, input, select, textarea, [tabindex], [contenteditable]';
  /** Sets or removes an attribute, only when it differs. An observer then sees nothing when nothing changes. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };
  /** The author's input, looked up each time (P6). */
  const inputOf = (el: Element) => el.querySelector(':scope > input[data-part="input"]') as HTMLInputElement | null;

  /** Brings the input and the mirrors in step; set while mounted. */
  let sync: (() => void) | null = null;

  const setup = (el: HTMLSpanElement) => {
    /** The inputs whose user is due to be told (F5). One per input, so a replaced input starts untold. */
    const told = new WeakSet<HTMLInputElement>();
    /** The inputs this field disabled, so that it never enables one the author disabled. */
    const disabledHere = new WeakSet<HTMLInputElement>();

    const update = () => {
      const field = inputOf(el);
      if (field) {
        if (disabled && !field.disabled) { field.disabled = true; disabledHere.add(field); }
        else if (!disabled && disabledHere.has(field)) { field.disabled = false; disabledHere.delete(field); }
      }
      const invalid = !!field && told.has(field) && !field.validity.valid;
      if (field) put(field, 'aria-invalid', invalid ? 'true' : null);
      put(el, 'invalid', invalid ? '' : null);
      put(el, 'readonly', field?.readOnly ? '' : null);
    };
    sync = update;

    const off = new AbortController();
    const listen = { signal: off.signal };
    const tell = (event: Event) => {
      const field = inputOf(el);
      if (!field || event.target !== field) return;
      told.add(field);
      update();
    };
    // The user is due to be told once they have changed the value and left it, or tried to submit (F5).
    el.addEventListener('change', tell, listen);
    // invalid does not bubble.
    el.addEventListener('invalid', tell, { capture: true, signal: off.signal });
    // Once told, the state follows every keystroke, so a correction clears it at once.
    el.addEventListener('input', update, listen);
    // A form reset clears the mark (F6). The reset event comes before the values go back; the mark alone decides.
    el.ownerDocument.addEventListener('reset', (event) => {
      const field = inputOf(el);
      if (!field || event.target !== field.form) return;
      told.delete(field);
      update();
    }, { capture: true, signal: off.signal });

    // The observer sees an input that arrives, is replaced, or changes its constraints: the author's markup, which
    // re-renders without this component, is seen this way, in a microtask of the same task.
    const observer = new MutationObserver(update);
    observer.observe(el, {
      childList: true, subtree: true, attributes: true,
      attributeFilter: ['data-part', 'readonly', 'disabled', 'required', 'pattern', 'min', 'max', 'step', 'minlength', 'maxlength', 'type'],
    });
    update();
    return () => { off.abort(); observer.disconnect(); sync = null; };
  };

  // Mounted once. `ref` is read untracked: a parent's function binding re-reads it whenever the parent's own state
  // changes, and a rerun here would forget which inputs were told and which this field disabled.
  $effect(() => untrack(() => (ref ? setup(ref) : undefined)));
  // The prop can change at any time: bring the input and the mirrors in step, in the flush that changed it.
  $effect(() => {
    void disabled;
    untrack(() => sync?.());
  });

  /** A press anywhere in the field focuses the input, except on something interactive of its own, the input included (focus() on a disabled input does nothing). */
  const press: MouseEventHandler<HTMLSpanElement> = (event) => {
    onmousedown?.(event);
    if (event.defaultPrevented) return;
    const el = event.currentTarget;
    const input = inputOf(el);
    const target = event.target instanceof Element ? event.target : null;
    if (!input || !target) return;
    const own = target.closest(INTERACTIVE);
    if (own && own !== el && el.contains(own)) return;
    event.preventDefault();
    input.focus();
  };

  // The span has no disabled of its own: it is an author attribute, as on the Web Component.
  const mirrored = $derived({ disabled: disabled ? '' : undefined });

  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  $effect(() => {
    const root = untrack(() => ref);
    const at = requestAnimationFrame(() => root?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  });
</script>

<span
  {...rest}
  bind:this={ref}
  data-ui="text-field"
  {...mirrored}
  onmousedown={press}
>{@render children?.()}</span>
