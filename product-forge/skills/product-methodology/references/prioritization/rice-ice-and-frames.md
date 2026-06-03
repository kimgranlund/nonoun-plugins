---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Sean McBride, \"RICE: Simple prioritization for product managers.\" Intercom blog, 2018. https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/"
  - "Sean Ellis, ICE Score framework, as used at LogMeIn/Dropbox/GrowthHackers and described in Sean Ellis & Morgan Brown, *Hacking Growth* (Crown Business, 2017)."
  - "Gary Klein, \"Performing a Project Premortem.\" *Harvard Business Review*, September 2007. https://hbr.org/2007/09/performing-a-project-premortem"
  - "Deborah J. Mitchell, J. Edward Russo, Nancy Pennington, \"Back to the future: Temporal perspective in the explanation of events.\" *Journal of Behavioral Decision Making* 2(1), 1989 (prospective hindsight)."
---

# RICE, ICE, and how to frame a prioritization decision

Scoring frameworks rank a backlog; they do not produce judgment. RICE and ICE are useful because they force a few honest estimates into the open and make items comparable — and dangerous because a tidy number invites teams to stop thinking. This file gives the two canonical frames as their authors defined them, the two _ways of valuing_ a choice (ROI vs. opportunity cost), the risk-surfacing complement (the pre-mortem), and the anti-pattern that swallows all of them — **scoring theater**. It pairs with `doshi-lno.md`, which governs effort _per task once chosen_; RICE/ICE govern _which_ items get chosen at all.

## RICE (Intercom)

RICE was created at Intercom by **Sean McBride** (published on the Intercom blog in 2018) to fix a specific failure: prioritization that drifted toward personal preference, cleverness over impact, and exciting-but-unproven ideas, with no consistent way to compare projects. Four factors, combined into one comparable score:

```text
            Reach  x  Impact  x  Confidence
RICE  =     -----------------------------------
                        Effort

  Reach       how many people/events this affects in a defined time period
              (concrete count: "customers per quarter", "signups per month")
  Impact      how much it affects each one, on a fixed scale:
                3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal
  Confidence  how sure you are of your estimates, as a percentage:
                100% = high, 80% = medium, 50% = low, <50% = "total moonshot"
  Effort      total work in PERSON-MONTHS (whole numbers or 0.5), across all roles
```

The score reads as **"total impact per unit of work."** Two design choices carry the weight. **Impact is a small discrete scale, not a free number** — you pick one of five rungs, which prevents false precision at the input. **Confidence is the integrity check** — it is the explicit place to discount a score you can't back with evidence; a "moonshot" rating below 50% deliberately tanks an exciting-but-unfounded idea so it can't outrank a proven one on enthusiasm alone. RICE earns its keep when Reach and Effort are real counts; it degrades into fiction when they're guesses dressed as data.

## ICE (Sean Ellis)

ICE is the lighter, older frame, created by **Sean Ellis** (who coined "growth hacking") for prioritizing **growth experiments** at LogMeIn, Dropbox, and later GrowthHackers in the early 2010s. Three factors, multiplied — no division, no person-months:

```text
ICE  =  Impact  x  Confidence  x  Ease

  Impact      how much this will move the target metric if it works
  Confidence  how sure you are it will produce the expected result
              (data / past experiments / research > a gut feeling)
  Ease        how quickly and cheaply you can run it
```

ICE is built for **speed and volume** — ranking a large backlog of cheap experiments where the cost of a wrong rank is small and the next test is days away. It deliberately trades RICE's rigor (no Reach term, no effort denominator in real units) for throughput. The two frames suit different regimes: **ICE for high-velocity experimentation** where you'll learn fast and re-rank constantly; **RICE for product-roadmap bets** where Reach matters, Effort is measured in months, and a wrong rank is expensive. Using RICE's machinery on a same-day growth test is over-engineering; using ICE to sequence a year of roadmap is under-powered.

## ROI thinking vs. opportunity-cost thinking

Both frames produce a _ratio_ (value over effort/ease), and ratios share a bias: they reward **quick wins and low-hanging fruit** — high ratio, low _absolute_ impact — because easy things score well on the denominator. This is ROI thinking, and left unchecked it fills a roadmap with comfortable small wins.

The corrective is **opportunity-cost thinking**: the true cost of a choice is the _best alternative you gave up_, not the resources it consumed. Under this lens a high-ROI quick win that crowds out a much larger bet is _expensive_, because its real price is the bigger thing you didn't do. The practical move: after scoring, ask of the top of the list — "what larger bet are these easy wins displacing, and is that trade worth it?" RICE/ICE rank the items in front of you; opportunity cost asks whether the _right_ items are in front of you at all. (This is the same reallocation logic that `doshi-lno.md` applies to effort within a chosen task, lifted to the level of which initiatives make the list.)

## Pre-mortems (the risk complement)

Scoring tells you a bet's expected value; it does not tell you how it fails. The **pre-mortem**, introduced by psychologist **Gary Klein** in _Harvard Business Review_ (September 2007), supplies the missing half. The move: **before committing, assume the project has already failed**, then have the team independently write down every plausible reason why.

```text
Pre-mortem (Klein, HBR 2007):
  1. State the plan as if it just shipped — and FAILED, badly.
  2. Each person privately lists reasons for the failure (independently, to avoid anchoring).
  3. Share, cluster, and feed the surfaced risks back into the plan or the score.
```

Its power is psychological, not procedural. It exploits **prospective hindsight** — the Mitchell/Russo/Pennington (1989) finding that imagining an event _has already happened_ improves people's ability to name its causes by roughly **30%**. The grammatical shift from "what _could_ go wrong" (conditional, defensive) to "what _did_ go wrong" (past tense, licensed to be blunt) gives cover to the team member who privately doubts the plan. Run it _before_ you spend on the highest-scoring bet — it stress-tests whether the score's Confidence was real or wishful.

## The "scoring theater" anti-pattern

The dominant failure mode of every scoring framework: **producing beautiful spreadsheets that yield poor decisions** — the appearance of rigor substituting for the substance. Its symptoms:

- **False precision.** A score of 42.7 ranked above 41.3 implies a confidence the inputs cannot support. Discriminating between Impact 1.7 and 1.8 is theater; the scale was never that sharp. The number's decimals lie about how much you actually know.
- **Garbage in, garbage out.** "80% confidence" based on vibes is fiction, and multiplying it by an invented Reach launders a guess into an "objective" score. What separates a useful RICE/ICE score from a misleading one is **not the math — it's the quality of the evidence behind each variable.** A defensible default: **assume 50% confidence unless you have real evidence to go higher.**
- **Scores worshipped over judgment.** Treating the ranked list as truth rather than as _structured input to a decision_. The frameworks are **relative** scoring aids, not an exact science; the point is to inform the product owner's ordering of the top of the list, not to replace it. When a team can't override a score it knows is wrong, the tool has captured the team.
- **Precision arms race.** Adding factors and decimals to make the model "more accurate" usually adds noise, not signal — more inputs means more guesses to get wrong.

The honest framing: a scoring framework is a **conversation forcer and a bias check**, not an oracle. Its job is to make estimates explicit (so they can be argued) and to stop enthusiasm from outranking evidence (via the Confidence term). The moment the spreadsheet's output is treated as the decision rather than an input to it, you have scoring theater.

## The "is this a decision or a performance?" test

```text
Before you trust a prioritized list, check:

  - Evidence behind the variables?  Is each Reach/Impact/Confidence/Ease backed by data
    or a real prior — or is it a number invented to fill the cell? If the latter, the
    rank is theater. Default Confidence to 50% absent evidence.
  - False precision?  Are you splitting hairs between near-equal scores (42.7 vs 41.3)?
    Treat near-ties as ties; the scale isn't that sharp. Rank into tiers, not a strict order.
  - Override allowed?  If a senior PM looked at the #1 item and said "obviously no," could
    the process accommodate that? If the score is unoverridable, it has captured judgment.
  - Opportunity cost checked?  Are the top items quick wins crowding out a larger bet?
    Price the displaced bet, not just the resources spent.
  - Failure surfaced?  Have you run a pre-mortem on the top bet before funding it, to test
    whether its Confidence was real?
```

Failure modes to watch: ranking on a denominator (Ease/Effort) so the backlog fills with cheap wins; a Confidence column that is always 80% (nobody is discounting anything); decimals presented as if meaningful; and a team that defends the spreadsheet instead of the decision.

## Note on attribution and scope

RICE (Intercom / Sean McBride) and ICE (Sean Ellis) are widely-used industry frames, not academic instruments — included here as the canonical lightweight scorers. The pre-mortem and its 30% prospective-hindsight figure trace to Klein (HBR 2007) and Mitchell/Russo/Pennington (1989) respectively. The opportunity-cost-over-ROI framing and the LNO effort model are treated at length in `doshi-lno.md`; this file cites them as complementary lenses, not as its own contribution.
