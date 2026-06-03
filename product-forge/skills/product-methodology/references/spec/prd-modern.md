---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Lenny Rachitsky, *My favorite product management templates* and *Examples and templates of 1-pagers and PRDs*, Lenny's Newsletter. https://www.lennysnewsletter.com/p/my-favorite-templates-issue-37 · https://www.lennysnewsletter.com/p/prds-1-pagers-examples"
  - "Lenny's Product Requirements template (Atlassian Confluence template, authored by Lenny Rachitsky). https://www.atlassian.com/software/confluence/templates/lennys-product-requirements"
  - "Marty C., *How To Write a Good PRD*, Silicon Valley Product Group. https://www.svpg.com/wp-content/uploads/2024/07/How-To-Write-a-Good-PRD.pdf"
  - "Marty C., *Revisiting the Product Spec* (2006), Silicon Valley Product Group. https://www.svpg.com/revisiting-the-product-spec/"
  - "Marty C., *Inspired: How to Create Tech Products Customers Love*, 2nd ed. (Wiley, 2018)."
---

# What a good modern PRD contains

A modern product requirements document is not a feature list with a cover page. It is the artifact that lets a team commit to building something without re-deriving _why_ and _for whom_ every time the work gets hard. This reference defines what a good one contains, why each part earns its place, and the single test that separates a usable PRD from a document that merely looks complete. The depth here is conceptual — the formal authoring engines that turn these contents into a finished, schema-validated PRD or spec are the global `plan-prd` and `plan-spec` skills; this library is a peer that names what _belongs_ in the artifact and why, not a duplicate of those engines.

## The shift: outcome-framed, not feature-framed

The defining property of a good modern PRD is that it is framed around the **outcome to achieve**, not the **output to ship**. Marty C. draws the line bluntly: the old "project model" is "all about output" — stakeholders hand down a prioritized list of features, "a feature team product manager creates a specification (e.g. a PRD) of that feature," a designer makes it pretty, and engineers build it. The "product model," by contrast, "is all about outcomes," where a team is given "an important problem to solve" and works to "discover a solution worth building" for which there is "evidence we can deliver the necessary outcome." Marty C. has made this distinction since 2007, and it is the through-line of _Inspired_ and _Transformed_.

The practical consequence for the document: a feature-framed PRD opens with "build X" and spends its pages specifying X. An outcome-framed PRD opens with the **problem and the change in customer/business behavior that would count as solving it**, and treats any particular feature as a current best hypothesis about how to get there — explicitly falsifiable, not the point of the document. If your PRD could be satisfied by shipping the listed features even if no customer behavior changed, it is feature-framed, and you have written a build order, not a requirements document.

## The contents (and what each part is for)

These are the load-bearing sections of a modern PRD. The framing of the first cluster — problem, why-now, success, audience — follows the structure of Lenny Rachitsky's widely-used Product Requirements template, which is built on what he calls "a three-step framework to solving problems" and pushes teams to "align on the problem space before going into solutions." Each section answers a question; the section exists only to answer it.

| Section | The question it answers | Why it earns its place |
| --- | --- | --- |
| **Problem** | What problem is this solving, for whom, and how do we know it's real and worth solving? | Rachitsky calls nailing the problem statement "the single most important step" and "deceptively easy to get wrong." Everything downstream inherits its errors. |
| **Target user** | Who, specifically, are we building for? | A solution that is "for everyone" is positioned for no one; the user definition scopes every later trade-off. |
| **Outcomes / success metrics** | How will we _know_ if we solved the problem? | Converts intent into a measurable target, so "done" means "the outcome moved," not "the feature shipped." |
| **Non-goals** | What is explicitly _out_ of scope? | Scope is defined as much by what you refuse as by what you commit to; non-goals pre-empt the scope creep that silently re-frames the work. |
| **Risks / assumptions** | What must be true for this to work, and what could sink it? | Names the bets the plan rests on, so they can be tested in discovery rather than discovered in production. |
| **Open questions** | What do we not yet know, and who owns finding out? | Makes uncertainty explicit and assignable instead of papering over it with false confidence. |

The first four come close to Rachitsky's own headings — "What problem is this solving?", "How do we know this is a real problem and worth solving?", "How do we know if we've solved this problem?", "Who are we building for?" The last two — risks/assumptions and open questions — are the discipline that keeps a PRD honest about its own limits; a document with no stated risks and no open questions is almost always overconfident rather than complete.

### Outcomes and success metrics, specifically

This is the section teams most often fake. A real success metric is a **behavioral or business measurement that would move if and only if the problem were actually solved** — and ideally it is paired with a counter-metric or guardrail so that gaming one number is visibly caught by another. "Ship the redesign" is not a success metric; "task-completion rate for first-time users rises from X to Y, without a rise in support tickets" is. The test: read the metric, then ask whether you could hit it while the underlying customer problem remained untouched. If you could, the metric is a vanity proxy and the PRD's spine is hollow.

### Non-goals, specifically

Non-goals are not a courtesy; they are a structural defense. Every problem worth solving sits adjacent to three others that are tempting to fold in, and each fold doubles the cost and halves the clarity. A crisp non-goal ("we are _not_ solving for enterprise SSO in this release") does two jobs at once: it stops scope creep before it starts, and it tells reviewers what _not_ to object to the absence of. A PRD without non-goals invites every stakeholder to imagine their pet adjacency is in scope.

## The "could a team act on this without re-deriving it" test

The single test that distinguishes a good modern PRD from a complete-looking one:

```text
Hand the document to a competent team that was NOT in the room when it was written.
Ask: can they build the right thing — and, more importantly, make the dozens of
small judgment calls that come up mid-build — WITHOUT coming back to re-derive
the reasoning the author already did?

PASS if, for each call, the team can find the answer (or a clear way to get it) in:
  - the PROBLEM and TARGET USER  → "who is this really for, what hurts?"
  - the OUTCOME / METRIC          → "what counts as winning?"
  - the NON-GOALS                 → "is this adjacent thing in scope? (no)"
  - the RISKS / ASSUMPTIONS       → "what are we betting on here?"
  - the OPEN QUESTIONS            → "is this a known unknown, and who owns it?"

FAIL if the team must reconstruct the author's intent from scratch — if the doc
records WHAT to build but not enough of WHY and FOR-WHOM to resolve the build-time
trade-offs the author has already reasoned through.
```

This test is why a PRD is outcome-framed and why risks and open questions are mandatory: those sections are exactly the parts a downstream team would otherwise have to re-derive. A feature list tells a team what to type; it does not tell them which of two reasonable interpretations to choose when the spec is silent, and specs are silent constantly. The reasoning — problem, user, outcome, what's deliberately excluded, what's uncertain — is the part that does not survive being left out. If the document forces re-derivation, it has failed at the one job that justifies writing it down.

## On format and weight: the spec is overdue for renovation

A modern PRD is deliberately light. Marty C. argues the product spec "is long overdue for a renovation" and that he moved away from the "heavy-weight PRD" toward "a light-weight high-fidelity prototype as the basis for your product spec" — in his framing, "the majority of the product spec should be the high-fidelity prototype," because a prototype "can eliminate problems with varied interpretations that lengthy product requirements elicit." This does not abolish the PRD; it relocates the _functional, interaction, and visual detail_ into a prototype that communicates more precisely than prose, and leaves the PRD to carry what a prototype cannot: the problem, the target user, the outcome, the non-goals, the risks, and the open questions. The heavyweight, exhaustively-specified PRD is the anti-pattern; the lean problem-and-outcome PRD paired with a high-fidelity prototype is the modern shape.

Marty C.'s deeper warning applies regardless of format: "whether you use stories or PRDs doesn't matter; the issue is whether the product manager is just making things up ... or are they credible and have they actually discovered the right product." A beautifully structured PRD built on undiscovered assumptions is still fiction. The document is a vehicle for validated thinking, not a substitute for it.

## Failure modes to watch

- **The feature list in disguise** — pages of "the system shall…" with no stated outcome the features are meant to produce. Passes a completeness checklist; fails the act-without-re-deriving test.
- **The hollow metric** — a success metric you could hit while the customer problem stays untouched (ship-count, page-views, "engagement" with no guardrail).
- **No non-goals** — every reviewer assumes their adjacency is in scope; the document cannot defend its own boundaries.
- **No risks, no open questions** — false confidence; the bets the plan rests on are never named, so they are tested in production instead of discovery.
- **Heavyweight detail, light thinking** — exhaustive functional specification standing in for a discovered, evidence-backed solution. Marty C.'s "making things up" failure, dressed in thoroughness.
