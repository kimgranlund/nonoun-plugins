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
New files:
- `docs/validation/carry-forward-live-run/probe.sh`.
- `docs/validation/carry-forward-live-run/scout.txt`, `with.txt`, and `without.txt`, all written by probe.sh.
- `docs/validation/carry-forward-live-run.md`.

Changed: `docs/README.md` (one index line).

**probe.sh setup**
- Run it as `bash docs/validation/carry-forward-live-run/probe.sh` from the repository root.
- It sets `R=$(git rev-parse --show-toplevel)`, `RUN=$R/plugins/sdlc-lite/scripts/run.sh`, and `OUT=$R/docs/validation/carry-forward-live-run`.
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
  - Precedent: the Method section of `docs/validation/plan-reviewer-live-run.md`.
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

**Report `docs/validation/carry-forward-live-run.md`**
Follow the precedent of `docs/validation/role-result-schema-live-run.md`. Start with the title `# Carry forward live run` and a `Recorded: <date>. Live run for ticket T-0202: ...` line. Then:
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
- `f=docs/validation/carry-forward-live-run/scout.txt && grep -qx "carry_forward_section=yes" "$f" && awk -F= '$1=="carry_forward_lines" && $2>=1 && $2<=15 {ok=1} END {exit !ok}' "$f"`
- `f=docs/validation/carry-forward-live-run/with.txt && grep -qx "read_scout_result=yes" "$f" && grep -qx "cites_result_path=yes" "$f" && grep -qx "copies_section=no" "$f" && grep -qx "symbol_searches=0" "$f"`
- `awk -F= '$1=="symbol_searches" && $2>=1 {ok=1} END {exit !ok}' docs/validation/carry-forward-live-run/without.txt`
- `bash -n docs/validation/carry-forward-live-run/probe.sh && for a in scout with without; do f=docs/validation/carry-forward-live-run/$a.txt; grep -qx "arm=$a" "$f" || exit 1; grep -q "^tool=" "$f" || exit 1; done`
- `f=docs/validation/carry-forward-live-run.md && grep -qx "## Environment" "$f" && grep -qx "## Method" "$f" && grep -qx "## Evidence" "$f" && grep -qx "## Limits" "$f" && grep -qF "T-0202" "$f" && grep -qF "(validation/carry-forward-live-run.md)" docs/README.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(docs/validation/carry-forward-live-run\.md|docs/validation/carry-forward-live-run/(probe\.sh|scout\.txt|with\.txt|without\.txt)|docs/README\.md|plugins/sdlc-lite/agents/(scout|researcher|architect|archaeologist|planner|builder)\.md|plugins/sdlc-lite/scripts/(results|check)\.py|plugins/sdlc-lite/adapters/codex/agents/sdlc-[a-z0-9-]+\.toml)$" | grep -q .`
- (guard) `! grep -qsF "—" docs/validation/carry-forward-live-run.md docs/validation/carry-forward-live-run/probe.sh docs/README.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`

## Assumptions
- A result needs only its key section, undeclared headings are ignored, and the declared sections that are present must keep declared order: verified by results.py:7-13 and `_check`. At HEAD a scout result with `## Carry forward` first still validates (probe of criterion 5, rc 1).
- check.py item 13 requires each SCHEMA section as a heading line in agents/<role>.md and prints `FAIL agents/<role>.md: result schema: missing ## <Section>`: verified by check.py:416-429 and a probe on a plugin copy with `## Map` renamed, which printed `FAIL agents/scout.md: result schema: missing ## Map` (rc 1).
- check.py takes a plugin root argument and imports that root's results.py: verified by check.py:56 and 352-353, and by the copy probes above.
- run.sh needs no change: verified by run.sh:440 (`results.py key`) and run.sh:464 (`results.py validate`). No key section changes.
- steps.py needs no change: verified by steps.py:895-900, 1041-1050, 1081, and 1112. It reads only planner, plan-reviewer, builder, and verifier results through results.py.
- The seven committed producer results under `.sdlc/` validate at HEAD, and none has a `## Carry forward` heading: verified by the criterion 6 probe (rc 0) and `grep -c "^## Carry forward"` (0 for each).
- results.py:295 is the only selftest that pins a producer's full section list: verified by `git grep -n "Entry points"`. codex-selftest.py:25's scout fixture lacks the section and stays valid, because only the key is required.
- The generated Codex TOMLs embed each role body: verified by codex_roles.py `instructions()`, and by `grep -l` listing sdlc-builder-l1 to l5 for the builder body and sdlc-planner-l1 to l3 for the planner body.
- The phrases `at most 15 lines`, `search only what it does not answer`, `cite the result path`, and `Carry forward` appear in no file under agents, scripts, adapters, or docs/maintenance at HEAD: verified by grep (no hits). The new guard therefore bites.
- Probe results on the current tree: step 1 criteria 1-5, 7, 8, and 10 are red (rc 1), and guards 6, 9, 11, and 12 are green. Each guard's red form was observed:
  - a headerless result fails the criterion 6 loop;
  - a renamed `## Map` fails check.py;
  - an extra path trips the scope filter;
  - an em dash fixture trips the grep.
- Step 2's new-behavior criteria are red at HEAD only because the evidence files do not exist yet. The awk forms return 0 for `symbol_searches=2`, 1 for `symbol_searches=0`, and 1 for `carry_forward_lines=16` on fixtures.
- All gates are green at HEAD dd14392: verified by running each one:
  - `check.sh`: rc 0, ends `ok: plugin validate`; shellcheck skipped, not installed;
  - `check-packaging.py`: PASS;
  - `generate --check`: rc 0;
  - `tickets.py --root .sdlc check`: `ok: 208 tickets, roadmap current`;
  - `git diff --check`: rc 0.
- No file this plan touches holds an em dash at HEAD: verified by grep (rc 1).
- The conductor commits each verified step, so step 2's `SDLC_BASE_SHA` comes after step 1's work: verified by commit de46ba6 (`.sdlc/0194-lean-lane-text step-1: built and verified`).
- A builder can launch nested run.sh roles in a throwaway project through a wrapper that clears session variables: verified by the Method sections of docs/validation/plan-reviewer-live-run.md and docs/validation/role-result-schema-live-run.md.
- The jq tool-call extraction works on this host's stream-json logs: verified on `.sdlc/0202-carry-forward/planner-L3.log`, which printed `tool=Bash input={"command":...}` and `tool=Read input={"file_path":...}` lines. `claude --version` is 2.1.286.
- The fixture behaves as written: verified in a temp dir. `bash tests/pad_test.sh` printed `ok`, `bash bin/table.sh a bc` printed `|a       |bc      |`, and `grep -rn pad_cell .` found the definition, the one caller, and the test.
- The ticket asks for one focused live run and names no Codex run: verified by the handoff Intent and Done when. Codex parity is checked structurally by `codex_roles.py generate --check`, and the report records Codex as not run.
- The Contract dependents clause applies the ticket's own rule ("search only what it does not answer") and adds no new rule: verified by the handoff Intent, design.md:57, and design.md:119. Without the clause, planner.md:40 would require a `git grep` that repeats the scout's search.
- `steps.py lint` accepts these criterion spans: verified by linting a draft of both steps' criteria in a temp git repo (`steps lint: ok`).

## Risks
- The live run is one trial per arm, and model behavior varies. If arm with greps for `pad_cell` or skips the scout result, step 2 blocks. The fix is a replan of step 1's wording, not a rerun.
- `symbol_searches` is a heuristic. A planner criterion probe that runs a tree grep for `pad_cell` (for example to check callers) counts as a repeated search, which is a false positive the verifier must judge from the quoted tool lines.
- The Contract dependents clause trusts a producer's list in place of the planner's own `git grep`. A scout (Haiku) can miss a fixture or snapshot dependent. The mitigation is that the list must name its search and scope, and only a search covering the same scope counts as answered.
- Declaring `Carry forward` last makes a producer that writes it before another declared section fail `run.sh` with exit 3, a new failure mode. The template puts it last, but the live run exercises only the scout.
- Codex behavior is not live-tested; only the generated agents' freshness is checked.
- planner.md and builder.md are also written by other lean-SDLC rows (T-0201 anchor rule, T-0200 plan-merge). Per the handoff, never run them in parallel lanes with this ticket.
- `check.sh` includes host-dependent pieces (`claude plugin validate`; shellcheck is skipped here). A host without the `claude` CLI turns the gates guard red for reasons unrelated to this change.
- Criterion 6 of step 1 reads committed producer results at run time. A lane that commits an invalid producer result would turn it red for reasons outside this step.
