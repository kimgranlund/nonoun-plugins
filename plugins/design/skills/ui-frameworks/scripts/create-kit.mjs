// Creates a kit in a project: copies the shared stylesheets and the chosen components of one target, with
// every module they import, and writes the kit's index stylesheet. The copy keeps the layout of kit/, so
// every relative import still resolves and nothing is rewritten except a recipe for a framework target (D62).
//
//   node scripts/create-kit.mjs <destination> [--target web-components|react] [--components all|id,id,…] [--tokens all|used] [--keep name,prefix-*,…] [--force]
//
// A component brings its whole family (a tab brings tabs, tab list and tab panel). `--components` defaults to
// all the components built for the target. `--tokens used` trims tokens.css to the custom properties the copied
// stylesheets reach (D103); `--keep` names more to keep, for the project's own CSS. The destination must be empty or absent unless --force is given.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { rewrite, variantsOf } from './rewrite-recipe.mjs';
import { reads, trim } from './trim-tokens.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LAYERS = '@layer reset, base, tokens, recipes, utilities;';
const SHARED = ['reset.css', 'tokens.css', 'icons.css', 'kit.config.json'];

/** Every file a module reaches through relative imports, itself included, as paths from the project root. */
function reach(entry, seen = new Set()) {
  if (seen.has(entry) || !fs.existsSync(path.join(root, entry))) return seen;
  seen.add(entry);
  const text = fs.readFileSync(path.join(root, entry), 'utf8');
  for (const m of text.matchAll(/(?:from|import)\s*\(?\s*['"](\.{1,2}\/[^'"]+)['"]/g)) reach(path.posix.join(path.posix.dirname(entry), m[1]), seen);
  return seen;
}

/**
 * @param {{ destination: string, target?: string, components?: string[] | 'all', force?: boolean, tokens?: 'all' | 'used', keep?: string[] }} options
 * @returns {{ target: string, components: string[], files: string[] }}
 */
export function createKit({ destination, target = 'web-components', components = 'all', force = false, tokens = 'all', keep = [] }) {
  if (tokens !== 'all' && tokens !== 'used') throw new Error(`create-kit: --tokens is all or used, not ${tokens}`);
  const registry = JSON.parse(fs.readFileSync(path.join(root, 'kit/registry.json'), 'utf8'));
  const byId = Object.fromEntries(registry.components.map((c) => [c.id, c]));
  // A style-only recipe is written for a native element, so every target has it (D93).
  const has = (c) => c.targets[target] === 'built' || (c.kind === 'recipe' && c.targets['web-components'] === 'built');
  if (!registry.components.some((c) => c.targets[target] !== undefined)) throw new Error(`create-kit: no target named ${target}`);
  const asked = components === 'all' ? registry.components.filter(has).map((c) => c.id) : components;
  const chosen = new Set();
  for (const id of asked) {
    const c = byId[id];
    if (!c) throw new Error(`create-kit: no component named ${id}; see kit/registry.json`);
    for (const member of registry.families[c.family] ?? [id]) {
      if (!has(byId[member])) throw new Error(`create-kit: ${member} is not built for ${target}`);
      chosen.add(member);
    }
  }
  if (fs.existsSync(destination) && fs.readdirSync(destination).length && !force) throw new Error(`create-kit: ${destination} is not empty; pass --force to write into it`);

  /** Destination path (from the kit folder) to its text. */
  const out = new Map();
  const copy = (file) => out.set(file.replace(/^kit\//, ''), fs.readFileSync(path.join(root, file)));
  // A framework target also takes native.css, which resets what a native root brings (X11).
  const sheets = target === 'web-components' ? SHARED : ['reset.css', 'native.css', ...SHARED.slice(1)];
  for (const f of sheets) if (fs.existsSync(path.join(root, 'kit/styles', f))) copy(`kit/styles/${f}`);
  const recipes = [];
  for (const id of [...chosen].sort()) {
    const c = byId[id], folder = `kit/components/${id}`;
    copy(`${folder}/${id}.manifest.json`);
    if (c.kind === 'recipe' || target === 'web-components') {
      copy(`${folder}/${id}.css`);
      recipes.push(`../components/${id}/${id}.css`);
      if (c.kind !== 'recipe') for (const f of reach(`${folder}/${id}.js`)) copy(f);
    } else {
      const manifest = JSON.parse(fs.readFileSync(path.join(root, `${folder}/${id}.manifest.json`), 'utf8'));
      const css = rewrite(fs.readFileSync(path.join(root, `${folder}/${id}.css`), 'utf8'), { id, prefix: registry.prefix, variants: variantsOf(manifest) });
      out.set(`${target}/${id}/${id}.css`, Buffer.from(css));
      recipes.push(`../${target}/${id}/${id}.css`);
      for (const f of reach(`kit/${target}/${id}/${id}.js`)) copy(f);
    }
  }
  let trimmed;
  if (tokens === 'used' && out.has('styles/tokens.css')) {
    const others = [...out].filter(([file]) => file.endsWith('.css') && file !== 'styles/tokens.css').map(([, data]) => String(data));
    trimmed = trim(String(out.get('styles/tokens.css')), reads(others), keep);
    out.set('styles/tokens.css', Buffer.from(trimmed.text));
    // The copied config says so, and scripts/tokens.mjs then writes the same trimmed file when the project restyles.
    const config = JSON.parse(String(out.get('styles/kit.config.json')));
    out.set('styles/kit.config.json', Buffer.from(JSON.stringify({ ...config, tokens: 'used', ...(keep.length ? { keep } : {}) }, null, 2) + '\n'));
  }
  const shared = sheets.filter((f) => f.endsWith('.css') && out.has(`styles/${f}`)).map((f) => `./${f}`);
  out.set('styles/kit.css', Buffer.from(`${LAYERS}\n\n/* The kit's index. Link this file ahead of any kit script. Written by create-kit for the ${target} target. */\n${[...shared, ...recipes].map((f) => `@import '${f}';`).join('\n')}\n`));
  out.set('kit.json', Buffer.from(JSON.stringify({ target, prefix: registry.prefix, components: [...chosen].sort(), tokens }, null, 2) + '\n'));
  for (const [file, data] of out) {
    const to = path.join(destination, file);
    fs.mkdirSync(path.dirname(to), { recursive: true });
    fs.writeFileSync(to, data);
  }
  return { target, components: [...chosen].sort(), files: [...out.keys()].sort(), tokens: trimmed ? { kept: trimmed.kept, removed: trimmed.removed } : null };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const flag = (name) => (args.includes(name) ? args[args.indexOf(name) + 1] : undefined);
  const destination = args.find((a, i) => !a.startsWith('--') && !['--target', '--components', '--tokens', '--keep'].includes(args[i - 1]));
  if (!destination) { console.error('usage: node scripts/create-kit.mjs <destination> [--target web-components|react] [--components all|id,id,…] [--tokens all|used] [--keep name,prefix-*,…] [--force]'); process.exit(2); }
  try {
    const list = flag('--components');
    const made = createKit({ destination: path.resolve(destination), target: flag('--target'), components: !list || list === 'all' ? 'all' : list.split(','), force: args.includes('--force'), tokens: /** @type {'all' | 'used' | undefined} */ (flag('--tokens')), keep: flag('--keep')?.split(',') });
    console.log(`wrote ${made.files.length} files to ${destination}: ${made.components.length} component(s) for ${made.target}${made.tokens ? `; tokens.css keeps ${made.tokens.kept} custom properties of ${made.tokens.kept + made.tokens.removed}` : ''}`);
  } catch (error) { console.error(String(/** @type {Error} */ (error).message)); process.exit(1); }
}
