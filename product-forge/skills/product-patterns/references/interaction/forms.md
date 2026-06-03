---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Nielsen Norman Group — 10 Design Guidelines for Reporting Errors in Forms (nngroup.com/articles/errors-forms-design-guidelines)"
  - "Baymard Institute — Usability Testing of Inline Form Validation (baymard.com/blog/inline-form-validation)"
  - "Baymard Institute — Checkout Optimization: From 16 Form Fields to 8 Fields (baymard.com/blog/checkout-optimization-from-16-fields-to-8)"
  - "Luke Wroblewski — Web Form Design: Filling in the Blanks (Rosenfeld Media, 2008); Best Practices for Form Design (static.lukew.com/webforms_lukew.pdf)"
  - "Jakob N. / Laws of UX — Jakob's Law (lawsofux.com/jakobs-law)"
---

# Form Design

Forms are where intent meets friction: every field is a small toll, and abandonment is the cumulative bill. Baymard's checkout research names form friction the **primary cause of mobile checkout abandonment — ahead of price, shipping cost, and trust.** The craft is therefore subtractive first (ask for less), then supportive (make what you do ask easy to get right, and easy to fix when it's wrong). This reference covers field reduction, inline validation, error placement and wording, and the multi-step wizard — grounded in NN/g's error guidelines, Baymard's testing, and Wroblewski's form canon.

> Two anchors. **Wroblewski:** the way to shrink a form is to interrogate every field — **"Keep, Cut, Postpone, or Explain."** **Baymard:** "checkout usability testing showed that most sites can achieve a 20–60% reduction in the number of form fields displayed by default," and high-performing checkouts complete in roughly 6–8 fields against an industry average near 11–12.

## When to use which form pattern

| Pattern | Use when | Notes |
| --- | --- | --- |
| **Single-column form** | Almost always | One field per line; a predictable top-to-bottom path. Multi-column forms cause skipped fields and ambiguous tab order |
| **Inline validation** | Whenever feasible | Validate per field on blur; correct errors in context, not after a full-page submit |
| **Multi-step wizard** | A genuinely long, sequential task (checkout, onboarding, applications) | Chunk into stages with a visible progress indicator; this is _staged_ disclosure |
| **Gradual engagement** | Sign-up that currently demands a big form before any value | Let users start with the minimum; ask for the rest once they're invested |
| **Selection-dependent inputs** | Some fields apply only given an earlier answer | Reveal dependent fields after the triggering choice — don't show all permutations at once |

## Field reduction: the highest-leverage move

Before styling a field, justify it. Wroblewski's **Keep / Cut / Postpone / Explain** is the decision frame:

- **Keep** — required to complete the task _now_; ask it.
- **Cut** — not actually needed; delete it. (Every cut field is friction removed for every user, forever.)
- **Postpone** — useful later, not now; collect it after the user has committed (post-signup, in settings).
- **Explain** — needed but suspicious-looking (phone number, date of birth); keep it _and_ say why it's asked, inline.

Supporting moves:

- **Don't ask for what you can derive or default.** City/state from a postal code; country from locale. Baymard's billing-address work shows large field reductions come from inferring and defaulting rather than asking.
- **Mark the rare exception, not the rule.** If most fields are required, mark the _optional_ ones; if most are optional, mark the required ones. Either way, mark consistently and visibly (don't rely on a tiny asterisk alone).
- **Gradual engagement (Wroblewski):** replace the upfront long form with a let-them-start flow — collect the minimum to begin, earn the right to ask for more once the user sees value.

## Inline validation: validate in context, at the right moment

Baymard found **31% of sites still lack inline validation** — and that adding it "can mostly resolve the issue of form abandonment." NN/g and Baymard converge on _when_ and _how_:

- **Validate on blur, not on every keystroke.** NN/g guideline #7: **"Don't validate fields before the input is complete"** — show the error only after the user leaves the field, so you're not scolding them mid-type. (A short 300–500ms debounce suits format-checked fields like email.)
- **Clear the error the instant it's fixed.** Baymard: error messages should be **"removed as soon as the input is corrected"** — leaving a stale red message after the user fixes the value is its own friction.
- **Use positive inline validation, sparingly.** A checkmark or "looks good" on _complex_ fields (passwords, usernames, card numbers) reassures and reduces cognitive load (Baymard); but don't decorate every trivial required field with a tick (NN/g #2).
- **Server-side validation still needs a graceful path.** When a check can only happen on the server, NN/g's rule holds: the reloaded form must show **clear, actionable, easy-to-locate** errors next to the offending fields.

## Error placement and wording

NN/g's **10 Design Guidelines for Reporting Errors in Forms** are the canonical checklist; the load-bearing ones:

1. **Aim for inline validation** wherever possible (#1).
2. **Indicate successful entry for complex fields** — but don't over-tick simple ones (#2).
3. **Keep error messages next to the field.** The message must be **"explicit, human-readable, polite, precise, and give constructive advice"** — tell the user what's wrong _and_ how to fix it (#3).
4. **Use color to differentiate error states** — red for errors, plus a semi-transparent field background on long forms so the bad field is findable; don't rely on red text alone (#4).
5. **Add an icon (and, sparingly, subtle motion)** for scanning — place an icon left of the message to help colorblind users; never animate the message text itself (#5).
6. **Use modals/confirmation dialogs sparingly** — they're disruptive and raise cognitive load (#6).
7. **Don't validate before input is complete** (#7).
8. **Don't rely on a top-of-form summary as the only signal** — a summary must accompany per-field messages, not replace them (#8).
9. **Don't report errors in tooltips** — hover/focus-gated errors get missed entirely (#9).
10. **Provide extra help for repeated errors** — many identical errors signal a design flaw; review analytics and consider a support link (#10).

```text
Email
┌─────────────────────────────────────┐
│ jane@example                         │   ← red border + tinted background
└─────────────────────────────────────┘
⚠ Enter a complete email, e.g. jane@example.com   ← icon + plain, fix-oriented text, by the field
```

Wording principle (NN/g + Nielsen's heuristics): an error message says **what happened, why, and what to do next**, in human language — never an error code, never blame ("Invalid input" tells the user nothing; `Enter a complete email, e.g. jane@example.com` tells them everything).

## Multi-step wizards

A wizard chunks a long, sequential task into ordered steps — this is **staged disclosure** (linear; every user proceeds through the steps), distinct from progressive disclosure's optional depth (see `progressive-disclosure.md`).

- **Use it for genuinely long sequential tasks** (checkout, account setup, multi-part applications), not to pad a short form across screens for no reason.
- **Show a progress indicator** — labeled steps and current position — so users know how much remains. An unknown-length wizard breeds abandonment.
- **One coherent group per step.** Group related fields (Wroblewski's form-organization principle); the chunking should match the user's mental model of the task, not arbitrary page breaks.
- **Let users go back without data loss,** review before final submit, and never silently discard entered data on a validation failure.
- **Validate per step,** so a user isn't carried to step 4 only to be bounced back to a step-1 error.

## Conventions (Jakob's Law)

Forms are where Jakob's Law bites hardest because users have filled in thousands of them: labels **above** fields (fastest top-to-bottom scan), a primary submit button **after** the last field, expected input formats, and conventional field order (name → email → password). Reordering or restyling these for novelty makes a routine task suddenly effortful. Match the patterns users already carry.

## Anti-patterns

- **Asking for fields you don't need** (or could derive/default) — the abandonment tax you control most directly.
- **Validation on every keystroke** — flagging an email as invalid while the user is still typing it.
- **Stale errors** — leaving the red message up after the value is corrected.
- **Errors far from their field** — a top-of-page summary as the _only_ signal, forcing a hunt for which field is wrong (NN/g #8).
- **Tooltip-only errors** — hover/focus-gated, easily missed (NN/g #9).
- **Color-only error signaling** — red border with no icon/text fails colorblind users (NN/g #4–5; WCAG 1.4.1).
- **Cryptic / blaming messages** — "Error 0x2F", "Invalid input" — no cause, no fix.
- **Multi-column layouts** for sequential forms — skipped fields and ambiguous tab order.
- **Wizards with no progress indicator** or that lose data on Back/refresh.
- **Resetting the whole form on one bad field** — discarding correct entries punishes the user for the system's strictness.
- **Placeholder text as the only label** — it disappears on focus, defeating recall and accessibility.

## Accessibility

- **Every field needs a programmatic `<label>`** tied via `for`/`id` (or wrapping). Placeholders are not labels (WCAG 3.3.2 Labels or Instructions; 1.3.1 Info and Relationships).
- **Errors must be announced, not just shown.** Associate the message with the field via `aria-describedby`, set `aria-invalid="true"` on the field, and/or place errors in an `aria-live="assertive"` region so screen-reader users hear them (WCAG 3.3.1 Error Identification).
- **Give actionable correction guidance**, not just "invalid" — WCAG 3.3.3 (Error Suggestion) requires suggesting a fix when one is known.
- **Don't rely on color alone** for error/success state — pair with icon + text (WCAG 1.4.1 Use of Color).
- **Visible focus and full keyboard operation** across all fields, controls, and wizard steps (WCAG 2.4.7; 2.1.1).
- **Set input affordances:** correct `type`/`inputmode` and `autocomplete` tokens (e.g., `autocomplete="email"`) so browsers and AT can autofill and mobile shows the right keyboard (WCAG 1.3.5 Identify Input Purpose).
- **Group related fields** with `<fieldset>`/`<legend>` (e.g., a wizard step, an address block) so the relationship is conveyed to assistive tech.

## Good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Field count** | Every conceivable field, asked upfront | Keep/Cut/Postpone/Explain applied; derive & default; ~6–8 in checkout |
| **Validation timing** | On every keystroke; or only on full-page submit | On blur; positive validation on complex fields; cleared once fixed |
| **Error placement** | Top-of-form summary only, or tooltip-only | Inline, next to the offending field, with icon + tinted background |
| **Error wording** | "Invalid input" / error code / blame | Plain language: what's wrong + how to fix, with an example |
| **Layout** | Multi-column, ambiguous tab order | Single column; labels above; conventional order (Jakob's Law) |
| **Wizard** | No progress indicator; loses data on Back/refresh | Labeled progress; coherent step groups; back-safe; per-step validation |
| **Color reliance** | Red border alone signals the error | Color + icon + text; survives color blindness |
| **A11y** | Placeholder-as-label; silent errors; `aria-invalid` missing | `<label>` + `aria-describedby` + `aria-invalid`; live-region announce; autocomplete tokens |
