---
date: 2026-06-03
coverage: deep
primary_sources:
  - "Erika Hall, Just Enough Research, 2nd ed. (A Book Apart, 2019)"
  - "Ron K., Diane Tang, Ya Xu — Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing (Cambridge University Press, 2020)"
  - "Ron K., Henne, Sommerfield — Practical Guide to Controlled Experiments on the Web: Listen to Your Customers not to the HiPPO (KDD 2007)"
  - "Ronny Ron K. — The Origin of HiPPO: Highest Paid Person's Opinion (linkedin.com/pulse, exp-platform.com/hippo)"
  - "Teresa T., Continuous Discovery Habits (Product Talk LLC, 2021); Assumption Testing (learn.producttalk.org/assumption-testing)"
  - "Raymond S. Nickerson — Confirmation Bias: A Ubiquitous Phenomenon in Many Guises, Review of General Psychology 2(2), 1998"
  - "Farnam Street — Confirmation Bias and the Power of Disconfirming Evidence (fs.blog/confirmation-bias)"
---

# Research to Decision: Turning Findings Into Bets

Research that does not change what someone does is overhead. The hard part of synthesis is not summarizing what you learned — it is converting findings into a **bet**: a specific decision the team will make differently because of the evidence. This reference is about that conversion. It covers what research is _for_ (reducing the risk of a decision), how to weigh evidence by strength rather than by how much you like it, the bias that quietly turns research into theater, and the one acceptance test that separates real decision-changing research from expensive self-congratulation.

> Erika Hall's reframe is the whole posture: stop asking _"do we need to do research?"_ and ask _"what do we need to learn?"_ — because _"the greater risk is to design and build a product without doing research,"_ and good research _"isn't about proving yourself right, it's about staying genuinely curious."_ Research is a tool for **reducing the risk of a decision**, and the amount of research should _scale with the amount of risk and the number of unknowns_. If a finding can't move a decision, it wasn't worth gathering.

---

## Start from the decision, not the method

A finding is inert until it is tied to a choice. The synthesis flow runs decision-first:

```text
  DECISION at stake        →  what will we do differently, and what are the options?
        ↓
  unknown that blocks it   →  what do we not yet know that, if known, picks an option?
        ↓
  research to learn it     →  the smallest study that resolves the unknown
        ↓
  finding                  →  what the evidence actually showed
        ↓
  BET                      →  the option chosen, and what would have changed it
```

If you cannot name the decision a piece of research feeds, you are collecting, not deciding. Hall's _"how much research is enough"_ has a precise answer in this frame: **enough to make _this_ decision with acceptable risk** — no more (gold-plating burns time) and no less (deciding on a guess). The output of synthesis is not a report; it is _"we will do X (not Y), because the evidence showed Z."_

---

## Weigh evidence by strength, not by comfort

Not all findings carry the same weight, and the most dangerous error is to weight a finding by how much it pleases you rather than by how much it can bear. Two complementary models calibrate this.

**Torres's evidence map (for discovery-grade signals).** Plot each assumption on two axes: importance (low → high) and strength of evidence you currently have (strong → weak). The assumptions in the **weak-evidence / high-importance** corner are the _leap-of-faith_ assumptions — _"which assumptions should be tested first."_ Critically, Torres pushes teams off the statistical-significance treadmill at the discovery stage: teams _"get caught up in statistical significance and squabbling over sample size,"_ but assumption tests are meant to give _"quick directional feedback (signals)"_ — you _"don't need large sample sizes to get started,"_ you iterate through small tests for direction, _then_ verify with structured experiments when stakes and sample size warrant. Match the rigor to the bet.

**Ron K.'s bar (for ship-grade causal claims).** When the decision is a real launch with real stakes, directional signal isn't enough — you need a controlled experiment. Ron K., Tang, and Xu's central caution is that observed effects are routinely _not_ what they appear: the book is largely about the traps (novelty effects, segment mix shifts, p-hacking, peeking) that make a result _look_ real when it isn't. A causal "X caused the lift" claim earns ship-grade trust only from a trustworthy controlled experiment; everything weaker is a hypothesis, not a verdict.

A rough strength ladder, weakest to strongest — label every finding with where it sits:

| Strength | Evidence type | What it licenses |
| --- | --- | --- |
| **Weakest** | A stakeholder opinion / one anecdote | A hypothesis to test — nothing more |
| **Weak** | What customers _say_ they'll do (stated preference, predictions) | Directional curiosity; people over-report intent |
| **Moderate** | A specific story about real past behavior; a small assumption test | A directional bet you can act on with eyes open |
| **Strong** | Observed behavior at scale; a single controlled experiment | A confident decision, watched for confounds |
| **Strongest** | Replicated controlled experiments / triangulated sources agreeing | A durable commitment |

> **Triangulate before you commit big.** A single source — however clean — is a single point of failure. Strength comes partly from _agreement across methods_: a behavioral signal that matches what interviews surfaced and what the experiment confirmed is far stronger than any one of them alone. When one source must stand alone, label the bet as single-source and size the commitment accordingly.

---

## Confirmation bias: how research quietly becomes theater

The failure mode that voids research is not bad data — it is selectively gathering and reading data to confirm what you already wanted. Confirmation bias is, in Nickerson's classic definition, the tendency to _"seek out, interpret, remember, and give more weight to evidence that supports"_ a held view while _"ignoring, dismissing, or undervaluing"_ evidence that contradicts it. It is, in his words, a _"ubiquitous"_ phenomenon — the default, not the exception.

How it shows up in product research specifically:

- **Asking only confirming questions.** Running interviews or tests designed to elicit the "yes" you're hoping for, and skipping the probes that could surface a "no."
- **Reading neutral data as supportive.** Interpreting an ambiguous result as a green light because that's the result you wanted.
- **Discounting the disconfirming case.** Treating the one user who hated it as an outlier while treating the one who loved it as the signal.
- **Stopping early.** Halting data collection the moment the evidence tips toward the prior (the experimentation analogue: _peeking_ and stopping when the result looks good).

Why it's so sticky: people show confirmation bias partly _to protect self-esteem_ — discovering a valued belief is wrong feels bad, so we seek information that supports what we already think. That is the motivational engine you are fighting.

**The two evidence-backed countermeasures:**

1. **Actively seek disconfirming evidence.** The single most reliable correction: go looking for the data that would prove you _wrong_, not right. Karl Popper's falsification logic, restated for product: a claim is only as strong as the disconfirming tests it has _survived_, not the confirming examples you can list. Design at least one probe whose results could kill the idea.
2. **Build in accountability.** Lerner and Tetlock's finding: we think critically _"only when held accountable by others"_ — if we expect to justify our conclusions to someone, we are markedly less prone to confirmatory reasoning. Operationally: before fielding research, pre-register what you expect and what result would change your mind; review findings with a skeptic whose job is to argue the opposite read.

> **The HiPPO trap is confirmation bias with a title.** Ron K. coined _HiPPO_ — the **Highest Paid Person's Opinion** — for decisions driven _"not by evidence or user needs, but by the gut feelings of the most senior person in the room."_ His prescription is the title of the 2007 paper: _"Listen to Your Customers not to the HiPPO."_ Research used to ratify the HiPPO's prior, rather than to test it, is the organizational form of confirmation bias — and the most expensive, because it wears the costume of evidence.

---

## The acceptance test: did the research change a decision, or confirm a prior?

This is the single test that tells real research from theater. After synthesis, ask of every study:

> **Could this research have come back the other way — and if it had, would the team have done something different?**

- If **no result would have changed the plan**, the research was theater. It was run to manufacture cover for a decision already made. (Tell-tale signs: the study was commissioned _after_ the decision; the deck only contains supporting quotes; nothing surprised anyone.)
- If a **plausible result would have changed the plan**, the research was a genuine input — whether or not it happened to confirm the prior this time. Confirming a prior is fine _when the prior was genuinely at risk_; the test is whether the risk was real, not whether the answer flipped.

|  | Decision-changing research | Confirmation theater |
| --- | --- | --- |
| **Timing** | Run _before_ the decision, to inform it | Run _after_, to defend a decision already made |
| **Falsifiability** | A defined result would have killed/changed the bet | No result could have changed anything |
| **The findings** | Include the disconfirming cases, surprises, "we were wrong about X" | Curated to support; outliers dismissed; all tidy |
| **The questions** | Probe for the "no" as hard as the "yes" | Leading questions engineered to elicit "yes" |
| **Emotional tell** | Something in it was uncomfortable or surprising | Everyone nodded; it felt great; it matched the plan exactly |
| **The bet** | "We'll do X, and here's what would have changed our mind" | "The research confirms we should do what we planned" |

> **The surprise heuristic.** Decision-changing research almost always contains at least one finding the team didn't want or expect — a relocated pain point, a killed assumption, a "users do the opposite of what we thought." Research that comes back 100% confirming the prior, with zero surprises, is either extraordinarily lucky or — far more often — was never a real test. Treat a frictionless, all-confirming result as a smell, not a win.

---

## Operating notes

- **Write the bet, not the summary.** The synthesis deliverable is a decision sentence — "we will do X (not Y) because Z; here is what would have changed our mind" — not a findings dump. A summary with no decision attached has done none of the hard work.
- **Pre-commit to what would change your mind.** Before fielding, write down the prior and the result that would overturn it. This is the cheapest, strongest defense against reading the data to suit yourself.
- **Match rigor to the size of the bet.** Directional assumption tests for cheap, reversible discovery calls; controlled experiments for expensive, hard-to-reverse launches. Demanding statistical significance for a one-day spike is as wrong as shipping a billion-dollar bet on three interviews.
- **Name the strength of every finding.** Tag each input — opinion / stated / observed / experimental — so the team can't quietly promote a stakeholder hunch to the weight of a controlled result.
- **Keep a skeptic in the room.** Accountability to someone whose job is to argue the opposite is, per the evidence, the most effective debiasing move available. Use it on every consequential bet.
