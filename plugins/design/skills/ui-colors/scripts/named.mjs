#!/usr/bin/env node
// named.mjs: a named-color reference as DTCG (named.dtcg.json) and CSS (named.css). Contract: ../references/named.md.
//   --source css (default)        the bundled CSS Color 4 named colors (system/named-colors.json), no network
//   --from FILE                   a saved file: a ColorItem JSON array, a cache this script wrote, or the saved
//                                 Encycolorpedia named-colors page as Markdown; no network
//   --source encycolorpedia       GET /v1/colors/named/{lang} with ENCYCOLORPEDIA_TOKEN, the raw response kept in --cache;
//                                 an existing cache is read instead of a request unless --refresh is given
// Exit codes: 0 written; 1 a source that does not parse or a failed request; 2 bad usage or a missing token.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, basename } from 'node:path';
import { createHash } from 'node:crypto';
import { parseArgs } from 'node:util';
import { dtcgColor } from './system/dtcg.js';
import { hctOfHex, oklchOfHex, parseHex } from './system/hct.js';

const USAGE = 'usage: node named.mjs [--source css | --source encycolorpedia --lang CODE --cache FILE [--refresh] | --from FILE [--lang CODE]] --out DIR';
const TOKEN_VAR = 'ENCYCOLORPEDIA_TOKEN';
const API = 'https://api.encycolorpedia.com/v1/colors/named/';
const LANGS = ['en', 'ar', 'zh', 'es', 'hi', 'he', 'pt', 'ja', 'ru', 'de', 'ko', 'fr', 'nl', 'it', 'tr', 'pl', 'sv', 'el', 'id', 'fa', 'ro', 'uk', 'vi', 'fil'];
const fail = (code, msg) => { console.error(msg); process.exit(code); };
const sha = (b) => createHash('sha256').update(b).digest('hex');
const r4 = (x) => +(+x).toFixed(4) || 0;

let values;
try { ({ values } = parseArgs({ options: { source: { type: 'string' }, lang: { type: 'string' }, cache: { type: 'string' }, refresh: { type: 'boolean' }, from: { type: 'string' }, out: { type: 'string' } } })); }
catch (e) { fail(2, e.message + '\n' + USAGE); }
if (!values.out) fail(2, USAGE);
if (values.from && values.source) fail(2, '--from and --source are exclusive\n' + USAGE);
const source = values.from ? 'file' : values.source ?? 'css';
if (!['css', 'encycolorpedia', 'file'].includes(source)) fail(2, `--source must be css or encycolorpedia, not ${JSON.stringify(values.source)}\n` + USAGE);
const lang = values.lang ?? (source === 'encycolorpedia' ? 'en' : null);
if (lang !== null && !LANGS.includes(lang)) fail(2, `--lang must be one of ${LANGS.join(', ')}`);

// ── Sources: each returns { group, entries: [{ name, hex, extra? }], provenance } ─────────────────────────────
const hexOf = (h) => { const m = /^#?([0-9a-f]{6})$/i.exec(String(h ?? '').trim()); return m ? '#' + m[1].toLowerCase() : null; };
function fromCss() {
  const d = JSON.parse(readFileSync(new URL('./system/named-colors.json', import.meta.url), 'utf8')), P = d.provenance;
  if (sha(JSON.stringify(d.colors)) !== P.colorsSha256) fail(1, 'system/named-colors.json does not hash to provenance.colorsSha256');
  return { group: 'css', entries: Object.entries(d.colors).map(([name, hex]) => ({ name, hex })),
    provenance: { source: 'css', title: P.source, url: P.url, language: null, published: P.published, fetched: P.fetched, sha256: P.colorsSha256, license: P.license } };
}
// A ColorItem array (bare, or under `items`): name and hex required; lrv, undertone and codes kept.
function itemsOf(body, what) {
  let j; try { j = JSON.parse(body); } catch (e) { fail(1, `${what}: not JSON (${e.message})`); }
  const arr = Array.isArray(j) ? j : Array.isArray(j?.items) ? j.items : null;
  if (!arr) fail(1, `${what}: expected a JSON array of ColorItem (or { items: [...] })`);
  return arr.map((it, i) => {
    const hex = hexOf(it?.hex);
    if (typeof it?.name !== 'string' || !it.name.trim() || !hex) fail(1, `${what}: item ${i} needs a name and a 6-digit hex`);
    const extra = {}; for (const k of ['lrv', 'undertone', 'codes']) if (it[k] !== undefined && it[k] !== null) extra[k] = it[k];
    return { name: it.name.trim(), hex, extra };
  });
}
// The saved named-colors page: a numbered list, each entry `N.  [<name>  \n    #<hex>](/<hex>)`.
const MD_ENTRY = /^[ \t]*(\d+)\.[ \t]+\[(.*?)[ \t]*\r?\n[ \t]*#([0-9a-fA-F]{6})\]\(\/([0-9a-fA-F]{6})\)/gm;
const unescapeMd = (s) => s.replace(/\\([\\`*_{}[\]()#+\-.!|<>~"])/g, '$1').trim();
function markdownEntries(text, what) {
  const entries = []; let last = 0;
  for (const m of text.matchAll(MD_ENTRY)) {
    if (m[3].toLowerCase() !== m[4].toLowerCase()) fail(1, `${what}: entry ${m[1]} shows #${m[3]} but links /${m[4]}`);
    entries.push({ name: unescapeMd(m[2]), hex: '#' + m[3].toLowerCase(), extra: {} }); last = Math.max(last, +m[1]);
  }
  const listed = [...text.matchAll(/^[ \t]*(\d+)\.[ \t]+\[/gm)].length;
  if (!entries.length) fail(1, `${what}: no named-color entries found (expected a numbered list of [name\\n#hex](/hex))`);
  if (listed !== entries.length || last !== entries.length) fail(1, `${what}: ${entries.length} entries parsed, ${listed} list items, last number ${last}`);
  return entries;
}
function fromFile(path) {
  if (!existsSync(path)) fail(2, `--from ${path}: no such file`);
  const buf = readFileSync(path), text = buf.toString('utf8'), what = basename(path);
  const base = { source: 'encycolorpedia', title: 'Encycolorpedia named colors', url: null, language: lang, fetched: null, sha256: sha(buf), license: null, file: what };
  if (/^\s*[[{]/.test(text)) {
    let j; try { j = JSON.parse(text); } catch (e) { fail(1, `${what}: not JSON (${e.message})`); }
    if (j && !Array.isArray(j) && typeof j.body === 'string') return fromCache(j, what); // a cache this script wrote
    return { group: 'encycolorpedia', entries: itemsOf(text, what), provenance: { ...base, format: 'ColorItem JSON' } };
  }
  return { group: 'encycolorpedia', entries: markdownEntries(text, what), provenance: { ...base, url: 'https://encycolorpedia.com/named', format: 'saved named-colors page (Markdown)' } };
}
function fromCache(c, what) {
  if (sha(c.body) !== c.sha256) fail(1, `${what}: the cached body does not hash to its sha256`);
  return { group: 'encycolorpedia', entries: itemsOf(c.body, what),
    provenance: { source: 'encycolorpedia', title: 'Encycolorpedia named colors', url: c.url, language: c.lang, fetched: c.fetched, sha256: c.sha256, license: c.license ?? null } };
}
async function fromApi() {
  const cache = values.cache;
  if (!cache || !existsSync(cache) || values.refresh) {
    const token = process.env[TOKEN_VAR];
    if (!token) fail(2, `${TOKEN_VAR} is not set: export your Encycolorpedia API token as ${TOKEN_VAR} (it is read from the environment only and never written)`);
    if (!cache) fail(2, '--source encycolorpedia needs --cache FILE (the raw response is kept there)\n' + USAGE);
    const url = API + lang;
    let res; try { res = await fetch(url, { headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' } }); } catch (e) { fail(1, `GET ${url} failed: ${e.message}`); }
    const body = await res.text();
    if (!res.ok) fail(1, `GET ${url}: HTTP ${res.status}; no cache written`);
    itemsOf(body, url); // parse before caching
    const record = { $description: 'Raw Encycolorpedia API response cached by named.mjs. Local data: do not commit or bundle it.', url, lang, fetched: new Date().toISOString(), sha256: sha(body), license: null, body };
    mkdirSync(join(cache, '..'), { recursive: true }); writeFileSync(cache, JSON.stringify(record, null, 2) + '\n');
    console.log(`cached ${url} (${body.length} bytes) in ${cache}`);
  }
  let c; try { c = JSON.parse(readFileSync(cache, 'utf8')); } catch (e) { fail(1, `--cache ${cache}: not a cache this script wrote (${e.message})`); }
  return fromCache(c, basename(cache));
}

// ── Keys: name slugs; a repeated name takes its hex as a suffix (amber-ca6924); any clash left takes -2, -3 ──────
const slug = (s, hex) => s.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || hex.slice(1);
function keyed(entries) {
  const seen = new Map(); for (const e of entries) { const k = e.name.toLowerCase(); seen.set(k, (seen.get(k) || 0) + 1); }
  const used = new Set();
  return entries.map((e) => {
    let k = slug(e.name, e.hex); if (seen.get(e.name.toLowerCase()) > 1) k += '-' + e.hex.slice(1);
    let key = k; for (let n = 2; used.has(key); n++) key = `${k}-${n}`;
    used.add(key); return { ...e, key };
  });
}

const S = source === 'css' ? fromCss() : source === 'file' ? fromFile(values.from) : await fromApi();
const rows = keyed(S.entries), group = {}, css = [];
for (const r of rows) {
  const t = dtcgColor('srgb', parseHex(r.hex).map(r4), 1, r.hex);
  t.$extensions = { 'ui-colors': { name: r.name, oklch: oklchOfHex(r.hex).map(r4), hct: hctOfHex(r.hex).map((x) => +x.toFixed(2)) } };
  if (S.group === 'encycolorpedia' && Object.keys(r.extra).length) t.$extensions.encycolorpedia = r.extra;
  group[r.key] = t;
  css.push(`  --named-${S.group}-${r.key}: ${r.hex};`);
}
const doc = { $description: `Named colors from ${S.provenance.title}${S.provenance.language ? ` (${S.provenance.language})` : ''}, written by ui-colors named.mjs. sRGB values; $extensions["ui-colors"] holds each original name, OKLCH and HCT (CAM16, default viewing conditions) computed by the skill.`,
  $extensions: { 'ui-colors': { provenance: S.provenance, count: rows.length } }, named: { [S.group]: group } };
const out = values.out; mkdirSync(out, { recursive: true });
writeFileSync(join(out, 'named.dtcg.json'), JSON.stringify(doc, null, 2) + '\n');
writeFileSync(join(out, 'named.css'), `/* Named colors: ${S.provenance.title}${S.provenance.language ? ` (${S.provenance.language})` : ''}, ${rows.length} colors, sRGB hex. Written by ui-colors named.mjs; provenance in named.dtcg.json. */\n:root {\n${css.join('\n')}\n}\n`);
console.log(`named: ${rows.length} colors from ${S.provenance.title} into ${join(out, 'named.dtcg.json')} and named.css`);
