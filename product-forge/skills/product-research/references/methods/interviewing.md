---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Rob Fitzpatrick. *The Mom Test: How to Talk to Customers & Learn If Your Business Is a Good Idea When Everyone Is Lying to You*. 2013. Book site: https://www.momtestbook.com/"
  - "Teresa T. *Continuous Discovery Habits: Discover Products that Create Customer Value and Business Value*. Product Talk LLC, 2021."
  - "Product Talk — \"Story-Based Customer Interviews Uncover Much-Needed Context.\" https://www.producttalk.org/2024/04/story-based-customer-interviews/"
  - "Steve Portigal. *Interviewing Users: How to Uncover Compelling Insights*. 2nd ed., Rosenfeld Media, 2023. https://rosenfeldmedia.com/books/interviewing-users-second-edition/"
method: interviewing
phase: discover
domains: [1, 11]
timebox: "30–60 min per interview"
cadence: recurring
participants: [interviewer, participant, notetaker]
inputs: ["a research question", "recruited participants", "a discussion guide"]
produces: "validated user insight — the real need, context, and problem behind what people say"
de_risks: [value, usability]
rubric: rubric-discovery
---

# Customer Interviewing as a Discipline

Customer interviewing is the most over-claimed and under-practiced method in product research. Almost every team says they "talk to users"; very few run interviews that produce evidence rather than reassurance. The failure is structural, not motivational: the default conversation — pitch the idea, ask whether the person likes it, ask whether they'd buy it — is engineered to return a comforting fiction. This reference defines the discipline that prevents that, drawn principally from Rob Fitzpatrick's _The Mom Test_ (the interrogation rules) and Teresa T.'s _Continuous Discovery Habits_ (the cadence and the story-based question form), and gives a rubric a discovery review can score against.

## The core problem: people lie, and they don't know they're lying

The premise of _The Mom Test_ is in its title. If you ask your mother whether your business idea is good, she will say yes — she loves you and does not want to hurt your feelings. Customers do the same thing without realizing it: faced with a founder visibly invested in an idea, they default to politeness, optimism, and helpfulness, and they answer the question they think you want answered. Fitzpatrick's framing is that the problem is not the customer's honesty but **the questions you asked** — bad questions all but force a useless answer, and the burden is on the interviewer to ask questions that "even your mom can't lie to you about."

The deeper mechanism (Teresa T. makes this explicit, citing Kahneman) is cognitive: when people are asked to generalize ("what do you usually do," "would you use this"), they answer fast from **System 1** — automatic, low-effort recall that is cheap but distorted by aspirational bias (people describe their idealized selves), recency, and the availability heuristic. Ask what someone likes to watch and you hear "documentaries" while last night's reality-TV binge goes unmentioned. The interview's whole job is to route around System 1 by anchoring every question in a **specific, datable past event** the person cannot smoothly idealize.

## The Mom Test: three rules

Fitzpatrick reduces good interviewing to three rules. They are about what the **interviewer** does, not the customer.

1. **Talk about their life, not your idea.** The moment you describe your solution, you contaminate the conversation — the customer starts reacting to your pitch instead of describing their world. Done right, "they won't even know you have an idea." Your job is to learn about the customer's problems, goals, workflow, and constraints, not to test reactions to a concept.
2. **Ask about specifics in the past, not generics or hypotheticals about the future.** "Would you use a tool that did X?" and "Do you usually...?" both invite invention. "Tell me about the last time you hit this problem" forces recall of something real. Anything about the future is a prediction, and predictions are fantasy.
3. **Talk less and listen more.** The customer should be doing most of the talking. An interviewer who is explaining, defending, or steering is not gathering data.

## Story-based, not opinion-based

The single most consequential move, on which Fitzpatrick and Teresa T. agree completely, is to **collect specific stories about past behavior, not opinions, generalizations, or predictions.** An opinion is what a person believes about themselves in the abstract; a story is what they actually did on a specific day. Only the second is evidence.

Teresa T.'s worked contrast: ask the generic "what do you like to do?" and you get a thin, idealized summary — _"I like to download shows on my iPhone."_ Open instead with **"Tell me about the last time you watched Netflix"** and you get the usable, contextual thing — _"I downloaded episodes ahead of time so I could watch Breaking Bad on my flight."_ The second answer carries the trigger, the constraint, and the workaround; the first carries nothing you can design against.

```text
                       OPINION-BASED                       STORY-BASED
trigger question   "What do you usually do?"           "Tell me about the last time
                   "Would you use X?"                   you did X."
                   "What do you like/dislike?"          "Walk me through what happened."
returns            a generalization, a prediction,     a specific, datable episode with
                   an idealized summary (System 1)      context, motivation, constraint
verdict            REJECT — not evidence of behavior   USE — this is the unit of discovery
```

The operating rule that follows: **open with a specific instance, then follow that one story from beginning to end** — what was happening just before, what triggered action that day, what they tried, what they abandoned, what they did next. You are reconstructing a documentary timeline, not collecting a satisfaction score.

## Leading and hypothetical questions: the two killers

Two question shapes destroy interviews and recur in nearly every weak transcript.

**Leading questions** embed the answer in the question. "Don't you think it's frustrating when...?" tells the customer the expected response. "How much would you love a feature that...?" presupposes love. The fix is to strip the valence and the solution out: ask "Walk me through the last time you did that" and let the frustration (or its absence) surface on its own. If the pain is real, the customer will volunteer it; if you have to lead them to it, it isn't there.

**Hypothetical / future questions** ask the person to predict their own behavior, which they do badly and optimistically. "Would you pay for this?", "Would you use it weekly?", and "Would you switch?" all return what Fitzpatrick calls _fluff_ — generic, aspirational, free-to-give answers with no predictive value. The replacement is always to convert the hypothetical into history: not "would you pay?" but "what are you paying for this today, and what did it take to get that budget approved?" Past behavior is the only honest predictor of future behavior.

## The three kinds of bad data

Fitzpatrick names three categories of answer that feel like signal and are noise. Recognizing them in real time is the interviewer's core skill.

| Bad data | What it sounds like | Why it's worthless | What to do instead |
| --- | --- | --- | --- |
| **Compliments** | "That's so cool." "I'd totally use that." "Great idea." | Costs the speaker nothing, so it's worth nothing — and a meeting that ends in a compliment is a meeting where you got "friend-zoned." | Deflect it, don't bank it. Steer back to their life and their actual behavior. |
| **Fluff** | Generics ("I usually..."), hypotheticals ("I would..."), and future promises ("I'll definitely..."). | Lives in the realm of the idealized and the imagined, not the real. | Anchor it: "When was the last time that happened? Tell me about it." |
| **Ideas / feature requests** | "You should add X." "It'd be great if it could Y." | Customers are good at naming pain, bad at designing solutions; a request is a symptom, not a spec. | Don't accept at face value — dig for the underlying motivation: "What would that let you do that you can't today?" |

## Commitment and advancement: the test for real interest

Words are cheap; the antidote to compliments and fluff is to look for **commitment** and **advancement**. Commitment means the customer gives up something they value — Fitzpatrick names the three "currencies" as **time, reputation, and money** (a long follow-up meeting, an introduction to their boss, a deposit). Advancement means they move to the next concrete step in your real funnel. A conversation that ends with enthusiasm but no commitment and no advancement was, in his blunt phrasing, a polite rejection. This is the cheapest available test of whether stated interest is real: ask for something costly and watch what happens.

## Continuous, not a phase

Interviewing is not a study you run before building. In Teresa T.'s model it is a **weekly habit held by the team that builds the product** — "at a minimum, weekly touchpoints with customers, by the team building the product." Cadence matters more than batch size: one real conversation every week, indefinitely, beats a thirty-interview blitz once a year, because the blitz validates a bet once and is then defended, while the weekly habit keeps correcting the bet against reality. The practical enabler is to **automate recruiting** so a conversation lands on the calendar every week without a fresh act of will, and to keep each interview small enough to repeat.

## Rigorous vs. weak (scoring rubric)

A discovery rubric can score an interview — or a set of them — on these axes. The left column is what rigorous looks like; the right is the failure mode.

| Axis | Rigorous | Weak |
| --- | --- | --- |
| **Question form** | Specific past instances ("the last time..."), open-ended, neutral. | Hypotheticals ("would you..."), leading ("isn't it annoying..."), yes/no. |
| **Idea exposure** | The customer doesn't know what you're building; questions are about their life. | The interviewer pitches early, then collects reactions to the pitch. |
| **Talk ratio** | Customer talks ~80%+; interviewer mostly follows the story. | Interviewer explains, defends, and sells; customer mostly agrees. |
| **Data harvested** | Concrete episodes, workarounds, what was tried and dropped, costs paid. | Compliments, generalizations, feature requests, predictions. |
| **Bias handling** | Compliments deflected; fluff anchored to a specific time; requests dug into for motivation. | Compliments and "I'd use it" recorded as validation. |
| **Evidence of interest** | A sought, costly commitment (time / reputation / money) and a funnel advancement. | "They loved it" with no commitment and no next step. |
| **Recruiting & cadence** | Standing weekly contact with real users; the makers are in the room. | A one-off batch; a researcher hands over a report the makers never witnessed. |

## Note on scope and lineage (labeled)

This file covers the _discovery / generative_ interview — open exploration of a person's world to find problems worth solving. It is distinct from, and should not be conflated with, two adjacent practices: the **JTBD switch interview** (Moesta / Re-Wired Group — a structured reconstruction of one purchase decision; see `jtbd-discovery.md`), and the **moderated usability test** (observing a person attempt tasks with a prototype — a _behavioral_ method; see `behavioral-vs-attitudinal.md`). _The Mom Test_ is a practitioner book by a startup founder, not peer-reviewed research; its rules are widely adopted craft heuristics, and the System-1 mechanism Teresa T. invokes is grounded in Kahneman's _Thinking, Fast and Slow_. Steve Portigal's _Interviewing Users_ is the fuller craft reference for moderation technique (rapport, silence, the "uncomfortable pause") and is cited here as the deeper treatment of the interviewer's behavior in the room.
