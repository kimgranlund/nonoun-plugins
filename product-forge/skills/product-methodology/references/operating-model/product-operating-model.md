---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Marty C., *Inspired: How to Create Tech Products Customers Love*, 2nd ed. (Wiley, 2017)"
  - "Marty C. & Chris Jones, *Empowered: Ordinary People, Extraordinary Products* (Wiley, 2020)"
  - "Marty C., *Transformed: Moving to the Product Operating Model* (Wiley, 2024)"
  - "Marty C., 'The Product Operating Model: An Introduction', Silicon Valley Product Group (svpg.com), 2024"
  - "Marty C., 'Empowered Product Teams', Silicon Valley Product Group (svpg.com)"
---

# Marty C.'s Product Operating Model as a Working Method

Marty C.'s product operating model (POM) is the load-bearing distinction in modern product work: it separates companies that **build features** from companies that **solve problems**. This reference treats the POM not as a thing to admire but as a working method — what to do differently on Monday, and how to tell whether a team or a document is actually operating this way or only saying the words. The conceptual source of truth is Marty C.'s three books (_Inspired_, _Empowered_, _Transformed_) and SVPG; this file compresses them into an applied checklist.

> The model's own framing, restated across SVPG and _Transformed_: the product operating model is **a set of principles, not a process, methodology, or framework.** Any document that hands you a fixed ceremony and calls it "the product model" has already missed the point.

---

## The one distinction: product-led vs feature factory

Everything else descends from a single split. Get this wrong and no amount of process repairs it.

|  | Feature factory (project / IT model) | Product operating model (empowered) |
| --- | --- | --- |
| **What the team receives** | A roadmap of features and solutions to build | A **problem to solve** and the strategic context around it |
| **What "done" means** | The feature shipped on schedule | The **outcome** moved (the problem is measurably less of a problem) |
| **Who decides the solution** | Stakeholders / leadership, up front | The cross-functional team, after discovery |
| **What the team is accountable for** | Output — did you ship what was asked | Results — did it work for customers _and_ for the business |
| **Failure mode** | Ships a lot, moves little; "we delivered everything and nothing changed" | Requires real trust and real talent; fails when leadership delegates problems but not authority |

A "feature factory" is the term for an organization that measures itself by the quantity of features shipped rather than the problems solved. The POM's whole purpose is to escape it. (Note: "feature factory" is widely attributed in the literature to John C.'s 2016 essay of that name; Marty C. adopts the contrast under the labels _feature teams_ vs _empowered product teams_.)

---

## The four principles to apply

These are the principles a team is actually being asked to live by. Treat each as a question you can ask of any team or roadmap.

### 1. Empowerment — give teams problems, not features

The team is **given a problem to solve, not a solution to build**, and is then empowered to find the best solution. The apply-test: read the team's current assignment. If it is phrased as "build X" it is a feature spec; if it is phrased as "reduce Y" or "increase Z for customer-segment W" it is a problem. The first is a feature factory in disguise even when everyone has the word "product" in their title.

### 2. Outcomes over output — set goals for the right thing

Teams exist to **produce outcomes** (a customer problem solved, a business result moved), not output (features shipped). The apply-test, drawn straight from the model: **set goals only for outcomes, never for outputs.** A team whose OKRs are a list of features to ship has encoded the build trap into its own targets. See `build-trap.md` for the same idea from Melissa P.'s angle.

### 3. Sense of ownership — durable teams that own something meaningful

Teams are **durable** (not spun up per project) and own a meaningful slice of the product or customer experience end-to-end. Ownership is what makes accountability for outcomes fair — you cannot hold a team responsible for a result it does not control. The apply-test: if the team is dissolved and reformed every quarter around the project du jour, it has no ownership and cannot be held to outcomes.

### 4. Collaboration — cross-functional, not hand-off

Product, design, and engineering work **together to solve the problem**, side by side, rather than passing a spec down a relay. This is the structural precondition for addressing the four risks early (see `four-big-risks.md`): you cannot de-risk feasibility or usability during discovery if engineers and designers only appear at delivery time.

---

## Strategic context: empowerment is not a blank check

The most common misreading of "empowered teams" is "autonomous teams that do whatever they want." Marty C. is explicit that empowerment is bounded by **strategic context** supplied by leadership: the product vision, the company and product strategy, the team's specific objectives, and the broader business context. Empowerment without strategic context is not empowerment — it is abandonment, and it produces locally optimal features that do not add up to a strategy.

The working formulation: **leadership owns the strategic context (the problems worth solving and why); teams own the solutions (how to solve them).** A team that is handed solutions has no empowerment; a team that is handed no context has no direction.

---

## The three things the model actually covers

_Transformed_ organizes the move to the POM around three dimensions; these map cleanly onto the three competencies an empowered team runs continuously. Use them as the table of contents for "are we doing this."

1. **How to decide what to work on → product strategy.** Identify and prioritize the few problems worth solving, grounded in insight, not in a stakeholder request queue.
2. **How to solve problems → product discovery.** Address the four big risks (value, usability, feasibility, business viability) on cheap prototypes _before_ committing to build. This is where the POM lives or dies; see `four-big-risks.md`.
3. **How to build and deliver → product delivery.** Ship reliably and frequently, instrumented so you can measure whether the outcome actually moved.

A team can be excellent at delivery and still be a feature factory — fast shipping of unvalidated features is the build trap running efficiently. Discovery is the competency that distinguishes the model. (The looser groupings vary by source: SVPG and secondary summaries variously enumerate the model as "principles," "dimensions," or a longer list of functions such as strategic context, goals/metrics, research, discovery, delivery, go-to-market, operations, and culture. The three dimensions above are the most consistently primary-attributable spine; treat the longer enumerations as elaborations of the same idea, not a competing canon.)

---

## How to apply it (and how it goes wrong)

| Lever | Good — operating the model | Bad — cargo-culting it |
| --- | --- | --- |
| **The assignment** | "Reduce first-week churn for new SMB accounts." | "Build an onboarding checklist and a welcome email." |
| **The goal / OKR** | Outcome metric the team can influence (activation rate, retention). | A list of features with ship dates dressed as objectives. |
| **Discovery** | Risks tested on prototypes before build; some ideas killed. | "Discovery" is a sprint where the pre-decided feature gets refined. |
| **Leadership's job** | Supplies vision + strategy + context; coaches; resists dictating solutions. | Supplies the roadmap; asks "is it done yet." |
| **The team** | Durable, cross-functional, accountable for results. | Reassembled per project; accountable only for shipping. |
| **Definition of success** | The problem is measurably smaller. | The feature shipped on time. |

---

## The test: is this team in the model, or only using the vocabulary?

Adopting the language ("empowered," "outcomes," "discovery") is easy and free; adopting the model costs leadership its habit of dictating solutions. Three questions separate the two:

1. **The assignment test.** Is the team's current top item a _problem_ ("move this metric") or a _solution_ ("build this feature")? Solutions handed down = feature factory, regardless of titles.
2. **The kill test.** Name the last idea this team _killed in discovery_ because it failed a risk test. If nothing is ever killed, discovery is theater and the team is validating predetermined features.
3. **The accountability test.** Is the team measured by **outcomes it can influence** or by **output it can guarantee**? A team measured on shipped features will, rationally, become a feature factory.

If the honest answers are "solutions, nothing, output," the org has the vocabulary and not the model. The fix is not more process — it is giving teams problems plus context, and changing what success is measured as.
