---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Harry Brignull. *Deceptive Patterns: Exposing the Tricks Tech Companies Use to Control You*. Testimonium Ltd, 2023. ISBN 9781739454302."
  - "Harry Brignull et al. \"Types of Deceptive Pattern.\" Deceptive Design (deceptive.design), the canonical taxonomy. https://www.deceptive.design/types"
  - "Federal Trade Commission. *Bringing Dark Patterns to Light* (Staff Report). September 2022. https://www.ftc.gov/reports/bringing-dark-patterns-light — full PDF: https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf"
  - "NN/g (Kate Moran & Tim Neusesser). \"Deceptive Patterns in UX: How to Recognize and Avoid Them.\" https://www.nngroup.com/articles/deceptive-patterns/"
  - "Colin M. Gray, Yubo Kou, Bryan Battles, Joseph Hoggatt, Austin L. Toombs. \"The Dark (Patterns) Side of UX Design.\" *Proceedings of the 2018 CHI Conference* (CHI '18). DOI 10.1145/3173574.3174108 — origin of the five-category taxonomy (nagging, obstruction, sneaking, interface interference, forced action)."
---

# Deceptive (Dark) Patterns: the line you do not cross

A deceptive pattern — Harry Brignull's 2010 coinage was "dark pattern," now retired in favour of "deceptive pattern" — is a user-interface choice that benefits the business by tricking, misdirecting, shaming, or obstructing a user into an action they would not otherwise have taken. NN/g's working definition: "a design pattern that prompts users to take an action that benefits the company employing the pattern by deceiving, misdirecting, shaming, or obstructing the user's ability to make another (less profitable) choice." This file is the inverse of the rest of the pattern library: it catalogues what you must **not** ship, and marks the line where a monetization or growth tactic stops being persuasion and becomes deception, fraud, or a regulatory violation. Everything here is a finding to flag in a critique, never a technique to apply.

> The one-line test: persuasion gives the user accurate information and a free choice; deception removes, hides, distorts, shames, or obstructs the choice. If the design only works _because_ the user is confused, rushed, or didn't notice — it is a deceptive pattern.

## Persuasion vs. deception: the bright line

NN/g draws the boundary explicitly, and it is the line that matters most for a working team. Legitimate persuasive design uses real social proof, honest anchoring, genuine scarcity, and accurate framing — the user is nudged but informed, and could still freely choose otherwise. A deceptive pattern involves intentional dishonesty, fabrication, or the obscuring of information the user needs to decide fairly. The same surface feature sits on either side of the line depending on truth and freedom: a "Only 2 left in stock" banner is persuasion when it is true and deception (_fake scarcity_) when the number is invented. Scarcity, urgency, and social-proof messages are therefore not banned — _fabricated_ ones are.

A second, adjacent distinction (Brignull): a deceptive pattern is not the same as a merely _bad_ or _ugly_ pattern. Bad design fails the user by incompetence; a deceptive pattern succeeds for the business _by_ failing the user, on purpose. Intent and asymmetry of benefit are what make it dark.

## The two canonical taxonomies (use both)

There are two reference taxonomies a reviewer should hold at once, because regulators and designers cite different ones.

- **Brignull / deceptive.design (the pattern-level catalogue).** The canonical site currently enumerates these named patterns: _Comparison prevention_, _Confirmshaming_, _Disguised ads_, _Fake scarcity_, _Fake social proof_, _Fake urgency_, _Forced action_, _Hard to cancel_, _Hidden costs_, _Hidden subscription_, _Nagging_, _Obstruction_, _Preselection_, _Sneaking_, _Trick wording_, and _Visual interference_. (Older Brignull names you will still see in the wild map onto these: _roach motel_ → **hard to cancel**; _sneak into basket_ → a form of **sneaking**; _forced continuity_ → **hidden subscription**; _privacy zuckering_ → coercive privacy **forced action**; _misdirection_ → **visual interference / trick wording**; _bait and switch_ and _price comparison prevention_ persist by name.)
- **Gray et al. CHI '18 (the five strategy-level categories).** Academic and NN/g writing groups patterns into five higher-order strategies: **nagging**, **obstruction**, **sneaking**, **interface interference**, and **forced action**. This is the framing to use when classifying _why_ a pattern works, not just _what_ it is. (NN/g's article condenses to five overlapping buckets: obstruction; visual or wording tricks; nagging; emotionally manipulative design; sneaking/preselection.)

The two are compatible: the five strategies are the _mechanisms_; the named patterns are the _instances_. A reviewer cites the named pattern and the strategy it belongs to.

## The patterns named in scope, defined

These six were called out for this library; each is given with its definition, its strategy category, and the tell that distinguishes it from honest design. Definitions track deceptive.design wording.

| Pattern | Strategy (Gray et al.) | Definition | The tell |
| --- | --- | --- | --- |
| **Forced action** | Forced action | The user wants to do something, but is required to do something else undesirable in return (e.g. create an account, accept marketing, hand over data to use a feature). | A wanted action is gated behind an unrelated, business-favourable one. |
| **Confirmshaming** | Interface interference (emotional) | The user is emotionally manipulated — through shame, guilt, or fear — into doing something they would not otherwise have done. | The decline option is worded to demean the user ("No thanks, I don't want to save money"). |
| **Roach motel** (now **hard to cancel**) | Obstruction | The user finds it easy to sign up or subscribe, but very hard to cancel — an easy way in, an obstructed way out. | Asymmetric effort: one-click in, phone-call/mail/maze out. |
| **Sneak into basket** (a form of **sneaking**) | Sneaking | The user is drawn into a transaction on false pretences because pertinent information (an added item, an added cost) is hidden or delayed. | Something the user didn't choose appears in the cart or total. |
| **Nagging** | Nagging | The user tries to do something but is persistently interrupted by repeated requests to do something else not in their interest, until they relent. | The same request reappears after the user already declined it. |
| **Obstruction** | Obstruction | The user faces barriers or hurdles that make a task or choice artificially hard, raising interaction cost to steer them away from a less-profitable option. | The cheaper / privacy-protective / cancel path is deliberately harder than the profitable one. |

## The legal and regulatory line (why this is not just an ethics note)

Deceptive patterns are increasingly _illegal_, not merely distasteful — which is why this file lives in the monetization branch and not a style guide.

- **US — FTC.** The FTC's September 2022 staff report _Bringing Dark Patterns to Light_ (approved 5-0) treats dark patterns as practices that "obscure, subvert, or impair consumer autonomy, decision-making, or choice," and as **unfair or deceptive acts under Section 5 of the FTC Act**. It singles out disguised ads, hard-to-cancel subscriptions, buried junk fees / hidden costs, and tricking users into sharing data. The FTC's "Click to Cancel" rulemaking and its negative-option / ROSCA enforcement directly target _hard to cancel_ and _hidden subscription_. (Note: specific FTC rules and their effective dates shift with litigation; treat the _report's principles_ as the durable citation and verify the current rule text before relying on a deadline. Labeled time-sensitive.)
- **EU.** The **Digital Services Act (Regulation (EU) 2022/2065), Article 25** prohibits online-platform interfaces that deceive or manipulate users or otherwise distort their ability to make free, informed decisions. The **GDPR** (valid, freely-given consent) and the consumer-protection / UCPD regime catch _preselection_, coerced consent (_forced action_), and dark-pattern cookie banners. The EDPB has published dark-pattern guidance for social-media interfaces.
- **US state law.** California's CPRA/CCPA explicitly states that consent obtained through dark patterns is **not** valid consent; Colorado and Connecticut privacy laws follow suit.

The practical upshot for a reviewer: a _hard to cancel_ flow, a _preselected_ consent box, or a _hidden subscription_ is not a "growth experiment" to A/B test — it is potential liability, and should be flagged as a defect with the regulatory hook named.

## Using this file in a critique

When this library reviews a monetization, onboarding, consent, or cancellation flow, deceptive-pattern detection runs as a hard gate. The procedure:

```text
For each decision point where the business benefits from a particular user choice:

1. NAME the pattern.        Match the surface against the deceptive.design catalogue
                            (forced action, confirmshaming, hard-to-cancel, sneaking,
                            nagging, obstruction, fake scarcity/urgency/social-proof,
                            hidden costs/subscription, preselection, trick wording,
                            visual interference, disguised ads, comparison prevention).
2. CLASSIFY the strategy.   Map to Gray et al.: nagging / obstruction / sneaking /
                            interface interference / forced action.
3. APPLY the bright line.   Does it work because the user is INFORMED and FREE
                            (persuasion) — or because they are confused, rushed,
                            shamed, or obstructed (deception)? Is any claimed
                            scarcity / urgency / social proof actually TRUE?
4. CHECK asymmetry.         Is the effort to choose the business-favoured option far
                            lower than the effort to choose otherwise? (in-vs-out,
                            accept-vs-decline, keep-vs-cancel)
5. NAME the legal hook.     FTC Section 5 / Click-to-Cancel / ROSCA; EU DSA Art. 25;
                            GDPR consent; CCPA "dark patterns ≠ consent."
6. PRESCRIBE the honest form. Every deceptive pattern has a non-deceptive counterpart
                            (symmetric cancel, neutral decline copy, true counts,
                            opt-in defaults, all costs shown before commitment).
```

The deliverable is a finding, not a tactic: the pattern named, the strategy classified, the line crossed, the law implicated, and the honest design that replaces it.
