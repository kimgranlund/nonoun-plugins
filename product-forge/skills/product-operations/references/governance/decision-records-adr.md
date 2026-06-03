---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Michael Nygard, “Documenting Architecture Decisions” (cognitect.com/blog/2011/11/15/documenting-architecture-decisions, 2011) — the ADR format: Context → Decision → Consequences, with Status."
  - "Jeff Bezos, 2015 Letter to Amazon Shareholders — Type 1 (irreversible, one-way door) vs. Type 2 (reversible, two-way door) decisions."
  - "Martin Fowler, “Architecture Decision Record” (martinfowler.com/bliki/ArchitectureDecisionRecord.html) and the ADR community index (adr.github.io)."
---

# Decision Records (ADRs) & the Reversibility Bar

An organization's memory of _why_ decisions less than its memory of _what_ was decided. Six months on, the reasoning is gone, the people who held it have rotated, and the team relitigates a settled question because no one recorded the forces that made the call obvious at the time. A decision record fixes that for a flat cost: a short, immutable note capturing the situation, the choice, and what it cost. Michael Nygard's ADR is the canonical form, and Bezos's type-1/type-2 distinction tells you **how much ceremony a given decision deserves** — which is the difference between a useful records practice and a bureaucratic one.

> **Nygard (2011):** an ADR is "a short text file… [each] describes a set of forces and a single decision in response to those forces." It is written when the decision is made, never edited after, and superseded (not deleted) when reversed. The artifact is the reasoning, frozen at the moment of choice.

## The Nygard format

An ADR has four parts, and the discipline is in keeping each one honest. Nygard's original is deliberately tiny — resist the urge to bloat it.

| Section | Captures | The discipline |
| --- | --- | --- |
| **Status** | proposed → accepted → deprecated / superseded-by-XXX | A decision has a lifecycle; a superseded ADR stays in the log with a pointer to its replacement, never erased |
| **Context** | "the forces at play… technological, political, social, and project-local" | State the situation _neutrally_, including the forces pushing the other way. If the context only justifies the decision, it's a sales pitch, not a record |
| **Decision** | the response, "in full sentences, with active voice" | "We will…" — one decision per record. If you're recording two choices, write two ADRs |
| **Consequences** | "the resulting context, after applying the decision" — good, bad, and neutral | Name what gets _harder_, not just what gets better. A consequences section with no downside is incomplete by definition |

Two properties make ADRs work and are routinely violated:

- **Immutability.** You do not edit an accepted ADR to reflect a later change of mind. You write a _new_ ADR that supersedes it. The log is a history, and editing history destroys its value — the whole point is to see what was true when the call was made, including the parts that later proved wrong.
- **One decision per record.** A record covering "our entire architecture" is a design doc, not a decision record. ADRs are atomic so they can be superseded individually and cited precisely.

## Context → Decision → Consequences is the reusable spine

The ADR's three-beat structure is not specific to architecture; it is the right shape for **any** consequential product decision — a pricing change, a platform bet, a deprecation, a scope cut. Product decision logs lift the same spine: the situation and forces, the choice with its rationale, and the accepted consequences. The move that separates a real record from theater is the **Consequences** beat: it forces you to pre-commit to the costs, so when a cost lands later you can point to the record and say "we knew, and chose anyway" — rather than treating a foreseeable trade-off as a surprise failure.

A decision log also closes the loop with principles and strategy: a good record _cites the principle or strategic diagnosis it leaned on_ (see `product-principles.md`), so the chain from standing commitment → specific decision → consequence is legible to the next reader. That is how an org's decisions compound instead of contradicting each other.

## Type-1 vs. type-2: setting the review bar

Bezos's 2015 shareholder letter gives the single most useful lever for right-sizing decision process. **Not all decisions deserve the same ceremony**, and most organizations get this exactly backwards as they scale.

- **Type 1 — one-way doors.** "Consequential and irreversible or nearly irreversible." If you walk through and dislike what's there, "you can't get back to where you were before." These "must be made methodically, carefully, slowly, with great deliberation and consultation." _These deserve an ADR and a real review._ Examples: a public API contract, a data model others will build on, a pricing architecture, a platform/vendor lock-in.
- **Type 2 — two-way doors.** "Changeable, reversible." "If you've made a suboptimal Type 2 decision, you don't have to live with the consequences for that long. You can reopen the door." These "can be made quickly, often by individuals or small teams, without extensive oversight." _These deserve a one-line log entry at most, and often nothing._ Examples: a button label, a copy change, an internal tool default, a reversible feature flag.
- **The scaling failure Bezos names directly:** "As organizations get larger, there seems to be a tendency to use the heavy-weight Type 1 decision-making process on most decisions, including many Type 2 decisions. The end result… is slowness, unthoughtful risk aversion, failure to experiment… and consequently diminished invention." Applying type-1 ceremony to type-2 decisions is not caution; it is a tax on velocity that masquerades as rigor.

The practical rule for governance: **classify the door before you choose the process.** A one-way door gets the ADR, the review, the named Approver (see `ownership-and-raci.md`). A two-way door gets a fast call by the owning team and, if anything, a logged note. The error in both directions is real — skipping rigor on a one-way door is reckless; piling rigor on a two-way door is sclerotic — but in mature orgs the dominant failure is the second.

## How to run a records practice that survives

A decision-records habit dies the same way documentation dies: friction kills adoption (see `documentation-as-system.md`). Keep it cheap or it won't happen.

- **Keep records next to the work.** ADRs live in the repo as markdown (`docs/adr/0001-title.md`), versioned with the code, reviewed in the same pull request as the change they justify. A decision log in a separate wiki drifts; one in the repo gets updated because it's in the diff.
- **Write it when the decision is made, not after.** A record reconstructed weeks later launders out the forces that pushed the other way — exactly the part future-you needs. The cost of an ADR is ten minutes _at the moment of choosing_; deferred, it's never paid.
- **Number them and never renumber.** Sequential IDs make them citable ("see ADR-0042"). Superseding ADR-0042 means writing ADR-0067 and marking 0042 `superseded by 0067` — both stay.
- **Lower the bar to entry.** A three-sentence ADR that exists beats a perfect one that doesn't. The format is small on purpose; gold-plating the template is how a records practice dies of its own weight.

## Tells of good vs. bad decision records

| Dimension | Bad | Good |
| --- | --- | --- |
| **Context honesty** | Reads as justification; omits the forces against | States the situation neutrally, including the losing arguments |
| **Decision atomicity** | One record covers many entangled choices | One decision per record; "We will…" in active voice |
| **Consequences** | Lists only benefits | Names what gets harder; pre-commits to the cost |
| **Mutability** | Edited later to match what actually happened | Immutable; reversals are new, superseding records |
| **Reversibility match** | Same heavy process for every decision | Door classified first; type-1 gets the ADR, type-2 gets a line or nothing |
| **Locality** | Lives in a separate wiki; drifts | In the repo, in the PR, versioned with the code |
| **Timing** | Reconstructed after the fact | Written at the moment of decision |
| **Linkage** | Free-floating; cites no principle or strategy | Cites the principle/diagnosis it leaned on; chain is legible |

The fastest single test: open any decision record and look for the sentence that says **what this decision made worse.** If every record is all upside, the practice is theater — it's recording conclusions, not decisions. A real record can be read back, years later, by someone who'll inherit the cost, and it tells them the org saw the cost coming.

## One labeled caveat

The Nygard format specifics ("a short text file," "forces at play… technological, political, social," "full sentences, with active voice," "resulting context, after applying the decision," and the proposed/accepted/superseded statuses) are attributed to his 2011 Cognitect post "Documenting Architecture Decisions," cross-checked against the ADR community index (adr.github.io) and Martin Fowler's bliki entry. The type-1/type-2 quotes ("one-way doors," "you can't get back to where you were before," and the "tendency to use the heavy-weight Type 1… process on most decisions" passage) are attributed to Bezos's 2015 Letter to Shareholders, paraphrased from the letter and multiple secondary summaries in this session; verify exact wording against the primary PDF before quoting verbatim.
