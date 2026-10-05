# Carry forward live run

Recorded: 2026-10-04. Live run for ticket T-0202: a scout writes a `## Carry forward` section, and a planner given that result reads it, cites its path, and does not repeat the scout's search, compared with a planner given no scout result. Two runs of the same probe, each with one real Claude Code run per arm: scout L1, then planner L2 with the scout result, then planner L2 without one. The criteria read run 2.

Outcome of run 2: the scout wrote a 5-line section. The planner given it printed it in its first tool call, cited `.sdlc/cf/scout-L1.md` in its plan, copied none of it, and ran no `pad_cell` search. The planner without a scout result ran `git grep -n pad_cell`, and the full-input metric counts it (`symbol_searches=1`). The with planner read the scout result through a glob, `for f in .sdlc/cf/*.md; do ...; cat "$f"; done`, so no tool input names `scout-L1.md`, and the specified `read_scout_result` metric, which looks for that file name in tool inputs, records `no`. The with-arm criterion (`read_scout_result=yes`) is therefore red as specified although the planner read the file; see Evidence and Limits. In run 1 the 200-character metric missed the without planner's `git grep -n pad_cell`; recounted over full inputs, run 1 meets every evidence criterion.

## Environment

Run 2:

- Date: 2026-10-04, 10:38 to 10:39 PDT.
- Host OS: macOS 26.6.2 (build 25G83), Darwin 25.6.0 (`sw_vers`, `uname -r`).
- `claude --version`: `2.1.286 (Claude Code)`. Default Claude backend of `plugins/sdlc-lite/scripts/run.sh`.
- Models, from the `model=` lines and result headers of the evidence files:
  - scout: `model=claude-haiku-4-5-20251001`; result header `<!-- role=scout level=L1 model=claude-haiku-4-5 effort=low -->`.
  - planner, with: `model=claude-opus-5-5`; result header `<!-- role=planner level=L2 model=opus effort=medium -->`.
  - planner, without: `model=claude-opus-5-5`; result header `<!-- role=planner level=L2 model=opus effort=medium -->`.
- Repo commit: `git rev-parse HEAD` is `4c442cea62bcedd912508eb0182b2fede1649805` (`T-0202 replan split (step 2)`), with the step 2 `probe.sh` changes uncommitted in the worktree. The step 1 contracts (the scout's `## Carry forward` section and the planner and builder reader rule) are committed in it, and every run used `plugin=<repo>/plugins/sdlc-lite` from this worktree.
- Throwaway project: `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.3grTyXYGVo`, made with `mktemp -d`, outside this repository, holding `with/` and `without/`. Role logs are kept there, not in this repository.

Run 1:

- Same host, `claude --version`, and models as run 2.
- Repo commit: `8433d80deca3e558c440e78249bba71c81ac87f2` (`.sdlc/.0202-carry-forward step-1: built and verified`), with the step 1 contracts committed in it.
- Throwaway project: `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.7n2YHsjnKS`.

## Method

[probe.sh](carry-forward-live-run/probe.sh) did everything below and wrote [scout.txt](carry-forward-live-run/scout.txt), [with.txt](carry-forward-live-run/with.txt), and [without.txt](carry-forward-live-run/without.txt). Each run ran it once, from the repository root:

```sh
bash docs/reports/carry-forward-live-run/probe.sh
```

Run 2 overwrote run 1's evidence files; run 1's files stay in git history and in this report.

Fixture. Two projects, `with/` and `without/`, were built by one function: `git init -q`, the files below, a `.gitignore` of `.sdlc/` and `.worktrees/`, one commit `init`, then `.sdlc/cf/handoff.md`.

```
README.md            Tiny table printer.
bin/table.sh         sources lib/table/render.sh, calls render_row "$@"
lib/text/pad.sh      # pad_cell <text> <width>: ...; pad_cell() { printf '%-*s' "$2" "$1"; }
lib/text/trim.sh     trim()
lib/table/render.sh  sources ../text/pad.sh; render_row calls pad_cell "$c" 8
lib/table/header.sh  header_rule()
lib/io/csv.sh        split_csv()
tests/pad_test.sh    sources lib/text/pad.sh; test "$(pad_cell ab 4)" = "ab  " && echo ok
```

The handoff is titled `# Task: fill character for cell padding`. Its Goal: `pad_cell` takes an optional third argument, a fill character (default a space), so `pad_cell ab 4 .` prints `ab..`, and every existing caller keeps its output. Its Constraints: Bash only, and `bash tests/pad_test.sh` still prints `ok`. It names the symbol but not its file.

Arms, in order, one trial each per run, none rerun within a run. Each ran through a subshell wrapper that unsets `CLAUDECODE`, every `CLAUDE_CODE_*` variable, and `SDLC_ROLE SDLC_BASE_SHA SDLC_TMP_WORKTREES SDLC_HEADLESS SDLC_ATTEMPT_ID SDLC_ATTEMPT_NAME SDLC_LIFECYCLE_CHILD SDLC_ROUTING_REASON SDLC_BACKEND`, then runs from the project root, as in [the plan reviewer live run](plan-reviewer-live-run.md):

```sh
cd <P>/with    && bash <repo>/plugins/sdlc-lite/scripts/run.sh scout L1 .sdlc/cf/handoff.md
cd <P>/with    && bash <repo>/plugins/sdlc-lite/scripts/run.sh planner L2 .sdlc/cf/handoff.md
cd <P>/without && bash <repo>/plugins/sdlc-lite/scripts/run.sh planner L2 .sdlc/cf/handoff.md
```

All three exited 0 in both runs. Planner L2 is the planner level the Lean chain gives a size S or M ticket; the scout has only L1. In `with/` the planner's artifacts dir held `scout-L1.md`; `without/` had no scout result.

Metrics, per arm, from `<role>-<level>.log` and `.md`. Run 1 cut each tool input at 200 characters and read searches from those cut tool lines. Run 2 used the full input and read searches from the log:

- `tool=<name> input=<...>`: one line per tool call in log order; the input is the compact JSON input, trailing whitespace removed, with no cut, from `jq -R -r` over `fromjson? // empty | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use")`.
- `search=<...>`: read from the log, not from the tool lines, and printed in log order after all tool lines and before `tool_calls=`. Each Grep or Glob tool call gives `search=<name> <compact JSON input>`. For each Bash tool call, the full `.input.command` string, never `.input.description`, is split into command-list elements on newline, `;`, `&&`, and `||`, a pipeline staying whole; each element, trimmed of surrounding whitespace, that matches the ERE `git grep|grep -[A-Za-z]*[rR]|rg |find ` gives `search=Bash <the element as a JSON string>`, for example `search=Bash "git grep -n pad_cell"`. The description is excluded because run 1's without planner described a call as `Read source files and find pad_cell callers`, model prose that matches `find `. The unit is a command-list element because run 1's with planner batched `find . -name AGENTS.md` with criterion probes that name `pad_cell` in one call.
- `tool_calls`: the number of tool lines.
- `tree_searches`: the number of `search=` lines.
- `symbol_searches`: the number of `search=` lines that contain `pad_cell`.
- Scout only: `carry_forward_section` is yes when the result has the heading line `## Carry forward`; `carry_forward_lines` counts the non-blank lines after that heading, up to the next heading line or the end of the file.
- Planner arms only: `read_scout_result` is yes when some tool line contains `scout-L1.md`; `cites_result_path` is yes when `planner-L2.md` contains `scout-L1.md`; `copies_section` is yes when `planner-L2.md` has the heading line `## Carry forward` or contains verbatim any body line of the `with/` scout section that is 20 or more characters long after stripping surrounding whitespace and a leading `- `.

Evidence-only mode. `bash docs/reports/carry-forward-live-run/probe.sh --evidence-only <project dir> <out dir>` builds no fixture and runs no role. It computes the three arms' evidence from `<project dir>/with` and `<project dir>/without` exactly as a full run does, writes only `scout.txt`, `with.txt`, and `without.txt` to `<out dir>`, and exits 0; any other argument count prints a usage line and exits 2. A missing or empty log or result gives zero tool lines and the `no` values. It recounts a kept run without a model call, and it is the negative control for the metric. The control's fixture is a project whose logs and results are empty files except the without planner's log, which holds three Bash tool calls, each with the description `git grep the pad_cell callers`: `cat lib/text/pad.sh`; a command that pads `cat lib/text/pad.sh` with a 5000-character comment before `; git grep -n pad_cell`; and `find . -name AGENTS.md; . lib/text/pad.sh; pad_cell ab 4 .`. The full-input metric gives `tree_searches=2`, `symbol_searches=1`, a line `search=Bash "git grep -n pad_cell"`, and a tool line holding `git grep -n pad_cell`. The 200-character metric gives 2 and 2 on the same fixture: it misses the long call's search and counts the batched `find` and `pad_cell` call as a `pad_cell` search.

## Evidence

### Run 1: 200-character metric

| arm | tool_calls | tree_searches | symbol_searches | read_scout_result | cites_result_path | copies_section |
| --- | --- | --- | --- | --- | --- | --- |
| scout | 12 | 4 | 1 | n/a | n/a | n/a |
| with | 5 | 2 | 0 | yes | yes | no |
| without | 3 | 0 | 0 | no | no | no |

The scout result: `carry_forward_section=yes`, `carry_forward_lines=6`. Its carried-forward text, verbatim:

```
## Carry forward
- `pad_cell` currently uses `printf '%-*s' "$2" "$1"` at lib/text/pad.sh:2
- Only two call sites: render_row (lib/table/render.sh:2) and test (tests/pad_test.sh:2)
- Both existing calls omit the third parameter and must keep space-padding (existing output)
- Test constraint: `bash tests/pad_test.sh` must print `ok` (test on line 2 expects `pad_cell ab 4` to equal `ab  `)
- Implementation needs to accept optional `$3` parameter as fill char, default to space
- Printf format string `%-*s` pads with spaces; need to handle custom fill character via expansion or alternative method
```

The section lists the two call sites but does not name the search that produced the list or its scope, which the scout contract asks for with a complete list. The scout's own search tool lines (`<P>` is the project dir):

```
tool=Bash input={"command":"find /private<P>/with -type f -name \"*.sh\" | head -20"}
tool=Bash input={"command":"grep -r \"pad_cell\" /private<P>/with --include=\"*.sh\" -n"}
tool=Bash input={"command":"grep -r \"lib/text/pad\" /private<P>/with --include=\"*.sh\" -n"}
tool=Bash input={"command":"grep -r \"pad\\.sh\" /private<P>/with --include=\"*.sh\" -n"}
```

Planner with the scout result. Its second tool call was `cat .sdlc/cf/scout-L1.md`, and its first had already printed every file in `.sdlc/cf`. Its two tree searches are `find . -name AGENTS.md -not -path './.sdlc/*'`; neither names `pad_cell`. Its step's Do says "Contract dependents come from `.sdlc/cf/scout-L1.md` (Carry forward)" and lists the two call sites, and its Assumptions cite the same path. It did not add a `## Carry forward` heading or copy a section line.

Planner without a scout result. Its second tool call, untruncated, is:

```
cd <P>/without; for f in lib/text/pad.sh tests/pad_test.sh bin/table.sh lib/table/*.sh lib/io/csv.sh lib/text/trim.sh README.md .gitignore; do echo "== $f"; cat $f; done; git grep -n pad_cell; find . -name AGENTS.md -not -path './.git/*'
```

`git grep -n pad_cell` starts after character 200 of the compact JSON input, so the truncated tool line in run 1's `without.txt` held neither it nor `find `, and the 200-character metric recorded `tree_searches=0` and `symbol_searches=0`. Its plan states "Contract dependents: `git grep -n pad_cell` finds two" and the Assumptions say "verified by `git grep -n pad_cell`".

Recount. Step 2 ran the full-input metric over run 1's kept logs, with no model call:

```sh
bash docs/reports/carry-forward-live-run/probe.sh --evidence-only /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.7n2YHsjnKS "$(mktemp -d)"
```

It gives scout 4 and 1, with 2 and 0, and without 2 and 1 (tree_searches and symbol_searches); every other evidence value is unchanged. On that recount run 1 meets every evidence criterion: the planner with the scout result did not repeat the `pad_cell` search, and the planner without one ran it. Its `search=` lines (`<P>` is run 1's project dir):

```
scout:
search=Bash "find /private<P>/with -type f -name \"*.sh\" | head -20"
search=Bash "grep -r \"pad_cell\" /private<P>/with --include=\"*.sh\" -n"
search=Bash "grep -r \"lib/text/pad\" /private<P>/with --include=\"*.sh\" -n"
search=Bash "grep -r \"pad\\.sh\" /private<P>/with --include=\"*.sh\" -n"
with:
search=Bash "find . -name AGENTS.md -not -path './.sdlc/*'"
search=Bash "find . -name AGENTS.md -not -path './.sdlc/*'"
without:
search=Bash "git grep -n pad_cell"
search=Bash "find . -name AGENTS.md -not -path './.git/*'"
```

### Run 2: full-input metric

| arm | tool_calls | tree_searches | symbol_searches | read_scout_result | cites_result_path | copies_section |
| --- | --- | --- | --- | --- | --- | --- |
| scout | 11 | 4 | 1 | n/a | n/a | n/a |
| with | 3 | 1 | 0 | no | yes | no |
| without | 3 | 2 | 1 | no | no | no |

The scout result: `carry_forward_section=yes`, `carry_forward_lines=5`. Its carried-forward text, verbatim except one character: the scout's first line held an em dash after `"$2" "$1"`, written here as `--`.

```
## Carry forward
- `pad_cell` defined at /lib/text/pad.sh:2 as `printf '%-*s' "$2" "$1"` -- currently takes 2 args (text, width)
- Single caller: /lib/table/render.sh:2 in `render_row` loop, calls `pad_cell "$c" 8` with 2 args only
- Test at /tests/pad_test.sh:2 asserts `pad_cell ab 4` equals `ab  ` (space-padded), must pass after modification
- `printf '%-*s'` with format specifier can accept fill char via `%(...)s` in newer bash, or require wrapper logic for custom padding char
- Default fill must be space for backward compatibility; third arg optional
```

The section names `lib/table/render.sh:2` as the single caller and the test separately, and, as in run 1, it does not name the search that produced the list or its scope.

The `search=` lines of each arm, verbatim:

```
scout:
search=Bash "find /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.3grTyXYGVo/with -type f -name \"*.sh\" | head -20"
search=Bash "grep -r \"pad_cell\" /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.3grTyXYGVo/with --include=\"*.sh\""
search=Bash "grep -r \"render_row\\|\\.table/render\" /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.3grTyXYGVo/with --include=\"*.sh\""
search=Bash "find /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.3grTyXYGVo/with/lib -type f"
with:
search=Bash "find . -name AGENTS.md -not -path './.git/*'"
without:
search=Bash "git grep -n pad_cell"
search=Bash "find . -name AGENTS.md -not -path './.git/*'"
```

Planner with the scout result. Its first tool call (`<P>` is run 2's project dir) was:

```
cd <P>/with && cat .sdlc/cf/handoff.md; ls -la .sdlc/cf; for f in .sdlc/cf/*.md; do echo "=== $f"; cat "$f"; done; git ls-files | head -50
```

Its tool result, in the log, prints `=== .sdlc/cf/scout-L1.md` and then the scout result with its `## Carry forward` section. No tool input names `scout-L1.md`, so `read_scout_result=no`. Its one tree search is `find . -name AGENTS.md -not -path './.git/*'`, which does not name `pad_cell`. Its step's Do says "Callers and the existing test come from the scout result `.sdlc/cf/scout-L1.md` (Carry forward)", and its Assumptions say the one caller is "verified by `.sdlc/cf/scout-L1.md` Carry forward". Its Risks say "The scout's caller list is relied on without a second search." It did not add a `## Carry forward` heading or copy a section line.

Planner without a scout result. Its second tool call ran `git grep -n pad_cell` as its own command-list element, and its plan lists "Contract dependents, from `git grep -n pad_cell`" and says the two callers are "verified by `git grep -n pad_cell`".

Against the step's criteria, run 2 meets the scout criterion (`carry_forward_section=yes`, 5 lines) and the without criterion (`symbol_searches=1`). The with criterion is red on `read_scout_result=no` alone; its other three values hold (`cites_result_path=yes`, `copies_section=no`, `symbol_searches=0`).

## Limits

- Two runs, one trial per arm in each, on one machine and one account. Model behavior varies between runs. The criteria read run 2. Run 2 was the conductor's decision, recorded as "rerun the arms" in the handoff's plan review, and it keeps the evidence files produced end to end by the committed `probe.sh`. Run 1 already met every evidence criterion on the full-input recount, so run 2 was not taken to change an outcome. No run 3 was made.
- Claude Code only: Codex was not run, and its generated agents are checked only by `codex_roles.py generate --check`.
- The metrics are heuristics over tool inputs. `tree_searches` and `symbol_searches` count search commands, not reads. The ERE misses a non-recursive grep over globs, such as `grep -n pad_cell lib/*/*.sh`, and a search split across command-list elements. `read_scout_result` looks for the file name in tool inputs, so it misses a read through a glob such as `cat .sdlc/cf/*.md`; in run 2 that hid the with planner's read of the scout result, and the criterion for that arm is red although the read happened.
- One small fixture: eight files and two call sites. The without planner found the callers in one compound command, so the saving the scout result buys here is one search, not a measured cost difference.
