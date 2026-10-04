## Task goal
Add the free half of the spec gate: `scripts/specgate.py check`, the `run.sh` plan-reviewer refusal, and a plan-level `guard timeout:` line that `steps.py split --only` honors.

## Step 2: Guidance, check.py guard, regenerated agents, gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1.

1. `plugins/sdlc-lite/agents/planner.md`: add one sub-bullet under rule 14 (`## Criteria that can pass`, the gates green rule). This is not the intro paragraph that T-0202 edits (`git diff main...t0202 -- plugins/sdlc-lite/agents/planner.md` touches only line 11), so no wait is needed. Text: "A `(guard)` that runs `check.sh` (or another whole suite) needs a `guard timeout: <seconds>` line: time the command once at plan time and write about three times that, on its own line in `## Goal` for the whole plan or right after a step's `level:` line for that step, because `steps.py split --only` runs guards under that timeout (default 300) and `specgate.py check` refuses the plan without it."
2. `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: one line in `## Step handoff`, right after the paragraph that starts "`scripts/steps.py split` writes these files". Text: "A plan may hold a `guard timeout: <seconds>` line (in `## Goal` for the whole plan, or right after a step's `level:` line for that step); `steps.py split --only` uses it as the `--guard-timeout` default, an explicit `--guard-timeout` wins, and `specgate.py check` refuses a `(guard)` that runs `check.sh` without one."
3. `plugins/sdlc-lite/skills/chain/SKILL.md`: append to the `review L1` bullet in /chain 3 (chain/SKILL.md:47). Text: "If that run exits 2 with `specgate:` lines on stderr, `specgate.py check` refused the plan before any model call: append those lines under `## Plan review` and replan as for a `steps.py split` `plan defect` (below)." Without this, an exit 2 leaves no result, `steps.py review` prints `review L1` again, and the chain loops.
4. `plugins/sdlc-lite/agents/conductor.md`: one pointer clause at the end of the plan-review bullet (conductor.md:27), allowed now that T-0199 (cb18cdd) is on this branch. Text: "A `run.sh plan-reviewer` exit 2 with `specgate:` lines is a `specgate.py check` refusal; /chain 3 routes it as a plan defect." Do not restate anything else.
5. `plugins/sdlc-lite/scripts/check.py`: add docstring item 16, "Spec gate", and a guard in the style of the lean-lane guard (check.py:390-401).
   - Phrase `guard timeout:` must appear in `agents/planner.md`, `skills/handoff-format/SKILL.md`, `scripts/steps.py` and `scripts/specgate.py`.
   - Phrase `specgate.py check` must appear in `scripts/run.sh`, `skills/chain/SKILL.md` and `agents/conductor.md`.
   - A missing phrase prints `FAIL <rel>: spec gate text missing "<phrase>"`.
   - The order check fails with `FAIL scripts/run.sh: specgate.py check does not come before exec run_lifecycle.py` unless the first `specgate.py check` line of run.sh sits before the line that holds `exec python3 "$plugin_root/scripts/run_lifecycle.py"`.
   - Each check has a negative control (phrase removed, lines swapped) that appends `check.py: spec gate ... negative control not flagged` when it does not fire.
6. `docs/maintenance/sdlc-internals.md`:
   - Add a `scripts/specgate.py` entry: what `check` flags, exit 0/1, skip on no plan, findings on stderr, imports steps, the `run.sh` gate with exit 2 and `SDLC_SPECGATE=off`.
   - In the `scripts/steps.py` entry, add that `--guard-timeout` defaults to the step's, then the plan's, `guard timeout:` line, else 300.
7. `docs/lean-sdlc/cost-control.md` line 3: replace "Nothing here is built." with "A1 (T-0210) is built; nothing else here is." This keeps the record from going stale.
8. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. It rewrites `plugins/sdlc-lite/adapters/codex/agents/*.toml` from the agent and skill bodies. Never edit TOML by hand.
9. Run every gate: `bash plugins/sdlc-lite/scripts/check.sh` (273 s at plan time, so this plan carries `guard timeout: 900`), `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, and `git diff --check`.
   - Fix any red step 1 or this step introduced, inside the files these steps changed.
   - A gate red at the build-start HEAD is `inherited red`.
   - All four gates were green at plan time.
   - Add no em dash. No version bump, tag, push or publish.
### Acceptance criteria
- `grep -qF "guard timeout:" plugins/sdlc-lite/agents/planner.md && grep -qF "specgate.py check" plugins/sdlc-lite/agents/planner.md`
- `grep -qF "guard timeout:" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF "specgate.py check" plugins/sdlc-lite/skills/chain/SKILL.md && grep -qF "specgate.py check" plugins/sdlc-lite/agents/conductor.md`
- `grep -qF "scripts/specgate.py" docs/maintenance/sdlc-internals.md && grep -qF "guard timeout:" docs/maintenance/sdlc-internals.md`
- `grep -qF "A1 (T-0210) is built" docs/lean-sdlc/cost-control.md`
- `grep -qF "guard timeout:" plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l2.toml`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && python3 -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); f=p/\"agents/planner.md\"; f.write_text(f.read_text().replace(\"guard timeout:\", \"x\")); g=p/\"scripts/run.sh\"; g.write_text(g.read_text().replace(\"specgate.py check\", \"x\"))" "$t/p" && out=$(python3 "$t/p/scripts/check.py" "$t/p" 2>&1); printf "%s\n" "$out" | grep -qF "FAIL agents/planner.md: spec gate text missing \"guard timeout:\"" && printf "%s\n" "$out" | grep -qF "FAIL scripts/run.sh: spec gate text missing \"specgate.py check\""`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/check.py -e plugins/sdlc-lite/agents/planner.md -e plugins/sdlc-lite/agents/conductor.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/skills/chain/SKILL.md -e docs/maintenance/sdlc-internals.md -e docs/lean-sdlc/cost-control.md | grep -vE "^plugins/sdlc-lite/adapters/codex/")" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/specgate.py)"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
