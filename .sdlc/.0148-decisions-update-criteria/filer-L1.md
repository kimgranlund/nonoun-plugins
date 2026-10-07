<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0148: Add `steps.py widen` so conductor scope decisions rewrite the scope-guard criterion

## PR body
### Summary
A conductor decision to widen a step's scope used to reach the builder only as prose. The step's scope criterion, a `git diff --name-only "$SDLC_BASE_SHA"` allow-list, stayed unchanged. The next builder obeyed the old guard and blocked again.

This PR adds a script-checked route, `steps.py widen`. The conductor names only paths. The script rewrites the criterion, so "never edit the criterion by hand" and "whoever writes the work never sets its check" both still hold. The conductor and /chain contracts now document the route.

### Changes
- `plugins/sdlc-lite/scripts/steps.py`: new `widen <step dir> <path> [<path> ...] [--timeout SECONDS]` subcommand, modeled on `swap`.
  - It finds exactly one scope criterion. It recognizes three allow-list forms: `grep -vxF -e`, `grep -vxE "..."` and `grep -vE "^(...)$"`.
  - It ERE-escapes paths for the regex forms and skips paths already listed (`widen: already applied`).
  - It runs the rewritten span under `SDLC_BASE_SHA` before writing, and it refuses on a red span, a timeout or a span that changed the tree.
  - On success it replaces the criterion line and appends a `## Scope widened` section to the step handoff.
  - Every refusal writes nothing, exits 1 and ends with `plan defect: steps widen refused: ...; replan this step (/chain 4.2)`.
  - It adds an argparse subparser and 25 `widen:` selftest cases.
  - `main` now uses `parse_known_args` so a path like `-x` gets widen's refusal instead of a usage error. Only `widen` accepts the leftover arguments.
- `docs/references/sdlc-internals.md`: documents the subcommand.
- `skills/chain/SKILL.md`: new item 9, "Scope widening". Item 2 (builder blocked) names it as its one exception.
  - On exit 0, log `scope widened:` in `## Plan review` and rerun the builder at the same level. That rerun is not a bump and gets no `## Previous attempt`.
  - On exit 1, log `scope decision:` plus the stderr and take the 4.2 replan path.
- `agents/conductor.md`: the escalation bullet carries the route.
- `skills/handoff-format/SKILL.md`: documents the `scope widened:` and `scope decision:` entries in `## Plan review`, and the step handoff's `## Scope widened` section.
- `skills/level-rubric/SKILL.md`: a block resolved by `steps.py widen` never counts toward a bump.
- `agents/planner.md`: rule 9 now reads a `scope decision:` entry at replan time. Plan-time scope-guard rules are unchanged.
- `scripts/check.py`: new `PLAN_DEFECT_DOCS` entry for `'steps.py widen'`.
- `adapters/codex/agents/sdlc-conductor-l1.toml` and `sdlc-planner-l1/l2/l3.toml`: regenerated with `codex_roles.py generate`, not hand-edited.

### How each was verified
Step 1 (verifier L2, pass):
- Throwaway-repo checks:
  - F form: the widened `b.txt` passes the new span and `c.txt` fails it.
  - E form: the path is escaped, so `b.txt` passes and the lookalike `bxtxt` fails.
  - A step with no scope criterion refuses with exit 1, a `plan defect:` last line and an unchanged handoff.
- The verifier also ran the A forms, a rerun, two scope lines, and the bad paths `../x`, `/x`, `-x`, `a/../b` and `a b`.
- `steps.py selftest` passes and prints 21 `ok: widen:` lines.
- The `widen <step dir>` text is present in `steps.py` and `sdlc-internals.md`.
- The scope guard against `SDLC_BASE_SHA` exited 0.
- Builder negative control: a copy of `steps.py` with ERE escaping turned off made the selftest fail, on the E-form and A-form `(a)` cases only.

Step 2 (verifier L1, pass):
- The `steps.py widen` and `scope decision:` greps pass on the target docs and on `check.py`. Where checked at HEAD, they were red before the change.
- `codex_roles.py generate --check` passes.
- `check.py` reports "ok: 18 role levels, 8 agents checked".

Step 3 (verifier L1, pass):
- `check.py plugins/sdlc-lite`, `check-packaging.py` and `git diff --check` all pass.
- `check.sh` passes, with shellcheck skipped because it is not installed on this host. The verifier saw one unexplained non-zero exit (see Follow-ups).

### Not verified
- No live conductor run. Deciding to widen in an unattended lane is documented only, and the plan excluded a throwaway-project live run.
- The verifier did not run the red-span branch on its own. Its own test hit the lint refusal, and the branch is covered by selftest case `widen: (c) a red new span`.
- The verifier did not run the scope guard red.

### Known limits
- `widen` recognizes only three allow-list forms. A scope criterion written as an exact `test "$(git diff ...)" = "<file>"` or a prefix `grep -v '^path$'` refuses and falls back to a planner L3 replan with a `scope decision:` entry. Changing how planners write scope guards is a non-goal.
- `steps.py next` still prints `replan` for a blocked result until the rerun builder runs. The chain and conductor docs say the widen route overrides that one `replan`.
- If a blocked builder already edited files outside even the widened set, `widen` refuses and the step goes to a replan.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `steps.py widen`, a script-checked route by which a conductor scope-widening decision rewrites the step's scope-guard criterion. The route is documented in the /chain and conductor contracts, `handoff-format` and `level-rubric`, and `planner.md` rule 9 reads its `scope decision:` fallback at replan time.

## Follow-ups
- decide: `steps.py widen` refuses the exact `test "$(git diff ...)" = "<file>"` and prefix `grep -v '^path$'` scope-guard forms that past plans used, so those steps take the slower L3 replan. Decide whether to add those forms or standardize the planner's guard form.
- note: The step-3 verifier saw one unexplained non-zero `check.sh` exit that did not reproduce, and no log was saved. If it recurs, capture the log and check whether it depends on concurrent runner activity.
- note: The live conductor behavior for widening in an unattended lane is untested, and no throwaway-project live run was done. AGENTS.md asks for live evidence when changed host behavior is claimed.
