---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "NN/g — Designing Empty States in Complex Applications: 3 Guidelines (nngroup.com/articles/empty-state-interface-design)"
  - "NN/g — 3 Guidelines for Search Engine \"No Results\" Pages (nngroup.com/articles/search-no-results-serp)"
  - "NN/g — Visibility of System Status (Usability Heuristic #1) (nngroup.com/articles/visibility-system-status)"
---

# Empty States

An empty state is what a surface shows when it has no content to display. It is the most under-designed and over-consequential screen in most products: it is frequently the **first** screen a new user sees, and a blank panel reads as "broken," "nothing happened," or "I did something wrong." The discipline here is to treat every place that can be empty as a designed state with a job — communicate status, teach the feature, and hand the user a way forward — rather than as the absence of a screen. NN/g's framing is that well-designed empty states "communicate system status, increase learnability of the system, and deliver direct pathways for key tasks."

The single most important move is to **distinguish which empty state you are in**, because the three are not interchangeable and a recommendation that fixes one breaks another.

---

## The three empty states (do not conflate them)

| State | What caused it | What the user needs | Wrong response |
| --- | --- | --- | --- |
| **First-use (zero-data)** | The user is new; nothing has been created or configured yet. | Orientation + one obvious first action that produces value. | A sad "Nothing here" with no path; a 40-field setup wall. |
| **User-cleared** | The user emptied the surface themselves — archived the last item, completed every task, dismissed all notifications. | Acknowledgement and reassurance — this is **success**, not failure. | Treating it like an error ("No data found"); hiding that the action worked. |
| **No-results / error** | A search, filter, or query returned nothing — or a fetch failed. | What was searched, why it's empty, and a way to broaden or retry. | A dead end; identical copy to the first-use state; a blank that looks like a load. |

The bright line: **first-use is an opportunity, user-cleared is an achievement, and no-results is a recovery.** The first should onboard, the second should congratulate-and-reset, the third should re-route. Shipping one generic "empty" component for all three is the core anti-pattern, because the same words ("There's nothing here") are encouraging to a new user, condescending to someone who just cleared their inbox, and useless to someone whose search failed.

A fourth case masquerades as empty and must be excluded: **content still loading.** NN/g warns explicitly against premature "no records" copy — a panel that says "There are no records to display" while a request is in flight teaches the user a falsehood. Show a loading state (skeleton/spinner; see the feedback reference) until the result is known, then resolve to the correct empty state.

---

## Canonical form

A well-formed empty state carries up to four parts, in priority order. Not every state needs all four — a user-cleared state may be a single warm line — but the order is the contract.

1. **Status line — what is true and why.** State the fact plainly so the surface does not read as broken. NN/g: a simple message such as "There are no records to display for the selected date range" "communicates the state of the system and increases user confidence." This is heuristic #1 (Visibility of System Status) applied to emptiness — its core rule is "Don't blindfold your users."
2. **Teaching cue — what this feature does.** Use the empty moment to explain the feature it belongs to, contextually. NN/g calls these "pull revelations" — help that appears in the moment the user is looking right at the thing (their example: DataDog's "Star your favorites to list them here").
3. **Primary action — the one next step.** A button or link that launches the workflow that fills the state. NN/g's principle is to "create direct pathways for key tasks," not merely describe them (Loggly offers "adding log sources or exploring with demo data" rather than only narrating the possibility).
4. **Optional supporting element** — an illustration, a secondary "import demo data" path, or a link to docs. Supporting, never load-bearing; an illustration with no action is decoration.

```text
┌─────────────────────────────────────────────┐
│              [ light illustration ]          │  ← optional, supporting
│                                              │
│   You haven't created any projects yet       │  ← status: what's true
│   Projects group your tasks and files so      │  ← teaching: what it does
│   your team can find them.                    │
│                                              │
│        [  Create your first project  ]        │  ← primary action (the point)
│        or  import from a template             │  ← optional secondary path
└─────────────────────────────────────────────┘
```

---

## The onboarding-via-empty-state pattern

The strongest use of a first-use empty state is **as the onboarding surface itself** — instead of (or alongside) a separate tour or coachmark overlay. The product's home, with zero data, doubles as the first lesson: each empty region explains its own feature and offers its own first action, so the user learns by filling the real interface rather than by clicking through a modal sequence they will forget.

Why this beats a front-loaded tour:

- **It is contextual and just-in-time.** The explanation sits on the feature, in the moment of attention — NN/g's "pull" model — rather than describing eight features the user cannot yet see. Push tours are skipped and not retained; pull cues land.
- **It produces a real first win.** A first-use state whose primary action creates the user's first actual artifact (project, note, dashboard) converts orientation into value in one step. The empty state is the call to the activation moment, not a preamble to it.
- **It degrades gracefully.** As the user fills one region, that empty state resolves to real content and the next empty region becomes the next lesson — onboarding distributed across the surface and paced by the user, not by a wizard.
- **It is reusable.** The same teaching empty state re-appears for a returning user who later visits a feature they never adopted, so the "onboarding" keeps working past day one.

Pre-populating a brand-new account with **sample/demo data** is the related move: it removes the blank-canvas freeze by letting the user explore a populated, working product before committing their own data — provided the sample is clearly labeled and trivially clearable, so it never gets mistaken for real content.

---

## No-results, specifically

The no-results / search-error case has its own rules because it is a recovery, not an introduction. NN/g's guidance for "no results" pages:

- **Make the zero result unmistakable and explain it.** Restate the query and the active filters so the user can see _what_ returned nothing — "No results for `wireless headphnoes` in Electronics under $50" surfaces the typo and the filters in one line.
- **Offer a path out, not a wall.** Suggest relaxing a filter, broadening the term, correcting a likely misspelling, or browsing related/popular content. NN/g frames the no-results page as a high-abandonment moment that good design can convert "into an opportunity for content discovery."
- **Never let it read as the first-use state.** A search that fails is a different problem from a workspace that is new; reusing the welcome copy here is disorienting.

A failed _fetch_ (network/server error) is an error state, not an empty state: it needs a retry affordance and plain-language error copy — see the error-handling reference — not "you have no items."

---

## Variants

- **Zero / one / some.** Design the empty state alongside the one-item and the populated states; a layout tuned only for "many" looks broken at zero and lonely at one.
- **Filtered-empty vs truly-empty.** "No items match this filter" (offer **Clear filters**) is distinct from "you have no items yet" (offer **Create**). Same panel, opposite action.
- **Permission/eligibility-empty.** Empty because the user lacks access or the feature is gated — the action is "request access" or "upgrade," not "create."
- **Cleared-success.** Inbox-zero, all-tasks-done, no-notifications: lean warm and brief, optionally celebratory, and never alarming.
- **Error-empty.** A load failed; pair plain-language cause with a **Retry**, and preserve any context (the query, the filters) so retry is one tap.

---

## Anti-patterns

- **One generic "empty" for all states.** The defining failure: identical copy and action across first-use, cleared, no-results, and error. Each needs different words and a different next step.
- **Decorative dead ends.** A cute illustration and a witty line with **no action** — the user is told it's empty and given nothing to do about it.
- **Premature emptiness.** Showing "No records" while data is loading (NN/g's explicit warning); resolve loading first.
- **The setup wall.** A first-use state that demands heavy configuration before showing anything; defer configuration, deliver a first win, then layer setup.
- **Blame in no-results.** "You searched wrong" framing; describe the gap and offer a fix, never fault the user (the same tone rule as error messages).
- **Unlabeled sample data that can't be cleared.** Demo content the user mistakes for their own and cannot easily remove pollutes their first real session.

---

## Accessibility

- **Announce the transition, don't just repaint.** When a search or filter resolves to empty, the result count and message must reach a screen reader. Render the count/status in an `aria-live="polite"` region (or a `role="status"`) so "No results found" is announced when the list updates — a silently repainted panel leaves non-visual users believing the action did nothing. (See the feedback reference for live-region mechanics.)
- **Don't carry meaning in the illustration alone.** Empty-state art is decorative — mark it `aria-hidden` (or empty `alt`) and put the real message in text, so nothing essential depends on perceiving the image.
- **The primary action is a real control.** The "create" call to action must be a focusable, labeled button/link reachable by keyboard with a visible focus indicator and an accessible name that states the action ("Create your first project"), not a non-semantic clickable `div`.
- **Sufficient contrast on muted styling.** Empty-state text is often deliberately low-emphasis grey; it must still meet contrast minimums — status and instructions failing contrast is a common, quiet WCAG miss.

---

## Good vs bad (for scoring)

```text
BAD                                  GOOD
─────────────────────────────────    ─────────────────────────────────
"No data."                           "No invoices for May 2026."
(no cause, no path, reads broken)    "Invoices appear here once a client
                                      is billed.  [ Create invoice ]"

[ ☹ empty box, no action ]           "All caught up — inbox zero."
(dead end on a first-use screen)      (warm acknowledgement of a cleared
                                      state; not framed as an error)

Search "x" → blank list, no count    "No results for 'reciepts'.
(user can't tell if it ran or          Did you mean receipts?  ·  Clear
 failed; no recovery)                  filters  ·  Browse all documents"
                                      (restates query, surfaces typo,
                                       offers a way out; announced via
                                       aria-live to AT)
```

A scoring heuristic: identify which of the three states each empty surface is, then check it carries the right job — first-use teaches and offers a first action, cleared reassures, no-results restates-and-reroutes — and that none of them fire while content is still loading or read as an error when they aren't one.
