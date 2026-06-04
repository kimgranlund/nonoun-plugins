---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Pew Research Center. \"Writing Survey Questions.\" https://www.pewresearch.org/writing-survey-questions/"
  - "Pew Research Center. \"Methods 101: Survey Question Wording\" (video + transcript). https://www.pewresearch.org/methods/2018/03/21/methods-101-video-question-wording/"
  - "Sean Ellis. \"Using Product/Market Fit to Drive Sustainable Growth.\" GrowthHackers / Medium. https://medium.com/growthhackers/using-product-market-fit-to-drive-sustainable-growth-58e9124ee8db"
  - "Sean Ellis. \"The Startup Pyramid.\" Startup Marketing Blog. https://www.startup-marketing.com/the-startup-pyramid/"
  - "Rahul Vohra. \"How Superhuman Built an Engine to Find Product/Market Fit.\" First Round Review. https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/"
method: survey-design
phase: measure
domains: [11]
timebox: "design + field over days"
cadence: per-decision
participants: [researcher, "a representative sample"]
inputs: ["a precise question", "a sample frame", "a piloted instrument"]
produces: "quantified attitudes and segment signal at scale (including the PMF signal)"
de_risks: [value]
rubric: rubric-discovery
---

# Survey Design: Pitfalls, Sampling, and When Surveys Lie

Surveys are the most abused method in product research because they are the cheapest to run and the easiest to run _badly_. A survey is an **attitudinal, quantitative instrument** (see `behavioral-vs-attitudinal.md`): it measures _what a self-selected sample says_, gathered indirectly. That makes it powerful for sizing opinions across many people — and dangerous when used to answer questions it cannot answer, with questions that bias the answer, on a sample that doesn't represent the population. This reference catalogs the failure modes, the sampling traps, and the conditions under which a survey produces truth, then covers the one product survey worth memorizing: Sean Ellis's product-market-fit question.

## What surveys are good at — and what they are not

Use a survey to **quantify the distribution of an attitude** across a population too large to interview: how many users hold an opinion, which of several stated preferences ranks highest, how satisfaction varies by segment. Do **not** use a survey to discover _why_ (that is qualitative — interviews, usability), to predict _behavior_ from stated intent ("would you use this?" — see below), or to find unknown problems (a survey can only ask about what you already thought to ask). The strongest pattern is **qual-then-quant**: interviews surface the hypotheses and the _language_ real users use, and a survey then sizes them. Writing a survey before you have talked to anyone usually bakes your own assumptions into the question set.

## The question-wording pitfalls

Most survey error is introduced before a single response arrives, in the wording. The recurring offenders:

- **Leading questions** embed the desired answer or a presupposition. _"How much do you love our new dashboard?"_ presumes love; _"Don't you agree that faster checkout is important?"_ signals the expected reply. Strip the valence and the assumption: _"How would you describe your experience with the dashboard?"_
- **Loaded / assumptive questions** assume something about the respondent that may be false, alienating or skewing them. _"What do you think about the negative impact of social media on teenagers?"_ presupposes a negative impact; _"When did you stop using competitor X?"_ presupposes they used it.
- **Double-barreled questions** ask about two things at once, so a single answer is uninterpretable. _"How satisfied are you with the pace and content of this training?"_ cannot be answered honestly by someone for whom the pace worked but the content didn't. Split it into two questions.
- **Acquiescence bias** is the documented tendency to **agree** with a statement, independent of its content — especially among less-informed respondents, and (per Pew) _more pronounced when an interviewer is present_ than when self-administered. Agree/disagree formats are the chief vector. Mitigations: prefer construct-specific response options over agree/disagree (ask _"How would you rate the speed?"_ not _"Speed is good — agree/disagree?"_), and include a few **reverse-scored items** to detect respondents who agree with everything.
- **Vague quantifiers and undefined terms.** "Often," "regularly," "a few" mean different things to different people; "Do you use it regularly?" returns noise. Anchor to concrete frequencies ("In the last 7 days, how many times...?").
- **Memory and projection.** Questions about _past_ behavior and _future_ intentions are, in Pew's and NN/g's shared view, **imperfect estimates, not measurements.** "How many times did you do X last month?" overstates; "Would you use this?" overstates more.

## Scale and response-option pitfalls

The answer options bias the result as much as the question stem.

- **Unbalanced scales.** Response options skewed toward one pole (e.g., _Excellent / Very good / Good / Fair_) push answers positive. Balance them around a neutral center.
- **The midpoint problem.** A neutral midpoint ("Neither agree nor disagree") gives respondents a low-effort escape and can hide real signal; removing it forces a lean but may manufacture opinions where none exist. The decision is deliberate, not default. A worse, subtler failure is **silent redefinition** of the midpoint — relabeling the middle option (e.g., from "Neutral" to "Somewhat agree") quietly shifts what the whole scale means and makes responses non-comparable across versions.
- **Number of points.** Too few points lose resolution; too many exceed people's ability to discriminate. Common practice is 5- or 7-point scales for Likert-type items; whatever you pick, keep it consistent across the instrument.
- **Order effects** (Pew). The order of _answer options_ and of _questions_ both move results. For closed-ended items, Pew documents **contrast effects** (an item read in light of the prior one diverges) and **assimilation effects** (it converges); and a closed-ended question placed before an open-ended one **primes** the concepts respondents then volunteer. Randomize option order where feasible, and sequence questions general-to-specific so early specifics don't contaminate later generals.

## Sampling: where surveys quietly break

A perfectly worded survey on the wrong sample is still wrong — and sampling error is invisible in the results, which is what makes it dangerous.

- **Coverage / sampling frame.** You can only survey people you can reach. An in-app survey reaches _current, active_ users and structurally cannot hear from people who churned, never signed up, or were never aware — exactly the people whose answers you often most need.
- **Non-response & self-selection bias.** The people who _choose_ to answer differ systematically from those who don't — often the most delighted and the most furious, with the indifferent middle silent. A 4% response rate skewed to enthusiasts can read as glowing PMF while the silent majority drifts away.
- **Survivorship.** Surveying only retained users (the survivors) to ask "is the product working?" omits everyone for whom it didn't — the population that would answer "no."
- **Sample size vs. representativeness.** A large sample reduces _random_ error (margin of error) but does **nothing** to fix _systematic_ bias from a skewed frame — 50,000 responses from a self-selected pop-up are still a self-selected pop-up. Representativeness beats raw N.
- **Leading recruitment.** How you invite people biases who shows up: "Help us improve the feature you love!" recruits a different population than a neutral invitation.

## When surveys lie (the summary)

A survey produces a comforting lie, not the truth, when **any** of these holds — and a discovery rubric should treat each as a defect:

1. It asks about **future behavior or intent** ("would you use / pay") and the result is read as a forecast.
2. The **questions are leading, loaded, or double-barreled**, so the wording manufactured the answer.
3. The **scale is unbalanced** or its midpoint was silently redefined.
4. The **sample is self-selected or coverage-limited** and the result is generalized to the whole population.
5. It is used to discover **why** or to find **unknown problems** — jobs that require qualitative work.
6. **N is large but the frame is biased**, and size is mistaken for validity.

## The one survey worth memorizing: the Sean Ellis PMF test

The most useful product survey is also among the simplest. Sean Ellis (who led growth at Dropbox, LogMeIn, and Eventbrite, and coined "growth hacking") arrived at it by **reversing the usual satisfaction question** — instead of asking whether people _like_ a product (which invites polite, inflated answers), he asked how they would feel to _lose_ it, which forces a more honest, visceral answer.

**The question:** _"How would you feel if you could no longer use [product]?"_ with three options:

```text
  ○ Very disappointed
  ○ Somewhat disappointed
  ○ Not disappointed (it isn't really that useful)
  [+ "What type of people do you think would most benefit from [product]?"]
  [+ "What is the main benefit you receive from [product]?"]
  [+ "How can we improve [product] for you?"]
```

**The benchmark:** Ellis benchmarked roughly 100 startups and found a leading indicator — **products where ≥ 40% of users say "very disappointed"** tend to have product-market fit and grow relatively easily; below ~25%, companies struggle to grow at all. The 40% line is an empirical rule of thumb from his sample, not a law of nature — treat it as a directional threshold, not a guarantee.

**Who to ask (this is the part teams get wrong):** survey only **recent, active users** — Vohra's operationalization at Superhuman: people who used the product _at least twice in the last two weeks_ — so you measure people who actually experienced it, not curious sign-ups. Results become directionally stable around **~40 respondents**.

**Superhuman's refinement** turns the metric into an engine: **segment the "very disappointed" users**, distill them into a _High-Expectation Customer_ (HXC) profile from their own self-descriptions, **ignore "not disappointed" feedback entirely**, and mine the _"somewhat disappointed"_ users whose desired benefit matches the product's strength for the roadmap. Vohra then split effort ~50/50 between deepening what fans love and converting the on-the-fence segment, re-surveyed continuously, and moved Superhuman's score from 22% → 33% → 58% across three quarters. The PMF question even illustrates _good_ survey design: it sidesteps acquiescence and politeness by inverting the frame, and it pairs the closed metric with open-ended "why" follow-ups.

## Rigorous vs. weak (scoring rubric)

| Axis | Rigorous | Weak |
| --- | --- | --- |
| **Question fit** | Sizes a _known_ attitude across a population. | Used to discover _why_ or to predict behavior from intent. |
| **Wording** | Neutral, single-barreled, no presuppositions; construct-specific options. | Leading, loaded, or double-barreled; agree/disagree everywhere. |
| **Scales** | Balanced, consistent point count, deliberate midpoint choice. | Unbalanced, drifting/relabeled midpoints, inconsistent scales. |
| **Order** | Questions general→specific; option order randomized where possible. | Earlier items prime later ones; fixed leading option order. |
| **Sample frame** | Defined target population; coverage of churned/non-users where relevant. | In-app only, generalized to everyone; churned users unheard. |
| **Self-selection** | Non-response bias acknowledged; neutral recruitment. | Enthusiast-skewed responders read as the whole base; leading invite. |
| **N vs. validity** | Representativeness prioritized; MoE reported honestly. | Large biased N treated as proof. |
| **Intent vs. behavior** | Self-reported future/past treated as imperfect estimate. | "Would you pay?" read as a revenue forecast. |
| **PMF survey (if used)** | Recent active users, ≥~40 responses, "very disappointed" tracked + open follow-ups. | Whole list incl. inactive sign-ups; "very disappointed" %=PMF declared and forgotten. |

## Note on sourcing (labeled)

The wording, order-effect, and acquiescence guidance is from **Pew Research Center's** survey-methodology materials — a public-opinion-research authority; the principles are well established across the survey-methods literature. The PMF test is **practitioner** material: Ellis's own blog/Medium posts and Vohra's First Round essay. The **40% threshold and the ~40-respondent floor are heuristics from a single practitioner's benchmarking and one company's case**, not validated constants — flagged here as such; use them as directional, and re-derive your own threshold as your sample grows. The origin detail (Ellis reverse-engineering the question after LogMeIn / at "Xobni") comes from secondary interviews and is reported as biography, not load-bearing method.
