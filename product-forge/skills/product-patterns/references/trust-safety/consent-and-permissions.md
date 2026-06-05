---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Regulation (EU) 2016/679 (GDPR), Article 4(11) (definition of consent) and Article 7 — 'Conditions for consent,' incl. Art. 7(3) 'it shall be as easy to withdraw as to give consent.' https://gdpr-info.eu/art-7-gdpr/"
  - "European Data Protection Board. *Guidelines 03/2022 on Deceptive Design Patterns in Social Media Platform Interfaces* (adopted Feb 2023). https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032022-deceptive-design-patterns-social-media_en"
  - "California Civil Code §1798.140(l) (CCPA/CPRA) — consent obtained through 'dark patterns' is not consent; and CPPA consumer-rights overview. https://oag.ca.gov/privacy/ccpa"
  - "Maria Rosala. \"3 Design Considerations for Effective Mobile-App Permission Requests.\" NN/g, 2019-04-28. https://www.nngroup.com/articles/permission-requests/"
---

# Consent & Permissions

Consent is the moment a product asks for something it cannot take by right — access to a sensor, a contact list, or the user's agreement to be tracked or profiled. This reference is about whether that consent is _genuine_: a freely given, informed, specific, reversible "yes," versus a manufactured one extracted by bundling, defaults, asymmetry, or fatigue. It is the trust-discipline companion to the UX-mechanics file (`flows/permissions-consent.md`, which covers permission priming, just-in-time timing, and the OS-dialog dance) — that one is about _how to ask well_; this one is about _what makes the answer real_ and the design implications of the regimes (GDPR, CCPA/CPRA) that increasingly say a coerced yes is no consent at all. The load-bearing principle: **the user must be able to refuse without losing the core function they came for** — if "no" breaks the product, the "yes" was never free.

> The legal definition that drives the design, from GDPR Article 4(11): consent is "any freely given, specific, informed and unambiguous indication" of agreement, "by a statement or by a clear affirmative action." Each adjective is a design constraint. _Freely given_ → refusal can't cost the core service. _Specific_ → no bundling unrelated purposes. _Informed_ → plain-language statement of what and why. _Unambiguous / affirmative_ → no pre-ticked boxes, no silence-as-yes.

This file describes **design implications, not legal advice** — the patterns that follow are how the regimes' principles cash out at the interface, not a compliance opinion. Where a specific article or deadline is cited, it is the durable principle that matters; verify current rule text before relying on it.

---

## The four conditions of genuine consent

GDPR's four adjectives are the cleanest checklist anyone has produced for "is this consent real," and they apply far beyond the EU as a design standard. Run each as a test.

| Condition | The test | Fails when |
| --- | --- | --- |
| **Freely given** | Can the user refuse and still get the core thing they came for? | Refusal blocks the service; consent is the price of entry to something unrelated |
| **Specific** | Is each distinct purpose consented separately? | Analytics, marketing, and third-party sharing bundled under one "I agree" |
| **Informed** | Does the user know what data, for what purpose, to whom — in plain words? | "To improve your experience"; a 40-page policy no one reads as the only disclosure |
| **Unambiguous** | Is consent an affirmative act the user took on purpose? | Pre-ticked boxes; "by continuing you agree"; silence or inactivity counted as yes |

The most-violated condition is **freely given**, because it is the one with revenue attached. The EDPB's "consent or pay" scrutiny and the GDPR's own Recital 43 (consent is presumed not freely given when it's a condition of a service that doesn't actually need the processing) both target the same move: making the user pay for refusal. The design implication is blunt — separate the data grab from the core function, so a "no" to tracking still leaves a working product.

---

## Just-in-time vs. upfront: when to ask

_Where_ in the journey you ask changes whether consent is informed. Two postures, and the rule for choosing.

- **Upfront / batch.** All permissions and consents requested at first launch or sign-up, before any feature is used. The failure mode: the user has no context to evaluate the request ("why does a notes app want my location?"), so they either refuse by reflex or click-through to escape — neither is informed consent. Upfront is appropriate only for the one or two grants the product genuinely cannot start without, stated with their reason.
- **Just-in-time / contextual.** The request fires at the moment the user takes an action that obviously needs it — a camera prompt the instant they tap "scan a receipt." NN/g (Rosala) frames this as the timing rule for effective permission requests: ask in context, where the request is self-justifying. The benefit is legible because the user is already reaching for the feature, so the "yes" is meaningfully informed.

```text
BAD (upfront batch):                      GOOD (just-in-time):
First launch →                            User taps "Add photo" →
  ┌────────────────────────────┐            ┌────────────────────────────┐
  │ Allow Location?            │             │ Allow camera to take the   │
  │ Allow Contacts?            │             │ photo you're adding?       │
  │ Allow Notifications?       │             │ [ Not now ]  [ Allow ]     │
  │ Allow Camera?              │             └────────────────────────────┘
  │ [ Allow All ]              │           ↑ self-justifying: the user
  └────────────────────────────┘             already wants the feature
  ↑ no context; reflex-deny or click-through
```

The default posture is just-in-time; upfront is the exception you justify, not the norm you default to.

---

## The right to refuse — and to withdraw

Two distinct rights, both load-bearing, both routinely designed away.

- **Refuse without losing core function.** This is the "freely given" condition made operational. A user who declines tracking, or a non-essential permission, must still get the product's core value. Concretely: decline must be as reachable as accept (symmetric effort), and the consequence of declining must be proportionate — losing a feature that genuinely needs the data is fine; losing the whole product because you wouldn't accept marketing cookies is coercion. Graceful degradation is the pattern: offer a reduced-capability path (manual entry instead of contacts) so "no" narrows the experience rather than ending it.
- **Withdraw as easily as you gave.** GDPR Article 7(3) is explicit: "it shall be as easy to withdraw as to give consent." The design implication is a standing, findable control (a privacy/permissions center) where any prior consent can be revoked in roughly the same number of steps it took to grant — not a buried email-the-DPO process. If granting was one tap and withdrawing is a support ticket, the asymmetry itself is the defect. (See `auditability-and-control.md` for the broader control surface this lives in.)

The tell that refusal is real: try to say no. If "no" is hidden, multi-step, guilt-tripped, or breaks the product, the consent architecture is extractive.

---

## Dark-pattern consent: the manufactured yes

A consent UI can technically collect a "yes" while destroying every condition that makes it real. Regulators now name this directly: under CCPA/CPRA, agreement obtained through "dark patterns" is **not** valid consent (Cal. Civ. Code §1798.140(l)); the EDPB's deceptive-design guidelines (03/2022) catalogue the interface tricks that invalidate consent under GDPR. These are findings to flag, never patterns to ship. (The full deceptive-pattern taxonomy lives in `monetization/dark-patterns.md`; here is the consent-specific subset.)

| Dark-pattern consent | What it breaks | The honest form |
| --- | --- | --- |
| **Forced / bundled consent** | Freely given + specific — refusal blocks the service, or unrelated purposes share one switch | Separate each purpose; decline leaves core function intact |
| **Asymmetric choice** | Freely given — "Accept all" is one loud button; "Reject" is buried or multi-click | Accept and reject equally prominent, equally few clicks |
| **Pre-ticked / opt-out defaults** | Unambiguous — consent is the default state the user must notice and undo | Affirmative opt-in; every box starts unchecked |
| **Confirmshaming** | Freely given — the decline is worded to shame ("No, I don't want to save money") | Neutral decline copy; "No thanks" without the guilt |
| **Hard-to-withdraw** | Art. 7(3) — granting is one tap, revoking is a support process | Withdrawal as easy as granting, in a standing control |
| **Consent fatigue / interface interference** | Informed — endless nags or visual tricks until the user clicks "yes" to escape | Ask once, in context; respect a "not now" |

The unifying tell, and the single fastest audit: **symmetry**. If saying yes is meaningfully easier than saying no — fewer clicks, louder button, no guilt, no broken product — the design is engineered to extract consent, and under GDPR/CCPA-style regimes that consent may not legally count. Genuine consent is symmetric by construction.

---

## Anti-patterns

- **Consent as the price of entry.** The product won't work at all unless the user agrees to processing it doesn't actually need — the "freely given" violation with revenue behind it (GDPR Recital 43; EDPB "consent or pay").
- **The bundle.** One "I agree" covering analytics, marketing, personalization, and third-party sale at once — destroys "specific." Each purpose needs its own switch.
- **Pre-ticked everything.** Consent boxes that start checked, so inaction is taken as agreement — destroys "unambiguous" and is invalid under GDPR.
- **The asymmetric banner.** Prominent "Accept all," buried or multi-click "Reject" — the canonical cookie-consent dark pattern, explicitly flagged by the EDPB and invalid as consent under CCPA.
- **Confirmshaming the no.** Wording the decline to shame or scare the user into the yes.
- **Withdrawal black hole.** Easy to consent, near-impossible to revoke — violates Art. 7(3) directly.
- **Upfront permission gauntlet.** Every permission demanded at launch with no context — depresses grants and produces uninformed reflex-clicks, not consent.

---

## The scoring test: is consent genuine or manufactured?

1. **Freely given.** Can the user refuse a non-essential grant and still get the core function — or does "no" break the product or gate it behind acceptance of something unrelated?
2. **Specific.** Is each distinct purpose consented separately — or are unrelated purposes bundled under one "I agree"?
3. **Informed and in context.** Does the user know what data, why, and to whom in plain words, asked just-in-time where the need is obvious — or upfront, vague, and out of context?
4. **Unambiguous.** Is consent an affirmative act — no pre-ticked boxes, no "by continuing you agree," no silence-as-yes?
5. **Symmetric and reversible.** Is declining as easy as accepting, and is withdrawing as easy as granting (a standing control), per GDPR Art. 7(3)?

A product passes when a user can say no as easily as yes, refuse the non-essential and still use the product, understand exactly what each grant covers, and revoke it later in one place. It fails when the consent UI is engineered so that yes is the path of least resistance — at which point, under GDPR and CCPA, it may not be consent at all.

---

## One labeled caveat

This file describes **design implications, not legal advice**, and is not a compliance opinion for any jurisdiction. The GDPR Article 4(11) definition and Article 7(3) withdrawal quote are verbatim from the regulation text. The "consent or pay" / "freely given" reasoning tracks GDPR Recital 43 and the EDPB's published opinions and Guidelines 03/2022 on deceptive design; specific guideline numbering and any enforcement deadlines shift over time — treat the principles as durable and verify current text before relying on a specific article or date. The CCPA/CPRA "dark patterns are not consent" rule is Cal. Civ. Code §1798.140(l). NN/g's just-in-time / contextual-timing guidance is Rosala (2019). The deceptive-pattern names (confirmshaming, forced action, asymmetric choice) follow the Brignull / deceptive.design taxonomy detailed in `monetization/dark-patterns.md`.
