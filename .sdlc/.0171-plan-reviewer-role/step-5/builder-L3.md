<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- docs/validation/plan-reviewer-live-run.md: new dated live-run report. It covers environment, projects, method with exact commands, which runs ran, a Results table, Limits, and the "No benefit is claimed" sentence.
- docs/validation/plan-reviewer-live-run/claude/probe-defective/: copied evidence (handoff.md, planner-L3.md, plan-reviewer-L1.md, plan-reviewer-L1.attempt.json, runs.jsonl).
- docs/validation/plan-reviewer-live-run/claude/probe/: copied evidence (handoff.md, planner-L3.md, planner-L3.attempt.json, plan-reviewer-L1.md, plan-reviewer-L1.attempt.json, runs.jsonl, and step-1/ with base-sha, handoff.md, builder-L1.md, verifier-L1.md, both attempt.json files, runs.jsonl; no .log files).
- docs/validation/plan-reviewer-live-run/codex/probe-defective/: copied evidence (handoff.md, planner-L3.md, plan-reviewer-L1.md, plan-reviewer-L1.attempt.json, runs.jsonl).
- docs/README.md: one list entry for the new report.

## Checks
- `steps.py review .sdlc/probe-defective` (Claude, before review): `review L1`.
- `W plan-reviewer L1 .sdlc/probe-defective/handoff.md` (Claude): exit 0, Verdict `replan` with 5 findings. Header `model=opus effort=high`.
- `steps.py review .sdlc/probe-defective` (after): `replan`. `steps.py split .sdlc/probe-defective`: exit 1, stderr contains `plan defect: plan review: replan`.
- `W planner L3 .sdlc/probe/handoff.md`: exit 0, one step at L1. `steps.py review`: `review L1`.
- `W plan-reviewer L1 .sdlc/probe/handoff.md`: Verdict `pass`. `steps.py review`: `split`. `steps.py split`: exit 0.
- `W builder L1 .sdlc/probe/step-1/handoff.md`: Status `done`. `steps.py next`: `verify L1`.
- `W verifier L1 .sdlc/probe/step-1/handoff.md`: Verdict `pass`. `steps.py next`: `done`.
- `SDLC_DRY_RUN=1 W plan-reviewer L1` with an `opus` planner-L2 header: `--model fable --effort high`. Negative control with a `sonnet` header: `--model opus --effort high`. The first dry-run attempt failed with `git repo has no commit` until the fixture got one commit.
- Codex: `codex login status`: `Logged in using ChatGPT`. `codex_roles.py install .`: 24 agents. `codex_roles.py resolve plan-reviewer L1 .sdlc/probe-defective`: `gpt-6.1-sol high`.
- `SDLC_BACKEND=codex W plan-reviewer L1 .sdlc/probe-defective/handoff.md`: exit 0, Verdict `replan`, header `model=gpt-6.1-sol effort=high`, attempt record `transport: exec`. After it, review printed `replan` and split was refused with exit 1.
- All 10 acceptance criteria, including the (guard), run from the repo root: all PASS.
- `git diff --check`: exit 0. Local link targets exist. No em dashes in the new doc or README.

## Notes
- The probe dir came from `mktemp -d` (`/var/folders/.../plan-review-probe.3WrEjPYrWb`) and was removed at the end. No git worktree was created.
- The sound plan passed on the first review, so the /chain 3 replan loop did not run live. The Limits section says so.
- The Codex result has a blank line after `## Verdict`. The criterion's awk skips blank lines, so it still reads `replan`.
- The Codex `runs.jsonl` records `"transport":"codex"`. The attempt record is what shows `exec`, and the doc says this.
- Six model calls ran as the step budgeted: 2 Claude reviewers, planner L3, builder L1, verifier L1, and 1 Codex reviewer. None was retried.
