---
name: ui-explore-variants
description: Explore a UI design problem as a set of coarsely distinct layout or interaction solutions on one published page - each variant live, drawn from one shared fixture, under one shared stress control (width, count, length, time), with what it keeps, gives up and where it breaks, a comparison table, a recommendation, and a feedback form per variant (multiple choice and text) that copies one JSON object the user pastes back in chat. Then run the next round from that JSON. Use for "explore N ways to...", "how else could we show...", "show me options for this layout", "I'm not sure how this should work, explore it", a component that fails at some size or state and needs rethinking, or when the user pastes ui-explore-variants feedback JSON. NOT for comparing code implementations of one settled design (component-variants), whole-page wireframes (wireframe-review), tuning a system's constants (ui-kit-inspector), a showcase of finished components (ui-showcase-bento), or building the chosen variant in the product.
---

# UI explore variants

One design question, several answers that differ in kind, on one page the user can operate, judge and answer.
The page is a thinking tool: it is finished when the user can say which way to go, not when it is pretty.

## Route

| You have | Do |
|---|---|
| A design problem, no page yet | The procedure below, from step 1 |
| A page and pasted feedback JSON | [Reading the feedback](#reading-the-feedback), then a round 2 |
| A request for a different number of variants, or a named axis | Step 3 with that number or axis fixed |

Files, relative to this folder: `assets/template.html` (page skeleton), `assets/feedback.css` and
`assets/feedback.js` (the feedback module), `scripts/inline.mjs` (puts the module into a page).

## Procedure

1. **State the one question.** In the user's words, as a headline: "Five ways to show an event without wrapping its
   title". Say what is wrong today in one or two sentences, from the screenshot or element they sent. If the request
   holds two questions, explore the first and name the second.
2. **Look for existing work first.** Other branches, prototypes, a related skill, a decision record. If someone has
   already explored this, say so on the page or in the reply, and build on it.
3. **Choose variants that differ in kind.** List the structural axes of the problem (what carries the text, what
   carries the quantity, whether the frame is kept or dropped, orientation, all at once or one in focus, where
   detail lives). Each variant moves a different axis. Tests: each is described in one sentence without naming
   another; no two share a silhouette at thumbnail size; none is a restyling of another. Include the user's own
   idea as one variant when they offered one. Default five. A variant you already believe is wrong still earns
   its place if it shows a real trade.
4. **One fixture for all.** Real content, the same in every variant, including the cases that make the problem
   hard (the long title, the overlap, the very short item, the empty day). Never lorem ipsum, never a variant
   flattered by easier content. When a variant stands for a kind of product, the fixture is that product in use
   (the player playing, the article being read, the game being played), with no navigation or headline about it;
   a landing page is a fixture only when the subject is a landing page.
5. **One shared stress control.** A slider or toggle that changes what makes the problem hard, applied to every
   variant at once, so the reader sees where each gives out. Add a second control only when round 2 needs it
   (a "now" scrubber for time-dependent states). Mark each with `data-fb-control="<name>"` so the feedback records
   what was on screen.
6. **Make every variant live.** Rendered from the fixture by script, operable where the idea depends on operation
   (choose a day, open a column). A static picture of an interactive idea hides its cost.
7. **Three facts per variant:** Keeps, Gives up, Breaks when. One sentence each. The cost is stated as plainly
   as the benefit.
8. **Compare and take a position.** One table with the same criteria for every variant, then your reading as a
   sentence: which you would pick, and when. A ladder (this one at this size, that one at that) is a valid
   answer. Mark every figure that is an estimate, not a measurement.
9. **Add feedback capture** (next section), publish as an Artifact, and say in the reply: what each variant is in
   one line, your reading, the choices you made that the user may want different, and what you could not verify
   (for example that you could not render-check the page).

Build on the Artifact tool's page contract (theme tokens in both schemes, side gutters, a named title). Use the
product's own tokens and vocabulary when they exist. Keep the page utilitarian: no hero, no decoration; the
variants are the content. Follow the product's standing rules in the mocks (for example no borders, neutral
selected states) or the reader judges the wrong thing.

## Feedback capture

Start from `assets/template.html`. Each variant is a `section[data-variant="<slug>"]` inside one
`[data-explore]` container that carries `data-question`, `data-round` and `data-aspects` (the things a reader can
say work or do not; make them specific to the problem, such as "Shows duration", "Readable at a glance").
A page with several moments gives each its own aspects: `data-aspects` on a wrapper around that moment's variants,
or on a variant. The nearest one wins, then the container's.
Then run `node <skill>/scripts/inline.mjs <page.html>` and publish.

The module reads `--fb-ink`, `--fb-panel`, `--fb-fill`, `--fb-muted`, `--fb-quiet`, `--fb-focus` and `--fb-bg`,
falling back to the same names without the prefix. A page that inlines a design system's tokens sets the `--fb-*`
names, so the system's own `--ink` or `--panel` never reach the form.

Each variant also carries `data-moment="<slug>"`, the component or UI moment it answers (a page about one question
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
aspects, and a note. After the last section it adds "Send feedback": what to do next (Refine the picks, Combine
the picks, Explore further, Build it), an overall note, **Copy feedback JSON**, and a preview. Answers are kept
as a draft in the reader's browser. Where the clipboard is refused, the JSON is selected for copying by hand.

```json
{ "skill": "ui-explore-variants", "schema": 1,
  "exploration": "Calendar Event Layouts", "question": "…", "round": 2,
  "controls": { "width": "440", "now": "560", "view": "Week" },
  "variants": [ { "id": "dots", "name": "Dots, with the day spelled out below",
                  "verdict": "pursue", "works": ["Layout"], "doesnt": [], "note": "…" } ],
  "overall": { "next": "combine", "note": "…" },
  "capturedAt": "2026-11-13T14:02:11.000Z" }
```

## Reading the feedback

The JSON is the user's answer; treat its notes as their words. Then:

1. Restate it in two lines: what is pursued, kept in part and dropped, and the next step they chose.
2. A `null` verdict is "not judged", not "dropped". A note outranks a choice when they disagree; quote it.
   When every verdict is `null` and there is no note, the JSON carries no answer (`overall.next` is then only the
   form's remembered value): do not run a round on it. Ask the user for the pick directly, with your recommendation
   first.
3. Every question in a note gets an answer that is **built** on the page where it can be, not only described.
4. Act on `overall.next`:
   - `refine` or `combine`: a round 2 on the same artifact. Add a "Direction" section above the variants that
     joins the picks, increment `data-round`, keep the earlier variants below it for reference, and take what
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

- Variants differ in structure, never only in styling.
- One fixture, one stress control, the same facts and criteria for every variant.
- Every variant names its moment, so Compare can gather it.
- State the cost of each variant, and your own recommendation, even when the user has a favourite.
- State by shape as well as colour (hollow and filled, size, weight), so a variant is judged without colour.
- An estimate is labelled an estimate. An unverified page is reported as unverified.
- Republish to the same artifact across rounds; label each publish with what the round added. Keep the previous
  round's file beside the page, so a later round can be diffed against what the user judged.
- When a round fixes something the user pointed at, say whether the fix was looked at in a render, and in which
  schemes and states it was not.
- Stop exploring when the user picks. More variants after a decision is noise.

## Worked example

The calendar event problem this skill was written from: a week scheduler whose event titles wrapped inside
narrow day columns. Round 1: five variants on five axes (a rail with a floating label; dots with one day
listed below; an agenda list with no grid; a sideways timeline; one day wide with the rest as slivers), nine
shared events including an overlap and a quarter-hour meeting, a width slider, a ladder as the reading. The user
picked dots and agenda with a toggle and asked three questions (emphasise the current or next meeting, a
current-time line, past versus upcoming). Round 2 answered each on the page: the current event's dot grows to
a bar with its title, the next gets a halo and the time to go, a dashed now line, past events hollow and quiet,
and a "now" scrubber as the second control so every state could be seen.
