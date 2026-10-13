<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Record the maintainer's 2026-10-12 model decisions for the planner, architect, plan-reviewer, verifier, scout, researcher, filer, messenger and conductor in the model tables, keep the verifier and plan-reviewer off the model family they check, and lock the change with one new eval.
guard timeout: 900

## Step 1: Model batch, family rule, pins, eval and gates green
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `.sdlc/evals/AGENTS.md`
- `.sdlc/messages/AGENTS.md`
- `docs/specs/sdlc-lite/AGENTS.md`
- `docs/specs/AGENTS.md`
- `docs/planning/AGENTS.md`
- `docs/references/AGENTS.md`
### Do
Depends on: none. All paths are relative to the repository root. This one step is also the gates green step. The handoff names the gates (its `Done when` line); the full `check.sh` belongs to the `fanout.py land` gate that runs after this lane.

Work in this order, so the family cases are seen red before the code changes.

1. Tables. Change exactly these rows in `plugins/sdlc-lite/adapters/claude/levels.json`, the mirror `case` rows in `plugins/sdlc-lite/scripts/run.sh` (lines 163 to 176), and the tables in `plugins/sdlc-lite/skills/level-rubric/SKILL.md` (written as `Sonnet high`, `Opus xhigh`, and so on):
   - planner L1 sonnet high, L2 opus medium, L3 opus high
   - architect L1 opus xhigh
   - plan-reviewer L1 fable high
   - verifier L1 opus low (L2 sonnet high and L3 fable xhigh stay)
   - scout L1 sonnet low
   - researcher L1 sonnet high (L2 and L3 stay)
   - filer L1 sonnet low
   In `plugins/sdlc-lite/adapters/codex/models.json` change only scout L1 to `["gpt-6.1-sol", "low"]`. Builder, solo, archaeologist, and every other Codex row stay as they are (handoff Non-goals).
2. Frontmatter. `plugins/sdlc-lite/agents/messenger.md`: `model: sonnet` and a new `effort: low` line. `plugins/sdlc-lite/agents/conductor.md`: new `model: opus` and `effort: medium` lines after `description:`.
3. Selftest cases first. In section 2 and section 4 of `selftest` in `plugins/sdlc-lite/scripts/dispatch.py` add cases whose labels start with `T-0519:`, each through the existing `same()` helper so `run.sh` parity is compared too:
   - verifier L1 after an opus builder L1 result runs sonnet low
   - verifier L2 after an opus builder L3 result keeps sonnet high
   - verifier L3 after an opus builder L4 result, and after an opus L5 result, keeps fable xhigh
   - verifier L2 after a sonnet builder L2 result runs opus high
   - negative control: verifier L1 after a sonnet builder L2 result keeps opus low
   - plan-reviewer with no planner result runs fable high, and after a fable planner result runs opus high
   Run `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` now and copy the red `T-0519:` lines into your result under a heading `Observed red`. If a case is green before the code change, say so there: the handoff asks for red only where the code needs a change.
4. Family rule. Settled here, from the handoff ("an Opus build gets a Sonnet verifier at L1 and L2") and the standing rule in `plugins/sdlc-lite/skills/level-rubric/SKILL.md` (same effort; the reviewer never runs on the planner's family):
   - verifier: when the verifier's model equals the newest build's model (or the solo record's, or `--solo-model`), fable or sonnet moves to opus as today, and opus moves to sonnet, at the same effort.
   - plan-reviewer: when its model equals the newest planner's model, opus moves to fable as today, and fable moves to opus, at the same effort. A sonnet planner or no planner keeps the row (now fable high).
   Change `family()` in `plugins/sdlc-lite/scripts/dispatch.py` and the two matching blocks in `plugins/sdlc-lite/scripts/run.sh` (the `case "$model"` after `bmodel`, and the plan-reviewer block). The Codex twin (`codex_roles.py resolve`, `verifier_alternates`) does not change. If a handoff case cannot pass, stop and report blocked.
5. Pins of the old rows. Found with `git grep -n -iE 'haiku'` and a grep for model-plus-effort phrases over the repo, leaving out `.sdlc`, `docs/reports` and `docs/other`:
   - `plugins/sdlc-lite/scripts/dispatch.py`: the module docstring `family` lines; the case `plan-reviewer with no planner keeps opus high` (now fable high); the `sonnet planner` row of the plan-reviewer loop (now fable); the case `CLI prints the dispatch JSON on stdout` (scout model is now `sonnet`). Keep `agent_alias('claude-haiku-5-5') == 'haiku'`: it tests the alias function, not a row.
   - `plugins/sdlc-lite/scripts/run-selftest.sh`: the header comment and every expectation that names verifier L1 (`sonnet --effort medium` with no build becomes `opus --effort low`; after an opus build it becomes `sonnet --effort low`; after a sonnet build it stays `opus --effort low`), the plan-reviewer expectations (no planner and sonnet planner become `fable --effort high`; a fable planner stays `opus --effort high`), and planner L3 (`opus --effort high`).
   - `plugins/sdlc-lite/scripts/run.sh`: the header comment (lines 24 to 28) and the two rule comments.
   - `plugins/sdlc-lite/scripts/check.py`: `MESSENGER_WORDS` holds `model: sonnet` and `effort: low` in place of `model: claude-haiku-5-5`, and docstring item 12 says so. Keep `cap('claude-haiku-5-5')`: it tests the id mapping. The scout negative control (`claude-haiku-9-9`) still bites and stays.
   - `plugins/sdlc-lite/scripts/messages.py` `ENTRY_TEMPLATE`: the Claude messenger line says model `sonnet`, effort low. Make the same one-line edit in the tracked copy `.sdlc/messages/AGENTS.md`.
   - `plugins/sdlc-lite/skills/level-rubric/SKILL.md` prose: the verifier paragraph (add the opus to sonnet move), the plan-review paragraph (every Claude plan is reviewed on Fable high; a Fable planner result moves it to Opus high), the session agents paragraph (messenger `sonnet` low, conductor `opus` medium, both pinned in their own front matter), and the scout clause in the Agent-tool spawns section (the scout row no longer pins a Haiku id; the `haiku` seat for bare spawns stays).
   - Docs that state the rows or the rule: `docs/references/sdlc-internals.md` (run.sh entry, both family rules), `docs/planning/sdlc-lite/subagent-mode.md` (the family rule sentence and the "scout is pinned to" clause), `docs/specs/sdlc-lite/cost-control.md` (the delta re-review paragraph: `plan-reviewer:L1` is now `fable high`, and a Fable planner moves it to Opus), `docs/specs/sdlc-lite/plan-doc-executor.md` (the line saying Haiku 5.5 exists only as the scout row: no Claude row is Haiku now), `docs/specs/ticket-stages/design.md` (messenger model: Claude `sonnet` low; Codex the `messenger` row, `gpt-5.6-terra`).
   - Left alone on purpose: `plugins/sdlc-lite/scripts/supervisor.py` (its `claude-haiku-5-5` is an example receiver config, not a role row), `plugins/sdlc-lite/scripts/hook-selftest.sh`, `cost_estimate.py` and `prompt_lint.py` (fixtures with their own records), `plugins/sdlc-lite/adapters/claude/prices.json` (handoff non-goal), the Codex messenger row, and dated reports and their index lines in `docs/README.md`.
6. Generated files. Run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. Never edit `agents/<role>-L<n>.md` or a Codex TOML by hand.
7. Eval and lock. The lock now cites `.sdlc/evals/0008-solo-codex-l1-medium.md`, dated 2026-10-14, and `evals.py lock` accepts the same date with a higher number, so no lock reset is needed. Run `python3 plugins/sdlc-lite/scripts/evals.py add model-batch-roles --role all --level all --model all --effort all --host all --task-set "maintainer decision 2026-10-12, no replay run" --pass-rate 0/0 --cost-usd unknown --date 2026-10-14 --evidence .sdlc/notes.md --method TEXT --result TEXT`, then `python3 plugins/sdlc-lite/scripts/evals.py lock --eval` with the path `add` printed. The Method text lists every changed row with its old value and says the decision is the maintainer's, dated 2026-10-12, recorded in `.sdlc/notes.md`. The Result text says: no replay or benchmark ran; the Pareto read behind the decision comes from third-party summaries of Artificial Analysis, is secondary and unverified, and has no copy in `docs/reports/`; `adapters/claude/prices.json` was not recalibrated for the new rows.
8. Gates. Run every command in the criteria below and fix any red this step caused. A gate that was already red at the base goes back as Status `inherited red`. Not proven by this step: live behavior of the new rows (no live role run), and that the host honors `effort:` in the messenger and conductor front matter.
### Acceptance criteria
- (red) `python3 -c 'import json,os,subprocess,sys; p="plugins/sdlc-lite/adapters/claude/levels.json"; o=json.loads(subprocess.check_output(["git","show",os.environ["SDLC_BASE_SHA"]+":"+p])); o.update({"planner":{"L1":["sonnet","high"],"L2":["opus","medium"],"L3":["opus","high"]},"architect":{"L1":["opus","xhigh"]},"plan-reviewer":{"L1":["fable","high"]},"verifier":{"L1":["opus","low"],"L2":["sonnet","high"],"L3":["fable","xhigh"]},"scout":{"L1":["sonnet","low"]},"researcher":{"L1":["sonnet","high"],"L2":["opus","medium"],"L3":["opus","high"]},"filer":{"L1":["sonnet","low"]}}); sys.exit(0 if json.load(open(p))==o else 1)'` exits 0: the Claude table is the base table with exactly the handoff's rows changed.
- (red) `python3 -c 'import json,os,subprocess,sys; p="plugins/sdlc-lite/adapters/codex/models.json"; o=json.loads(subprocess.check_output(["git","show",os.environ["SDLC_BASE_SHA"]+":"+p])); o["scout"]={"L1":["gpt-6.1-sol","low"]}; sys.exit(0 if json.load(open(p))==o else 1)'` exits 0: the Codex table is the base table with only scout L1 changed.
- (red) `head -8 plugins/sdlc-lite/agents/messenger.md | grep -qx "model: sonnet" && head -8 plugins/sdlc-lite/agents/messenger.md | grep -qx "effort: low" && head -8 plugins/sdlc-lite/agents/conductor.md | grep -qx "model: opus" && head -8 plugins/sdlc-lite/agents/conductor.md | grep -qx "effort: medium"` exits 0.
- (red) `python3 -c 'import sys,tempfile,pathlib; sys.path.insert(0,"plugins/sdlc-lite/scripts"); import dispatch; d=pathlib.Path(tempfile.mkdtemp()); v=dispatch.family("verifier","opus",d,"opus"); (d/"planner-L1.md").write_text("<!-- role=planner level=L1 model=fable effort=x -->\n"); r=dispatch.family("plan-reviewer","fable",d); sys.exit(0 if (v,r)==("sonnet","opus") else 1)'` exits 0: an opus verifier after an opus solo moves to sonnet, and a fable reviewer after a fable planner moves to opus.
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && test "$(printf '%s\n' "$out" | grep -c '^ok: T-0519')" -ge 6` exits 0: the selftest passes and at least 6 `T-0519:` cases ran.
- The builder result has an `Observed red` heading that quotes the `T-0519:` selftest lines that failed before `family()` changed, or states which of them were green before it and why.
- `out=$(python3 plugins/sdlc-lite/scripts/evals.py check) && printf '%s\n' "$out" | grep -q 'model-batch-roles'` exits 0: the lock cites the new eval and the table hash matches.
- `! git grep -q 'claude-haiku-5-5' -- plugins/sdlc-lite/adapters/claude/levels.json plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/agents/messenger.md plugins/sdlc-lite/agents/scout-L1.md plugins/sdlc-lite/skills/level-rubric/SKILL.md plugins/sdlc-lite/scripts/messages.py .sdlc/messages/AGENTS.md docs/specs/ticket-stages/design.md docs/planning/sdlc-lite/subagent-mode.md` exits 0: no named file still pins the old scout or messenger model.
- (guard) `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check && python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check && python3 plugins/sdlc-lite/scripts/check.py && python3 scripts/check-packaging.py` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/solo_run.py selftest && python3 plugins/sdlc-lite/scripts/messages.py selftest && python3 plugins/sdlc-lite/scripts/codex-selftest.py` exits 0.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh` exits 0.
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" ":(exclude)plugins/sdlc-lite" ":(exclude)docs"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc" ":(exclude)plugins/sdlc-lite" ":(exclude)docs")"` exits 0: nothing outside `plugins/sdlc-lite`, `docs` and `.sdlc` changed.

## Assumptions
- The swapped verifier and reviewer keep the row's effort (opus low becomes sonnet low): verified by the standing rule text in `plugins/sdlc-lite/skills/level-rubric/SKILL.md` ("becomes Opus at the same effort") and `plugins/sdlc-lite/scripts/dispatch.py` `family()`, which changes only the model.
- A fable reviewer after a fable planner moves to opus: verified by the existing cases that already expect it (`plugins/sdlc-lite/scripts/dispatch.py` plan-reviewer loop row `fable planner`, `plugins/sdlc-lite/scripts/run-selftest.sh` "fable planner newest"); with the row on Fable they need the new branch to stay green.
- The family rule needs a code change: verified by running the fourth criterion on the current tree, where `family()` returned opus and fable.
- No lock reset is needed: verified by `.sdlc/evals/0008-solo-codex-l1-medium.md` (date 2026-10-14) and the `evals.py` docstring ("dated the same with a higher number"); the new eval takes number 0009 here.
- Every gate is green at the base: verified by running all of them on the current tree (claude_roles, codex_roles, evals check, check.py, check-packaging under 6 s each; dispatch selftest 145 s, run-selftest 142 s, messages selftest 76 s, codex-selftest 36 s, solo_run selftest 31 s).
- `.sdlc/messages/AGENTS.md` is a tracked rendered copy of `ENTRY_TEMPLATE`: verified by `git ls-files` and its matching line 64.
- The plan text passes the structural checks: verified by `steps.py lint` (ok), `specgate.py check` (ok) and `results.py validate --role planner` (exit 0) on a scratch copy.

## Risks
- The dispatch selftest criterion is not tagged `(red)` because it runs about 145 s and a red-first run may time out; it was seen red by hand (0 `T-0519` lines today).
- Another lane may add eval 0009 at the same time; `evals.py check` reports a duplicate number after the merge. The criterion matches the slug, not the number.
- `supervisor.py` keeps `claude-haiku-5-5` in its example receiver config. If the maintainer meant that to follow the messenger, it is a follow-up.
- A conductor pinned to `model: opus` changes the model of every session that uses `sdlc-lite:conductor` as its agent. That is the handoff's decision; it has no live check here.
- A sonnet low verifier after an opus builder L1 is the weakest verifier seat in the table. It follows from the same-effort rule; the handoff does not name the effort.
- `prices.json` holds no fitted rate for the new mix, so cost estimates for the changed rows drift until it is recalibrated.
- The scratch copy of this plan stays at `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout60/m/.worktrees/tmp/0519-planner-L2/` (gitignored); nothing was deleted, per the no-delete rule.
