<!-- role=planner level=L2 model=opus effort=medium -->
Handoff read and the code checked. Writing the plan now: two steps, the script first and then the wiring.

## Goal
Add `plugins/sdlc-lite/scripts/steps.py` (`split`, `selftest`) so that /chain writes step handoffs from a plan by running a script, and wire it into check.sh, /chain, handoff-format, CLAUDE.md, and the author agent.

## Step 1: Add scripts/steps.py with split and selftest
level: L3
### Do
Create `plugins/sdlc-lite/scripts/steps.py`. Use only the Python 3 standard library and argparse, and match the style of `scripts/tickets.py` and `scripts/board.py`: a module docstring with usage, a `main(argv)` function, and `sys.exit(main(sys.argv[1:]))`. Make it executable.

`split <planner.md | task dir> [--only N ...]`:
- Input. Given a directory, use the newest `planner-*.md` in it by mtime. Given a file, the task dir is the file's parent. If a directory has no `planner-*.md`, fail.
- Task goal. Read `<task dir>/handoff.md`, skip any leading `---` front matter block, and take the text under `## Goal` up to the next `## ` heading, with leading and trailing blank lines stripped. If the handoff or its Goal section is missing, fail with a clear message.
- Parsing. A step block starts at a line matching `^## Step (\d+): (.+)$` and runs up to the line before the next line starting with `## ` (another step, `## Risks`, or anything else) or to end of file. `### Do` and `### Acceptance criteria` stay inside the block verbatim. Trim trailing blank lines from each block. Fail on: no step blocks, a duplicate step number, or a block with no line matching `^level: L[1-5]\s*$`.
- `--only N`. Repeatable (`action='append'`, int). Write only the listed steps. An N that is not in the plan is an error.
- Refusal. For each step to be written, if `<task dir>/step-<n>/` already holds a `builder-*.md` or `verifier-*.md`, fail. The message must name the /chain 4.2 rename to `step-<n>.superseded-<k>/`. The script never renames anything.
- Atomicity. Run every check (parse, --only, refusal) before any write. Every failure exits nonzero, prints its message on stderr, and writes nothing.
- Output. For each step, write `<task dir>/step-<n>/handoff.md` (create the dir if missing, overwrite an existing handoff.md) with the content `## Task goal\n<goal>\n\n<step block>\n`. Print one line per file written (its path).

`selftest`: build fixtures in a `tempfile` dir and prove each case, printing `ok: ...` lines and exiting nonzero on any failure. Cases:
- (a) A normal 2-step plan followed by `## Risks`. Both handoffs are written and match the template exactly, and the Risks text is absent from the last step.
- (b) `--only 2` writes only step-2. `--only 9` fails and writes nothing.
- (c) Task-dir input with `planner-L2.md` older and `planner-L3.md` newer (set mtimes with `os.utime`) uses the newer file's steps.
- (d) Missing `level:` fails and writes nothing.
- (e) A duplicate step number fails and writes nothing.
- (f) No steps fails.
- (g) `step-1/builder-L2.md` present makes the run fail with a message containing `superseded`, and step-1/handoff.md and every other step stay unchanged.
- (h) A handoff with no Goal section fails.
- Also: a re-split with a plain existing `step-1/handoff.md` (no role output) overwrites it.

Each failure case must also check that nothing was written, for example by comparing the file listing before and after.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 and prints an ok line for each of cases (a) through (h) plus the overwrite case.
- Negative control: temporarily change the level regex to accept any line, or skip the refusal check, and the selftest exits nonzero. Revert afterwards and confirm with `git diff` that only the intended file differs.
- Manual split: `d=$(mktemp -d); cp -R .sdlc/.0025-bench-project-dirs "$d/"; rm -rf "$d"/bench-project-dirs/step-*; python3 plugins/sdlc-lite/scripts/steps.py split "$d/bench-project-dirs"` exits 0. Each `step-<n>/handoff.md` starts with `## Task goal`, then the Goal text from that handoff.md, a blank line, and `## Step <n>:`. It contains the `level:` line and ends at the line before the next `## ` heading of the planner file (`diff` against the corresponding slice of the planner file).
- Running the same split without the `rm` step, against a task dir whose step dirs hold builder output, exits nonzero, names `superseded`, and changes no file mtimes.
- `git status` shows no changes under the real `.sdlc/` (all splits run on temp copies).
- `python3 -m py_compile plugins/sdlc-lite/scripts/steps.py` passes, and `grep -E '^(import|from) ' plugins/sdlc-lite/scripts/steps.py` lists only stdlib modules.

## Step 2: Wire steps.py into check.sh, /chain, and the docs
level: L2
### Do
- `plugins/sdlc-lite/scripts/check.sh`: add `python3 "$root/scripts/steps.py" selftest || fail=1` after the board selftest line, and mention the steps selftest in the header comment.
- `plugins/sdlc-lite/skills/chain/SKILL.md`:
  - Add `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*)` to `allowed-tools`.
  - Step 3: replace "For each `## Step n` block, write `step-<n>/handoff.md` per the step template" with a sentence that runs `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py split .sdlc/<task>` and says never to parse the plan by hand.
  - Step 4.2: keep the superseded rename as a conductor action. Replace "write fresh `step-<n>/handoff.md` files, rewriting the remaining step handoffs from the newest planner file" with running `steps.py split .sdlc/<task>` after the rename (optionally `--only N` for the steps being rewritten), noting that the script refuses a step dir that still holds builder or verifier output.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: under "Step handoff", add one line saying `scripts/steps.py split` writes these files from the newest planner file and that no one writes them by hand.
- Repo-root `CLAUDE.md`:
  - Add a Layout bullet for `scripts/steps.py`: `split <planner.md | task dir> [--only N]` writes `step-<n>/handoff.md` per the step template, refuses a step dir holding builder or verifier output, and `selftest` proves each failure; `/chain` steps 3 and 4.2 run it.
  - Add "the steps selftest" to the Commands check.sh list.
- `.claude/agents/sdlc-lite-author.md`: add "steps selftest" to the check.sh list on line 19.
- Audit: grep `agents/` and `skills/` for any other instruction to parse `## Step` blocks or to write step handoffs by hand, and point each one at the script. `agents/planner.md` only defines the output format, so leave it unchanged. At plan time no other hits were found.

### Acceptance criteria
- `plugins/sdlc-lite/scripts/check.sh` exits 0, and its output includes the steps.py selftest ok lines.
- Negative control: break the steps selftest temporarily (for example, make one assertion false), confirm `check.sh` exits nonzero, then revert.
- `grep -n 'steps.py' plugins/sdlc-lite/skills/chain/SKILL.md` shows the allowed-tools entry, a step 3 line, and a step 4.2 line.
- `grep -n 'write `step-<n>/handoff.md` per the step template' plugins/sdlc-lite/skills/chain/SKILL.md` returns nothing.
- `grep -n 'steps.py' plugins/sdlc-lite/skills/handoff-format/SKILL.md CLAUDE.md .claude/agents/sdlc-lite-author.md` has at least one hit in each file.
- `grep -rn '## Step' plugins/sdlc-lite/agents plugins/sdlc-lite/skills` shows only `agents/planner.md` (the format definition) and the handoff-format template.
- The /chain 4.2 text still says the conductor moves step dirs to `step-<n>.superseded-<k>/`.
- The diff touches no file in `scripts/run.sh`, `scripts/board.py`, or `agents/planner.md`.

## Risks
- Older planner files in `.sdlc/` may format steps differently (for example `level:` inside `### Do`, or extra `## ` headings inside a step), so the manual-split check could fail on a real file. If `bench-project-dirs` does not fit, the verifier should pick another `planner-*.md` that has step dirs and a Goal section.
- The ticket asks for a `## Task goal` heading, but some existing step handoffs may have been written in other shapes by hand. That is harmless for new runs.
- No plugin version bump is planned. If releases require one, `plugin.json` (0.4.3) needs a bump, which is out of scope here.
- `.sdlc/.0039-superseded-step-dirs` has a work-in-progress commit that also touches /chain 4.2 wording. If it lands separately, step 2's edit to 4.2 may conflict.
