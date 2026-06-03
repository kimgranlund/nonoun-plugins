---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Don N., *The Design of Everyday Things*, Revised & Expanded Edition (Basic Books, 2013) — Gulf of Execution, Gulf of Evaluation, the Seven Stages of Action, feedback."
  - "Donald A. Norman & Stephen W. Draper (eds.), *User Centered System Design* (Lawrence Erlbaum, 1986) — first formulation of the gulfs of execution and evaluation."
  - "Jakob N. — “10 Usability Heuristics for User Interface Design,” Heuristic #1 “Visibility of System Status” (nngroup.com/articles/ten-usability-heuristics). First published 1994."
  - "Aza Raskin, “Never Use a Warning When you Mean Undo,” A List Apart (2007) — habituation, confirmation fatigue (alistapart.com/article/neveruseawarning)."
---

# Feedback & Confirmation

This is the working method for the system's half of the conversation: how the product tells the user what state it's in, what just happened, and whether their action took effect. The frame is Norman's: every interaction crosses two gulfs, and feedback is what closes the second one. The companion problem is confirmation — when to interrupt the user to ask "are you sure?" and when that interruption is friction that trains the user to ignore you. Get feedback wrong and the user can't tell if the system heard them; over-confirm and you've built a button that everyone clicks reflexively.

## Norman's two gulfs (the spine)

Norman frames every interaction as bridging two gulfs across the **Seven Stages of Action** (goal → plan → specify → perform → perceive → interpret → compare). First formulated in _User Centered System Design_ (1986) and central to _The Design of Everyday Things_:

- **Gulf of Execution** — the gap between the user's intention and the actions the system allows. "How do I do this? What can I do? Is this control the one I want?" Bridged by good affordances, signifiers, mapping, and constraints — the _input_ side (see `inputs-and-controls.md`).
- **Gulf of Evaluation** — the gap between the system's state and the user's understanding of it. "Did it work? What state is it in now? Is this what I wanted?" Bridged by **feedback** — the system making its status perceivable and interpretable. This is the gulf feedback exists to close.

The operational consequence: every action the user takes is a question, and the absence of feedback leaves that question open. A wide gulf of evaluation is the root cause of the most corrosive UX failure — the user not knowing whether to wait, retry, or give up. When you design any action, finish the sentence "after the user does this, they will know it worked because **\_\_**." If you can't, the gulf is open.

## Visibility of system status (Heuristic #1)

Nielsen's first heuristic is the operational rule for the gulf of evaluation: **"The system should always keep users informed about what is going on, through appropriate feedback within a reasonable time."** Three timing bands govern what "appropriate" means (Nielsen's classic response-time limits):

- **~0.1s — feels instantaneous.** Direct-manipulation feedback (a button depresses, a dragged object follows the cursor) must land in this window or the link between action and reaction breaks. No spinner needed; the change _is_ the feedback.
- **~1s — keeps the flow of thought.** The user notices the delay but stays oriented; no special indicator needed beyond the eventual result, though a subtle busy cue helps.
- **>1s — attention wanders; show progress.** Beyond about a second the user needs an explicit indicator. Beyond ~10s, give a percent-done bar and keep them able to do something else.

Practical feedback rules: acknowledge _every_ action (a tap that produces nothing reads as a dead app); locate the feedback where the user is looking (next to the control, not in a corner they've left); make it proportional (a toast for a small success, a full state change for a big one); and prefer **determinate** progress (a real bar) over an indeterminate spinner whenever you can estimate completion, because a spinner that never resolves is indistinguishable from a hang.

## Optimistic UI: feedback before the server answers

When a network round-trip would otherwise stall feedback past the instantaneous band, **optimistic UI** closes the gulf of evaluation _immediately_ by updating the interface as if the operation already succeeded, then reconciling when the server responds. The like fills in on tap; the message appears in the thread; the row moves — before the write is confirmed.

The pattern has three load-bearing parts, and the third is the one teams skip:

1. **Snapshot** the current state before mutating.
2. **Apply** the change locally and instantly — the user perceives success now.
3. **Rollback** on failure — revert to the snapshot _and_ tell the user, because a silent revert is worse than a slow success: the user believes the action stuck and finds out later it didn't.

Use it where success is overwhelmingly likely and reversal is cheap and legible (likes, toggles, reordering, sending a chat message). **Don't** use it where failure is common, where the user will act irreversibly on the assumed-true result, or where a silent rollback would mislead (a payment, a "your order is placed"). The honest version of optimistic UI always handles the unhappy path; the dishonest version assumes the network never fails.

## When to confirm vs. when confirmation is friction

A confirmation dialog asks "are you sure?" before executing. It is the most overused safety mechanism in software, and Raskin's _A List Apart_ essay names why: **habituation.** Users who see the same prompt repeatedly stop reading it. His line — _"Software should know that after clicking 'Okay' countless times in response to the question, we'll probably click 'Okay' this time too, even if we don't mean to"_ — and the corollary that **"the more in-your-face the warning is, the faster we'll want to get away from it (by clicking 'Okay') and the more mistakes we'll make."** A confirmation that fires on a routine action trains the very reflex that defeats it.

The decision procedure:

| Situation | Do this | Not this |
| --- | --- | --- |
| Action is **reversible** (anything you can undo) | Just do it + offer **Undo** | Confirm |
| Action is **frequent** (happens many times a session) | Just do it; make recovery easy | Confirm (it'll be clicked past) |
| Action is **destructive _and_ irreversible _and_ rare** | Confirm — and make the confirm _effortful and specific_ | A reflexive Yes/No |
| Action has a **large blast radius** (bulk delete of 248 items) | State the scope + prefer recoverable bulk + Undo; confirm only if truly unrecoverable | A bare "Delete?" |

So: **confirmation is justified only when the act is genuinely irreversible, consequential, and infrequent** — the narrow intersection where habituation hasn't set in and undo isn't available. Everywhere else, the answer is reversibility, not interruption.

## Designing the confirmation that survives (when you must)

If a confirmation is warranted, design it to break the reflex rather than feed it:

- **Make the consequence concrete and specific.** Name the object and the count: "Delete _Q3 Forecast_ and its 14 attachments? This can't be undone." A generic "Are you sure?" carries no information and is clicked past fastest.
- **Make the confirming action require thought, proportional to the stakes.** For the most dangerous acts, require typing the resource's name or an explicit phrase — friction that's impossible to perform absent-mindedly. (Use this sparingly; it's heavy.)
- **Don't make the destructive action the default/primary-styled button**, and never place it where "OK muscle memory" lands. Distinguish the destructive verb by label ("Delete", not "OK") and treatment.
- **Offer the safe path out plainly** — Cancel/Esc must be obvious and must be the easy thing to do by accident.

## Accessibility

- **Status changes must reach non-visual users.** Wrap dynamic feedback (toasts, "saved", validation, progress) in an ARIA **live region** — `aria-live="polite"` for routine status, `role="alert"` (assertive) for errors — so a screen reader announces what a sighted user sees.
- **Don't signal status by color alone** (WCAG 1.4.1) — pair the green/red with an icon, text, or shape, so success/error survives low vision and color blindness.
- **Confirmation and destructive dialogs are modal dialogs** (WAI-ARIA dialog pattern): move focus into the dialog, trap it there, restore focus on close, and make Esc cancel.
- **Progress indicators** need an accessible name and, when determinate, `role="progressbar"` with `aria-valuenow`, so the wait is perceivable without sight.
- **Give enough time, or none required** (WCAG 2.2.1) — an auto-dismissing "Undo" toast must stay long enough to be read and reached, or offer a non-timed path to the same action.

## Good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Gulf of evaluation** | Action produces no perceivable change; user can't tell it worked | Every action answered; "they'll know because \_\_\_" is fillable |
| **Status timing** | Long operation with a spinner that never resolves | Determinate progress past ~1s; instantaneous feedback under 0.1s |
| **Optimistic UI** | Optimistic update with silent rollback on failure | Snapshot → apply → rollback _with_ a visible failure message |
| **Confirm vs. friction** | "Are you sure?" on a reversible, frequent action | Undo for reversible/frequent; confirm only for irreversible+rare |
| **Confirmation quality** | Generic "Are you sure? OK/Cancel", destructive = default button | Names the object+consequence; destructive verb distinguished; effort scaled to stakes |
| **Habituation** | A prompt fired so often users click through it blind | Friction reserved for where it isn't yet reflexive |
| **A11y** | Color-only status; toast invisible to screen readers; untrapped dialog | Live regions, non-color status, ARIA dialog with focus management, sufficient time |
