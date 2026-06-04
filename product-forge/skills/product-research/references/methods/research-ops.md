---
date: 2026-06-03
coverage: deep
primary_sources:
  - "Emma Boulton. \"The Eight Pillars of User Research.\" ResearchOps Community / Medium. https://medium.com/researchops-community/the-eight-pillars-of-user-research-1bcd2820d75a"
  - "Kate Kaplan (Nielsen Norman Group). \"ResearchOps 101.\" 2020-08-16. https://www.nngroup.com/articles/research-ops-101/"
  - "Nielsen Norman Group. \"Democratize User Research in 5 Steps.\" https://www.nngroup.com/articles/democratize-user-research/"
  - "User Interviews. \"Ethical Guidelines for Research\" (UX Research Field Guide). https://www.userinterviews.com/ux-research-field-guide-chapter/ethical-inclusive-research"
  - "User Interviews. \"The User Researcher's Guide to Data Privacy Regulations: GDPR, CCPA, CPRA.\" https://www.userinterviews.com/blog/the-user-researchers-guide-to-gdpr"
method: research-ops
phase: govern
domains: [11, 12]
timebox: "ongoing"
cadence: continuous
participants: [research-ops lead, researchers, "the wider org"]
inputs: ["demand for research", "tooling", "a governance / ethics need"]
produces: "the research operating system — recruiting, cadence, repository, ethics, democratization"
rubric: rubric-discovery
---

# Research Operations: Recruiting, Cadence, Repositories, Democratization, Ethics

Research operations (ResearchOps / ReOps) is the **plumbing that lets research happen repeatedly, at scale, and ethically** — the recruiting pipeline, the cadence, the repository, the consent and privacy regime, and the training that lets non-researchers participate without degrading quality. It is the difference between a team that _can_ talk to a customer this week and one that _does_, every week, without heroics. This reference covers the operational layer that surrounds the methods in this folder; the interview and survey _methods_ live in their own files. (Coverage is **developing** here: this is fast-moving practitioner territory, not a settled or peer-reviewed body of knowledge — sources are labeled accordingly.)

## What ResearchOps covers — NN/g's six areas

Nielsen Norman Group (Kate Kaplan) defines ResearchOps as _"the orchestration and optimization of people, processes, and craft in order to amplify the value and impact of research at scale"_ — a collective term for the efforts that support researchers in planning, conducting, and applying quality research. NN/g groups the work into **six operational areas**:

| Area | What it covers |
| --- | --- |
| **Participants** | Recruiting, screening, scheduling, and compensating study participants. |
| **Governance** | Processes and guidelines for consent, privacy, and information storage (the ethics/legal layer). |
| **Knowledge** | Collecting, synthesizing, and sharing research insights (the repository). |
| **Tools** | Consistent toolsets and platforms that create efficiencies. |
| **Competency** | Educating and onboarding others to perform research activities (the democratization enabler). |
| **Advocacy** | Defining and socializing the value of research across the organization. |

## The community origin: Boulton's Eight Pillars

The field's foundational map predates NN/g's framing: Emma Boulton's **Eight Pillars of User Research**, developed through the ResearchOps Community's global "#WhatIsResearchOps" workshops. The eight are commonly read as two halves: **four "left-hand" pillars about how research gets done and what supports it** (the context and capability) and **four "right-hand" pillars about systematizing and scaling it** — _"where the pain is felt"_ and what typically triggers a team to invest in ReOps in the first place. The pillars are widely summarized as: **Recruitment & admin; Tools & infrastructure; Data & knowledge management; Participant & data governance; Skills & competency; Socialization & advocacy; Templates & guidance; and the people/environment that hold it together.** The exact pillar names vary slightly between Boulton's original post and later restatements; this file treats the _categories_ as canonical and flags the labels as paraphrased.

## Recruiting: the bottleneck that breaks cadence

Recruiting is the single operational task that most often kills a research habit, because every study restarts the search for participants from scratch. The operational fixes:

- **A standing pipeline, not a fresh hunt.** Maintain a screened panel or participant pool (with consent to be re-contacted) so the next session is a scheduling problem, not a sourcing problem. This is the mechanism that makes Torres-style _weekly_ contact sustainable: a customer conversation lands on the calendar without a fresh act of will.
- **Screeners that protect validity.** A screener recruits the _right_ people and excludes the wrong ones (professional survey-takers, people outside the target job). Over-broad screeners pollute findings; over-narrow ones starve the pipeline.
- **Incentives, handled as policy.** Fair compensation for participants' time, budgeted and standardized (amount by session length/type), paid reliably. Incentives must compensate, not coerce — an incentive large enough to override a person's real preferences corrupts both ethics and data.
- **Scheduling and no-show management.** Over-recruit modestly, send reminders, and track no-show rates; a 30% no-show rate silently doubles your recruiting cost.

## Cadence: the operational target

Operations exists to support a _rhythm_. The discovery target (from `interviewing.md` / continuous discovery) is **at least weekly contact with real users, held by the team that builds the product.** ReOps makes that rhythm cheap enough to sustain: the panel removes the recruiting tax, templates remove the setup tax, and the repository removes the synthesis-from-scratch tax. The operational success test is not "did we run a big study" but "is a customer conversation a routine, low-friction event on this team's calendar." When research lapses, the cause is almost always operational friction (recruiting, scheduling, no template), not lack of will — fix the friction, not the motivation.

## Repositories: making insight outlast the researcher

A **research repository** is the shared, searchable store of research insight — what NN/g calls knowledge management, _"a shared database of research insights... where findings from studies across the organization can be stored."_ Its job is to stop insight from dying in slide decks the makers never see and from being re-discovered every two years. Operating principles:

- **Findability over volume.** A repository nobody can search is a graveyard. Tag by job, feature, segment, and date; make a stakeholder able to answer "what do we know about X?" in minutes.
- **Insight decay is real.** Findings have a shelf life — the product, the users, and the market move. Date everything and treat old findings as evidence-with-an-expiry, not permanent truth. (This is the same discipline as a dated reference file.)
- **"Atomic research" / nuggets (labeled as a practitioner pattern).** A popular approach decomposes findings into small, tagged, reusable units (an observation + evidence + tag) so insights can be recombined across studies. This is a useful pattern, _not_ settled doctrine — it can fragment context if a nugget is divorced from the story it came from; flagged here as a practitioner technique to adopt deliberately, not by default.
- **Raw + synthesized.** Store the evidence (clips, quotes, transcripts) alongside the synthesis, so a reader can audit a claim rather than trust a summary — the same "behavior over report" principle that makes co-witnessed interviews superior to handed-over PDFs.

## Democratizing research: the promise and the failure mode

"Democratization" means **enabling non-researchers (PMs, designers, support) to do research**, so insight isn't bottlenecked behind a small central team. NN/g's _Competency_ pillar is precisely this: _"developing formalized training... to train nonresearchers so that basic research can be incorporated into work when researchers cannot scale to demand."_ It is also the place ReOps most often goes wrong.

The honest trade-off, stated plainly by practitioners: **done well it scales insight and builds a user-centric culture; done badly it produces "poor-quality research, biased data, and diluted research rigor."** The specific failure modes when democratization is uncontrolled:

- **Confirmation-biased cherry-picking** — stakeholders run a quick study and surface only the findings that confirm what they already wanted to build.
- **Method misuse** — leading interviews, biased surveys, hypotheticals treated as forecasts (every pitfall in this folder, now committed at scale).
- **Misinterpretation in synthesis** — when many untrained people analyze, personal bias and subjective reading distort conclusions.

The consensus mitigation (NN/g, ResearchOps Community, Rosenfeld practitioners): democratization is **"a controlled approach led by research/ReOps professionals who provide training, guardrails, and oversight"** — programmes of **training, templates, and critique** that raise everyone's baseline. The model is _scaffolded participation_, not a free-for-all: researchers shift from doing all the research to **enabling and quality-controlling** it (guardrail templates for interview guides and surveys, a review/critique step, and clear lines for which studies a non-researcher may run solo versus which need a specialist). Democratize the _easy, well-scaffolded_ work; keep the high-stakes or high-ambiguity work with specialists.

## Consent and ethics: non-negotiable, and increasingly regulated

Governance is the pillar with legal teeth. The baseline is **informed consent**: the participant's voluntary agreement, _free of coercion_, with full disclosure of the study's purpose, procedures, risks, benefits, their rights, and crucially **the right to withdraw at any time without penalty** — captured as a signed or recorded record. The operational essentials:

- **Tell them what's collected and why**, in plain language, before you start — including whether the session is recorded.
- **The right to withdraw** must be real and easy, at any point, including after the session (data deletion on request).
- **Granular consent under GDPR (and CCPA/CPRA).** Where consent is the legal basis, it must be _"freely given, specific, informed, and unambiguous,"_ and **granular** — separate consent for each use. Concretely: consent to _participate_ does not cover sharing the recording later, or sending it to an external transcription vendor; each downstream use needs its own opt-in. (Labeled: GDPR/CCPA specifics are jurisdictional and evolving — confirm current requirements with counsel; this file states the principle, not legal advice.)
- **Data minimization, storage, and retention.** Collect only what the study needs, store it securely (access-controlled), and set a retention/deletion schedule rather than hoarding recordings indefinitely.
- **Anonymize and protect in the repository.** PII in clips and transcripts is a liability; strip or restrict it, and never let a quote in a repo expose a participant.
- **Inclusion as ethics.** Recruiting only convenient users (often the most similar to the team) both biases findings and excludes people the product affects — representative, inclusive recruitment is an ethical obligation, not only a validity one.

## Rigorous vs. weak (scoring rubric)

| Axis | Rigorous | Weak |
| --- | --- | --- |
| **Recruiting** | Standing screened panel with re-contact consent; validity-protecting screener. | Every study re-sources from scratch; recruits whoever is convenient. |
| **Cadence support** | Friction removed so weekly contact is routine and low-effort. | Heroic one-off pushes; research lapses whenever the team is busy. |
| **Incentives** | Standardized, fair, reliably paid; compensates without coercing. | Ad hoc or absent; or so large it distorts who participates. |
| **Repository** | Findable, tagged, dated; raw evidence + synthesis; decay acknowledged. | Findings stranded in decks; no search; undated and treated as permanent. |
| **Democratization** | Scaffolded — training, templates, critique, clear solo-vs-specialist lines. | Uncontrolled self-serve; cherry-picking and method misuse at scale. |
| **Consent** | Informed, voluntary, withdrawable; recorded; granular per-use under GDPR. | Verbal hand-wave; one blanket consent reused for any future purpose. |
| **Data handling** | Minimized, secured, retention-scheduled, PII stripped from the repo. | Recordings hoarded indefinitely; PII exposed in shared clips/quotes. |
| **Inclusion** | Representative, inclusive recruitment of affected users. | Convenience sample of users most like the team. |

## Note on sourcing (labeled)

ResearchOps is an active practitioner discipline, not an academic field — the canonical sources here are NN/g articles and the **ResearchOps Community** (Boulton's Eight Pillars), and the framing has evolved since ~2018, so specific pillar labels and tooling are paraphrased and dated rather than fixed. The **consent / GDPR / CCPA** specifics are summarized from practitioner guides (User Interviews' field guide and privacy guide) and reflect general principles; data-protection law is jurisdiction-specific and changes — treat this as orientation, **not legal advice**, and verify current obligations for your region before relying on them. The "atomic research / nuggets" repository pattern is one popular approach among several, labeled here as a technique to adopt deliberately, not a settled standard.
