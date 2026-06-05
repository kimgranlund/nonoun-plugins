---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Aurora Harley, Kim Flaherty. \"'Get Started' Stops Users.\" NN/g, 2017-08-20. https://www.nngroup.com/articles/get-started/"
  - "Kim Salazar. \"Mobile-App Onboarding: An Analysis of Components and Techniques.\" NN/g. https://www.nngroup.com/articles/mobile-app-onboarding/"
  - "Page Laubheimer. \"Onboarding Tutorials vs. Contextual Help.\" NN/g, 2023-02-12. https://www.nngroup.com/articles/onboarding-tutorials/"
  - "Jakob N. \"The Power of Defaults.\" NN/g, 2005-09-25. https://www.nngroup.com/articles/the-power-of-defaults/"
  - "Jon Yablonski. \"Goal-Gradient Effect\" and \"Zeigarnik Effect.\" Laws of UX. https://lawsofux.com/"
---

# Onboarding & Activation

Onboarding is not the tour you show a user — it is **the shortest path from sign-up to the moment the product's value becomes real to them.** Most teams confuse the two and ship a carousel of feature screenshots that delays value instead of delivering it. This reference defines first-run done well: the activation/"aha" frame, value-first onboarding, the empty-state-to-first-value transition, checklists, and a good-vs-bad rubric. The single most important reframe, drawn straight from NN/g, is that **the best onboarding is often no onboarding** — let the interface teach itself, and intervene only where value genuinely needs a nudge.

> NN/g's "paradox of the active user" (Laubheimer): users "want to start using products immediately rather than study instructions." Onboarding that sits _between_ the user and the product fights this instinct and loses.

---

## Activation, not introduction: the "aha" frame

The job of onboarding is **activation** — getting the user to perform the specific action most correlated with their staying. That action is the product's value made concrete (the practitioner term is the "aha moment" / time-to-first-value). Define it as a behavior, not a feeling: _the file shared_, _the first message sent_, _the dashboard populated with the user's own data_.

- **Find the activation action empirically**, by correlating early behaviors with retention — not by guessing what feels impressive in a demo.
- **Then design the whole first run to reach that one action as fast as possible**, cutting everything that does not move the user toward it.
- **Two related-but-distinct things** (label as a practitioner distinction, widely held but not a single canonical source): the _aha moment_ is when the user _perceives_ value; _activation_ is the measurable behavioral milestone you instrument. Onboarding should engineer both — the realization and the recorded action.

> Reframe for the reviewer: a feature tour answers "what can this product do?" Activation answers "what did _I_ just accomplish with it?" Only the second predicts retention.

---

## Value first, setup last

The dominant anti-pattern is front-loading setup — import your data, connect integrations, complete your profile, invite your team — _before_ the user has seen anything work. This inverts the right order. The principle, consistent with NN/g's "Get Started" finding that you must not "ask for too much too soon": **show value with sample/seed data first, ask for the user's real data only once they want to make the value their own.**

- **Seed the product so it works on first open.** Pre-populate with sample data, a template, or a worked example so the empty product _demonstrates the end state_ before the user has entered anything.
- **Defer heavy setup until it pays for itself.** Don't gate first value on a full CSV import, every integration, or a complete profile. Ask for each piece of setup at the moment it unlocks something the user now wants.
- **Customize content, not chrome.** NN/g (Salazar): content customization (what the product is about, for me) can create a relevant first experience; _visual_ customization in onboarding — "pick a theme color" — is friction that doesn't move activation. Spend the user's first attention on relevance, not decoration.
- **Defaults are silent onboarding.** Jakob N.'s "Power of Defaults": most users never open settings, so a well-chosen default both reduces effort and acts as a "just-in-time" instruction about the expected choice. Optimize the default path rather than asking the user to configure it.

---

## Empty state to first value

The empty state is not a blank screen to apologize for — it is **the highest-leverage onboarding surface you have**, because it is exactly where a new user stands before their first action. A good empty state previews the filled state and offers one clear next step; a blank or dead-end empty state is where early churn happens.

```text
BLANK (bad)                         GUIDED (good)
┌──────────────────────┐            ┌──────────────────────────────┐
│                      │            │  No projects yet              │
│                      │            │  Projects keep your work       │
│   (nothing here)     │            │  organized and shareable.      │
│                      │            │                                │
│                      │            │  [ + Create your first project ]│
│                      │            │  or  [ Start from a template ] │
└──────────────────────┘            │  ▸ preview of a sample project │
                                     └──────────────────────────────┘
```

A strong empty state does three things: **explains what lives here and why it matters, shows or previews the end-state value (sample row, ghosted example, template), and offers a single primary action** to create the first real item. The transition you are designing is empty → _one_ meaningful action → first value; everything else is secondary.

---

## Checklists and progress

A setup checklist is a strong activation device _when the items are genuinely value-bearing_ — each completed item should leave the user better off, not just leave you with more of their data. Two well-documented psychological levers make checklists work:

- **The goal-gradient effect** (Laws of UX): "the tendency to approach a goal increases with proximity to the goal" — so a checklist that shows the user _already partway done_ (e.g., "account created ✓" pre-checked) increases completion versus one starting at zero.
- **The Zeigarnik effect** (Laws of UX): "people remember uncompleted or interrupted tasks better than completed tasks" — an open, visible checklist creates a gentle pull back to finish.

Design rules: keep it short (a handful of items, Miller's-Law sized), order items by value-per-effort so the first win is fast, let users dismiss or defer it (never trap them in it), and make every item lead to a real outcome rather than busywork. A checklist of vanity steps ("watch this video," "read these tips") is a tour wearing a checklist's clothing.

---

## Tutorials vs contextual help

NN/g's clearest onboarding guidance (Laubheimer) is a distinction between two ways to reveal help, and a strong preference for the second:

|  | Push revelation (tutorials) | Pull revelation (contextual help) |
| --- | --- | --- |
| **When shown** | Up front, at a system-convenient moment | When a signal shows the user needs it, in context |
| **Problem** | "Hard to remember when the user needs it"; interrupts the task; "don't result in better task performance" | Arrives at the point of need, against the real UI |
| **Verdict** | Use sparingly, if at all | Default to this |

NN/g's operating rules for contextual help: **"No memorization!"** (show help alongside the step, never expect users to retain a tour), **"Make it easy to dismiss (and recall)"** the help, **use progressive disclosure**, and **"skip the obvious stuff"** — explain genuinely complex functionality, not buttons whose labels already say what they do. (The mechanics of tooltips, coachmarks, and tours are covered in the companion guidance reference; the onboarding point is simply: prefer just-in-time help over an upfront lecture.)

---

## Common mistakes & anti-patterns

- **The feature-tour carousel** — three-to-five swipe screens of screenshots shown before the product, retaining nothing and delaying value. NN/g's body of onboarding work is consistent that this rarely improves task performance.
- **Setup-before-value** — forcing import, integrations, or a full profile before the user has seen the product do anything. Seed first; ask for real data when the user wants ownership.
- **The blank empty state** — dropping a new user onto an empty screen with no preview and no clear first action.
- **Onboarding as a wall** — a mandatory, un-skippable flow between the user and the app. Always allow skip/defer; the active user will route around it anyway and resent being blocked.
- **Vanity checklists** — items that benefit the company's data collection, not the user's progress toward value.
- **Theme-picking as first-run** — spending the user's scarce first attention on visual customization instead of relevance.
- **Re-onboarding on every release** — firing the whole tour again after an update; show a single contextual tip on what changed instead.
- **No path back to value when help is dismissed** — closing a tip should return the user to a usable state, not a dead end.

---

## Accessibility notes

- **Onboarding must be skippable and not a focus trap** — a modal/coachmark sequence that can't be escaped by keyboard or assistive tech blocks the very users least served by a visual tour (WCAG 2.1.2 No Keyboard Trap).
- **Don't auto-advance carousels** — moving content that the user can't pause, stop, or hide fails WCAG 2.2.2 and is hostile to screen-reader, low-vision, and cognitive-load users.
- **Tips and overlays must be reachable in DOM/reading order and announced** — visual-only spotlight effects are invisible to screen-reader users; the tip text must be programmatically present and associated with the element it explains.
- **Don't rely on color or position alone** to convey "do this next"; pair the cue with text and a real, labeled control (WCAG 1.4.1).
- **Respect reduced-motion** — celebratory animation on activation should honor `prefers-reduced-motion`.
- **Checklists need accessible state** — completed vs incomplete must be conveyed to assistive tech, not by a green checkmark alone.

---

## Good vs bad

```text
GOOD                                          BAD
────────────────────────────────────────────────────────────────────
Reaches a defined activation action fast →    A tour of features, no action
Seed/sample data; product works at open   →    Empty product, "import to begin"
Real data asked when user wants ownership →    Full setup gated before any value
Empty state previews value + one CTA      →    Blank screen, no next step
Contextual, just-in-time help             →    Upfront un-skippable tutorial
Short, value-bearing, dismissible list    →    Long vanity checklist, no exit
Sensible defaults reduce setup            →    "Pick your theme" as step one
Skippable; intervenes only where needed   →    Mandatory wall before the app
Content customization (relevance)         →    Visual customization (decoration)
```

The through-line for the reviewer: **good onboarding deletes itself the moment the user reaches value; bad onboarding stands between the user and the value and calls the delay an experience.** Measure it by time-to-first-value and activation rate, not by tour-completion.
