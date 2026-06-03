---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Marcia W. Blenko, Michael C. Mankins & Paul Rogers, *Decide & Deliver* (Bain & Company / Harvard Business Review Press, 2010) — the RAPID® decision-rights model."
  - "Paul Rogers & Marcia W. Blenko, “Who Has the D? How Clear Decision Roles Enhance Organizational Performance,” Harvard Business Review (January 2006)."
  - "Atlassian Team Playbook — “DACI: A Decision-Making Framework” (atlassian.com/team-playbook/plays/daci); DACI originated at Intuit."
  - "Colin Bryar & Bill Carr, *Working Backwards: Insights, Stories, and Secrets from Inside Amazon* (St. Martin's Press, 2021) — single-threaded leadership and separable teams."
---

# Ownership & Decision Rights

Most product dysfunction that looks like a strategy problem is actually a **decision-rights** problem: nobody can say who decides, so decisions get made three times, unmade in the hallway, and escalated to whoever is most senior in the room. Clarifying who decides is cheaper and higher-leverage than almost any process change. This file is the working method for assigning decision rights with RACI, DACI, and Bain's RAPID, and for the structural move that prevents the whole class of problem — single-threaded ownership.

> **Rogers & Blenko (HBR, 2006):** the diagnostic question is literally _"Who has the D?"_ — who holds the **D**ecide right. In high-performing orgs, for any given decision, everyone can name the single person who decides. In dysfunctional ones, the answer is "it depends," and that ambiguity is the tax.

## RACI: the baseline, and its one fatal misuse

RACI assigns four roles per task: **R**esponsible (does the work), **A**ccountable (owns the outcome), **C**onsulted (two-way input before), **I**nformed (told after). It is the lingua franca of operating models, and its single most important rule is the one teams break constantly.

- **Exactly one Accountable per decision — always.** "There must be only one accountable stakeholder." When two people are Accountable, "responsibility becomes fragmented… executors don't know whose direction to follow." Two A's is not shared ownership; it is no ownership, dressed as collaboration. If you cannot name one A, you have not finished designing the decision.
- **Watch the inflation of C and R.** "Too many C's" yields conflicting opinions and gridlock; "too many R's" leaves tasks neglected because everyone assumes someone else has it. A row with five Consulted is a meeting, not a decision.
- **RACI's blind spot: it maps tasks, not the decision itself.** RACI tells you who's accountable for _executing_, but it blurs who chooses _which path_. For genuine decisions (not deliverables), reach for a model built around the choice — DACI or RAPID.

## DACI: built for the decision, not the task

DACI (originated at Intuit, popularized by Atlassian) reframes the four roles around making a _choice_: **D**river, **A**pprover, **C**ontributors, **I**nformed. It is the workhorse for product decisions — picking an option, not assigning a chore.

- **Driver** corrals stakeholders, frames the options, gathers the inputs, and drives to a decision **by a date.** The Driver does not decide; they make the decision _happen_.
- **Approver** — "just one person, not several" — has the final say across the options the Driver presents. This is the D in "Who has the D?", named explicitly. One Approver is the whole point; two reintroduces the ambiguity DACI exists to kill.
- **Contributors** do the legwork: frame proposals, weigh options, supply expertise. They have voice, not vote.
- **Informed** are affected by the outcome and told once it's made — "no vote, no voice." Putting someone in Informed is a deliberate, defensible "you don't get a say here," which is exactly what keeps the decision small enough to move.

The DACI discipline that matters most: **separate Driver from Approver.** When the same person frames the options _and_ picks among them, the framing quietly preordains the choice. Splitting them forces honest options on the table.

## RAPID: for cross-functional, high-stakes decisions (Bain)

Bain's RAPID® is the heaviest model, built for consequential decisions that cross many functions. The letters are roles, **not a sequence** (the order is a memorable acronym, not a workflow): **R**ecommend, **A**gree, **P**erform, **I**nput, **D**ecide.

| Role | Who holds it | The job |
| --- | --- | --- |
| **Recommend (R)** | One person | Owns the proposal — aligns with the Decider on context/criteria, gathers Input, drives a recommendation to a decision |
| **Agree (A)** | Assigned _sparingly_ | Holds a veto: must agree the recommendation is feasible/compliant before it advances (e.g., legal, security). Their concerns must be reflected |
| **Perform (P)** | Those who'll execute | Understands intent and is on point to deliver once decided |
| **Input (I)** | Subject experts | Supplies expertise that shapes the recommendation — consulted, not deciding |
| **Decide (D)** | One person | Has the broad view of trade-offs, primary accountability for the outcome; sits as close to implementation as feasible |

RAPID's distinctive moves: it separates **Recommend** from **Decide** (the same split DACI makes between Driver and Approver), and it isolates **Agree** as a true veto used rarely — pile on Agree roles and every decision needs unanimous consent, which is how large orgs grind to a halt. Use RAPID when a decision genuinely spans functions with veto-holding stakeholders; for an ordinary product call, DACI is lighter and sufficient. Don't run RAPID on a two-way-door decision (see `decision-records-adr.md`) — the ceremony costs more than the mistake.

## Single-threaded ownership: fix the structure, not just the chart

RACI/DACI/RAPID clarify decision rights _within_ a given setup. Amazon's single-threaded leadership (per Bryar & Carr's _Working Backwards_) attacks the problem one level up: structure the org so one person can own an initiative end-to-end without competing for shared resources.

- **The definition:** a single-threaded leader (STL) is "a single person, unencumbered by competing responsibilities, [who] owns a single major initiative and heads up a separable, largely autonomous team to deliver its goals." Single-threaded means **they work on nothing else.**
- **The insight that retired two-pizza teams:** Amazon found the predictor of success "was not whether [a team] was small but whether it had a leader with the appropriate skills, authority, and experience" and an undivided focus. Smallness was a proxy; **dedicated ownership** was the real variable.
- **Separable means decoupled like an API.** Teams are "almost as separable organizationally as APIs are for software" — clear, unambiguous ownership of specific functionality, able to "drive innovations with a minimum of reliance or impact upon others." Cross-team dependencies are the thing single-threading exists to eliminate, because dependencies are where ownership goes to die.
- **When to reach for it:** a critical initiative is stalling because the person notionally responsible is split across five priorities, or because shipping it requires constant negotiation with teams that have their own roadmaps. The fix is to give it an STL and a separable team — not another RACI workshop on the existing tangle.

## The cost of unclear ownership

Name the symptoms so you can diagnose the disease. Unclear decision rights show up as:

- **Decisions made repeatedly.** The same choice resurfaces in successive meetings because no one had the authority to close it. Re-deciding is the most visible tax of "no D."
- **Decisions unmade after the meeting.** A call is made, then quietly reversed in a side channel by someone who felt they should have had the D. This is the signature of a missing or contested Approver.
- **Reflexive escalation.** Every non-trivial choice floats up to a VP because the level that should own it can't. The senior person becomes a bottleneck and the org learns helplessness.
- **Diffusion of responsibility when it fails.** With multiple A's, a bad outcome has no owner — "owners disagree, priorities conflict," and the post-mortem finds everyone and no one accountable.
- **Velocity collapse.** "The more people involved… the longer approvals take," producing "bureaucracy that consumes time without adding value." Slow decisions are usually over-shared decisions.

## Tells of good vs. bad ownership

| Dimension | Bad | Good |
| --- | --- | --- |
| **The D** | "It depends who you ask" | Everyone names one Decider/Approver for the decision |
| **Accountability** | Two or more Accountable; shared = none | Exactly one A per decision, always |
| **Recommend vs. Decide** | Same person frames and chooses; framing preordains | Driver/Recommender split from Approver/Decider |
| **Veto sprawl** | Many Agree/Consulted roles; needs unanimity | Agree assigned sparingly; veto used rarely and on purpose |
| **Informed honesty** | Everyone gets a vote to seem inclusive | Affected parties placed in Informed — a deliberate "no say here" |
| **Model weight** | RAPID ceremony on a reversible call | Model matched to stakes: DACI for product calls, RAPID for cross-functional one-way doors |
| **Structure** | Critical initiative split across a divided owner amid dependencies | Single-threaded leader + separable team for the few initiatives that warrant it |

The fastest single test: for any decision in flight, ask three people independently **"who decides this?"** and see if you get one name. Convergent answer: ownership is clear. Divergent answers, hedges, or "well, technically…": you've found the decision that will be made three times and unmade once.

## One labeled caveat

The RAPID role definitions and the "Who has the D?" framing are attributed to Bain's _Decide & Deliver_ and the Rogers/Blenko 2006 HBR article, cross-checked against multiple secondary summaries (including Bain's own published material) in this session. RAPID® is a registered trademark of Bain & Company. DACI's Intuit origin and Atlassian's role definitions are from the Atlassian Team Playbook. The single-threaded-leadership quotes ("unencumbered by competing responsibilities," "separable… as APIs are for software," and the small-vs-dedicated finding) are attributed to Bryar & Carr's _Working Backwards_, paraphrased from secondary summaries rather than the print edition; verify exact wording before quoting verbatim.
