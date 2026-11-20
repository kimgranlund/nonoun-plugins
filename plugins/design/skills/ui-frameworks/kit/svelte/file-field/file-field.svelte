<script lang="ts">
  // file-field.svelte: the file field for Svelte (docs/specs/targets.md, V1 to V7).
  //
  // The root is a <div>, a plain element and not a form control (D14): the author's native file input, the child
  // marked data-part="input", carries the files, the name and the validity, is visible and works with no script
  // (J118). It is the author's child, in the `children` snippet: the component finds it in the DOM and never renders,
  // clones, moves or wraps it. As the Web Component and the React file field do, it disables the input while the
  // field is disabled (J120) and marks the root `aria-disabled` whenever the input is disabled, whoever disabled it,
  // and `invalid` while the input is (J121). It takes files dropped on it (J119): while files are dragged over it
  // the root has `data-drag`; a drop gives the input the files it would take (the first only without `multiple`, and
  // only the kinds `accept` names) and dispatches `input`, then `change`, on the input, which the author's oninput
  // and onchange on that input hear. A drag is kept from navigating the page even on a disabled field.
  //
  // Those writes are made in the DOM, in an effect after mount and as events arrive, so a listener sees them in the
  // same task. The server markup carries `disabled` of the prop, which the recipe selects; `aria-disabled` and
  // `invalid` follow once the input is known, as they do on the Web Component once it is defined (U2).
  import { untrack, type Snippet } from 'svelte';
  import type { HTMLAttributes } from 'svelte/elements';

  type Props = Omit<HTMLAttributes<HTMLDivElement>, 'children'> & {
    disabled?: boolean;
    /** The root, for `bind:ref`. */
    ref?: HTMLDivElement | null;
    children?: Snippet;
  };

  let { disabled = false, ref = $bindable(null), children, ...rest }: Props = $props();

  /** Whether a drag carries files. */
  const hasFiles = (event: DragEvent) => !!event.dataTransfer && Array.from(event.dataTransfer.types ?? []).includes('Files');
  /** Sets or removes an attribute, only when it differs. An observer then sees nothing when nothing changes. */
  const put = (el: Element, name: string, value: string | null) => {
    if (el.getAttribute(name) === value) return;
    if (value === null) el.removeAttribute(name);
    else el.setAttribute(name, value);
  };
  /**
   * Whether a file is one the `accept` list names: an extension (".pdf"), an exact type ("application/pdf") or a
   * type family ("image/*"), compared without regard to case. An empty list names everything.
   */
  const accepts = (file: File, accept: string) => {
    const tokens = accept.split(',').map((token) => token.trim().toLowerCase()).filter(Boolean);
    if (!tokens.length) return true;
    const name = file.name.toLowerCase(), type = file.type;
    return tokens.some((token) => token.startsWith('.') ? name.endsWith(token)
      : token.endsWith('/*') ? type.startsWith(token.slice(0, -1))
      : type === token);
  };
  /** The files an input would take from a drop of `files`. */
  const taken = (files: File[], input: HTMLInputElement) => {
    const kept = files.filter((file) => accepts(file, input.getAttribute('accept') ?? ''));
    return input.multiple ? kept : kept.slice(0, 1);
  };

  /** Brings the input and the mirrors in step; set while mounted. */
  let sync: (() => void) | null = null;

  const setup = (el: HTMLDivElement) => {
    /** The inputs this field disabled, so that it never enables one the author disabled. */
    const disabledHere = new WeakSet<HTMLInputElement>();
    /** The author's input, looked up each time (P6). */
    const input = () => el.querySelector(':scope > input[data-part="input"]') as HTMLInputElement | null;
    /** Whether files can be dropped now. */
    const open = () => {
      const field = input();
      return !!field && !field.disabled && !disabled;
    };

    const update = () => {
      const field = input();
      if (field) {
        if (disabled && !field.disabled) { field.disabled = true; disabledHere.add(field); }
        else if (!disabled && disabledHere.has(field)) { field.disabled = false; disabledHere.delete(field); }
      }
      if (!open()) el.removeAttribute('data-drag');
      // The root paints disabled when its input is, whoever disabled it, and invalid when its input is (J120, J121).
      put(el, 'aria-disabled', field?.disabled ? 'true' : null);
      put(el, 'invalid', field && (field.matches(':user-invalid') || field.getAttribute('aria-invalid') === 'true') ? '' : null);
    };
    sync = update;

    const off = new AbortController();
    const listen = { signal: off.signal };
    const over = (raw: Event) => {
      const event = raw as DragEvent;
      if (!hasFiles(event)) return;
      // Prevented even while disabled, so the page never navigates to the file; nothing is marked or taken.
      event.preventDefault();
      if (!open()) { if (event.dataTransfer) event.dataTransfer.dropEffect = 'none'; return; }
      if (event.dataTransfer) event.dataTransfer.dropEffect = 'copy';
      el.setAttribute('data-drag', '');
    };
    el.addEventListener('dragenter', over, listen);
    el.addEventListener('dragover', over, listen);
    el.addEventListener('dragleave', (raw) => {
      const event = raw as DragEvent;
      const to = event.relatedTarget;
      if (to instanceof Node && el.contains(to)) return;
      if (!to) {
        // Some engines give no relatedTarget: a point inside the field is a move between its children.
        const r = el.getBoundingClientRect();
        if (event.clientX > r.left && event.clientX < r.right && event.clientY > r.top && event.clientY < r.bottom) return;
      }
      el.removeAttribute('data-drag');
    }, listen);
    el.addEventListener('drop', (raw) => {
      const event = raw as DragEvent;
      el.removeAttribute('data-drag');
      if (!hasFiles(event)) return;
      event.preventDefault();
      const field = input();
      if (!field || !open()) return;
      const files = taken(Array.from(event.dataTransfer?.files ?? []), field);
      if (!files.length) return;
      const list = new DataTransfer();
      for (const file of files) list.items.add(file);
      field.files = list.files;
      field.dispatchEvent(new Event('input', { bubbles: true }));
      field.dispatchEvent(new Event('change', { bubbles: true }));
    }, listen);

    // The input's own events bring the invalid mark in step; invalid does not bubble.
    el.addEventListener('change', update, listen);
    el.addEventListener('invalid', update, { capture: true, signal: off.signal });
    el.ownerDocument.addEventListener('reset', () => queueMicrotask(() => { if (!off.signal.aborted) update(); }), { capture: true, signal: off.signal });

    // The observer sees an input that arrives, is replaced, or is disabled by the author: the author's markup, which
    // re-renders without this component, is seen this way, in a microtask of the same task.
    const observer = new MutationObserver(update);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'disabled', 'required', 'accept', 'multiple', 'aria-invalid'] });
    update();
    return () => { off.abort(); observer.disconnect(); sync = null; };
  };

  // Mounted once. `ref` is read untracked: a parent's function binding re-reads it whenever the parent's own state
  // changes, and a rerun here would forget which inputs this field disabled.
  $effect(() => untrack(() => (ref ? setup(ref) : undefined)));
  // The prop can change at any time: bring the input and the mirrors in step, in the flush that changed it.
  $effect(() => {
    void disabled;
    untrack(() => sync?.());
  });

  // The div has no disabled of its own: it is an author attribute, as on the Web Component.
  const mirrored = $derived({ disabled: disabled ? '' : undefined });

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
  data-ui="file-field"
  {...mirrored}
>{@render children?.()}</div>
