# Bounded traversal and exposure

Resolve a concrete intent through an explicit route, a known ID/path, or a scoped
local index. When no index exists, inspect the nearest known entry and perform a
bounded search in that scope. Report its boundary. Do not recursively enumerate
an entire corpus by default. Ambiguous targets require disambiguation, not a
silent first match. A named implementation file is an appropriate direct start. Select by action and
concern as well as target: guidance-only tasks should not eagerly load full APIs;
implementation routes must still deliver their required contracts.

Load governing contracts and required dependencies before the target is used.
Optional references and examples are not eager dependencies. Keep a visited set;
record why each expansion is necessary and stop at the first blocked requirement.
Depth L0-L5 is a description, not a mandatory sequence of six reads.

| Condition | Response |
|---|---|
| No registry | Use a known local entry or targeted search; do not create a registry automatically |
| Missing target or inaccessible dependency | Stop the affected route; request the exact missing item or permission |
| Stale summary or source hash | Mark freshness unverified; inspect the source within budget, then refresh metadata only with authorization |
| Duplicate IDs or aliases | Resolve ownership/identity before choosing a target |
| Dependency cycle | Report the cycle; do not loop or silently drop a required dependency |
| Conflicting governing declarations | Check governing scope and ownership; report unresolved clauses and the decision needed, pause dependent work and continue independent work |
| Read/byte/time budget exhausted | Return incomplete with the unresolved requirement and smallest next read; no success claim |
| Submission telemetry absent | Returned is known; submitted, influence and retention remain unknown |
| Known implementation target | Read required governing scope then the source; skip irrelevant abstracts |

The local replay tool uses read count and UTF-8 byte budgets. It does not estimate
model tokens or latency. The caller chooses budgets per task. A hash pass establishes
byte identity, not semantic freshness. Metadata validation bytes are reported
separately from the simulated context reads.

Exposure ledger fields: artifact ID, source location/revision/hash, operation,
returned bytes, explicit submission receipt if present, and reason. States are
not inferred from each other. Record compaction or removal only when the harness
provides it. A proposed assembly is not proof of actual submission.

Use the declared authority process for unresolved conflicts. Current implementation
is evidence of behavior, not an automatic ruling about intended behavior. Reconcile
contracts when authorized; do not invent precedence.

## Delivery sufficiency and changing scope

Before action, identify the task’s minimum usable contract: governing rules, required
inputs or parts, dependencies, prerequisites, supported operations and working entry.
An index description can route to that contract but does not substitute for it.
For example, discovering a menu name does not establish its trigger, keyboard
behavior, portal prerequisite or implementation API. Read the relevant contract
sections, rather than automatically reading every implementation file.

Budget each return, each combined batch and cumulative assembled context. A set
of individually small parallel returns can still overflow their shared envelope.
Record the actually delivered portion, not the bytes the source could supply.
Keep transport clipping separate from intentional projection or pagination limits.
Track fields/record IDs, page/range, source revision, continuation and completeness.
Follow returned continuation/read instructions, including budget overrides. A batch
may exit successfully while required documents remain pending. Avoid combining
returns or truncating them with head/tail to manufacture apparent completeness.
Recover the missing text after host clipping; reuse already-delivered bodies rather
than opening the same documents again. Request the smallest missing page or governing
section; do not retry a whole large source blindly. See [replay delivery contract](evaluation.md#delivery-and-scope-extensions-suite-v1-replay-output-v2).

When a task adds a component, behavior or runtime constraint, recompute its required
context. Reuse unchanged, adequately covered evidence, and retrieve newly applicable
policy/dependencies before action. A prior successful retrieval does not permanently
cover future task scope. If context was compacted, retained coverage needs a receipt;
the local replay's reuse is simulated assembly, not proof of model retention.
