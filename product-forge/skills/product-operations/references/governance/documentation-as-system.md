---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Write the Docs community — “Docs as Code” (writethedocs.org/guide/docs-as-code) — write docs with the same tools and workflows as code; the codebase as single source of truth."
  - "Andrew Etter, *Modern Technical Writing: An Introduction to Software Documentation* (2016) — lightweight markup, docs-as-code, static site generators."
  - "Diátaxis (Daniele Procida) — the four documentation modes: tutorials, how-to guides, reference, explanation (diataxis.fr)."
  - "Anne Gentle, *Docs Like Code* (2017) — treating documentation with version control, review, and CI."
---

# Documentation as a Living System

Documentation is not a deliverable you finish; it is a system you maintain, and the default state of every doc is **drift** — the moment the artifact it describes changes, the doc is wrong, and it stays wrong until someone notices and pays to fix it. The expensive failure mode is not a missing doc; it's a confidently wrong one that a teammate trusts and acts on. The discipline that contains drift is **docs-as-code**: write documentation "with the same tools as code, following the same workflows," version it, review it, and — critically — change it _in the same pull request_ as the thing it documents. This file is the working method for keeping documentation coherent across surfaces, deciding what to write down versus what to let the artifact carry, and treating drift as the defect it is.

> **Docs-as-code (Write the Docs):** with this approach "the Single Source of Truth becomes the codebase itself." The biggest win is "eliminating documentation drift by updating docs and code in the same pull request" — and adding "automated checks… to find broken links, misspellings, or obsolete references… the same way [you] find code."

## Single source of truth, and why it's hard

A single source of truth (SSOT) means each fact lives in exactly **one** authoritative place, and every other surface either links to it or is generated from it. The principle is easy to state and hard to hold, because facts get _copied_ — a description written in a PRD gets restated in a README, a marketing page, a help article, and a slide, and now there are five copies that must change together and never do.

- **The copies are the bug.** Every duplicated fact is a future inconsistency with a probability approaching one. The CLAUDE.md convention in this very repo names it directly: keeping a plugin's four descriptions (marketplace entry, manifest, README, changelog) in sync is required, and "drift between them is a defect." That is SSOT stated as a contract.
- **Prefer one source + transclusion/generation over synchronized copies.** Where a fact must appear in many places, _generate_ those places from the one source (API docs from the schema, a component's props table from its type) rather than hand-copying. A generated surface can't drift; a copied one always will.
- **Where you can't generate, link.** If the canonical statement of scope lives in the spec, the README points _at_ the spec rather than paraphrasing it. A pointer can go stale (the link breaks — catch it with a link-checker) but it can't quietly contradict the source the way a paraphrase does.

## Keeping descriptions in sync across surfaces

Product facts fan out across many surfaces — spec, README, changelog, in-app copy, help center, sales deck, store listing. The governance problem is that each surface has a different owner and a different update cadence, so they desync silently.

- **Designate the canonical surface per fact, explicitly.** For "what this product does and for whom," name the one doc that's authoritative; everything else defers to it. Ambiguity about which surface is canonical guarantees that two of them will disagree and no one will know which is right.
- **Bundle the fan-out into one change.** When the canonical fact changes, the same change-set updates (or regenerates) every dependent surface. This is the repo's "keep the four descriptions in sync" rule operationalized: a scope change that touches the manifest but not the README is an incomplete change, the way a code change that breaks a test is incomplete.
- **Add a drift trip-wire.** A CI check, a lint, or a review checklist that fails when surfaces disagree turns "remember to update all five" (which fails) into "the build won't pass until you do" (which holds). Structure beats diligence — humans forget; the check doesn't. (This mirrors how the brand and plugin tooling in this repo mechanize structural rules via hooks and CI gates rather than relying on reviewer memory.)

## Docs-as-code: the operating model

Docs-as-code is the practice that makes all of the above enforceable. It treats prose like source.

- **Plain-text, version-controlled docs (Etter, Gentle).** Markdown/lightweight markup in the repo, under the same version control as the code. You get diffs, blame, history, and the ability to revert — the doc's evolution is as legible as the code's.
- **Docs reviewed in the same PR as the change.** The reviewer sees the behavior change and the doc change together and can refuse to merge one without the other. This is the mechanism that actually prevents drift; everything else is exhortation.
- **CI on the docs.** Automated link-checking, spell/style linting, and reference validation run on every change — "obsolete references" fail the build "the same way [you] find code." A broken doc reference should break CI, not wait for a user to stumble on it. (This repo does exactly this: a reference-lint gate fails when doc/command references don't resolve.)
- **Generate what can be generated.** API references from schemas, CLI docs from `--help`, type tables from types. Generated docs are drift-proof by construction; reserve hand-written prose for the things only a human can explain.

## What to document vs. what to let the artifact carry

More documentation is not better. Every doc is a liability that can drift, so the governance question is **what _must_ be written down because the artifact can't carry it.** The Diátaxis split (tutorials / how-to / reference / explanation) is a useful lens: reference can often be _generated_ from the artifact; explanation usually can't.

- **Let the artifact carry the "what."** Well-named code, a clear type, a self-evident UI, a generated API reference — these state _what_ a thing is better than prose ever will, and they can't drift from themselves. Documenting in prose what the code already says plainly just creates a second copy to maintain. Comments that restate the line below them are this anti-pattern in miniature.
- **Write down the "why" and the "context."** The reasoning, the rejected alternatives, the constraints, the trade-offs accepted — the artifact cannot carry these, and they are exactly what's lost when people rotate. This is the same content an ADR captures (see `decision-records-adr.md`); decision context is the highest-value, least-substitutable documentation there is.
- **Write down what crosses a boundary.** A contract another team or another system depends on (an API shape, an integration assumption, an SLA) must be explicit, because the dependent party can't read your code or your mind. Internal mechanics that no one downstream depends on can stay in the code.
- **Don't document what you'll never maintain.** A doc you won't update is worse than no doc — it will be trusted and it will lie. If you can't commit to keeping a fact current, either generate it, link to its source, or leave it out. Aspirational documentation is drift waiting to happen.

## The cost of drift

Name the cost so the maintenance investment is justified, not assumed.

- **Erosion of trust, then abandonment.** "Version drift is where critical artifacts fall out of sync and people stop trusting the system." Once a team catches the docs being wrong twice, they stop reading them — and then even the correct docs are dead weight. Trust is the asset; drift spends it.
- **Wrong action on confident misinformation.** A doc that's _missing_ makes someone ask; a doc that's _wrong_ makes them act incorrectly. The confidently-stale doc is the dangerous one precisely because it doesn't signal its own staleness.
- **Compounding reconciliation cost.** Drift across N copies grows worse the longer it's left — by the time someone reconciles, they must first _discover_ which of the contradictory surfaces is true, an archaeology tax that dwarfs the original cost of SSOT.

## Tells of good vs. bad documentation systems

| Dimension | Bad (drift-prone) | Good (living system) |
| --- | --- | --- |
| **Source of truth** | Same fact copied across many surfaces | One canonical source; others generated or linked |
| **Sync mechanism** | "Remember to update the others" (relies on diligence) | Bundled in one change; a trip-wire fails the build on disagreement |
| **Locality** | Docs in a separate wiki, updated separately | Docs in the repo, changed in the same PR as the artifact |
| **CI** | No checks; broken refs found by users | Link-check, lint, reference-validation on every change |
| **Generation** | Hand-written API/reference docs that go stale | Reference generated from schema/types — drift-proof |
| **What's documented** | Prose restating what the code already says plainly | The why/context/contracts the artifact can't carry |
| **Maintenance honesty** | Aspirational docs no one will keep current | Only what the team commits to maintain; the rest linked or generated |
| **Drift posture** | Drift noticed when it breaks something | Drift treated as a defect, caught at change time |

The fastest single test: pick one product fact (what it does, its pricing, a key API shape) and find it on three surfaces. If they disagree — or if you can't tell which is authoritative — the documentation isn't a system, it's a pile of copies, and it's already lying to someone. A living system has one answer, and a mechanism that won't let the others diverge from it.

## One labeled caveat

The docs-as-code quotes ("the Single Source of Truth becomes the codebase itself," "updating docs and code in the same pull request," "obsolete references… the same way [you] find code") and the version-drift line ("critical artifacts fall out of sync and people stop trusting the system") are paraphrased/quoted from Write the Docs and from technical-documentation blog sources cross-checked in this session, not re-read from a single canonical print source; treat them as faithful summaries rather than page-cited quotations. The Diátaxis four-mode model is attributed to Daniele Procida's framework; the docs-as-code practice to Etter's _Modern Technical Writing_ and Gentle's _Docs Like Code_. The repo-specific examples (the "four descriptions in sync… drift is a defect" rule and the reference-lint CI gate) are this repository's own conventions, included to show the principle mechanized rather than as external sourcing.
