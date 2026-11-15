// Checks every component manifest against references/manifest.schema.json and the rules of
// docs/specs/manifest.md, and writes kit/registry.json, the generated index of the components.
//
//   node scripts/manifests.mjs           check the manifests, then write the registry and kit/styles/kit.css
//   node scripts/manifests.mjs --check   exit 1 if a manifest breaks a rule or the registry is stale
//
// Each problem names the rule it breaks (H1 to H12). kit/components/manifests.test.js runs this on the real
// manifests and, as the negative control, on copies with one rule broken at a time.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PREFIX = 'ui';
/** The files a component built for the Web Components target has (D48). */
const FILES = (m) => (m.kind === 'recipe' ? [`${m.id}.css`, `${m.id}.manifest.json`] : [`${m.id}.class.js`, `${m.id}.js`, `${m.id}.props.js`, `${m.id}.css`, `${m.id}.manifest.json`]);
/** The framework targets whose files the checker knows, and the files a built component has in each (X10). */
export const TARGET_FILES = { targets: ['react'], files: (/** @type {string} */ id) => [`${id}.js`, `${id}.css`] };
/** The fields a consumer routes by. The registry keeps each one unchanged (H11). */
export const ROUTING = ['kind', 'family', 'tier', 'role', 'focus'];

// ---------- the subset of JSON Schema the manifest schema uses ----------
const typeOf = (v) => (v === null ? 'null' : Array.isArray(v) ? 'array' : Number.isInteger(v) ? 'integer' : typeof v);
/**
 * @param {any} value @param {any} schema @param {any} rootSchema @param {string} at
 * @returns {string[]} One message per violation, each starting with the path of the value.
 */
export function validate(value, schema, rootSchema = schema, at = '') {
  if (schema.$ref) return validate(value, schema.$ref.split('/').slice(1).reduce((s, key) => s[key], rootSchema), rootSchema, at);
  const out = [];
  const where = at || '(the manifest)';
  const type = typeOf(value);
  if (schema.type) {
    const allowed = [].concat(schema.type);
    if (!allowed.includes(type) && !(type === 'integer' && allowed.includes('number'))) return [`${where}: is ${type}, not ${allowed.join(' or ')}`];
  }
  if ('const' in schema && value !== schema.const) out.push(`${where}: is ${JSON.stringify(value)}, not ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.includes(value)) out.push(`${where}: ${JSON.stringify(value)} is not one of ${schema.enum.join(', ')}`);
  if (type === 'string') {
    if (schema.pattern && !new RegExp(schema.pattern).test(value)) out.push(`${where}: "${value}" does not match ${schema.pattern}`);
    if (schema.minLength && value.length < schema.minLength) out.push(`${where}: shorter than ${schema.minLength} characters`);
  }
  if (type === 'array') {
    if (schema.minItems && value.length < schema.minItems) out.push(`${where}: fewer than ${schema.minItems} item(s)`);
    if (schema.uniqueItems && new Set(value.map((v) => JSON.stringify(v))).size !== value.length) out.push(`${where}: an item is listed twice`);
    if (schema.items) value.forEach((item, i) => out.push(...validate(item, schema.items, rootSchema, `${at}[${i}]`)));
  }
  if (type === 'object') {
    for (const key of schema.required ?? []) if (!(key in value)) out.push(`${where}: the field "${key}" is missing`);
    for (const [key, item] of Object.entries(value)) {
      const here = at ? `${at}.${key}` : key;
      if (schema.propertyNames?.pattern && !new RegExp(schema.propertyNames.pattern).test(key)) out.push(`${here}: the name does not match ${schema.propertyNames.pattern}`);
      if (schema.properties?.[key]) out.push(...validate(item, schema.properties[key], rootSchema, here));
      else if (schema.additionalProperties === false) out.push(`${here}: the schema has no such field`);
      else if (typeof schema.additionalProperties === 'object') out.push(...validate(item, schema.additionalProperties, rootSchema, here));
    }
  }
  return out;
}

// ---------- reading the kit ----------
export const schema = () => JSON.parse(fs.readFileSync(path.join(root, 'references/manifest.schema.json'), 'utf8'));
/** @returns {Record<string, any>} Every manifest, by the name of its folder. */
export function readManifests() {
  const dir = path.join(root, 'kit/components');
  return Object.fromEntries(fs.readdirSync(dir).filter((id) => fs.existsSync(path.join(dir, id, `${id}.manifest.json`)))
    .map((id) => [id, JSON.parse(fs.readFileSync(path.join(dir, id, `${id}.manifest.json`), 'utf8'))]));
}
/** What the rules need from the rest of the kit. A test passes its own, to break one thing at a time. */
export function context() {
  const dir = path.join(root, 'kit/components');
  return {
    states: JSON.parse(fs.readFileSync(path.join(root, 'references/states.json'), 'utf8')).states.map((s) => s.id),
    behaviours: fs.readdirSync(path.join(root, 'kit/behaviours')).filter((f) => f.endsWith('.js')).map((f) => f.slice(0, -3)),
    files: (id) => (fs.existsSync(path.join(dir, id)) ? fs.readdirSync(path.join(dir, id)) : []),
    /** The files of a component in a framework target's folder, kit/<target>/<id>/. @param {string} target @param {string} id */
    targetFiles: (target, id) => (fs.existsSync(path.join(root, 'kit', target, id)) ? fs.readdirSync(path.join(root, 'kit', target, id)) : []),
  };
}

// ---------- the rules ----------
/**
 * @param {Record<string, any>} manifests  By folder name.
 * @param {ReturnType<typeof context>} kit
 * @returns {{ rule: string, id: string, message: string }[]}
 */
export function check(manifests, kit = context()) {
  const problems = [];
  const shape = schema();
  for (const [folder, m] of Object.entries(manifests)) {
    const fail = (rule, message) => problems.push({ rule, id: folder, message });
    if (m.id !== folder) fail('H1', `the id is "${m.id}", but the folder and the file are named "${folder}"`);
    const broken = validate(m, shape);
    for (const message of broken) fail('H2', message);
    if (broken.length) continue; // the rules below read fields the schema has just refused

    // A style-only recipe is for a native element, which takes focus by itself and is given no tabindex.
    if (m.kind === 'recipe' ? m.tabindex !== null || !m.element || m.formAssociated || m.behaviours.length || Object.keys(m.attributes).some((name) => m.attributes[name].kind !== 'variant') : m.element !== undefined) fail('H15', m.kind === 'recipe' ? 'a style-only recipe names its native element, and has no tabindex, no behaviour, no form association and no attribute other than a variant' : 'only a style-only recipe names a native element');
    if (m.kind !== 'recipe' && (m.focus === 'own') !== (m.tabindex !== null)) fail('H3', `focus is "${m.focus}" and tabindex is ${m.tabindex}; a tabindex goes with focus "own", and only with it`);
    for (const state of m.states) if (!kit.states.includes(state)) fail('H4', `the state "${state}" is not in the state matrix`);
    for (const [name, a] of Object.entries(m.attributes)) {
      if (a.state && !m.states.includes(a.state)) fail('H4', `the attribute "${name}" sets the state "${a.state}", which the manifest does not list`);
      if ((a.type === 'enum') !== Array.isArray(a.values)) fail('H5', `the attribute "${name}" has type ${a.type} ${a.values ? 'and' : 'but no'} values; values go with type enum, and only with it`);
      if (a.type === 'enum' && a.values && !a.values.includes(a.default)) fail('H5', `the default of "${name}" is not one of its values`);
    }
    for (const name of m.resets) if (!(name in m.attributes)) fail('H6', `resets names "${name}", which is not an attribute`);
    if (m.resets.length && !m.formAssociated) fail('H6', 'resets is set, but the component is not form-associated');
    for (const token of m.tokens) if (!token.startsWith(`--${m.id}-`)) fail('H7', `the token ${token} does not start with --${m.id}-`);
    // A component that is only planned may name a behaviour that is still to be written.
    if (m.targets['web-components'] === 'built') for (const name of m.behaviours) if (!kit.behaviours.includes(name)) fail('H8', `the behaviour "${name}" has no file in kit/behaviours`);
    for (const [name, p] of Object.entries(m.parts)) {
      if ((name === 'root') !== (p.kind === 'root')) fail('H9', `the part "${name}" has kind ${p.kind}; the root, and only the root, has kind root`);
      if (p.kind === 'element' && !(p.tag && p.at)) fail('H9', `the element part "${name}" needs a tag and a place (at)`);
      if (p.kind === 'pseudo' && !p.pseudo) fail('H9', `the pseudo part "${name}" does not say which pseudo-element it is`);
    }

    // Relations: a family is led by the component it is named for; uses points outside it; writes stays inside both.
    const lead = manifests[m.family];
    if (!lead) fail('H10', `the family "${m.family}" is not the id of a component`);
    else if (lead.family !== m.family) fail('H10', `the family "${m.family}" is led by a component of the family "${lead.family}"`);
    for (const other of m.uses ?? []) {
      if (!manifests[other]) fail('H10', `uses names "${other}", which is not a component`);
      else if (manifests[other].family === m.family) fail('H10', `uses names "${other}", which is in the same family; the family already says so`);
    }
    for (const other of Object.keys(m.writes ?? {})) {
      const known = other === m.id || (manifests[other] && (manifests[other].family === m.family || (m.uses ?? []).includes(other)));
      if (!known) fail('H10', `writes names "${other}", which is neither this component, nor in its family, nor in uses`);
    }

    if (m.targets['web-components'] === 'built') {
      const have = kit.files(folder);
      for (const file of FILES(m)) if (!have.includes(file)) fail('H11', `the Web Components target is marked built, but ${file} is missing`);
    }
    // A framework target marked built has its component and its generated recipe (docs/specs/targets.md, X10).
    for (const target of TARGET_FILES.targets) {
      if (m.targets[target] !== 'built') continue;
      const have = kit.targetFiles?.(target, folder) ?? [];
      for (const file of TARGET_FILES.files(folder)) if (!have.includes(file)) fail('X10', `the ${target} target is marked built, but kit/${target}/${folder}/${file} is missing`);
    }
  }
  return problems;
}

// ---------- the registry ----------
/** The modules a defining module loads, itself included, as paths from the project root. */
function modules(entry) {
  const seen = new Set();
  const visit = (file) => {
    if (seen.has(file) || !fs.existsSync(path.join(root, file))) return;
    seen.add(file);
    for (const m of fs.readFileSync(path.join(root, file), 'utf8').matchAll(/(?:^|\n)\s*import\s[^'"]*?from\s*['"](\.[^'"]+)['"]/g)) visit(path.posix.join(path.posix.dirname(file), m[1]));
  };
  visit(entry);
  return [...seen].sort();
}
/** @param {Record<string, any>} manifests */
export function registry(manifests) {
  const ids = Object.keys(manifests).sort();
  const families = {};
  for (const id of ids) (families[manifests[id].family] ??= []).push(id);
  const components = ids.map((id) => {
    const m = manifests[id];
    const dir = `kit/components/${id}`;
    /** Who writes which attribute on this component's root: the other side of every `writes`. */
    const writtenBy = Object.fromEntries(ids.filter((other) => other !== id && manifests[other].writes?.[id]).map((other) => [other, manifests[other].writes[id]]));
    return {
      id, ...Object.fromEntries(ROUTING.map((field) => [field, m[field]])),
      summary: m.summary, ...(m.kind === 'recipe' ? { element: m.element, selector: `[data-${PREFIX}="${id}"]` } : { tag: `${PREFIX}-${id}` }), path: `${dir}/${id}.manifest.json`,
      targets: m.targets,
      with: [...families[m.family].filter((other) => other !== id), ...(m.uses ?? [])],
      ...(Object.keys(writtenBy).length ? { writtenBy } : {}),
      // A component that is only planned has no files yet, so it lists none.
      styles: [`${dir}/${id}.css`].filter((file) => fs.existsSync(path.join(root, file))),
      modules: modules(`${dir}/${id}.js`),
    };
  });
  return {
    generated: 'By scripts/manifests.mjs from kit/components/*/*.manifest.json. Do not edit; run node scripts/manifests.mjs.',
    schema: 1,
    prefix: PREFIX,
    shared: { styles: ['kit/styles/reset.css', 'kit/styles/tokens.css'], index: 'kit/styles/kit.css' },
    families,
    components,
  };
}
export const render = (manifests) => JSON.stringify(registry(manifests), null, 2) + '\n';
/** kit/styles/kit.css, the one stylesheet a page links (D49): the shared stylesheets, then every recipe. */
export function index(manifests) {
  const shared = ['reset.css', 'tokens.css', 'icons.css'].filter((f) => fs.existsSync(path.join(root, 'kit/styles', f))).map((f) => `./${f}`);
  const recipes = Object.keys(manifests).sort().filter((id) => fs.existsSync(path.join(root, `kit/components/${id}/${id}.css`))).map((id) => `../components/${id}/${id}.css`);
  return `@layer reset, base, tokens, recipes, utilities;\n\n/* The kit's index (D49). Link this file ahead of any kit script.\n   Generated by scripts/manifests.mjs from the components that exist. Do not edit. */\n${[...shared, ...recipes].map((f) => `@import '${f}';`).join('\n')}\n`;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const onlyCheck = process.argv.includes('--check');
  const manifests = readManifests();
  const problems = check(manifests);
  for (const p of problems) console.log(`ERROR kit/components/${p.id}/${p.id}.manifest.json ${p.rule}: ${p.message}`);
  if (!problems.length) {
    // --registry <file> holds another file against the manifests, so a test can show a stale one without touching the real one.
    const other = process.argv.includes('--registry') ? path.resolve(process.argv[process.argv.indexOf('--registry') + 1]) : null;
    for (const [file, wanted] of [['kit/registry.json', render(manifests)], ['kit/styles/kit.css', index(manifests)]]) {
      const target = other && file.endsWith('.json') ? other : path.join(root, file);
      const current = fs.existsSync(target) ? fs.readFileSync(target, 'utf8') : null;
      if (current === wanted) continue;
      if (onlyCheck) { console.log(`ERROR ${file} H12: it is ${current === null ? 'missing' : 'stale'}; run node scripts/manifests.mjs`); problems.push({ rule: 'H12', id: '', message: '' }); }
      else { fs.writeFileSync(target, wanted); console.log(`wrote ${file}`); }
    }
  }
  console.log(problems.length ? `${problems.length} problem(s)` : `${Object.keys(manifests).length} manifest(s) follow the schema and the rules${onlyCheck ? ', and the registry matches them' : ''}`);
  process.exit(problems.length ? 1 : 0);
}
