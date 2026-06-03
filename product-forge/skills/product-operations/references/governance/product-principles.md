---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Julie Zhuo, “A Matter of Principle,” The Year of the Looking Glass (Medium, 2016) — design principles should be controversial; they explain a decision another company wouldn't make."
  - "Government Digital Service — Government Design Principles (gov.uk/guidance/government-design-principles, first published 2012, iterated since)."
  - "Intercom — “Foundations to build on: Intercom's principles for building product” (intercom.com/blog/intercom-product-principles)."
  - "Spotify Design — “The lifecycle of a design principle” / Spotify's “Ship it, then refine” articulated in Spotify Design and engineering writing (spotify.design)."
---

# Product & Design Principles

A principle is a pre-committed answer to a recurring decision, written down before the decision is in front of you so the team doesn't relitigate the same trade-off every time. The single most useful test, due to Julie Zhuo, is that **a good principle is controversial** — it "should explain why your company made a decision that another wouldn't." If the opposite of your principle is obviously stupid, it is not a principle; it is a platitude, and it will guide nothing. This file is the working method for telling the two apart, writing principles that survive contact with a real decision, and putting them to work.

> **Zhuo's test (2016):** _Strong principles encode "what is unique about the way we as a team think that might be different from the way other companies think."_ A principle that any competent team would also sign is decoration. A principle that a reasonable competitor would reject is doing its job.

## The three properties of an enforceable principle

A principle earns the name only when all three hold. Miss one and you have a value, a slogan, or a wish.

| Property | What it means | The failing opposite |
| --- | --- | --- |
| **Takes a side** | A reasonable, competent team could hold the opposite view and ship a real product on it | "We value quality" — no one is for low quality, so it picks nothing |
| **Names a trade-off** | It tells you what you give up when you follow it; it has a cost you accept on purpose | "Delight users _and_ ship fast _and_ be rigorous" — names no sacrifice, so it never breaks a tie |
| **Is testable in a decision** | You can hold a concrete proposal against it and get a different answer than you'd get without it | "Be customer-obsessed" — true of every option on the table; resolves nothing |

The combined test is one question: **can this principle lose an argument?** If following it never costs you anything you wanted, it is not steering — it is applause. GOV.UK's "Do less" is enforceable precisely because it loses arguments: it tells a government team to _not_ build something it could build, to "only do what only government can do," and to link to others' work instead. That is a side, a cost, and a verdict you can apply to a specific proposal.

## How to write one

The reliable shape is **a verb-led directive plus the trade-off it accepts**, often "Prefer X over Y" or "Do A, even when B." The "even when" clause is where the side lives — it pre-commits you to the hard case.

- **Start from a real decision you keep re-arguing.** Principles are harvested, not brainstormed. Find the meeting you have over and over (scope vs. polish, bespoke vs. reuse, breadth vs. depth) and write the answer you wish you'd already agreed on. A principle with no originating argument is theoretical.
- **Write the trade-off into the sentence.** Intercom's "Think big, start small" pairs ambition with a forced constraint — "always try to find the smallest coherent solution." The two halves are in tension on purpose; that tension is what makes it useful when someone wants to ship the big version now.
- **Make it falsifiable against a proposal.** A principle should let two people look at the same mock or PRD and reach the _same_ call. If it can't adjudicate, sharpen it until it can. "Follow fundamentals" (Intercom) cashes out as "reuse, evolve and merge before creating something new" — that is a check you can run on a pull request.
- **Order them, because they will collide.** Two good principles will eventually point opposite ways. Amazon's Leadership Principles are explicitly applied with judgment about which dominates in context; GOV.UK lists "Start with user needs" _first_ on purpose. An unordered set defers the real decision — which principle wins — to whoever is loudest in the room.
- **Keep the set small enough to recall.** GOV.UK runs on ten; most teams should run on fewer. A principle no one can recite in the moment of decision is not operating. If you have twenty, you have a wiki page, not a spine.

## How principles get used in decisions

A principle that lives only on a poster is dead. Live principles show up at three moments, and you can audit a team by checking whether they do.

- **As a tie-breaker in review.** When a design or spec review stalls between two defensible options, the chair names the governing principle and the principle decides. "We're choosing the simpler flow because _Do less_ — yes, we're giving up the power-user shortcut, and that's the trade we signed." (See `review-rituals.md` for the mechanics of a review that decides.)
- **As a rationale in the decision record.** A good ADR or decision log cites the principle it leaned on, so the next reader sees not just _what_ was chosen but _which standing commitment_ drove it. This is how a principle compounds: every decision that cites it strengthens it, and every decision that quietly violates it is a visible defect. (See `decision-records-adr.md`.)
- **As an onboarding shortcut.** Zhuo's point about scaling: principles let a new hire predict "what's important for us and what's true to us" without shadowing a VP for six months. The faster a newcomer can guess your call before you make it, the better your principles are written.

The tell of a healthy principle is that someone can point to a feature you _killed_ or a request you _refused_ because of it. Principles are proven by their "no," exactly like strategy (see the methodology's strategy references) — if no shipped decision was ever harder because of a principle, the principle is inert.

## Tells of good vs. bad principles

| Signal | Platitude (bad) | Principle (good) |
| --- | --- | --- |
| **Sidedness** | A competitor would happily sign it too | A competent rival could reasonably reject it |
| **Trade-off** | Names only upside; stacks virtues | States what you give up to honor it |
| **Adjudication** | True of every option; breaks no tie | Two readers reach the same verdict on a real proposal |
| **Originating argument** | Invented in a workshop, no real decision behind it | Harvested from a fight the team keeps having |
| **Collision handling** | Flat, unordered list; conflicts unresolved | Ordered or scoped, so you know which one wins |
| **Recall** | Twenty entries no one can name | A handful anyone can recite mid-decision |
| **Evidence of use** | Cited nowhere; lives on a slide | Visible in killed features, refused requests, decision records |

The fastest single audit, when time is short: take any principle and write its credible opposite as a sentence a real company might adopt. If the opposite is absurd ("we value low quality"), the principle is a platitude — delete or rewrite it. If the opposite is a stance a serious competitor might actually take, you have a principle worth keeping.

## One labeled caveat

The Zhuo formulations ("should be controversial," "explain why your company made a decision that another wouldn't," the scaling/onboarding rationale) are attributed to her essay "A Matter of Principle" and her Intercom podcast appearance on product design, cross-checked across multiple secondary summaries in this session rather than re-read line-by-line from the originals. The GOV.UK principles, the Intercom principle set ("Think big, start small," "Follow fundamentals," "Ship to learn"), and Amazon's Leadership-Principles-applied-with-judgment posture are paraphrased from their published sources; verify exact wording against the live pages before quoting verbatim, since both GOV.UK and Intercom iterate their lists over time.
