# Clarify v2 replay on the eight eval cases

Date: 2026-10-11. Ticket: T-0448, step 2.

## Method

The rewritten `plugins/sdlc-lite/skills/clarify/SKILL.md` was applied unattended to each of the eight `plugins/sdlc-lite/skills/clarify/evals/*.ask.md` cases. Each case ran in a fresh-context Claude sub-agent (Sonnet, default effort), spawned by the step 2 builder. Each sub-agent read the skill and its one ask file, and nothing else under `evals/`. It skipped the Tracker section and `steps.py lane`, and wrote its output to a throwaway folder under the build's tmp worktree prefix. The builder then linted every output with `python3 plugins/sdlc-lite/scripts/plan_check.py clarify --file <output>`. A pass-through case also had to be exactly one non-empty line with the right prefix.

This is a builder replay, not an independent model run. The builder that rewrote the skill also wrote the replay prompts and judged the outputs, so the count below shows the skill can produce accepted blocks, not how often a separate run would.

## Cases

- 01-bare-goal: handoff block, lint `ok: clarify plan passes`: pass
- 02-wrong-unit: handoff block, lint `ok: clarify plan passes`: pass
- 03-conflicting-ask: handoff block, lint `ok: clarify plan passes`: pass
- 04-unattended-gap: handoff block with two `(gap: ...; default: ...)` deltas, lint `ok: clarify plan passes`: pass
- 05-multi-step: handoff block with a `## Outcome` section, lint `ok: clarify plan passes`: pass
- 06-bad-done-when: handoff block, the rehearsal item moved to `[owner: maintainer]`, lint `ok: clarify plan passes`: pass
- 07-already-scoped: one line starting `already scoped: `: pass
- 08-follow-up: one line starting `follow-up: `: pass

Result: 6 of 6 non-pass-through accepted, 2 of 2 pass-through one-line

## By-eye comparison with the expected outputs

The lint checks shape only. Read against each `.expected.md`:
- 02 picked the deterministic script over an agent, as expected. 03 kept the narrow, script-decided exception to the one-verifier rule. 06 moved the rehearsal to the maintainer, as expected.
- Level estimates differ in two cases. 05 read the source ticket as a design-only pass and sized it L2 solo, where the expected output sizes the full build at L4. 06 sized L3 where the expected output says L2. Both are inside L1 to L4 and both name their lane and cost.
- Every Level line uses the skill's `Level: L<n> (lane: ...; cost: ...; reversible: ...)` shape. The `.expected.md` files use an older comma shape; the lint accepts both.
- The outputs use `plugins/sdlc-lite/scripts/...` paths, which run from this repo's root, where the expected outputs use `${CLAUDE_PLUGIN_ROOT}/scripts/...`.
