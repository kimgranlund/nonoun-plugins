## Task goal
A new pipeline role, `ui-designer`, that plans, reviews and generates correct, semantic DOM structure and excellent CSS, aware of the design system and sibling styling around the code it touches.

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
