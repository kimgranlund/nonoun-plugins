<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Chain SKILL.md holds `## Lean chain`, `always runs the filer` and `Coarse steps`: pass. Evidence: the grep chain exited 0. The diff shows the new section inserted before `## 1. Brief`.
- planner.md holds `## Coarse steps`, `independently verifiable outcome` and `steps lint: warning:`: pass. Evidence: the grep chain exited 0. The diff shows the section placed before `## Criteria that can pass`.
- The l2 planner TOML holds `independently verifiable outcome`: pass. Evidence: grep exited 0. The TOML is in the diff (`sdlc-planner-l2.toml`, 1 line changed), so the phrase was absent at base.
- check.py rejects a planner.md with the phrase removed: pass. Evidence: the command exited 0, meaning `check.py` failed on the copy. The output was `FAIL agents/planner.md: lean lane text missing "independently verifiable outcome"`. It failed for the intended reason.
- check.py rejects a chain SKILL.md with `## Lean chain` removed: pass. Evidence: the command exited 0. The output was `FAIL skills/chain/SKILL.md: lean lane text missing "## Lean chain"`.
- (guard) no em dash in the listed files: pass. Evidence: exit 0.
- (guard) only allowed files changed: pass. Evidence: exit 0. The changed files are `planner.md`, `chain/SKILL.md`, `check.py` and three planner TOMLs, all in the allowlist.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0, ending `ok: plugin validate`. `shellcheck` is not installed, so that step was skipped.
- (guard) `python3 scripts/check-packaging.py`: pass. Evidence: `PASS: catalog parity, identity, skill routes, hook isolation and context links`.
- (guard) `codex_roles.py generate --check`: pass. Evidence: `Codex agent definitions verified`.
- (guard) `tickets.py --root .sdlc check`: pass. Evidence: `ok: 208 tickets, roadmap current`.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: pass. Evidence: exit 0.

Steelman: I looked for a reason to fail the guard criteria and found none. All gates were green on the built tree, so no pre-build run was needed. `steps.py` already holds `steps lint: warning:` (6 matches), so the new check.py pair for that file passes for real, not vacuously.

## Out of scope changes
None. The diff touches only `planner.md`, `chain/SKILL.md`, `check.py` and the three regenerated planner TOMLs. `steps.py` was not touched.

## For the next attempt
None
