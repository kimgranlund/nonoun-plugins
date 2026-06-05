---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Matt Ström, “Critique vs. review: a brief guide to design feedback” (mattstromawn.com) — “critique makes designs better; review makes decisions about them.”"
  - "NN/g, “Design Critiques: Encourage a Positive Culture to Improve Products” (nngroup.com/articles/design-critiques)."
  - "Figma, “How we run design critiques at Figma” (figma.com/blog/design-critiques-at-figma)."
  - "Marty C., *INSPIRED: How to Create Tech Products Customers Love* (2nd ed., 2017) — product reviews, the role of the decider, and operating cadence."
---

# Review Rituals & Operating Rhythm

A product org runs on a rhythm of recurring reviews — design crits, spec/PRD reviews, sprint ceremonies, quarterly business reviews. Done well, they are where decisions get made and quality gets enforced; done badly, they degrade into status theater where work is _admired_ and nothing is _decided_. The governing distinction, from Matt Ström, is sharp and load-bearing: **"critique makes designs better; review makes decisions about them."** Conflating the two is the single most common reason a review meeting produces a warm feeling and no verdict. This file is the working method for picking the right ritual, naming whether it's a gate or a checkpoint, and running a review that decides.

> **Ström's distinction:** a _critique_ is collaborative — the work is a draft, the goal is to make it better, and the designer "filters feedback and chooses what to act on." A _review_ is evaluative — the goal is to decide whether the work proceeds, and "approved changes are requirements." Be explicit about which one you are running; if you must combine them, separate the phases in time ("first 30 min critique, last 15 review").

## Gate vs. checkpoint: the structural choice

Before scheduling any recurring review, decide what it _is_. The two shapes have opposite postures and mixing them quietly is how reviews lose their teeth.

|  | **Gate** | **Checkpoint** |
| --- | --- | --- |
| **Purpose** | Decide go / no-go / change — work cannot pass without a verdict | Surface state, align, unblock; work continues regardless |
| **Output** | A decision, with a named decider | Shared understanding + any course corrections |
| **Posture** | Evaluative (Ström's "review") | Collaborative (Ström's "critique") or informational |
| **Authority** | Someone holds the D; can say no (see `ownership-and-raci.md`) | No one needs decision authority |
| **Failure mode** | Becomes a rubber stamp; gate that never stops anything | Becomes a covert gate; people block work without owning the call |
| **Examples** | Launch readiness, spec sign-off, system-contribution merge | Design crit, standup, mid-sprint demo, backlog refinement |

The rule: **a gate must be able to say no.** A "review" that has never rejected or materially changed anything is not a gate — it's a ceremony, and people learn to treat it as one. Conversely, a checkpoint that starts blocking work without a designated decider produces the worst outcome: decisions made by ambush, owned by no one. Name the shape, and match the authority to it.

## The ritual families

Match the ritual to the artifact and the cadence to the decision's tempo. Most orgs over-meet on checkpoints and under-invest in real gates.

- **Design critique (checkpoint, collaborative).** A standing forum to make in-progress design better. Figma's model: the presenter frames the problem and states **what feedback they want** ("I need help with the empty state, not the color"), so critique is targeted rather than a free-for-all. NN/g's load-bearing rule: critique is about the _work_, not the person, and it is explicitly **not** the venue for roadmap or major product decisions — keep those in a separate gate. A crit that wanders into "should we even build this" has lost its job.
- **Spec / PRD review (gate).** Evaluative sign-off that a spec is ready to build: problem clear, scope bounded, success measurable, open questions closed or owned. This gate has a single Approver (DACI's Approver / RAPID's Decide). Its tell of health is that specs sometimes come back marked _not ready_ — a PRD review that always approves isn't reviewing.
- **Sprint rituals (mixed).** Planning (a gate on _what enters_ the sprint), standup (a checkpoint — surface blockers, not status-report to a manager), review/demo (a checkpoint — show working software, gather reactions), retro (a checkpoint on _process_). The common decay is standup becoming a status meeting for the lead instead of a peer sync to unblock; if no one ever changes plan based on standup, it's theater.
- **Operating-rhythm reviews (gate, periodic).** Marty C.'s product reviews and the quarterly/business-review cadence: senior leaders evaluate progress against strategy and decide on bets, resourcing, and pivots. These are real gates with real deciders. The failure is the QBR-as-pageant: heavily produced slides, optimistic narratives, no hard decision — the org spends a week preparing to _not_ decide anything.

## How to run a review that decides

A decision-producing review is a designed thing, not a calendar invite. The mechanics:

- **State the decision on the table, up front.** "Today we decide whether this ships Thursday" or "we choose between flow A and flow B." A review without a named decision-to-be-made will drift into admiration by default — there's nothing to converge on.
- **Name the decider before the discussion.** Everyone should know who holds the D walking in (see `ownership-and-raci.md`). Without it, the loudest or most senior voice becomes the de facto decider, and the decision gets unmade later by whoever felt they should have had it.
- **Pre-read the material; don't present it live.** Amazon's narrative-memo discipline applies broadly: circulate the spec/doc in advance and open with silent reading, so the meeting is spent _deciding_, not _absorbing_. A review where the author walks slides for 40 minutes leaves 5 for the decision — backwards.
- **Separate critique from verdict in time.** If a session must both improve and decide, run the collaborative phase first ("explore, no decisions yet"), then explicitly switch ("now we decide"). Announcing the switch keeps people from treating exploratory ideas as binding requirements and vice versa.
- **End with a decision and an owner, recorded.** Close every gate with an explicit verdict (go / no-go / go-with-changes), the decider's name, and a one-line entry in the log — for one-way doors, an ADR (see `decision-records-adr.md`). A review whose output is "great discussion, let's reconvene" has failed; reconvening _is_ the cost of not deciding.
- **Right-size by reversibility.** Don't gate a two-way door. A reversible call gets a fast checkpoint or a delegated decision, not a launch-review committee. Reserve heavy gates for one-way doors (Bezos type-1 — see `decision-records-adr.md`); spending type-1 ceremony on type-2 work is the dominant rhythm failure in scaling orgs.

## Tells of good vs. bad review rituals

| Dimension | Bad | Good |
| --- | --- | --- |
| **Shape clarity** | Nobody knows if it's a gate or a checkpoint | Named explicitly; authority matched to the shape |
| **Critique vs. review** | Conflated — exploration treated as sign-off, or vice versa | Separated; presenter states what feedback they want |
| **Decision on table** | Open-ended "let's look at the work" | A specific decision named at the top |
| **Decider** | Emerges from seniority/volume mid-meeting | Named before discussion; holds a real D |
| **Material** | Presented live; meeting spent absorbing | Pre-read; meeting spent deciding |
| **Gate teeth** | Never rejects or changes anything; rubber stamp | Sometimes returns work as not-ready |
| **Output** | "Good discussion," reconvene later | Recorded verdict + owner; ADR for one-way doors |
| **Rhythm fit** | Heavy gate on reversible calls; QBR pageantry | Ceremony scaled to reversibility; checkpoints stay light |

The fastest single test for any recurring review: ask **"when did this meeting last change an outcome?"** If a gate has never said no and a checkpoint has never redirected work, the ritual is admiring, not deciding — and you can either give it teeth and a decider, or delete it and reclaim the hour.

## One labeled caveat

The "critique makes designs better; review makes decisions" framing and the critique-vs-review phase-separation advice are attributed to Matt Ström's essay and corroborated by NN/g's "Design Critiques" article in this session. The "state what feedback you want" presenter discipline is attributed to Figma's published crit practice. Marty C.'s product-review and operating-cadence material is paraphrased from _INSPIRED_ via secondary summaries rather than the print edition. The Amazon pre-read / silent-reading practice is widely reported (and appears in Bryar & Carr's _Working Backwards_) but is summarized here, not quoted; verify exact wording against the originals before quoting verbatim.
