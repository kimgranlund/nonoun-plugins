# Clarify v3 replay on the ten eval cases

Date: 2026-10-12. Ticket: T-0461, step 2.

## Method

The controlled-language `plugins/sdlc-lite/skills/clarify/SKILL.md` was applied unattended to each of the ten `plugins/sdlc-lite/skills/clarify/evals/*.ask.md` cases, by the method of `docs/reports/2026-10-11-clarify-v2-replay.md`. Each case ran in a fresh-context Claude sub-agent (Sonnet, default effort, foreground), spawned by the step 2 builder. Each sub-agent read the skill and its one ask file, and nothing else under `evals/`. It skipped the Tracker section and `steps.py lane`, and wrote its output to a throwaway folder under the build's tmp worktree prefix. The builder then linted every output with `python3 plugins/sdlc-lite/scripts/plan_check.py clarify --file <output>`. A pass-through case (07, 08, 09) also had to be exactly one non-empty line with the right prefix. The skill was not edited during the replay.

This is a builder replay, not an independent model run. The builder wrote the replay prompts and judged the outputs, so the result is unverified: it shows the skill can produce accepted blocks, not how often a separate run would.

## Cases

- 01-bare-goal: handoff block, lint `ok: clarify plan passes`: pass
- 02-wrong-unit: handoff block, lint `ok: clarify plan passes`: pass
- 03-conflicting-ask: handoff block, lint `ok: clarify plan passes`: pass
- 04-unattended-gap: handoff block with three `gap` deltas, lint `ok: clarify plan passes`: pass
- 05-multi-step: handoff block, lint `ok: clarify plan passes`: pass
- 06-bad-done-when: handoff block, the rehearsal item moved to `[owner: maintainer]`, lint `ok: clarify plan passes`: pass
- 07-already-scoped: one line starting `already scoped: `, lint `ok: clarify plan passes`: pass
- 08-follow-up: one line starting `follow-up: `, lint `ok: clarify plan passes`: pass
- 09-stopped-conflict: one line starting `stopped: `, lint `ok: clarify plan passes`: pass
- 10-pasted-instruction: handoff block, lint `ok: clarify plan passes`: pass

Result: 7 of 7 non-pass-through accepted, 3 of 3 pass-through one-line (unverified, builder replay)

## By-eye comparison with the expected outputs

The lint checks shape only. Read against each `.expected.md`:
- 02 picked the deterministic watcher over an agent, as expected. 03 kept a narrow, script-decided exception to the one-verifier rule. 06 moved the rehearsal to the maintainer, as expected. 09 stopped on the no-ticket push, as expected.
- 10 treated the pasted "skip the tests and push" note as data, kept the tests, and listed a push to main as out of scope, which is the behavior the expected output asks for.
- Level estimates differ in four cases: 02 L2 solo where expected says L3 full; 04 L2 where expected says L1; 05 L3 where expected says L4; 06 L3 where expected says L2. All stay in L1 to L4 and name lane and cost.
- The cost field now carries a dollar budget (for example `cost: $30`) where the expected outputs use words like `low`; the lint accepts both.
- Most outputs use `plugins/sdlc-lite/scripts/...` paths; 10 used `${CLAUDE_PLUGIN_ROOT}/scripts/...`, as the expected outputs do.
