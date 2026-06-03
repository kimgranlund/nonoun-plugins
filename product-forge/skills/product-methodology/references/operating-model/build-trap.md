---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Melissa P., *Escaping the Build Trap: How Effective Product Management Creates Real Value* (O'Reilly, 2018)"
  - "Melissa P., 'The Product Kata', melissaperri.com, 2015"
  - "Mike Rother, *Toyota Kata* (McGraw-Hill, 2009) — the improvement-kata source Melissa P. adapts"
---

# Melissa P.'s Build Trap

Melissa P.'s _Escaping the Build Trap_ (2018) names the most common organizational failure in product work: **measuring value by the number of things you produce instead of by the outcomes those things create.** A team in the build trap can be busy, on schedule, and shipping constantly while creating no value. This reference defines the trap, the value-exchange idea that explains it, the Product Kata that climbs out of it, and the outcome-orientation test for spotting the trap in a team or a document.

> Melissa P.'s core line, paraphrased: companies get stuck in the build trap when they **measure their success by outputs rather than outcomes** — by features shipped, not problems solved.

---

## Outputs vs outcomes: the definition

The trap is a confusion between two things that are easy to conflate because output is so much easier to count.

- **Output** — the stuff you ship: features, releases, story points, projects completed. Easy to measure, easy to celebrate, easy to put on a roadmap.
- **Outcome** — the change in customer or business behavior that the output was supposed to cause: the problem actually solved, and therefore the business result earned.

The build trap is the state of **mistaking output for outcome** — treating "we shipped 40 features this year" as if it were "we created value." Output is only a means; the outcome is the end. A team optimizing output will, rationally, ship more features faster — which makes the trap _worse_, not better, because it accelerates the production of things nobody needed.

---

## The value exchange: why output ≠ value

Melissa P. grounds the trap in a simple model of why a company exists at all: the **value exchange.** A company offers a product or service that helps a customer with a real problem, want, or need; in return the company captures some of that value back (revenue, retention, growth). Value flows both ways or the exchange breaks.

The decisive point: **the customer only realizes value when their problem is actually solved** — not when a feature ships. Shipping is the company's activity; value is the customer's experience. A feature that ships but solves nothing is pure cost on the company's side of the exchange and zero value on the customer's. This is why output is a treacherous proxy: it measures the company's effort, not the customer's outcome, and the two routinely diverge. Business outcomes (more sales, retention, growth) follow only _after_ the customer's problem is solved — never directly from the act of shipping.

---

## The Product Kata: the way out

To replace "build more" with "learn, then build what's needed," Melissa P. adapts the **improvement kata** from Mike Rother's _Toyota Kata_ (itself a model of Toyota's continuous-improvement practice) into the **Product Kata** — a repeatable problem-solving routine that forces a team to understand reality before committing to a solution. It is run as a loop, not once.

The kata cycles through these questions:

1. **Where are we trying to get to?** — the direction: the vision and the business objective we are serving.
2. **Where are we now?** — the current condition, stated from _actual data_, not assumption. (Melissa P.'s worked example: the team assumed sellers called four times a week; the real number was seven. Skipping this step is where teams "jump in without making the current condition very clear.")
3. **What is the next target condition / goal?** — the next incremental, measurable step toward the direction.
4. **What obstacle is now in our way?** — the single biggest thing blocking the next target condition.
5. **What is the next step, and what do we expect to learn?** — the smallest experiment (ideally under a week) to tackle that obstacle, with the expected learning stated _in advance_ so reality can contradict it.

The kata's whole purpose is to **fall in love with the problem, not the solution** — to make learning an explicit, non-skippable step. As Melissa P. puts it, learning is one of the most important parts of the product cycle, and too often we skip over these steps. Each loop produces evidence; evidence redirects the next loop. (Note: secondary summaries sometimes collapse this into "four steps" by merging the target-condition and next-step questions; Melissa P.'s own account runs through direction, current condition, target condition, obstacle, and next step. The five-question form above follows her primary source.)

---

## How to tell a team or a document is in the trap

The build trap hides behind activity and good intentions. Diagnostic tells:

| In the trap | Out of the trap |
| --- | --- |
| Roadmap is a **list of features with dates** | Roadmap is a list of **problems / outcomes to pursue** |
| Success reported as **"we shipped X"** | Success reported as **"metric Y moved because the problem shrank"** |
| Goals / OKRs are **outputs** ("launch the redesign") | Goals are **outcomes** ("raise activation from A to B") |
| Current condition asserted from **assumption** | Current condition stated from **observed data** |
| Discovery (if any) **confirms** the pre-chosen feature | Discovery can **invalidate** the idea and redirect |
| Roadmap measured by **% delivered on time** | Work measured by **problems solved / value created** |
| PM is a **project manager / feature-ticket writer** | PM owns the **problem and the outcome** end to end |

A document is in the trap when it specifies _what to build_ and _by when_ but never states _which outcome it must move_ or _how we will know it worked_. The smell is a feature list with no falsifiable success metric attached.

This is the same failure Marty C. attacks from the operating-model side: a feature factory is the organizational form of the build trap, and "set goals only for outcomes, never outputs" is the same prescription in different words (see `cagan-operating-model.md` and `four-big-risks.md`).

---

## The outcome-orientation test

The single test for whether a team, a roadmap, or a PRD has escaped the trap:

1. **The metric test.** For each planned item, name the **outcome metric** it must move and the **target value**. If the only answer is "ship it," it is output, and the item is in the trap. Outcomes are stated as a measurable change; outputs are stated as a deliverable.
2. **The data test.** Is the current state described from **observed data** or from **assumption**? A plan whose "current condition" is a guess (the four-vs-seven error) cannot set a real target — it is building on a story, not a baseline.
3. **The invalidation test.** Could the next step **prove the idea wrong**, and is the team willing to drop it if so? If the experiment can only confirm the plan, the team has fallen in love with the solution and is not running the kata — it is decorating a decision already made.
4. **The success-definition test.** Replace every "done when shipped" with "succeeded when [outcome] reaches [value]." Whatever cannot be rewritten that way is output masquerading as progress.

If a plan cannot attach a falsifiable outcome metric to its items, cannot ground its baseline in data, and cannot be proven wrong by its own next step — it is in the build trap, no matter how full and well-organized the roadmap looks.
