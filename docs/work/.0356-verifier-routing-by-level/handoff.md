---
id: T-0356
title: "Route the L3 Fable verifier to L4, L5, merge and security tickets only; replay T-0333 on L2 first"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The L3 Fable verifier runs only for L4, L5, merge and security tickets; L1 and L2 tickets use the L2 Sonnet verifier.

## Intent
- Do: (1) Replay the 12 T-0333 verifications with verifier L2 (sonnet, high) in a throwaway tree and compare with the recorded L3 verdicts, including the 3 true fails (T-0334 to T-0336); budget about $5 to $10. (2) Add maison and agent-ui tickets to the replay only if the sdlc-lite replay is clean. (3) If L2 catches every recorded fail with no new false fail, change the routing in the level rubric and steps.py or adapters/claude/levels.json, lock an eval with evals.py, and regenerate agents. Stop and report before step 3 if the replay misses a fail.
- Non-goals: Changing the model or effort of any row without the replay result and the user's go-ahead on step 3.
- Done when:
  - A dated report in docs/reports/ with the per-ticket L2 versus L3 comparison.
  - If routing changes: eval record locked, generated agents and Codex TOML current, check.sh passes.

## Context
Replay done (docs/reports/2026-10-07-verifier-l2-replay.md, uncommitted in main; commit it with this ticket): L2 matched L3 on 41 of 43 criteria, missed T0280-2 (literal label match), one false fail; $6.19 vs about $36.56. The user approved shipping on 2026-10-07: verifier L3 only for L4, L5, merge and security tickets, plus any ticket with a criterion that pins an exact label or string; L1 and L2 tickets use verifier L2. Find where verifier level is chosen (steps.py lane/split, the level rubric, conductor.md and the verify skill) and make that the rule, with a selftest positive and negative control. No levels.json model or effort row changes.
Fleet cost analysis of 2026-10-07 (all-time deduped run records, five repos): verifier L3 Fable $1,291 over 198 runs (about $6.5 each) versus verifier L2 Sonnet about $0.50 each; solo L2 Sonnet xhigh about $406 ($3.31 to $5.53 per run). The user approved these four proposals on 2026-10-07.

## Constraints
Model and effort defaults are the user's decision: the user approved the replay and the proposal, step 3 reports before shipping. No em or en dashes.

## Acceptance criteria
- [ ] T0356-1: `steps.py verifier-level` prints L2 for a plain size L2 ticket and L3 for size L4: `S=plugins/sdlc-lite/scripts; d=$(mktemp -d); printf -- '---\nid: T-0001\ntitle: "x"\nsize: L2\n---\n\n## Goal\ng\n' > $d/handoff.md; python3 $S/steps.py verifier-level $d | head -1 | grep -qx L2 && sed -i.bak 's/size: L2/size: L4/' $d/handoff.md && python3 $S/steps.py verifier-level $d | head -1 | grep -qx L3`
- [ ] T0356-2: the steps.py selftest holds the positive and negative controls (size L4 or L5, a Merge title, the word security, a `verifier: L3` line, an exact label criterion raise to L3; plain L1, L2, L3 and unsized tickets stay L2): `python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1 | grep -c '^ok: (v) ' | grep -qx 10 && python3 plugins/sdlc-lite/scripts/steps.py selftest >/dev/null`
- [ ] T0356-3: fanout's default solo verifier is L2 and is no longer a fixed L3: `grep -q "^SOLO_VERIFIER = 'L2'" plugins/sdlc-lite/scripts/fanout.py && ! grep -q "SOLO_VERIFIER = 'L3'" plugins/sdlc-lite/scripts/fanout.py && python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- [ ] T0356-4: a Sonnet solo's L2 verifier still moves off its family on all three paths (a runs.jsonl solo record in `run.sh`, the same in `dispatch.py`, and `--solo-model` for a sub-agent worktree that holds no record): `bash plugins/sdlc-lite/scripts/run-selftest.sh && python3 plugins/sdlc-lite/scripts/dispatch.py selftest`
- [ ] T0356-5: `solo_run.py` prints the verifier command at the rule's level: `python3 plugins/sdlc-lite/scripts/solo_run.py selftest`
- [ ] T0356-6: the rule is stated once in each owner and agrees (solo.md, the fanout skill, the level rubric, the internals reference all name `steps.py verifier-level`): `test "$(grep -l 'verifier-level' plugins/sdlc-lite/agents/solo.md plugins/sdlc-lite/skills/fanout/SKILL.md plugins/sdlc-lite/skills/level-rubric/SKILL.md docs/references/sdlc-internals.md | wc -l)" -eq 4`
- [ ] T0356-7: generated Claude and Codex agents are current: `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check && python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- [ ] T0356-8: no model or effort row changed and the eval record exists with the table lock still valid: `git diff --quiet HEAD -- plugins/sdlc-lite/adapters/claude/levels.json plugins/sdlc-lite/adapters/codex/models.json && python3 plugins/sdlc-lite/scripts/evals.py list | grep -q 0003-verifier-l2-routing && python3 plugins/sdlc-lite/scripts/evals.py check`
- [ ] T0356-9: the dated replay report is in the tree and the full suite passes: `test -f docs/reports/2026-10-07-verifier-l2-replay.md && python3 plugins/sdlc-lite/scripts/check.py && bash plugins/sdlc-lite/scripts/check.sh`
- [ ] T0356-10: no em or en dash was added outside the generated Codex agents (their pre-existing role text holds some): `python3 -c "import subprocess,sys;d=subprocess.run(['git','diff','HEAD','-U0','--','.',':(exclude)plugins/sdlc-lite/adapters/codex/agents'],capture_output=True,text=True).stdout;sys.exit(any(l.startswith('+') and not l.startswith('+++') and ('\u2014' in l or '\u2013' in l) for l in d.splitlines()))"`

## Closed

2026-10-07: Merged cf3f5b84. Lane verifier L3 passed 7 of 7 criteria on the second run except the agent SKILL.md hardcoded L2, fixed in the lane tree and rechecked by grep; gates green.
