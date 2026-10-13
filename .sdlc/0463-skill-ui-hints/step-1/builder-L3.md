<!-- role=builder level=L3 model=opus effort=medium -->
## Status
done

## Changes
This attempt made no edits: every criterion was green on the resumed tree. The step's changes, all uncommitted from the first attempt, are:
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/plugins/sdlc-lite/scripts/check.py`: docstring item 60 `Argument hints (T-0463)`, `hint_parses`, `usage_block`, `hints_bad(skills, usage)`, the script map, the allowlist, the call on the real tree, and the H-1 to H-7 controls before the final `for e in errors` loop.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/docs/specs/doc-standards/prompts.md`: new section `## Skill arguments and questions`.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/docs/specs/doc-standards/README.md`: `| Skill |` row Check cell gains `check.py argument hints (H-1 to H-7)`.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/plugins/sdlc-lite/AGENTS.md`: one skill-authoring bullet under `## Contracts and routing`.

## Checks
- Criterion 1, `python3 plugins/sdlc-lite/scripts/check.py | grep -qF 'check.py: argument hints: '`: exit 0. `check.py` itself exits 1 with 78 argument-hint findings, as the step intends.
- Criterion 2, the six expected findings (agent H-2, build H-2, ticket H-3, report H-4, fleet-retro H-5, board H-6): exit 0.
- Criterion 3 (guard), `! python3 plugins/sdlc-lite/scripts/check.py | grep '^FAIL ' | grep -qvF 'check.py: argument hints: '`, run under `bash -c`: exit 0. The only non-hint line is the summary `FAIL: 19 role levels, 9 agents, 22 generated definitions checked`.
- Criterion 4, the seven `argument hints negative control not flagged for H-<n>` literals in `check.py`: exit 0.
- Criterion 5 (guard), no stub or reference skill flagged, run under `bash -c`: exit 0.
- Criterion 6, `grep -qF '## Skill arguments and questions' docs/specs/doc-standards/prompts.md`: exit 0.
- Criterion 7, `grep -qF 'argument-hint' plugins/sdlc-lite/AGENTS.md`: exit 0.
- Criterion 8, `grep -E '^\| Skill \|' docs/specs/doc-standards/README.md | grep -qF 'check.py'`: exit 0.
- Criterion 9, read from `git diff $SDLC_BASE_SHA -- plugins/sdlc-lite/scripts/check.py`: item 60 names H-1 to H-7 and each negative control, and every control is a `hints_bad` mutant run at module level. The `check.py` output holds zero `negative control` or `positive control` lines.
- Criterion 10 (guard), `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`: exit 0, 0 errors, 30 warnings. I read only the last lines of its output, so I did not confirm that none of the warnings sit on the changed files.
- Criterion 11 (guard), the scope check against `$SDLC_BASE_SHA`: exit 0. No file under `plugins/sdlc-lite/skills/` is modified.
- `git diff --check`: clean.

## Notes
- No `redck.py record` was run this attempt, because the handoff carries no `(red)` tag. The pre-edit record for this work is `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/.sdlc/0463-skill-ui-hints/step-1.superseded-1/red-checkpoint.jsonl`.
- `check.py` is red by design with 78 argument-hint findings for step 2 to clear. `check.sh` was not run, per the handoff.
- Run the negated guards (criteria 3 and 5) under `bash` or `sh`. The first attempt saw a false pass on criterion 3 when it was wrapped as `( ! ... ); echo $?` under zsh.
- H-5 flags the first attempt left off the allowlist, carried from its result for step 2 to settle:
  - `ticket`: `--keep-refs`
  - `board`: `--summary`, `--task`, `--waiting`
  - `fanout`: `--dry-run`, `--root`
  - `onboard`: `--dry-run`
  - `fleet-retro`: `--days`, `--du-timeout`, `--since`, `--until`
  - `review-traces`: `--out`, `--bench-dir`, `--load-series`, `--rerun-criteria`
- The `review-traces` allowlist holds only `--repo`, `--backend`, `--codex-home`, the flags that only `detect`, `clusters` and `context` take. `--out` is also on the `ingest` line, so it stays red.
- The `ticket` allowlist entry still includes `--apply` and `--scope`, as the handoff says to leave it. Step 2 moves those two to the `ticket` table.
- Controls beyond the handoff's list, kept from the first attempt: positive controls for a clean reader, a 100-character hint, and a usage flag carried by the table under `[options]`, plus a third H-6 mutant with a wrong header row.
