## Task goal
Add a `## Carry forward` section to the scout, researcher, architect, and archaeologist results and the reader rule to planner and builder.

## Step 2: Focused live run, report, and gates green
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
This is a replan of step 2. Its first build blocked on a plan defect (`.sdlc/0202-carry-forward/step-2.superseded-1/builder-L3.md`). The `symbol_searches` metric read only the first 200 characters of each tool input, so the without planner's `git grep -n pad_cell`, past character 200 of its second Bash call, was not counted.

The first build's files are committed and are reused, not rewritten from scratch: `docs/reports/carry-forward-live-run/probe.sh`, the three evidence files of run 1 (`scout.txt`, `with.txt`, `without.txt`), `docs/reports/carry-forward-live-run.md`, and the carry forward line in `docs/README.md`. This step changes what the metric measures, adds an evidence-only mode as the metric's negative control, reruns the three arms once (run 2), and updates the report and the README line. No threshold changes: criterion 3 is the earlier criterion, word for word.

Targets:
- `docs/reports/carry-forward-live-run/probe.sh`: changed.
- `docs/reports/carry-forward-live-run/scout.txt`, `with.txt`, `without.txt`: rewritten by run 2.
- `docs/reports/carry-forward-live-run.md`: updated.
- `docs/README.md`: the existing `(validation/carry-forward-live-run.md)` line replaced; no other line changes.

**probe.sh changes**

Everything not listed here stays as built: the fixture, the handoff, the `role_run` wrapper, the arm order, and every other evidence line and its definition.
1. Arguments. With no argument, probe.sh does the full run as now.
   - `bash docs/reports/carry-forward-live-run/probe.sh --evidence-only <project dir> <out dir>` sets `P=<project dir>` and `OUT=<out dir>` and runs `mkdir -p "$OUT"`.
   - It makes no temp dir, builds no fixture, and runs no role. It computes the three arms' evidence from `$P/with` and `$P/without` exactly as a full run does, writes only `$OUT/scout.txt`, `$OUT/with.txt`, and `$OUT/without.txt`, and exits 0.
   - `--evidence-only` with any other argument count prints a usage line on stderr and exits 2.
   - A missing or empty log or result gives zero tool lines and the `no` values. That is not an error.
   - Why: it is the negative control for the metric change (criterion 4), and it recounts run 1 from its kept logs without a model call.
2. Tool lines: `tool=<name> input=<compact JSON input, trailing whitespace removed>`, with no cut. Drop `.[0:200]`.
3. Search lines. Read them from the log, not from the tool lines. Print them in log order, after all tool lines and before `tool_calls=`:
   - Each Grep or Glob tool call gives `search=<name> <compact JSON input>`.
   - Each Bash tool call: take the full `.input.command` string, never `.input.description`. Split it into command-list elements on newline, `;`, `&&`, and `||`; a pipeline stays whole. Trim surrounding whitespace, and keep each element that matches the ERE `git grep|grep -[A-Za-z]*[rR]|rg |find ` as `search=Bash <the element as a JSON string>`, for example `search=Bash "git grep -n pad_cell"`.
4. `tree_searches=<the number of search= lines>` and `symbol_searches=<the number of search= lines that contain pad_cell>`.
5. Drop the `$P/<arm>-tools-full.txt` dump, because the tool lines are now untruncated.
6. Update the header comment to show both invocations.

Reference jq for item 3, as run with `jq -R -r -f <file> <log>` on this host:
```
fromjson? // empty | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use")
  | if .name=="Grep" or .name=="Glob" then "search=\(.name) \(.input|tojson)"
    elif .name=="Bash" then ((.input.command // "") | [splits("\n|;|&&|\\|\\|")] | .[]
      | sub("^\\s+"; "") | sub("\\s+$"; "")
      | select(test("git grep|grep -[A-Za-z]*[rR]|rg |find ")) | "search=Bash \(tojson)")
    else empty end
```

Evidence that settled items 2 to 4:
- The description is excluded because run 1's without arm, call 2, has the description `Read source files and find pad_cell callers`. That text matches the ERE's `find `, but it is model prose, not a command.
- The unit is a command-list element because run 1's with arm ran `find . -name AGENTS.md` in calls 2 and 3 and criterion probes naming `pad_cell` (`. lib/text/pad.sh; pad_cell ab 4 .`) in calls 4 and 5. Per-call counting would count one call that batched both as a `pad_cell` search.
- The reference jq over run 1's kept logs gives scout 4 and 1, with 2 and 0, and without 2 and 1 (tree_searches and symbol_searches). On that recount every evidence criterion below holds.
- A throwaway prototype of items 1 to 5, built and run at plan time and not kept, passed criterion 4. The current metric gives 2 and 2 on criterion 4's fixture, so that criterion fails it.

**Order of work**
1. Edit probe.sh. Run `bash -n` on it, then criterion 4, before any model call.
2. Recount run 1. If `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.7n2YHsjnKS` still exists, run `bash docs/reports/carry-forward-live-run/probe.sh --evidence-only <that dir> "$(mktemp -d)"`. Keep each arm's `tree_searches`, `symbol_searches`, and `search=` lines for the report's Run 1 section. If the dir is gone, say so in that section and keep the recount the report already holds.
3. Run 2. Run `bash docs/reports/carry-forward-live-run/probe.sh` once, in the foreground, with the Bash timeout at 3600000.
   - It overwrites run 1's evidence files. Run 1 stays in git history and in the report.
   - The rerun is the conductor's decision: the handoff's `## Plan review` entry says "rerun the arms". It also keeps the evidence files produced end to end by the committed probe.sh. On the full-input recount, run 1 already met every evidence criterion, so run 2 is not taken to change an outcome.
   - There is no run 3, whatever run 2 shows.
4. Failure handling is unchanged. If criterion 1, 2, or 3 fails on model behavior, do not edit any contract or the metric, and do not rerun. Set Status blocked and quote the evidence lines in Notes. The report and the README line state the actual outcome.
5. Update the report and the README line, as below.
6. Run every gate. Fix any red that step 1 introduced, and only in step 1's files, which the scope guard allows. Write no em dashes.

**Report `docs/reports/carry-forward-live-run.md`**
Keep the title and the precedent of `docs/reports/role-result-schema-live-run.md`.
- The `Recorded: <date>. Live run for ticket T-0202: ...` line and the outcome paragraph describe run 2's actual result, with one sentence on run 1.
- `## Environment`:
  - Run 2: the date, `sw_vers` or `uname -r`, `claude --version`, the `model=` lines and result headers, `git rev-parse HEAD` with a note that the step 1 contracts are in it, and the project path, which is the `project=` value of `with.txt` without the trailing `/with`.
  - Run 1: its project path and commit, as the report states them now.
  - Remove the `<arm>-tools-full.txt` mention.
- `## Method`:
  - The fixture, the arms, and the commands, as now.
  - Run 1 cut each tool input at 200 characters. Run 2 used the full input.
  - The metric definitions of items 2 to 4 above.
  - The `--evidence-only` mode, and criterion 4's fixture described in prose.
- `## Evidence` holds two subsections, with these exact heading lines:
  - `### Run 1: 200-character metric`: the existing table, the scout text, the recount paragraph, and the step 2 recount output, if any.
  - `### Run 2: full-input metric`: one table with columns arm, tool_calls, tree_searches, symbol_searches, read_scout_result, cites_result_path, copies_section; the scout's carried-forward text, verbatim; and each arm's `search=` lines.
- `## Limits`:
  - Two runs, one trial per arm in each. The criteria read run 2. The reason for the rerun, as in order-of-work item 3.
  - Claude Code only: Codex was not run, and its generated agents are checked only by `codex_roles.py generate --check`.
  - The metric is a heuristic. The ERE misses a non-recursive grep over globs, such as `grep -n pad_cell lib/*/*.sh`, and a search split across command-list elements.
  - One small fixture.

**docs/README.md**
Replace the existing carry forward line in place. When run 2 meets criteria 1, 2, and 3, the line is exactly: `- [Carry forward live run](validation/carry-forward-live-run.md): dated live run for T-0202 in which a planner given a scout result with a Carry forward section read it, cited its path, and did not repeat the scout's search, while a planner given no scout result ran that search.` Otherwise the line states the actual outcome.

Raw logs stay out of the repository (`*.log` is in `.gitignore`), in the printed project dir.

Criteria 1 and 2 are tagged `(guard)` by rule 1's definition. Run 1's committed evidence files already satisfy them, run 2 rewrites those files, and both must still hold afterwards.

Depends on: step 1, which is committed and verified (`.sdlc/0202-carry-forward/step-1/verifier-L2.md`).
### Acceptance criteria
- (guard) `f=docs/reports/carry-forward-live-run/scout.txt && grep -qx "carry_forward_section=yes" "$f" && awk -F= '$1=="carry_forward_lines" && $2>=1 && $2<=15 {ok=1} END {exit !ok}' "$f"`
- (guard) `f=docs/reports/carry-forward-live-run/with.txt && grep -qx "read_scout_result=yes" "$f" && grep -qx "cites_result_path=yes" "$f" && grep -qx "copies_section=no" "$f" && grep -qx "symbol_searches=0" "$f"`
- `awk -F= '$1=="symbol_searches" && $2>=1 {ok=1} END {exit !ok}' docs/reports/carry-forward-live-run/without.txt`
- `f=docs/reports/carry-forward-live-run/probe.sh && grep -qF -- "--evidence-only" "$f" && d=$(mktemp -d) && mkdir -p "$d/p/with/.sdlc/cf" "$d/p/without/.sdlc/cf" && touch "$d/p/with/.sdlc/cf/scout-L1.log" "$d/p/with/.sdlc/cf/scout-L1.md" "$d/p/with/.sdlc/cf/planner-L2.log" "$d/p/with/.sdlc/cf/planner-L2.md" "$d/p/without/.sdlc/cf/planner-L2.md" && c="cat lib/text/pad.sh # $(printf "%05000d" 0); git grep -n pad_cell" && for x in "cat lib/text/pad.sh" "$c" "find . -name AGENTS.md; . lib/text/pad.sh; pad_cell ab 4 ."; do jq -cn --arg c "$x" '{type:"assistant",message:{model:"m",content:[{type:"tool_use",name:"Bash",input:{command:$c,description:"git grep the pad_cell callers"}}]}}' || exit 1; done > "$d/p/without/.sdlc/cf/planner-L2.log" && bash "$f" --evidence-only "$d/p" "$d/o" && w="$d/o/without.txt" && grep -qx "tree_searches=2" "$w" && grep -qx "symbol_searches=1" "$w" && grep -qx 'search=Bash "git grep -n pad_cell"' "$w" && grep -q "^tool=Bash input=.*git grep -n pad_cell" "$w"`
- `for a in scout with without; do f=docs/reports/carry-forward-live-run/$a.txt; t=$(grep -c "^search=" "$f"); s=$(grep "^search=" "$f" | grep -c pad_cell); grep -qx "tree_searches=$t" "$f" || exit 1; grep -qx "symbol_searches=$s" "$f" || exit 1; done`
- (guard) `bash -n docs/reports/carry-forward-live-run/probe.sh && for a in scout with without; do f=docs/reports/carry-forward-live-run/$a.txt; grep -qx "arm=$a" "$f" || exit 1; grep -q "^tool=" "$f" || exit 1; done`
- `f=docs/reports/carry-forward-live-run.md && grep -qx "### Run 1: 200-character metric" "$f" && grep -qx "### Run 2: full-input metric" "$f" && p=$(sed -n "s|^project=\(.*\)/with$|\1|p" docs/reports/carry-forward-live-run/with.txt) && test -n "$p" && grep -qF "$p" "$f"`
- (guard) `f=docs/reports/carry-forward-live-run.md && grep -qx "## Environment" "$f" && grep -qx "## Method" "$f" && grep -qx "## Evidence" "$f" && grep -qx "## Limits" "$f" && grep -qF "T-0202" "$f" && grep -qF "(validation/carry-forward-live-run.md)" docs/README.md`
- `grep -qxF -- "- [Carry forward live run](validation/carry-forward-live-run.md): dated live run for T-0202 in which a planner given a scout result with a Carry forward section read it, cited its path, and did not repeat the scout's search, while a planner given no scout result ran that search." docs/README.md && test "$(grep -c "(validation/carry-forward-live-run.md)" docs/README.md)" -eq 1`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(docs/reports/carry-forward-live-run\.md|docs/reports/carry-forward-live-run/(probe\.sh|scout\.txt|with\.txt|without\.txt)|docs/README\.md|plugins/sdlc-lite/agents/(scout|researcher|architect|archaeologist|planner|builder)\.md|plugins/sdlc-lite/scripts/(results|check)\.py|plugins/sdlc-lite/adapters/codex/agents/sdlc-[a-z0-9-]+\.toml)$" | grep -q .`
- (guard) `! grep -qsF "—" docs/reports/carry-forward-live-run.md docs/reports/carry-forward-live-run/probe.sh docs/README.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
