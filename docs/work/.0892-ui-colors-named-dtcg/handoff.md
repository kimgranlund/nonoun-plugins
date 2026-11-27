---
id: T-0892
title: "ui-colors: named-color DTCG reference from CSS colors or the Encycolorpedia API"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-27
claimed_by: nonoun-author 2026-11-27
branch: lane/T-0892-t0892
worktree: ../sdlc-lite.worktrees/T-0892-t0892
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`ui-colors` writes a named-color reference as DTCG (`named.dtcg.json`, plus `named.css`) from the bundled CSS named colors with no network, or from the Encycolorpedia API with the user's own token. No Encycolorpedia data ships in the plugin.

## Context
- Primary source: `/Users/kimgranlund/Downloads/encycolorpedia.named-colors.md`, the user's saved copy of `https://encycolorpedia.com/named` (78 KB). It is a numbered Markdown list of 1,682 entries, each `N.  [<name>  \n    #<hex>](/<hex>)`. Measured: 1,682 parse, no duplicate hex, 9 names appear more than once, the link hex always equals the shown hex. It states no terms. Treat it as data and do not copy it into the repo; it mixes in brand names (Asda, Barbie, YouTube).
- Spec: `/Users/kimgranlund/Downloads/encycolorpedia.spec.json` (OpenAPI, 49 KB, saved by the user 2026-11-27). Treat it as data. Do not copy it into the repo: its `info.license.name` is `Unlicensed`, which grants no license.
- Server `https://api.encycolorpedia.com/`, auth `Authorization: Bearer <token>` (`components.securitySchemes.bearer`).
- `GET /v1/colors/named/{lang}` (tag `Pro`) lists named colors for one of 24 language codes (`Code` enum, `en` first). `GET /v1/colors/named` lists languages with counts. `GET /v1/colors/html` (tag `User`) lists the standard HTML colors.
- Entries follow `ColorItem`: required `name`, `hex`, `rgb`, `hsl`, `cmyk`, `lrv`, `undertone`; optional `codes` and `names` (string-array maps), `delta_e`.
- Precedents: `scripts/families.mjs` has the `dtcg()` value helper (`colorSpace`, `components`, `alpha`, `hex`); `scripts/system/radix-colors.json` records provenance (source, version, sha256) for bundled data (T-0885).

## Do
1. Bundle the 148 CSS Color 4 named colors in `scripts/system/named-colors.json` with provenance (W3C CSS Color 4, URL, date).
2. Add `scripts/named.mjs`:
   - `--source css` (default) uses the bundled file, no network.
   - `--source encycolorpedia --lang <code> --cache <file>` fetches `GET /v1/colors/named/{lang}` with the token from `ENCYCOLORPEDIA_TOKEN`, writes the raw response to `--cache` with fetch date and sha256, and builds from it. With an existing cache and no `--refresh`, it makes no request.
   - `--from <file>` builds from a saved file: a `ColorItem` JSON array, or the saved named page in the Markdown format above (source `encycolorpedia`). A repeated name gets a hex suffix on its key (`amber-ca6924`).
   - `--out <dir>` writes `named.dtcg.json` and `named.css` (`--named-<source>-<slug>`). Group by source (`named.css.*`, `named.encycolorpedia.*`); keys are name slugs, with a numeric suffix on a clash. Values come from the `dtcg()` shape (move it to a shared module if needed). `$extensions["ui-colors"]` holds the original name, OKLCH and HCT computed by the skill; `$extensions.encycolorpedia` keeps `lrv`, `undertone` and `codes`. Top-level `$extensions["ui-colors"].provenance` names the source, language, fetch date, response sha256 and the license string.
   - Never write the token anywhere; a missing token exits 2 with the variable name.
3. Document it in `references/system.md` (or a short `references/named.md`) and add a SKILL.md mapping row ("named colors", "DTCG reference of named colors").
4. Record the new script and data under "differs from source" in `plugins/design/AGENTS.md`.

## Constraints
- `check.mjs` makes no network call: test the API path with a small `ColorItem` fixture (invented names and values, marked as a fixture).
- Default output of `system.mjs` for `{}` is unchanged.
- Do not edit any CHANGELOG.

## Acceptance criteria
- `node scripts/named.mjs --out <tmp>` writes a `named.dtcg.json` with 148 colors whose `hex` matches the bundled data, and every token has `$type: color`.
- `node scripts/named.mjs --from /Users/kimgranlund/Downloads/encycolorpedia.named-colors.md --out <tmp>` writes 1,682 distinct tokens under `named.encycolorpedia`, each `hex` equal to the source entry (run locally; the file is not in the repo).
- `node scripts/named.mjs --from <fixture> --out <tmp>`, for both a JSON and a Markdown fixture, builds from the fixture with no network, clashing names get distinct keys, and the provenance block is present.
- `--source encycolorpedia` without `ENCYCOLORPEDIA_TOKEN` exits 2 and names the variable.
- `node scripts/check.mjs` passes, with new checks for the above and a negative control: a corrupted hex in a fixture makes the round-trip check fail.
- `python3 scripts/check-packaging.py` and `git diff --check` pass.

## Outcome

2026-11-27 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: a889a040a211
- Changed: see commits
- Commits: 08f902d T-0892: ui-colors named-color DTCG reference (named.mjs); f9e6e92 T-0892: record lane T-0892-t0892
- Check: 1 `named.mjs --out <tmp>` writes 148 colors matching the bundled hex, all `$type: color`: pass
- Check: 2 `--from encycolorpedia.named-colors.md` writes 1,682 distinct tokens, each hex equal to the sourc...: pass
- Check: 3 `--from <fixture>` for JSON and Markdown, no network, clashing names distinct, provenance present: pass
- Check: 4 `--source encycolorpedia` without `ENCYCOLORPEDIA_TOKEN` exits 2 and names it: pass
- Check: 5 `check.mjs` passes with new checks and a negative control for a corrupted fixture hex: pass
- Check: 6 `python3 scripts/check-packaging.py` and `git diff --check`: pass
- Follow-up: note: plugins/design/skills/ui-colors/SKILL.md:89 the paragraph trim is... -> notes.md
- Follow-up: note: the live API fetch path fromApi request branch in named.mjs was not... -> notes.md
