---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Nielsen Norman Group — Infinite Scrolling: When to Use It, When to Avoid It (nngroup.com/articles/infinite-scrolling-tips)"
  - "Nielsen Norman Group — Infinite Scrolling Is Not for Every Website (nngroup.com/articles/infinite-scrolling)"
  - "Nielsen Norman Group — Item-List Pagination Preferences and \"View All\" (nngroup.com/articles/item-list-view-all)"
  - "Laws of UX — Zeigarnik Effect (lawsofux.com/zeigarnik-effect)"
  - "Laws of UX — Peak-End Rule (lawsofux.com/peak-end-rule)"
---

# Feeds & Content Consumption

A feed is a long, often unbounded list of homogeneous items the user scans, browses, or grazes — a news river, a social timeline, a product grid, a search-results list. The defining design decision is the **paging mechanism**: how the next batch of items arrives. The three viable answers — infinite scroll, pagination, and the Load More hybrid — are not stylistic preferences; each optimizes for a different _user task_, and choosing wrong actively obstructs the user. A second, sharper question sits underneath: feeds are where engagement mechanics and user wellbeing collide, so the choice also carries an ethical load that this reference makes explicit.

---

## When to use which paging mechanism

NN/g's controlling rule: there is no universally superior option — it "always depends on the specific circumstances of your website and the goals that your users want to accomplish." Match the mechanism to the task.

| Mechanism | Use when the user is… | Why | Cost |
| --- | --- | --- | --- |
| **Infinite scroll** | Grazing homogeneous items with **no specific goal** — entertainment, news, social. | "Minimizes interaction cost and increases user engagement"; uninterrupted flow keeps the user in the stream. | Footer becomes unreachable; back-button loses position; weak for findability; accessibility problems. |
| **Pagination** | **Goal-directed** — finding a specific item, comparing across a long list, or judging effort. | "A beginning and an end"; the user can anticipate scan effort and feels "a happy sense of completion." Gives control over whether to continue. | Each page change is an interruption that can break the task and shed momentum. |
| **Load More (hybrid)** | Mostly grazing, but the footer matters and you want users to feel in control. | Restores footer access and signals "more exists" while keeping flow; an explicit choice to continue. | "Interaction cost increases — users have to click," which can reduce total consumption. |

NN/g's plain statement of fit: infinite scroll "typically works best for situations where users will want to scroll through homogeneous items with no particular task or goal in mind." Conversely, avoid it when users need to "find something specific," "compare items in a long list," or "inspect only a few items at the top of the list" — those are pagination's job.

A practical rule of thumb: **discovery → infinite scroll; retrieval → pagination; in between → Load More.** A social timeline is discovery. A search results page, an admin table, or a "find my order" list is retrieval and should paginate.

---

## The known costs of infinite scroll (and their mitigations)

Infinite scroll's downsides are well documented; if you choose it, design around them.

- **The footer is unreachable.** A perpetual content stream means the page bottom (links, legal, support, sitemap) keeps receding. NN/g: classic infinite scroll "can make it impossible to access the footer." _Mitigation:_ a Load More button, or a sticky/parallel footer, or move footer links into the header/menu.
- **The back button destroys position.** Open an item, hit Back, and "they will find themselves at the top of the list, having to scroll down through screenfuls and screenfuls of already seen content." _Mitigation:_ persist scroll position and loaded items on back-navigation; restore the user where they left.
- **Findability and "where am I?"** No page numbers means no sense of how far in, no way to return to "around item 200," no anticipation of effort — the very things pagination provides.
- **Accessibility.** Keyboard users must "tab through content link by link," and "screen-reader users will only see the first chunk of the list." _Mitigation:_ see the accessibility section — Load More with a managed focus target is the most accessible of the three.

---

## End-of-feed (design the bottom on purpose)

Every finite feed eventually ends, and an infinite mechanism still terminates when the data does. The end is a designed moment, not an accident:

- **Mark the end explicitly.** A clear "You're all caught up" / "End of results" terminator tells the user there is nothing more, so they stop scrolling into a void and don't read the stop as a load failure. This is Visibility of System Status applied to the feed's tail.
- **Offer an onward action at the end.** The bottom of a finished feed is a natural place to re-route — refresh, switch sort/filter, browse a related stream, or surface "since you're here" content — turning a dead end into a branch.
- **Distinguish "end" from "still loading" from "error."** Three different tail states: a loading affordance (more is coming), an end marker (nothing more), and an error with **Retry** (fetch failed). Collapsing them leaves the user unable to tell "done" from "broken."
- **"Caught up" is a wellbeing affordance too.** A definitive end (some apps inject a synthetic "You're all caught up" boundary) gives a natural stopping point — the opposite of an engineered bottomless well.

---

## The engagement / dopamine trade-off (Zeigarnik, and the ethics)

Infinite scroll's "engagement" advantage is the same property that makes it a wellbeing hazard, and a serious pattern library names both sides.

The relevant principle is the **Zeigarnik Effect** — Laws of UX, after Soviet psychologist Bluma Zeigarnik (1900–1988): _"People remember uncompleted or interrupted tasks better than completed tasks."_ An unbounded feed is, by construction, a permanently uncompleted task: there is always one more item just below the fold. The interface exploits the mind's pull toward the unfinished — there is no completion, so there is no natural stopping cue, and the user keeps going.

Laws of UX presents the effect as a usable, mostly _constructive_ lever — its takeaways are about motivating **task completion**: invite content discovery "by providing clear signifiers of additional content," show "clear indication of progress … to motivate users to complete tasks," and even use "artificial progress towards a goal." Note the framing: progress meters and signposted next content help a user _finish something they came to do_. A bottomless graze-feed inverts that — it manufactures endless incompleteness with no goal to complete, which is the dark side of the same mechanism.

The trade-off, stated plainly:

- **For the operator:** infinite scroll lowers interaction cost and raises time-on-feed and session length — the metrics a graze product is usually optimized for.
- **For the user:** the absence of a stopping cue can convert "I'll check the feed" into a session far longer than intended — the design profits from the user's _failure_ to stop.

This is why the **end-of-feed marker, "caught up" boundaries, and Load More** are not just usability fixes — they are the levers that return a stopping cue to the user. The honest position for a pattern library: infinite scroll is the right call for genuine discovery surfaces, but pairing it with explicit completion signals (and not engineering artificial bottomlessness onto goal-directed surfaces) is the difference between reducing friction and engineering compulsion. Related: the **Peak-End Rule** (Laws of UX) — people judge an experience by its peak and its **end** — argues that a graceful, satisfying feed _ending_ improves how the whole session is remembered, which aligns the wellbeing move with the experience-quality one.

> **Single-source / interpretive caution.** The Zeigarnik–infinite-scroll connection and the "manufactured incompleteness" framing are this reference's synthesis of the cited Laws of UX principle applied to feeds — Laws of UX states the effect and constructive takeaways but does not itself frame infinite scroll as exploitative. The underlying Zeigarnik finding is early-20th-century psychology with a mixed and contested replication record; treat the _mechanism_ as a design heuristic, not a settled causal law.

---

## Variants

- **Reverse-chronological vs ranked/algorithmic feed.** A time-ordered river (predictable, user-controllable) vs an engagement-ranked feed (sticky, opaque). Ranking raises the wellbeing stakes and the transparency obligation.
- **Pull-to-refresh + prepend.** New items arrive at the top on demand; pair with a "N new posts" pill so the user controls when the feed jumps rather than having content shift under them.
- **Virtualized / windowed lists.** Rendering only on-screen rows for performance on long feeds — an implementation technique under any of the three mechanisms (mind its accessibility implications: off-window items aren't in the DOM for AT).
- **"View all" vs paged.** NN/g found users often _prefer_ a "View all" option for moderate lists they want to scan or Ctrl-F; paginate the long, paginate-to-compare cases.
- **Cursor (keyset) vs offset paging.** A backend concern with UX fallout — offset paging on a fast-changing feed causes duplicated/skipped items at page boundaries; cursor paging avoids the drift.

---

## Anti-patterns

- **Infinite scroll on a goal-directed surface.** Search results, order history, or a comparison list with no page numbers — the user can't anchor, compare, or return to a spot. NN/g's clearest misuse.
- **Unreachable footer with no Load More.** Hiding essential links below a stream that never bottoms out.
- **Position loss on back.** Sending the returning user to the top of the feed after they open one item.
- **Endless feed with no terminator.** No "caught up," no end marker — the user can't tell "nothing more" from "still loading," and there's no stopping cue.
- **Engineered bottomlessness on a finite dataset.** Looping or padding a feed so it _feels_ infinite when the real content has ended — manufacturing incompleteness to extend sessions.
- **Content that shifts under the reader.** Auto-prepending new items (or layout shift from late-loading media) that bumps what the user is reading; stage new content behind an explicit control.

---

## Accessibility

- **Load More is the most accessible mechanism; manage focus after it.** When new items load, move focus to the first newly-loaded item (or announce "N more loaded") so keyboard and screen-reader users can reach the new content and aren't stranded — NN/g flags that classic infinite scroll leaves keyboard users tabbing link-by-link and screen-reader users seeing only the first chunk.
- **Announce batch loads via a live region.** A visually-hidden `aria-live="polite"` status ("Showing 40 of many") tells AT users that more arrived, since a silent DOM append is invisible to them.
- **Keep the footer and key links reachable without infinite scrolling.** Provide header/menu access to anything that would otherwise live only in an unreachable footer.
- **Virtualized lists must expose totals and current range.** With most rows absent from the DOM, supply `aria-setsize`/`aria-posinset` (or equivalent) so AT can convey list length and position; otherwise the list appears tiny and unnavigable.
- **Respect reduced motion.** Honor `prefers-reduced-motion` for feed animations, auto-advancing media, and scroll-triggered effects.

---

## Good vs bad (for scoring)

```text
BAD                                   GOOD
──────────────────────────────────    ──────────────────────────────────
Search results, infinite scroll,      Search results paginated, page count
no page count, no "of N"              shown, "1–20 of 412" — user can
(can't compare, can't return,          anchor, jump, and feel completion
 footer unreachable)

Timeline scrolls forever, no end,     Timeline with "You're all caught up"
auto-prepends posts mid-read          terminator + onward links; new posts
(no stopping cue, content jumps)       staged behind a "12 new posts" pill

"Load more" appends items, focus      "Load more" appends items, focus moves
stays on the button                   to first new item, "20 more loaded"
(keyboard user can't reach new rows)   announced via aria-live
```

A scoring heuristic: name the user's task on the surface (discovery vs retrieval), check the paging mechanism fits it, confirm the **end** of the feed is an explicit designed state, and verify the design returns a _stopping cue_ to the user rather than engineering bottomlessness — then check focus management and live-region announcements on each batch load.
