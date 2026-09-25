<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0040: A script writes step handoffs from a plan

## PR body
### Summary
/chain used to tell each conductor to parse `## Step n` blocks out of the plan and write `step-<n>/handoff.md` by hand. Every session ended up writing its own parser, and one session needed a second parser just for a single-step replan. This PR adds `scripts/steps.py`, which writes the step handoffs, and changes /chain and the docs to call it.

### Changes
**Step 1: `plugins/sdlc-lite/scripts/steps.py`** (new file, executable, standard library only)
- `split <planner.md | task dir> [--only N ...]`:
  - Given a task dir, it uses the newest `planner-*.md` by mtime.
  - It reads the task goal from the `## Goal` section of `handoff.md` and skips any front matter.
  - It writes `step-<n>/handoff.md` as `## Task goal`, then the goal, then the step block copied verbatim.
- It fails and writes nothing when:
  - the plan has no steps
  - a step number appears twice
  - a step has no `level: L<1-5>` line
  - `--only` names a step that isn't in the plan
  - the handoff has no Goal section, or the Goal section is empty
  - a step dir already holds `builder-*.md` or `verifier-*.md`. The error message points to the /chain 4.2 rename to `step-<n>.superseded-<k>/`. The script never renames anything itself.
- `selftest` covers cases (a) through (h) and the overwrite case, 12 ok lines in all.

**Step 2: wiring**
- `scripts/check.sh` now runs the steps selftest.
- `skills/chain/SKILL.md`:
  - `allowed-tools` gains the `steps.py` entry.
  - Step 3 runs `steps.py split .sdlc/<task>` and says never to parse the plan by hand.
  - Step 4.2 keeps the superseded rename as a conductor action, then runs `steps.py split`, optionally with `--only N`.
- `skills/handoff-format/SKILL.md` now says `steps.py split` writes step handoffs.
- The repo `CLAUDE.md` gets a Layout bullet and a check.sh list entry. `.claude/agents/sdlc-lite-author.md` gets a check.sh list entry.
- An audit of `agents/` and `skills/` found no other instructions that parse steps by hand.

### Verification
- **Step 1: verifier L2 (Fable medium), pass.**
  - The selftest exits 0 with all 12 ok lines.
  - Negative controls, each run on a throwaway copy of the script: accepting any level line, skipping the refusal, disabling the duplicate check, and writing before the refusal check. Each one made the selftest exit 1.
  - Manual split of a temp copy of `.sdlc/bench-project-dirs`: the output matched expected files rebuilt independently, with an empty `diff` for both steps.
  - Refusing a step dir that holds builder output exited 1, named `superseded`, and left every file mtime unchanged.
  - `py_compile` passes and every import is from the standard library.
- **Step 2: verifier L1 (Sonnet medium), pass.**
  - `check.sh` exits 0 and its output includes `steps selftest: PASS`.
  - A negative control on a temp plugin copy flipped the selftest to FAIL. The exit code alone did not isolate the edit, because the copy has no repo-root CLAUDE.md. The line `|| fail=1` in check.sh turns a selftest FAIL into a nonzero exit.
  - The greps confirm the `steps.py` hits in chain (allowed-tools, step 3, step 4.2), handoff-format, CLAUDE.md, and the author agent, and that the old hand-parse wording is gone.
  - The 4.2 rename text is still there. `run.sh`, `board.py`, and `planner.md` are untouched.
  - The `## Step` grep also matches the `## Steps` heading in `decompose/SKILL.md`. The builder and the verifier both judged it an unrelated section heading.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `scripts/steps.py` (`split`, `selftest`). It writes `step-<n>/handoff.md` files from the newest plan and refuses step dirs that already hold builder or verifier output. /chain steps 3 and 4.2 now run it instead of parsing plans by hand, and `check.sh` runs its selftest.

## Follow-ups
- Reconcile the /chain 4.2 wording from T-0040 (rename, then `steps.py split`) with the in-progress superseded-step-dirs ticket, which also edits 4.2 and may conflict when it lands.
