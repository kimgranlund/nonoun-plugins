---
date: 2026-06-03
coverage: deep
primary_sources:
  - "Aurora Harley. \"Instructional Overlays and Coach Marks for Mobile Apps.\" Nielsen Norman Group, 2014-02-16. https://www.nngroup.com/articles/mobile-instructional-overlay/"
  - "Page Laubheimer. \"Onboarding Tutorials vs. Contextual Help.\" Nielsen Norman Group, 2023-02-12. https://www.nngroup.com/articles/onboarding-tutorials/"
  - "Nielsen Norman Group. \"Tooltips in the User Interface\" (video) and \"Help and Documentation (Usability Heuristic #10).\" https://www.nngroup.com/articles/help-and-documentation/"
  - "Jon Yablonski. \"Tesler's Law\" (conservation of complexity). Laws of UX. https://lawsofux.com/"
---

# Guidance: Tooltips, Coachmarks, Tours & Contextual Help

Guidance is the layer that explains the interface _from inside the interface_: tooltips, coachmarks, product tours, interactive walkthroughs, and contextual help. It is also the layer teams most often abuse, because adding a tooltip feels like fixing a problem when it is frequently a way of _postponing_ one. The core discipline: **guidance is a patch over an interface that did not fully explain itself, and the best guidance is the kind you didn't need to add.** This reference defines each form, when each is appropriate, when tours backfire, and a good-vs-bad rubric.

> NN/g's foundational finding (Laubheimer) governs this whole layer: guidance shown out of context — the classic tour — is "hard to remember when the user needs it" and tutorials "don't result in better task performance." Prefer help that arrives _at the point of need_.

---

## The guidance forms

| Form | What it is | Trigger | Best for |
| --- | --- | --- | --- |
| **Tooltip** | A small popup explaining one element on hover/focus/tap | User-initiated (points at / focuses the element) | Clarifying a single control, icon, or term — on demand |
| **Coachmark** | An overlay annotation pointing at a UI element, usually on first run | System (shown at launch) | One genuinely non-obvious gesture or affordance |
| **Product tour** | A sequence of coachmarks/dialogs stepping through features | System (shown up front) | Rarely the right tool; see "when tours backfire" |
| **Interactive walkthrough** | Guidance that has the user _do_ each step in the real UI | System, but action-gated | Teaching a complex multi-step task by doing it |
| **Contextual help / hint** | A tip surfaced in place when a signal shows the user needs it | Behavioral / on-demand | The default for most help — "pull," not "push" |

The hierarchy to internalize: **on-demand and contextual forms (tooltips, contextual hints, walkthroughs) outperform pushed, upfront forms (coachmark stacks, tours)** because they respect the active user and arrive when the information is actually relevant.

---

## Tooltips

A tooltip is the lightest form: user-triggered, single-element, on demand. NN/g's standing guidance: tooltips are useful for _supplementary_ explanation but **must never carry critical or task-essential information**, because they are easy to miss and, on touch, hard to trigger discoverably.

- **Supplementary only** — if the user _must_ read it to proceed, it doesn't belong in a tooltip; put it in the UI.
- **User-triggered, brief, and non-blocking** — appear on hover/focus, dismiss on blur, never obscure the thing they describe.
- **Touch is the hard case** — hover doesn't exist on touch, so a tooltip's content must also be reachable another way (a tap target, an info affordance); never make a touch user guess that a long-press reveals essential help.
- **Don't tooltip the obvious** — NN/g's "skip the obvious stuff"; a tooltip on a button labeled "Save" is noise that trains users to ignore all of them.

---

## Coachmarks and the memory problem

Coachmarks — annotated overlays shown at first launch — are the single most over-used guidance form, and Aurora Harley's NN/g analysis is precise about why they usually fail: **they demand memorization the user cannot perform.** The user cannot read the instruction and use the app at the same time, so they must hold the hint in short-term memory — and "our short-term memory cannot retain very much information, and that information fades in about 20 seconds." Stack several coachmarks and it gets worse: Harley found that serial tips cause users to "dismiss hints more quickly, regardless of how helpful each may be," and long instruction chains make an app "appear overly complicated and daunting."

NN/g's rules for _if you must_ use a coachmark:

- **Focus on a single interaction**, not a guided tour of every region — Harley: "focus on a single interaction rather than attempting to explain every possible area."
- **Reveal hints one at a time, at the right moment** — "hints one-by-one, at the right moment, makes it a lot easier for users to understand" than a wall of annotations at launch.
- **Lead with visuals** — pair short text with an image/gesture so the user understands "without reading very much."
- **Make it look like an annotation, not the UI** — a distinct, sketch/handwritten style signals "this is a temporary note," not an interactive part of the app.
- **Reserve them for the genuinely non-obvious** — a hidden gesture (swipe-to-reveal) earns a coachmark; a visible labeled button does not.

> The reframe: a coachmark explaining a control is often evidence the control isn't self-explanatory. Fix the affordance first; the best coachmark is the one the redesign made unnecessary.

---

## When tours backfire

Product tours are where guidance most reliably goes wrong, and the failure is structural, not cosmetic. NN/g's tutorials-vs-contextual-help finding applies directly: an upfront tour is pushed "out of context, at a moment that is convenient for the system rather than the user," is "hard to remember when the user needs it," and research shows tutorials "don't result in better task performance." The recurring ways tours backfire:

- **Front-loaded, so nothing sticks** — value-less feature parade shown before the user has done anything; by the time a step is relevant, the tour is long forgotten (the memory problem at scale).
- **Interrupts the active user** — it stands between the user and the thing they came to do, and they "want to start using products immediately." The rational response is to mash "Skip" — which means the effort produced nothing.
- **Guidance fatigue** — when an app over-uses tips, coachmarks, and tours, users learn to dismiss _all_ instructional UI reflexively, so even a genuinely useful later tip gets swatted away. (This learned-dismissal effect is well documented in NN/g's body of work and broad practitioner consensus; treat specific viral "X% dismissed in Y seconds" figures circulating online as **unverified marketing claims**, not citable research.)
- **Re-fires on updates** — replaying the whole tour after a release punishes returning users for upgrading.
- **Conceals a structural problem (Tesler's Law)** — a tour bolted on to make a confusing flow usable is moving complexity onto the user instead of absorbing it in the design; the conserved complexity doesn't disappear, it just lands on the person.

**The defensible use of a tour** is narrow: a complex, professional tool where the user has _opted in_ to learn, delivered as an **interactive walkthrough** (the user performs each step in the real UI, action-gated) rather than a passive carousel — because doing-it beats being-told-it, and the user is motivated. Even then, make it skippable and recallable on demand.

---

## Contextual help: the default

The pattern NN/g actively recommends is **pull-based contextual help** — help triggered by a signal that the user needs it (repeated errors, hesitation, first arrival at a complex feature) and shown _in place, against the real UI, alongside the step_. Laubheimer's operating principles:

- **"No memorization!"** — co-locate help with the step it explains so nothing must be remembered.
- **"Make it easy to dismiss (and recall) the help content"** — let users close it _and_ get it back; never a one-shot.
- **Use progressive disclosure** — a short hint that expands to detail on request, not a paragraph dumped up front.
- **"Skip the obvious stuff"** — spend guidance budget on genuinely complex functionality.
- **Map it to the user's journey** — surface the right help at the right point, not all help at the start.

A persistent, user-initiated **help affordance** (a "?" that opens contextual docs, a searchable help surface — NN/g Heuristic #10, Help and Documentation) is the backstop: easy to find, focused on the user's task, listing concrete steps. It coexists with the principle that the _primary_ interface should need as little of it as possible.

---

## Common mistakes & anti-patterns

- **The upfront feature tour** — pushed before value, forgotten by the time it's relevant, skipped by the active user.
- **Coachmark stacks** — five annotations at launch the user must memorize and can't; dismiss-rate climbs with each.
- **Critical info in a tooltip** — task-essential content hidden behind hover/long-press, missed by many and unreachable on touch.
- **Tooltipping the obvious** — hints on self-explanatory controls, training users to ignore all guidance.
- **Guidance as a patch for bad UX** — adding a coachmark instead of fixing the unclear affordance (Tesler's-Law violation).
- **No way to recall help** — one-time tours/coachmarks with no "show me again," so a user who dismissed too fast is stuck.
- **Re-onboarding on every release** — the whole tour replays after an update.
- **Auto-advancing or undismissable overlays** — motion the user can't stop, or a coachmark with no escape.

---

## Accessibility notes

- **Tooltips must be keyboard- and screen-reader-accessible** — show on focus as well as hover, associate via `aria-describedby`, and follow WCAG 1.4.13 (Content on Hover or Focus): dismissible, hoverable, and persistent (it doesn't vanish the instant the pointer moves).
- **Hover-only is an accessibility failure** — keyboard and touch users get nothing; always provide a focus/tap path to the same content.
- **Overlays must not trap focus and must be Escape-dismissible** — a coachmark or tour step that can't be left by keyboard fails WCAG 2.1.2 (No Keyboard Trap); manage focus into and out of each step.
- **Spotlight/dimming effects are invisible to screen readers** — the guidance text must be in the DOM, in reading order, and programmatically tied to the element it points at; don't rely on a visual highlight to convey "this one."
- **No auto-advance** — tour steps that move on their own violate WCAG 2.2.2 (Pause, Stop, Hide) and defeat anyone who reads slowly or uses assistive tech.
- **Don't convey the cue by color/position alone** (WCAG 1.4.1); pair every visual pointer with text.
- **Respect `prefers-reduced-motion`** for any animated reveal, pulse, or transition between steps.

---

## Good vs bad

```text
GOOD                                          BAD
────────────────────────────────────────────────────────────────────
Contextual, just-in-time, in place        →    Upfront tour of every feature
One coachmark for one non-obvious gesture →    Five coachmarks to memorize at launch
Tooltips for supplementary info on demand →    Critical info hidden in a tooltip
Tooltip works on focus + touch, not hover →    Hover-only; nothing for keyboard/touch
Help is dismissible AND recallable        →    One-shot tour, no "show again"
Interactive walkthrough for complex tasks →    Passive carousel the user skips
Fix the affordance, then maybe annotate   →    Annotate to paper over bad UX
Skips the obvious; explains the complex   →    Tooltips on self-evident buttons
Escapable, no focus trap, no auto-advance →    Undismissable, auto-advancing overlay
```

The through-line for the reviewer: **good guidance arrives when the user needs it and disappears cleanly; bad guidance arrives when the system finds it convenient and demands the user remember it.** And the deepest tell — heavy reliance on coachmarks and tours usually signals an interface that should have been made self-explanatory instead.
