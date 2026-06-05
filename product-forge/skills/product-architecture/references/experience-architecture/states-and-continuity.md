---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Scott Hurff, *Designing Products People Love* (O'Reilly, 2016) — the UI Stack: the five states (blank, loading, partial, error, ideal)."
  - "Scott Hurff — “The Best Way to Improve Your App's User Experience” / the UI Stack (scotthurff.com/posts/why-your-user-interface-is-awkward-youre-ignoring-the-ui-stack)."
  - "37signals (Jason Fried, David Heinemeier Hansson, Matthew Linderman), *Getting Real* (2006) — the original three-state solution (blank / regular / error) the UI Stack extends."
  - "NN/g — Skeleton Screens & response-time / progress-indicator guidance; Empty States guidance."
---

# States & Continuity

This is the working method for two disciplines that separate a robust product from a demo: **designing every state a surface can be in**, and **designing continuity across sessions** so a user can pick up where they left off. Both attack the same illusion — that a product is the "ideal" screen where data exists, everything loaded, and nothing went wrong. That screen is the minority case. The architectural work is the rest: the empty product on day one, the spinner, the half-loaded list, the error, the success, the offline gap — and the larger arc of a user who closes the laptop mid-task and returns tomorrow. The tell of an unfinished product is that only the ideal state was designed; the tell of a finished one is that every state, including the unglamorous ones, was designed on purpose.

## The state model (Hurff's UI Stack)

The canonical enumeration is **Scott Hurff's "UI Stack"** from _Designing Products People Love_ (O'Reilly, 2016): every screen exists in one of **five states**, and a designer who renders only one of them has shipped a fifth of the work. The UI Stack extends 37signals' earlier **three-state solution** (blank / regular / error, from _Getting Real_, 2006), which mobile/touch products outgrew once loading and partial data became first-class concerns.

| State | When the screen is in it | What it must do |
| --- | --- | --- |
| **Ideal (regular)** | Content exists and is fully loaded — the "happy" screen | Present the content well; this is the only state most teams design |
| **Empty (blank)** | No content yet — a new account, a cleared list, no results | **Onboard, not apologize.** Explain what goes here, why it's valuable, and give the one action to fill it |
| **Loading** | Content is being fetched | Set expectations; reduce perceived wait (skeleton screens, progress for long waits) |
| **Partial** | Some content exists but it's sparse — one item where there'll be many | Bridge empty→ideal; show the real content _and_ encourage adding more |
| **Error** | A request failed, input was rejected, the network dropped | Say what went wrong, why it matters, and what to do next; never expose raw errors; preserve the user's input |

To these five, modern products add **offline** (or "no connection") as a first-class state of its own — increasingly necessary for mobile and PWA contexts, and distinct from a transient error because it persists and may degrade rather than fail. So the practical working set is **empty / loading / partial / error / ideal / offline.** And a frequently-missed seventh: **success** as a deliberate terminal state (the confirmation, the "done") — easy to skip because it feels like the absence of a problem, but its absence leaves the user unsure the action took.

```text
   ┌──────────┐  fetch   ┌──────────┐  some    ┌──────────┐  all    ┌──────────┐
   │  EMPTY   │ ───────▶ │ LOADING  │ ───────▶ │ PARTIAL  │ ──────▶ │  IDEAL   │
   │ (onboard)│          │(skeleton)│          │(+ add CTA)│         │ (content)│
   └──────────┘          └────┬─────┘          └──────────┘         └────┬─────┘
                              │ fails                                     │ acts
                              ▼                                           ▼
                         ┌──────────┐         ┌──────────┐          ┌──────────┐
                         │  ERROR   │         │ OFFLINE  │          │ SUCCESS  │
                         │(recover) │         │(degrade) │          │ (confirm)│
                         └──────────┘         └──────────┘          └──────────┘
```

## Designing for every state (procedure)

For every screen that shows data or accepts input, walk the full set — don't let any state default to a blank page or a raw stack trace:

1. **Empty:** Is this a first-use empty (never had data) or a user-emptied empty (deleted everything) or a no-results empty (search/filter returned nothing)? Each wants a different message and a different action. The first-use empty is the single highest-leverage onboarding surface in the whole product — it's where a new user decides whether to invest. Make it instructive and inviting, not a sad illustration with "Nothing here yet."
2. **Loading:** Match the indicator to the wait. NN/g's response-time thresholds: under ~0.1s feels instant (no indicator); up to ~1s the user notices but stays in flow (subtle or none); beyond ~1s show a clear indicator; for longer or known-duration waits use a progress bar or **skeleton screens** (placeholders that show the coming layout and reduce _perceived_ wait by signaling what's loading where).
3. **Partial:** Don't treat one-of-many as if it were the ideal state. Show the real item and keep the "add more" affordance visible so the screen pulls the user toward fullness.
4. **Error:** Apply the flow discipline from `flows-and-task-design.md` — message says what happened and what to do, input is preserved, there is always a recovery action, and the error never blames the user or leaks internals.
5. **Offline:** Decide degrade-vs-block. Can cached content still be read? Can actions queue and sync on reconnect? Or must the feature block? Communicate the offline condition clearly and recover automatically on reconnection.
6. **Success:** Confirm terminal actions explicitly (a created record, a sent message, a completed payment) so the user knows it took — and point to the obvious next step.

A useful audit trick: for each screen, screenshot or sketch all six/seven states side by side. The gaps in the row are the states that will ship undesigned.

## Cross-session continuity & resumability

Beyond the momentary states is the longer arc: a user does not experience a product in one unbroken session. They get interrupted, switch devices, close the tab, come back tomorrow. **Continuity** is the architectural property that the product remembers, so the user doesn't have to start over. Its absence — losing a half-filled form, a lost draft, a re-login that dumps you on the home page instead of where you were — is one of the most quietly corrosive experience defects, because it punishes exactly the engaged users who do the most.

The continuity moves, roughly in order of leverage:

- **Persist in-progress work automatically.** Drafts, partially-filled forms, multi-step flows — save as the user goes, not only on explicit submit. A user who abandons step 3 of 5 and returns should land back at step 3 with steps 1–2 intact (this is where state design meets flow design — abandonment is a designed case, not a data-loss event).
- **Restore position, not just data.** "Pick up where you left off" means returning the user to the _place_ they were — the document, the scroll position, the open record — not just preserving the data somewhere they have to re-navigate to find. Recently-viewed, "continue where you left off," and reopening the last context all serve this.
- **Continuity across surfaces/devices.** The job started on the phone continues on the desktop. This is the cross-surface continuity that `surfaces-and-screens.md` requires — shared state so a hand-off between surfaces resumes rather than restarts.
- **Graceful session expiry.** When a session must end (auth timeout), preserve context so re-authentication returns the user to where they were, with their unsaved work intact — never silently discard it.
- **Be explicit about what's saved.** Tell the user it's saved (an autosave indicator), so they can close with confidence rather than compulsively re-submitting.

The architectural test for continuity: **can a user be interrupted at any point and resume without re-doing work or re-finding their place?** If interruption costs them progress, the product is hostile to real-world use, where interruption is the norm.

## What to check (good vs. bad)

| Dimension | Bad | Good |
| --- | --- | --- |
| **State coverage** | Only the ideal state designed; others default to blank/crash | All of empty/loading/partial/error/(offline)/success designed |
| **Empty state** | "Nothing here yet" + a sad icon | Instructive first-use onboarding with a clear fill-it action |
| **Empty variants** | One empty state for first-use, user-emptied, and no-results alike | Each empty variant has its own message and action |
| **Loading** | Spinner for everything, or nothing for a long wait | Indicator matched to wait length; skeletons for layout-heavy loads |
| **Error** | Raw error dumped; input lost; no recovery | Plain message + cause + next step; input preserved; recovery action |
| **Offline** | Feature silently breaks with a generic error | Offline handled explicitly; degrade or queue; auto-recover on reconnect |
| **Success** | No confirmation; user unsure it took | Explicit terminal confirmation + next step |
| **In-progress work** | Abandon = lose the draft / restart the flow | Autosave; return to the exact step with prior input intact |
| **Position restore** | Returns user to home, makes them re-find their place | Returns user to the exact document/record/scroll position |
| **Cross-device** | Start on phone, restart on desktop | Shared state resumes the job across surfaces |
| **Session expiry** | Timeout discards unsaved work silently | Re-auth returns to context with work preserved |

The fastest single test for states: open any data screen and force each condition (clear the data, throttle the network, kill the connection, fail the request). Any condition that produces a blank page or a raw error is an undesigned state. The fastest test for continuity: start something, kill the tab mid-way, reopen — measure how much was lost. Anything lost is the continuity gap.

## One labeled caveat

The five-state UI Stack (blank/loading/partial/error/ideal) is accurately attributed to Scott Hurff (_Designing Products People Love_, O'Reilly 2016) and his widely-circulated UI Stack post, and its lineage from 37signals' three-state solution in _Getting Real_ (2006) is well documented. "Offline" and "success" are added here as practical extensions, not part of Hurff's original five — they are labeled as such. NN/g's response-time thresholds (0.1s / 1s / 10s, originating with Miller 1968 and Card/Robertson/Mackinlay, popularized by Jakob N.) and skeleton-screen guidance are standard and accurately characterized; confirm exact figures against NN/g's current articles if precise numbers are quoted. Continuity/resumability is presented as synthesized working method rather than a single named framework.
