---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Eric Meyer & Sara Wachter-Boettcher. *Design for Real Life.* A Book Apart, 2016 — the 'stress cases' (not edge cases) reframing and worst-case / vulnerable-user thinking."
  - "OWASP Foundation. \"Abuse Case Cheat Sheet\" and the 'Secure by Default' principle (OWASP Developer Guide / Top 10 Proactive Controls C5). https://cheatsheetseries.owasp.org/cheatsheets/Abuse_Case_Cheat_Sheet.html ; https://owasp.org/www-project-proactive-controls/"
  - "Jakob N.. \"Confirmation Dialogs\" / error-prevention heuristic (Heuristic 5, 'Error Prevention'). Nielsen Norman Group. https://www.nngroup.com/articles/ten-usability-heuristics/"
---

# Designing for Risk & Harm

Most product design optimizes for the cooperative user doing the intended thing. This reference is about the rest of reality: the user who misuses the feature, the attacker who abuses it, the person who hits it mid-crisis, and the action that — done by accident or malice — causes harm that can't be taken back. The discipline is to design _against_ the worst plausible use, not just for the best intended one. It draws together misuse/abuse-case thinking (OWASP), safety- and secure-by-default, harm reduction, the "stress case" reframing (Meyer & Wachter-Boettcher), friction-as-safety on dangerous actions, and the practice of red-teaming your own design before someone else does. It is the harm-side hardening of the trust cluster: `trust-control-steerability.md` calibrates autonomy to risk; this file is about identifying the risk in the first place and designing so the harm doesn't happen. The load-bearing principle: **the worst-case user is not an edge case to defer — they are a primary case to design for**, because the harm they cause (or suffer) is the harm that ends up on the front page.

> The reframing to hold onto, from Meyer & Wachter-Boettcher: design for "stress cases," not "edge cases." The term "edge case" implies rare and dismissible; their point is that the hard cases — the person in crisis, grief, panic, or under threat — are not edges but a normal, recurring slice of real users, and "when we call them edge cases, we... give ourselves permission to ignore them." Renaming them stress cases makes them un-ignorable.

The frameworks here are established: OWASP's abuse cases and secure-by-default are mature security practice; "Design for Real Life" is a named, widely-cited design text. AI-specific red-teaming is a fast-moving area where the _principle_ (adversarially probe your own system for harmful outputs before release) is well-established even as specific methods evolve; that is labeled below.

---

## Misuse and abuse cases: design against, not just for

A use case describes a cooperative user achieving a goal. OWASP's **abuse case** is the inverse: a description of how a hostile or careless actor turns the same feature against its intent or against other people. The practice is to write them down alongside the use cases, because "developing abuse cases helps engineers think from the attacker's perspective." Two distinct actors, often conflated, must both be modeled:

- **Misuse (benign actor, bad outcome).** A well-meaning user does something harmful by mistake or because the design invited it — deletes the wrong thing, shares to the wrong audience, fires the irreversible action they didn't understand. The defense is design (defaults, friction, reversibility), not policing.
- **Abuse (malicious actor, intentional harm).** A hostile user weaponizes the feature against others or the system — harassment via a messaging feature, doxxing via a profile field, fraud via a payment flow, prompt-injection or jailbreak of an AI feature, scraping a "find friends" lookup to harvest data. The defense is constraint, detection, and rate-limiting.

```text
For each feature, write the inverse of its use cases:

  USE CASE   — "User shares a post with friends."
  MISUSE     — "User accidentally shares a private post publicly."
               → design defense: privacy-default + a visible audience indicator + undo
  ABUSE      — "Attacker mass-shares to harass / floods a target with mentions."
               → design defense: rate limits, block/mute, report, no-mention-from-strangers

  Ask of every input field, every action, every integration:
    "Who is harmed if this is used by the worst person I can imagine,
     or by a good person on their worst day?"
```

The deliverable is a list of harms the feature enables and the design defense for each — produced _before_ build, not after the incident report.

---

## Safety / secure by default

The single highest-leverage harm control is the default, because most users never change settings (Nielsen's defaults principle) and because the out-of-the-box state is the state that ships to everyone. OWASP's **secure-by-default** principle: products should "start in a secure state without requiring... configuration," and the default settings should be "the most secure settings possible." Generalized to harm: the default should be the _safest_ state, and the user should have to deliberately opt _into_ risk, never accidentally fall into it.

| Domain | Safe default (ship this) | Unsafe default (the harm) |
| --- | --- | --- |
| **Visibility** | Private / friends-only; user opts into public | Public-by-default; user is exposed before they notice |
| **Sharing / discovery** | Not discoverable by phone/email unless enabled | Searchable by default — enables stalking, scraping |
| **Permissions** | Least privilege; granted just-in-time | Broad access pre-granted "to be safe" |
| **Destructive actions** | Reversible (trash/undo) by default | Hard-delete by default; mistakes are permanent |
| **AI autonomy** | Suggest / confirm; user opts into autonomous | Acts autonomously on high-stakes actions by default |
| **Data retention** | Minimize and expire | Keep everything forever (breach surface) |

The tell of safety-by-default: a brand-new user who changes nothing is in the safe state, and reaching a risky capability takes a deliberate act. The tell of its absence: the user is exposed, over-permissioned, or one misclick from permanent loss the moment they arrive — and "they could have changed the setting" is the excuse offered after the harm.

---

## Harm reduction and friction-as-safety

You cannot prevent every harmful action without making the product unusable; harm _reduction_ accepts that some risky actions will be attempted and designs to lower the damage when they are. The primary lever is **friction deliberately placed on dangerous, irreversible actions** — speed bumps that interrupt the automatic, scaled to the stakes. Friction is normally a usability cost; on a dangerous action it is a safety feature, because it converts an impulsive or accidental act into a considered one.

The graduated friction ladder, lightest to heaviest — match the rung to harm × reversibility (the calibration in `trust-control-steerability.md`):

1. **None.** Reversible, low-stakes (draft, archive, anything with undo) — don't add friction; add reversibility instead.
2. **Undo window.** The action proceeds but is reversible for a period ("Undo send"; trash for 30 days) — protects against mistakes without interrupting the common case. The preferred control where possible (Nielsen H3, and `auditability-and-control.md`).
3. **Confirmation.** "Are you sure?" — weak, because users click through it. Use only when undo is impossible, and make it _informative_ ("This permanently deletes 1,240 files") not reflexive ("Are you sure?").
4. **Type-to-confirm / re-authenticate.** For high-stakes irreversible actions (delete account, wire funds, drop a database) — require typing the resource name or re-entering a password, defeating the click-through reflex. Friction proportional to permanence.
5. **Cooling-off / delay.** For the most consequential and abuse-prone (account deletion with a grace period, a large transfer with a hold, a cancel-account flow that can be reversed for 14 days) — time itself is the safety mechanism, undoing impulse and giving harm a chance to be caught.

```text
HARM × IRREVERSIBILITY rises  ──────────────────────────────────────►
  reversible          undo            confirm        type-to-       cooling-off
  + low stakes        window          (informative)  confirm /      / delay
                                                      re-auth
  ◄── add reversibility, not friction ──┤  ├── add friction proportional to permanence ──►
```

The discipline (and the common error it prevents): don't sprinkle confirmation dialogs on everything — that just trains click-through and adds no safety. Put _real_ friction on the few genuinely dangerous, irreversible actions, and make the rest reversible instead. Friction is a scarce resource; spend it where harm is permanent.

---

## Vulnerable-user and worst-case-user thinking

Two populations break the "average cooperative user" assumption in opposite directions, and both are primary, not edge.

- **The vulnerable user (harm _to_ them).** Meyer & Wachter-Boettcher's stress cases: the person hitting your product in crisis, grief, panic, financial distress, illness, abuse, or under coercion. Their canonical example is Facebook's "Year in Review" auto-celebrating a feed that, for Meyer, surfaced a photo of his recently deceased daughter ringed in party graphics — a feature that worked perfectly for the happy case and wounded the grieving one. The design move is to imagine the feature meeting someone on their worst day and ask what assumption it makes that breaks: celebratory framing, cheerful copy, an upbeat empty state, a "memories" resurfacing — anything that assumes the user is okay. (This connects to `feedback/microcopy.md` and empty/error states: tone that delights the happy user can gut the distressed one.)
- **The worst-case user (harm _by_ them).** The abuse-case actor above, given full design weight: assume the most hostile capable person will use every feature, and design so they can't weaponize it against others. A "share location with family" feature must assume a controlling ex; a "find people you know" feature must assume a stalker; an open text field must assume harassment. The question is "what's the worst this enables?" — and the safe-by-default, friction, blocking/reporting, and rate-limiting answers follow.

The unifying discipline: **the happy-path user is the easy case; the stressed user and the hostile user are where design earns its keep.** A feature that only works for the cooperative, calm, well-meaning user is unfinished.

---

## Red-team your own design

The capstone practice: before shipping, deliberately adopt the adversary's seat and try to make your own feature cause harm — the design analogue of security red-teaming, increasingly formalized for AI systems as adversarially probing a model for harmful, jailbroken, or unsafe outputs before release. You are looking for the harm your cooperative-user testing structurally cannot find, because friendly testing confirms the feature works rather than trying to break it.

```text
Red-team pass — for each feature, actively attempt:

  1. MISUSE IT     — how does a careless/confused user cause harm? (wrong audience,
                     irreversible click, misread state) → fix with default/friction/undo
  2. ABUSE IT      — how does a hostile user weaponize it against others or the system?
                     (harass, stalk, defraud, scrape, jailbreak) → fix with constraint/limit/report
  3. STRESS IT     — how does it land on someone in crisis? (tone, timing, resurfacing)
                     → fix the assumption that the user is okay
  4. SCALE IT      — what breaks when it's used a million times, or automated by a bot?
                     (rate-limit, throttle, detect)
  5. WORST OUTPUT  — for AI: what's the most harmful thing it could be coaxed to produce?
                     → guardrail, refuse, escalate (labeled: AI red-teaming is evolving practice)

  Output: the harms you found + the design change that closes each, BEFORE launch.
```

The tell of a team that red-teamed: they can name the harms their feature enables and show the defense for each. The tell of one that didn't: every harm is a surprise discovered in production, and the response is a policy or a patch rather than a design that never permitted it.

---

## Anti-patterns

- **Happy-path-only design.** The feature is designed and tested only for the cooperative, calm, well-meaning user; misuse, abuse, and stress are deferred as "edge cases" until an incident forces them.
- **Unsafe default.** Public, discoverable, over-permissioned, or hard-delete by default — the user is exposed or one misclick from permanent loss before they notice, and "they could've changed it" is the after-the-fact excuse.
- **Confirmation theater.** "Are you sure?" on everything, reversible or not — trains click-through and adds zero real safety, while the genuinely dangerous action gets the same weak gate as a trivial one.
- **Friction in the wrong place.** Heavy gates on safe, reversible actions (annoying) and a light touch on irreversible, high-stakes ones (dangerous) — friction uncoupled from harm.
- **Cheerful-by-default tone.** Celebratory copy, upbeat empty states, "memories" resurfacing that assume the user is fine — wounding the stress-case user (Meyer & Wachter-Boettcher).
- **Ignoring the hostile user.** An open field, a lookup, a sharing feature with no block/report/rate-limit — built as if no one will weaponize it.
- **Harm as a policy problem.** Responding to enabled harm with terms-of-service language or after-the-fact moderation instead of a design that doesn't permit it in the first place.

---

## The scoring test: is the worst case designed for, or deferred?

1. **Abuse cases written.** Did the team write the misuse and abuse cases alongside the use cases — naming who is harmed by the careless and the hostile user — and design a defense for each, _before_ build?
2. **Safe by default.** Is a brand-new user who changes nothing in the safest state (private, least-privilege, reversible) — does reaching risk require a deliberate act, not an accident?
3. **Friction matched to harm.** Is real friction (type-to-confirm, re-auth, cooling-off) on the few irreversible high-stakes actions, and reversibility (undo) on the rest — rather than confirmation theater everywhere?
4. **Stress and worst-case users designed for.** Does the feature hold up when it meets someone in crisis (tone, resurfacing) and when used by the most hostile capable person (block/report/rate-limit) — or only the happy path?
5. **Red-teamed before launch.** Can the team name the harms their feature enables and show the design defense for each — or are harms discovered in production and patched with policy?

A product passes when the worst plausible user — careless, hostile, or in crisis — was a primary case in the design, the safe state is the default, real friction guards the irreversible, and the team broke their own feature before shipping it. It fails when design optimized only for the cooperative user, harm is a surprise found in production, and the response is a policy rather than a design that never let it happen.

---

## One labeled caveat

The "stress cases" reframing, the quoted reasoning that calling them "edge cases" gives "permission to ignore them," and the Facebook "Year in Review" example are from Meyer & Wachter-Boettcher's _Design for Real Life_ (A Book Apart, 2016), cross-checked against the authors' published talks and A List Apart excerpts in this session rather than against the print pagination. Abuse cases and the attacker's-perspective rationale are OWASP's (Abuse Case Cheat Sheet); secure-by-default ("most secure settings possible," "start in a secure state") is OWASP's Developer Guide / Proactive Controls C5. The undo-over-confirm and error-prevention guidance is Nielsen's Heuristics 3 and 5 (NN/g). AI-specific red-teaming is a **fast-evolving area** — the principle (adversarially probe for harmful/jailbroken outputs before release) is well-established and durable, but specific methods, taxonomies, and tooling change quickly; treat the practice as sound and verify current technique before relying on a specific method. Risk × reversibility calibration is developed in `ai-ux/trust-control-steerability.md`; the undo/lifecycle surface in `auditability-and-control.md`; stress-case tone in `feedback/microcopy.md`.
