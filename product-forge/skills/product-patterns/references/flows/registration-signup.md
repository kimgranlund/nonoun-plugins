---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Raluca Budiu. \"Login Walls Stop Users in Their Tracks.\" Nielsen Norman Group, 2014-03-02. https://www.nngroup.com/articles/login-walls/"
  - "Raluca Budiu. \"A Checklist for Registration and Login Forms on Mobile.\" Nielsen Norman Group, 2017-06-04. https://www.nngroup.com/articles/checklist-registration-login/"
  - "Aurora Harley, Kim Flaherty. \"'Get Started' Stops Users.\" Nielsen Norman Group, 2017-08-20. https://www.nngroup.com/articles/get-started/"
  - "Bruce Tognazzini. \"How to Achieve Painless Registration.\" AskTog / Nielsen Norman Group. https://www.nngroup.com/articles/how-achieve-painless-registration/"
  - "Jon Yablonski. \"Hick's Law\" and \"Postel's Law.\" Laws of UX. https://lawsofux.com/"
---

# Registration & Sign-Up

Registration is the moment a product asks a stranger to commit before they have a reason to. It is the single most over-eagerly deployed gate in software, and almost every default version of it leaks users. The discipline here is not "design a beautiful form" — it is **deciding whether to ask at all, and if so, asking for the least, at the latest defensible moment, in exchange for visible value.** This reference defines the canonical sign-up/login flow, its high-value variants (social/SSO, magic links, progressive registration), the friction-vs-security trade-off that governs every choice, and a good-vs-bad rubric a UX-quality reviewer can score against.

> The governing finding, from Raluca Budiu's analysis of login walls: a registration or login wall imposes a high **interaction cost**, and "people have to be highly motivated in order to incur that cost." Before designing the form, justify the wall — most experiences cannot.

---

## When to use it (and when not to)

The first decision is binary and architectural: does this product need an account at this point in the journey? NN/g's login-wall guidance gives a clean test — gate hard only when the value to the user _requires_ identity, and defer or skip otherwise.

| Situation | Verdict | Why |
| --- | --- | --- |
| Highly personal, persistent data (email, banking, health records) | **Gate up front** | The product is meaningless without an identity to attach data to; security justifies the cost. |
| Returning users to an established account | **Login, not registration** | The account already exists; the job is fast, low-friction re-entry. |
| E-commerce checkout | **Defer — offer guest checkout** | Forcing account creation before purchase is a documented conversion killer; ask _after_ the sale via the reciprocity principle. |
| First visit / first app launch / content browsing | **Skip or defer** | Users have no reason to commit; let them experience value, then invite registration when they have something to save. |
| A "Get Started" button that drops users into a sign-up form | **Anti-pattern** | NN/g (Harley & Flaherty): "Don't ask for too much too soon, or you risk losing people's trust." Users expect reciprocal value before commitment. |

The unifying rule: **registration is a cost the user pays; value is what you pay them with.** If you cannot name the value the user receives in exchange for registering _right now_, you are asking too early.

---

## The canonical form

When registration is justified, the canonical mobile-and-web form is deliberately minimal. Budiu's checklist is the reference standard; the spine is "ask for the minimum, make every field forgiving, never make the user type twice."

```text
┌─────────────────────────────────────────┐
│  Create your account                      │
│  (one line: the benefit of doing so)      │
│                                           │
│  [ Continue with Google        ]  ← SSO   │
│  [ Continue with Apple         ]          │
│  ───────────  or  ───────────             │
│  Email     [______________________]       │
│  Password  [______________] [👁 Show]      │  ← masked by default, toggle to reveal
│            Min 8 chars · 1 number         │  ← constraints shown UP FRONT
│            [▓▓▓░░] strength               │
│                                           │
│  [          Create account          ]     │
│  Already have an account?  Log in →       │
└─────────────────────────────────────────┘
```

Budiu's checklist items, restated:

- **Explain the benefit of registering** — one line, near the form, answering "why should I?"
- **Ask for the minimum** — email + password is the floor; every extra field is friction. (Hick's Law: decision/effort cost rises with the number and complexity of inputs.)
- **Make the password visible via a "Show password" toggle**, masked by default — typing a hidden password on a phone keyboard is error-prone.
- **Disclose password constraints up front**, before the user types, not as a post-submit error; pair with a real-time **strength meter**.
- **Never use a duplicate "confirm password" field** — the show/hide toggle replaces it and removes a guaranteed friction point.
- **Don't force email confirmation to proceed** when avoidable; if verification is required, an SMS/OTP code or a magic link is lighter than "go check your inbox and come back."
- **Forgiving input** (Postel's Law — "be liberal in what you accept"): trim whitespace, accept emails case-insensitively, don't reject a pasted card or phone number over formatting.

For **login** specifically, Budiu adds: mask the password with a Show toggle, always include a **"Forgot password?"** link (rarely used passwords are forgotten), and support **biometric auth** (Face ID / fingerprint) and platform password managers so returning users rarely type anything.

---

## Key variants

### Social login / SSO

A single "Continue with Google/Apple/Microsoft" button collapses sign-up, login, and email verification into one tap and eliminates a new password. It is the lowest-friction option for returning users (a fraction of a second once the provider session exists). Trade-offs to design around:

- **Provider sprawl and the "which button did I use?" problem** — offer two or three providers, not eight, and on return show or remember the method the user chose so they don't create a second, orphaned account with a different provider.
- **Platform requirements** — Apple's App Store guidelines require offering "Sign in with Apple" if you offer other third-party social logins; design the button set accordingly.
- **Dependency and privacy** — you inherit the provider's outages and the user inherits a data-sharing relationship; always keep an email-based path as a fallback.

### Magic links (passwordless email)

The user enters an email, receives a one-time link, and clicking it both authenticates and (for new users) creates and verifies the account in one motion — collapsing sign-up and email verification into a single fluid step. Where it fits and where it bites:

- **Best for low-friction, lower-assurance contexts** — newsletters, trials, consumer apps where "no password to forget" is the win.
- **The honest security caveat (label this as a contested claim):** practitioners disagree on whether magic links are _more secure_ than passwords. A common critique is that a magic link is a single possession factor (access to the inbox) — it is not two factors, so it offers convenience rather than added security on its own; its assurance is only as strong as the email account and email-delivery chain (SPF/DKIM/DMARC). Treat "passwordless = more secure" as **vendor-dependent and disputed**, not settled.
- **The latency and reliability cost** — the user must context-switch to their inbox; a delayed or spam-filtered email is a hard stop. OTP codes are a faster-feeling sibling (type 6 digits in place) that avoid the inbox round-trip.

### Progressive registration (lazy / deferred registration)

Let the user _do the thing first_ and create the account only when there is something worth saving — the cart to check out, the document to keep, the score to record. This is the deferral NN/g's login-wall and "Get Started" guidance both point to: value precedes the ask, and by the time you ask, the reciprocity is real ("you just built this — want to save it?").

A related move is **progressive profiling**: collect the bare minimum at sign-up, then enrich the profile over later sessions when each field is contextually justified, rather than front-loading a long form.

---

## The friction-vs-security trade-off

Every registration decision is a point on one axis: **less friction converts more users; more friction (more factors, more verification) raises assurance.** The error is treating this as a single global setting. The mature pattern is **progressive / risk-based security** — match the assurance to the stakes of the action, not to the moment of sign-up.

```text
   LOW assurance ───────────────────────────────► HIGH assurance
   social / magic link / OTP   password   password + 2FA / passkey / step-up
        │                          │                    │
   newsletter, trial,        general account,     payments, admin, money
   content app                profile data        movement, data export

   Rule: raise the bar at the RISKY ACTION, not uniformly at the front door.
```

- **Don't tax low-risk users with high-assurance friction.** Requiring 2FA to read a free article loses the reader for no security gain.
- **Do step up at the moment of risk.** A trial can start with a magic link; require a stronger factor only when the user upgrades to paid, moves money, or changes security settings.
- **Friction is not always loss.** A small, _legible_ friction at a genuinely risky step (a confirmation, a re-auth before a destructive action) reads as the product taking the user's safety seriously. The failure mode is friction the user can't connect to a benefit.

---

## Common mistakes & anti-patterns

- **The premature wall** — forcing registration before the user has experienced any value (the login wall on a first visit; the "Get Started" CTA that is really a sign-up form). The highest-leverage fix is usually to _remove the gate_, not polish it.
- **The kitchen-sink form** — asking for name, company, phone, and role at sign-up "while we have them." Each field is measurable drop-off; collect later via progressive profiling.
- **The hidden-rules password** — masking the password with no Show toggle, and revealing the rules only after a failed submit. Disclose constraints up front; offer reveal.
- **The confirm-password field** — a guaranteed extra error path that the show/hide toggle makes obsolete.
- **The forced inbox detour** — blocking first use on "verify your email," sending the user out of the product, and losing them to the inbox. Defer verification or use OTP/magic-link flows that don't require a return trip.
- **The orphaned-account trap** — a user who signed up with Google last time types email/password this time and silently creates a second account. Detect the existing identity and route them to their original method.
- **Dark-pattern defaults** — pre-checked "subscribe me" boxes, a buried "no thanks," or burying guest checkout below the fold. These convert short-term and erode trust long-term.
- **Punishing error handling** — clearing the form on error, vague "invalid input," or rejecting valid emails over case or whitespace (a Postel's Law violation).

---

## Accessibility notes

- **Label every field with a real, programmatic `<label>`** — placeholder text is not a label; it disappears on focus and is invisible to many screen readers and to users with memory load.
- **Use correct input types and autocomplete tokens** — `type="email"`, `inputmode`, and `autocomplete="email" / "current-password" / "new-password" / "one-time-code"` so browsers and password managers autofill and the right mobile keyboard appears. This is both an accessibility and a friction win.
- **Don't trap focus or disable paste** — disabling paste in password or OTP fields breaks password managers and is a documented usability and accessibility failure.
- **Announce errors with `aria` and tie them to their field** — error text must be programmatically associated (e.g., `aria-describedby`) and announced, not signalled by color alone (WCAG 1.4.1 Use of Color).
- **Show-password toggle must be a real, labeled, keyboard-reachable control** with state communicated to assistive tech (e.g., `aria-pressed`).
- **Meet target size and contrast** — buttons and toggles should satisfy WCAG 2.2 target-size guidance; the strength meter and constraint text must not rely on color alone.
- **CAPTCHAs are an accessibility hazard** — image/audio challenges block real users; prefer invisible/risk-based bot mitigation and always provide an accessible alternative.

---

## Good vs bad

A UX-quality rubric can score a registration flow on these observable signals.

```text
GOOD                                          BAD
────────────────────────────────────────────────────────────────────
Value experienced before the ask        →    Login wall on first contact
Benefit of registering stated at form    →    Bare form, no "why"
Email + password (or one SSO tap)         →    8 fields "while we're here"
Password masked WITH a Show toggle        →    Masked, no reveal, no rules shown
Constraints + strength shown up front     →    Rules revealed only on failed submit
No confirm-password field                 →    Duplicate-entry confirm field
Guest checkout offered; register after    →    Forced account creation before purchase
SSO + email fallback; remembers method    →    SSO only, or orphaned duplicate accounts
Assurance raised at the risky action      →    2FA tax on low-risk reading
Forgiving input; errors tied to fields    →    Form cleared on error; vague messages
Real labels, autocomplete, paste allowed  →    Placeholder-as-label; paste disabled
```

The through-line for the reviewer: **a good flow earns the right to ask, asks for the minimum, and matches security to stakes; a bad flow gates first, asks for everything, and treats every user as a payment-grade risk.**
