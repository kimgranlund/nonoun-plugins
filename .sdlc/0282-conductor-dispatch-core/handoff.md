---
id: T-0282
title: "Conductor and chain dispatch roles as sub-agents"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0276, T-0278, T-0279, T-0280, T-0281]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The conductor, chain, fix, level-rubric, and handoff-format texts replace "run run.sh" with prepare, Agent spawn, record; this is the flip that makes sub-agents the Claude mode.

## Intent
- Do: Conductor and chain dispatch roles as sub-agents.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `agents/conductor.md`, `skills/chain/SKILL.md`, `skills/fix/SKILL.md`, `skills/level-rubric/SKILL.md`, and `skills/handoff-format/SKILL.md` name `dispatch.py prepare`, the `Agent` spawn with `name`, `model`, and `run_in_background`, and `dispatch.py record`; none tells the conductor to run `run.sh` for the Claude backend.
  - `check.py` guards (items 4, 11, 21 and a new dispatch item) pass and each new phrase guard has a negative control (phrase removed, check fails).
  - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` passes after regeneration; the Codex path text is unchanged in meaning.
  - A throwaway-project run of one `/fix` item through the conductor produces a recorded builder and verifier result with `transport: subagent`, and `steps.py next` reads them (evidence pasted in the ticket).

## Context
Design sections 1, 4, 8. Land only after the hook gate (G) so conductor spawns are not denied. The headless conductor rules (`SDLC_HEADLESS`) keep foreground spawns.

## Constraints
Do not remove run.sh or its Claude branch in this ticket. No em dashes. No push, tag, or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- `cd plugins/sdlc-lite && for f in agents/conductor.md skills/chain/SKILL.md skills/fix/SKILL.md skills/level-rubric/SKILL.md skills/handoff-format/SKILL.md; do for ph in 'dispatch.py prepare' 'dispatch.py record' '`Agent`' '`name`' '`model`' '`run_in_background`'; do grep -qF -- "$ph" "$f" || { echo "$f lacks $ph"; exit 1; }; done; done`
- `cd plugins/sdlc-lite && test "$(for f in agents/conductor.md skills/chain/SKILL.md skills/fix/SKILL.md skills/level-rubric/SKILL.md skills/handoff-format/SKILL.md; do grep -n 'run\.sh' "$f" | grep -v -i codex; done | wc -l | tr -d ' ')" = 0`
- `grep -q '"transport":"subagent"' .sdlc/0282-conductor-dispatch-core/handoff.md`
- `test "$(grep -c '"transport":"subagent"' /tmp/t0282-live2/.sdlc/typo-demo/step-1/runs.jsonl)" = 2`
- `python3 plugins/sdlc-lite/scripts/steps.py next /tmp/t0282-live2/.sdlc/typo-demo/step-1 | head -1 | grep -qx done`
- (guard) `git diff --check`

Known and out of scope: `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` is red at the base commit (`budget.spend` returns three values since T-0280, solo_run.py unpacks two), so `bash plugins/sdlc-lite/scripts/check.sh` exits 1 on that line alone; every other check.sh step passes.

## Evidence
Throwaway run of one `/fix` item through the conductor, in `/tmp/t0282-live2` (a git repo holding `notes.txt` with the typo "teh" and `.sdlc/typo-demo/handoff.md`), 2026-10-07, Claude Code 2.1.292:

`env -u SDLC_ROLE SDLC_HEADLESS=1 claude -p --plugin-dir plugins/sdlc-lite --agent sdlc-lite:conductor --model sonnet --effort medium --dangerously-skip-permissions -- "/sdlc-lite:fix typo-demo ..."`

The conductor wrote `step-1/handoff.md`, ran `dispatch.py prepare builder L1` and `prepare verifier L1`, spawned `sdlc-lite:builder-L1` (`builder-L1-typo-demo-s1`, model sonnet, `run_in_background: false`) and `sdlc-lite:verifier-L1` (`verifier-L1-typo-demo-s1`, model opus, since a Sonnet build moves the verifier to Opus), and ran `dispatch.py record` for each. Session cost 0.56 USD. `runs.jsonl` of the step dir, selected fields:

```
{"role":"builder","level":"L1","model":"sonnet","effort":"low","file":"builder-L1.md","backend":"claude","transport":"subagent","agent_id":"a45c488c59da6a5f2","usage":{"subagent_tokens":35050,"tool_uses":4},"cost_usd":0.02839,"cost_estimated":true,"cost_basis":"tokens x blended"}
{"role":"verifier","level":"L1","model":"opus","effort":"medium","file":"verifier-L1.md","backend":"claude","transport":"subagent","agent_id":"af97a073618eda727","usage":{"subagent_tokens":40029,"tool_uses":4},"cost_usd":0.039629,"cost_estimated":true,"cost_basis":"tokens x blended"}
```

Result headers: `<!-- role=builder level=L1 model=sonnet effort=low -->`, `<!-- role=verifier level=L1 model=opus effort=medium -->`; builder `## Status` done, verifier `## Verdict` pass. `dispatch.py status` listed both attempts `completed`. `steps.py next .sdlc/typo-demo/step-1` printed:

```
done
reason: newest verifier verifier-L1.md passed
read: .sdlc/typo-demo/step-1/builder-L1.md
read: .sdlc/typo-demo/step-1/verifier-L1.md
```

An earlier run of the same item (`/tmp/t0282-live`, text before the stdin rule below) found two things. First, the conductor ran `dispatch.py record` with no result file and no stdin, because neither role writes its result file when the prompt only says its final message is "saved verbatim"; `record` closed the attempt failed and refused a second record. The conductor, chain, and fix texts now say to pipe the final message to `record` on stdin and never to run it with neither (the second run followed it). Second, the conductor spawned the second verifier with `model: sonnet`, and the spawn gate denied it (`model 'sonnet' is not the dispatch model 'opus'`): the gate bites, and the texts now say to read `model` from each dispatch's JSON.
