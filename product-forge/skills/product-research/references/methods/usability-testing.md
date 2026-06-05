---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Steve K. *Rocket Surgery Made Easy: The Do-It-Yourself Guide to Finding and Fixing Usability Problems*. New Riders, 2009. https://sensible.com/rocket-surgery-made-easy/"
  - "Jakob N. (NN/g). \"Why You Only Need to Test with 5 Users.\" 2000. https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/"
  - "NN/g. \"Thinking Aloud: The #1 Usability Tool.\" https://www.nngroup.com/articles/thinking-aloud-the-1-usability-tool/"
  - "Jakob N. (NN/g). \"Severity Ratings for Usability Problems.\" https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/"
method: usability-testing
phase: make
domains: [2, 3, 5, 6]
timebox: "½ day (3–5 sessions) + analysis"
cadence: recurring
participants: [facilitator, "3–5 representative users (one at a time)", "the team as observers"]
inputs: ["something to test (prototype, build, or live site)", "real task scenarios (not questions)", "a screener for representative users"]
produces: "the top usability problems, prioritized by severity"
de_risks: [usability]
rubric: rubric-ux-quality
---

# Usability Testing — watch 5 people try the real task, fix what breaks

A **moderated think-aloud test** (Steve K. / NN/g): recruit a few representative users, give them real task scenarios, have them narrate their thoughts while they attempt the tasks, and **observe in silence** — then fix the most serious problems and run it again. It is the cheapest honest answer to one question: _can a real person actually use this?_ The method is behavioral, not attitudinal — it watches what people **do**, because what they **say** they'd do is unreliable (see `behavioral-vs-attitudinal.md`). The output is not a satisfaction score; it is a ranked list of the problems that stop people, with the worst ones fixed.

## When to run it · when NOT

**Run it** when you have something a user can attempt — a prototype, a staging build, or a shipped flow — and you need to know where real people get stuck _before_ committing more build. It de-risks **usability** specifically (Marty C.'s "can the user actually figure out how to use it?"), and it is the canonical close-the-loop move after a design decision: cheap, fast, recurring, run on whatever fidelity you have. **Do NOT run it** to answer a _value_ question ("do they want this at all?" — that's discovery interviewing, `interviewing.md`, or a design sprint's test) or a _how-many_ question ("which variant converts?" — that's an A/B test, a quantitative behavioral method). Five think-aloud users tell you _why_ a task fails and _where_; they cannot tell you _how many_ users it affects in aggregate. Don't use it to settle a preference debate ("do people like the blue?") — that's an attitudinal/desirability question a task-success test can't measure. And don't run it with no real task — a demo you narrate _to_ the user is a sales pitch, not a test.

## The run (one session, repeated 3–5×)

| # | Step | Who | Timebox | Output |
| --- | --- | --- | --- | --- |
| 1 | **Recruit & screen** — find people representative of real users (a screener, not whoever's nearby); Steve K.'s stance is "recruit loosely, grade on a curve" — close-enough beats waiting | facilitator | ahead of the day | 3–5 booked sessions, one per slot |
| 2 | **Set the room** — the participant + one facilitator; the team watches on a separate screen/stream and takes notes; record screen + audio with consent | facilitator | 5 min/session | a watching team, a recording |
| 3 | **Warm up & set expectations** — reassure: "we're testing the _site_, not you; there are no wrong answers; if something's confusing that's our fault" — to defeat the politeness reflex | facilitator | 5 min | a participant who'll be honest |
| 4 | **Give a task scenario, then shut up** — hand them a realistic _task_ ("buy a ticket to a show next Friday under \$50"), never a leading question ("do you find this easy?"); ask them to **think aloud** — narrate what they see, expect, and try | facilitator → participant | ~30 min/session | observed attempts + a running narration |
| 5 | **Observe, don't help** — bite your tongue; let them struggle so the problem reveals itself; nudge only with neutral, non-leading prompts ("what are you trying to do now?", "what did you expect?") and never point at the answer | facilitator | (within step 4) | unaided behavior — the actual data |
| 6 | **Debrief the team** — straight after each session (or at day's end), the watchers compare notes; the strongest signal is the problem **multiple** users hit at the **same** place | team | 10 min | a shared list of observed problems |
| 7 | **Rank by severity & fix the worst** — rate each problem (NN/g: frequency × impact × persistence), then fix the few most serious _before_ chasing the long tail; re-test next round | team | analysis | the top problems, prioritized → fixes |

## Roles

A **facilitator** (one person — sets tasks, keeps the participant thinking aloud, and **stays neutral**: asks, never leads, never rescues). **3–5 representative users**, run **one at a time** (a usability test is 1:1; a room of users is a focus group, a different and weaker instrument for this question). The **team as observers** — designers, PM, engineers watching live: the witnessing is half the value, because a problem a maker _sees_ a user hit lands far harder than the same problem in a report they didn't watch (the maker-in-the-room principle, shared with `interviewing.md`). Steve K.'s whole framing is that anyone on the team can facilitate — this is DIY, not a specialist's ritual.

## Failure modes

- **Leading the witness** — "Was that easy?" / "You'd click here, right?" telegraphs the answer; the participant obliges and the data is worthless. Tasks and prompts must be neutral; the test is of the _design_, not the user.
- **Helping** — the facilitator rescues a stuck user, and the exact problem you were there to find evaporates. Silence is the method. If they're stuck, that _is_ the finding.
- **Asking instead of watching** — collecting opinions ("would you use this?", "do you like it?") turns a behavioral test into an attitudinal one; self-report on one's own behavior is unreliable (`behavioral-vs-attitudinal.md`). Watch what they do; weight that over what they say.
- **Unrepresentative recruits** — testing with teammates, or people who'd never be users; they share your context and can't hit the problems a real first-timer will.
- **Listing problems but fixing none** — a ranked list nobody acts on is theater. The loop is _find → fix the worst → re-test_; without the fix-and-repeat, you ran a study, not a method.
- **Drowning in the long tail** — recording 40 nitpicks and treating them as equal. Severity-rank; the few serious blockers earn the budget, the cosmetic ones wait.
- **Mistaking it for a value test** — a smooth task run proves the thing is _usable_, not that anyone _wants_ it. Usability ≠ desirability; don't read adoption into task success.

## A good run vs. a bad run

|  | Bad run | Good run |
| --- | --- | --- |
| The prompt | a leading question ("isn't this simple?") | a realistic task scenario, neutrally posed |
| The facilitator | explains, defends, rescues | sets the task and goes quiet |
| Participants | teammates / friends, in a group | 3–5 representative users, one at a time |
| What's collected | opinions, compliments, a satisfaction rating | observed behavior — where they stalled, mis-clicked, gave up |
| The output | a long flat list of everything | the top problems, severity-ranked, worst ones fixed |
| The team | reads a report later | watched it happen, live |

**The single test:** name the most serious problem the session surfaced and the fix you shipped because of it. If the answer is "users said they liked it," you ran a satisfaction survey, not a usability test — you measured an attitude where you needed a behavior.

## Hand-off

The ranked problem list flows into the build: the top usability problems become fixes in the surface under test, and the run **scores against `rubric-ux-quality`** — its task-completion gate (can a representative user finish unaided?) is precisely what a think-aloud session measures, and its error-prevention, empty-state, and pattern-fit lenses name the problem _types_ to watch for. Because the method spans **Experience Architecture, the Interaction Model, Content & Communication, and the Interface System** (domains 2·3·5·6), a finding may route to whichever of those owns it. A problem that turns out to be a _value_ failure (they completed the task but wouldn't use it) routes back to discovery (`interviewing.md`, or the opportunity-solution tree in `product-methodology`). The fix-and-re-test cadence is the point: each round is cheap, so run it per-design, recurring — not once.

## Sourcing

The DIY think-aloud protocol — loose recruiting, real task scenarios, observe-don't-help, fix-the-worst-and-repeat — is Steve K.'s _Rocket Surgery Made Easy_ (New Riders, 2009), the practitioner standard, alongside NN/g's _Thinking Aloud: The #1 Usability Tool_. The small-_n_ rationale is **Jakob N.'s guidance**, not a measured law: in _Why You Only Need to Test with 5 Users_ (NN/g, 2000), Jakob N. argues — from a mathematical model he and Tom Landauer derived — that about **five users typically surface the large majority (~85%) of a design's usability problems**, with steeply diminishing returns after that, so testing a few users and iterating beats one big study. Treat that figure as Jakob N.'s modeled estimate and the basis for the iterate-in-small-rounds posture — _not_ a hard guarantee that five users find a fixed fraction of problems in any given test (it varies with the design and the tasks; Jakob N.'s own counsel is to run more, smaller rounds rather than one large one). Severity rating (frequency × impact × persistence) is NN/g's _Severity Ratings for Usability Problems_. This is a behavioral, qualitative, scripted-use method in the NN/g taxonomy (`behavioral-vs-attitudinal.md`); it is distinct from the discovery interview (`interviewing.md`) and the survey (`survey-design.md`), and complementary to them.
