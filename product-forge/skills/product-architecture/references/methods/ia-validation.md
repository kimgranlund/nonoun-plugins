---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Donna Spencer, *Card Sorting: Designing Usable Categories* (Rosenfeld Media, 2009). https://rosenfeldmedia.com/books/card-sorting/"
  - "Nielsen Norman Group — “Card Sorting vs. Tree Testing,” “Tree Testing: Fast, Iterative Evaluation of Menu Labels and Categories,” “Card Sorting: How Many Users to Test,” and “Open vs. Closed Card Sorting” (nngroup.com)."
  - "Tom Tullis & Larry Wood, “How Many Users Are Enough for a Card-Sorting Study?” (UPA Conference, 2004) — the source of NN/g's ≈15-users guidance."
method: ia-validation
phase: structure
domains: [4]
timebox: "a few hours per study (remote, unmoderated)"
cadence: per-decision
participants: [ia/ux-researcher, "content/domain owner (to source items + labels)", "target users (open/closed sort + tree test)"]
inputs: ["a content inventory or item set", "a candidate structure or proposed tree (for the validation pass)", "real find-tasks the IA must support"]
produces: "evidence the IA matches users' mental models — or where it fails"
de_risks: [usability]
rubric: rubric-information-architecture
---

# IA Validation — build a structure with users, then prove they can find things in it

A **two-technique study** that tests whether an information architecture matches users' mental models: **card sorting** to build or refine the grouping and labels, then **tree testing** (the "reverse card sort") to prove people can actually navigate to a target in the resulting tree. Card sorting is _generative_ — it tells you how users would cut and name the content; tree testing is _evaluative_ — it puts the naked hierarchy in front of users and measures whether they can find things. You run them as a pair because each answers a question the other can't: a structure users _co-designed_ is not automatically a structure users can _navigate_, and a tree that tests well says nothing about whether you cut the categories the way users think. This file is the runnable procedure; the IA concepts it exercises — controlled vocabulary, hierarchical vs. faceted structure, the org-chart trap, the four polar-bear systems and the findability test — are defined in `taxonomy-and-classification.md` and `polar-bear-foundations.md` and not restated here.

## When to run it · when NOT

**Run it** whenever you are setting or changing a structure users navigate — a new product's top-level IA, a navigation redesign, a section rename, a content migration, or any time "the IA is bad" is a complaint without a diagnosis. Card-sort _early_ (you have content but no agreed categories) to forage the user's groups and labels; tree-test _before you build_ (you have a candidate tree) to catch a findability failure while it is still cheap to move a label. **Do NOT run it** when there is nothing to validate yet (settle the object model and controlled vocabulary first — there is no point sorting cards whose meanings aren't agreed), when the "structure" is really one screen (overkill), when you can't recruit _target_ users (sorting with random people validates a random mental model), or when the real defect is visual/interaction rather than structure — tree testing deliberately strips the UI, so if the problem is the menu's affordance, not its labels, this is the wrong instrument (see `navigation-and-wayfinding.md`).

## The run

Two studies, run in sequence: **card sorting builds/refines the structure, tree testing validates it.** Each is typically remote and unmoderated and takes a few hours of researcher time per study (plus fielding time to recruit). Pick the card-sort variant by how settled your categories are.

### Part 1 — Card sorting (build or refine the structure)

| # | Step | Who | Timebox | Output |
| --- | --- | --- | --- | --- |
| 1 | **Choose the variant.** _Open_ (users group **and name** the groups) when you have no categories yet and want the user's mental model + labels; _closed_ (users sort into **your fixed** categories) to validate a proposed structure; _hybrid_ (your categories, but users may add their own) when you have a draft but suspect gaps. | researcher | 30 min | a chosen technique + why |
| 2 | **Build the card set.** One concept per card, drawn from the content inventory, in the users' language not internal jargon; trim to a sortable set (a sort balloons past ~50–60 cards). Write find-tasks now too — they feed Part 2. | researcher + content owner | 1–2 hrs | the deck + a task list |
| 3 | **Recruit target users.** Card sorting is _generative_, so it needs more participants than the 5 of a usability test — NN/g recommends **≈15 per user group** (Tullis & Wood 2004 found 15 reaches a ~0.90 correlation; ~30 for large, well-funded studies). Segment if groups think differently. | researcher | (fielding) | a recruited panel |
| 4 | **Field the sort.** Each participant groups the cards (and, for open/hybrid, names the groups). Unmoderated tools field many in parallel; a few moderated sessions add the _why_ behind the groupings. | participants | a few hrs | raw sorts per participant |
| 5 | **Analyze.** Build a similarity/agreement matrix (which cards travel together), read a dendrogram for natural clusters, and harvest the **labels users wrote** — the priceless output of an open sort for the controlled vocabulary. Open sorts need interpretation; closed sorts read cleaner (did items land where you expected?). | researcher | 2–4 hrs | a proposed/confirmed structure + candidate labels |

The card sort produces a _hypothesis_: a grouping and a set of labels the evidence supports. It does **not** prove people can find things — for that, tree-test it.

### Part 2 — Tree testing (validate findability of the structure)

| # | Step | Who | Timebox | Output |
| --- | --- | --- | --- | --- |
| 6 | **Render the bare tree.** Turn the proposed structure into a clickable hierarchy of **labels only** — no UI, no search box, no visual design. Stripping everything is the point: a failure can't then be blamed on the search bar or the styling, only on the structure and its words. | researcher | 1–2 hrs | a naked tree |
| 7 | **Write the find-tasks.** For each, a realistic goal phrased in the user's words (never echoing a category label — that gives the answer away) and the node(s) that count as correct. Cover the IA's load-bearing paths, not every leaf. | researcher + content owner | 1 hr | tasks + correct-answer keys |
| 8 | **Recruit + field.** Participants get one task at a time and click down the tree to where they'd expect the answer. For **quantitative** findability NN/g recommends a **larger sample (≈50)**; a **qualitative** read of where people stumble works with ~5. | participants | a few hrs | click-paths per task |
| 9 | **Read the metrics.** **Success** (did they reach a correct node?), **directness** (did they go straight there, or backtrack — a label/grouping clarity signal), and **time**; then the diagnostic gold: **where they went wrong** — which _sibling_ stole the click pinpoints the exact label or grouping defect. | researcher | 2–4 hrs | a findability verdict + located defects |
| 10 | **Decide and iterate.** Fix the labels/groupings the failures point to and re-test the changed branches — tree tests are cheap and built to be run iteratively. Ship only when the load-bearing tasks succeed _directly_, not merely eventually. | researcher | (loop) | a validated tree, or a revision + next round |

## Roles

An **IA/UX researcher** owns the study — picks the variant, builds the deck and tree, recruits, runs the analysis, and reads the metrics. A **content/domain owner** sources the inventory and the realistic find-tasks and sanity-checks the candidate labels (without imposing internal jargon — they advise the vocabulary, they don't dictate it). **Target users** are the instrument in both passes: their sorts generate the structure, their click-paths validate it. The discipline is that the researcher stays neutral on _content_ — the evidence sets the tree, not the loudest stakeholder.

## Failure modes

- **Sorting then shipping.** Treating the card sort as the whole study. A co-designed grouping is a hypothesis about findability, not proof of it — un-tree-tested, you shipped an untested tree.
- **Tree-testing with the UI on.** Leaving search, styling, or navigation chrome in the test, so a structural failure hides behind a search box (or a beautiful menu flatters a broken structure). Test the labels _naked_.
- **Tasks that leak the answer.** Phrasing a find-task in the category's own words ("find the _Billing_ settings" when "Billing" is the label) measures reading, not findability. Phrase tasks in the user's goal language.
- **Wrong / too few participants.** Sorting with non-target users validates a stranger's mental model; running a card sort with 5 (it's generative — it needs ~15) or a _quantitative_ tree test with a handful yields noise read as signal.
- **Validating the org chart.** Supplying closed-sort categories that mirror internal team boundaries — users then "confirm" a structure they'd never have built. Use an _open_ sort to forage the user's cuts before you ever hand them yours.
- **One-and-done.** Running a single tree test, finding failures, and shipping anyway. The method's value is the cheap iteration loop — fix the labels the failures point to and re-test.

## A good run vs. a bad run

|  | Bad run | Good run |
| --- | --- | --- |
| Card set | internal jargon; one card = several concepts | user-language items, one concept per card |
| Variant | closed sort of org-chart categories | open sort to forage groups + labels, then closed/hybrid to confirm |
| Participants | 5 strangers | ~15 target users per group (sort); ~50 for a quantitative tree test |
| Tree test | UI, search, and styling left in | a naked hierarchy of labels only |
| Tasks | worded in the category's own labels | worded as the user's real goal |
| Read | "success rate looked fine" | success **and** directness, plus _which sibling_ stole each wrong click |
| After | shipped on the first result | fixed the located defects and re-tested the branch |

**The single test:** can you point at the proposed tree and say, in evidence, _which_ find-tasks users completed **directly** and _which_ sibling label stole each failed click? If you can only report "the sort felt about right" or a bare success percentage, you have an opinion and a number — not a validated IA.

## Hand-off

A **validated** structure flows into the build of the navigation and labeling systems — the confirmed groups become the hierarchy/sections, the foraged labels become the controlled vocabulary, the faceted dimensions feed filtering (→ `taxonomy-and-classification.md`, `navigation-and-wayfinding.md`, `filtering-and-faceting.md`). A structure that **fails** the tree test flows back into the arrangement work: the located defects (which sibling stole the click) tell you exactly which label or cut to revise before re-testing — far cheaper than discovering it in production analytics or support tickets. Score the run with `rubric-information-architecture` (does the IA match the user's mental model, evidenced — labels foraged, structure tree-tested, findability demonstrated by every path real users take, per the polar-bear findability test in `polar-bear-foundations.md`).

## Sourcing

Card sorting and its open/closed/hybrid variants are from Donna Spencer, _Card Sorting: Designing Usable Categories_ (Rosenfeld Media, 2009), the standard reference. The card-sort participant guidance (≈15 users for a ~0.90 correlation; ~30 for large studies) is **Nielsen Norman Group's, citing Tullis & Wood's 2004 UPA study** — attributed, not invented. Tree testing as the evaluative "reverse card sort," its naked-hierarchy discipline, the success/directness/time metrics, and the ≈50-participant quantitative / ~5 qualitative split are from **NN/g's** "Card Sorting vs. Tree Testing" and "Tree Testing" articles. The pairing logic (card sort generates and labels the structure; tree test proves people can navigate to a target in it) and the IA vocabulary it exercises are established in `taxonomy-and-classification.md` and `polar-bear-foundations.md`. Confirm any verbatim quotation or exact figure against the cited print/source pages before publishing.
