# Work items

Tickets, bug reports, feature requests, chores, spikes, issue titles, labels, and definitions of done: the units of work an agent picks up. [Core rules](core.md) apply to all of them. This is the highest-leverage document family in an agent workflow and the one most often written as loose prose.

| Type | Shape | Machine-checked |
|---|---|---|
| Agent task / ticket / work order | Fixed schema: goal, context pointers, constraints, definition of done, out of scope, verification command. Definition of done as Gherkin or an executable check. | none |
| Bug report | [bug.tmpl](../../assets/templates/bug.tmpl): environment, numbered reproduction steps (full STE, one action each), expected, actual, evidence, severity and impact. | none |
| Feature request / enhancement | [feature-request.tmpl](../../assets/templates/feature-request.tmpl): problem in Plain Language, a user story with Gherkin acceptance criteria, the PRD requirement ID. No proposed solution in the body. | none |
| Task / chore ticket | The agent-task schema. The definition of done is checkable by a command or a test, not by judgment. | none |
| Spike / investigation | [spike.tmpl](../../assets/templates/spike.tmpl): question, time box, the decision it feeds, the deliverable. Closes with the finding, not with "done". | none |
| Issue titles | `<type>: <scope>: <imperative summary>` under 72 characters, type one of bug, feat, chore, spike. | none |
| Issue / PR labels | A closed, documented vocabulary with one axis per label family: type, priority, status, area. The labels are glossary terms. | none |
| Definition of done / acceptance checklist | Gherkin or a yes or no checklist where every item is verifiable. It sits in the issue template, so it exists before work starts. | none |

## Rules

1. Reproduction steps are the one part a model executes literally. Write them in full STE: numbered, one imperative action per step, from a clean checkout.
2. A bug report with no reproduction is labeled as such (`no-repro`), not filed as a bug.
3. A feature request states the problem, not the fix. A request that says "do X via Y" gets Y built; put Y in a comment or a decision record.
4. Every done-condition names the command or test that proves it.

## This repository's tickets

SDLC Lite tickets already follow this family. The front matter of the ticket templates in `plugins/sdlc-lite/skills/ticket/templates/*.md` (`feature.md`, `bug.md`, `chore.md`, `spike.md`, `idea.md`) is the source; [ticket.json](../../assets/schemas/ticket.json) states the same fields as a schema and adds nothing. When the two differ, the templates and `tickets.py` win, and the schema is fixed to match.

| Template front matter | Schema property | Values |
|---|---|---|
| `id: T-0000` | `id` | `T-NNNN`, stamped by `tickets.py new` |
| `title:` | `title` | free text |
| `type:` | `type` | feature, bug, chore, spike, idea |
| `status:` | `status` | proposed, ready, claimed, paused, blocked, done, dropped |
| `size:` | `size` | L1, L2, L3, L4 (L5 reserved); the ticket's level |
| `priority:` | `priority` | P1, P2, P3 |
| `depends:` | `depends` | list of `T-NNNN`, `file:<path>`, `cap:<name>` |
| `created:` | `created` | `YYYY-MM-DD` |
| `area:`, `claimed_by:`, `paused_reason:` | optional properties | `claimed_by:` goes with status claimed, `paused_reason:` with status paused |

The template body sections map to the agent-task schema: `## Goal` is the goal, `## Context` the context pointers, `## Constraints` the constraints and out of scope, and the acceptance criteria the plan writes per step are the definition of done with its verification command. A bug template's `## Repro`, `## Expected`, and `## Actual` are the bug report core; [bug.tmpl](../../assets/templates/bug.tmpl) adds environment, evidence, and severity for a consumer repo's tracker.
