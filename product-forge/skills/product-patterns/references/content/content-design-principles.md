---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Sarah Richards, *Content Design* (Content Design London, 2017; 2nd ed. 2023). ISBN 9781527209183. https://contentdesign.london/the-content-design-book"
  - "PlainLanguage.gov — Federal Plain Language Guidelines, and the Plain Writing Act of 2010 (P.L. 111-274). https://www.plainlanguage.gov/guidelines/ , https://www.govinfo.gov/app/details/PLAW-111publ274"
  - "Digital.gov — 'An introduction to plain language.' https://digital.gov/resources/an-introduction-to-plain-language/"
  - "NN/g — 'Match Between the System and the Real World (Usability Heuristic #2)' (Jakob N. / Maria Rosala). https://www.nngroup.com/articles/match-system-real-world/"
  - "Torrey P., *Strategic Writing for UX* (O'Reilly, 1st ed. 2019; 2nd ed. 2025) — the dual-goal premise (name both the user's goal and the organization's goal for a screen) and the voice chart. https://www.oreilly.com/library/view/strategic-writing-for/9781492049388/"
---

# Content Design Principles

Content design is the discipline of deciding **what content best serves a user's need at a given moment, and in what form** — and only then writing it. The term and the practice come from Sarah Richards, who led the Government Digital Service team that consolidated 400+ UK government websites into GOV.UK between 2010 and 2014. Her load-bearing reframe: you don't start from what the organisation wants to say; you start from the user need and the job the user is trying to do, then give them "the content they need, at the time they need it, in a way they expect." This is a **product-side UX-writing discipline** — the words and structure that help someone complete a task in the interface — and it is distinct from brand voice and brand identity, which belong to brand-forge (see the boundary note below).

> The framing to hold onto: content design treats the words in the product as **a designed material, not decoration applied afterward.** A label, a heading, a paragraph of help is a component with a job — and like any component, it is designed from the user's need, prototyped, tested, and cut if it doesn't earn its place. "What do we want to tell people?" is the wrong opening question; "what does the user need to know or do here?" is the right one.

## Content design vs. copywriting: not the same job

The two are routinely conflated, and the conflation produces clever interfaces that don't work. The distinction, drawn from Richards and the broader content-design field:

- **Copywriting persuades.** Its job is to sell, to move, to make the reader feel — it serves the organisation's message and is often measured by conversion or response. Cleverness, wordplay, and tone are legitimate tools because the goal is persuasion.
- **Content design serves the task.** Its job is to help the user understand and act — it serves the user's need and is measured by task completion, comprehension, and reduced support load. Cleverness that costs comprehension is a defect, not a flourish.
- **The overlap is real but the centre of gravity differs.** A product has both: a marketing page may be mostly copywriting; an error message, a form label, or a settings screen is almost entirely content design. The failure mode is applying copywriter instincts (make it punchy, make it on-brand, make it surprising) to interface text whose only job is to let someone finish a task.

The single sharpest test of which mode you're in: **if a user reads this wrong, do they fail to feel something, or fail to do something?** If they fail to _do_ something, you're in content-design territory and clarity wins outright.

## Start from the user need and the job

Content design begins with research into the actual need, expressed in the user's own words — not the organisation's framing of it. Richards' method is to write the need as a user-need statement and design content against it, then verify against real data on how users search for and digest the information.

- **Name the need as a job, not a topic.** "Renew a passport" (a job) tells you what content must enable; "Passport information" (a topic) is an org-shaped bucket that invites a content dump.
- **Use the user's words, not the institution's.** If users search "how much does it cost," the heading is about cost, in those words — not "Fee schedule." This is the content-design face of Jakob N.'s Heuristic #2, _Match between the system and the real world_: "speak the users' language, with words, phrases, and concepts familiar to the user, rather than system-oriented terms."
- **Answer the question, then stop.** Content earns its place by serving a need; if no user need maps to a paragraph, cut it. GOV.UK's discipline was ruthless deletion — content with no demonstrated need is removed, not reworded.
- **Pick the right form for the need, not the default form.** Content design is medium-agnostic: the answer to a need might be a table, a calculator, a short video, a single sentence, or a diagram — prose is one option among several, not the assumed one.

## Clarity over cleverness

This is the field's first principle and the one most often violated in the name of "voice." Plain, unambiguous, task-serving language beats witty language wherever the user is trying to accomplish something. PlainLanguage.gov's working definition — codified in the US Plain Writing Act of 2010 — is communication the audience "can understand the first time they read or hear it"; the Act requires federal writing that is "clear, concise, well-organized." Applied to product:

- **Clear beats entertaining at every task-critical surface.** Even brand-forward products subordinate cleverness to comprehension in errors, forms, confirmations, and instructions. (MailChimp, a famously voice-driven product, states the rule outright: "it's always more important to be clear than entertaining.")
- **One idea per sentence; the action stated directly.** Front-load the point. Users scan in an F-pattern and bail on dense blocks; bury the answer and they never reach it.
- **Cut the throat-clearing.** "In order to be able to" → "to." "At this point in time" → "now." Plain language is not dumbed-down language — it's the removal of everything between the user and the meaning.
- **Cleverness has a place — at the edges.** Personality belongs where comprehension isn't at stake (an empty state's encouragement, a 404, a celebratory toast). It does not belong in the words a user must parse correctly to avoid a mistake. (Tone-by-situation is the subject of `voice-and-tone.md`.)

## Content-first / wireframe with real words

A core content-design practice — and a direct rebuke of "lorem ipsum" design — is to **design with real content from the start, not placeholder text dropped into a finished visual.** Content-first design means the words come before or alongside the layout, because the content reveals what the layout must accommodate.

- **No lorem ipsum.** Placeholder text hides the hard problems: the heading that's actually three lines long, the error that needs two sentences, the label that doesn't fit the button. Real words surface these while they're cheap to fix.
- **Words before chrome.** Often the fastest way to design a screen is to write its content as plain text first — the real heading, the real body, the real CTA — and let that draft drive the visual hierarchy, rather than reverse-engineering content to fit a pretty frame.
- **The content reveals the structure.** Writing the real answer to a user need frequently shows the screen needs a table, a step list, or a split into two pages — a discovery placeholder text can never produce.
- **Prototype the content, test the content.** Treat copy as a testable artifact: put real words in front of users and watch for misreadings, hesitation, and wrong turns, then revise. Content is iterated, not written once.

## Tells of good vs. bad

| Dimension | Good content design | Bad (copy-as-decoration) |
| --- | --- | --- |
| **Starting point** | A user need / job, in the user's words | "What we want to say" / a topic bucket |
| **Mode awareness** | Task surfaces written for completion | Copywriter cleverness applied to a form/error |
| **Language** | Plain, one idea per sentence, action stated | Jargon, throat-clearing, system-oriented terms |
| **Form** | Form chosen to fit the need (table, video, sentence) | Prose by default, regardless of need |
| **Process** | Real words drive the design; content tested | Lorem ipsum filled in at the end |
| **Deletion** | Content with no need is cut | Everything kept "for completeness" |
| **Voice vs. clarity** | Clarity wins where the task is at stake | Personality preserved at the cost of comprehension |

The single test: **for each piece of content on the screen, name the user need it serves and the job it enables.** If you can't name the need, the content shouldn't be there; if the content is clever but the user can't tell what to do, the cleverness has cost the only thing that matters.

## Boundary: this is UX writing, not brand voice

Content design as covered here is **product-side**: clarity, task completion, and the words in the interface. The _personality_ those words express — the brand's distinctive voice, its cultural positioning, its identity — is a brand-strategy question, not a UX-writing one, and lives in **brand-forge**, not here. The two meet at the surface (a product's UX writing should sound like the brand), but they answer different questions: brand voice asks "who are we and how do we sound," product content design asks "can the user understand this and finish the task." When a request is about establishing or evaluating brand voice/identity, route to brand-forge; this file and its siblings cover the interface-level writing that gets a user through the job. The sibling `voice-and-tone.md` covers exactly where this seam sits — defining a _product_ voice for the interface without straying into brand identity.
