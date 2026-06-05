---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Page Laubheimer — 'Onboarding Tutorials vs. Contextual Help.' NN/g, 2023-02-12. https://www.nngroup.com/articles/onboarding-tutorials/"
  - "Jakob N. — '10 Usability Heuristics for User Interface Design,' Heuristic #6 'Recognition Rather Than Recall' and #10 'Help and Documentation.' NN/g. https://www.nngroup.com/articles/ten-usability-heuristics/ , https://www.nngroup.com/articles/help-and-documentation/"
  - "John M. Carroll — *The Nurnberg Funnel: Designing Minimalist Instruction for Practical Computer Skill* (MIT Press, 1990). ISBN 9780262031455. (The 'paradox of the active user.')"
  - "Sarah Richards — *Content Design* (Content Design London, 2017; 2nd ed. 2023). ISBN 9781527209183."
---

# Education in Product (Learnability)

In-product education is the content that **teaches a user how to get value from the product, from inside the product** — concept explanations, help articles, contextual hints, tooltips, sample data, and the docs a user can reach without leaving. The discipline's organizing question is **learnability**: how quickly a new user can understand enough to do useful work, and how a returning user discovers capability they haven't used yet. The hard truth governing the whole area, from John Carroll's _Nurnberg Funnel_ onward, is the **paradox of the active user**: people "want to start using products immediately rather than study instructions" — so education that sits _between_ the user and the task tends to be skipped, and education that arrives _at_ the task tends to land.

> **Scope boundary — read this first.** This file is about the _content and strategy_ of teaching: what to teach, when, and whether it belongs in a doc or in the UI. It deliberately does **not** re-cover two things already owned elsewhere in this skill: (1) the **onboarding / activation** frame — time-to-first-value, the "aha" moment, value-first first-run — lives in `../flows/onboarding.md`; (2) the **mechanics of coachmarks, tooltips, product tours, and walkthroughs** — the forms, their triggers, the memory problem, when tours backfire — live in `../flows/guidance-coachmarks.md`. This file is the _content-design view that sits above both_: the teaching strategy and the doc-vs-in-product decision. Where it touches those patterns, it points to them rather than restating them.

## Just-in-time guidance vs. upfront tutorials

The single most consequential choice in product education is **when** the teaching arrives, and the evidence points one way. NN/g (Laubheimer) frames it as _push_ vs. _pull_ revelation:

- **Upfront tutorials (push)** are shown "out of context, at a moment that is convenient for the system rather than the user." They are "hard to remember when the user needs it," and research finds they "don't result in better task performance." The user reads (or skips) a lesson about a task they aren't doing yet, then has forgotten it by the time the task arrives.
- **Just-in-time guidance (pull)** arrives at the point of need — triggered by the user reaching a complex feature, hesitating, or repeating an error — and is shown in place, against the real UI. Because the information is relevant _now_, it's retained and used.
- **The default is pull.** Prefer education that surfaces when a signal says the user needs it, over a lesson delivered before the need exists. Reserve upfront teaching for the rare case where a user genuinely cannot start without one concept (and even then, make it skippable).
- **Teach concepts, not buttons.** Just-in-time guidance should explain the genuinely non-obvious — a model the user needs, a non-standard gesture — and "skip the obvious stuff." A hint on a self-labeled "Save" button trains users to ignore all hints.

## The doc-vs-in-product question

A recurring decision: when a user needs to learn something, does it belong **in the interface** (a hint, inline help, sample data, a clearer label) or **in documentation** (a help article, a guide, reference docs)? The wrong split either bloats the UI with explanation or buries essential knowledge in a doc nobody opens.

- **Prefer fixing the interface over documenting around it.** The cheapest education is the kind you didn't have to write because the design explains itself. If a doc exists only to explain a confusing label or flow, the real fix is the label or flow (this is the content-design instinct — see `content-design-principles.md` — and the Tesler's-Law point in `../flows/guidance-coachmarks.md`). A help article is not a substitute for a comprehensible UI.
- **In-product for the immediate and task-bound; docs for the deep and reference.** Put in the interface what the user needs _to take the next step right now_ — a one-line hint, an example, a label that needs no explanation. Put in documentation what is _long, occasional, or reference-shaped_: comprehensive how-tos, troubleshooting, edge cases, admin/setup guides a user consults deliberately. Don't dump reference-length content into a tooltip; don't hide a one-line clarification in a doc.
- **Connect the two with a findable backstop.** Jakob N.'s Heuristic #10 (_Help and Documentation_) holds even for the best self-explanatory product: provide help that is "easy to search, focused on the user's task, list[s] concrete steps," and is reachable on demand (a persistent "?" or help surface). The interface handles the moment; the docs handle depth; a clear path links them.
- **Make in-product help recallable, not one-shot.** Anything taught in the UI should be dismissible _and_ retrievable — a user who closed a hint too fast must be able to get it back. (Mechanics in `../flows/guidance-coachmarks.md`.)

## Teaching without blocking

The active-user paradox means the _manner_ of teaching matters as much as the content: education must teach **without standing between the user and the task.**

- **Never gate the product behind a lesson.** A mandatory, un-skippable tutorial wall is the canonical violation — the active user mashes "Skip," so the effort taught nothing and annoyed someone. Always allow skip/defer.
- **Let the interface teach itself.** Recognition over recall (Jakob N.'s Heuristic #6): make options, actions, and state _visible_ so the user doesn't have to be taught and then remember. A well-designed affordance is silent education. The strongest learnability comes from a UI legible enough to need little explanation.
- **Seed the product so it demonstrates itself.** Pre-populating with sample data, a template, or a worked example teaches the end-state by showing it — the user learns by seeing a populated product, not by reading about an empty one. (As an onboarding device this is covered in `../flows/onboarding.md`; as _education_, the point is that a concrete example often teaches better than prose.)
- **Layer it (progressive disclosure).** Offer a short hint that expands to detail on request, rather than front-loading a paragraph. The user pulls more only if they want it.
- **Teach by doing for complex tasks.** When a genuinely multi-step task must be taught, an interactive walkthrough (user performs each step in the real UI, action-gated) beats a passive lesson — doing-it sticks where being-told-it doesn't. (Form details: `../flows/guidance-coachmarks.md`.)

## The cost of tours (and education that doesn't pay for itself)

Education is not free; every piece has a cost in attention, maintenance, and learned-dismissal, and much of it doesn't earn back its cost.

- **The upfront tour is the worst offender.** It interrupts the active user, is forgotten before it's relevant, and is reflexively skipped — high cost, near-zero retention. (The full failure analysis is in `../flows/guidance-coachmarks.md`; the education-strategy takeaway: a tour is rarely the right way to teach, and almost never the _first_ thing to reach for.)
- **Guidance fatigue is a real cost.** When a product over-uses tips, coachmarks, and tours, users learn to dismiss _all_ instructional UI on sight — so even a genuinely useful later hint gets swatted. Every unnecessary teaching moment spends down the budget for the necessary ones. (Treat viral "X% dismissed in Y seconds" figures as unverified marketing claims, not citable research.)
- **Education has a maintenance cost.** A help article or tour describes a UI that changes; stale education that no longer matches the product actively misleads. Content you teach is content you must keep true, or retire.
- **Re-teaching on every release punishes loyalty.** Replaying the whole tour after an update taxes returning users for upgrading; show a single contextual note on what changed instead.
- **The right default is less.** Because education costs attention and maintenance and risks fatigue, the discipline biases toward _teaching less, later, and in context_ — and toward making the interface clear enough that there's less to teach.

## Distinguishing this from the onboarding/coachmark patterns

To keep the boundary crisp (the three files are companions, not duplicates):

| Question | Where it's answered |
| --- | --- |
| _When does value become real? What's the activation action? How do I design first-run?_ | `../flows/onboarding.md` (onboarding & activation) |
| _Which guidance form — tooltip, coachmark, tour, walkthrough? How do they work, when do tours backfire?_ | `../flows/guidance-coachmarks.md` (guidance mechanics) |
| _What should we teach, when, and does it belong in the UI or in docs? How do we teach without blocking, and what does teaching cost?_ | **This file** (education strategy & content) |

## Tells of good vs. bad

| Dimension | Good in-product education | Bad |
| --- | --- | --- |
| **Timing** | Just-in-time, at the point of need (pull) | Upfront lesson before the need exists (push) |
| **Blocking** | Skippable; never gates the product | Mandatory tutorial wall |
| **Doc-vs-UI split** | Immediate/task-bound in UI; deep/reference in docs; linked | Reference dumped in tooltips; one-liners buried in docs |
| **Self-teaching UI** | Affordances + sample data teach silently | Confusing UI propped up by help articles |
| **What's taught** | Genuinely complex concepts; "skip the obvious" | Tooltips on self-evident controls |
| **Recall** | Dismissible _and_ retrievable | One-shot; no way to get help back |
| **Cost discipline** | Teaches less, later, in context | Over-uses tips/tours → guidance fatigue |
| **Freshness** | Education kept true to the product, or retired | Stale docs/tours describing an old UI |
| **Complex tasks** | Interactive walkthrough (learn by doing) | Passive carousel the user skips |

The single test: **does each piece of education arrive when the user needs it, teach something the interface can't make obvious, and let the user keep working?** If a lesson blocks the task, explains the obvious, can't be recalled, lives in the wrong place (doc vs. UI), or props up a UI that should have been made clearer — the education has cost more than it taught. The deepest tell, shared with the guidance layer: heavy reliance on tutorials and tours usually signals an interface that should have been made self-explanatory instead.
