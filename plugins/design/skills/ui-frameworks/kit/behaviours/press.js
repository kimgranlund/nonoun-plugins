// @ts-check
/**
 * press: makes a root activate from the keyboard the way a native button does (D45).
 * A behaviour: it imports nothing, takes a root and options, and returns its cleanup (D12).
 *
 * Rules: docs/specs/foundation.md, F8 to F10.
 *
 * - Enter activates at key down, Space at key up. Both have their default action prevented.
 * - While either key is held, the root carries `data-active`, the only attribute this behaviour writes.
 * - Activation calls `root.click()`, so a component listens for `click` and nothing else.
 * - A key pressed inside a child, such as a native input, is left alone.
 *
 * Unlike a native button, a held Enter does not repeat the activation.
 *
 * @param {HTMLElement} root
 * @param {{ disabled?: () => boolean }} [options]  `disabled` is read at each key press.
 * @returns {() => void}
 */
export function press(root, options = {}) {
  const off = new AbortController();
  const listen = { signal: off.signal };
  const disabled = () => options.disabled?.() ?? false;
  /** The key that went down on the root and has not come up. */
  let held = '';
  const release = () => { held = ''; root.removeAttribute('data-active'); };

  root.addEventListener('keydown', (event) => {
    if (event.target !== root || (event.key !== 'Enter' && event.key !== ' ')) return;
    event.preventDefault();
    if (event.repeat || disabled()) return;
    held = event.key;
    root.setAttribute('data-active', '');
    if (held === 'Enter') root.click();
  }, listen);

  root.addEventListener('keyup', (event) => {
    if (!held || event.key !== held) return;
    const space = held === ' ';
    release();
    if (space && !disabled()) root.click();
  }, listen);

  // Focus left while the key was down: the press is abandoned, as on a native button.
  root.addEventListener('blur', release, listen);

  return () => { off.abort(); release(); };
}
