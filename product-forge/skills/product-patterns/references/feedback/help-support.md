---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Nielsen Norman Group — 'Usability Heuristic #10: Help and Documentation' (Jakob N., 1994; updated). https://www.nngroup.com/articles/help-and-documentation/"
  - "Nielsen Norman Group — 'Help and Documentation (Usability Heuristic #10)' video. https://www.nngroup.com/videos/help-and-documentation/"
  - "Nielsen Norman Group — 'Onboarding Tutorials vs. Contextual Help' (research summary). https://www.nngroup.com/articles/onboarding-tutorials/"
  - "Nielsen Norman Group — 'Empty States in Application Design' (Kate Moran / Page Laubheimer). https://www.nngroup.com/articles/empty-state-interface-design/"
  - "Laws of UX — 'Tesler's Law' (the conservation of complexity) and 'Doherty Threshold' (Jon Yablonski). https://lawsofux.com/teslers-law/ , https://lawsofux.com/doherty-threshold/"
---

# In-Product Help and Support

This reference covers the patterns that help a user who is stuck — in-product help (tooltips, contextual panels, guided assistance), support entry points (where you ask for human help), the self-serve-vs-escalation gradient, and contextual documentation. The governing principle, straight from Nielsen's tenth heuristic, is that **the best help is the help you never need** — but since some help is always necessary, the job is to deliver it _at the moment of need, scoped to the task, without hijacking the workflow_. Help that is comprehensive but un-findable, or findable but un-actionable, has failed the heuristic regardless of how much was written.

> The framing to hold onto: help is not a content-completeness problem, it is a _delivery-timing_ problem. The same sentence is a great tooltip next to the field it explains and a useless modal thrown in the user's face on launch. Judge a help pattern by whether it reaches the user where and when the question actually arises.

## When to use which help pattern

NN/g splits help into **proactive** (preventive — shown before the user hits a problem, to familiarize) and **reactive** (troubleshooting — surfaced when the user goes looking). Within proactive help, the decisive distinction is **push vs. pull revelations**: push help is context-agnostic and interrupts (often ignored, because it obstructs the goal the user actually came for); pull help is context-sensitive — triggered by user behavior or proximity to a relevant control — and is the one to prefer. Match the pattern to the moment.

| Situation | Pattern to reach for | Why |
| --- | --- | --- |
| User is mid-task and a single field/control is unclear | **Inline contextual help** (helper text, an info tooltip on hover/focus) | A pull revelation right at the source; answers the question without leaving the task |
| Feature is genuinely new or just redesigned | **Contextual coachmark / tip on first encounter**, dismissible | Proactive familiarization scoped to the relevant control — not an upfront tour |
| User is exploring an empty screen | **Empty-state guidance** (what this is + the one action to fill it) | NN/g: empty states are prime "pull revelation" real estate; teach the feature while explaining the blank space |
| User has a question that spans multiple steps | **Contextual help panel / drawer** (in-context, persistent, searchable) | Keeps the help beside the work; no context switch to a separate site |
| User is actively stuck and self-serve failed | **Support entry point** (search → docs → contact) escalating to human help | Reactive help; the escape hatch when the in-product layer ran out |

The anti-pattern that bounds all of these is the **upfront product tour**. NN/g's research is blunt: tutorials interrupt, do not reliably improve task performance, and are quickly forgotten. They are a push revelation dressed up as onboarding. Prefer contextual, on-demand help triggered by the user reaching the relevant part of the UI.

## Canonical form: the self-serve → escalation gradient

A mature help system is a _staircase_, not a single door. The user should be able to resolve the problem at the lowest, cheapest, fastest rung — and step up to a more expensive rung only when the cheaper one fails. Each rung must hand off cleanly to the next, carrying context forward (a search that finds nothing should offer "contact us," pre-filled with what was searched).

```text
Rung 0  Prevent the question      Clear UI, good labels, inline helper text, sensible defaults
Rung 1  Answer in context         Tooltip / info popover / contextual help panel at the point of need
Rung 2  Self-serve knowledge      Searchable docs / help center, scannable, task-focused, with steps
Rung 3  Assisted self-serve       In-product search + AI/bot answer grounded in the docs, with citations
Rung 4  Async human support       Ticket / email form, pre-filled with context (page, account, last error)
Rung 5  Synchronous human support Live chat / call for blocking, account-specific, or high-stakes issues
```

Two design rules govern the staircase. First, **never skip rungs upward by default** — do not throw a "Contact support" modal at a user who has not been offered an inline answer first (it is expensive for both sides and trains users to escalate). Second, **never trap users at a rung** — a self-serve layer with no visible escape to a human is the support equivalent of a maze; NN/g and the FTC both treat hard-to-reach cancellation/contact as a deceptive-by-omission pattern.

## Variants

- **Inline helper text** — persistent micro-guidance under a field or control. Cheapest, most reliable. Use for anything a non-trivial fraction of users will pause on. Always visible (no hover required) when the guidance is essential.
- **Info tooltip / popover** — an "i" or "?" affordance revealing a short explanation on hover _and_ focus/click. Use for secondary detail that would clutter the layout if always shown. Must be keyboard-reachable (see a11y).
- **Coachmark / spotlight tip** — a one-time contextual callout on a specific control's first encounter. Use sparingly, make it dismissible, and never chain more than a couple. Prefer one tip on the relevant control over a multi-step tour.
- **Contextual help panel / drawer** — an in-app slide-out with searchable articles relevant to the current screen. Keeps help beside the task. Strong for complex B2B tools where context-switching to a docs site is costly.
- **Help center / knowledge base** — the reactive self-serve corpus. NN/g's requirements: scannable (headings, lists, chunking, keyword highlighting), genuinely searchable with relevant results, organized by topic or user level, surfacing top/frequently-viewed articles, and including video alongside text where it helps.
- **AI/bot assistant** — grounded retrieval over the knowledge base. Useful as Rung 3 _only_ when it cites sources and offers a clean handoff to a human; an unbounded chatbot that confidently invents answers is worse than a search box.
- **Support entry point** — the contact surface (form, email, chat launcher, phone). NN/g recommends offering **at least two** channels (e.g. live chat + email). It must be findable from the point of frustration, not buried.
- **Contextual documentation links** — deep links from a specific UI surface into the exact doc section, opening in-context (panel) rather than navigating away when possible.

## Anti-patterns

| Anti-pattern | Why it fails | The fix |
| --- | --- | --- |
| **Upfront product tour** | Push revelation; interrupts, doesn't stick, forgotten before it's needed (NN/g) | Contextual, on-demand pull help triggered at the relevant control |
| **Help icon as a dumping ground** | One "?" linking to the entire manual makes the user do the retrieval | Scope the link to the current task; deep-link the exact section |
| **Search box that returns nothing useful** | Reactive help that doesn't resolve, with no next step | Relevant results + an explicit "still stuck? contact us" escape carrying the query |
| **Hidden / hard-to-find contact** | Traps users in self-serve; the FTC treats hard-to-cancel/contact as a deceptive pattern | A visible, predictable support entry point; ≥2 channels |
| **Tooltip-only essential info** | Hover-only content is invisible on touch and to keyboard/AT users | Make essential guidance persistent inline text; reserve tooltips for secondary detail |
| **Modal help that blocks the task** | Interrupts the very workflow the user is trying to complete | Non-blocking panel/inline; let the user keep working alongside the help |
| **Nagging re-prompts** | Repeatedly re-offering a dismissed tip/tour erodes trust (a recognized deceptive pattern) | Respect dismissal; show a contextual tip at most once, then leave it discoverable |
| **Docs that describe _what_ but not _how_** | NN/g empty-state finding: telling users what to do without the steps strands them | List concrete steps; link to the action, not just the concept |

## Accessibility

- **Tooltips and popovers must be keyboard-operable and AT-exposed.** Trigger on focus as well as hover; associate the tip with its control via `aria-describedby` so screen-reader users hear it. Per WCAG 1.4.13 (Content on Hover or Focus), hover/focus content must be dismissible (without moving the pointer/focus), hoverable (the pointer can move onto it), and persistent (stays until dismissed). A tooltip that vanishes the instant the pointer drifts fails this.
- **Never make essential help hover-only.** Touch devices have no hover; keyboard and switch users cannot trigger it. Essential guidance belongs in persistent visible text.
- **Help that opens in a panel or modal must manage focus** — move focus into the help region on open, trap it appropriately for modals, and return focus to the triggering control on close. Announce dynamically-revealed help via a live region where appropriate.
- **Knowledge-base content is content** — it must meet the same WCAG bar as the product: heading structure, alt text on screenshots/diagrams, captions/transcripts on help videos, and link text that makes sense out of context (not "click here").
- **Don't rely on an icon alone.** A bare "?" or "i" glyph needs an accessible name (`aria-label`) so its purpose is announced.

## Good vs. bad (for scoring)

| Dimension | Good — help that lands | Bad — help that misses |
| --- | --- | --- |
| **Timing** | Contextual, pull, at the moment of need | Upfront tour / push modal on launch |
| **Scope** | Answers _this_ task; one link → the exact section | Generic "see the manual" dump |
| **Delivery** | Non-blocking inline/panel; user keeps working | Blocking modal that interrupts the task |
| **Findability of humans** | Support entry point visible from the frustration; ≥2 channels | Contact buried or absent — self-serve trap |
| **Escalation** | Clean staircase; each rung hands off context upward | Skips straight to "contact us," or dead-ends with no escape |
| **Actionability** | Concrete steps; links to the action | Describes the concept but not the procedure |
| **Self-serve quality** | Searchable, scannable, organized, relevant results | Search returns noise; no structure |
| **Accessibility** | Keyboard + AT reachable; WCAG 1.4.13 met; essential help persistent | Hover-only tooltips; bare icons; unmanaged focus |
| **Respect** | Honors dismissal; shows a tip once | Nags; re-prompts dismissed tours |

The single test: **drop a representative user at the exact point they'd get stuck — can they resolve it at the lowest rung, and if not, is the next rung one obvious, context-carrying step away?** If the only help is an upfront tour they've forgotten, a manual they must search blind, or a contact link they can't find, the system fails the heuristic no matter how much content exists behind it.
