// Rewrites a recipe for the React, Svelte and Solid targets (D62; CSS contract, C23 and C24).
//
// A recipe is written once, for the Web Components target: its root is a tag and a variant is an author
// attribute. The other targets render a native element as the root, which carries data-<prefix>="<id>" and
// data-<variant name>. So the tag in @scope (…) and each variant attribute selector are rewritten, and nothing
// else: the conditions already cover a native element (D26).
//
// This module imports nothing, so a browser test can load it as well as the skill's copy step.
//
//   import { rewrite } from './rewrite-recipe.mjs';
//   rewrite(css, { id: 'button', prefix: 'ui', variants: ['variant'] })

/**
 * @param {string} css  The recipe as written for the Web Components target.
 * @param {{ id: string, prefix: string, variants: string[] }} component  `variants` are the names of the
 *   manifest's attributes whose kind is variant.
 * @returns {string}
 */
export function rewrite(css, { id, prefix, variants }) {
  const tag = `${prefix}-${id}`;
  if (!css.includes(`@scope (${tag})`)) throw new Error(`rewrite: the recipe has no @scope (${tag})`);
  let out = css.replace(`@scope (${tag})`, `@scope ([data-${prefix}="${id}"])`);
  for (const name of variants) out = out.replaceAll(`:scope[${name}=`, `:scope[data-${name}=`);
  return out;
}

/** The names of a manifest's variant attributes. @param {any} manifest */
export const variantsOf = (manifest) => Object.entries(manifest.attributes).filter(([, a]) => a.kind === 'variant').map(([name]) => name);
