---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Nielsen Norman Group — Error-Message Guidelines (nngroup.com/articles/error-message-guidelines)"
  - "Nielsen Norman Group — 10 Usability Heuristics for User Interface Design — #5 Error Prevention, #9 Help Users Recognize, Diagnose, and Recover from Errors (nngroup.com/articles/ten-usability-heuristics)"
  - "Nielsen Norman Group — 10 Design Guidelines for Reporting Errors in Forms (nngroup.com/articles/errors-forms-design-guidelines)"
  - "W3C Web Accessibility Initiative — Accessibility Principles (POUR) (w3.org/WAI/fundamentals/accessibility-principles)"
  - "W3C WAI — ARIA19: Using role=alert or Live Regions to Identify Errors (w3.org/WAI/WCAG21/Techniques/aria/ARIA19)"
---

# Error Handling

An error is the moment a user's intent and the system's reality diverge — a wrong input, a failed action, a broken state. It is also the moment trust is most fragile, so error handling is a load-bearing UX surface, not an afterthought bolted on at the end. The discipline has two halves that operate in sequence: **prevent the error from happening** (NN/g heuristic #5) and, when it happens anyway, **help the user recognize, diagnose, and recover** (NN/g heuristic #9). The most important strategic point is the ordering — _prevention beats recovery_ — because the best error message is the error the user never hit. This reference covers both halves and ties the recovery path to the WCAG POUR principles so the handling is usable by everyone, not just sighted mouse users.

---

## Prevent first (heuristic #5)

NN/g's heuristic #5 — **Error Prevention** — outranks message-writing: "even better than good error messages is a careful design which prevents a problem from occurring in the first place." Design the error out before you design the message:

- **Constrain the input.** Use the right control so an invalid value is hard to produce — pickers for dates, steppers/selects for bounded values, input masks for formatted fields, disabled states for unavailable actions.
- **Forgive format.** Accept the value in any reasonable shape and normalize it (phone numbers with or without dashes, dates in multiple formats, trimming whitespace) instead of rejecting on punctuation.
- **Validate at the right time.** Catch problems early enough to be helpful but not so early they nag — generally validate a field on blur / once the user has had a fair chance to complete it, not on the first keystroke (premature errors feel hostile). Re-validate on submit.
- **Confirm only the consequential.** For destructive or costly actions, prevent the slip with a confirmation _or_ an undo (prefer undo for reversible actions — see the feedback reference); don't gate routine actions, which only trains click-through.
- **Show requirements up front.** State constraints (password rules, allowed file types, max length) _before_ the user acts, not as a post-hoc rejection.

NN/g splits errors into **slips** (right intent, wrong execution — a mistype) and **mistakes** (wrong intent, from a bad mental model). Slips are fought with constraints and forgiveness; mistakes with clearer information and good defaults. Naming which you're facing tells you which prevention to reach for.

---

## When it happens anyway: the error message (heuristic #9)

Heuristic #9 — **Help Users Recognize, Diagnose, and Recover from Errors** — sets the bar: error messages should "be expressed in plain language (no error codes), precisely indicate the problem, and constructively suggest a solution." NN/g's Error-Message Guidelines expand this into a checklist. A complete error message does four jobs:

1. **Say what went wrong, precisely** — not "An error occurred." Describe the exact problem so the user can recognize it ("concisely and precisely describe the issue").
2. **Say how to fix it** — "constructive advice" with a concrete remedy and a **low interaction cost** to act on. Recognition without a path is just blame.
3. **Use human language, no codes/jargon** — "human-readable language"; hide error codes and abbreviations except where needed for technical diagnostics.
4. **Be visible and correctly placed** — display the error "adjacent to where it occurred," with redundant cues (text + icon + color, not color alone), and styling that draws attention without screaming.

### Plain language, not codes

This is the single most-cited rule and the most-violated. "Error 0x80070057" tells the user nothing they can act on. NN/g: hide codes from the user (keep them for logs/support), and write the message in the user's vocabulary. The fix the user needs is in words: _what_ is wrong and _what to do._ If a reference ID is genuinely useful for support, show it as secondary text — not as the entire message.

### Polite, blame-free tone

The message must "avoid language that blames users or implies they are doing something wrong." "You entered an invalid email" accuses; "That doesn't look like an email address — check for a missing @" guides. NN/g's separate "Hostile Patterns in Error Messages" makes the point sharply: blame, snark, and dead-ends are hostile design. Be neutral, specific, and on the user's side.

### Preserve the user's work

Never make an error cost the user their input. NN/g: "preserve the user's input" — show the original text for editing rather than forcing a restart, and never clear a form on a validation failure. Losing a filled-out form to one bad field is among the most expensive, trust-eroding errors a product can commit.

> NN/g doesn't fix a single reading-grade target in the Error-Message Guidelines themselves (it emphasizes "legible and readable" text); their related error-message _scoring rubric_ discusses readability checks. Treat "plain, jargon-free, short" as the operative rule and verify with a readability tool rather than citing a hard grade number from this source.

---

## The recovery path, POUR-aligned

A recovery path is the full route from "something is wrong" to "the user has fixed it and moved on." For it to work for _everyone_, walk it against the four WCAG principles — **POUR: Perceivable, Operable, Understandable, Robust** (W3C/WAI):

- **Perceivable — the user can sense the error happened.** Don't signal errors with color alone (fails color-blind users) — pair red with an icon and text. Critically, an error that only repaints the screen is invisible to a screen-reader user: the error text must be **announced** (see Accessibility), and it must meet contrast minimums.
- **Operable — the user can get to and act on the fix by any input.** Move keyboard focus to the first error (or the error summary) so a keyboard user lands on the problem, not at the top of the page hunting. The remedy control (retry, edit, the offending field) must be reachable and operable by keyboard, with a visible focus indicator, and not time out before the user can act.
- **Understandable — the user knows what's wrong and what to do.** This is heuristic #9 restated as accessibility: plain language, precise problem, concrete solution. WCAG's Understandable principle (Guideline 3.3, Input Assistance) is explicit that users need "descriptive instructions and error messages with correction suggestions." Tie each message to its field, and keep wording consistent across the product.
- **Robust — the error is conveyed reliably to assistive tech.** Expose the error programmatically — associate the message with its field (`aria-describedby`), mark the field invalid (`aria-invalid="true"`), and surface the alert through a live region — so any user agent or screen reader reports it. A visually-styled error that isn't in the accessibility tree is not robust.

The POUR walk is the test for a recovery path: _Can the user perceive the error, operate the fix by keyboard, understand both, and will assistive tech reliably convey it?_ If any answer is no, the recovery is incomplete for some users.

---

## Variants

- **Inline / field-level** — validation tied to one input, shown adjacent to it. NN/g's preferred placement for form errors; pair with `aria-describedby` + `aria-invalid`.
- **Summary + inline (forms)** — an error summary at the top listing every problem (with in-page links to each field) _plus_ the inline messages. The summary gives the screen-reader and keyboard user an overview and jump targets; the inline message fixes each field. Strongest pattern for long forms.
- **Toast / banner (transient or page-level)** — for a non-blocking status or a recoverable failure ("Couldn't save — Retry"); use sparingly for errors and never as the _only_ record of something needing action (NN/g: a toast "would be a bad way to implement an error message" when attention/action is required).
- **Modal (blocking)** — reserve for severe, must-decide-now errors; over-use trains dismissal.
- **Full-page / fallback (4xx · 5xx · offline · error boundary)** — when a whole view can't render: plain cause, a **Retry**, a way back/home, and preserved context (the search, the filters) so retry is one step.
- **Optimistic-action rollback** — when an optimistically-applied action fails, reconcile visibly: revert the UI, say it failed, and offer retry (don't leave the user believing it succeeded — see the feedback reference).

---

## Anti-patterns

- **Error codes as the message.** "Error 500" / "0x0000007B" with no human explanation or action.
- **Generic non-messages.** "Something went wrong" / "Invalid input" with no specifics and no fix.
- **Blame and hostility.** "You did this wrong," snark, or a dead end with no recovery.
- **Clearing the form.** Wiping the user's input on a validation failure — the costliest, most-hated error behavior.
- **Color-only signaling.** A red border with no text/icon — invisible to color-blind users and silent to AT.
- **Silent failure / silent success-that-wasn't.** No feedback at all, or showing success when the action failed.
- **Premature, nagging validation.** Firing field errors on the first keystroke before the user could finish.
- **Toast-only for actionable errors.** A 3-second toast as the sole notice of a problem needing action — gone before it's read, absent from the AT tree.
- **Focus stranded on error.** Errors shown but focus left at the top of the page, leaving keyboard users to hunt.

---

## Accessibility

- **Announce errors with a live region.** Per W3C technique **ARIA19**, identify errors using `role="alert"` (assertive — equivalent to `aria-live="assertive"` + `aria-atomic="true"`, for the error that must interrupt) or a polite live region for less urgent ones, so the screen-reader user hears the error when it appears rather than discovering it by accident. Use `role="alert"` sparingly — "only in situations where the user's immediate attention is required."
- **Associate message with field, and mark invalidity.** Link the error text to its input via `aria-describedby` and set `aria-invalid="true"` on the field, so the message is read when focus reaches it and the field's invalid state is exposed programmatically (the Robust principle in practice).
- **Manage focus on submit-with-errors.** Move focus to the error summary (or the first invalid field) so the keyboard user lands on the problem; provide in-page links from a summary to each field.
- **Never rely on color alone.** Red + icon + text; ensure error text and indicators meet WCAG contrast minimums.
- **Keep the recovery operable and untimed.** The fix must be reachable by keyboard with a visible focus ring, and a session/timeout must not destroy the user's input before they can correct it (and warn before any time limit).

---

## Good vs bad (for scoring)

```text
BAD                                   GOOD
──────────────────────────────────    ──────────────────────────────────
"Error: 0x80070057"                   "We couldn't save your changes —
(code, no cause, no fix)               your network looks offline.
                                       [ Retry ]  (your edits are kept)"

"Invalid email."                      "That doesn't look like an email
(blames, vague)                        address — check for a missing '@'."
                                       (neutral, precise, actionable)

Submit fails → whole form clears,     Submit fails → form preserved, focus
focus jumps to top, red borders only  moves to an error summary linking to
(work lost; silent to AT)              each field; each field aria-invalid +
                                       aria-describedby; summary in a live
                                       region (perceivable, operable,
                                       understandable, robust)

3s toast "Save failed" then gone      Inline "Save failed — Retry" persists
(unreadable; not in AT tree)           until resolved; role=alert announces it
```

A scoring heuristic: first ask whether the error could have been _prevented_ (constraint, forgiving input, good default). For the messages that remain, check each does the four jobs — precise cause, concrete fix, plain language (no codes), correct visible placement — and that the work is preserved. Then walk the recovery path against POUR: perceivable (not color-only, announced), operable (focus moved, keyboard-reachable fix), understandable (plain + specific), robust (associated with the field and exposed to AT).
