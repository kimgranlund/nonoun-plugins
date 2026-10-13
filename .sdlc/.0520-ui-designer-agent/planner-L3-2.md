<!-- role=planner level=L3 model=opus effort=high -->
## Goal
Add a `ui-designer` pipeline role (modes plan, review, generate; Claude L1 opus medium and L2 opus high; Codex L1 and L2 gpt-6.1-sol medium and high) wired like the existing roles, with its table rows locked by an eval and its three modes proven by one live run each.

## Step 1: Wire the ui-designer role and lock its table rows
level: L3
guard timeout: 600
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/AGENTS.md`
- `docs/references/AGENTS.md`
- `docs/reports/AGENTS.md`
- `.sdlc/evals/AGENTS.md`
### Do
Depends on: none.

Settled decisions (do not reopen):
- One role with a mode, holding the builder's write allowances. Evidence: every write gate keys on the role name, never on a handoff line (`plugins/sdlc-lite/hooks/_role.sh:19-23`, `plugins/sdlc-lite/hooks/block-role-write.sh:14`, `plugins/sdlc-lite/scripts/claude_roles.py:46`, `plugins/sdlc-lite/scripts/run.sh:414`, `plugins/sdlc-lite/scripts/codex_roles.py:165`), so a per-mode gate would need a new mechanism the handoff does not ask for. The rule that plan and review never edit is held by the role contract and by the check.py item below, not by a hook.
- Mode comes from one handoff line: `mode: plan`, `mode: review`, or `mode: generate`. A missing or unknown mode returns the key section with first line `blocked: <the exact question>` and the other sections `None`.
- Result schema: key section `Mode`; allowed tokens `plan`, `review`, `generate`, and `blocked` (regex `blocked: .+`, display `blocked: <question>`, the same shape as `_INHERITED` in `results.py`); declared sections in order `Mode`, `Decisions`, `Findings`, `Changes`, `Context used`, `Carry forward`.
- One-shot role: `ui-designer` joins `PRUNE_ROLES` (a failed generate run is dispatched again, not resumed).
- No new skill, no `/chain` route, no change to `agents/planner.md`, `agents/builder.md`, `agents/verifier.md`, `skills/chain/SKILL.md`, `skills/handoff-format/SKILL.md`, or `docs/specs/sdlc-lite/design.md` (lines 119 and 124 list the roles the planner reads; planner intake of a ui-designer result is a follow-up ticket, see Risks).

Targets:
1. `plugins/sdlc-lite/agents/ui-designer.md` (create), modeled on `plugins/sdlc-lite/agents/architect.md`.
   - Front matter: `name: ui-designer` and a one-line double-quoted `description` (use for plan, review, or generate of semantic DOM and CSS that follows the project's design system; NOT for framework-specific code generation, visual regression tooling, or a non-UI plan step); no `skills:` list.
   - `## Brief`: handoff, artifacts dir, result path, cannot ask the user, the three `mode:` lines, the blocked rule, a Resume line.
   - `## Modes`: plan is a DOM and CSS structure with reasons before any build, no edits; review is findings tied to file:line, never rewrites, no edits; generate writes the markup and CSS in the tree. Include the sentence `Generate is the only mode that edits.` No commits, never push.
   - `## Method`: find the design system first (tokens file, theme, component library, existing CSS conventions) and follow it; a deviation is stated with a reason. Then two passes named `Inside out` and `Outside in` with the content of the handoff's fourth Do bullet.
   - `## Output`: the standard final-message paragraph and the `results.py validate <file> --role ui-designer` line, then the six schema sections as `## ` headings in order. `## Context used` lists each design-system and peer file read, with its path. `## Carry forward` uses the architect's text, including `at most 15 lines`.
2. `plugins/sdlc-lite/scripts/results.py`: the `SCHEMA` entry above, the docstring, and selftest: a `bodies` entry, the role-count case renamed to eleven, and cases titled `a missing ui-designer Mode fails`, `ui-designer rejects maybe`, and `ui-designer accepts blocked: <question>`.
3. Tables.
   - `plugins/sdlc-lite/adapters/claude/levels.json`: `ui-designer` L1 `["opus", "medium"]`, L2 `["opus", "high"]`.
   - `plugins/sdlc-lite/adapters/codex/models.json`: `ui-designer` L1 `["gpt-6.1-sol", "medium"]`, L2 `["gpt-6.1-sol", "high"]`.
   - `plugins/sdlc-lite/scripts/run.sh`: the two `ui-designer:L<n>)` case rows; keep `ui-designer` out of the `read_only` case at line 414.
4. `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: a `## ui-designer (L1 to L2)` section after the researcher section, same table shape. Rows: L1 `Opus medium`, fits one component or one surface inside a design system the repo already has, or a review; L2 `Opus high`, fits a page or several components, a new pattern, or no design system found. One line under it: the mode comes from the handoff's `mode:` line and generate is the only mode that edits.
5. Generators.
   - `plugins/sdlc-lite/scripts/claude_roles.py`: add `ui-designer` to `WRITERS` and to the docstring sentence about `disallowedTools`.
   - `plugins/sdlc-lite/scripts/codex_roles.py:165`: add `ui-designer` to the `workspace-write` tuple.
   - `plugins/sdlc-lite/scripts/codex-selftest.py`: one assertion that `sdlc-ui-designer-l1` has `sandbox_mode` `workspace-write`.
   - Then run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`; never edit a generated file.
6. Hooks.
   - `plugins/sdlc-lite/hooks/_role.sh`: add `ui-designer` to `SDLC_PIPELINE_ROLES` only (not `SDLC_READONLY_ROLES`) and update the comment.
   - `plugins/sdlc-lite/hooks/block-role-spawn.sh`: add `ui-designer` to `re_bare`.
   - `plugins/sdlc-lite/scripts/hook-selftest.sh`: a bare-spawn denial case, a `_role.sh` resolver case for `ui-designer-L1`, and `sdlc-lite:ui-designer-L1` Edit and Write cases in the not-restricted loop.
7. `plugins/sdlc-lite/scripts/dispatch.py`: `ui-designer` in `PRUNE_ROLES` (line 156) and in the docstring list (line 109). The selftest loop at `PRUNE_ROLES + ('builder',)` then covers it, and the `pf8` handoff on the `--prune turns a builder on` line moves to the builder's new index.
8. `plugins/sdlc-lite/scripts/check.py`.
   - Add `agents/ui-designer.md` to `CF_PRODUCERS` and reword docstring item 17 (five producing contracts).
   - Add one new numbered docstring item with a `docstring item N` comment (item 23 checks the numbering): `agents/ui-designer.md` names `mode: plan`, `mode: review`, `mode: generate`, `Inside out`, `Outside in`, and `only mode that edits`; `ui-designer` is in `claude_roles.WRITERS` and absent from the `SDLC_READONLY_ROLES` line of `hooks/_role.sh`.
   - Each phrase and the writer agreement gets a built-in negative control, as items 14 and 17 do.
9. `plugins/sdlc-lite/skills/agent/SKILL.md` (item 25 requires every role stem in backticks): name `ui-designer` in the description and the `<agent>` row, add a table row (dispatch `ui-designer` at `<level>` on a handoff that holds a `mode:` line; Codex `scripts/run.sh ui-designer <level> <handoff>`; default L1), and make workflow step 4 cover it.
10. Prose lists found by `git grep -n -E "scout, researcher|architect, archaeologist|architect\|archaeologist" -- . ":(exclude).sdlc" ":(exclude)docs/reports"`.
    - Update `plugins/sdlc-lite/agents/conductor.md:40` (prune list) and `docs/references/sdlc-internals.md:31` and `:214`.
    - Update `docs/references/codex-role-execution.md:25` (28 definitions become 30, 24 base become 26) and any role list in `docs/references/claude-hooks.md`.
11. `docs/reports/2026-10-13-ui-designer-role.md` (create), linked from `docs/README.md` if `docs_check.py` asks: `Recorded: 2026-10-13`, `## Decision` (the four rows are the user's stated choices of 2026-10-13 in T-0520, no experiment), `## Wiring` (the one-role decision above with its evidence), `## Not proven` (live behavior; the live-run report lands in step 2).
12. Eval and lock, last.
    - Run `python3 plugins/sdlc-lite/scripts/evals.py add ui-designer-role --role ui-designer --level all --model all --effort all --host all --task-set "user decision 2026-10-13, new role rows, no experiment" --pass-rate 0/0 --cost-usd unknown --date 2026-10-14 --evidence docs/reports/2026-10-13-ui-designer-role.md --method <text> --result <text>`.
    - Then run `python3 plugins/sdlc-lite/scripts/evals.py lock --eval .sdlc/evals/<the file add printed>`.
    - The date is 2026-10-14 because the locked eval `.sdlc/evals/0009-model-batch-roles.md` is dated 2026-10-14 and a replacement must not be earlier (`evals.py:276`, same date with a higher number passes). State the real decision date in Method.
    - Never edit `table-lock.json` by hand.

Validation scope: the criteria below. The dependents are the selftests of every script and hook this step edits. The full `check.sh` belongs to step 2.
### Acceptance criteria
- (red) The result schema holds the role: `python3 -c "import sys;sys.path.insert(0,'plugins/sdlc-lite/scripts');import results;s=results.SCHEMA['ui-designer'];assert s['key']=='Mode' and s['sections']==('Mode','Decisions','Findings','Changes','Context used','Carry forward') and [a[0] for a in s['allowed']]==['plan','review','generate','blocked']"`
- Negative control, the schema rejects a result with no key section: `out=$(python3 plugins/sdlc-lite/scripts/results.py selftest 2>&1) && printf '%s\n' "$out" | grep -qF 'ok: a missing ui-designer Mode fails'`
- (red) Both tables hold the user's rows: `python3 -c "import json;a=json.load(open('plugins/sdlc-lite/adapters/claude/levels.json'));b=json.load(open('plugins/sdlc-lite/adapters/codex/models.json'));assert a['ui-designer']=={'L1':['opus','medium'],'L2':['opus','high']};assert b['ui-designer']=={'L1':['gpt-6.1-sol','medium'],'L2':['gpt-6.1-sol','high']}"`
- (red) The role file names the three modes, both passes, and the edit rule: `for p in 'mode: plan' 'mode: review' 'mode: generate' 'Inside out' 'Outside in' '## Context used' 'only mode that edits'; do grep -qF "$p" plugins/sdlc-lite/agents/ui-designer.md || exit 1; done`
- Generated definitions are current on both hosts and give the role write access: `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check && python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check && grep -qx 'effort: high' plugins/sdlc-lite/agents/ui-designer-L2.md && ! grep -q '^disallowedTools:' plugins/sdlc-lite/agents/ui-designer-L1.md && grep -qF 'sandbox_mode = "workspace-write"' plugins/sdlc-lite/adapters/codex/agents/sdlc-ui-designer-l1.toml`
- (red) A conductor session cannot spawn the bare role name: `printf '%s' '{"tool_name":"Agent","agent_type":"sdlc-lite:conductor","tool_input":{"subagent_type":"ui-designer","name":"x"}}' | env -u SDLC_ROLE bash plugins/sdlc-lite/hooks/block-role-spawn.sh 2>/dev/null; test $? -eq 2`
- (guard) The write gate lets the role edit: `printf '%s' '{"tool_name":"Edit","agent_type":"sdlc-lite:ui-designer-L1","tool_input":{"file_path":"/x/a.css"}}' | env -u SDLC_ROLE bash plugins/sdlc-lite/hooks/block-role-write.sh 2>/dev/null`
- The dispatcher treats the role as one-shot and its selftest passes: `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && printf '%s\n' "$out" | grep -qF 'prune flag: prepare sets prune True for ui-designer'`
- (guard) The edited scripts' and hooks' own checks pass: `python3 plugins/sdlc-lite/scripts/claude_roles.py selftest && python3 plugins/sdlc-lite/scripts/codex-selftest.py && bash plugins/sdlc-lite/scripts/hook-selftest.sh && python3 plugins/sdlc-lite/scripts/prompt_lint.py && python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- (guard) Role, table, rubric, skill, and lock agree: `python3 plugins/sdlc-lite/scripts/check.py`
- (red) An eval for the role cites the decision report: `grep -lx 'role: ui-designer' .sdlc/evals/[0-9]*.md | xargs grep -lF 'docs/reports/2026-10-13-ui-designer-role.md' | grep -q .`
- (guard) Scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE '^(plugins/sdlc-lite/(agents|adapters|hooks|scripts|skills/level-rubric|skills/agent)/|docs/references/|docs/README\.md$|docs/reports/2026-10-13-ui-designer-role\.md$)')"`

## Step 2: Live run of the three modes, release note, gates green
level: L2
guard timeout: 3960
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
Depends on: step 1, which is built and verified (pass) and sits uncommitted in this tree. `$SDLC_BASE_SHA` is the commit before step 1, so the scope list below holds step 1's paths too.

Names used below: `<tree>` is this repository's work tree, `<project>` is the throwaway project's root, `<mode>` is one of `plan`, `review`, `generate`, and `<level>` is the level that mode runs at.

Path rule, the defect that refused try 1 of this step: `steps.py lint` reads every literal path under a `.sdlc` folder in a step handoff as a path of this repository that must exist (`cited_sdlc_paths` and `link_findings` in `plugins/sdlc-lite/scripts/steps.py`). The throwaway project's handoffs and results are files of another git repository, so this step names them only with the `<mode>` placeholder, which lint does not read as a path. Use the same form in your result file.

1. Throwaway project. Under the tmp prefix your brief names, `git init` a folder named `ui-designer-live`. Its one commit holds a `.gitignore`, three project files, and three handoffs.
   - `.gitignore`: one line, `.worktrees/`. `run.sh` gives each role a scratch folder under the project's `.worktrees/tmp` (`plugins/sdlc-lite/scripts/run.sh:510`), and that folder must not show in the status files.
   - `index.html`: a product list built from generic `div` elements with no landmarks and one clickable `div`.
   - `tokens.css`: custom properties for color, space, and radius.
   - `styles.css`: a layer order, one card component that uses the tokens, and one rule with a hardcoded color.
   - One handoff per mode at `.sdlc/<mode>/handoff.md` under `<project>`. Each holds a `## Goal` and exactly one mode line (`mode: plan`, `mode: review`, `mode: generate`), and names project files only. Plan: an order summary section for the page. Review: `index.html` and `styles.css`. Generate: add the order summary to `index.html` and `styles.css`.
   - Never delete the project; the run cleans the prefix.
2. Runs. From `<project>`, run `SDLC_CLAUDE_EXEC=1 bash <tree>/plugins/sdlc-lite/scripts/run.sh ui-designer <level> .sdlc/<mode>/handoff.md` three times, in this order: plan at `L2`, review at `L1`, generate at `L1`.
   - Run each in the foreground with the Bash timeout at 600000 or more; `plugins/sdlc-lite/hooks/block-background.sh` refuses a background run in this session.
   - This is the legacy Claude branch of `run.sh` (`plugins/sdlc-lite/AGENTS.md`, Contracts and routing): a running session cannot load the lane's new `ui-designer-L<n>` definitions, so `dispatch.py prepare` is not usable here.
   - Each run starts from a clean project. When `git status --porcelain -- . ":(exclude).sdlc"` prints anything before a run, run that mode in a fresh `git clone` of `<project>` instead (a sibling folder under the same prefix). Nothing is deleted or reset.
   - After each run, save the output of that same status command as `<mode>.status.txt`.
3. Evidence. Copy each run's result unchanged to `docs/reports/2026-10-13-ui-designer-live-run/<mode>.txt`, and the three status files beside them. `run.sh` writes the result beside the handoff as `ui-designer-<level>.md`; a second run in the same folder gets a `-2` suffix, so copy the newest.
4. Rerun rule. If a result fails `results.py validate`, or the plan or review run changed a project file, fix `plugins/sdlc-lite/agents/ui-designer.md`, regenerate both hosts (`claude_roles.py generate`, `codex_roles.py generate`), and rerun that mode. At most two reruns per mode, then Status blocked. If the host refuses to start `claude -p`, Status is blocked with the exact refusal; never substitute a fixture for a run.
5. `docs/reports/2026-10-13-ui-designer-live-run.md` (create), linked from `docs/README.md` if `docs_check.py` asks.
   - Header facts: `Recorded:` date, `claude --version`, and the base commit with a note that step 1's changes are uncommitted on top of it.
   - Per run: the command, exit code, model and effort and cost from the `runs.jsonl` beside that handoff, the `results.py validate` outcome, and a link to its `.txt` and status file.
   - `## Not proven`: the Codex host, and the sub-agent dispatch path with the generated definitions.
   - `## Release note`: one line for the next patch (no release-notes file exists before a release is cut, so the filer copies this line into its Changelog entry).
6. Gates. Run every gate below and fix any red step 1 or this step introduced. A gate already red at the build-start HEAD is Status `inherited red`. When `SDLC_BASE_SHA` is empty in your shell, export it from the first line of the `base-sha` file beside this handoff.
### Acceptance criteria
- (red) The three retained results are valid: `for m in plan review generate; do python3 plugins/sdlc-lite/scripts/results.py validate docs/reports/2026-10-13-ui-designer-live-run/$m.txt --role ui-designer || exit 1; done`
- (red) Each result states the mode it ran: `python3 -c "import sys;sys.path.insert(0,'plugins/sdlc-lite/scripts');import results;sys.exit(any(results.key_value('docs/reports/2026-10-13-ui-designer-live-run/%s.txt'%m,'ui-designer')!=m for m in ('plan','review','generate')))"`
- (red) Plan and review left the project unchanged and generate changed it: `d=docs/reports/2026-10-13-ui-designer-live-run; test -f $d/plan.status.txt && test ! -s $d/plan.status.txt && test -f $d/review.status.txt && test ! -s $d/review.status.txt && test -s $d/generate.status.txt`
- (red) The report links the three results: `for m in plan review generate; do grep -qF "2026-10-13-ui-designer-live-run/$m.txt" docs/reports/2026-10-13-ui-designer-live-run.md || exit 1; done`
- (red) The report carries the release-note line: `grep -qx '## Release note' docs/reports/2026-10-13-ui-designer-live-run.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) Scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE '^(plugins/sdlc-lite/(agents|adapters|hooks|scripts|skills/level-rubric|skills/agent)/|docs/references/|docs/README\.md$|docs/reports/2026-10-13-ui-designer-(role|live-run)(\.md$|/))')"`

## Assumptions
- This is a replan of step 2 only. Goal and Step 1 are copied unchanged from `.sdlc/0520-ui-designer-agent/planner-L3.md`, and step 1 passed: verified by `.sdlc/0520-ui-designer-agent/step-1/verifier-L2.md` (Verdict pass) and by assembling this plan from the earlier file's text up to its step 2 heading.
- The `<mode>` placeholder form is not read as a cited path: verified by `steps.py lint` on a scratch copy of this plan and on a scratch `step-2/handoff.md` that holds the new step (both print `steps lint: ok`, and `cited_sdlc_paths` returns an empty list for it). Negative control: the refused try 1 handoff gives the same three findings through `link_findings`.
- Every step 2 guard is green on the current tree, which holds step 1 uncommitted: `bash plugins/sdlc-lite/scripts/check.sh` exit 0 in 1320 s with the tree unchanged before and after, `python3 scripts/check-packaging.py` exit 0, the `git diff --check` guard exit 0, and the scope guard exit 0 with `SDLC_BASE_SHA` set to HEAD.
- `guard timeout: 3960` is three times that 1320 s run.
- The scope guard and the `git diff --check` guard can go red: the scope command with `docs/references/` left out of its allow-list exits 1 on this tree, and `git diff --check HEAD` exits 2 on a scratch repo with a trailing-space line.
- The five (red) criteria of step 2 are red now because the report and its evidence folder do not exist (exit 1, or exit 2 from grep on the missing report), and each command shape exits 0 on a scratch fixture of the finished files. The validate criterion exits 1 on a fixture result with no `## Mode`.
- `run.sh` accepts a throwaway handoff for this role: a dry run (`SDLC_DRY_RUN=1 SDLC_CLAUDE_EXEC=1`) from a scratch project printed `claude -p --plugin-dir <this tree>/plugins/sdlc-lite --agent sdlc-lite:ui-designer --model opus --effort medium` with no `--disallowedTools`, exit 0, and left the project's status empty.
- A real `run.sh` run puts the role's scratch folder inside the project (`plugins/sdlc-lite/scripts/run.sh:510`, `$toplevel/.worktrees/tmp/<role>-<pid>`), which the dry run does not show; the project's `.gitignore` keeps it out of the status files.
- No hook refuses a `run.sh` call from a role session; only a background run is refused: verified by `grep` over `plugins/sdlc-lite/hooks/*.sh` and by the `block-background.sh` refusal this planner received.
- Write gates key on the role name only, so one role with a mode needs the builder's allowances: verified by `plugins/sdlc-lite/hooks/_role.sh:19-23`, `block-role-write.sh:14`, `claude_roles.py:46`, `run.sh:414`, `codex_roles.py:165`.
- No release-notes file exists before a release is cut: verified by the earlier plan (`git ls-files | grep -i -E 'changelog|release'` shows only closed release tickets and dated release reports).
- `docs/reports/AGENTS.md` allows small evidence files in a sibling folder of the report's stem: verified by reading it; five such folders exist under `docs/reports/`.

## Risks
- Plan and review modes are kept from editing by the role contract and a `check.py` phrase guard only. The three status files in step 2 are the one behavioral proof.
- The live run uses the legacy `run.sh` Claude branch, so the generated `ui-designer-L<n>` definitions, the sub-agent dispatch path, and the Codex host stay unproven live. The report says so.
- The builder is a sub-agent that starts `claude -p --dangerously-skip-permissions` three times through `run.sh`. If the host refuses that, step 2 blocks with the exact refusal and the conductor runs the three commands.
- `check.sh` takes about 22 minutes on this host. `steps.py split --only 2` runs it as a guard before the build, then the builder and the verifier each run it again.
- The red state of `check.sh` and `check-packaging.py` was not observed at plan time. Both are whole gates with their own negative controls; no base worktree copy was made.
- Nothing was deleted. The planner's scratch files (a probe script, a scratch plan, a fixture folder, and a scratch project) stay under `.worktrees/tmp/0520-planner-L3-2`, which is git-ignored; the brief asked for removal and rule 15 of the planner contract forbids it. No worktree was created.
- The planner, the builder, and `/chain` do not read ui-designer results yet (`agents/planner.md:16`, `docs/specs/sdlc-lite/design.md:119`). A handoff must cite a ui-designer result by path. Follow-up ticket: route the role into planner intake and `/chain`.
- Another lane may take eval number 0010 first; `evals.py check` reports the duplicate after a merge and one eval is renumbered.
- `docs_check.py` may ask for the live-run report to be linked from `docs/README.md`; the scope list allows that file.
