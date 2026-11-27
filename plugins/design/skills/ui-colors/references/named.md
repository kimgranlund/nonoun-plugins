# Named colors (`scripts/named.mjs`)

A reference of named colors as DTCG tokens (`named.dtcg.json`) and CSS variables (`named.css`). It is a lookup set to pick from or map against, not a color system: no modes, roles or contrast.

## Sources

| Source | Command | Network |
|---|---|---|
| The 148 CSS Color 4 named colors, bundled in `scripts/system/named-colors.json` (W3C, with URL, dates, licence and a sha256 of the data) | `node scripts/named.mjs --out DIR` (`--source css` is the default) | None |
| A saved file: a `ColorItem` JSON array (or `{ "items": [...] }`), a cache this script wrote, or the saved Encycolorpedia named-colors page as Markdown (a numbered list; each entry a name and its `#hex`, linked to `/hex`) | `node scripts/named.mjs --from FILE [--lang CODE] --out DIR` | None |
| The Encycolorpedia API, `GET /v1/colors/named/{lang}` with your own token | `ENCYCOLORPEDIA_TOKEN=... node scripts/named.mjs --source encycolorpedia --lang en --cache FILE [--refresh] --out DIR` | Only without a cache, or with `--refresh` |

`--lang` is one of the API's 24 codes (`en` by default for the API). The token is read from `ENCYCOLORPEDIA_TOKEN` only, sent as `Authorization: Bearer`, and never written to the cache, the output or a message. A run that needs a request and has no token exits 2 naming the variable; a run with an existing cache and no `--refresh` makes no request and needs no token. A failed request exits 1 and writes no cache. The cache holds the raw response body with its URL, language, fetch time and sha256; a cache whose body does not hash to its sha256 is refused.

No Encycolorpedia data ships with the skill: its API description states no licence that grants reuse, and its names include brand names. Keep caches and saved pages local; do not commit or bundle them.

## Output

```
named.dtcg.json   $extensions["ui-colors"].provenance, then named.<source>.<key>: one color token per entry
named.css         :root { --named-<source>-<key>: #rrggbb; }
```

- `<source>` is `css` or `encycolorpedia`. Keys are name slugs (lower case, ASCII, hyphens). A name that appears more than once takes its hex as a suffix on every occurrence (`amber-ca6924`); a slug two different names share takes `-2`, `-3` in source order; a name with no Latin letters falls back to its hex. Tokens keep the source order.
- Each token is `$type: "color"` with `$value` in the shape `families.mjs` writes (`colorSpace: "srgb"`, `components`, `alpha`, `hex`; shared in `scripts/system/dtcg.js`). `hex` is the source's, lower-cased. `$extensions["ui-colors"]` holds the original `name`, `oklch` and `hct` (CAM16 hue and chroma under the default viewing conditions, CIE L* tone; `scripts/system/hct.js`) computed by the skill. Encycolorpedia entries keep `lrv`, `undertone` and `codes` under `$extensions.encycolorpedia` when the source has them.
- `$extensions["ui-colors"].provenance` names the `source`, `title`, `url`, `language`, `fetched` date, `sha256` (of the bundled data, the saved file or the response body), `license` (null where the source states none) and, for a saved file, its file name and format.

## Checks

`check.mjs` runs `named.mjs` offline: the bundled data (148 names, hash), the CSS source (every hex the bundled value, red at its published HCT), invented `ColorItem` fixtures as JSON, Markdown and an API cache (round trip, distinct keys for a repeated name and a slug clash, provenance), and a run without `ENCYCOLORPEDIA_TOKEN` (exit 2, nothing written). Negative controls corrupt a fixture hex, collapse a repeated name, drop the provenance and edit the bundled data.
