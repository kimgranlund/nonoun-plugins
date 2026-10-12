<!-- role=solo level=L2 model=sonnet effort=high -->
## Output
T-0492 meets its done criterion, and every named check exits 0. I wrote no `(red)` control, because the ticket has none. I did not run `check.sh` or the other suites.

**Changed files**
- `plugins/sdlc-lite/agents/conductor.md`: a `## Merge ops` block of 7 lines. The old "then run the lane sweep" now points at it. I reworded "Do not narrate every background wake-up" to an affirmative line so the prohibition count stays at 30.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: list item 4 now says to run `land` as a background Bash call and mentions `--priority 1`. Section `## 5. Main` now calls `fanout.py settle <integration> --forward --gate "<cmd>"...`, then `lanes.py sweep --apply`, and checks status with `board.py --lanes` and `lanes.py list --stale`.
- `plugins/sdlc-lite/skills/handoff-format/run-operations.md`: a new `## Merge ops` recipe with enqueue, dequeue, status, priority, release and the Never line.
- `plugins/sdlc-lite/scripts/check.py`: a new docstring item 56 and a merge-ops case. All three files must carry the conductor's settle command, plus the shared phrases. The case includes negative controls: each phrase removed from each file, and the settle command changed in each file.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`: regenerated. The Claude generate wrote nothing, since the conductor has no per-level definition.
- `.sdlc/0492-merge-ops-duty-block/handoff.md`: I appended `## Acceptance criteria`.

**Checks**, each run exactly as written:
- `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exit 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0
- `python3 plugins/sdlc-lite/scripts/prompt_lint.py` exit 0. `conductor.md` is at 30 prohibitions, the same as before the change.
- `git diff --check` exit 0

**Observed red:** with `settle <integration> --forward` replaced by `settle <integration>` in `run-operations.md`, `check.py` exited 1 with "run-operations.md settle command disagrees with the conductor". I restored the file and it went back to exit 0.

**Still open:**
- `fanout.py` still passes no `--priority 1` to `gate_lock.py`; the design doc files that as later build C. The block states it as policy only.
- I did not commit. The brief says `fanout.py` commits this lane.
- `solo-report` was not run, because I wrote no report file.

verify: needed. The ticket is L2, so the parent runs the one batched verifier at the level `steps.py verifier-level` prints. I did not start it, as `solo.md` says.
