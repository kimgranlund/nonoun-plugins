---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Raja Parasuraman, Thomas B. Sheridan & Christopher D. Wickens, “A Model for Types and Levels of Human Interaction with Automation,” IEEE Transactions on Systems, Man, and Cybernetics—Part A, 30(3): 286–297 (2000)."
  - "Thomas B. Sheridan & William L. Verplank, *Human and Computer Control of Undersea Teleoperators* (MIT Man-Machine Systems Lab, 1978) — the original ten levels of automation."
  - "Eric Horvitz, “Principles of Mixed-Initiative User Interfaces,” Proceedings of CHI ’99 (ACM, 1999) — expected-value of acting vs. asking; cost of intervention."
  - "NN/g — “The Role of Automation in UX” / human-in-the-loop guidance (nngroup.com/articles)."
---

# Automation Boundaries

This is the working method for the most consequential line in a modern product: where the system **acts on its own** versus where it **stops and asks the human.** As products absorb prediction, generation, and agency, this boundary stops being an edge case and becomes the core of the interaction model. Drawn well, the user feels amplified — the system handles the obvious and reserves judgment for them. Drawn badly, the product is either a nag that asks about everything (so the human becomes a rubber stamp) or a cowboy that acts on everything (so the human discovers consequences after the fact). This file gives the spectrum, the criteria for placing the line, and how to keep it trustworthy.

## The spectrum: act, suggest, ask (and the LoA ladder behind it)

The clean product framing is a three-point spectrum, and it's a compression of the human-factors **Levels of Automation (LoA)** literature — Sheridan & Verplank's ten-level ladder (1978) and the four-stage model of Parasuraman, Sheridan & Wickens (2000).

| Mode | What the system does | The human's role | LoA mapping (Sheridan/Verplank) |
| --- | --- | --- | --- |
| **Ask** | Presents options or asks permission; takes no action until told | Decides everything; the system advises | Low — computer offers alternatives, human selects |
| **Suggest** | Proposes a default action and acts only on approval (or after a vetoable delay) | Approves, edits, or vetoes; the default does the work | Mid — computer suggests one action / executes if approved / executes-unless-vetoed |
| **Act** | Performs the action autonomously, then reports (or doesn't) | Oversees after the fact; intervenes by exception | High — computer acts, then informs the human, possibly only if asked |

The 2000 model adds a crucial refinement: automation isn't one dial but applies independently across **four stages** — (1) information acquisition (what it gathers), (2) information analysis (how it interprets), (3) decision/action selection (what it chooses), (4) action implementation (whether it executes). **A product can automate early stages aggressively and the last stage timidly** — e.g., let the system gather and analyze and even _recommend_ at high autonomy, while keeping _execution_ in "suggest" so a human approves the irreversible step. Most well-designed AI features live exactly there: high automation on perception and proposal, a deliberate human gate on consequential action. The single biggest design error is automating all four stages to the same high level because the first three were easy.

## Placing the line: the act/suggest/ask decision criteria

Where each capability sits on the spectrum is decided by four variables. Score the action on each; the worse it scores, the further toward "ask" it belongs.

- **Reversibility.** Can the human undo it cheaply? Reversible → bias to **act** (do it, offer undo). Irreversible → bias to **ask**, or at least **suggest** with a real veto window. Reversibility is the master variable: it converts a scary autonomous action into a safe one.
- **Confidence.** How sure is the system it's right _here_? High and calibrated → act/suggest. Low or uncertain → ask, or escalate. The system should know what it doesn't know and route those cases to the human (Horvitz's mixed-initiative principle: don't act when uncertain if the cost of a wrong act is high).
- **Cost of being wrong (blast radius).** Trivial slip vs. data loss, money moved, message sent to the wrong person, public exposure. Large blast radius pulls hard toward **ask**, _regardless_ of confidence — a 99%-confident wrong wire transfer is still a disaster.
- **Cost of interrupting.** Asking has a price too: it breaks flow, and over-asking trains the rubber-stamp reflex (the automation analogue of confirmation-dialog habituation). Frequent, low-stakes, reversible actions should _not_ ask — the interruption cost exceeds the error cost.

Horvitz's _Principles of Mixed-Initiative User Interfaces_ formalizes this as an expected-value trade: **act autonomously only when the expected value of acting exceeds the expected value of asking** — accounting for the probability the action is right, the cost if it's wrong, and the cost of the interruption itself. The practical synthesis: **act when reversible and confident and low-blast-radius; ask when irreversible or uncertain or high-blast-radius; suggest in between, with the default carrying the load and a frictionless override.**

## Reversible automation: the cheat code

The reason reversibility is the master variable: it lets you move a capability _up_ the autonomy ladder without raising the risk, because the human's veto moves _after_ the action instead of before it.

- **Prefer "act + undo" over "ask first" for reversible operations.** Auto-categorize, auto-tag, auto-arrange, auto-format — then make the result trivially reversible and reviewable. The user gets the speed of automation and keeps the last word. (This is the undo-over-confirmation argument from `undo-and-recovery.md`, applied to the machine.)
- **Use a vetoable delay for the middle ground.** "Sending in 5s · Undo" (the Gmail Undo-Send pattern) is "act" with a built-in ask-window — autonomy by default, human override on tap. It's the highest-throughput safe design for actions that are _mostly_ fine.
- **Stage, don't commit, when stakes climb.** For higher-blast-radius automation, have the system prepare the action (draft the email, stage the changes, propose the merge) and require a human commit. Preparation is cheap to discard; commitment isn't.
- **Make autonomous actions legible after the fact.** An activity log / "what the system did" feed turns silent automation into reviewable automation — the human can audit and reverse, which is what makes ceding the action tolerable.

## Trust calibration: the real goal

The objective isn't maximum trust or minimum trust; it's **calibrated** trust — the human's reliance matching the system's actual reliability. The two failure modes are named in the literature:

- **Over-trust (misuse / automation complacency)** — the human stops checking and rubber-stamps, so the system's errors pass straight through. Caused by an interface that hides uncertainty, asks so often the human tunes out, or presents guesses with unearned confidence.
- **Under-trust (disuse)** — the human ignores or disables a system that's actually good, losing its value. Caused by early visible failures, opaque behavior, or no way to correct it.

Design moves that calibrate:

- **Expose confidence honestly.** Show when the system is unsure; don't render a 51% guess identically to a 99% one. Let uncertainty be a first-class output, and route low-confidence cases to "ask."
- **Make reasoning inspectable** (why did it do/suggest this?) so the human can decide whether to trust _this_ instance, not just the system in general.
- **Let the human correct, and learn from it visibly** — a system that absorbs a correction and stops repeating the mistake earns trust; one that re-offers the rejected suggestion erodes it.
- **Fail toward the human.** When confidence drops, degrade to "suggest" or "ask" rather than acting anyway — the boundary should move conservatively under uncertainty.

## Designing the "are you sure the machine should do this" line

A practical checklist for every capability where the system might act:

1. **Score it** on the four variables (reversibility, confidence, blast radius, interruption cost). The score, not the demo's wow-factor, sets the mode.
2. **Default to the most autonomy reversibility allows** — and no more. If it's reversible, lean to act-with-undo; if not, the burden of proof is on automating it at all.
3. **Decouple the stages.** Automate acquisition/analysis/recommendation freely; gate _execution_ by stakes. Don't let an easy-to-automate perception step drag the consequential action up with it.
4. **Give a frictionless override and a visible trail.** Every autonomous or defaulted action needs an obvious way to stop/undo it and a record of what happened.
5. **Re-evaluate as confidence data arrives.** The line isn't set once — tighten it where the system proves reliable, pull it back where errors show up. Treat the boundary as tunable, not fixed.

## Accessibility & inclusion

- **Autonomous changes must be announced**, not silent — a live region ("3 emails auto-archived · Undo") so non-visual users aren't surprised by state they didn't cause (WCAG 4.1.3, Status Messages).
- **Override and undo of automation must be keyboard-operable** and not buried — the human's veto can't depend on a pointer gesture (WCAG 2.1.1).
- **Don't impose timed auto-actions a user can't keep up with.** A vetoable-delay window must be long enough, and adjustable/defeatable, for users who need more time (WCAG 2.2.1).
- **Be cautious automating on inferred attributes** — predictions about a person can encode bias; expose the inference and the correction path, and never let an irreversible automated decision about a user run without a human-reachable appeal.

## Good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Mode fit** | Asks about trivial reversible things; acts on irreversible ones | Mode set by reversibility/confidence/blast-radius/interruption score |
| **Stage decoupling** | All four stages automated to the same high level | High autonomy on perception/analysis; human gate on consequential execution |
| **Reversibility leverage** | "Ask first" everywhere, or autonomous + no undo | Reversible → act + undo; irreversible → stage/ask; vetoable delay in between |
| **Uncertainty handling** | 51% guess shown like a 99% one; acts when unsure | Confidence exposed; low-confidence cases degrade to suggest/ask |
| **Trust calibration** | Over-asking breeds rubber-stamping, or opacity breeds disuse | Inspectable reasoning, learnable corrections, fail-toward-human |
| **Legibility** | Silent autonomous actions the human can't see or audit | Activity trail + announced changes + frictionless override |
| **Boundary maintenance** | Line set once at launch by demo appeal | Boundary tuned as reliability data arrives; conservative under uncertainty |
| **A11y / fairness** | Silent timed auto-actions; biased inference with no appeal | Announced, keyboard-overridable, adjustable timing; inference + appeal path |
