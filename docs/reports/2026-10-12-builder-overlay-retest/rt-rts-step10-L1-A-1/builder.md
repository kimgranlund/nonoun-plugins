## Status
done

## Changes
- `packages/agent-ui/a2ui/src/agent/response-type.ts`: dropped `render` and `in words`. `show me`, `build a` and `make me a` now count as surface overrides only when a surface noun follows within four words (`VERB_NOUN_RE`). `as a card`, `as a table`, `as a chart` and the other text phrases are kept. The whole-word boundary and the text-wins-a-tie rule are unchanged.
- `packages/agent-ui/a2ui/src/agent/response-type.test.ts`: updated the phrase lists (removed `in words` and `Render it`; `make me a quiz` became `make me a survey`). Added `describe("lexicon false positives")` with the seven no-override phrases, four must-still-surface phrases and two must-still-text phrases.
- `.claude/docs/spec/response-type-selection.spec.md`: status line is now v0.3. RTS-R6 now states the new lexicon, and I added AC4 for the false-positive cases.

## Checks
- Red node one-liner: exit 0. I ran `redck.py record` before editing, and it recorded all 3 red criteria as red at base.
- Red `-t "lexicon false positives"` vitest plus grep: exit 0.
- Red python check for `'render'` and `'in words'`: exit 0.
- Guard vitest (`response-type.test.ts`, `layering.test.ts`, `produce-response-type.test.ts`): 3 files, 90 tests passed.
- Guard vitest `--project tools` on agent-eval: 4 files, 29 tests passed.
- `doc_lint` on the SPEC: exit 0. It printed "not a functional document" and linted nothing.
- `npx tsc -p tsconfig.json`: exit 0.
- Scope guard: no out-of-scope files. The loop printed nothing and ran with `SDLC_BASE_SHA` set manually.

## Notes
None
