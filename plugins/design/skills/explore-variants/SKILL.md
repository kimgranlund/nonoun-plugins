---
name: explore-variants
description: Explore one open question as a set of answers that differ in kind, on one published page - each answer shown as the thing itself at small scale (a live mock, a diagram with one case traced through it, a plan's first moves, the same piece written in each direction), from one shared fixture, under one shared stress, with what it keeps, gives up, depends on and where it breaks, a comparison table, a recommendation, and a feedback form per answer that copies one JSON object the user pastes back in chat. Then run the next round from that JSON. Use for "explore N ways to...", "what are our options for...", "how else could we...", "show me directions for...", a UI layout or interaction, an architecture, a strategy, a decision, a name, a voice or creative direction, a review of what was built (keep or go back), or when the user pastes explore-variants or ui-explore-variants feedback JSON. NOT for a design whose decisions are mostly unmade (grill), designing one settled approach (architect), mapping what exists (system-atlas), comparing code implementations of one settled design (component-variants), whole-page wireframes (wireframe-review), tuning constants (ui-kit-inspector), or building the chosen answer.
---

# Explore variants

One open question, several answers that differ in kind, on one page the user can operate, judge and answer.
The page is a thinking tool: it is finished when the user can say which way to go, not when it is pretty.

## Route

| You have | Do |
|---|---|
| An open question, no page yet | The recipe for its subject (next table), then the procedure from step 1 |
| A page and pasted feedback JSON | The recipe for its subject, then [Reading the feedback](#reading-the-feedback) and the next round |
| A request for a different number of variants, or a named axis | The recipe, then step 3 with that number or axis fixed |

| The question is about | Read first |
|---|---|
| A UI layout or interaction | `references/ui.md` |
| A system's structure | `references/architecture.md` |
| A plan, or a choice among courses | `references/strategy.md` |
| Words, a name, a voice or a visual direction | `references/creative.md` |
| Work already done (keep or go back) | `references/review.md` |

Read the recipe before choosing variants and again before each later round: it holds rules for later rounds
too. A question that fits none takes the three questions every recipe
answers: what is the specimen, what is the fixture, what is the stress.

Files, relative to this folder: `assets/template.html` (page skeleton), `assets/feedback.css` and
`assets/feedback.js` (the feedback module), `scripts/inline.mjs` (puts the module into a page),
`scripts/check.mjs` (the skill's own check: `node scripts/check.mjs <project-with-playwright>`; run it before and
after any change to the module).

## Procedure

1. **State the one question.** In the user's words, as a headline: "Five ways to show an event without wrapping its
   title", "Four places the session state could live". Say what is wrong today in one or two sentences, from what
   they sent. If the request holds two questions, explore the first and name the second.
2. **Look for existing work first.** Other branches, prototypes, a related skill, a decision record. If someone has
   already explored this, say so on the page or in the reply, and build on it.
3. **Choose variants that differ in kind.** List the structural axes of the problem (the recipe names the usual
   ones for its subject). Each variant moves a different axis. Tests: each is described in one sentence without
   naming another; none is a restatement or a restyling of another. Include the user's own idea as one variant
   when they offered one. Default five. A variant you already believe is wrong still earns its place if it shows
   a real trade.
4. **One fixture for all.** One real case, the same in every variant, including the parts that make the problem
   hard. Never a placeholder, never a variant flattered by an easier case. The recipe says what a fixture is for
   its subject.
5. **One shared stress control.** A control (a slider, a toggle, a set of named scenarios) that changes what makes
   the problem hard, applied to every variant at once, so the reader sees where each gives out. Add a second
   control only when round 2 needs it. Mark each with `data-fb-control="<name>"`, or a group of buttons with
   `data-fb-control-group="<name>"` where the chosen button carries `aria-pressed="true"`, so the feedback records
   what was on screen.
6. **Show the thing, not a description of it.** Each variant is the answer itself at small scale, made from the
   fixture. A description of an answer hides its cost.
7. **Three facts per variant:** Keeps, Gives up, Breaks when. One sentence each. The cost is stated as plainly
   as the benefit. A variant that cannot be operated carries a fourth, Depends on (see Rules).
8. **Compare and take a position.** One table with the same criteria for every variant, then your reading as a
   sentence: which you would pick, and when. A ladder (this one at this size, that one at that) is a valid
   answer. Mark every figure that is an estimate, not a measurement.
9. **Add feedback capture** (next section), publish as an Artifact, and say in the reply: what each variant is in
   one line, your reading, the choices you made that the user may want different, and what you could not verify
   (for example that you could not render-check the page).

Build on the Artifact tool's page contract (theme tokens in both schemes, side gutters, a named title). Write every
visible word of the page (question, headings, facts, comparison, recommendation, aspect labels) in plain language a
person outside the project understands: say what an option does ("Make the button a bit darker, whatever colour it
is"), not its internal name. No amendment ids, token names or system shorthand in headings or the main text; when
the builder needs them, put them in one collapsed "Technical details" block per moment. Keep the page utilitarian:
no hero, no decoration; the variants are the content.

## Feedback capture

Start from `assets/template.html`. Each variant is a `section[data-variant="<slug>"]` inside one
`[data-explore]` container that carries `data-question`, `data-round` and `data-aspects` (the things a reader can
say work or do not; make them specific to the problem, such as "Shows duration", "Readable at a glance").
A page with several moments gives each its own aspects: `data-aspects` on a wrapper around that moment's variants,
or on a variant. The nearest one wins, then the container's.
From round 2 the page opens on the current round; "All rounds" shows the earlier ones. Mark an earlier round's own
table or reading with its `data-round`, so it hides with its variants.
Then run `node <skill>/scripts/inline.mjs <page.html>` and publish.

The module reads `--fb-ink`, `--fb-panel`, `--fb-fill`, `--fb-muted`, `--fb-quiet`, `--fb-focus` and `--fb-bg`,
falling back to the same names without the prefix. A page that inlines a design system's tokens sets the `--fb-*`
names, so the system's own `--ink` or `--panel` never reach the form.

Each variant also carries `data-moment="<slug>"`, the one decision it answers (a page about one question
has one moment; a page about several has one per question), and keeps it across rounds. A variant kept from an
earlier round also carries its own `data-round`. A page that sets no moment has one. The module then adds
**Compare**: a button fixed to the page's corner, the shortcut `C` (the reader can turn it off), and a "Compare all"
button in each variant's header.

Compare opens a modal dialog over the page. It holds every section with the chosen moment, from every round, as
cards in one track that scrolls without paging. Each card shows the variant's name, its round and its verdict, and
the variant stays live: the module moves the variant's `.stage` into the card and puts it back on close, leaving a
placeholder of the same height, so the page under the dialog does not move (an `iframe` in a stage reloads when it
is moved). The dialog's header has a moment picker, filters for round and verdict, a fit/natural size toggle
(natural by default, so nothing is judged scaled; a fitted card says how far it is scaled), and a copy of each
`data-fb-control`, bound to the page's controls, so the stress applies in the dialog too. The verdict on a card
writes the same draft as the form. Escape closes only the dialog and focus returns to the control that opened it;
a layer inside a variant that takes Escape first must cancel the keydown. Beyond 24 cards only those near the view
hold their stage. Compare is a view: the JSON gains nothing.

The module adds to each variant: a verdict (Pursue, Keep parts, Drop), "Works" and "Does not" choices from the
aspects, and a note. At the end of the container it adds "Send feedback": what to do next (Refine the picks, Combine
the picks, Explore further, Build it), an overall note, **Copy feedback JSON**, and a preview. Answers are kept
as a draft in the reader's browser. Where the clipboard is refused, the JSON is selected for copying by hand.

A page that asks another kind of question names its own verdicts: `data-verdicts` on the container, as labels or
`key:Label` pairs with the positive one first (a review of what is already built: `data-verdicts="keep:Keep,revert:Go back"`).
The JSON then carries `verdicts`, the keys offered. Where a moment's variants are alternatives and only one can win
(a pair of before and after, three candidates for one slot), put `data-pick="one"` on the container, on a wrapper
around that moment or on its variants: giving one variant the first verdict moves the moment's other variants that
are not judged, or that held it, to the last verdict, so one click answers the moment. A middle verdict is left alone.

```json
{ "skill": "explore-variants", "schema": 1,
  "exploration": "Calendar Event Layouts", "question": "…", "round": 2,
  "controls": { "width": "440", "now": "560", "view": "Week" },
  "variants": [ { "id": "dots", "name": "Dots, with the day spelled out below",
                  "offered": ["Layout", "Shows duration"],
                  "verdict": "pursue", "works": ["Layout"], "doesnt": [], "note": "…" } ],
  "overall": { "next": "combine", "note": "…" },
  "capturedAt": "2026-11-13T14:02:11.000Z" }
```

## Reading the feedback

The JSON is the user's answer; treat its notes as their words. A JSON whose `skill` is `ui-explore-variants` comes
from a page built before the rename; read it the same way. Save it beside the page as
`feedback.round-<n>.json` before acting on it, so what was decided can be checked later. Then:

1. Restate it in two lines: what is pursued, kept in part and dropped, and the next step they chose.
2. A `null` verdict is "not judged", not "dropped". A note outranks a choice when they disagree; quote it.
   An aspect in `offered` and in neither list was not ticked; one absent from `offered` was never asked.
   When every verdict is `null` and there is no note, the JSON carries no answer (`overall.next` is then only the
   form's remembered value): do not run a round on it. Ask the user for the pick directly, with your recommendation
   first.
3. Every question in a note gets an answer that is **built** on the page where it can be, not only described.
4. Act on `overall.next`:
   - `refine` or `combine`: a round 2 on the same artifact. Add a "Direction" section above the variants that
     joins the picks, increment `data-round`, keep the earlier variants on the page, hidden until asked for, and take what
     "Works" from dropped variants only where a note asks. Where the picks conflict, or a note asks for "more" or
     "stronger", the Direction holds judgeable sub-variants (each its own `section[data-variant]`): two honest
     combinations, or two or three strengths side by side with the computed figure for each. Never blur a conflict
     into one mock.
   - A standing rule the user states in a note ("disabled never uses the primary colour") applies to every variant
     in every later round, and is listed on the page as a rule heard.
   - `more`: new variants on the axes the notes point at; retire the dropped ones to a short list.
   - `build`: stop exploring. Hand over a short spec (what was chosen, states, rules, starting values marked as
     unconfirmed, any accepted risk with its fallback, what was not chosen, and the fixture as test cases) to whatever
     builds it; this skill does not implement the product.
5. In the reply, list the choices you made in the round that the user may want different.

## Rules

- Variants differ in kind, never only in wording or styling.
- One fixture, one stress control, the same facts and criteria for every variant.
- Plain language on the page; internal names only under Technical details.
- Every variant names its moment, so Compare can gather it.
- State the cost of each variant, and your own recommendation, even when the user has a favourite.
- An estimate is labelled an estimate. An unverified page is reported as unverified.
- Where a variant cannot be operated, it carries a fourth fact, Depends on: the assumption that sinks it if false.
- Every claim on such a page is marked measured, sourced, estimated or assumed.
- Republish to the same artifact across rounds; label each publish with what the round added. Keep the previous
  round's file beside the page, so a later round can be diffed against what the user judged.
- Stop exploring when the user picks. More variants after a decision is noise.

## Worked example

The UI recipe, on the calendar event problem this skill was written from: a week scheduler whose event titles
wrapped inside narrow day columns. Round 1: five variants on five axes (a rail with a floating label; dots with one day
listed below; an agenda list with no grid; a sideways timeline; one day wide with the rest as slivers), nine
shared events including an overlap and a quarter-hour meeting, a width slider, a ladder as the reading. The user
picked dots and agenda with a toggle and asked three questions (emphasise the current or next meeting, a
current-time line, past versus upcoming). Round 2 answered each on the page: the current event's dot grows to
a bar with its title, the next gets a halo and the time to go, a dashed now line, past events hollow and quiet,
and a "now" scrubber as the second control so every state could be seen.
