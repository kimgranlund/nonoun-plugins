---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Signicat & Sapio Research. *The Battle to Onboard 2022* (5th edition). Survey of 7,600 adults who applied for a financial product in the prior year, across 14 European countries. https://www.signicat.com/the-battle-to-onboard-2022"
  - "Signicat. \"Record number of European consumers abandon financial applications during onboarding\" (press release, 30 March 2022). https://www.signicat.com/press-releases/the-battle-to-onboard-2022"
  - "Baymard Institute. *E-Commerce Cart & Checkout Usability* (ongoing large-scale usability research program; cart-abandonment benchmark aggregates 49 studies, 2006–2023). https://baymard.com/research/checkout-usability"
  - "Baymard Institute. \"How Users Perceive Security During the Checkout Flow.\" https://baymard.com/blog/perceived-security-of-payment-form"
  - "Federal Trade Commission. \"Collecting, Using, or Sharing Consumer Health Information? Look to HIPAA, the FTC Act, and the Health Breach Notification Rule\" — illustrative of the FTC-Act \"unfair or deceptive practices\" frame that also governs fintech claims. https://www.ftc.gov/business-guidance/resources/collecting-using-or-sharing-consumer-health-information-look-hipaa-ftc-act-health-breach"
  - "NN/g. \"Few Guesses, More Success: 4 Principles to Reduce Cognitive Load in Forms.\" https://www.nngroup.com/articles/4-principles-reduce-cognitive-load/"
---

# Finance & Fintech as a Product Genre

Finance is the genre where the product's core job is to make a stranger comfortable handing over money and identity to software. Two forces shape almost every screen: **trust** (the user is risking funds and personal data, often before they have any relationship with you) and **regulation** (identity verification, disclosures, and data handling are not optional UX choices — they are legal obligations that you must absorb into the flow without destroying it). The defining design tension of the genre is that the legally-required friction (KYC, disclosures, security checks) collides head-on with the conversion incentive, and the abandonment data shows the collision is brutal. This reference treats consumer fintech — banking, payments, lending, brokerage/portfolio, personal finance — as the center of gravity; the same principles harden as you move toward regulated brokerage and away from light personal-finance trackers.

> The discipline in one line: every gram of friction in a money app must be either legally required or trust-building — friction that is neither is pure leakage, and the leakage is measurable.

## Conventions: what a competent finance product reliably does

These are the table-stakes patterns a user has been trained to expect by incumbents and well-run challengers. Violating one reads as either amateurish or untrustworthy, which in this genre are the same failure.

- **Trust is established before the ask, not after.** Security posture, regulatory standing (e.g. "deposits insured," licensing/registration where applicable), and what data is being collected and why are surfaced _at_ the point of the ask — Baymard's checkout-security work finds users judge security by visible cues near the sensitive field, not by the actual cryptography. The cue must sit next to the input, not on an "About" page.
- **Onboarding is staged, not front-loaded.** The flow asks for the minimum to deliver first value, then layers identity and funding as the user commits. This is **progressive disclosure / progressive data input**: don't demand SSN, full address, and a document scan on screen one.
- **KYC/identity verification is explained and given a progress model.** Users tolerate document upload and a liveness/selfie check far better when told it's a legal requirement, how long it takes, and where they are in it. An unexplained camera permission request mid-flow is a classic abandonment trigger.
- **Money movements are confirmed, reversible where possible, and receipted.** A transfer shows amount, destination, fee, and arrival time _before_ commit; produces an immediate confirmation; and lands in a durable transaction history. Irreversibility is disclosed loudly (wires, crypto sends).
- **Numbers are precise, formatted, and never ambiguous.** Currency, decimals, dates, fees, and pending-vs-settled balances are unambiguous. "Available" vs "current" balance is a distinction users will hold you legally and emotionally responsible for.
- **Regulatory disclosures are present but designed.** APR, fees, risk warnings ("investments can go down"), and terms appear where the decision is made — folded into the flow with good typography, not dumped as a wall of fine print or hidden behind a checkbox nobody reads.

## Signature patterns

The genre-specific UI moves that distinguish finance from generic SaaS.

### Progressive data input (the staged KYC funnel)

The strongest pattern in the genre. Decompose onboarding into a sequence — _account creation → identity (KYC) → funding_ — where each stage is short, justified, and ideally delivers a small payoff (you can see the dashboard before you've funded; you can browse a portfolio before full verification). Each added field and each added step is a known drop-off point, so the design question is always "can this be deferred until after the user has committed?" The Signicat data below is the reason this pattern exists.

### Trust cues co-located with the ask

Encryption/lock affordances, licensing or insurance statements, recognizable third-party security/identity-provider marks, and a plain-language "why we need this" sit adjacent to the sensitive input. Baymard's eye-tracking research on payment forms found that _familiar_ marks (e.g. PayPal, well-known security brands) were recalled as adding security far more than unfamiliar ones — recognizability, not the underlying certificate, drives perceived safety. (Single-program source; treat as directional.)

### The spending / portfolio dashboard

The home surface for consumer finance. Conventions: a hero balance or net-worth figure; a time-series of the thing the user cares about (balance, portfolio value, spend-by-category); a clear pending-vs-settled distinction; and drill-down to transactions. For investing products, gain/loss must be honest about cost basis and time window — a "+12%" with no timeframe is a dark pattern waiting to be a complaint.

### Security UX as an ongoing surface, not a one-time gate

2FA/biometric unlock, step-up authentication for risky actions (adding a payee, large transfer, changing security settings), session/device management, and clear, human breach/fraud-alert messaging. The pattern: _raise_ authentication friction in proportion to the risk of the action, and keep it _low_ for read-only viewing.

```text
Step-up authentication — friction proportional to risk (illustrative ladder)

  View balance / history ........ session auth only (biometric unlock)
  Move money to a saved payee ... confirm in-app (push/biometric)
  Add a NEW payee / change limit  step-up: re-auth + out-of-band confirm
  Wire / irreversible transfer .. step-up + explicit irreversibility notice
  Change security settings ...... step-up + notification to user's channels
```

## Key metrics

What this genre actually measures. Cite the authoritative figures; treat single-vendor numbers as directional.

- **Onboarding / application abandonment rate.** The headline genre metric. Signicat's _Battle to Onboard 2022_ (7,600 European applicants, 14 countries, fielded by Sapio Research) found **68% of consumers had abandoned a financial application in the past year, up from 63% in 2020** — and the average abandoner gave up after **18 min 53 s** (down from ~26 min in 2020, i.e. patience is shrinking). The top three abandonment reasons were roughly equal: application took too long (21%), too much personal information requested (21%), and changed their mind (21%); separately, **38%** abandoned because they lacked the right identity credential (e.g. passport / digital ID). These are the canonical genre benchmarks.
- **KYC / identity-verification completion rate** — the conversion of the single highest-drop step. Document upload, liveness/biometric, and address verification are repeatedly named as the steepest exit points. (Widely reported across fintech-vendor sources; directional, not a single audited benchmark — label as such when quoting a specific percentage.)
- **Funding / activation rate** — share of verified accounts that complete first deposit or first transaction. The gap between "verified" and "funded" is where many neobanks actually leak.
- **Data-privacy concern as a conversion drag.** Signicat: **92%** of consumers are concerned about how financial providers use and protect their data — a standing headwind that trust cues and clear data-use copy exist to counter.
- **Trust-cue conversion lift** — frequently cited in vendor "trust badge" studies (e.g. CXL's eye-tracking work showed differential recall across badges). Real directionally, but the round "+X% conversion" figures circulating in marketing blogs are **vendor-reported and not peer-reviewed — do not present them as established benchmarks.**

## Pitfalls

The recurring ways finance products fail.

- **Front-loading identity.** Demanding full KYC (SSN, document scan, liveness) before the user has seen any value is the single biggest, best-documented leak (Signicat). The fix is staging, not a prettier form.
- **Unexplained or untimed friction.** A camera-permission prompt, an SSN field, or a "verifying…" spinner with no explanation, no "why," and no progress model converts a tolerable legal step into an exit.
- **Hiding required disclosures — or drowning the screen in them.** Both fail. Burying APR/fees/risk warnings invites regulatory and trust failure; dumping an undesigned wall of fine print buries the one disclosure that matters. The FTC Act's prohibition on _unfair or deceptive_ practices means a misleading or buried fee/term is a legal exposure, not just a UX smell.
- **Ambiguous money state.** Conflating pending vs settled, available vs current, or showing a gain/loss with no timeframe or cost basis. Users treat any ambiguity about _their money_ as either a bug or a betrayal.
- **Treating security as a one-time gate.** No step-up auth for risky actions, no device/session visibility, robotic fraud-alert copy. Security UX is a continuous, proportional surface; a single login wall is not it.
- **Optimizing the funnel into a dark pattern.** Pre-checked add-ons, a buried "no thanks," obscured irreversibility, or a "+12% returns!" with no risk context. In a regulated genre this is the failure mode that converts a growth win into an enforcement action.

## Good vs. bad

Concrete contrasts that separate a trustworthy money product from a leaky or predatory one.

```text
KYC / onboarding
  BAD : Screen 1 demands name, DOB, full address, SSN, and a passport scan —
        no explanation, no progress bar, camera opens with no warning.
  GOOD: Create account → see the (empty) dashboard → "To move money we have to
        verify your identity (legal requirement, ~2 min). Step 2 of 3."
        Each field justified; document step previewed before the camera opens.

Trust cues
  BAD : "Bank-grade security!" on a marketing page; nothing near the SSN field.
  GOOD: Plain-language "why we ask for this + how it's protected," with a
        recognizable security/identity mark, sitting beside the sensitive input.

Disclosures
  BAD : 19.99% APR and a $35 fee discoverable only in a linked PDF of terms.
  GOOD: APR, fees, and the risk warning rendered at the point of decision,
        in real type, with the total cost shown before commit.

Portfolio / balance
  BAD : "+12.4%" hero number — no timeframe, no cost basis, green and huge.
  GOOD: "+12.4% (past 12 months, vs cost basis)"; pending vs settled labeled;
        losses shown as plainly as gains.

Money movement
  BAD : One-tap "Send" on a saved payee; new wire with no irreversibility notice.
  GOOD: New payee triggers step-up auth; wire shows "this cannot be reversed"
        before commit; every movement produces a receipt and a history entry.
```

The throughline: in finance, **trust is the product and friction is the tax.** Every required step must be staged late, explained, and visibly safe; every number must be unambiguous; and every growth optimization must survive the question "would a regulator or a defrauded user call this deceptive?" The genre rewards products that treat compliance as a design surface rather than a checkbox — and punishes, sometimes legally, the ones that don't.
