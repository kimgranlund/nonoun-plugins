<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/plugins/sdlc-lite/scripts/docs_check.py: added rules S-1 to S-7, all at error level, in a new `standards_rules()` and `_registry()`, with helpers `_body`, `_links`, `_resolve` and `_cells`. `on()` now accepts the `standards` group (S-*). Updated the `--only` help text and the docstring, which names `docs/specs/doc-standards/README.md` as the rules' home. Added 10 `_cases()` entries covering S-1 to S-7.

## Checks
- `python3 -B -c "...ids={c[0] for c in docs_check._cases()}..."` (red 1): exit 0.
- `python3 -B -c "...docs_check.run(d, only={'standards'})...== ['S-5']"` (red 2): exit 0.
- `python3 plugins/sdlc-lite/scripts/docs_check.py selftest` (guard): PASS. All four gates report positive ok and negative ok, including a `drops S-1` to `drops S-7` control for each new rule.
- `python3 plugins/sdlc-lite/scripts/docs_check.py --root .` (guard): exit 0 with 0 errors and 24 warnings, all from existing D-10, D-11, B-2a and B-3a. No S finding on this tree.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0, so the `DOCS_CHECK_NEEDS` pins are intact.
- Scope guard (`git diff --name-only $SDLC_BASE_SHA ... | grep -vxE ...`, with `SDLC_BASE_SHA=ad35eaaa`): exit 0.
- `git diff --check -- plugins/sdlc-lite/scripts/docs_check.py`: exit 0. A grep found no em or en dash in the file.
- An extra probe on a temp fixture got the expected results:
  - Not flagged: upper-case MUST, a modal word inside a code span or a fence, an ID line followed by `Acceptance:`, a numbered runbook step, and a report link or code span that resolves from the root or the report folder.
  - Flagged: an `Acceptance:` that only appears after a heading, a mixed-case `May`, a missing code-span path, broken card and assets links, a bad Enforcement value, and a card the registry does not link.

## Notes
- The red checkpoint was recorded as retrospective, not as a pre-edit record. `redck.py record` ran before any edit of mine, but the tree already held step-1 changes from another builder (8 dirty paths: check.py, check.sh, prompt_lint.py, AGENTS.md, architect files). `docs_check.py` was still unchanged at that point. Both red commands exited 1 there, as recorded in `.sdlc/0447-doc-standards-suite/step-2/red-checkpoint.jsonl`.
- `SDLC_BASE_SHA` was empty in the shell. The scope guard ran with the base sha from the brief, `ad35eaaa04e635875c9db778c0a741ee5319421b`.
- Decisions the spec left open, which step 3 should know:
  - S-2 matches `shall` in any case, and allows leading spaces before the optional `- ` and the ID.
  - S-3 counts `## Decision` lines only outside fences.
  - S-5 skips a code span of any backtick length.
  - S-6 skips code spans that start with `/` or `~`.
  - S-1 reports an S-1 error on the schema file if `kpi.json` is not a JSON object.
  - S-7 checks a header that starts with `Type` against the full contract header, strips backticks from Enforcement and Check cells, and reports an unlinked card on the card's own path. Other S-7 findings go on the registry path.
- The S rules are not Legacy-exempt.
