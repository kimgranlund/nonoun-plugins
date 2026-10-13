<!-- role=builder level=L3 model=opus effort=medium -->
## Status
blocked

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/plugins/sdlc-lite/scripts/check.py`: docstring item 60 `Argument hints (T-0463)`; `hint_parses`, `usage_block`, `hints_bad(skills, usage)`, the script map, the allowlist, the call on the real tree, and the H-1 to H-7 controls before the final `for e in errors` loop.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/docs/specs/doc-standards/prompts.md`: new section `## Skill arguments and questions` (hint syntax and grammar, the `## Arguments` table shape, H-1 to H-7, the seven question rules, Codex display unverified).
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/docs/specs/doc-standards/README.md`: `| Skill |` row Check cell now `prompt_lint P-2, P-3, P-6; check.py argument hints (H-1 to H-7)`.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/plugins/sdlc-lite/AGENTS.md`: one skill-authoring bullet under `## Contracts and routing`.

## Checks
- `python3 .../scripts/redck.py record .sdlc/0463-skill-ui-hints/step-1/handoff.md`, run before the first edit: exit 0, 5 controls recorded red.
- `python3 plugins/sdlc-lite/scripts/check.py` at base, before editing: one line, `ok: 19 role levels, 9 agents, 22 generated definitions checked`.
- Criterion 1 (red), `check.py | grep -qF 'check.py: argument hints: '`: pass.
- Criterion 2, the six expected findings (agent H-2, build H-2, ticket H-3, report H-4, fleet-retro H-5, board H-6): pass.
- Criterion 3 (guard), `! python3 plugins/sdlc-lite/scripts/check.py | grep '^FAIL' | grep -qvF 'check.py: argument hints: '`: FAIL, exit 1 under both `bash -c` and `sh -c`. The one non-hint line is `FAIL: 19 role levels, 9 agents, 22 generated definitions checked`.
- Criterion 4 (red), the seven `argument hints negative control not flagged for H-<n>` literals in `check.py`: pass.
- Criterion 5 (guard), no stub or reference skill flagged: pass.
- Criterion 6 (red), `grep -qF '## Skill arguments and questions' docs/specs/doc-standards/prompts.md`: pass.
- Criterion 7 (red), `grep -qF 'argument-hint' plugins/sdlc-lite/AGENTS.md`: pass.
- Criterion 8 (red), `grep -E '^\| Skill \|' docs/specs/doc-standards/README.md | grep -qF 'check.py'`: pass.
- Criterion 9, docstring item 60 names H-1 to H-7 and their controls, and each control is a `hints_bad` mutant at module level: holds by my reading of the diff, and no control line fires in the `check.py` output.
- Criterion 10 (guard), `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`: exit 0, 0 errors, 30 warnings, none on the files this step changed.
- Criterion 11 (guard), the scope check against `$SDLC_BASE_SHA`: pass.
- `git diff --check`: clean.

## Notes
plan defect: criterion 3 `(guard) ! python3 plugins/sdlc-lite/scripts/check.py | grep '^FAIL' | grep -qvF 'check.py: argument hints: '` contradicts criteria 1 and 2. Whenever `check.py` is red its last line is the summary `FAIL: N role levels, ...`, which starts with `FAIL` and is not an argument-hints line, and criteria 1 and 2 require `check.py` red in this step.

- **Fix for the planner:** use `grep '^FAIL '` with a trailing space. Finding lines are `FAIL check.py: ...` and the summary is `FAIL: ...`, so that variant excludes only the summary. I ran it on this tree and it passes: the summary is the only non-hint `FAIL` line, and no control misfired.
- **Not an inherited red:** the guard is green at base because `check.py` prints only `ok: ...` there.
- **Work is in the tree:** all four targets are complete and uncommitted, and every other criterion passes. I did not change the summary `print` line to get around the grep.
- **zsh false pass:** my first combined run wrapped criterion 3 as `( ! ... ); echo $?` under zsh and printed 0. The as-written command under `bash` and `sh` exits 1, and that is the result to trust.
- **Still red for step 2:** `check.py` reports 78 argument-hint findings. The H-5 flags left off the allowlist because the handoff does not list them are:
  - `ticket`: `--keep-refs`
  - `board`: `--summary`, `--task`, `--waiting`
  - `fanout`: `--dry-run`, `--root`
  - `onboard`: `--dry-run`
  - `fleet-retro`: `--days`, `--du-timeout`, `--since`, `--until`
  - `review-traces`: `--out`, `--bench-dir`, `--load-series`, `--rerun-criteria`
- **`review-traces` allowlist reading:** I allowlisted `--repo`, `--backend`, `--codex-home`, the flags only `detect`, `clusters` and `context` take. `--out` also sits on the `ingest` line, so I left it red.
- **Controls on a red tree:** every non-stub reader already fails H-6, so the handoff-based controls mutate a clean reader built in memory from the real `handoff` skill (hint set, table appended). The `report` controls filter on a flag no real skill holds. I added positive controls beyond the five must-parse hints: the clean reader, a 100-character hint, and a usage flag carried by the table under `[options]`. There is also a third H-6 mutant, a wrong header row.
- **H-6 "followed by":** implemented as the next non-blank line after the heading equals the header row exactly. The docstring and `prompts.md` both say so.
