---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Anthropic, 'Our framework for developing safe and trustworthy agents' (anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents), 2025-08-04"
  - "Erik Schluntz & Barry Zhang, 'Building Effective Agents', Anthropic (anthropic.com/research/building-effective-agents), 2024-12-19"
  - "Saranya Gunasekaran, 'Designing for Autonomy: UX Principles for Agentic AI', UXmatters (uxmatters.com/mt/archives/2025/12/designing-for-autonomy-ux-principles-for-agentic-ai.php), 2025-12-15"
  - "Victor Yocco, 'Designing For Agentic AI: Practical UX Patterns For Control, Consent, And Accountability', Smashing Magazine (smashingmagazine.com/2026/02/designing-agentic-ai-practical-ux-patterns), 2026-02-11"
---

# Trust, Control & Steerability

Every AI product makes an implicit bet about how much it does on the user's behalf and how much the user directs. Get that bet wrong and the product fails in one of two symmetric ways: too much autonomy and it takes actions the user did not want and cannot undo; too little and it is a slow, nagging assistant that asks permission for everything. This reference is about calibrating that bet — the trust/autonomy spectrum, the controls that give users steerability, and the central principle that **autonomy should be matched to the risk and reversibility of the action**, not set once and applied everywhere. It is the conceptual spine under the agentic-workflows reference: that one covers the mechanics of running an agent; this one covers how much rope to give it and why.

> The framing to hold onto, from Anthropic's agent framework: "humans should retain control over how their goals are pursued, particularly before high-stakes decisions." Control is not a single toggle. It is a graded thing — earned, adjustable, and proportional to what is at stake.

The trust/autonomy spectrum is an **emerging area** with a maturing literature. Anthropic's framework and engineering writing are durable, named sources for the principles; the UX patterns that operationalize them (Gunasekaran, Yocco) are recent named-author posts converging on a shared model. Where a specific traffic-light scheme or autonomy taxonomy is one source's framing rather than an industry standard, it is labeled below.

---

## The trust / autonomy spectrum

Trust in an AI product is not binary and not granted up front — it is built, and the interface should let it move. Yocco states it plainly: "trust is not a binary switch; it's a spectrum," and his Autonomy Dial lets users set independence per task type across `Observe & Suggest → Plan & Propose → Act with Confirmation → Act Autonomously`. Gunasekaran frames autonomy as a continuum "between complete human control and full AI autonomy," with safeguards "distributed across this range rather than clustered at either extreme."

The design consequence: **build for movement along the spectrum, not a position on it.** A new user starts low (the AI suggests, the human acts); as the AI demonstrates reliability on a given task, the user dials autonomy up. A product that hard-codes one position serves neither the cautious nor the confident — and gives the user no way to express growing or collapsing trust.

```text
HUMAN CONTROL ◄─────────────────────────────────────────► AI AUTONOMY
  AI suggests,        AI drafts a plan,     AI acts but        AI acts and
  human does          human approves        confirms first     reports after
  ───────────         ─────────────         ────────────       ─────────────
  ◄── trust is earned moving rightward; risk pulls it back leftward ──►
```

---

## Matching autonomy to risk and reversibility

This is the load-bearing principle. The right autonomy level for an action is a function of **how bad it is if it's wrong** (risk) and **how easily it can be undone** (reversibility) — not a global product setting. Anthropic's engineering guidance states the goal directly: "match the level of oversight to the task's risk," where "low-risk tasks can run autonomously, while high-stakes actions should require manual approval," and agents should "prefer reversible actions over irreversible ones" with "explicit human-confirmation steps for high-stakes operations." Anthropic's "Building Effective Agents" reinforces the checkpoint idea — pause "for human feedback at checkpoints or when encountering blockers" — and Claude Code's read-only default (analyze freely, ask before modifying) is this principle shipped: low-risk reads run autonomously, state-changing writes require approval.

A reversible, low-stakes action (drafting text, running a read-only query, suggesting an edit) can run autonomously. An irreversible, high-stakes action (sending a message, moving money, deleting data, publishing) should drop to confirmation or human approval regardless of how much the user trusts the AI in general.

> **Note on the traffic-light framing.** A green/yellow/red action classification — green runs autonomously, yellow needs brief review, red is blocked — circulates widely in agent-governance writing as a useful mental model. It is a clarifying _convention_, not a quote from Anthropic's framework page (which lists five principles, not a three-color scheme); cite it as a community pattern, not as an Anthropic standard. The underlying idea (sort actions by stakes, gate the consequential ones) _is_ well-grounded in Anthropic's "match oversight to risk" guidance.

| Action profile | Reversible? | Stakes | Right default autonomy |
| --- | --- | --- | --- |
| Draft / suggest / preview | Yes | Low | Autonomous — let it run |
| Read-only query / analysis | Yes | Low | Autonomous |
| Edit user's own working document | Mostly (undo) | Medium | Act with confirmation, or reviewable change |
| Send / publish / notify others | No | High | Require explicit approval |
| Move money / delete data / external commit | No | High | Require explicit approval; consider a second confirm |

The same product should sit at different points on this table for different actions. That is the whole discipline: **autonomy per action, calibrated to risk × reversibility — not one global trust setting.**

---

## Steerability: the user's controls

Steerability is the user's ability to direct, correct, and constrain the AI — before, during, and after it acts. Gunasekaran's principles name the surfaces:

- **Clarity of intent (before).** The user articulates "direction, limitations, and exceptions; what success looks like; what failure looks like; and what must never happen." Steering starts with being able to set bounds, not just a goal.
- **Perceived control (during).** "A system that allows intervention even if the user rarely needs it feels trustworthy. A system that the user cannot interrupt, override, or question quickly becomes threatening." The mere _availability_ of an override builds trust, even when unused — and it "must be visible, not hidden."
- **Collaboration over replacement (throughout).** Suggestions should "invite judgment, not replace it." The AI proposes; the human disposes.

| Steering surface | What it gives the user | Anti-pattern it prevents |
| --- | --- | --- |
| **Constraints / guardrails up front** | Bound the space before the AI acts ("never email external contacts") | Discovering the AI's limits only after it crosses them |
| **Per-action autonomy dial** | Set how much the AI does on its own, per task | One global setting that fits no task well |
| **Visible interrupt / override** | Stop or redirect at any moment | A process the user can only watch, never steer |
| **Correction that sticks** | Teach the AI a preference and have it hold | Re-correcting the same thing every session |

---

## Transparency: showing what the AI is doing

A user cannot calibrate trust in a black box. Anthropic's framework makes transparency a named principle — "humans need visibility into agents' problem-solving processes," with the framework emphasizing "showing planned actions and allowing users to adjust workflows in real time." Gunasekaran calls this "transparency as affordance": users need to understand "why the AI has made a certain decision, what information influenced it, what assumptions it made, how confident the system is."

Transparency is what makes the spectrum usable: it is the feedback signal a user reads to decide whether to dial autonomy up or down. Without it, trust is a guess. (The uncertainty-citations reference covers the honest-confidence and sources side of this; here the point is structural — visibility of intent and action is a _precondition_ for graded control.)

---

## Anti-patterns

- **The single trust toggle.** "AI: on/off." No way to grant more autonomy for safe actions and less for dangerous ones — the whole calibration collapsed into one switch.
- **Autonomy decoupled from reversibility.** Letting the AI take irreversible, high-stakes actions (send, publish, delete, pay) at the same autonomy level as reversible drafts.
- **Hidden override.** A stop/redirect control buried in a menu — present in theory, useless at the moment of need. Gunasekaran: it "must be visible, not hidden."
- **Trust that can't grow (or shrink).** A fixed autonomy level the user cannot move as the AI proves (or loses) reliability on a task.
- **Opaque action.** The AI acting with no visibility into what it did or why, so the user has no basis to recalibrate trust.
- **Borrowed authority as fact.** Presenting a community framing (e.g. a specific traffic-light scheme) as an official vendor standard. Cite conventions as conventions.

---

## The scoring test: is autonomy calibrated, or one-size-fits-all?

1. **Spectrum, not switch.** Can the user grant graded autonomy (suggest → confirm → autonomous), and does that setting actually move — or is it one global on/off?
2. **Risk × reversibility.** Do irreversible, high-stakes actions (send, publish, delete, pay) require more human involvement than reversible drafts — or does everything run at one level?
3. **Steerable.** Can the user set constraints up front, interrupt/override during, and have corrections persist? Is the override _visible_?
4. **Transparent enough to calibrate.** Can the user see what the AI is doing and why, well enough to decide whether to trust it more or less next time?
5. **Honest sourcing of its own claims.** Where the product (or its docs) borrow a governance framing, is it labeled as a convention rather than dressed as a vendor standard?

A product passes when a user can lend the AI exactly as much rope as each action's risk warrants, watch what it does with that rope, and take it back instantly. It fails when trust is a single switch and the AI's autonomy bears no relation to whether its actions can be undone.
