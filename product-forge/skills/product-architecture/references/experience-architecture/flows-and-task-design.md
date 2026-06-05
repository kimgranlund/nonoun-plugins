---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Jesse G., *The Elements of User Experience* (New Riders, 2002/2010) — the structure plane: interaction design as the design of how the system behaves in response to the user."
  - "NN/g — Flow Charts & User Flows (nngroup.com); UX Mapping Methods Compared (nngroup.com/articles/ux-mapping-cheat-sheet)."
  - "Alan C., Robert Reimann, David Cronin, *About Face: The Essentials of Interaction Design* (Wiley) — goal-directed flows and the role of error states."
  - "Don N., *The Design of Everyday Things* (Basic Books, rev. ed. 2013) — error as a property of the system, the gulfs of execution and evaluation."
---

# Flows & Task Design

This is the working method for designing at the **flow** level — the structure plane in Jesse G.'s stack, where you decide how the system behaves as a user moves through a task. A flow is the sequence of screens, decisions, and system responses that carries a user from intent to completion. Designing flows is a design act in its own right, distinct from designing screens: you can have beautiful screens strung together into an incoherent flow, and you can have plain screens in a flow so well-sequenced it feels effortless. The discipline here is **modeling the whole flow before drawing any screen** — mapping the happy path, then deliberately enumerating every branch, error, and dead-end the happy path conveniently ignores. The tell of an amateur flow is that only the happy path was designed; the tell of a professional one is that the edges were designed _on purpose._

## Task flow vs. user flow vs. wireflow

Three flow artifacts get conflated. Pick by what you're trying to reason about.

| Artifact | Shows | Use it to |
| --- | --- | --- |
| **Task flow** | A single generalized path through a task — no branching by user type, one happy line of steps | Establish the canonical sequence; align the team on "the task is these N steps" |
| **User flow** | The branching paths different users/decisions take through a task, with decision points and outcomes | Find where the flow forks, where edges live, where users drop |
| **Wireflow** | A user flow where each node is a wireframe, not a label — flow + screen layout together | Bridge structure (flow) to skeleton (screens) when the two must be reasoned about jointly |

Start with a task flow to agree on the spine, expand to a user flow to expose the branches, and only move to wireflows when you're ready to commit screen layout.

## The happy path is the smallest part of the design

The **happy path** is the flow when everything goes right: the user has permission, the network holds, the input validates, the resource exists, the payment clears. It is necessary but it is the _minority_ of real sessions. The architectural work is the rest. For every step on the happy path, interrogate it with a fixed set of questions:

- **Authorization:** What if the user isn't allowed to do this? (logged out, wrong role, expired session)
- **Input:** What if the input is invalid, empty, malformed, or too large?
- **Existence:** What if the thing they're acting on was deleted, moved, or never existed (a stale link, a 404)?
- **System:** What if the request is slow, times out, fails, or partially succeeds?
- **Conflict:** What if someone else changed the data first, or the user has two tabs open?
- **Abandonment:** What if the user leaves mid-flow and comes back? (this is where flow design meets `states-and-continuity.md`)

Each "what if" that you answer becomes a designed branch. Each one you skip becomes a dead-end your users discover for you in production.

## Decision points and branches

A **decision point** is a fork in the flow — a place where the path diverges based on a user choice or a system condition. Good flow design makes decision points few, clear, and recoverable.

- **Minimize forks on the happy path.** Every decision the user must make is interaction cost and a chance to choose wrong. Default aggressively; ask only what you cannot infer.
- **Distinguish user-choice forks from system-condition forks.** A user choosing "personal vs. business account" is a designed branch; the system hitting an auth failure is an error branch. They look the same on a diagram but are designed differently — one is offered, one is handled.
- **Every branch must rejoin or resolve.** A branch either merges back into the main flow, reaches a legitimate terminal state (success/done), or is a designed off-ramp. A branch that just stops is a dead-end.

## Dead-ends: the defect class flows exist to eliminate

A **dead-end** is a state from which the user cannot make progress and cannot recover within the flow: an error screen with no next action, a permission wall with no request-access path, a "no results" with no way to broaden, a confirmation that traps the user with no exit. Dead-ends are the single most common flow defect and the easiest to find once you look. The rule: **every state must offer at least one forward or recovery action.** This connects directly to Don N.'s framing — a good system minimizes the **gulf of execution** (the user can always see what to do next) and the **gulf of evaluation** (the user can always tell what just happened and whether it worked). A dead-end is a gulf the design left open.

Don N.'s reframing of error is load-bearing for flow design: **error is a property of the system, not a failing of the user.** "When people err, change the system so that type of error will be reduced or eliminated." This means error branches are not afterthoughts bolted on — they are first-class parts of the flow, designed to prevent the error where possible (constraints, good defaults, confirmation only for destructive acts) and to recover gracefully where not (clear message, preserved input, an obvious next step).

## Flow diagramming as a design act

Drawing the flow _is_ designing it — the diagram surfaces problems no screen mockup can. A workable flow diagram uses a small, consistent vocabulary:

```text
   ( start )──▶[ screen / step ]──▶< decision? >──yes──▶[ next step ]──▶(( success ))
                                          │
                                          no
                                          ▼
                                   [ error / branch ]──▶[ recovery ]──┐
                                          │                            │
                                          └──────── rejoins ───────────┘

   shapes:  (  )  terminator (start)        (( )) terminal success/done
            [  ]  screen or system step      <  > decision / fork
            ───▶  directed transition        ⚠ flag: any node with no outgoing arrow = DEAD-END
```

What the diagram reveals that screens hide: **orphan nodes** (no way in), **dead-ends** (no way forward), **unbalanced forks** (a decision with a designed "yes" and an undesigned "no"), **loops with no exit**, and **excessive depth** (a task that should be 3 steps sprawling to 9). Reviewing the diagram is faster and cheaper than reviewing the screens, and it catches structural faults before they're expensive.

## What to check (good vs. bad)

| Dimension | Bad flow | Good flow |
| --- | --- | --- |
| **Coverage** | Only the happy path is designed | Every happy-path step has its edges/errors enumerated and handled |
| **Dead-ends** | Error and empty screens with no next action | Every state offers a forward or recovery action |
| **Decision points** | Many forks, unclear defaults, user must decide constantly | Few forks, strong defaults, ask only the un-inferable |
| **Branch resolution** | Branches that just stop | Every branch rejoins, resolves, or is a designed off-ramp |
| **Error stance** | Errors blame the user; input is lost on failure | Errors are prevented or recovered; input is preserved; message says what to do |
| **Depth** | Task sprawls across many steps | Step count is the minimum the task honestly requires |
| **Diagram** | No flow diagram, or one with orphans/loops | A clean diagram with no orphans, no dead-ends, balanced forks |
| **Resumability** | Abandon mid-flow = start over | Mid-flow abandonment is a designed case (see continuity) |

The fastest single test: take the flow diagram and try to find a node with no outgoing arrow. Every such node is a place a real user will get stuck. A flow with zero of them is the baseline, not the achievement.

## One labeled caveat

The flow taxonomy (task flow / user flow / wireflow) follows NN/g's mapping vocabulary and is standard practice. The happy-path-plus-edges discipline and the dead-end framing are widely taught interaction-design practice rather than a single named framework; they are presented here as method. The specific Don N. claims — error as a system property, the gulfs of execution and evaluation — are from _The Design of Everyday Things_ (rev. ed. 2013) and are accurately characterized, though the verbatim phrasing was cross-checked against the well-known summaries of the book rather than a paginated edition in this session. Alan C.'s _About Face_ is cited for goal-directed flow design and the primacy of error handling; confirm specific page references against the print edition if quoting directly.
