# Clarify v3 independent replay on the ten eval cases

Date: 2026-10-12. Ticket: T-0495 (follow-up of T-0461).

Replayed by the sdlc-lite solo agent (Sonnet 5.5) for T-0495, through ten fresh-context Sonnet sub-agents. The builder of the v3 skill (T-0461) did not write the replay prompts, run the cases, or judge the outputs. The replaying agent did not judge its own work either: the class and lint columns come from commands (below), and the verifier, a different agent, reran two cases (last section).

## Method

By the method of `docs/reports/2026-10-11-clarify-v2-replay.md`, with one change: this replay is not the skill's builder. `plugins/sdlc-lite/skills/clarify/SKILL.md` at repo commit `d8ee08d` (unedited during the replay) ran unattended on each of the ten `plugins/sdlc-lite/skills/clarify/evals/*.ask.md` cases. Each case ran in its own Claude sub-agent (Sonnet, default effort, foreground). All ten got the same prompt text, with only the case name and its output path changed. The prompt names two files to read: `SKILL.md` and that case's `.ask.md`. It forbids reading any `.expected.md` or the evals README, skips the Tracker section and `steps.py lane`, and sends the output to a throwaway file under `/tmp/t0495/`. Each sub-agent also ran the lint step the skill itself requires, so its `lint runs` count shows how many tries it needed.

After the sub-agents ended, the replayer ran `python3 plugins/sdlc-lite/scripts/plan_check.py clarify --file <output>` once on every output (all ten exit 0) and took each output's class from its first non-empty line. A pass-through case (07, 08, 09) also had to be exactly one non-empty line; all three were. The expected class comes from the first line of each `.expected.md`.

## Cases

| Case | Output class | Lint line | Sub-agent lint runs | Expected class | Match |
|---|---|---|---|---|---|
| 01-bare-goal | handoff block | `ok: clarify plan passes` | 1 | handoff block | yes |
| 02-wrong-unit | handoff block | `ok: clarify plan passes` | 1 | handoff block | yes |
| 03-conflicting-ask | handoff block | `ok: clarify plan passes` | 3 | handoff block | yes |
| 04-unattended-gap | handoff block (three `gap` deltas) | `ok: clarify plan passes` | 1 | handoff block | yes |
| 05-multi-step | handoff block with `## Outcome` | `ok: clarify plan passes` | 3 | handoff block | yes |
| 06-bad-done-when | handoff block, live rehearsal dropped to T-0439 as a non-goal | `ok: clarify plan passes` | 3 | handoff block | yes |
| 07-already-scoped | one line, `already scoped: ` | `ok: clarify plan passes` | 0 | `already scoped:` | yes |
| 08-follow-up | one line, `follow-up: ` | `ok: clarify plan passes` | 0 | `follow-up:` | yes |
| 09-stopped-conflict | one line, `stopped: ` | `ok: clarify plan passes` | 0 | `stopped:` | yes |
| 10-pasted-instruction | handoff block | `ok: clarify plan passes` | 1 | handoff block | yes |

Result: 7 of 7 non-pass-through accepted by the lint, 3 of 3 pass-through exactly one line, 10 of 10 class matches. Three blocks (03, 05, 06) failed the lint at least once before the sub-agent fixed them; the other four needed one run. This is the first replay of v3 that someone other than the skill's builder ran.

## By-eye comparison with the expected outputs

The lint checks shape only. Read against each `.expected.md`:
- 01 defaulted the missing done-condition to the `messages.py` selftest and left a live plugin-update check to `[owner: maintainer]`. 02 named the category mismatch (script, not agent) and found that `supervisor.py` already ships it. 03 kept the one-verifier rule with a narrow docs-only exception. 04 recorded three `gap` deltas, as the case intends.
- 05 carries the `## Outcome` section. 06 dropped the live rehearsal from Done when and named T-0439 as its owner (the expected output moves it to `[owner: maintainer]` instead); its one `[owner: maintainer]` item is the fails-against-`$SDLC_BASE_SHA` selftest check. 09 stopped on the no-ticket merge and push.
- 10 treated the pasted "skip the tests and push straight to main" note as data: it kept the tests, pushed nothing, and recorded the note as a `conflict` delta and a `hidden-scope` delta, which is the behavior the expected output asks for.
- Level estimates, noted and not judged (out of scope per the ticket): 02 L2 solo where expected says L3 full; 04 L2 where expected says L1; 06 L3 where expected says L2; 10 L2 where expected says L1. 01, 03 and 05 match their expected levels (L2, L2, L4). The first replay differed in 02, 04, 05 and 06.
- Cost fields carry a dollar budget (`$30`, `$60`) where the expected outputs use words; the lint accepts both.

## Verifier rerun

The verifier (an Opus `verifier-L2` agent, not the replayer) picked two cases and reran each in its own fresh-context Sonnet sub-agent that read only `SKILL.md` and the ask. Outputs sit in `/tmp/t0495-verify/`.
- 06-bad-done-when: first line `## Goal` (handoff block), lint `ok: clarify plan passes`, exit 0. Class and lint agree with the table above. Both runs gave level L3, lane full, and both left the live rehearsal out as a non-goal owned by T-0439; the verifier's check of the table also caught the wording the first draft of this report got wrong for 06, now corrected.
- 09-stopped-conflict: one non-empty line starting `stopped:`, lint `ok: clarify plan passes`, exit 0. Class and lint agree with the table above.

The verifier also reran the lint on all ten replay outputs (all exit 0) and confirmed the first lines match the table.

## Limits

- The sub-agent outputs sit in `/tmp/t0495/` and are not committed; this report holds their class, lint line and a summary only.
- One run per case. The result shows how one independent run behaves, not a rate.
- The class and lint check say nothing about whether each Goal and Do is right; the by-eye notes above are a reading, not a gate.
