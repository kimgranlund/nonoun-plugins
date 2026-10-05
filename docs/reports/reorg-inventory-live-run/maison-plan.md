# Reorganization plan: ui-kit-maison at 01951d4e

## Summary

- The inventory reports 230 documents, 10 skipped, and 2 folders without an entry file. The flags are `broken_links` 5, `duplicate` 42, `misplaced` 10 and `orphan` 2. No `stale` or `oversized` rows were reported.
- After opening the backing documents, no file needs to move and none needs to merge.
- Three small changes are worth making:
  1. 🟡 Rewrite 5 ticket links in 4 specs.
  2. 🟢 Add 2 `AGENTS.md` entry files.
  3. 🟢 Link the 2 orphans into their parents.
- The other flags are leads that dissolve on inspection. The reasons are below, so nobody re-derives them.

## Moves

None proposed. Each `misplaced` row group stays where it is:

- `src/components/{button,card,input,select}/README.md`, `select/listbox/README.md` and `select/listbox/option/README.md` (`misplaced`, suggest `docs/reports`):
  - The "4 of 6" links are inbound from `docs/reports/2026-10-01-*.sha256` hash manifests, not prose links.
  - `docs/reports` is a frozen path in `docs/layout.md`.
  - A component README belongs beside its `contract.json`.
- `.agents/skills/gen-ui-component/SKILL.md` and `.agents/skills/gen-ui-review/SKILL.md` (`misplaced`, suggest `specs/`):
  - Skills are found by their `.agents/skills/<name>/SKILL.md` location.
  - Linking to specs is what a skill does.
- `docs/reference/gen-ui-system/specs/gen-ui-recipes.md` (`misplaced`, suggest the audit folder):
  - The evidence is inbound from `audit-snapshot.json`, `gen-ui-gap-analysis.json` and `gen-ui-gap-analysis.md`, which cite every spec.
  - Moving a spec into dated evidence is the wrong direction.
- `examples/application-patterns/component.md` (`misplaced`, suggest `advanced-workflows`):
  - It documents the sibling `.js` and `.html` files in its own folder (Glob).
  - Two of three links is thin evidence.

## Merges

None proposed.

- The 40 README rows flagged `duplicate` (`src/components/*` and `src/layout/*`) are templated files of the same kind, intentionally alike.
  - I opened `agent-reasoning/README.md` and `layout/grid/README.md`. Both start with "Author semantic intent in contract.json", then carry links that differ per component.
  - A grep found that sentence only in READMEs, so no script emits it.
  - Every one of these rows is cited by the generated `gen-ui/observations/button.installed.json`, so a merge would stale it.
  - `select/README.md` and `select/listbox/README.md` flag each other because they are parent and child of one family and link to each other.
  - Keep all 40.
- `.agents/skills/gen-ui-recipes/SKILL.md` and `.agents/skills/gen-ui-system/SKILL.md` (`duplicate`):
  - The two "Distribution boundary" and "Structured authority" paragraphs appear in all 10 skills (grep count 1 each).
  - These two differ in frontmatter `name`, `description`, Workflow and linked spec.
  - Merging would delete a routing entry and break the `CORPUS.md` and `audit-snapshot.json` inbound links.
  - Keep both. Hoisting the shared paragraphs would be a content change outside this plan.

## New entry files

- 🟢 `docs/reference/AGENTS.md` (`docs/reference`, 10 documents, no entry file).
  - `README.md` already exists, and three tests cite it (inbound: `tests/first-wave-docs.spec.js`, `second-wave-docs.spec.js`, `third-wave-docs.spec.js`). Add alongside, do not rename.
  - Scope: "Reference docs. Start at README.md. The Gen UI system lives in gen-ui-system/, which README.md does not link."
- 🟢 `docs/reference/gen-ui-system/specs/AGENTS.md` (11 documents, no entry file).
  - Scope: "Eleven SPECs, one per subsystem. Read gen-ui-system.md first, then only the SPEC the task needs."
  - Source: the parent `AGENTS.md` read order. It adds nothing new, so it is low value but cheap.
- 🟢 `docs/maintenance/README.md` is not a `no_entry_file` row. It is the fix for the orphan below.

## Links to rewrite

No move is proposed, so no move breaks a link. These are the `broken_links` rows and the orphans.

- 🟡 `docs/reference/gen-ui-system/specs/gen-ui-authoring.md` (2 links), `gen-ui-ontology.md` (1) and `gen-ui-system.md` (1):
  - Rewrite `.sdlc/tickets/0059-theme-context-provider/theme-context-contract.md#...` to `.sdlc/tickets/.0059-theme-context-provider/theme-context-contract.md#...`.
  - The target exists at the dot-prefixed path.
  - Both anchors exist (headings "Immediate bootstrap selection" at line 5 and "Integration and implementation entry" at line 39).
- 🟡 `docs/reference/gen-ui-system/specs/gen-ui-components.md` (2 links):
  - Rewrite `.sdlc/tickets/0046-.../interfaces-v1.md` and `policy.md` to `.sdlc/tickets/.0046-gen-ui-source-layout-reconciliation/`.
  - Both files exist there.
- Risk on all five links:
  - The edit is in `docs/`, nothing under `.sdlc/` changes.
  - `.0059.../step-1/final-hashes.json` lists three of these specs, and `.0046.../step-1/after-hashes.json` lists `gen-ui-components.md`. Editing makes those frozen receipts stale.
  - I did not check whether a live gate reads those two files. Grep for a reader before applying. If one exists, leave the links and record that as the reason.
  - The specs will also depend on a closed-ticket archive path. If the archive is pruned, they break again.
- `src/components/button/component.md` (`broken_links`, "…"):
  - Line 46 is `<a href="…">` inside example prose, so the link extractor misread example markup.
  - The file is generated. Leave.
- `examples/fourth-wave-domain/component.md` (`orphan`):
  - Add one line to `examples/fourth-wave-domain/README.md`, a 3-line file with no inbound links: "Specimen contract: [component.md](component.md)."
  - Alternative: link it from `examples/component.md`, which already links `fourth-wave/component.md` at line 52. That also makes the folder reachable from the index, but I only grepped that file.
- `docs/maintenance/gen-ui-audit-2026-10-03/implementation-plan.md` (`orphan`):
  - Create `docs/maintenance/README.md` listing the audit folder's implementation plan and gap analysis.
  - `gen-ui-gap-analysis.md` has only the orphan as inbound, so it becomes reachable too.
  - `docs/layout.md` names `maintenance/` as a home, but `docs/AGENTS.md` Contents omits it.
  - That Contents list sits inside `sdlc-lite:managed` markers. Do not hand-edit it. After adding the README, re-run the onboard setup so `maintenance/` appears.
  - Fallback: a bullet under "Proposed topics" in `docs/AGENTS.md`, outside the markers, as `gen-ui-evaluation/` already does.
  - Do not touch the dated files.

## Leave alone

- `.sdlc/` is frozen. Nothing is proposed there.
- `docs/reports/` is a frozen path (`docs/layout.md`), and its `.sha256` manifests are snapshot evidence.
- `docs/maintenance/gen-ui-audit-2026-10-03/` is dated evidence. Only a new README goes beside it.
- Every `src/**/component.md` is generated, and the READMEs and skills say not to edit it.
- The 40 templated READMEs and the 6 "misplaced" READMEs stay.
- Skill locations stay.
- `gen-ui/observations/button.installed.json` is generated.
- `examples/application-patterns/component.md` and the `specs/gen-ui-recipes.md` spec stay.

## Not read

Opened in full:
- the 2 skill duplicates
- `agent-reasoning/README.md` and `layout/grid/README.md`
- `docs/AGENTS.md`, `docs/layout.md`, `docs/reference/README.md`
- `docs/reference/gen-ui-system/AGENTS.md`
- both `examples/fourth-wave-domain/` files

Opened in part:
- `implementation-plan.md`: first 14 lines only
- `button/component.md`: grep for "…" only
- `examples/component.md` and `examples/README.md`: grep only, and long lines were omitted from the output
- `gen-ui-gap-analysis.md`: its JSON row only
- `.sdlc/` files: greps only (anchors, hash-file counts), nothing proposed there

Not opened:
- the other 38 of the 40 duplicate READMEs
- about 100 `component.md` files
- 9 other specs, `specs/gen-ui-recipes.md`, `CORPUS.md`, `REVIEW-UPSERTS.md`, `gen-ui-system/README.md` and the 2 templates
- `docs/reports/*`, `docs/gen-ui-evaluation/*` and the other 8 `docs/reference/*` files
- `examples/advanced-workflows/*` and the other `fourth-wave*` folders
- `gen-ui/README.md`, `geometry/README.md`, `scripts/*`, `tests/README.md`, `src/AGENTS.md`, root `AGENTS.md` and `README.md`
- the other 8 skills
- the three `tests/*-docs.spec.js` files that cite `docs/reference/README.md`
- the onboard script and `tickets.py`, so the managed-block refresh and the dot-prefix ticket convention are inferred, not verified