// Writes kit/styles/icons.css from the SVG files that kit/styles/kit.config.json names (docs/specs/icons.md, I2 and I3).
//
//   node scripts/icons.mjs                     write the file
//   node scripts/icons.mjs --check             exit 1 if the file differs from what the config and the SVG files give now,
//                                              or if a named file is missing or is not one svg element with a viewBox
//   --config <file>   read the icons block of another config (a test uses this for a broken library)
//   --out <file>      write or check another stylesheet (a test uses this for a stale copy)
//
// The config's `icons.source` is a folder of SVG files, relative to the project or absolute; `icons.names` maps each
// name the kit uses to a file in it, without the extension. Each name becomes one rule in the tokens cascade layer:
//   ui-icon[name="<name>"], [data-ui="icon"][name="<name>"] { --glyph: url("data:image/svg+xml,…"); }
// The recipe of the icon component draws the glyph as a mask over a box in the ink (I1).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LAYERS = '@layer reset, base, tokens, recipes, utilities;';
const TAG = 'ui-icon';
const NAME = /^[a-z][a-z0-9-]*$/;

/**
 * The text of one SVG file as a single element, or the reason it is not one (I3): the file holds exactly one
 * root element, it is an svg element, and it has a viewBox of four numbers. An XML declaration, a doctype and
 * comments around it are allowed and dropped.
 * @param {string} text
 * @returns {{ svg: string } | { problem: string }}
 */
export function parseSvg(text) {
  const body = text.replace(/^﻿/, '').replace(/<\?xml[\s\S]*?\?>/g, '').replace(/<!DOCTYPE[^>]*>/gi, '').replace(/<!--[\s\S]*?-->/g, '').trim();
  if (!body) return { problem: 'is empty' };
  const tags = /<(\/?)([A-Za-z][\w:.-]*)((?:[^>"']|"[^"]*"|'[^']*')*?)(\/?)>/g;
  let depth = 0, roots = 0, first = '', open = '', end = -1;
  for (const m of body.matchAll(tags)) {
    const [whole, closing, name, attrs, selfClosing] = m;
    if (depth === 0) {
      if (closing) return { problem: `closes </${name}> that was never opened` };
      const before = body.slice(end === -1 ? 0 : end, m.index).trim();
      if (before) return { problem: 'has text outside its root element' };
      roots++;
      if (roots === 1) { first = name; open = attrs; }
    }
    if (closing) depth--;
    else if (!selfClosing) depth++;
    if (depth < 0) return { problem: `closes </${name}> that was never opened` };
    end = /** @type {number} */ (m.index) + whole.length;
  }
  if (roots === 0) return { problem: 'holds no element' };
  if (depth !== 0) return { problem: 'leaves an element open' };
  if (body.slice(end).trim()) return { problem: 'has text after its root element' };
  if (roots > 1) return { problem: `holds ${roots} root elements, not one svg element` };
  if (first !== 'svg') return { problem: `its root element is <${first}>, not <svg>` };
  const viewBox = /\sviewBox\s*=\s*("([^"]*)"|'([^']*)')/.exec(' ' + open);
  if (!viewBox) return { problem: 'its svg element has no viewBox' };
  const numbers = (viewBox[2] ?? viewBox[3]).trim().split(/[\s,]+/);
  if (numbers.length !== 4 || numbers.some((n) => n === '' || !Number.isFinite(Number(n))) || Number(numbers[2]) <= 0 || Number(numbers[3]) <= 0) {
    return { problem: `its viewBox "${viewBox[2] ?? viewBox[3]}" is not four numbers with a positive width and height` };
  }
  return { svg: body };
}

/**
 * The SVG as the body of a data URI, encoded the way checkbox.css encodes its glyphs: whitespace collapsed,
 * double quotes turned into single quotes, and the characters a URL or CSS would misread percent-encoded.
 * @param {string} svg
 */
export function encode(svg) {
  return svg
    .replace(/\s+/g, ' ').replace(/>\s+</g, '><').replace(/\s*\/>/g, '/>').trim()
    .replaceAll('"', "'")
    .replace(/[%#<>{}|\\^`\[\]]/g, (c) => '%' + c.charCodeAt(0).toString(16).toUpperCase().padStart(2, '0'));
}

/**
 * Builds the stylesheet. Throws, naming every problem, if a name is malformed, a file is missing or a file is not
 * one svg element with a viewBox (I3).
 * @param {{ config?: string }} [options]  `config` is the path of the config to read; the default is the kit's.
 * @returns {{ text: string, names: string[] }}
 */
export function build({ config = path.join(root, 'kit/styles/kit.config.json') } = {}) {
  const icons = JSON.parse(fs.readFileSync(config, 'utf8')).icons;
  if (!icons || typeof icons.source !== 'string' || !icons.names || typeof icons.names !== 'object') throw new Error(`${config} has no icons block with a source and names`);
  const folder = path.resolve(root, icons.source);
  const problems = [];
  const rules = [];
  for (const [name, file] of Object.entries(icons.names)) {
    if (!NAME.test(name)) { problems.push(`the name "${name}" is not lower-case letters, digits and hyphens`); continue; }
    const where = path.join(folder, `${file}.svg`);
    const shown = path.relative(root, where).startsWith('..') ? where : path.relative(root, where);
    if (!fs.existsSync(where)) { problems.push(`${name}: ${shown} is missing`); continue; }
    const parsed = parseSvg(fs.readFileSync(where, 'utf8'));
    if ('problem' in parsed) { problems.push(`${name}: ${shown} ${parsed.problem}`); continue; }
    // The second selector is the root a framework target renders: a native element that carries data-ui (X1).
    rules.push(`  ${TAG}[name="${name}"], [data-ui="icon"][name="${name}"] { --glyph: url("data:image/svg+xml,${encode(parsed.svg)}"); }`);
  }
  if (problems.length) throw new Error(`icons: ${problems.length} problem(s)\n  ${problems.join('\n  ')}`);
  const source = path.relative(root, config).startsWith('..') ? config : path.relative(root, config);
  const text = `${LAYERS}

/* Generated by scripts/icons.mjs from the SVG files in ${icons.source} that ${source} names. Do not edit.
   ${icons.library ?? 'The library names no licence.'} */

@layer tokens {
${rules.join('\n')}
}
`;
  return { text, names: Object.keys(icons.names) };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const option = (flag) => { const at = args.indexOf(flag); return at === -1 ? undefined : args[at + 1]; };
  const check = args.includes('--check');
  const config = option('--config') ? path.resolve(option('--config')) : undefined;
  const target = option('--out') ? path.resolve(option('--out')) : path.join(root, 'kit/styles/icons.css');
  const shown = path.relative(root, target).startsWith('..') ? target : path.relative(root, target);
  let built;
  try { built = build({ config }); } catch (error) { console.log(`ERROR ${/** @type {Error} */ (error).message}`); process.exit(1); }
  const current = fs.existsSync(target) ? fs.readFileSync(target, 'utf8') : null;
  if (check) {
    if (current !== built.text) { console.log(`ERROR ${shown} is ${current === null ? 'missing' : 'stale'}; run node scripts/icons.mjs`); process.exit(1); }
    console.log(`${shown} matches the config and its ${built.names.length} SVG file(s)`);
  } else {
    fs.writeFileSync(target, built.text);
    console.log(`wrote ${shown}: ${built.text.length} bytes, ${built.names.length} icon(s)`);
  }
}
