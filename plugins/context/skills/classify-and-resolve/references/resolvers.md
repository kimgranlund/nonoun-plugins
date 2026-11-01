# Resolvers

Load this when you add or change a resolver, raise or lower its autonomy, name a promotion gate, design an escalation path, or read an `autonomy-matrix`, `unknown-gate`, `gate-not-passed` or `auto-unclassified` finding. Field names are defined in [model.md](model.md); stages are in [growth.md](growth.md).

## The contract

A resolver is whatever handles one class: a person, a runbook, a script, a specialist agent, a team's queue. Its contract is declared in the pipeline file before it handles anything:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable; routes and logs name it. |
| `accepts` | yes | The class ids routed to it. The resolver on `unclassified_route` accepts `unclassified`. |
| `output_type` | yes | What it produces: a reply draft, an incident record, a filed document, a closed ticket. |
| `side_effects` | yes | `none` (it only produces output for someone to use), `reversible` (it changes state that can be undone: a label, a queue move, a draft), `irreversible` (it changes state that cannot be undone: a sent email, a refund, a deletion, a filing with a regulator). |
| `autonomy` | yes | `manual` (a person does it), `suggest` (it proposes, a person approves or corrects), `auto` (it acts alone). Every new resolver starts at `manual`. |
| `promotion_gate` | per the matrix | The id of a gate in `evaluation-system`'s `gates.yaml` that guards this resolver's autonomy. |
| `review_sample_rate` | per the matrix | The share of `auto` decisions a person reviews after the fact, 0 to 1. |
| `policy` | no | What it must and must not do, as `controlled-natural-language` statements: "The refund desk shall not refund more than the disputed charge." |

Judge `side_effects` by the worst thing the resolver can do, not the usual case. A resolver that drafts replies but can send them is `irreversible`.

## Autonomy matrix

| side_effects | manual | suggest | auto |
|---|---|---|---|
| none | allowed | allowed | requires passed `promotion_gate` |
| reversible | allowed | allowed | requires passed `promotion_gate` |
| irreversible | allowed | requires passed `promotion_gate` | requires passed `promotion_gate` **and** `review_sample_rate` > 0 |

- `manual` is always allowed and is the default. `suggest` is free where a wrong suggestion costs a person's minute, and gated where an approved-without-reading suggestion can do lasting harm.
- "Passed" means the gate's `status` in `gates.yaml` is `passed`, as `evaluation-system` records it. This skill reads that status and never computes the metric behind it. Without a registry no gate can pass, so autonomy stays at the free cells.
- Promotion is per resolver. Gating the billing resolver says nothing about the outage resolver.
- A gate guards one slice: write it on the slice for the resolver's class (`slice: billing`), not `all`, so one weak class cannot ride on the aggregate.
- Demotion needs no gate. When a gate fails, a sample review finds harm, or the class definition changes, move the resolver back to `manual` or `suggest` in the same change that records why.

## Escalation design

Every resolver has a way out that is not "do it anyway":

- **Abstain before dispatch.** Classification uncertainty belongs to the cascade (`abstain_below`, a human step, `unclassified_route`), not to the resolver.
- **Escalate after dispatch.** A resolver that receives an item it cannot handle logs `status: escalated` and hands it on (to a person, a second-line resolver, the unclassified queue). An item that is not its class at all is `rejected` with `corrected_label` naming the class it should have had; that record is the misroute signal.
- **Defer.** `deferred` parks an item with a reason, for example waiting on the customer. A deferred item is still owned; the unclassified queue defers until a class decision exists.
- **The unclassified route is human.** It leads to a `manual` or `suggest` resolver a person works. An `auto` resolver there would turn abstention back into guessing (`auto-unclassified`).
- **Sample review.** For `irreversible` + `auto`, a person reviews `review_sample_rate` of the decisions after the fact and logs `corrected_label` on each wrong one. Those corrections become regression cases through `logs_to_cases.py`.
- **Low-confidence policy.** Write it as CNL statements on the resolver or the step, so it can be reviewed: "If the confidence is below 0.8, then the class is unclassified."

## Examples across domains

### Software support or incident triage: runbooks and humans

```yaml
resolvers:
  - {id: on-call, accepts: [outage], output_type: an incident record, side_effects: none, autonomy: manual}
  - id: restart-runbook
    accepts: [stuck-worker]
    output_type: a restarted worker and a log entry
    side_effects: reversible
    autonomy: auto
    promotion_gate: stuck-worker-autonomy       # slice stuck-worker, threshold 0.98, min_n 200
  - id: refund-bot
    accepts: [duplicate-charge]
    output_type: a refund of the duplicate charge
    side_effects: irreversible
    autonomy: suggest
    promotion_gate: duplicate-charge-suggest
    policy:
      - The refund bot shall not refund more than the duplicate charge.
```

The runbook restarts workers alone once its gate passes; restarts are reversible. The refund bot stays at `suggest` behind its own gate, because a refund cannot be taken back; reaching `auto` would also need `review_sample_rate`.

### Document intake for a policy or legal corpus

`filing-clerk` (`accepts: [nda]`, `side_effects: reversible`, it moves a document into a folder) reaches `auto` behind gate `nda-filing`. `regulator-submission` (`accepts: [breach-notice]`, `irreversible`) stays `manual` indefinitely: the gate exists, but the owner decided that no pass rate justifies sending a regulator notice without a lawyer, and the contract records that in `policy`.

### Agent routing

Specialist subagents are resolvers. `docs-writer` (writes a draft for review) is `none`; `code-change` (opens a branch) is `reversible`; `deploy-agent` (ships to production) is `irreversible`. The router may let `docs-writer` act alone after its gate passes, while `deploy-agent` needs a gate even to suggest and, at `auto`, a `review_sample_rate` such as 0.1 with a named reviewer.
