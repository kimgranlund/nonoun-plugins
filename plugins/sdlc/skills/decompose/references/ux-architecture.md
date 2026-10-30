# Domain: UX Architecture (within-product IA)

> `decompose` domain reference. Method depth in `method.md`. Scope: **what screens and
> states EXIST and what each hosts** — the product's information architecture. The journey
> *between* screens — entry, transitions, exits declared as a state machine — is out of
> scope here; this reference stops at what screens/states exist and what each hosts. Model that
> journey with `ui:break-down-flow` (separate `ui` plugin, if installed) instead — its `*.flow.json` card and graph-liveness/safety
> checks (unreachable states, dead ends, orphan exits, missing recovery) are a different mechanism
> for a different consumer, not a deeper version of this one. · 2026-07-06, named 2026-07-19

## OUTSIDE-IN axis (structure)

`product → sections → screens → states`

- **product** — the whole surface area under decomposition (the IA root).
- **sections** — the named areas of the product (onboarding, account, billing, recovery).
- **screens** — a place that presents one decision or step.
- **states** — the variants of a screen (empty, loading, error, success, partial).

## INSIDE-OUT axis (behavior)

`user-goals → tasks → interactions → feedback`

- **user-goals** — what the person is trying to accomplish (not features).
- **tasks** — the concrete steps that satisfy a goal.
- **interactions** — the input acts a task requires.
- **feedback** — what the system shows so the user knows the task's result/system status.

## Stop rule

Stop dividing when a **screen presents one decision** and a **task is one user intent**. A screen asking two unrelated decisions is two screens; a "task" with no observable feedback is unfinished.

## Cross-check (defect quadrant)

- Every task must have a screen/state to occur in → else `UNHOSTED` (a step with no place to happen).
- Every leaf screen/state must serve a task **or** carry a `justify` (`transition`, `confirmation`) → else `UNJUSTIFIED-LEAF` (a screen for the org chart, not the user).
- A task with no `feedback` interaction is a coverage gap even if hosted (no failure-support / status visibility).
- The *ordering* of screens, the verbs that move between them, recovery, and resume are NOT checked here — model that journey with `ui:break-down-flow` instead (see the header note above).

## Worked pass (the account-recovery section)

OUTSIDE-IN: `recovery` (section) → `{request-screen, sent-screen, reset-screen}` → `reset-screen` → states `{form, error, success}`.
INSIDE-OUT goals/tasks: `request a reset link`, `set a new password`, `see why a reset failed`.
Map: `see why a reset failed` hosts on `reset-screen:error`. `sent-screen` hosts no task — it exists to confirm the send → tag `justify:"confirmation"`. Re-check → clean.

```json
{
  "domain": "ux-architecture",
  "nodes": [
    {"id":"request","label":"request-screen","leaf":true},
    {"id":"sent","label":"sent-screen","leaf":true,"justify":"confirmation"},
    {"id":"reset","label":"reset-screen"},
    {"id":"reset_err","label":"reset:error","leaf":true}
  ],
  "actions": [
    {"id":"req","label":"request reset link"},{"id":"setpw","label":"set new password"},
    {"id":"whyfail","label":"see why reset failed"}
  ],
  "hosts": [
    {"action":"req","node":"request"},{"action":"setpw","node":"reset"},
    {"action":"whyfail","node":"reset_err"}
  ]
}
```
