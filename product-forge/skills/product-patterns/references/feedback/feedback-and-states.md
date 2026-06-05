---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "NN/g — Visibility of System Status (Usability Heuristic #1) (nngroup.com/articles/visibility-system-status)"
  - "Jakob N. / NN/g — Response Time Limits: The 3 Important Limits (nngroup.com/articles/response-times-3-important-limits)"
  - "NN/g — Skeleton Screens 101 (nngroup.com/articles/skeleton-screens)"
  - "NN/g — Confirmation Dialogs Can Prevent User Errors (If Not Overused) (nngroup.com/articles/confirmation-dialog)"
  - "Aza Raskin / A List Apart — Never Use a Warning When You Mean Undo (alistapart.com/article/neveruseawarning)"
  - "MDN Web Docs — ARIA live regions (developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions)"
---

# Feedback & System States

Feedback is how the interface answers the user's implicit question after every action: _did that work?_ The governing principle is NN/g's Usability Heuristic #1, **Visibility of System Status** — systems "should always keep users informed about what is going on, through appropriate feedback within reasonable time." Its blunt summary: **"Don't blindfold your users."** When feedback is missing the user can't bridge the _Gulf of Evaluation_ — they can't tell what state the system is in, so they re-click, abandon, or distrust the product. This reference covers the toolkit that keeps status visible across the full lifecycle of an action: waiting (loading/skeletons), pre-emptive trust (optimistic UI), confirmation (toasts), gating risk (confirmations), and recovery (undo) — and the accessibility layer (live regions) that makes all of it work for non-visual users.

---

## The clock sets the tool: the three response-time limits

Jakob N.'s three limits decide _which_ feedback an action needs — they are perceptual thresholds, stable for decades:

| Limit | The user's experience | Feedback to use |
| --- | --- | --- |
| **0.1 s** | Feels instantaneous — "their actions are directly causing something to happen." | None needed; just respond. |
| **1 s** | A noticeable delay, but the user "stays focused on their current train of thought" and feels in control. | Keep flow; no heavy indicator required (a subtle cue at most). |
| **10 s** | The limit on holding attention; beyond it the mind wanders. | A clear progress indicator; **beyond 10 s, show a percent-done bar and an estimate of when it'll finish.** |

NN/g's mapping of indicator → wait: a **spinner / looping animation** suits **~2–10 s** (it says "working" but not how long); a **percent-done progress bar** for **>10 s** (it bounds the wait and lets the user decide whether to keep waiting). The rule: the longer and more uncertain the wait, the more _information_ the indicator owes the user.

---

## Loading & skeletons

A wait is a state, and it must be visible (heuristic #1) or the user assumes "broken/nothing happened."

- **Skeleton screens** — grey placeholder shapes mimicking the incoming layout. NN/g: best for short waits **under ~10 s**. They reduce _perceived_ wait by showing structure immediately and signaling "content is coming here," and they avoid the jarring blank-then-pop of a spinner. _(NN/g's caution: skeletons can feel slower than a clean instant load if overused; reserve them for genuinely-loading regions.)_
- **Spinners** — for short, indeterminate waits (~2–10 s) where you can't show layout or progress; they confirm activity but not duration.
- **Progress bars** — for long/determinate operations (>10 s); show percent and, per NN/g, an _estimate of completion time_.
- **Optimistic placeholders** — render known structure (the user's avatar, the heading) instantly and skeleton only the unknown parts, so the shell appears at 0.1 s and only the data waits.
- **Never show a false empty state during a load.** A panel that says "No items" while data is in flight teaches a falsehood; resolve to the empty state only once the result is known (see the empty-states reference).

---

## Optimistic UI

Optimistic UI updates the interface _immediately_ — as if the action already succeeded — then reconciles with the server result when it arrives. It trades a small correctness risk for a large perceived-speed and responsiveness win, pushing actions toward the 0.1 s "instantaneous" band.

- **When it fits:** high-probability-success, low-stakes, reversible actions — liking, marking read/done, reordering, adding a tag. The cost of a rare rollback is small and the responsiveness gain is felt on every interaction.
- **When it does not:** consequential, irreversible, or low-success-probability actions (payments, destructive ops, anything the user must _trust_ completed). Lying optimistically about a payment is a trust catastrophe — wait for the real result.
- **Reconcile failures visibly and honestly.** This is the make-or-break rule: when the optimistic action fails, **revert the UI to the prior state, tell the user it failed, and offer retry.** A silent failure that leaves the optimistic state showing makes the user believe something happened that didn't — the worst outcome, because it violates Visibility of System Status invisibly. (Ties to the error-handling reference's rollback variant.)
- **Don't optimistically render server-authored data.** Echoing the user's own input optimistically is safe; fabricating server-assigned values (IDs, computed totals, timestamps) risks showing a number that the server then contradicts.

---

## Toasts (transient confirmation)

A toast (a.k.a. snackbar) is a small, **nonmodal** popup that appears, confirms, and auto-dismisses without requiring interaction — NN/g: it "usually inform[s] users about the status of a process and disappear[s] automatically after a brief amount of time." Its job is **passive, low-stakes confirmation** ("Saved," "Copied," "Message sent").

- **Use for:** success confirmations and non-blocking, non-urgent status — the routine "it worked" that closes the feedback loop without interrupting.
- **Do not use for:** anything requiring action or that the user must not miss. NN/g is explicit that a toast "would be a bad way to implement an error message" — it vanishes before it's read and can be missed entirely. Errors and decisions need a persistent or modal surface (see error-handling).
- **The undo-toast** is the high-value pattern: confirm the action _and_ host an **Undo** button for a few seconds ("Conversation archived · Undo"). This pairs visible confirmation with cheap reversal — the single best small-action pattern.
- **Mind timing and stacking:** long enough to read (and to reach an Undo by keyboard), one at a time or a tidy queue — never a pile-up that obscures the UI.

---

## Confirmations — and why undo usually beats them

A confirmation dialog interrupts the user to make them approve a consequential action before it runs. It prevents slips — but it is a system-initiated interruption with a real cost, so NN/g bounds it tightly:

- **Reserve for serious, often irreversible consequences** — "destroying users' work or costing large amounts of money." Not for routine actions.
- **Habituation kills the generic confirm.** NN/g: "if you cry wolf too many times, people will stop paying attention." A vague "Are you sure?" trains automatic _Yes_ — "the only sensible reaction is 'of course I want to do the thing I just told you to do,' and hit Yes without further thinking." Over-used confirmations protect nothing.
- **Be specific when you do confirm.** Name the consequence — the filename, the count, the irreversibility ("Permanently delete 24 files?") — so the dialog informs rather than nags.

**Prefer undo over confirmation for anything reversible.** NN/g: "do go to great lengths to provide undo, because some user errors will remain despite even the best of confirmation dialogs." Aza Raskin's classic argument (A List Apart, _"Never Use a Warning When You Mean Undo"_) is the canonical statement: a warning interrupts _every_ user — including the majority who meant it — to catch the rare mistake; undo lets the action proceed instantly and gives the few who erred a cheap way back. The decision rule:

```text
Is the action reversible?
  ├─ Yes → perform it immediately + offer UNDO (toast/snackbar)   ← default
  └─ No  → is it consequential?
            ├─ Yes → specific CONFIRMATION dialog (+ soft-delete/undo if possible)
            └─ No  → just do it (with status feedback)
```

The strongest real-world pattern combines both for risky-but-recoverable actions: perform immediately, offer undo, _and_ (for the truly destructive) keep a soft-delete window behind a specific confirmation.

---

## System-status visibility (the through-line)

Every pattern above is one application of heuristic #1, which earns its own checklist because it's the principle the others serve:

- **Acknowledge every action.** A click that produces no visible change reads as a failed click and provokes re-clicks; confirm receipt (state change, spinner, toast) within the 1 s window.
- **Show where the user is and what mode they're in.** Selection states, active filters, current step, "saving…/saved/unsaved changes" — ambient status, not on-demand.
- **Surface the consequential truths.** NN/g's examples: "Only a Few Left!", out-of-stock on a wishlist, free-shipping thresholds — "when we understand the system's state, we feel in control"; concealing it "damages credibility."
- **Match feedback latency to the action.** Instant for instant actions; progress + estimate for long ones (the response-time limits).
- **Auto-save needs visible status too.** "All changes saved" / "Saving…" closes the loop; silent auto-save leaves the user unsure their work is safe.

---

## Variants

- **Determinate vs indeterminate progress.** Show percent when you can measure it (more reassuring, bounds the wait); fall back to a spinner only when you genuinely can't.
- **Inline vs global loading.** Load a region in place (skeleton in the panel) rather than blocking the whole screen, so the rest stays usable.
- **Optimistic vs pessimistic update.** Optimistic for reversible low-stakes actions; pessimistic (wait for confirmation) for consequential ones.
- **Toast vs inline vs banner vs modal.** Transient success → toast; persistent contextual status → inline; page-level non-blocking notice → banner; must-decide-now → modal. Right element for the stakes (NN/g, _Indicators, Validations, and Notifications_).
- **Undo vs confirm vs soft-delete.** Reversible → undo; irreversible+consequential → specific confirm; "delete now, purge later" → soft-delete window (often all three together).
- **Empty / loading / error / loaded.** The four states every data surface must design; never let one masquerade as another (cross-refs: empty-states, error-handling).

---

## Anti-patterns

- **No feedback at all.** A click with no acknowledgement — the original sin; drives re-clicks and distrust.
- **Spinner forever.** An indeterminate spinner on a long/possibly-failed operation, with no timeout, progress, or error path.
- **Optimistic lie on failure.** Showing success optimistically and never reverting when the action fails — the user believes a thing happened that didn't.
- **Toast for errors / actions.** Putting must-see or actionable information in a 3-second auto-dismissing popup.
- **Confirmation overload.** "Are you sure?" on routine actions, training reflexive _Yes_ and protecting nothing (NN/g's cry-wolf failure).
- **Destroy without undo.** A consequential, reversible-in-principle action with no undo and no recovery.
- **Skeleton everywhere.** Skeletons on instant or trivial loads, adding perceived latency where there was none.
- **Layout shift on load.** Content popping in and shoving the page (a CLS problem and a status problem) — reserve space / skeleton the region.

---

## Accessibility

- **Announce dynamic feedback via ARIA live regions.** A toast, status, or loading message that visually appears is invisible to a screen-reader user unless it's in a live region. Per MDN: use `role="status"` (implicit `aria-live="polite"`, `aria-atomic="true"`) for routine confirmations and status — it "waits until the user is idle" — and `role="alert"` (equivalent to `aria-live="assertive"` + `aria-atomic="true"`) only for the rare update needing immediate attention, used "sparingly … only in situations where the user's immediate attention is required." The live region should exist in the DOM _before_ content is injected.
- **Loading state must be perceivable non-visually.** Expose progress with `role="progressbar"` (and `aria-valuenow`/`min`/`max` when determinate), or announce "Loading…" / "Loaded, 20 results" in a polite live region — a purely visual spinner tells AT nothing.
- **Undo must be keyboard-reachable within its window.** If an Undo lives in an auto-dismissing toast, it must be focusable and operable by keyboard, and the toast must persist long enough to reach it — otherwise undo is a sighted-mouse-only affordance. (Consider keeping a durable undo in a menu, not only in the fleeting toast.)
- **Don't let feedback time out faster than people can use it.** Transient messages should not be the _only_ record of essential information; provide a persistent alternative for users who read slowly or use AT (WCAG-aligned).
- **Confirmation dialogs need focus management.** Move focus into the modal on open, trap focus within it, return focus to the trigger on close, and label it (`role="dialog"`, `aria-modal`, `aria-labelledby`) so the decision is operable and announced.
- **Respect `prefers-reduced-motion`** for spinners, skeleton shimmer, and toast transitions.

---

## Good vs bad (for scoring)

```text
BAD                                   GOOD
──────────────────────────────────    ──────────────────────────────────
Click "Save" → nothing visible        Click "Save" → button → "Saving…" →
(re-clicks; "did it work?")            "Saved" toast (role=status); status
                                       acknowledged within ~1s

Indeterminate spinner on a 30s        Percent-done bar + "~20s remaining"
export, no progress, no end           for the long export (>10s → estimate)

Like fails silently, heart stays      Like applies instantly (optimistic);
filled (optimistic lie)               on failure it reverts + "Couldn't like
                                       — Retry"

"Are you sure you want to archive?"   Archive happens instantly + "Archived ·
on every archive                      Undo" toast (Undo keyboard-reachable);
(habituated Yes; protects nothing)     confirm reserved for permanent delete
```

A scoring heuristic: for every user action, ask _does the interface answer "did that work?"_ within the right time band (0.1 / 1 / 10 s). Check loading states are visible and never masquerade as empty/error; optimistic updates reconcile failures honestly; toasts carry only passive confirmation (not errors/actions); confirmations are reserved for the consequential while reversible actions get undo; and every dynamic message reaches assistive tech through a live region with the correct politeness.
