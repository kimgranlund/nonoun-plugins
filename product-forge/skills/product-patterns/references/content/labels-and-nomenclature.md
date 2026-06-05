---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "NN/g — 'Match Between the System and the Real World (Usability Heuristic #2)' (Jakob N. / Maria Rosala). https://www.nngroup.com/articles/match-system-real-world/"
  - "Louis Rosenfeld, Peter Morville & Jorge Arango — *Information Architecture for the Web and Beyond*, 4th ed. (O'Reilly, 2015), ch. on Labeling Systems. ISBN 9781491911686."
  - "Donna Spencer — *Card Sorting: Designing Usable Categories* (Rosenfeld Media, 2009). ISBN 9781933820026."
  - "NN/g — 'Tree Testing: Fast, Iterative Evaluation of Menu Labels and Categories' and 'Card Sorting vs. Tree Testing.' https://www.nngroup.com/articles/tree-testing/ , https://www.nngroup.com/articles/card-sorting-tree-testing-differences/"
  - "NN/g — 'UI Copy: UX Guidelines for Command Names and Keyboard Shortcuts' (Anna Kaley). https://www.nngroup.com/articles/ui-copy/"
---

# Labels and Nomenclature

Labels are the words that _name things_ in a product — menu items, section titles, field names, object types, and the verbs on buttons. They are the most concentrated form of content design: a label is often the only text a user reads before deciding where to click, so a single wrong word can hide a whole feature. Rosenfeld, Morville & Arango treat labeling as one of the four core information-architecture systems (alongside organization, navigation, and search), and the discipline is the same as theirs: a product's labels form a **labeling system** that must be consistent, predictable, and spoken in the user's language — not a pile of independently-chosen words. This is product-side UX writing in its most structural form; it ties directly to information architecture (see `../interaction/navigation-ia.md`).

> The framing to hold onto: **a label is a promise about what's behind it.** Every label sets an expectation — "Reports," "Delete," "Members" — and the user navigates by matching their goal to the label that seems to keep that promise (the "information scent" they follow). Good labels keep the promise so reliably that the user predicts the result before acting. Bad labels — jargon, invented brand-words, the same concept named three different ways — break the scent, and the user clicks, backtracks, and loses trust in the whole system.

## A labeling system, not a bag of words

Labels fail in aggregate, not individually — a label that's fine alone becomes a defect when a sibling contradicts it. Treat labels as a system with system-level properties:

- **Consistency is the first property.** One concept gets one name everywhere. If the object is a "Project" in the nav, it is a "Project" in the button, the empty state, the settings, and the API-facing docs — never "Workspace" here and "Project" there. Inconsistent naming makes users wonder whether they're looking at two different things.
- **One action, one verb — always.** Don't alternate "Delete" / "Remove" / "Trash" for the same operation; each implies a different consequence. Pick the verb that names the real outcome and use it for that operation throughout. (This is the button-consistency rule from `../feedback/microcopy.md`, applied at the system level.)
- **Granularity and scope should match.** Sibling labels in a menu should be roughly the same level of abstraction ("Billing," "Members," "Integrations" — not "Billing," "Members," "Advanced stuff"). Mixed granularity signals a muddled underlying structure.
- **Mirror the object model.** The labels for objects and actions should reflect the real conceptual model of the product. If users think in "documents that live in folders," the labels are "Document" and "Folder" — not internal engineering names ("Node," "Container").

## Speak the user's language

The governing heuristic is Jakob N.'s #2, _Match between the system and the real world_: the system "should speak the users' language, with words, phrases, and concepts familiar to the user, rather than system-oriented terms," and should follow real-world conventions so information appears in a natural, logical order. Applied to labels:

- **User words beat internal words.** Label by what the user calls the thing, not what the team calls it in standups. "Invoices," not "Billing artifacts." "Sign in," not "Authenticate."
- **No invented brand-words in functional labels.** A made-up name for a navigation item ("Synergy Hub," "MyZone") carries no information scent — the user can't predict what's behind it. Brand-flavored naming belongs to brand-forge's identity work; _functional_ labels in the interface must be predictable first. (A product can have a branded _name_ and still label its functions plainly.)
- **Domain terms are correct when the audience owns them.** "Speak the user's language" cuts both ways: in an expert tool, the right label is the precise domain term the user already uses ("Reconciliation," "Refactor"), not a dumbed-down paraphrase. Match the _audience's_ vocabulary, not a generic one.
- **Avoid acronyms and jargon the user doesn't share.** If a term needs a tooltip to be understood, it's usually the wrong label — fix the word before annotating it.

## Button / CTA clarity

Buttons are the highest-leverage labels because they trigger consequences. The canon (NN/g command-name guidance, echoed in `../feedback/microcopy.md`):

- **`verb + noun` that names the outcome.** "Create project," "Send invite," "Delete account" — the user should predict the result before clicking. "OK," "Submit," "Continue" force the user to infer the consequence from context.
- **Label from the user's goal, not the system's mechanics.** "Get my report," not "Execute query." The button names what the user accomplishes, not what the code does.
- **Front-load the meaningful word** so it survives truncation and scanning; buttons are scanned, not read.
- **Match the button to its real effect, especially when destructive.** A button that permanently deletes says "Delete permanently," not "OK" — the label is the user's last honest warning. (Destructive-action confirmation copy: `../feedback/microcopy.md`.)
- **Pair the affordance with the label, don't replace it.** Icon-only controls without text labels force hover or trial-and-error; if an icon is essential, give it an accessible name and, for anything non-obvious, a visible label.

## Naming objects and actions consistently (the IA tie)

Labeling and information architecture are the same problem seen from two angles: IA decides _how things are grouped and related_; labels are _what those groups and relations are called_. A labeling defect is frequently an IA defect wearing a word.

- **Name the object once, then derive everything.** Decide the canonical name for each object type, then every action, menu item, empty state, and message about it inherits that name. This is what makes "the same thing" feel the same across the product.
- **Category labels need information scent.** Menu and section labels must let a user predict their contents at a glance. If users can't tell which bucket holds the thing they want, the labels (or the categories themselves) are wrong — and that's a finding for the IA, not just the copy. (See `../interaction/navigation-ia.md`.)
- **Keep system labels and content labels from colliding.** Utility/system labels ("Settings," "Account," "Help") should read distinctly from content/topical labels so they don't compete for the same meaning.
- **Synonyms are a search concern, not a labeling license.** Users may _call_ a thing several things; that belongs in search synonyms and metadata (so search finds it), not in the visible labels (which must stay singular and consistent). One visible name per concept; many synonyms behind the search box.

## Label testing: validate, don't guess

Labels are guesses about the user's vocabulary and mental model until tested. Two complementary, citable IA-research methods — and a fast informal one — make them empirical:

- **Card sorting (generative).** Give users cards naming content/features and have them group and name the groups; you learn the categories _and the words_ they'd use. Donna Spencer's _Card Sorting_ is the standard reference; open sorts surface the user's own labels, closed sorts test whether your labels fit your categories.
- **Tree testing (evaluative).** Strip away visuals and ask users to find specific items in your proposed label hierarchy; it measures _findability_ — whether your labels lead users to the right place. NN/g's framing: card sorting _generates_ an IA, tree testing _evaluates_ one. Run tree testing after you have candidate labels and before you build.
- **The fast informal check.** The "first-click" / "where would you go to…" test: show the nav and ask where they'd click for a given goal. Wrong first clicks point straight at mis-scented labels.
- **Watch for the tells in any usability session.** Hesitation before clicking, clicking-then-backtracking ("pogo-sticking"), and users renaming things in their own words are all signals the label doesn't match the user's vocabulary.

## Tells of good vs. bad

| Dimension | Good labeling system | Bad |
| --- | --- | --- |
| **Consistency** | One concept → one name, everywhere | "Project" here, "Workspace" there |
| **Action verbs** | One verb per operation; `verb + noun` | "Delete"/"Remove"/"Trash" mixed; "OK"/"Submit" |
| **User's language** | User/domain words, real-world terms | Internal jargon, invented brand-words, unshared acronyms |
| **Scent** | Labels predict what's behind them | "Synergy Hub" — no clue what's inside |
| **Object model** | Labels mirror how users conceive the objects | Engineering names leak into the UI |
| **Granularity** | Siblings at the same level of abstraction | Mixed levels ("Billing," "Advanced stuff") |
| **Buttons** | Name the outcome; honest on destructive acts | Generic/ambiguous; safe choice mislabeled |
| **Validation** | Card-sorted / tree-tested against users | Labels chosen in a meeting, never tested |
| **A11y** | Icon controls have visible/accessible names | Mystery-meat icon-only nav |

The single test: **for every label, can the user predict what's behind it before they act — in their own words?** If a button doesn't name its outcome, a menu item gives no scent, the same object wears two names, or the label is the team's word rather than the user's — the labeling system has broken its promise, and no amount of visual polish fixes a word the user can't decode.

## Boundary: functional labels vs. brand naming

The labels covered here are **functional** — their job is predictability and task-completion in the interface, governed by clarity and the user's vocabulary. The _branded_ names a product gives features or itself (a distinctive product name, a marketing-led feature name) are a brand/identity decision and belong to **brand-forge**. The two coexist: a product can carry a branded name and still label its functions plainly ("Settings," "Send," "Members"). Where a brand name _is_ used as a functional label, it must still earn information scent or be paired with a plain descriptor — a branded label that leaves the user unable to predict its contents has traded findability for flavor, and at a functional surface that trade is a defect. Route brand-naming strategy to brand-forge; keep interface labels in this lane.
