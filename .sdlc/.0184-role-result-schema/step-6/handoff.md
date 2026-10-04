## Task goal
Every role result file is validated against one declared schema before the pipeline advances, and a malformed result is refused so the pipeline does not move.

## Step 6: Live run proving a malformed builder result does not advance
level: L3
### Do
Depends on: steps 2 and 3.

Run a real Claude `run.sh builder L1` in a throwaway project and record the evidence in `docs/validation/role-result-schema-live-run.md`, following the shape of `docs/validation/plan-reviewer-live-run.md`. No em dashes.

Setup:
- Use a throwaway project made with `mktemp -d`: `git init`, one commit, and `.sdlc/t/step-1/handoff.md`. Never use this repository's `.sdlc`.
- Run `bash <abs path>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/t/step-1/handoff.md` from that project root.

Arms:
1. Malformed: the handoff tells the builder to make a trivial change and end its final message with only a `## Changes` section, with no `## Status`. Expect `run.sh` exit 3 with a `run.sh: builder result lacks ## Status ...` stderr line. Then `python3 <abs>/plugins/sdlc-lite/scripts/steps.py next .sdlc/t/step-1` must print `rebuild L1`, not `verify`, so the pipeline does not advance.
2. Structural: copy that run's saved `builder-L1.md` with its header line removed into a second step dir that has its own handoff and runs.jsonl line. `steps.py next` must print `invalid result: ...`.
3. Normal: a fresh step dir with a handoff that asks for the normal output. Expect exit 0, and `steps.py next` prints `verify L1`.

If the model ignores the malformed instruction, rerun once with a stronger instruction. If it still emits Status, record that arm as unverified, never as a fixture.

The doc has these sections, each containing the exact strings named:
- `## Environment`: date `2026-10-..`, host OS, `claude --version`, and the repo commit.
- `## Commands`: the exact commands, including the literal `run.sh builder L1`.
- `## Evidence`: per arm, the exit code, written as `exit 3` or `exit 0`, the stderr line, and the `steps.py next` first line (`rebuild L1`, `invalid result`, `verify L1`).
- `## Limits`: the Codex backend arm is unverified unless run, and it is one model at one level.
### Acceptance criteria
- `f=docs/validation/role-result-schema-live-run.md && for s in "## Environment" "## Commands" "## Evidence" "## Limits" "run.sh builder L1" "exit 3" "exit 0" "rebuild L1" "verify L1" "invalid result"; do grep -qF "$s" "$f" || exit 1; done`
- `grep -qE "2026-[0-9]{2}-[0-9]{2}" docs/validation/role-result-schema-live-run.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/fanout.py -e plugins/sdlc-lite/scripts/traces/selftest.py -e plugins/sdlc-lite/skills/chain/SKILL.md -e plugins/sdlc-lite/skills/fix/SKILL.md -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/AGENTS.md -e docs/validation/role-result-schema-live-run.md | { ! grep -q .; }`
