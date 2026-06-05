---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Bob Moesta. *Demand-Side Sales 101: Stop Selling and Help Your Customers Make Progress*. Lioncrest Publishing, 2020."
  - "Chris Spiek & Bob Moesta (The Re-Wired Group). The \"Switch\" interview and Forces of Progress diagram. https://jobstobedone.org/radio/unpacking-the-progress-making-forces-diagram/"
  - "Intercom — \"Bob Moesta on unpacking customer motivations with Jobs-to-be-Done.\" https://www.intercom.com/blog/podcasts/bob-moesta-on-unpacking-customer-motivations-with-jobs-to-be-done/"
  - "The Re-Wired Group — \"Milkshakes in the Morning\" case study. https://therewiredgroup.com/case-studies/milkshakes/"
  - "Clayton C., Taddy Hall, Karen Dillon, David S. Duncan. *Competing Against Luck*. HarperBusiness, 2016 (the mattress / milkshake interviews)."
method: jtbd-discovery
phase: discover
domains: [1, 11]
timebox: "~1 hr per interview"
cadence: recurring
participants: [interviewer, "recent switchers"]
inputs: ["recent switchers (people who just hired or fired a solution)", "the timeline technique"]
produces: "the job, the forces of progress, and the switch triggers"
de_risks: [value]
rubric: rubric-discovery
---

# JTBD Switch Interviews (Moesta / Re-Wired lineage)

This file covers the **Switch interview** — the investigative method, developed by Bob Moesta and Chris Spiek at The Re-Wired Group, for reconstructing the timeline and the forces behind a single real purchase decision. It is the _method_ half of Jobs-to-be-Done. The _theory_ half — Clayton C.'s "customers hire products to make progress in a circumstance" — lives in `../../../product-methodology/references/jtbd/jobs-to-be-done.md`; that file deliberately stays Clayton C.-canonical and flags this Moesta practice as a distinct lineage. Read this one for **how to run the interview**.

> The goal of a switch interview, in Moesta's framing, is to reverse-engineer one decision: to recover _"the causal mechanism that caused someone to switch"_ — what was going on in their life that made the old way intolerable, and what gave them the energy to buy the new thing on the day they bought it.

## What makes it a "switch"

The unit of study is the moment a customer **fired** one solution and **hired** another — the switch. This is why the method recruits **recent switchers** (people who bought, changed, or quit within roughly the last 60–90 days, while the memory is still vivid) rather than prospects, satisfied long-term users, or a demographic segment. Non-consumption counts as a fired solution: someone who finally bought a CRM after years of spreadsheets-and-sticky-notes switched away from "doing nothing in particular," and that prior struggle is exactly the data you want. The interview ignores who the person _is_ (age, role, segment) in favor of what _happened_ — Moesta's recurring point is that the circumstance, not the customer profile, is causal.

## The four forces of progress

Every switch is governed by four forces — two that push toward change and two that hold the person in place. A switch happens only when the forces of progress beat the forces of inertia.

```text
        FORCES DRIVING THE SWITCH                 FORCES OPPOSING THE SWITCH
   ┌──────────────────────────────────┐    ┌──────────────────────────────────┐
   │  PUSH of the situation            │    │  HABIT of the present             │
   │  the present is broken enough     │    │  the comfort/inertia of the       │
   │  that "this isn't good enough"    │    │  current way; "it's fine"         │
   │                                   │    │                                   │
   │  PULL of the new solution         │    │  ANXIETY of the new solution      │
   │  the new thing is attractive      │    │  fear of the unknown: will it     │
   │  enough to be worth the cost      │    │  work? will we adopt it? what     │
   │  of switching                     │    │  if it's worse?                   │
   └──────────────────────────────────┘    └──────────────────────────────────┘

          a SWITCH occurs only when:   PUSH + PULL  >  HABIT + ANXIETY
```

- **Push of the situation.** Almost all change starts with a push — a specific event or accumulating frustration that makes the status quo unacceptable. The push lives in a _circumstance_ (an occasion, a deadline, a breaking point), not in a personality.
- **Pull of the new solution.** What about the new thing is attractive enough to outweigh the cost of switching — a vivid feature, a promise, a peer's recommendation, a story of someone like them succeeding.
- **Anxiety of the new solution.** What worries the customer about adopting it — will it work, will it integrate, will the team actually use it. Anxiety is the most under-addressed force; sales and product teams pour effort into pull and ignore the anxiety that silently kills the deal.
- **Habit of the present.** The inertia and comfort of the existing way — even a bad current solution is _known_, and the known is safe. Switching costs (re-learning, migrating, the risk of looking foolish) all live here.

The practical lesson: a stuck switch is rarely fixed by adding more pull (more features). It is more often fixed by **reducing anxiety and habit** — de-risking the new solution and lowering the cost of leaving the old one. The forces are diagnostic: a finished interview should let you place quotes under each of the four.

## The timeline of the decision

The interview's spine is a **reconstruction of the timeline backward from purchase**, recovering the moments most people cannot recall when asked directly. The canonical Re-Wired / Clayton C. timeline runs through phases:

```text
  FIRST THOUGHT ──► PASSIVE LOOKING ──► ACTIVE LOOKING ──► DECIDING / PURCHASE ──► CONSUMING / ONGOING USE
   the very           "huh, maybe          actively           the moment of            living with the
   first time the     someday" — not       comparing,         commitment and the       choice; did it
   idea entered       yet shopping         shortlisting,      trigger that forced      deliver the
   their head                              shopping           action THAT day          progress?
```

The most valuable and hardest-won point on the timeline is the **first thought** — the very first moment the idea of a different solution crossed the person's mind, often long before any shopping began. Recovering it tells you what truly initiated the journey (the real push), which is almost never what the customer says when asked "why did you buy this?" Equally critical is the **deciding** moment: not the general intent but the _specific trigger_ that forced action on a particular day (a renewal notice, an outage, a colleague's comment, a deadline). Vague "I'd been meaning to" answers are a signal to dig until a concrete date and event surface.

## Running the interview: technique

The switch interview is closer to a documentary or detective interrogation than to a survey. Concrete craft, drawn from Moesta's and the Re-Wired team's practice:

- **Two interviewers.** One drives the conversation; the second documents and watches for threads the driver misses. (Clayton C.'s collaborators describe interviews staffed like a forensic team, "almost like CSI.")
- **Reconstruct backward, then walk forward.** Start at the known event — the purchase — and work back to the first thought, then replay the story forward in order. People remember a story better as a sequence than as an abstraction.
- **Ask "what happened," never "why."** "Why did you buy it?" invites a rationalized, after-the-fact justification. "What was happening the day you decided?" / "What did you do right before?" / "What did you Google?" recover behavior. Replace the abstract with the concrete event.
- **Chase the energy.** Emotional intensity — where the person's voice quickens, where they get animated or frustrated — marks what actually mattered in the decision. Follow the energy, not your script.
- **Unpack vague words.** When a customer says "it was too complicated" or "it just felt right," that is the beginning of the inquiry, not the end: "Too complicated — what do you mean? Walk me through the moment it felt complicated."
- **Hold a loose agenda.** Moesta's own opener is roughly _"I don't have a long list of questions — I just want to hear your story."_ The structure lives in the interviewer's head (the timeline and the four forces), not in a question list read aloud.

## The milkshake and mattress cases (where this method came from)

The method is most famous from the **milkshake study** — Re-Wired's work for a fast-food chain — which found two entirely different jobs (a viscous, one-handed companion for a boring morning commute; an afternoon treat a parent uses to say "yes" to a child), each with a different competitive set, and concluded that you can only improve a product _against a job in a circumstance_. The **mattress interview** reproduced in _Competing Against Luck_ is the canonical demonstration of the timeline technique itself: the interviewer painstakingly reconstructs when the buyer first thought about a new mattress, what pushed them, what they compared, and what nearly stopped them — modeling exactly the backward reconstruction described above.

## Synthesis: from interviews to a job

One interview is an anecdote. The method calls for **patterns across roughly 5–12 switch interviews** in the same job, after which the forces and the timeline begin to repeat. The output is not a persona but a **job spec**: the circumstance + the progress sought, with the four forces populated by real quotes, and a map of the competitive set the customer actually weighed (including non-consumption). That spec then drives both product (amplify push/pull, design out anxiety/habit) and messaging (speak to the circumstance and the struggling moment, not to demographics).

## Rigorous vs. weak (scoring rubric)

| Axis | Rigorous | Weak |
| --- | --- | --- |
| **Recruiting** | Recent switchers (bought/changed/quit in ~60–90 days), including switches from non-consumption. | Prospects, long-tenured happy users, or a recruited demographic segment. |
| **Anchoring** | A single, specific, datable purchase reconstructed end to end. | A general discussion of "how they think about" the category. |
| **First thought** | The interview recovers the original trigger long before shopping began. | The story starts at "I started looking" and never finds what initiated it. |
| **Question form** | "What happened the day you...?" — behavior and events. | "Why did you buy it?" — invites rationalized justification. |
| **Forces coverage** | Quotes populate all four forces, including anxiety and habit. | Only push/pull captured; anxiety and habit ignored. |
| **Trigger specificity** | The deciding moment is pinned to a concrete event and date. | "I'd been meaning to for a while" accepted as the answer. |
| **Synthesis** | Patterns drawn across ~5–12 interviews into a job spec. | A single vivid interview generalized into a product decision. |

## Note on lineage and sourcing (labeled)

"Jobs-to-be-Done" is not one school. This file covers the **Moesta / Spiek / Re-Wired switch-interview practice** (the four forces, the timeline of demand, the switch interview), which grew out of the same milkshake work as Clayton C.'s theory but is a distinct, more operational method. It differs again from **Tony Ulwick's Outcome-Driven Innovation (ODI)**, which decomposes a job into measurable "desired outcomes" and is heavily quantitative — do not blend ODI's outcome statements with Moesta's forces without flagging it. The sources here are practitioner books, the Re-Wired Group's own case material, and recorded interviews (Intercom, jobstobedone.org), not peer-reviewed research; treat the forces model as a well-validated practitioner framework, not an empirically tested theory. When a teammate says "JTBD," confirm which lineage they mean before reconciling definitions.
