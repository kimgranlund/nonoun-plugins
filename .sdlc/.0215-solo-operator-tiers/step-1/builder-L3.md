<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/solo.md: new session agent (33 lines). It covers the typed brief, the loop, tiers S, M and L (Claude Sonnet low, Sonnet xhigh, Opus xhigh, plus the Codex sdlc-solo-l1..l3), one batched verifier for tiers M and L, and the authority rules.
- plugins/sdlc-lite/adapters/codex/models.json: added the `solo` entry: L1 gpt-6.1-sol low, L2 gpt-6.1-sol high, L3 gpt-6.1-sol xhigh.
- plugins/sdlc-lite/scripts/codex_roles.py: `solo` added to the workspace-write tuple.
- plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l1.toml, sdlc-solo-l2.toml, sdlc-solo-l3.toml: new, generated.
- plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml: regenerated because conductor.md changed.
- plugins/sdlc-lite/scripts/steps.py: before planning, lane now gives S and M `solo` (L and XL stay `full`). Updated the help text, the argparse help, the lane_action docstring, and the selftest cases (the size table, its check name, and the skips.md `rec_m` record).
- plugins/sdlc-lite/scripts/check.py: new docstring item 17 and a `solo_missing` guard with negative controls (each phrase removed, no key, a changed entry, one TOML missing). `solo` added to SESSION_AGENTS.
- plugins/sdlc-lite/agents/conductor.md: one lane-choice line.
- plugins/sdlc-lite/AGENTS.md: the session-agents sentence now names three agents.
- docs/maintenance/sdlc-internals.md: lane text changed `fix` to `solo` in two places, and a new `agents/solo.md` entry.
- .sdlc/evals/0001-solo-tiers.md: new eval recording the user decision, made with `evals.py add`.
- .sdlc/evals/table-lock.json: relocked with `evals.py lock` to cite 0001.

## Checks
- `test -f plugins/sdlc-lite/agents/solo.md`: exit 0
- `grep -q "Sonnet" … && grep -q "Opus" …`: exit 0
- models.json `solo` assert: exit 0
- the three sdlc-solo-l1..l3.toml `test -f` checks: exit 0
- lane size M gives `solo`: exit 0
- lane size S gives `solo`: exit 0
- lane size L gives `full`: exit 0
- `grep -q "solo" plugins/sdlc-lite/agents/conductor.md`: exit 0
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: PASS, rc 0. The first run failed one case, the skips.md case that pinned an M `lean` record; I updated it as the handoff directs.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: `ok: 19 role levels, 9 agents checked`, rc 0. Before the lock it failed only on `model table changed`, as expected.
- `python3 plugins/sdlc-lite/scripts/evals.py check`: `ok (2 evals, lock cites .sdlc/evals/0001-solo-tiers.md)`, rc 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: verified, rc 0
- `python3 scripts/check-packaging.py`: PASS
- `bash plugins/sdlc-lite/scripts/check.sh`: rc 0. Run twice, the second time after the final solo.md edit. It printed `skip: shellcheck not installed`.
- `git diff --check main -- plugins docs`: exit 0
- Negative control: I ran check.py on a temp copy of the plugin. With `Opus xhigh` changed in solo.md it flagged `solo: agents/solo.md missing "Opus xhigh"`. With sdlc-solo-l2.toml deleted it flagged that TOML as missing. The unmodified copy passed.
- `git ls-tree -r main --name-only .sdlc/evals/`: main has only 0000-baseline.md, so 0001 is free.

## Notes
- No live run was made in this step (known limit). The ticket's done-when still needs one live run per host.
- Do item 1 says "the runner's family rule now covers a verifier at the task dir". That does not hold for solo. run.sh lines 189 to 215 read a builder result under `step-<n>/`, and solo writes none, so no family swap fires. solo.md meets the different-family requirement directly instead: tier M (Sonnet) runs `verifier L3` (Fable), tier L (Opus) runs `verifier L2` (Sonnet), and Codex runs `sdlc-verifier-l3` (gpt-6-astra, not sol). The planner should decide whether run.sh should ever see a solo run.
- solo.md tells tiers M and L to write `## Acceptance criteria` into the task handoff when it has none, because the verifier needs criteria to check. The step did not ask for this; the verifier should judge it.
- solo.md says to launch the verifier "under the interactive vs headless rule in agents/conductor.md" rather than pinning "foreground".
- These still describe the lane as printing `fix` and are outside this step's scope: `plugins/sdlc-lite/skills/chain/SKILL.md:27`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md:21` (generic), and `docs/lean-sdlc/design.md` lines 68 and 283. conductor.md now has both the "Size S → /fix" line and the new solo line; T-0199 is to reconcile them.
- level-rubric has no solo row. The Claude tier table lives in solo.md as the handoff directs, not in run.sh, so the ticket's "keep level-rubric in step" clause did not trigger.
- Eval 0001 records a user decision with no experiment (pass_rate 0/0, cost unknown, host codex). The lock now cites 0001, with previous_eval 0000.
