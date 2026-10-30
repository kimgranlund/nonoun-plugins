# SDLC integration

Read only when SDLC is present. Other projects should use their existing work and verification records.

Progressive Context owns durable intent, capability boundaries, context routes, and qualification claims. SDLC owns work execution: tickets, plans, runs, verification, and work closure. SDLC's `onboard` skill is the setup step for a repository's entry files and docs layout.

- Ticket: a desired change; link the capability contract from its Context section.
- Plan: steps toward that change; derive checks from the contract's criteria.
- Run: implementation attempt; retain its existing handoff and result artifacts.
- Verification: evidence for a named change; reuse it in the assessment when its scope and revision binding suffice.
- Roadmap: generated work ordering plus separately authored priorities. Dependency order cannot infer strategy or user commitment.

For a repeated process with a useful context boundary, a task handoff may also link a reusable [workflow definition](workflow-stages.md) and its relevant stage heading. The definition supplies expected inputs and outputs; the handoff supplies this task's actual paths, decisions, and unresolved findings. SDLC's plan steps and `steps.py next` still own build and verification routing. A stage boundary never advances a task or qualifies a capability by itself.

One capability can have several tickets; one ticket can touch several capabilities. Ticket closure does not publish a capability, and an accepted capability may still have open enhancement tickets. Do not synchronize independent status flags or duplicate the SDLC board in context files.

Example: a ticket adds keyboard selection to an existing invoice review capability. Its plan links the contract's selection criterion; its verifier result is referenced by a new assessment of the changed revision. The contract retains its stable ID after the ticket closes.
