# The enforcement ladder

The spine of the inside-out pass. Every rule the system states gets one rung, one named enforcer,
and for a judged check two extra answers: is it independent, and can its control fail.

| Rung | Name | What it means | Typical enforcer |
|---|---|---|---|
| 1 | Knowledge base | The right way could be read somewhere | a doc, an ADR, a ledger |
| 2 | Rule | Prose says must or never | CLAUDE.md, AGENTS.md, a `*-rules` skill, a permission entry |
| 3 | Procedure | A procedure does it right by construction | a skill, an agent, a command, a template |
| 4a | Mechanical check | The wrong way is refused, deterministically, at action time | hook, linter, type check, CI gate, test |
| 4b | Judged check | The wrong way is refused by judgment against a stated bar | evaluator (scored against a rubric, dataset or baseline) or verifier (pass or fail against acceptance criteria, on its own evidence) |

Rung 4 is reported as two halves, never merged into one cell. A system with only 4b has no
deterministic floor; a system with only 4a cannot catch anything a rubric would.

## The two extra questions for a judged check

Independence. A verifier that shares context, model family, or seat with the maker is grading its
own work with extra steps. Record all three: context (fresh or inherited), model family, seat.
Any shared axis is a finding.

Can the control fail. A check no one has seen go red is not a check. Ask for the observed red:
the command, the tree it was run against, the output. An evaluator needs a rubric, a threshold,
and a baseline it was compared against; missing any of the three is a finding.

## Reconcile before a rule drops to rung 2

A rung is assigned from two independent passes, never from one. The rules pass reads what the
system says; the checks pass reads what the system runs. "None found" from the rules pass is a
claim with one evidence path.

Before a rule is placed on rung 2 or lower, search the checks inventory (hooks, git hooks,
checkers, evaluators, verifiers) twice: once for the rule's key terms, once for the path of the
file the rule governs. Record both searches. Only when the checks inventory also shows nothing
does the rule sit at rung 2, and only then is it a finding.

The two passes disagreeing is the normal case, not the failure case. On the first real run of
this skill, two rules were headed for rung 2 on the rules pass alone while the checks pass
already held the hook that enforced them.

## The enforcement matrix

Output 4. One row per rule, in this shape:

| Rule | Stated in | Rung | Enforcer | Independent? | Control seen red? |
|---|---|---|---|---|---|
| Seats are never subagents | CLAUDE.md | 4a | `hooks/no-seat-subagents.py` | n/a | 🟢 blocked call, observed |
| No 🟢 row without a control | plan-rules | 4a | `verdict.py check` at commit-msg | n/a | 🟢 |
| Review before any PR | pre-land-review | 4b | reviewer-l4 plus verifier-l3 | 🟡 same model family as the builder at L5 and above | 🔴 never observed failing |
| Peer messages stay short | status-style | 2 | none | n/a | n/a |

Use 🟢 🟡 🔴 as state only. An empty cell is a finding, not a blank.

## Findings list

Write each one as: the claim, the evidence path, and what would close it.

- A skill nothing references.
- An agent nobody dispatches.
- A rule with no enforcement: rung 1 or 2 with no rung 3 or 4 behind it.
- A hook with no stated rule: something is refused that no document explains.
- A verifier that shares context, model family, or seat with the maker.
- An evaluator with no rubric, no threshold, or no baseline.
- A check whose control cannot fail, or whose red no one has seen.
- A term used but undefined, or defined twice.
- A knowledge base with no writer, or no staleness rule.
- A command no document mentions.
- A rule stated twice at different rungs with different wording.
