---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Colin Bryar and Bill Carr, *Working Backwards: Insights, Stories, and Secrets from Inside Amazon* (St. Martin's Press, 2021). ISBN 978-1-250-26796-3."
  - "Working Backwards LLC (Bryar & Carr), *The Amazon Working Backwards PR/FAQ Process*. https://workingbackwards.com/concepts/working-backwards-pr-faq-process/"
  - "Colin Bryar & Bill Carr, *Amazon Narratives — Memos, Working Backwards from Release, More*, a16z podcast (interview). https://a16z.com/podcast/amazon-narratives-memos-working-backwards-from-release-more/"
---

# Working Backwards: the PR/FAQ

Amazon's Working Backwards method, documented by Colin Bryar and Bill Carr (who spent a combined 27 years inside the company, Bryar as one of Bezos's early "shadows," Carr as the VP who launched much of digital media), inverts the normal order of product development. Instead of starting from what the team can build and reasoning forward to a launch, you **start by writing the launch announcement and work backwards from the customer experience it describes**. The central tenet, in the authors' words: "Start with the customer and work backwards." This reference covers the artifact that operationalizes it — the **PR/FAQ**, short for press release / frequently asked questions — and how it bridges into a PRD. The formal document-authoring engines (`plan-prd`, `plan-spec`) are global peer skills; this reference explains the Amazon method that often _feeds_ such a document, not how to render one.

## Why the press release goes first

Bryar and Carr describe the origin as trial-and-error: the team "eventually landed on the idea of writing a press release and a series of frequently asked questions (FAQs) to describe each new product." The insight is that "normally, writing a press release is the last step in launching a new product" — and writing it _first_ is "a forcing function to ensure that the creator of the new product idea is focused on the customer."

The mechanism is psychological and unforgiving. When you write a real launch announcement, you are "laser-focused on describing your product so that when a potential customer reads about it in the press, they will be excited and compelled to buy it." You cannot hide a weak idea inside a press release. If the customer benefit is thin, the headline is limp; if you do not know who the customer is, the announcement has no one to address; if the product is a "skills-forward" project (built because the team _can_, using existing expertise) rather than a customer-need project, the press release reads as a feature brag with no one cheering. The format exposes exactly the weaknesses an internally-framed spec lets you skate past.

This is also why the method explicitly favors **velocity over speed**. Bryar and Carr distinguish the two: "you want speed if you want to go fast but don't care about the direction or destination ... to reach a specific destination, you want velocity." AWS, they note, had roughly a two-year pre-launch planning period — the upfront clarity from working backwards bought faster execution later, not slower.

## The PR — what the press release contains

The press release is short (target ~one page) and written in plain, customer-facing language — no internal jargon, no "synergies." Its components, per the Working Backwards process:

| Component | What it does |
| --- | --- |
| **Heading** | Names the product in language the customer would use, not the internal codename. |
| **Subheading** | Names the **specific customer segment** and the benefit — because, in the authors' framing, "if you think your product is for everyone, you are mistaken." |
| **Summary paragraph** | Dateline (location, outlet, launch date) plus a crisp overview of the product and its primary benefit. |
| **Problem paragraph** | The customer's pain, stated **from the customer's point of view** — and scoped to a problem with enough total addressable market to matter. |
| **Solution paragraph(s)** | How the product solves it, including honest acknowledgment of what customers use today and why it falls short ("Today, customers ... use x, y, or z ... Those products fall short ... Our solution addresses these unmet needs in the following ways"). |
| **Quotes & call to action** | A spokesperson quote, a (hypothetical) delighted-customer quote, and how to get started. |

The discipline is that every line is about the customer experience and the customer's reason to care — capabilities, costs, and feasibility are deliberately kept _out_ of the PR and pushed into the FAQ.

## The FAQ — where the dragons live

If the PR is the destination, the FAQ is, in the authors' memorable phrase, "the map to that destination and a detailed description of the dragons you will need to slay." It is split into two kinds of questions:

- **External FAQs** — what a customer or the press would ask: pricing, how it works, availability, support, how to buy.
- **Internal FAQs** — the hard ones leadership will ask across finance, operations, legal, HR, and engineering: How much will it cost to build? Is it technically feasible? What are the economics, the risks, the dependencies? This is where "a clear-eyed and thorough assessment of how expensive and challenging it will be" lives.

The internal FAQ is what keeps the PR honest. A press release alone could describe a magical product; the internal FAQ forces the team to confront whether that product can actually be built at a price that makes sense. The PR sells the vision; the FAQ stress-tests whether the vision survives contact with cost and feasibility.

## How a PR/FAQ is reviewed (and why it is read in silence)

The PR/FAQ is a **narrative document, read silently in the meeting**, not presented as slides — a direct application of Amazon's broader six-page-memo culture (covered in the companion `one-pager-and-narrative` reference). The review arc the authors describe:

```text
1. Solo first draft            — the PM writes it (a few hours of real work)
2. Cross-functional feedback   — manager + relevant peers
3. Small-group review          — ~10 contributors refine it
4. Executive review            — decision-makers

In the review meeting:
  ~15-20 min  silent reading (comments entered in the doc, not spoken)
  ~40 min     page-by-page discussion

Reviewers test four things:
  - Is the customer clearly defined?
  - Is the problem clearly defined?
  - Does the proposed solution address the problem?
  - Would we expect customers to CHANGE THEIR BEHAVIOR to adopt it?
```

The authors stress the meetings are about "truth-seeking vs. selling and improving vs. deciding" — the point is to refine the idea through debate, not to win approval. A PR/FAQ may be iterated many times, or killed, before any code is written. Killing an idea on paper is the cheapest possible outcome and an explicit success of the method.

## The PR/FAQ → PRD bridge

The PR/FAQ and the PRD are not rivals; they sit at different stages and answer different questions.

- The **PR/FAQ decides _whether and why_** to build — it is a vetting and alignment instrument that establishes the customer, the problem, the benefit, and a clear-eyed read on cost/feasibility. Its output is a go/no-go and a shared, customer-anchored vision.
- The **PRD decides _what exactly_** to build for those who said go — it inherits the PR/FAQ's customer, problem, and benefit as fixed inputs and adds the requirements, scope, non-goals, metrics, and open questions a team needs to execute (see the `prd-modern` reference).

The bridge is clean because the PR/FAQ already did the hardest part of a good PRD: it forced an outcome-and-customer framing before anyone fell in love with a feature. A PRD that begins from an approved PR/FAQ starts with its problem statement validated and its target customer named — the two sections Rachitsky and Marty C. both warn are the easiest to get wrong. In practice, the PR (especially the problem and solution paragraphs) becomes the PRD's problem/outcome spine, the external FAQ seeds the requirements and edge cases, and the internal FAQ seeds the risks/assumptions section. The PR/FAQ is the front door; the PRD is the build plan you write only after walking through it.

## Failure modes the format is built to catch

- **Skills-forward disguised as customer-forward** — a product justified by what the team can build. The PR has no excited customer to address, and the format makes the absence obvious.
- **"For everyone"** — a vague subheading. The method's rule ("if you think your product is for everyone, you are mistaken") flags it on the first line.
- **A PR with no internal FAQ** — vision with no cost/feasibility reckoning; a magical press release no one can actually ship. The dragons go unslain until production.
- **Selling instead of truth-seeking** — treating the review as an approval pitch rather than an adversarial refinement. The silent-read, page-by-page format is designed to defeat exactly this.
- **No behavior change** — the solution is real but customers have no reason to switch. The fourth reviewer question is there to surface it before launch.
