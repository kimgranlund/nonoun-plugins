---
name: checks-that-bite
description: >-
  Makes a check actually discriminate — tests, negative controls, guard greps, gates — and
  audits prose claims with the same rigor. Use when writing a negative control, reviewing
  assertions, or asking "is this test actually testing anything", "prove the gate bites", "the
  test passes but the feature is broken", "vacuous test", "red-then-green", "why didn't this
  catch it". Carries the vacuous-predicate bestiary (grep -q on a missing path, always-true
  typeof/computed-style predicates, exit-code-only asserts) and the independence law for a
  second derivation. NOT for choosing WHAT to test (the owning test-plan skill); NOT for
  triaging whether a red is contention or a real regression (flaky-gates).
disable-model-invocation: false
user-invocable: true
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.


# checks-that-bite

A check's only property that matters is which world-states make it red. This is how that
property gets established — by observation, never by argument.

**The prime law: a check never seen failing is not a check.** Prove red-then-green — break the
mechanism, OBSERVE the red, restore, observe the green — and report both observations. "It
should fail if X breaks" is a prediction, not evidence, and does not close a check.

## Negative controls name the variable that bites

A negative control restores the pre-fix condition and must go red. Two that went green
instead:

- "restore `position: absolute`" didn't fail a popover probe — top-layer membership was the
  biting variable, and a promoted popover paints regardless of `position`.
- "restore `inset-inline: 0`" didn't fail — the trait's inline styles beat any stylesheet
  declaration, so the stylesheet edit was inert in both directions.

So: state WHICH conjunct of a multi-part assertion bites, and which conjuncts can never bite.
An NC whose biting variable isn't named is an NC that hasn't been designed yet.

## The vacuous-predicate bestiary

Each entry is a check that passed while examining nothing.

| Vacuous form | Why it can't fail | Write instead |
|---|---|---|
| `! grep -q pat <path>` with a missing or `...`-abbreviated path | grep exits 2 on a bad path; `!` inverts it to SUCCESS — five checks passed examining nothing | `test -f <path> && ! grep -q pat <path>`, full paths always |
| `grep -c pat` used to assert absence | exits 1 on zero matches — breaks exit-code discipline in the opposite direction | `! grep -q pat` |
| `computed.minInlineSize !== 'none'` | the initial value is `auto`, so it's true unconditionally | pin the VALUE (`toBe('20ch')`) |
| `typeof x === 'number'` on an awaited `Promise<number>` | can only fail by throwing, which the await already surfaces | pin the value or its bound |
| radius shorthand `not.toBe('0px')` | passes on `'0px 0px 18px 18px'` — the shorthand serializes as four longhands | read the longhands individually |
| assert only "exit code 1" | a DIFFERENT branch also exits 1, so the check can't tell which fired | discriminate on stderr message content |

## Helpers proven, wiring unproven

A suite that calls exported helpers directly proves the exports exist — not that production
reaches them. Measured: delete the real call site and all 14 tests still pass. One
subprocess/integration leg asserting the real entry point plus an unchanged side effect (a
corpus hash) is worth more than the 14.

## Independence is a property of the mechanism

A "second derivation" that reuses the first's technique is a TRANSCRIPTION — it agrees by
construction. Measured: two independent source re-scans both missed a planted commented-out
`define()`; only the third leg, mechanism-distinct, caught it. Legs must differ in mechanism:
**static artifact scan / source read / runtime observation** — pick two different ones.

And sweeps are shape-shaped, not name-shaped: grep the idiom (`=== last ? streak + 1 : 0`),
never the naming convention. A `wait*`/`poll*` name sweep missed `settledThemeColor` entirely.

## Prose is a check surface

Confidently-false comments appear in the same voice as the verified facts beside them —
measured examples: "the fleet has no such folder today" (four existed), "reproduced
deterministically" (the test never drove the sequence), "a direct port, transfers in full" (it
dropped the one load-bearing element its own source docstring flagged).

A claim in a comment, doc, or handoff gets verified at source before it is repeated or built
on. Only an independent reader catches these reliably — generator ≠ critic applies to prose
exactly as it does to code.

## Guards fail loudly or they don't guard

A bounded wait that returns its stale value on budget exhaustion makes a timed-out wait
indistinguishable from a settled one; a guard script exiting 0 silently when invoked under an
alias is the same defect wearing different clothes. Exhaustion throws or reports, with a
diagnostic naming what it was waiting for and how long it waited; a no-op path says so on
stderr.

A red you cannot yet trust (contention vs regression) is a separate question: the user-level `flaky-gates` skill, if installed.
