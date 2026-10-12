## Status
done

## Changes
- `packages/agent-ui/a2ui/src/agent/response-type.ts`: dropped `render` and `in words`. `show me`, `build a` and `make me a` now count as surface overrides only when one of the 16 surface nouns follows within four words. `as a card`, `as a table` and `as a chart` are unchanged.
- `packages/agent-ui/a2ui/src/agent/response-type.test.ts`: updated the changed phrases and added `describe("lexicon false positives")` with the seven false-positive phrases and the must-still-match phrases.
- `.claude/docs/spec/response-type-selection.spec.md`: RTS-R6 lexicon text updated, AC2b added, status line bumped to v0.3.

## Checks
- **Red criteria 1–3:** all three were red before the edits. The red checkpoint recorded 3 controls before the first edit. After the edits all three exit 0.
- **Guard, vitest:** `response-type.test.ts` + `layering.test.ts` + `produce-response-type.test.ts` passed, 92 tests. The agent-eval tests passed, 29 tests.
- **Guard, doc_lint:** exit 0.
- **Guard, scope:** exit 0.
- `npx tsc -p tsconfig.json`: exit 0.

## Notes
- I adjusted two existing test cases: `make me a quiz` became `make me a survey`, because `quiz` is not in the surface noun list. I removed `Render it` and `say it in words` from the old positive lists.
- Surface nouns match exactly as listed, so `forms` or `cards` do not match.
- I did not run `doc_lint` or the scope guard at the base sha. Both were green after the edits, so no base comparison was needed.
