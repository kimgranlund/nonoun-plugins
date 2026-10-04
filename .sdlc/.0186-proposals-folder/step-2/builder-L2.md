<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `.sdlc/proposals/CLAUDE.md`: new file, holds only `@AGENTS.md`.
- `.sdlc/proposals/AGENTS.md`: new self-contained entry file with the intro paragraph and the sections File format, Patterns, Statuses, Procedures and Limits.
- `.sdlc/AGENTS.md`: added the Proposals line to `## Other records`, after the Evals line and outside the managed block.
- `docs/maintenance/sdlc-internals.md`: new ``## `scripts/proposals.py` `` entry placed after the evals.py entry.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: added the `.sdlc/proposals/` layout line after the `.sdlc/evals/` line.
- `plugins/sdlc-lite/AGENTS.md`: added the Proposals verification line after the evals line.
- `docs/validation/proposals-live-run.md`: new live-run record with Environment, Commands, Evidence (all 8 arms, the list, and every proposal's text) and Limits.

## Checks
- `proposals.py selftest`: PASS, all 27 cases including the 7 negative controls.
- Live run arms, run from the repository root with candidates written to a temp dir:
  - Arm 2, scan: exit 0, 19 new (18 `replan`, plus one `plan-defect` with 12 evidence lines).
  - Arm 4, rescan: exit 0, `0 new, 0 updated, 19 unchanged`; `cmp` of the before and after hashes exit 0.
  - Arm 5, accept with no eval: exit 1, `no eval given`.
  - Arm 5, accept with an eval outside `.sdlc/evals/`: exit 1, `is not in`.
  - Arm 5, `cmp` of P-0001's file: exit 0, unchanged.
  - Arm 6: both the source and `plugins/` manifest `cmp` gave exit 0; `.sdlc/proposals` still holds only AGENTS.md and CLAUDE.md.
  - Arm 7, mutant scan: exit 0; `cmp` exit 1 with 1281 of 1601 source lines changed.
  - Arm 8, `rm -rf "$T"`: exit 0.
- Acceptance criteria 1 to 7: each exit 0.
- (guard) `tickets.py --root .sdlc check`: exit 0.
- (guard) `codex_roles.py generate --check`: exit 0.
- (guard) scope diff against `$SDLC_BASE_SHA` (66586153): exit 0.
- `git diff --check`: clean. No em dashes in the files I changed.

## Notes
- The first pass of arm 7 lost the mutant scan's exit code: the run was in zsh, where `${PIPESTATUS[0]}` is empty. I reran arm 7 alone in a fresh temp dir, with output redirected to a file. It gave exit 0 and the same results: `cmp` exit 1, 1281 changed lines. The doc says this in the arm 7 row.
- In the doc, the 18 `replan` show outputs were rebuilt by a script from the captured run output; P-0019 is pasted verbatim.
- The ids P-0001 to P-0019 exist only in the deleted temp dir. Nothing was promoted and no ticket was filed.
