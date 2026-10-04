# Carry forward live run

Recorded: 2026-10-04. Live run for ticket T-0202: a scout writes a `## Carry forward` section, and a planner given that result reads it, cites its path, and does not repeat the scout's search, compared with a planner given no scout result. One real Claude Code run per arm: scout L1, then planner L2 with the scout result, then planner L2 without one.

Outcome: the scout wrote a 6-line section, and the planner given it read it, cited `.sdlc/cf/scout-L1.md`, copied none of it, and ran no `pad_cell` search. The planner without a scout result did search for `pad_cell` (`git grep -n pad_cell`, named in its plan), but the search sits past character 200 of its tool input, so the specified `symbol_searches` metric, which reads truncated inputs, records 0 for that arm. The without-arm criterion (`symbol_searches>=1`) is therefore red as specified; see Evidence and Limits.

## Environment

- Date: 2026-10-04.
- Host OS: macOS 26.6.2 (build 25G83), Darwin 25.6.0.
- `claude --version`: `2.1.286 (Claude Code)`; the scout log records `"claude_code_version":"2.1.286"`. Default Claude backend of `plugins/sdlc-lite/scripts/run.sh`.
- Models, from the `model=` lines of the evidence files:
  - scout: `model=claude-haiku-4-5-20251001`; result header `<!-- role=scout level=L1 model=claude-haiku-4-5 effort=low -->`.
  - planner, with: `model=claude-opus-5-5`; result header `<!-- role=planner level=L2 model=opus effort=medium -->`.
  - planner, without: `model=claude-opus-5-5`; result header `<!-- role=planner level=L2 model=opus effort=medium -->`.
- Repo commit: `git rev-parse HEAD` is `8433d80deca3e558c440e78249bba71c81ac87f2` (`.sdlc/0202-carry-forward step-1: built and verified`). The step 1 contracts (the scout's `## Carry forward` section and the planner and builder reader rule) are committed in it, and every run used `plugin=<repo>/plugins/sdlc-lite` from this worktree.
- Throwaway project: `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.7n2YHsjnKS`, made with `mktemp -d`, outside this repository, holding `with/` and `without/`. Role logs and untruncated tool inputs (`<arm>-tools-full.txt`) are kept there, not in this repository.

## Method

[probe.sh](carry-forward-live-run/probe.sh) did everything below and wrote [scout.txt](carry-forward-live-run/scout.txt), [with.txt](carry-forward-live-run/with.txt), and [without.txt](carry-forward-live-run/without.txt). It ran once, from the repository root:

```sh
bash docs/validation/carry-forward-live-run/probe.sh
```

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

Arms, in order, one trial each, none rerun. Each ran through a subshell wrapper that unsets `CLAUDECODE`, every `CLAUDE_CODE_*` variable, and `SDLC_ROLE SDLC_BASE_SHA SDLC_TMP_WORKTREES SDLC_HEADLESS SDLC_ATTEMPT_ID SDLC_ATTEMPT_NAME SDLC_LIFECYCLE_CHILD SDLC_ROUTING_REASON SDLC_BACKEND`, then runs from the project root, as in [the plan reviewer live run](plan-reviewer-live-run.md):

```sh
cd <P>/with    && bash <repo>/plugins/sdlc-lite/scripts/run.sh scout L1 .sdlc/cf/handoff.md
cd <P>/with    && bash <repo>/plugins/sdlc-lite/scripts/run.sh planner L2 .sdlc/cf/handoff.md
cd <P>/without && bash <repo>/plugins/sdlc-lite/scripts/run.sh planner L2 .sdlc/cf/handoff.md
```

All three exited 0. Planner L2 is the planner level the Lean chain gives a size S or M ticket; the scout has only L1. In `with/` the planner's artifacts dir held `scout-L1.md`; `without/` had no scout result.

Metrics, per arm, from `<role>-<level>.log` and `.md`:

- `tool=<name> input=<...>`: one line per tool call in log order; the input is the compact JSON input, first 200 characters, trailing whitespace removed, from `jq -R -r` over `fromjson? // empty | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use")`.
- `tool_calls`: the number of tool lines.
- `tree_searches`: tool lines named Grep or Glob, plus Bash lines matching the ERE `git grep|grep -[A-Za-z]*[rR]|rg |find `.
- `symbol_searches`: the tree_searches lines that contain `pad_cell`.
- Scout only: `carry_forward_section` is yes when the result has the heading line `## Carry forward`; `carry_forward_lines` counts the non-blank lines after that heading, up to the next heading line or the end of the file.
- Planner arms only: `read_scout_result` is yes when some tool line contains `scout-L1.md`; `cites_result_path` is yes when `planner-L2.md` contains `scout-L1.md`; `copies_section` is yes when `planner-L2.md` has the heading line `## Carry forward` or contains verbatim any body line of the `with/` scout section that is 20 or more characters long after stripping surrounding whitespace and a leading `- `.

## Evidence

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

`git grep -n pad_cell` starts after character 200 of the compact JSON input, so the truncated tool line in `without.txt` holds neither it nor `find `, and the metrics record `tree_searches=0` and `symbol_searches=0`. Its plan states "Contract dependents: `git grep -n pad_cell` finds two" and the Assumptions say "verified by `git grep -n pad_cell`". Recounted over the untruncated inputs with the same ERE, the arms give scout 4 and 1, with 2 and 0, and without 1 and 1 (tree_searches and symbol_searches). So the planner with the scout result did not repeat the `pad_cell` search, and the planner without one did run it; the specified metric misses the second half because of the 200-character cut.

## Limits

- One trial per arm, on one machine and one account. Model behavior varies between runs; no arm was rerun.
- Claude Code only: Codex was not run, and its generated agents are checked only by `codex_roles.py generate --check`.
- symbol_searches is a heuristic over tool inputs. It counts search commands, not reads, and it reads only the first 200 characters of each input. In this run that cut hid the without arm's `git grep -n pad_cell`, so the specified criterion for that arm is red although the search ran.
- One small fixture: eight files and two call sites. The without planner found the callers in one compound command, so the saving the scout result buys here is one search, not a measured cost difference.
