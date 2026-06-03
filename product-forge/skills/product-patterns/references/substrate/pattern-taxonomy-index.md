---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Nielsen Norman Group (nngroup.com). UX pattern guidance across navigation, forms, error handling, empty states, notifications, search, modals, and onboarding (the practitioner standard). https://www.nngroup.com/"
  - "Jon Yablonski. *Laws of UX* (lawsofux.com) and *Laws of UX*, O'Reilly 2020 / 2nd ed. 2024 — the cognitive heuristics cross-referenced below. https://lawsofux.com/"
  - "Interaction Design Foundation. \"What are User Interface (UI) Design Patterns?\" https://www.interaction-design.org/literature/topics/ui-design-patterns"
  - "Jenifer Tidwell, Charles Brewer & Aynne Valencia. *Designing Interfaces: Patterns for Effective Interaction Design*. 3rd ed., O'Reilly, 2020 — the canonical interface-pattern catalogue this taxonomy is consistent with."
---

# Pattern Taxonomy: the master index

This is the table of contents for the product-pattern library — the categorized index behind the library's "and many more." Patterns are organized into **eight categories**: **flows** (multi-step journeys), **interaction** (single-surface behaviours), **content** (how information is presented and written), **feedback** (how the system tells the user what happened), **monetization** (commerce and conversion, including the deceptive line), **substrate** (the cross-cutting floor every pattern sits on), **ai-ux** (patterns specific to generative / agentic interfaces), and **trust-safety** (privacy, consent, and the safety floor every data-touching surface sits on). Each entry is a one-line scope plus, where one applies, the cognitive law it leans on (→ see the laws-of-ux reference) or the NN/g guidance it tracks. Patterns with their own deep-dive references in this library are noted; the rest are scoped here and expanded on demand. This index is the authoritative roster — when a critique asks "what patterns apply to this surface?", start here.

> How to read an entry: **Pattern** — one-line scope. _(law / source it leans on)_. A pattern that appears in two categories is cross-listed; the deceptive twin of a legitimate pattern is named in **monetization**.

## flows — multi-step journeys

Patterns that span more than one screen or state, where the unit of design is the _sequence_, not the surface.

- **Onboarding / first-run** — get a new user from zero to first value (the "aha" moment) with the least friction. _(Zeigarnik + Goal-Gradient: show progress to completion.)_
- **Setup wizard / stepper** — decompose a complex task into ordered, digestible steps with a visible progress indicator. _(Hick's Law: fewer choices per step; Miller's Law: carry context forward.)_
- **Sign-up / registration** — create an account with minimal required fields; defer what isn't needed to start. (Beware the deceptive twin _forced action_ in monetization.)
- **Sign-in / authentication** — log a returning user in; support password managers, passkeys, and SSO. _(WCAG 3.3.8 Accessible Authentication — no cognitive-function-test gates; → accessibility.)_
- **Checkout** — convert intent to purchase; show all costs before commitment, support guest checkout. (Deceptive twins: _hidden costs_, _sneaking_; → dark-patterns.)
- **Cancellation / offboarding** — let a user leave or downgrade as easily as they joined (symmetry). (Deceptive twin: _hard to cancel_ / roach motel; → dark-patterns.)
- **Empty-to-populated journey** — guide a user from an empty account to populated, valuable state over the first sessions.
- **Progressive disclosure** — reveal complexity only as the user needs it, across or within steps. _(Hick's Law; Tesler's Law: irreducible complexity must live somewhere.)_
- **Multi-step forms / branching** — long or conditional data entry split into sections with save-and-resume.
- **Search-to-result flow** — query → suggestions → results → refinement → detail. _(cross-listed in interaction.)_

## interaction — single-surface behaviours

Patterns local to one screen or component — how a control behaves under input.

- **Navigation: global / primary** — top bar, sidebar, bottom tab bar; the persistent way to move between sections. _(Jakob's Law: conform to platform expectations; → responsive-mobile for thumb-zone placement.)_
- **Navigation: local / secondary** — breadcrumbs, tabs, in-page anchors, sub-nav for going _within_ a section.
- **Navigation: drawer / hamburger menu** — collapse breadth behind a toggle (a known engagement trade-off on the desktop). _(NN/g: hidden nav lowers discoverability.)_
- **Forms & inputs** — text fields, selects, toggles, steppers, date/file pickers; the data-entry primitives. _(Fitts's Law: target size; → ui-compose-forms peers and accessibility for labels.)_
- **Input masking / formatting / chunking** — group long values (cards, phone numbers) as the user types. _(Miller's Law.)_
- **Search & filter** — typeahead/autocomplete, faceted filters, scoped search, sort. _(Doherty Threshold: instant suggestions.)_
- **Selection & bulk actions** — select one/many, then act; with a clear count and reversible result.
- **Drag-and-drop / reorder** — direct manipulation to move or rank items. _(WCAG 2.5.7: must have a non-drag alternative; → accessibility.)_
- **Modal / dialog** — interrupt for a focused sub-task or decision; trap focus, offer escape. _(WCAG 2.1.2 no keyboard trap.)_
- **Popover / tooltip / menu** — transient surfaces anchored to a trigger; dismiss on outside-tap.
- **Bottom sheet** — mobile surface that rises into the thumb zone instead of a centre modal. _(→ responsive-mobile.)_
- **Accordion / disclosure / expander** — show/hide a region to manage density. _(Hick's Law.)_
- **Inline edit** — edit a value in place without a separate form. _(Doherty: optimistic update.)_

## content — presenting information

Patterns governing how information is structured, shown, and made scannable.

- **Data table / grid** — dense tabular data with sort, filter, pagination, frozen headers.
- **List / feed / card layout** — repeating items; cards for scannable heterogeneous content, lists for homogeneous.
- **Dashboard** — at-a-glance status across multiple metrics. _(→ ref-dashboard; Von Restorff: make the key metric distinct.)_
- **Detail / record view** — the canonical view of a single entity with its fields and related actions.
- **Hierarchy & layout** — visual emphasis, grouping, and reading order. _(Gestalt laws: proximity, similarity, common region — see lawsofux.com; Von Restorff: one focal point.)_
- **Information density / progressive disclosure of detail** — show summary first, detail on demand.
- **Pagination vs. infinite scroll vs. load-more** — three ways to chunk long result sets, each with a known trade-off. _(NN/g: infinite scroll harms findability and footers.)_
- **Typography & readability** — type scale, measure, contrast for legible text. _(→ ref-typography; WCAG 1.4.3 contrast.)_
- **Truncation & "show more"** — clip long content gracefully with an affordance to expand.
- **Localization / i18n presentation** — content that adapts to language, length, and direction (RTL). _(→ ui-verify-i18n.)_

## feedback — telling the user what happened

Patterns that close the loop after an action, communicate state, or report an outcome.

- **Loading: spinner / skeleton / progress** — signal work in progress; skeletons for layout-known waits, determinate progress when measurable. _(Doherty Threshold: respond <400ms or simulate it; → laws-of-ux.)_
- **Optimistic UI** — reflect the action immediately, reconcile with the server in the background. _(Doherty Threshold.)_
- **Toast / snackbar** — transient, non-blocking confirmation of a completed action; auto-dismiss.
- **Inline validation & error messages** — identify the error at the field, in text, with a suggested fix. _(WCAG 3.3.1 / 3.3.3; → accessibility.)_
- **Empty states** — what a zero-data screen shows: explain, illustrate, and offer the first action. _(NN/g: empty states are an onboarding opportunity, not a dead end.)_
- **Confirmation & undo** — confirm destructive or irreversible actions; prefer _undo_ over a confirm dialog where feasible. _(NN/g: undo respects user control better than nagging confirms.)_
- **Notifications & badges** — surface events without derailing the task; respect a notification budget. (Deceptive twin: _nagging_; → dark-patterns.)
- **System status / banners** — persistent indication of degraded, offline, or maintenance state. _(Nielsen heuristic #1: visibility of system status.)_
- **Success / completion states** — reward task completion; the satisfying close of a Zeigarnik loop. _(Peak-End Rule: the end shapes the memory.)_
- **Error & fallback pages** — 404 / 500 / offline screens that orient and offer a way back.

## monetization — commerce, conversion, and the line

Patterns for revenue and conversion — _and_ the deceptive catalogue that marks where conversion tactics become illegitimate. This category carries two reference deep-dives.

- **Pricing page / plan comparison** — present tiers and help the user choose. (Von Restorff: highlight the recommended tier; deceptive twin: _comparison prevention_.)
- **Paywall / upgrade prompt** — gate premium value and present the upgrade at the moment of need.
- **Free trial / freemium conversion** — convert free users with honest value, not coercion.
- **Subscription management** — start, change, pause, and (symmetrically) cancel a recurring plan. (Deceptive twins: _hidden subscription_, _hard to cancel_; → dark-patterns.)
- **Cart & add-to-cart** — accumulate intended purchases transparently. (Deceptive twin: _sneak into basket_ / sneaking.)
- **Checkout & payment** — see flows; all costs disclosed before commitment. (Deceptive twin: _hidden costs_.)
- **Persuasion (legitimate)** — true social proof, honest scarcity/urgency, accurate anchoring. _(The bright line vs. deception; → dark-patterns.)_
- **Deceptive (dark) patterns — what NOT to do** — forced action, confirmshaming, roach motel, sneak-into-basket, nagging, obstruction, fake scarcity/urgency/social-proof, preselection, trick wording, visual interference, disguised ads. **(→ dark-patterns.md — the ethical and legal line: FTC, EU DSA Art. 25, NN/g.)**

## substrate — the cross-cutting floor

Not patterns _per se_ but the constraints every pattern above must satisfy. This category carries the foundational deep-dives.

- **Accessibility (WCAG 2.2 / POUR / AA)** — the inclusion floor: perceivable, operable, understandable, robust; contrast, keyboard, focus, target size. **(→ accessibility.md.)**
- **Responsive & mobile** — mobile-first layout, touch targets, thumb zone, platform conventions. **(→ responsive-mobile.md.)**
- **Laws of UX** — the cognitive heuristics every pattern leans on: Hick's, Fitts's, Jakob's, Doherty, Miller's, aesthetic-usability, Von Restorff, Zeigarnik. **(→ laws-of-ux.md.)**
- **Performance & perceived performance** — speed as a usability property. _(Doherty Threshold; → ui-verify-perf.)_
- **Motion & animation** — purposeful transitions that orient, not decorate; respect reduced-motion. _(→ ui-compose-motion; WCAG 2.3.3.)_
- **Theming / dark mode / tokens** — consistent visual language across modes. _(→ ui-build-theme, ui-build-tokens.)_
- **Voice & tone in UI copy** — microcopy that is clear, honest, and consistent. _(→ ui-compose-voice; ties to confirmshaming in dark-patterns — copy is where shaming lives.)_
- **Internationalization & safety** — i18n readiness and content-safety checks. _(→ ui-verify-i18n, ui-verify-safety.)_

## ai-ux — generative and agentic interfaces

Patterns specific to LLM- and agent-backed products, where output is probabilistic, streamed, and fallible. (Emerging tier — these conventions are younger and less settled than the rest; treat as practitioner-consensus, not canon. Labeled emerging.)

- **Prompt input** — the box (or structured controls) where intent is expressed; with affordances to refine before sending.
- **Streaming response** — render tokens as they arrive with a live cursor; never block on the full response. _(Doherty Threshold: perceived responsiveness during long generation.)_
- **Generative loading / thinking state** — multi-step "thinking" messages and skeletons that keep the user oriented during latency. _(cross-listed with feedback.)_
- **Citations & source attribution** — clickable links to the sources behind a factual claim; the transparency floor for retrieval. _(Trust pattern; ethical baseline.)_
- **Confidence & uncertainty signalling** — communicate when the model is unsure rather than asserting uniformly. _(Honesty; avoids the over-trust failure mode.)_
- **Human-in-the-loop confirmation** — require approval before an agent takes a consequential or irreversible action. _(cross-listed with feedback; ties to confirmation & undo.)_
- **Editable / regenerate output** — let users correct, refine, or regenerate a response rather than accept-or-discard. _(Tesler's Law: complexity the user must be allowed to steer.)_
- **Agent steps / transparency trace** — show what an agent did (tools called, steps taken) so the user can oversee it. _(Observability as a UX property.)_
- **Suggestion chips / guided prompts** — offer starting prompts to overcome the blank-canvas problem. _(Hick's Law: bounded starting choices; Paradox of the Active User.)_
- **Error & hallucination recovery** — graceful handling when the model is wrong, with an easy correction path. _(cross-listed with feedback: error & fallback.)_

## trust-safety — privacy, consent, and the safety floor

Patterns that govern how a product earns and keeps trust around personal data and risk — the floor beneath every data-touching surface. This category carries deep-dive references.

- **Privacy by design** — privacy as the architectural default, not a bolted-on remediation; data minimization. _(Ann C.'s 7 principles; GDPR Art. 5(1)(c); → privacy-by-design.md.)_
- **Consent & permissions** — genuine, freely-given, withdrawable consent; just-in-time permission priming; refuse without losing core function. (Deceptive twin: forced/bundled consent; → consent-and-permissions.md and dark-patterns.)
- **Explainability & transparency** — "why am I seeing this," a true explanation over a plausible rationalization, a route to contest. _(NIST XAI principles; → explainability-and-transparency.md.)_
- **Auditability & control** — access / export / correct / delete; history and audit trails; reversibility over confirmation. _(GDPR data-subject rights; → auditability-and-control.md.)_
- **Risk & harm handling** — misuse / abuse cases, safety-by-default, friction-as-safety matched to harm × reversibility, worst-case-user thinking. _(OWASP abuse cases; → risk-and-harm-handling.md.)_

## Note on scope and forks

This index is intentionally broad and shallow — one line per pattern. Several categories above point at deep-dive references that _do_ exist in this library (e.g. dark-patterns, accessibility, responsive-mobile, laws-of-ux, the trust-safety cluster, and this index); the remaining patterns are scoped here and expanded on demand, and many overlap with the wider `ui-*` skill family cross-referenced inline. Two cautions: pattern _names_ are not standardized across the field (NN/g, Tidwell's _Designing Interfaces_, Material, and component libraries each name overlapping patterns differently — confirm which vocabulary a teammate means before reconciling), and the **ai-ux** category is genuinely emergent and will move. Treat the seven-category spine as stable and the individual entries as a living roster.
