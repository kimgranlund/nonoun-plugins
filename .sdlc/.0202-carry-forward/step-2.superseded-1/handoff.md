## Task goal
Add a `## Carry forward` section to the scout, researcher, architect, and archaeologist results and the reader rule to planner and builder.

## Step 2: Focused live run, report, and gates green
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
New files:
- `docs/reports/carry-forward-live-run/probe.sh`.
- `docs/reports/carry-forward-live-run/scout.txt`, `with.txt`, and `without.txt`, all written by probe.sh.
- `docs/reports/carry-forward-live-run.md`.

Changed: `docs/README.md` (one index line).

**probe.sh setup**
- Run it as `bash docs/reports/carry-forward-live-run/probe.sh` from the repository root.
- It sets `R=$(git rev-parse --show-toplevel)`, `RUN=$R/plugins/sdlc-lite/scripts/run.sh`, and `OUT=$R/docs/reports/carry-forward-live-run`.
- It makes `P=$(mktemp -d -t carry-forward-probe)` and prints it. It keeps the directory after the run, so the verifier can reread the logs.
- It builds two projects, `$P/with` and `$P/without`, with one shared function:
  - `git init -q`
  - the fixture files below
  - a `.gitignore` of `.sdlc/` and `.worktrees/`
  - one commit `init`, made with `-c user.name=probe -c user.email=probe@example.invalid`
  - then `.sdlc/cf/handoff.md`

Fixture files and their contents. The left column is the path; continuation lines belong to the same file:
```
README.md            Tiny table printer.
bin/table.sh         #!/usr/bin/env bash
                     . "$(dirname "$0")/../lib/table/render.sh"
                     render_row "$@"
lib/text/pad.sh      # pad_cell <text> <width>: left-align text in a cell of width characters
                     pad_cell() { printf '%-*s' "$2" "$1"; }
lib/text/trim.sh     trim() { printf '%s' "$1" | sed 's/^ *//; s/ *$//'; }
lib/table/render.sh  . "$(dirname "${BASH_SOURCE[0]}")/../text/pad.sh"
                     render_row() { local out='' c; for c in "$@"; do out+="|$(pad_cell "$c" 8)"; done; printf '%s|\n' "$out"; }
lib/table/header.sh  header_rule() { printf '+%s+\n' '--------'; }
lib/io/csv.sh        split_csv() { local IFS=,; printf '%s\n' $1; }
tests/pad_test.sh    . "$(dirname "$0")/../lib/text/pad.sh"
                     test "$(pad_cell ab 4)" = "ab  " && echo ok
```

**Fixture handoff `.sdlc/cf/handoff.md`**
- The title line `# Task: fill character for cell padding`.
- A Goal section (heading line `## Goal`) whose body says: `pad_cell` takes an optional third argument, a fill character (default a space), and pads with it, so `pad_cell ab 4 .` prints `ab..`; every existing caller keeps its output.
- A Constraints section (heading line `## Constraints`): Bash only; `bash tests/pad_test.sh` still prints `ok`.
- The handoff names the symbol but never its file, so locating it takes a search.

**Role runs**
- Run the roles in this order:
  1. scout L1 in `$P/with`.
  2. planner L2 in `$P/with`, whose artifacts dir then holds `scout-L1.md`.
  3. planner L2 in `$P/without`, which has no scout result.
- Each run goes through a wrapper that works in a subshell:
  - It unsets `CLAUDECODE`, every `CLAUDE_CODE_*` variable, and `SDLC_ROLE SDLC_BASE_SHA SDLC_TMP_WORKTREES SDLC_HEADLESS SDLC_ATTEMPT_ID SDLC_ATTEMPT_NAME SDLC_LIFECYCLE_CHILD SDLC_ROUTING_REASON SDLC_BACKEND`.
  - It then `cd`s into the project and runs `bash "$RUN" <role> <level> .sdlc/cf/handoff.md`.
  - Precedent: the Method section of `docs/reports/plan-reviewer-live-run.md`.
- Planner L2 is the planner level the Lean chain section of `skills/chain/SKILL.md` gives a size S or M ticket. The scout has only L1.
- Run one trial per arm. Never rerun an arm to get a different outcome. Report a run that exits nonzero as it is.

**Evidence files**
probe.sh writes one file per arm: `scout.txt` from `$P/with/.sdlc/cf/scout-L1.log` and `.md`; `with.txt` and `without.txt` from each project's `.sdlc/cf/planner-L2.log` and `.md`. Lines come in this order:
- `arm=<scout|with|without>`, `project=<dir>`, `plugin=$R/plugins/sdlc-lite`, `result=<result path>`, `header=<first line of the result>`, and `model=<distinct .message.model values in the log, comma-joined>`.
- One line per tool call, in log order: `tool=<name> input=<compact JSON input, first 200 characters, trailing whitespace removed>`. Build them with `jq -R -r` over `fromjson? // empty | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use")` (verified on a planner log on this host).
- `tool_calls=<n>`.
- `tree_searches=<n>`: tool lines named Grep or Glob, plus Bash lines whose input matches the ERE `git grep|grep -[A-Za-z]*[rR]|rg |find `.
- `symbol_searches=<n>`: the tree_searches lines that contain `pad_cell`.
- Scout only:
  - `carry_forward_section=yes|no`: yes when the result has the heading line `## Carry forward`.
  - `carry_forward_lines=<n>`: the non-blank lines from that heading to the next heading line or the end of the file.
- Planner arms only:
  - `read_scout_result=yes|no`: yes when some tool line contains `scout-L1.md`.
  - `cites_result_path=yes|no`: yes when `planner-L2.md` contains `scout-L1.md`.
  - `copies_section=yes|no`: yes when `planner-L2.md` has the heading line `## Carry forward`, or contains verbatim any body line of the arm-with scout result's section that is 20 or more characters long after stripping surrounding whitespace and a leading `- `.

`carry_forward_section=yes` also proves that the scout ran this worktree's contracts, because the base contract asks for no such section.

**Running and failure handling**
- Run probe.sh once, in the foreground, with the Bash timeout at 3600000.
- An evidence criterion can fail on model behavior. For example: the scout writes no section or more than 15 lines; arm with searches for `pad_cell`, skips the scout result, does not cite it, or copies it; or arm without never searches for `pad_cell`. Then:
  - Do not edit any contract, and do not rerun to get a pass.
  - Status is blocked, and Notes quote the evidence lines.
  - The report and evidence files stay in the tree, stating the actual result.

**Report `docs/reports/carry-forward-live-run.md`**
Follow the precedent of `docs/reports/role-result-schema-live-run.md`. Start with the title `# Carry forward live run` and a `Recorded: <date>. Live run for ticket T-0202: ...` line. Then:
- `## Environment`: the date, `sw_vers` or `uname -r`, `claude --version`, the `model=` lines and result headers, `git rev-parse HEAD` with a note that the step 1 contracts are in it, and the project path.
- `## Method`: the fixture, the two arms, the commands, and the metric definitions above.
- `## Evidence`: one table with columns arm, tool_calls, tree_searches, symbol_searches, read_scout_result, cites_result_path, copies_section. Quote the scout's carried-forward text and list the scout's own search tool lines.
- `## Limits`:
  - one trial per arm;
  - Claude Code only: Codex was not run, and its generated agents are checked only by `codex_roles.py generate --check`;
  - symbol_searches is a heuristic over tool inputs;
  - one small fixture.

Raw logs stay out of the repository (`*.log` is in `.gitignore`).

**docs/README.md**
Add one line after the `Messages wait live run` entry, stating the outcome the evidence shows. For a passing run the line is: `- [Carry forward live run](validation/carry-forward-live-run.md): dated live run for T-0202 in which a planner given a scout result with a Carry forward section read it, cited its path, and did not repeat the scout's search, compared with a planner given no scout result.`

**Gates green**
Run every gate below. Fix any red that step 1 introduced, and only in step 1's files, which the scope guard allows. Write no em dashes.

Depends on: step 1. The run needs the new contracts in the tree.
### Acceptance criteria
- `f=docs/reports/carry-forward-live-run/scout.txt && grep -qx "carry_forward_section=yes" "$f" && awk -F= '$1=="carry_forward_lines" && $2>=1 && $2<=15 {ok=1} END {exit !ok}' "$f"`
- `f=docs/reports/carry-forward-live-run/with.txt && grep -qx "read_scout_result=yes" "$f" && grep -qx "cites_result_path=yes" "$f" && grep -qx "copies_section=no" "$f" && grep -qx "symbol_searches=0" "$f"`
- `awk -F= '$1=="symbol_searches" && $2>=1 {ok=1} END {exit !ok}' docs/reports/carry-forward-live-run/without.txt`
- `bash -n docs/reports/carry-forward-live-run/probe.sh && for a in scout with without; do f=docs/reports/carry-forward-live-run/$a.txt; grep -qx "arm=$a" "$f" || exit 1; grep -q "^tool=" "$f" || exit 1; done`
- `f=docs/reports/carry-forward-live-run.md && grep -qx "## Environment" "$f" && grep -qx "## Method" "$f" && grep -qx "## Evidence" "$f" && grep -qx "## Limits" "$f" && grep -qF "T-0202" "$f" && grep -qF "(validation/carry-forward-live-run.md)" docs/README.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(docs/reports/carry-forward-live-run\.md|docs/reports/carry-forward-live-run/(probe\.sh|scout\.txt|with\.txt|without\.txt)|docs/README\.md|plugins/sdlc-lite/agents/(scout|researcher|architect|archaeologist|planner|builder)\.md|plugins/sdlc-lite/scripts/(results|check)\.py|plugins/sdlc-lite/adapters/codex/agents/sdlc-[a-z0-9-]+\.toml)$" | grep -q .`
- (guard) `! grep -qsF "—" docs/reports/carry-forward-live-run.md docs/reports/carry-forward-live-run/probe.sh docs/README.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
