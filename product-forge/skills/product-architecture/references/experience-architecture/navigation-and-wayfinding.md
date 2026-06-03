---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Peter Pirolli & Stuart Card, “Information Foraging,” *Psychological Review* 106(4), 643–675 (1999) — origin of information scent, developed at Xerox PARC."
  - "Peter Pirolli, *Information Foraging Theory: Adaptive Interaction with Information* (Oxford University Press, 2007)."
  - "Louis Rosenfeld, Peter Morville & Jorge Arango, *Information Architecture for the Web and Beyond* (O'Reilly, 4th ed. 2015) — embedded vs. supplemental navigation systems."
  - "Nielsen Norman Group — Information Foraging: A Theory of How People Navigate on the Web (nngroup.com/articles/information-foraging)."
  - "Steve K., *Don't Make Me Think, Revisited* (New Riders, 2014) — the wayfinding questions and the persistent navigation conventions."
---

# Navigation & Wayfinding

This is the working method for designing navigation as a **wayfinding system** — the structure-to-skeleton bridge that lets a user always answer three questions: **where am I, where can I go, and how do I get back.** It is the architecture counterpart to the pattern-level navigation reference (which covers menus, tabs, breadcrumbs, hub-and-spoke as UI controls); here the concern is the _system_ — the layered set of navigation that surfaces an information architecture, and the cognitive theory (information scent) that governs whether users can actually find their way through it. The load-bearing idea: **navigation is not chrome, it is the user's model of the space.** When users get lost, it is almost never because a menu was styled badly — it is because the navigation system failed to communicate the structure, or the links gave off no scent.

## The three navigation systems (Rosenfeld/Morville/Arango)

A mature product layers three kinds of navigation, each doing a job the others can't. The classic Rosenfeld/Morville/Arango ("the polar bear book") taxonomy splits navigation into **embedded** (built into the page) and **supplemental** (outside the main structure), and the embedded kind into three scopes:

| System | Scope | Job | Lives where |
| --- | --- | --- | --- |
| **Global / primary** | The whole product | The persistent map — communicates total scope, enables re-orientation from anywhere | Top-level, on every screen |
| **Local / secondary** | Within a section | Lateral movement between siblings without climbing back to a hub | Within a section, contextual to where you are |
| **Contextual / inline** | A specific piece of content | Links _relevant to this exact thing_ — "related," "see also," cross-references embedded in content | Inside the content itself |

Supplemental systems sit outside this structure and serve as safety nets and accelerators: **search** (when browsing fails or is slower), **sitemaps / indexes** (a flattened overview of the whole), and **breadcrumbs** (showing the path back up). The architectural decision is not "which menu" but **which combination of these systems the product needs** — a deep content site needs all three embedded scopes plus search; a focused tool may need only global plus contextual.

## The three wayfinding questions

Krug's framing reduces good navigation to three questions a user must always be able to answer at a glance. Use them as the acceptance test for any screen.

1. **"Where am I?"** — Orientation. The user can tell, without thinking, what part of the product they're in. Provided by: a highlighted current item in global nav, a breadcrumb, a clear page heading, section-distinct local nav. NN/g calls failing to indicate the current location the single most common navigation mistake.
2. **"Where can I go?"** — Options. The available moves are visible (not hidden behind ambiguous icons), and their labels predict where they lead (scent — see below).
3. **"How do I get back?"** — Reversibility. There is always a way up (to the parent/hub) and a way out (cancel, home). A user who feels they can't retreat navigates timidly or not at all.

A screen that can't answer all three is a disorientation defect regardless of how it looks. The home/logo-to-home convention, persistent global nav, and a visible "you are here" are the cheap, expected mechanisms that answer them — and Jakob's Law applies: users expect these to work the way they do everywhere else.

## Information scent (Pirolli & Card)

The deepest model of _why_ navigation succeeds or fails comes from **Information Foraging Theory**, developed by **Peter Pirolli and Stuart Card at Xerox PARC**, formalized in their 1999 _Psychological Review_ paper "Information Foraging" and expanded in Pirolli's 2007 book. The theory borrows from how animals forage for food: just as an animal uses **scent** to judge whether prey is near and which direction to move, a user reads **information scent** — the cues (link labels, snippets, icons, surrounding context) that signal whether a path leads toward their goal.

The mechanics that matter for design:

- **Users follow the strongest scent.** At every choice point, the user estimates which link is most likely to lead to their target and clicks it. Navigation labels are scent; weak or ambiguous labels emit weak scent and users guess wrong.
- **Users forage by "patches" and satisfice.** People don't read exhaustively; they assess a "patch" of information, take what's good enough, and move on. They leave a patch when the expected value of staying drops below the expected value of looking elsewhere — the same calculus an animal uses to abandon a depleted feeding ground.
- **Low scent causes abandonment, not persistence.** When the cues stop pointing toward the goal — when every link looks equally unpromising — users don't dig harder; they leave (back-button, or the site entirely). This is why "clever" or jargon labels are so costly: they sever the scent trail. NN/g's practical translation: **make the scent strong by using the user's words, showing where links lead, and keeping the trail unbroken from the entry point to the goal.**

The design moves that strengthen scent: descriptive link labels in the user's vocabulary (not invented brand terms), informative snippets/previews, trigger words that match the user's goal, and consistent labeling so a category name on the menu matches the heading on the page it leads to. The moves that destroy it: vague labels ("Solutions," "Resources"), the same generic CTA repeated everywhere, and a mismatch between what a link says and what the destination delivers (a broken-promise that teaches users to distrust the navigation).

## Designing the navigation system (procedure)

1. **Start from the IA, not the menu.** Decide the structure first (the content's real shape — hierarchical, sequential, hub-and-spoke, matrix); navigation _expresses_ that structure. A menu can't fix a wrong IA.
2. **Choose the layered systems the product needs.** Global always; local where sections have siblings worth lateral movement; contextual where content relates to other content; search/sitemap as supplemental safety nets sized to the product's depth and breadth.
3. **Make scent the priority in labeling.** Label every navigation element in the user's words; ensure the menu label matches the destination heading (consistency is scent reinforcement).
4. **Guarantee the three questions on every screen.** Audit each screen for "where am I / where can I go / how do I get back." Add the current-location indicator, the available moves, and the way back/up wherever any is missing.
5. **Keep depth shallow and the trail unbroken.** Prefer flatter structures (clicks are cheap, getting lost is expensive); ensure no path requires the user to traverse a scentless step to reach their goal.

## What to check (good vs. bad)

| Dimension | Bad | Good |
| --- | --- | --- |
| **System layering** | One menu doing every job | Global + local + contextual chosen to fit the IA, with search/sitemap as needed |
| **"Where am I?"** | No active state, no breadcrumb, generic heading | Highlighted current item + breadcrumb + clear, matching heading |
| **"Where can I go?"** | Options hidden behind ambiguous icons | Visible options with scent-bearing labels |
| **"How do I get back?"** | No way up or out; back-button is the only escape | Logo-to-home, persistent global nav, explicit cancel/up |
| **Information scent** | Vague/jargon labels; CTA repeated; label ≠ destination | User's-words labels; previews; menu label matches destination heading |
| **Scent continuity** | Trail breaks — a scentless step between entry and goal | Unbroken scent from entry point through to the target |
| **IA fit** | Navigation mirrors the org chart | Navigation expresses the content's real structure |
| **Depth** | Deep tree burying content; users abandon mid-forage | As flat as content allows; goal reachable on a strong-scent path |

The fastest single test: open any deep screen cold and ask the three questions. If you can't immediately answer all three, the navigation system has a hole exactly there. The second-fastest: read the menu labels and predict, for each, what's behind it — then check. Every wrong prediction is a scent failure your users are also making.

## One labeled caveat

The three-systems taxonomy (global/local/contextual, embedded vs. supplemental) is the standard Rosenfeld/Morville/Arango model from _Information Architecture for the Web and Beyond_ and is uncontroversial. Information Foraging Theory and information scent are correctly attributed to Pirolli & Card (PARC, 1999 _Psychological Review_ paper) and Pirolli's 2007 OUP book — these are real, peer-reviewed primary sources; the conceptual claims (scent, patches, satisficing, leaving when scent drops) are accurately characterized, but verbatim quotations should be confirmed against the paper/book before publication. The three wayfinding questions are Krug's well-known formulation from _Don't Make Me Think_; the exact phrasing here is a faithful paraphrase rather than a direct quote.
