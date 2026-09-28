<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
When a builder finds a gate that is already red at the pre-build HEAD, it reports Status `inherited red: <tests>`. `steps.py next` prints `inherited` for it, `run.sh` accepts it, `board.py` renders it as 🔴 inherited red, and the builder, chain, conductor and repo docs name that status and its routing, with a check.py guard on them.

## Step 1: steps.py next maps an inherited red builder to `inherited`
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py`:
- Teach the builder Status parser to accept a third value. A first non-blank line under `## Status` that starts with `inherited red:` (case-insensitive) is the status `inherited`. `done` and `blocked` parse exactly as before. A bare `inherited red` with no colon stays statusless, which keeps the current `rebuild` / `stop` handling.
- `build_status_or_none` returns `inherited` for such a line, so it breaks a run of statusless builders like any real status does.
- In `next_action`, add a check right after the statusless branch and before the `blocked` check: when the newest builder's status is `inherited`, return `('inherited', None, '<name> reports inherited red (gate already red at the pre-build HEAD); ask the conductor, not a fail, rebuild, bump, or replan', read)`.
  - An older inherited builder followed by a `done` builder follows the normal path (verify).
  - An inherited builder is never a counted fail and never a bump.
- Update the module docstring's `next` rules. Add the line `newest builder Status inherited red: <tests> -> inherited` and say it is never counted as a fail, a bump, a rebuild, or a replan.
- Add selftest cases whose names start with `next inherited:`:
  - (a) newest builder `## Status\ninherited red: test_a` → `inherited`.
  - (b) inherited builder then a `done` builder → `verify L1`.
  - (c) a `done` builder, a verifier FAIL, then an inherited builder → `inherited`, not `rebuild` or `bump`.
  - (d) `## Status\ninherited red` with no colon → `rebuild L2`.
### Acceptance criteria
- `d=$(mktemp -d) && printf '## Status\ninherited red: test_a\n' > "$d/builder-L2.md" && out=$(python3 plugins/sdlc-lite/scripts/steps.py next "$d") && test "$(printf '%s\n' "$out" | head -1)" = inherited` (run from the repo root; the `&&` chain also requires exit 0)
- `grep -q "next inherited: " plugins/sdlc-lite/scripts/steps.py`
- `grep -q 'inherited red:' plugins/sdlc-lite/scripts/steps.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`

## Step 2: run.sh accepts an inherited red builder Status
level: L1
### Do
- In `plugins/sdlc-lite/scripts/run.sh`, change the builder case to `allowed='done|blocked|inherited red: .+'`. The existing `^($allowed)$` match on the lowercased value then accepts `inherited red: <tests>`. It still rejects `maybe`, and it rejects a bare `inherited red`.
- Update the header comment line `builder ## Status (done|blocked)` to name the new value.
- In `plugins/sdlc-lite/scripts/run-selftest.sh`, next to the existing builder `want_rc` cases, add two cases:
  - `want_rc 0 builder L2 $'## Status\ninherited red: test_a'`
  - `want_rc 3 builder L2 $'## Status\ninherited red'`
### Acceptance criteria
- `grep -q 'want_rc 0 builder L2 .*inherited red: ' plugins/sdlc-lite/scripts/run-selftest.sh`
- `grep -q "builder) sect=Status; allowed='done|blocked|inherited red" plugins/sdlc-lite/scripts/run.sh`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`

## Step 3: board.py renders an inherited red step as 🔴
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py`:
- In `step_row`, right after the `blocked` check on the newest builder, add a check: when `section(last_build, 'Status')` starts with `inherited red`, return `('🔴', f'inherited red · builder {level_of(last_build)}, ask the user{tries}', LADDER['building'])`. `--summary` then counts it in `🔴<n>` without further change.
- Mention the inherited red rendering in the module docstring's Status paragraph.
- Add a selftest case in section 7, using `step_fixture`: a single builder whose result is `## Status\ninherited red: test_a\n` renders glyph 🔴 with a status that starts with `inherited red`. Its expect label must contain `inherited red`.
### Acceptance criteria
- `d=$(mktemp -d) && printf '## Status\ninherited red: test_a\n' > "$d/builder-L2.md" && python3 -c 'import sys, pathlib; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import board; g, s, _ = board.step_row(pathlib.Path(sys.argv[1]), "x", "L2"); sys.exit(0 if g == "🔴" and s.startswith("inherited red") else 1)' "$d"` (run from the repo root)
- `grep -q 'inherited red' plugins/sdlc-lite/scripts/board.py`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`

## Step 4: Builder procedure, chain and conductor routing, repo docs, and a check.py guard
level: L3
### Do
- **`plugins/sdlc-lite/agents/builder.md`:**
  - Add a numbered rule for the pre-build check. Before claiming that a gate criterion failed (a check meant to hold before and after the step, such as a `(guard)` or a suite or lint over the repo, not a criterion for the step's new behavior, which is red at base by design), run the same command at the committed HEAD the build started from. Use a throwaway worktree, `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`; on a merge step use `HEAD^1` once the merge commit exists. This leaves the step's own changes untouched.
  - If the gate is red there with the same failures (the same failing test names or findings), Status is `inherited red: <tests>`, listing the failing tests. Notes give both runs' commands and outcomes, and the work done so far stays in the tree.
  - If the failures differ, or the gate is green at base, it is an ordinary failure.
  - Remove "or fails on findings that predate this build and that the step does not ask to fix" from the `plan defect:` sentence. `plan defect` keeps parse errors, contradictions, and criteria that are wrong on their face.
  - Change the Status line of the output format to `done | blocked | inherited red: <tests>`.
- **`plugins/sdlc-lite/skills/chain/SKILL.md`:**
  - In the step 4 action list, add `inherited` → the gate was already red at the pre-build HEAD (Status `inherited red: <tests>`). Interactive: ask the user through AskUserQuestion (fix main first, rebuild once main is green, or stop). Unattended: stop the task and report the inherited tests. It is never a fail, a rebuild, a bump, or a replan, and never waives the gate.
  - Add a numbered item 7 under "For each step" that says the same.
- **`plugins/sdlc-lite/agents/conductor.md`:** add the same `inherited red` routing to the escalation bullet in "How you run roles".
- **`CLAUDE.md` (repo root):**
  - In the `scripts/steps.py` bullet, change the action list to `(`build`, `verify`, `reverify`, `rebuild`, `bump`, `replan`, `done`, `stop`, `inherited`)`. Add that a builder Status `inherited red: <tests>` maps to `inherited`.
  - Add a clause that `board.py` renders an inherited red step 🔴 and `run.sh` accepts that Status.
- **`.claude/agents/sdlc-lite-author.md`:** add an "Inherited-red route" invariant line, modeled on the No-verdict route line. It names steps.py, board.py, run.sh, builder.md, chain SKILL.md, conductor.md, check.py, and CLAUDE.md as the places that must stay in sync.
- **`plugins/sdlc-lite/scripts/check.py`:**
  - Add a guard in the pattern of `PLAN_DEFECT_DOCS`: the phrase `inherited red` must appear in `agents/builder.md`, `agents/conductor.md`, `skills/chain/SKILL.md`, `scripts/steps.py`, `scripts/board.py`, and `scripts/run.sh`.
  - Each miss appends the error `<rel>: inherited-red route missing "inherited red"`.
  - Add a numbered item for it to the module docstring.
### Acceptance criteria
- `grep -q 'inherited red: <tests>' plugins/sdlc-lite/agents/builder.md`
- `! grep -q 'findings that predate this build' plugins/sdlc-lite/agents/builder.md`
- `grep -q 'inherited red' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q 'inherited red' plugins/sdlc-lite/agents/conductor.md`
- `grep -q "replan., .done., .stop., .inherited" CLAUDE.md`
- `grep -q 'inherited red' .claude/agents/sdlc-lite-author.md`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && cp CLAUDE.md "$t/p/CLAUDE.md" && perl -pi -e 's/inherited red/xx/g' "$t/p/agents/conductor.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/p" 2>&1 | grep -q 'agents/conductor.md: inherited-red route missing "inherited red"'` (run from the repo root; proves the new guard bites)
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- Step 4's check.py guard needs the phrase `inherited red` in steps.py, board.py and run.sh, which Steps 1 to 3 add. Run Step 4 last, or its `check.sh` guard goes red.
- `check.sh` takes about 90s here, under the 300s `split --only` guard timeout. It spends no model call. On a loaded host it could approach the timeout.
- A criterion for the step's new behavior is red at base by design, so the builder must apply inherited red only to gate criteria. If builder.md words that loosely, every red-now criterion could come back as inherited red. The Do spells out the distinction, and the verifier stays unchanged, per the ticket's non-goal.
- A `(guard)` already red when `split --only` runs is still a `plan defect` by code. Inherited red covers only gates that go red after the split (a main sync) and gates not tagged `(guard)`.
- fanout.py treats a lane that ends on inherited red like any other non-merged outcome. That is out of scope, as a non-goal.
