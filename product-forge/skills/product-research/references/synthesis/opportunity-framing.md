---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Teresa T. — Opportunity Solution Trees: Visualize Your Discovery to Stay Aligned and Drive Outcomes (producttalk.org/opportunity-solution-trees)"
  - "Teresa T. — Opportunity Mapping: An Essential Skill for Driving Product Outcomes (producttalk.org/2020/07/opportunity-mapping)"
  - "Teresa T. — Opportunity Solution Tree (glossary) (producttalk.org/glossary-discovery-opportunity-solution-tree)"
  - "Teresa T., Continuous Discovery Habits: Discover Products that Create Customer Value and Business Value (Product Talk LLC, 2021)"
  - "IDEO.org Design Kit — How Might We (designkit.org/methods/how-might-we)"
  - "Interaction Design Foundation — What is How Might We (HMW)? (interaction-design.org/literature/topics/how-might-we)"
  - "NN/g — Customer Journey Maps: When and How to Create Them (nngroup.com/articles/customer-journey-mapping)"
---

# Opportunity Framing: Turning Insights Into Opportunities

Research produces _insights_; a roadmap needs _opportunities_. Opportunity framing is the synthesis move in between — taking what people said and did and restating it as a set of customer needs the team can choose to address. Frame it well and the opportunity drops cleanly into an opportunity-solution tree and survives prioritization. Frame it badly and you have either smuggled a solution into the research or written something too vague to act on. This reference defines what an opportunity is, the rules for framing one, the How-Might-We reframe that opens it for ideation, and how a well-framed opportunity feeds the tree.

> The core distinction, in Teresa T.'s terms: an opportunity is _a customer need, a customer pain point, or a customer desire_ — it arises from _"gaps between what they expect and how the world works."_ It is emphatically **not** a solution. "Reduce time spent searching for a show" is an opportunity; "add a recommendation carousel" is one solution to it. The entire value of framing is keeping those two things in separate layers.

---

## What qualifies as an opportunity

Teresa T.'s test for an _actionable_ opportunity is specificity along four axes. A good opportunity is **specific**, occurs at a **specific moment in time**, occurs in a **specific context**, and is experienced by a **specific customer**. The opposite — a vague wish — is the most common framing failure.

| Axis | Vague (reject) | Specific (use) |
| --- | --- | --- |
| **Moment in time** | "I wish this were easier to use" | "When I opened the app on the plane with no signal, I couldn't find my downloaded episode" |
| **Customer** | "Users want more control" | "A power user managing multiple accounts wants to switch without re-logging in" |
| **Context** | "Onboarding is confusing" | "A first-time user, on mobile, can't tell which step they're on during setup" |
| **Phrasing** | A feature in disguise | A need expressed as a need |

Teresa T.'s warning about over-broad framing is precise: when customers say vague things like _"I wish this was easier to use,"_ it _"opens the door to all usability improvements"_ — the opportunity is so wide it constrains nothing and prioritizes nothing. The fix is to anchor it to a moment: re-frame to _"a specific moment in time from customer stories."_ A single rich interview story, Teresa T. notes, _"might elicit dozens of opportunities"_ — the synthesis work is decomposing that broad wish into the specific moments hiding inside it.

---

## The four framing rules

1. **Frame the need, never the solution.** This is the load-bearing rule. The whole point of the opportunity layer is to hold the _problem_ stable while the team explores many solutions. The moment an "opportunity" names a feature, the solution space has been collapsed before it was explored.
2. **Use the customer's perspective and language.** Opportunities should reflect how customers think about their own world, drawn _"directly from customer interviews and their language patterns."_ An opportunity written in internal product jargon is a tell that the team, not the customer, authored it.
3. **Anchor to a specific moment.** Tie the need to a datable instance from a real story (the constraint that defeats vagueness). "On the plane, offline" is actionable; "on the go" is not.
4. **Apply the disguise test.** If there is only _one_ conceivable way to address the thing, it is a **solution wearing an opportunity costume** — file it in the solution layer. A genuine opportunity is a need broad enough to admit several different solutions, yet specific enough to point at a real moment. This is the single fastest filter for separating the two layers.

> **The disguise test in one line.** Ask: _"Can I think of at least three different solutions to this?"_ If yes, it is an opportunity. If the only answer is the feature you already had in mind, you wrote a solution and disguised it as a need.

---

## How-Might-We: the reframe that opens an opportunity for ideation

Once an opportunity (a need or pain) is framed, **How-Might-We (HMW)** converts it from a stated problem into an open invitation to solve. IDEO.org's Design Kit positions it exactly there: _"By framing your challenge as a How Might We question, you'll set yourself up for an innovative solution."_ Mechanically, you _"start with insight statements and rephrase them by adding 'How might we' at the beginning."_

Each word does work (per IDEO's design-thinking framing): **"How"** assumes a solution exists; **"Might"** signals that some ideas will work and some won't, and that's fine; **"We"** makes it a collaborative build. The result _"suggests that a solution is possible"_ while leaving room to _"answer them in a variety of ways."_

A widely-taught structure (Interaction Design Foundation) gives the reframe a fill-in form:

```text
How might we [action verb] for [specific user] so that [desired outcome]?

insight   →  "Travelers can't access their content when they lose signal mid-trip."
HMW       →  "How might we let a traveler keep watching for a user who goes offline
              so that losing signal doesn't interrupt the show?"
```

**The Goldilocks scope rule.** IDEO's central caution is calibration: _"A properly framed How Might We doesn't suggest a particular solution, but gives you the perfect frame for innovative thinking."_ Too narrow and the HMW is a solution in disguise (_"How might we add an offline-download button"_ — that's the answer, not the question); too broad and it constrains nothing (_"How might we make travel better"_). A good HMW gives _"both a narrow enough frame to let you know where to start your Brainstorm, but also enough breadth to give you room to explore wild ideas."_ If a HMW admits only one idea, broaden it; if it admits anything at all, narrow it.

| HMW failure | Example | Fix |
| --- | --- | --- |
| **Too narrow (solution baked in)** | "How might we add a download button?" | Strip the solution: "How might we let travelers watch without a connection?" |
| **Too broad (constrains nothing)** | "How might we delight users?" | Anchor to the moment and outcome from the insight |
| **Negative framing** | "How might we stop users from churning at setup?" | Flip to the positive opportunity behind it |

---

## How a framed opportunity feeds the opportunity-solution tree

Opportunity framing is not a standalone deliverable — it is the step that populates the **middle layer** of Teresa T.'s opportunity-solution tree (the visual model for _"the paths you might take to reach a desired outcome"_). The tree has four layers: an **outcome** at the root, **opportunities** beneath it, **solutions** under each opportunity, and **assumption tests** at the bottom. Framing produces the opportunity layer, and frames it well enough that the layers above and below can attach.

```text
            OUTCOME              ← the product outcome the tree exists to move
          ┌────┴────┐
       OPP A     OPP B           ← framed opportunities  (the output of this skill)
      ┌──┴──┐
   SOL 1  SOL 2                  ← HMW opens each opportunity to several solutions
```

Two structural payoffs depend entirely on framing quality:

- **Opportunities are compared as a space before any is chosen.** Teresa T.'s first move on an outcome is to _"compare and contrast the opportunity space"_ — to ask _"what opportunities are available and what customer needs, pain points, and desires should be addressed."_ That comparison only works if each entry is a real, distinct need; solutions-in-disguise can't be weighed against each other on customer importance.
- **Connected edges expose off-strategy work.** Because every solution must trace up through an opportunity to the outcome, a feature with no opportunity above it has nowhere to attach — the tree reveals it as off-strategy by construction. A badly framed opportunity (a solution in a need's clothing) breaks this guarantee: it lets a pre-chosen feature masquerade as a validated need.

The hand-off, in sequence: **research insight → framed opportunity (need, specific, customer's words) → placed in the opportunity space → selected → opened with a HMW → solutions explored.** Frame the opportunity wrong and every downstream step inherits the error.

---

## Good framing vs. bad framing

| Dimension | Well-framed opportunity | Badly-framed |
| --- | --- | --- |
| **Layer** | A need, in the opportunity layer | A feature smuggled into the opportunity layer |
| **Specificity** | A specific moment, customer, and context | "Easier," "better," "more control" |
| **Authorship** | The customer's words, from a story | Internal jargon; written in a planning meeting |
| **Disguise test** | Admits several distinct solutions | Has exactly one obvious solution (it _is_ the solution) |
| **As a HMW** | Opens to many ideas; right-sized scope | Either names the answer or constrains nothing |
| **On the tree** | Attaches cleanly; can be compared and prioritized | Lets a pre-decided feature pose as a validated need |

> **The synthesis discipline.** Framing is where confirmation bias most easily enters discovery: it is tempting to "frame" the opportunity that happens to justify the feature you already wanted to build. The guard is the customer's own words and a specific moment — an opportunity you can quote from a real story, anchored to a datable instance, is hard to fake. If you cannot point to the interview moment an opportunity came from, you invented it.
