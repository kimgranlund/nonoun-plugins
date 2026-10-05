<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Give the scout, researcher, architect, and archaeologist results a closing `## Carry forward` section of at most 15 lines, make the planner and builder read it before searching and search only what it does not answer, guard both in results.py and check.py with negative controls, regenerate the Codex agents, and record a focused live run showing a planner using a scout's carried-forward facts instead of repeating the scout's search.

## Step 1: Carry forward contracts, result schema, check.py guard, Codex agents
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets:
- `plugins/sdlc-lite/agents/scout.md`, `researcher.md`, `architect.md`, `archaeologist.md`: one new output template section.
- `plugins/sdlc-lite/agents/planner.md`: a reader paragraph.
- `plugins/sdlc-lite/agents/builder.md`: a reader sentence.
- `plugins/sdlc-lite/scripts/results.py`: `SCHEMA` and `selftest()`.
- `plugins/sdlc-lite/scripts/check.py`: a new guard and docstring item 15.
- The regenerated `plugins/sdlc-lite/adapters/codex/agents/*.toml`.

Settled decisions:
- **Producer template.** Use the same text in all four files. Append it after the current last section, with one blank line before it: the heading line `## Carry forward`, then this body line: `The facts and paths later roles must not re-derive: at most 15 lines, one fact per line, each with its path:line or source. For a complete list, such as every caller of a symbol, also name the search that produced it and its scope. "None" if nothing.`
  - Evidence: the handoff Intent ("at most 15 lines: facts and paths later roles must not re-derive") and design.md:119.
  - The "Final message, exactly these sections:" lead-in stays, so the prompt asks for the section, while the schema keeps it optional (see results.py below).
- **Planner paragraph.** Insert this exact paragraph as a new paragraph right after the line `Read the code you plan against. Do not edit anything.` (planner.md:9): `Before searching the code, read the `## Carry forward` section of each scout, researcher, architect, and archaeologist result you read, and search only what it does not answer. A carried-forward list that names a search covering the same scope answers that search, the Contract dependents search included. When a step relies on a carried-forward fact, cite the result path (for example `.sdlc/<task>/scout-L1.md`) in that step's Do instead of copying the section into the plan; the builder reads it there.`
  - Evidence: the handoff Intent ("The planner cites the result path and does not copy it", "search only what it does not answer"), design.md:57 (principle 2) and design.md:131.
  - The Contract dependents clause applies the ticket's rule where planner.md:40 would otherwise repeat the scout's `git grep`. The Contract dependents paragraph itself stays unchanged, so that rule keeps one home.
- **Builder sentence.** Append this exact sentence to builder.md's first paragraph, after "...follow it for the files it governs." (builder.md:5): `When the handoff cites a scout, researcher, architect, or archaeologist result, read that result's `## Carry forward` section before searching the code, and search only what it does not answer.`
- **Inline only in planner.md and builder.md.** There, `## Carry forward` appears only inline in backticks, never as a heading line, so neither role's own output template gains the section.
- **results.py schema.** Append `'Carry forward'` as the last entry of the `sections` tuple of `researcher`, `scout`, `archaeologist`, and `architect` in `SCHEMA` (results.py:42-49).
  - Keys stay `Answer`, `Map`, `Summary`, `Approach`.
  - Only the key section is required (results.py:9-11). A result without the section, including every result written before this ticket, still validates.
  - A `## Carry forward` that is present must follow the other declared sections present. This enforces "ends its result".
  - The planner and builder schemas do not change.
- **results.py selftest.**
  - Append `\n## Carry forward\n- x\n` to the four roles' `bodies` entries.
  - Change the expected value of the `schema prints - for a role with no allowed set` case (results.py:295) to `['scout\tMap\t-\tMap|Entry points|Not found|Carry forward']`.
  - Add a case with the exact label `a scout result without ## Carry forward passes`: `head('scout')` plus `## Map\nm\n\n## Entry points\ne\n\n## Not found\nNone\n`, expecting `None`.
  - Add a case with the exact label `a scout result with ## Carry forward before ## Map fails`: `head('scout')` plus `## Carry forward\n- x\n\n## Map\nm\n`, expecting `## Carry forward comes before ## Map`.
- **check.py guard.** Add a Carry forward guard after the Lean lane text guard (check.py:385-397), using the same pattern: a dict `CARRY_FORWARD` maps each phrase to the files that must hold it.
  - `'## Carry forward'`: agents/scout.md, agents/researcher.md, agents/architect.md, agents/archaeologist.md, agents/planner.md, agents/builder.md.
  - `'at most 15 lines'`: the four producing contracts.
  - `'search only what it does not answer'`: agents/planner.md and agents/builder.md.
  - `'cite the result path'`: agents/planner.md.
  - Error lines, exactly: `<rel>: carry-forward text missing "<phrase>"` when the phrase is absent, and `<rel>: carry-forward negative control not flagged` when `text.replace(phrase, '')` is not flagged.
  - Add docstring item `15. Carry forward:` naming those pairs. State that each pair has a negative control, and that results.SCHEMA declares `Carry forward` last for the four producing roles, so item 13 also requires the heading line there. Label the code comment `(docstring item 15)`.
- **Regenerate.** After all agent edits, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. The TOMLs embed each role body (codex_roles.py `instructions()`), so the scout, researcher, architect, archaeologist, planner, and builder TOMLs change.

Contract dependents:
- results.py:295 pins the scout schema line. It is updated in this step.
- check.py item 13 (check.py:416-429) requires every SCHEMA section as a heading line in agents/<role>.md. The four template edits satisfy it.
- `plugins/sdlc-lite/scripts/codex-selftest.py:25` writes a scout result without the section. Leave it untouched, because the section is optional. Run `python3 plugins/sdlc-lite/scripts/codex-selftest.py` as a focused check.
- `run.sh` stays untouched. It validates with `results.py validate` (run.sh:464) and picks the result by `results.py key` (run.sh:440), and no key changes. This answers the ticket's "run.sh required-section handling if affected".
- `steps.py` stays untouched. It reads results through `results.structure_error` and `key_value` only for planner, plan-reviewer, builder, and verifier.
- The seven committed producer results under `.sdlc/` must keep validating (criterion 6).
- Left untouched on purpose:
  - architect.md's read rule: the ticket gives the reader rule to the planner and builder only.
  - `docs/maintenance/sdlc-internals.md`: its results.py entry describes the schema mechanics, which do not change.
  - `docs/lean-sdlc/design.md`: a proposal record.
  - `skills/handoff-format/SKILL.md`: the layout is unchanged.

Negative controls, red before this step and green after:
- Criterion 5: an out-of-order fixture fails validate.
- Criteria 7 and 8: check.py on a plugin copy with the heading or the reader phrase removed prints the FAIL line.

The check.py guard here is this step's own checker, not a repo gate; the whole gates stay on step 2. Write no em dashes.

Depends on: none. Focused checks: `python3 plugins/sdlc-lite/scripts/results.py selftest`, `python3 plugins/sdlc-lite/scripts/check.py`, `python3 plugins/sdlc-lite/scripts/codex-selftest.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`.
### Acceptance criteria
- `for f in scout researcher architect archaeologist; do p=plugins/sdlc-lite/agents/$f.md; test "$(grep "^## " "$p" | tail -n 1)" = "## Carry forward" || exit 1; grep -qF "at most 15 lines" "$p" || exit 1; done`
- `for f in planner builder; do grep -qF "search only what it does not answer" plugins/sdlc-lite/agents/$f.md || exit 1; grep -qF "## Carry forward" plugins/sdlc-lite/agents/$f.md || exit 1; done && grep -qF "cite the result path" plugins/sdlc-lite/agents/planner.md && ! grep -qx "## Carry forward" plugins/sdlc-lite/agents/planner.md plugins/sdlc-lite/agents/builder.md`
- `for r in scout researcher architect archaeologist; do python3 plugins/sdlc-lite/scripts/results.py schema --role $r | grep -q "|Carry forward$" || exit 1; done`
- `out=$(python3 plugins/sdlc-lite/scripts/results.py selftest) && printf "%s\n" "$out" | grep -qF "ok: a scout result without ## Carry forward passes" && printf "%s\n" "$out" | grep -qF "ok: a scout result with ## Carry forward before ## Map fails"`
- `t=$(mktemp) && printf "<!-- role=scout level=L1 model=claude-haiku-4-5 effort=low -->\n## Carry forward\n- a\n\n## Map\n- b\n" > "$t" && python3 plugins/sdlc-lite/scripts/results.py validate "$t" 2>&1 | grep -qF "## Carry forward comes before ## Map"`
- (guard) `fs=$(git ls-files .sdlc | grep -E "/(scout|researcher|architect|archaeologist)-L[0-9][^/]*\.md$") && test -n "$fs" && for f in $fs; do python3 plugins/sdlc-lite/scripts/results.py validate "$f" || exit 1; done`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && python3 -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.write_text(p.read_text().replace(\"## Carry forward\", \"\"))" "$t/p/agents/scout.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/p" | grep -qF "agents/scout.md: result schema: missing ## Carry forward"`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && python3 -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.write_text(p.read_text().replace(\"search only what it does not answer\", \"\"))" "$t/p/agents/builder.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/p" | grep -qF "agents/builder.md: carry-forward text missing"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- `grep -qF "search only what it does not answer" plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml && grep -qF "cite the result path" plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l2.toml && grep -qF "## Carry forward" plugins/sdlc-lite/adapters/codex/agents/sdlc-scout-l1.toml`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/agents/(scout|researcher|architect|archaeologist|planner|builder)\.md|plugins/sdlc-lite/scripts/(results|check)\.py|plugins/sdlc-lite/adapters/codex/agents/sdlc-[a-z0-9-]+\.toml)$" | grep -q .`
- (guard) `! grep -qF "—" plugins/sdlc-lite/agents/scout.md plugins/sdlc-lite/agents/researcher.md plugins/sdlc-lite/agents/architect.md plugins/sdlc-lite/agents/archaeologist.md plugins/sdlc-lite/agents/planner.md plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/scripts/results.py plugins/sdlc-lite/scripts/check.py`

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

## Assumptions
- This is a replan of step 2 only. Step 1's block is the text of `.sdlc/0202-carry-forward/planner-L3.md`, verbatim: verified by extracting it with `awk '/^## Step 1:/,/^## Step 2:/'` from that file and diffing it against this plan's step 1 (identical).
- Step 1 is built, verified, and committed: verified by `step-1/verifier-L2.md` (Verdict pass) and commit 8433d80 in `git log`.
- The first step 2 build's files are committed in 057ae64: probe.sh, the three run 1 evidence files, the report, and the README line. Verified by `git show --stat 057ae64`. The new attempt's `SDLC_BASE_SHA` (HEAD at its first builder run) therefore comes after them, so the scope guard sees only this attempt's changes.
- Step 2 stays at L3: the level-rubric says a builder block tagged `plan defect:` goes to replan and does not count toward a bump.
- Run 1's logs are kept at `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/carry-forward-probe.7n2YHsjnKS`, under `with/.sdlc/cf/` and `without/.sdlc/cf/`: verified by `ls`.
- The defect is as the handoff states. Run 1's without arm, call 2, is a 405-character tool line, and its `git grep -n pad_cell` sits past character 200: verified by `awk '{print length($0)}'` over `without-tools-full.txt` in that dir. The same call's description, `Read source files and find pad_cell callers`, matches the ERE's `find `: verified in the same file.
- The settled metric recounts run 1 as scout 4 and 1, with 2 and 0, and without 2 and 1. Criteria 1, 2, 3, and 5 all pass on that recount. Verified at plan time with a throwaway prototype of the probe.sh change, not kept: its `--evidence-only` mode on run 1's dir, then each criterion's command over the output files, each rc 0.
- Criterion 4 is red at HEAD for the right reason: probe.sh has no `--evidence-only`. Its leading `grep -qF` returns 1, so it never launches the probe. It is green on that throwaway prototype (rc 0). With the current metric's functions (probe.sh lines 85-93) on the same fixture, it prints `tree_searches=2` and `symbol_searches=2`, so it is red (rc 1). The fixture therefore separates the old metric from the new by its numbers alone.
- Probe of step 2's criteria on the current tree:
  - Red (rc 1), each for the right reason: 3 (`symbol_searches=0` in without.txt), 4 (no `--evidence-only`), 5 (scout.txt has `tree_searches=4` and no `search=` lines), 7 (no Run headings), and 9 (the README line differs).
  - Green (rc 0): guards 1, 2, 6, 8, and 10 to 16.
- Each guard's red form was observed:
  - a scout.txt fixture with `carry_forward_lines=16`: criterion 1 rc 1;
  - a with.txt fixture with `symbol_searches=1`: criterion 2 rc 1;
  - a file without `arm=with`: rc 1;
  - the report without `## Limits`: rc 1;
  - the scope filter on an extra path `docs/other.md`: un-negated rc 0;
  - an em dash fixture: un-negated rc 0.
  The gate guards are unchanged from the reviewed plan, whose red forms were observed then (check.py on a plugin copy).
- Criteria 7 and 9 pass when their target holds: verified on a copy of the report with both Run headings added (rc 0) and on a copy of docs/README.md with the line replaced (rc 0).
- The guards leave the work tree as it was, so the snapshot check in `steps.py split --only 2` passes: verified by `git status --short` after the probe run, which showed only `.sdlc/0202-carry-forward/planner-L3-2.attempt.json`.
- `bash plugins/sdlc-lite/scripts/check.sh` passes in 232 seconds on this host (rc 0, ends `ok: plugin validate`; shellcheck skipped, not installed). `check-packaging.py`, `generate --check`, `tickets.py --root .sdlc check` (`ok: 208 tickets, roadmap current`), and `git diff --check` are rc 0.
- The verifier's disk-scan hook allows every criterion span: verified by feeding each span as `tool_input` JSON to `plugins/sdlc-lite/hooks/block-disk-scan.sh` with `SDLC_ROLE=verifier` (rc 0 each). A whole-filesystem search control was blocked (rc 2).
- `steps.py lint` accepts the plan: verified on this draft in a temp git repo with a stub `plugins/sdlc-lite/AGENTS.md` (`steps lint: ok`). `results.py validate` passes it.
- A builder can launch the nested scout and planner runs through probe.sh's wrapper: verified by run 1, where all three exited 0.

## Risks
- Run 2 is a new trial, and model behavior varies. Criterion 2 or 3 goes red, and the step blocks with honest evidence and no run 3, if:
  - the with planner runs a `pad_cell` tree search;
  - the without planner finds the callers with a search the ERE misses, such as a non-recursive `grep -n pad_cell lib/*/*.sh`; or
  - the scout writes no section.
  The choice then is the user's: accept run 1's full-input recount, or change the contract wording.
- The metric stays a heuristic. Splitting on `;` does not respect quotes. It can split a quoted string but never joins two commands, so a split can only lose a search whose symbol sits in a different element.
- `check.sh` took 232 seconds, close to the 300-second default `--guard-timeout` of `steps.py split --only 2`. On a loaded host that guard can time out; rerun the split with `--guard-timeout 600`.
- Run 1's log dir is under the OS temp dir, and macOS may clean it. The builder then keeps the report's earlier recount, as the Do settles.
- Criterion 4 leaves its `mktemp -d` fixture dirs behind, outside the repository.
- Unchanged from the first plan:
  - Codex is not live-tested; only `generate --check` covers it.
  - planner.md and builder.md are shared with other lean-SDLC rows, so never run those in parallel lanes.
  - `check.sh` has host-dependent pieces (`claude plugin validate`; shellcheck skipped here).
  - Step 1's guard over the committed producer results reads files other lanes can add.
