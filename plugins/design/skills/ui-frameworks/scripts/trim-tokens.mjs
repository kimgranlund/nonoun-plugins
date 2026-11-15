// Trims a tokens.css to the custom properties a kit's stylesheets reach (D103): the ones they read, the
// ones those are defined from, and the ones a project asks to keep. Every other declaration of a custom
// property is removed, in every mode, density and media query; a rule left empty is removed with it.
//
// Used by scripts/tokens.mjs when kit.config.json says "tokens": "used", and by scripts/create-kit.mjs
// with --tokens used. It reads text and returns text.
const DECLARATION = /(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]*);[ \t]*/g;
const READ = /var\(\s*(--[A-Za-z0-9_-]+)/g;

/** Every custom property the given stylesheets read. @param {string[]} sheets */
export function reads(sheets) {
  const names = new Set();
  for (const text of sheets) for (const m of text.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(READ)) names.add(m[1]);
  return names;
}

/**
 * @param {string} css a tokens.css
 * @param {Iterable<string>} wanted the custom properties read outside it
 * @param {string[]} [keep] names to keep as well; a name that ends in "*" keeps every property that starts with it
 * @returns {{ text: string, kept: number, removed: number }}
 */
export function trim(css, wanted, keep = []) {
  /** @type {Map<string, Set<string>>} name to the properties its values read, over every declaration of it */
  const from = new Map();
  for (const m of css.matchAll(DECLARATION)) {
    const set = from.get(m[1]) ?? from.set(m[1], new Set()).get(m[1]);
    for (const r of m[2].matchAll(READ)) set.add(r[1]);
  }
  const reach = new Set();
  const queue = [...wanted];
  for (const pattern of keep) for (const name of from.keys()) if (pattern.endsWith('*') ? name.startsWith(pattern.slice(0, -1)) : name === pattern) queue.push(name);
  while (queue.length) {
    const name = queue.pop();
    if (reach.has(name) || !from.has(name)) continue;
    reach.add(name);
    for (const next of from.get(name)) queue.push(next);
  }
  // A removed declaration leaves a mark, so a line that held nothing else goes with it and the other blank lines stay.
  let text = css.replace(DECLARATION, (all, name) => (reach.has(name) ? all : '\u0000'));
  text = text.replace(/^[ \t\u0000]*\u0000[ \t\u0000]*\n/gm, '').replaceAll('\u0000', '');
  // Then rules and at-rules left with nothing but comments, innermost first.
  for (let before = ''; before !== text;) {
    before = text;
    text = text.replace(/(^|\n)[ \t]*(?:\/\*[^*]*(?:\*(?!\/)[^*]*)*\*\/\s*)*[^{};/]+\{(?:\s|\/\*[^*]*(?:\*(?!\/)[^*]*)*\*\/)*\}[ \t]*(?=\n|$)/g, '');
  }
  text = text.replace(/\{\n{2,}/g, '{\n').replace(/\n{2,}(\s*\})/g, '\n$1').replace(/\n{3,}/g, '\n\n');
  return { text, kept: reach.size, removed: from.size - reach.size };
}
