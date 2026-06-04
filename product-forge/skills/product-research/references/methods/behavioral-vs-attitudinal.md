---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Christian Rohrer (Nielsen Norman Group). \"When to Use Which User-Experience Research Methods.\" https://www.nngroup.com/articles/which-ux-research-methods/"
  - "Nielsen Norman Group. \"Attitudinal vs. Behavioral Research in UX.\" https://www.nngroup.com/articles/attitudinal-behavioral/"
  - "Nielsen Norman Group. \"UX Research Methods: Glossary.\" https://www.nngroup.com/articles/research-methods-glossary/"
  - "Jakob N. (Nielsen Norman Group). \"First Rule of Usability? Don't Listen to Users.\" https://www.nngroup.com/articles/first-rule-of-usability-dont-listen-to-users/"
method: behavioral-vs-attitudinal
phase: frame
domains: [11]
timebox: "a short selection step"
cadence: per-decision
participants: [researcher, pm]
inputs: ["the question / what you need to learn", "the constraints (time, access, stage)"]
produces: "the right-fit research method (the behavioral×attitudinal / qual×quant placement)"
rubric: rubric-discovery
---

# Behavioral vs. Attitudinal: Say vs. Do, Qual vs. Quant

The most important single distinction in choosing a research method is **what people _say_ versus what people _do_.** They diverge constantly, and a method that measures one cannot answer a question about the other. This reference lays out the Nielsen Norman Group framework — Christian Rohrer's research-methods map — that organizes the entire method landscape along that axis (plus a second axis, qualitative vs. quantitative), so that a discovery review can tell whether a team used a method that is actually _valid_ for the question it asked.

## The say–do gap

People are unreliable narrators of their own behavior. NN/g's _Attitudinal vs. Behavioral Research in UX_ puts it directly: attitudinal research "gathers self-reported data... about their thoughts, feelings, and opinions," while behavioral research "involves directly observing user interactions." What users report and what they actually do frequently diverge, because users have **imperfect memories**, are subject to **social-desirability bias**, and **unconsciously align their answers with perceived norms**. Jakob N.'s blunter version — the "first rule of usability" — is _"don't listen to users; watch them use the design,"_ because "people's claims about how they use products are unreliable."

This is not a reason to discard attitudinal data. NN/g's stance is the opposite: the two are complementary, and **"the mismatches between user attitudes and user actions are often a great source of insights."** A user who _says_ checkout was easy but visibly _hesitated_ before clicking "Done" is the most informative case of all — the behavior tells you _that_ something is wrong, and only a follow-up attitudinal question tells you _why_ (did they doubt the purchase, or not understand the next step?). Behavior reveals what and where; attitude reveals why. You usually need both.

## The two axes

Rohrer's framework maps research methods on two primary axes (a third — _context of use_ — is covered below).

- **Attitudinal ↔ Behavioral** — _what people say_ vs. _what people do._ Attitudinal methods capture stated beliefs and self-report; behavioral methods observe actual usage.
- **Qualitative ↔ Quantitative** — Rohrer's exact distinction is about _how the data is gathered_, not sample size: **qualitative** studies generate data by observing or hearing behaviors **directly** (a researcher in the room, interpreting), while **quantitative** studies gather data **indirectly, through a measurement or an instrument such as a survey** or an analytics tool. Qualitative answers _why_ and _how to fix_; quantitative answers _how many_ and _how much_.

A common error is to equate "qualitative" with "small" and "quantitative" with "large." Rohrer's framing is sharper: the difference is **directness of observation**. A think-aloud usability session is qualitative because a human observes and interprets in real time; an unmoderated test of 500 users is quantitative because the data arrives through an instrument with no interpreter in the loop.

## The 2×2

Placing the two axes orthogonally yields the map. Methods are positioned by where they _typically_ sit; Rohrer is explicit that the framework is "not set in stone" — most methods can slide along an axis depending on how they are run.

```text
                          QUALITATIVE                         QUANTITATIVE
                     (direct observation,                (indirect, via an instrument
                      answers "why / how to fix")          answers "how many / how much")
                 ┌───────────────────────────────┬───────────────────────────────────┐
   ATTITUDINAL   │  Interviews                    │  Surveys / questionnaires          │
   (what people  │  Focus groups                  │  Desirability studies (quant)      │
    SAY)         │                                │  Card sorting (large, quant)       │
                 ├───────────────────────────────┼───────────────────────────────────┤
   BEHAVIORAL    │  Usability testing (moderated) │  A/B testing                       │
   (what people  │  Field studies / contextual    │  Analytics / clickstream           │
    DO)          │  Eye tracking (qual analysis)  │  Unmoderated usability (metrics)   │
                 │                                │  Eye tracking (aggregate metrics)  │
                 └───────────────────────────────┴───────────────────────────────────┘
   Hybrid / movable: card sorting, concept testing, and desirability studies straddle
   quadrants depending on sample size and how they are run.
```

| Method | Axis placement | Best answers |
| --- | --- | --- |
| **Usability testing (moderated)** | Behavioral · Qualitative | Why does this task fail? Where do people get stuck? |
| **Field / contextual studies** | Behavioral · Qualitative | What do people actually do in their real environment and context? |
| **Interviews** | Attitudinal · Qualitative | What do people believe, value, intend, struggle with (self-reported)? |
| **Focus groups** | Attitudinal · Qualitative | Group attitudes, language, perceptions (note: not behavior). |
| **Surveys / questionnaires** | Attitudinal · Quantitative | How many hold an attitude? At what scale do opinions distribute? |
| **A/B testing** | Behavioral · Quantitative | Which variant produces more of the target behavior, at scale? |
| **Analytics / clickstream** | Behavioral · Quantitative | What are users doing at scale? Where do they drop off? |
| **Card sorting** | Attitudinal · (qual→quant by N) | How do people mentally group/label content (information architecture)? |
| **Eye tracking** | Behavioral · (qual or quant) | Where do people look; what draws or misses attention? |
| **Desirability studies** | Attitudinal · (often quant) | What do people feel about a visual design / brand impression? |

## The third axis: context of use

Rohrer's framework adds a third dimension — **how participants are using the product during the study** — with four contexts that materially change what a method can claim:

- **Natural or near-natural use.** Minimal researcher interference, maximizing external validity (e.g., field studies, intercept surveys, analytics). You see real behavior but control little.
- **Scripted use.** Predetermined tasks focus the study on specific product areas (e.g., a moderated usability test, benchmarking, tree testing). Control is high; naturalism is sacrificed.
- **Limited / decontextualized use of the product.** Participants interact with a partial or abstracted artifact — a prototype, a mockup, sorted cards (e.g., card sorting, concept testing, participatory design).
- **Not using the product at all.** The study examines broader issues — brand perception, prior experience, attitudes (e.g., focus groups, desirability studies, many interviews).

A claim about real-world adoption made from a _scripted_ lab task, or a claim about _behavior_ drawn from a study where the participant never touched the product, is a context-mismatch — a frequent and scoreable defect.

## When each is valid (the decision rule)

The framework reduces to a routing rule: **match the method's axis to the question's axis.**

- Asking **why** something happens, or **how to fix** a design → qualitative (interviews, moderated usability).
- Asking **how many / how much**, or measuring a change → quantitative (surveys, analytics, A/B tests).
- Asking what people **believe, prefer, or intend** → attitudinal — but treat self-reported _future_ behavior or _recalled_ behavior as an **"imperfect estimate," not a measurement.** NN/g's explicit guidance: when a question touches past behavior or future intentions, rely on _behavioral_ research for the truth.
- Asking what people **actually do** → behavioral (observe; don't ask).

The strongest research programs run a **loop**: behavioral methods surface _that_ a problem exists and _where_ (analytics shows the drop-off), and attitudinal methods explain _why_ (interviews and follow-ups reveal the cause) — then a behavioral test confirms the fix moved the behavior. Neither half alone gives the full picture.

## Common invalid pairings (red flags for a rubric)

| The question | The wrong (but common) method | Why it's invalid | Valid method |
| --- | --- | --- | --- |
| "Will users adopt this feature?" | Survey: "Would you use this?" | Attitudinal/future-intent — a prediction, not behavior. | Behavioral: ship to a cohort; measure usage. A/B test. |
| "Why are users dropping off at step 3?" | Analytics dashboard alone | Behavioral/quant shows _that_ and _where_, never _why_. | Qualitative: moderated usability / interviews on that step. |
| "Is our information architecture intuitive?" | Asking users if the menu "makes sense" | Attitudinal self-report on a behavioral question. | Behavioral: tree testing / first-click testing; card sorting for the model. |
| "Which headline converts better?" | A focus group voting on headlines | Attitudinal group opinion ≠ real conversion behavior. | Behavioral/quant: A/B test live traffic. |
| "Do people find this design appealing?" | A usability task-success rate | Behavioral metric can't measure an attitude (appeal). | Attitudinal: desirability study / preference test. |

## Note on sourcing (labeled)

The framework, axis definitions, and method placements here are NN/g's (Christian Rohrer's research-methods map and the companion attitudinal-vs-behavioral article) — a widely adopted practitioner taxonomy from a UX-research consultancy, not a peer-reviewed classification, and NN/g itself stresses the map is flexible rather than canonical. The say–do gap it rests on _is_ well established in the academic record (e.g., the LaPiere 1934 attitude–behavior discrepancy and the broad social-psychology literature on social-desirability bias); this file cites the NN/g operationalization because that is the form product teams use. Treat exact quadrant placements as typical-not-fixed, exactly as Rohrer does.
