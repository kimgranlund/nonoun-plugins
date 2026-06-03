---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Victor Yocco, 'Designing For Agentic AI: Practical UX Patterns For Control, Consent, And Accountability', Smashing Magazine (smashingmagazine.com/2026/02/designing-agentic-ai-practical-ux-patterns), 2026-02-11"
  - "Erik Schluntz & Barry Zhang, 'Building Effective Agents', Anthropic (anthropic.com/research/building-effective-agents), 2024-12-19"
  - "Saranya Gunasekaran, 'Designing for Autonomy: UX Principles for Agentic AI', UXmatters (uxmatters.com/mt/archives/2025/12/designing-for-autonomy-ux-principles-for-agentic-ai.php), 2025-12-15"
  - "'Exploring automation bias in human–AI collaboration: a review and implications for explainable AI', AI & SOCIETY, Springer (link.springer.com/article/10.1007/s00146-025-02422-7), 2025"
---

# Human-in-the-Loop

When an AI takes a consequential action — sends the email, moves the money, deletes the records, publishes the post — the interface needs a human gate. This reference covers the UX of that gate: review / approve / override / refine surfaces, the preview-vs-commit pattern for consequential actions, reversibility and undo, and the failure mode that quietly defeats all of them — **approval fatigue**, where a human asked to approve everything stops actually reviewing anything. Human-in-the-loop is the safety net under the trust and agentic references; this file is about building a net that actually catches, rather than one the user has learned to fall straight through.

> The framing to hold onto: a human-in-the-loop control is only worth its interruption cost if the human is _actually deciding_. A gate the user rubber-stamps is worse than no gate — it adds friction _and_ provides false assurance that something was checked. The entire design problem is keeping the human cognitively engaged at the gate, which means gating less and gating better.

This is an **emerging area** for the UX patterns specifically; the named patterns below (Yocco, Gunasekaran) are recent named-author conventions, while the approval-fatigue / automation-bias phenomenon they must defend against is grounded in older, peer-reviewed human-factors research, cited as such.

---

## When to put a human in the loop

Not every step needs a gate — gating everything is the disease, not the cure. The trigger is **consequence × reversibility** (the same calculus as the trust reference): interpose a human when an action is hard to undo, externally visible, or high-stakes, and let reversible, low-stakes actions run. Anthropic's "Building Effective Agents" frames it as building checkpoints where agents pause "for human feedback at checkpoints or when encountering blockers," with human review "crucial" before consequential operations. The corollary matters as much as the rule: **if an action is cheaply reversible, prefer letting it run with an undo over gating it with an approval.** Undo costs the user nothing until they need it; an approval costs them attention every single time.

| Action profile | Gate it? | Right surface |
| --- | --- | --- |
| Reversible, low-stakes (draft, read, suggest) | No | Let it run; offer undo |
| Reversible, medium-stakes (edit user's doc) | Usually no | Reviewable change + undo |
| Hard to reverse, visible to others (send, publish) | Yes | Preview → explicit commit |
| Irreversible, high-stakes (delete, pay, external commit) | Yes | Preview → commit, possibly a second confirm |

---

## Preview vs commit for consequential actions

The core pattern: for any consequential action, **show what will happen before it happens, and require an explicit, separate act to commit.** Yocco's "Intent Preview (Plan Summary)" names it — surface "sequential steps, clear outcomes in plain language," with the preview "immediately digestible… avoiding technical jargon," and offer real choices: "Proceed," "Edit Plan," or "Handle it Myself." The preview is not a confirmation dialog; it is a faithful, editable picture of the consequence, and the commit is a deliberate second step.

```text
   PREVIEW (what will happen)                 COMMIT (make it happen)
   ┌────────────────────────────────┐
   │ Will send to: 3 external clients│
   │ Subject: "Q3 results"           │         ┌──────────────┐
   │ Attaches: revenue.xlsx          │   ───►   │ [ Send now ] │  ← explicit,
   │                                 │         └──────────────┘    separate act
   │ [ Edit ]  [ Do it myself ]      │
   └────────────────────────────────┘
   ↑ digestible, faithful, editable           ↑ not the same click as "preview"
```

The discipline that makes a preview real: it must be **faithful** (it shows the actual consequence, not a sanitized summary), **editable** (the user can change the plan, not just accept or cancel), and **separated from commit** (reviewing and executing are distinct acts, so the user cannot commit by reflex while skimming).

---

## Review, approve, override, refine

Four distinct human moves; a mature human-in-the-loop UI supports all four, not just binary approve/reject:

| Move | What the human does | Why binary approve/reject isn't enough |
| --- | --- | --- |
| **Review** | Inspect what the AI proposes, and _why_ | Yocco's "Explainable Rationale" — "Because you said X, I did Y" — gives the human something to evaluate, not just a yes/no |
| **Approve** | Let the proposed action proceed | The baseline — but on its own it trains rubber-stamping |
| **Override** | Replace or correct what the AI proposed | Keeps the human in authority; Gunasekaran: intervention "must be visible, not hidden" |
| **Refine** | Edit the plan and have the AI re-propose | Turns a rejection into a correction — the human steers instead of just blocking |

The presence of **refine** is the tell of a good design: a UI where the only options are "approve" or "reject" forces the human to either accept a flawed plan or throw it away, whereas "edit and re-propose" keeps the collaboration moving. Gunasekaran's framing — suggestions should "invite judgment, not replace it" — is exactly this: the human is a collaborator who shapes the action, not a button that gates it.

---

## Reversibility and undo

Reversibility is the safety net _under_ the safety net: when an approval is wrong (and with approval fatigue, some will be), undo limits the blast radius. Yocco's "Action Audit & Undo" pattern pairs a "persistent chronological log of all agent-initiated actions" with "time-limited reversibility" — and, crucially, "clear communication about irreversible points." He calls it "the ultimate safety net, assuring the user that even if the agent misunderstands, consequences are not catastrophic." Gunasekaran defines the goal as "the ability for users to undo, retract, or reinterpret actions before consequences become permanent."

The design move with the highest leverage: **convert irreversible actions into reversible ones wherever possible** — a sent email becomes an undo-send window, a deletion becomes a recoverable trash, a publish becomes a staged draft. Every action you can make reversible is an action you can stop gating, which directly relieves the approval-fatigue pressure below. Where an action is genuinely irreversible, the UI must say so plainly at the commit point, because that is precisely where a fatigued user most needs to be slowed down.

---

## The approval-fatigue anti-pattern

This is the failure mode that quietly defeats human-in-the-loop, and it deserves its own section because it is so easy to design straight into. **Gate a human on too many decisions and they stop deciding** — they approve on autopilot, and the gate becomes a rubber stamp that adds friction while providing false assurance.

The phenomenon is well-documented in human-factors research under **automation bias** — the tendency to over-rely on automated recommendations. A peer-reviewed review in _AI & SOCIETY_ (Springer, 2025) surveys this in human–AI collaboration, and the broader literature names the cost concretely: cognitive fatigue from reviewing long runs of similar decisions "numbs scrutiny," and reviewers exhibit "rubber-stamping after long runs of similar cases." [Single-finding, widely-replicated:] one study of clinicians using intentionally biased AI assistance found diagnostic accuracy _fell_ from 73% to 61.7% — over-trust in the AI made the human-checked output worse than the human alone. The mechanism that defeats your safety net is not that humans are lazy; it is that high-volume, low-variation approval is a task humans are cognitively unsuited to perform attentively.

A grounded counter-design from the same literature: in some AI-assisted radiology workflows, "clinicians are encouraged to make an initial judgment _before_ receiving the system's recommendation," and this delayed disclosure reduces automation bias. The general principle — make the human commit to a judgment before showing the AI's answer — is one of the few empirically-supported debiasing moves, though it is drawn from high-stakes clinical settings and should be applied thoughtfully, not universally.

| Lever | Good — keeps the human deciding | Bad — trains rubber-stamping |
| --- | --- | --- |
| **Volume** | Gate only consequential actions; batch or auto-approve the routine | Approve every step, including trivial reversible ones |
| **Variation** | Surface what's _unusual_ about this action | Identical-looking approval after identical-looking approval |
| **Salience** | Make the consequence and the irreversibility vivid | A faithful preview the user has learned to skim |
| **Friction placement** | Heavier friction on irreversible actions only | Uniform friction that the user has habituated to |
| **Order (where apt)** | Ask for the human's judgment before showing the AI's | Show the AI's confident answer first, then ask to approve |

Yocco offers an oblique but useful health metric: an acceptance rate so high it implies _no_ edits ever ("> 85% accepted without edits" treated as the watch-line) can signal the human has stopped engaging — if nobody ever edits or rejects, the gate is probably ceremonial. [This specific threshold is one source's heuristic, not a validated benchmark — read it as "watch for suspiciously perfect approval rates," not a hard number.]

---

## Anti-patterns

- **Gate everything.** A human approval on every step, including cheaply-reversible ones — the direct cause of approval fatigue. Gate on consequence, not on principle.
- **Approve-or-reject only.** No "refine / edit and re-propose," forcing the human to accept a flawed plan or discard it. Removes the collaboration.
- **The skimmable preview.** A preview faithful in theory but so routine, jargon-heavy, or uniform that the user has stopped reading it before clicking commit.
- **Commit-by-reflex.** Review and execute collapsed into one click, so a skimming user commits without a deliberate second act.
- **Irreversible-by-silence.** An action with no undo and no warning that it is final — the worst place for a fatigued user to be on autopilot.
- **Ceremonial oversight.** A human-in-the-loop gate kept for the _appearance_ of control (or for liability) while everyone knows it is rubber-stamped — friction plus false assurance, the worst of both.

---

## The scoring test: does the gate actually catch?

1. **Gated for the right reasons.** Are human gates reserved for consequential, hard-to-reverse actions — or applied uniformly, training the user to rubber-stamp? Are reversible actions given undo instead of approvals?
2. **Preview is faithful and editable.** Does the preview show the actual consequence in plain language, let the user edit the plan, and require a _separate_ act to commit — or is it a skimmable dialog one click from execution?
3. **Four moves, not two.** Can the user review the rationale, approve, override, _and_ refine — or only approve/reject?
4. **Reversibility as the floor.** Are irreversible actions converted to reversible ones where possible (undo-send, trash, staged drafts), with plain warnings at the genuinely irreversible points?
5. **Engagement, not autopilot.** Does the design fight approval fatigue — gating less, surfacing what's unusual, varying salience, heavier friction only on the irreversible — or does it produce a long run of identical approvals the user has stopped reading?

A human-in-the-loop design passes when the human at the gate is genuinely deciding — reviewing faithfully, refining when needed, and stopped hard before anything irreversible. It fails the moment the gate becomes a reflex: friction the user has learned to click through, providing the false comfort that something was checked when nothing was.
