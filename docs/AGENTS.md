# Documentation

Read [the index](README.md) for the full list. Pick the topic for the task; read one file, not the folder.

| Topic | Holds | Read it for |
|---|---|---|
| `specs/sdlc-lite/` | The lane design, cost control, pillars, fleet config, solo lane contract, gate lock admission design (for review) | How lanes are chosen and how cost is controlled; the evidence for solo as the default is [the benchmark](reports/solo-vs-lean-benchmark-2026-10-04.md) |
| `specs/ticket-stages/`, `specs/repo-onboarding/` | The `.sdlc` router, ticket root and mailbox design; entry-file and docs-layout design for adopting repositories | Changing `.sdlc/` layout, messages, `onboard.py` or its templates |
| `specs/generative-constructs/` | Progressive Context specifications | Changing the Progressive Context plugin |
| `references/` | Runner and ticket internals, Claude hooks, Codex execution, packaging | Changing runner, hook, Codex adapter or marketplace behavior |
| `planning/` | Unbuilt proposals: sub-agent mode, the idle-host watcher, reorganization, the docs schema | Before building one; a built one moves into `specs/` |
| `reports/` | Dated evidence, including the [readiness and recovery trials](reports/readiness-recovery-validation.md) | What was verified; history, not instructions |

<!-- sdlc-lite:managed:start v1 sha256:a5d4c1a44546 -->
# Documents

Pick one home from the table, then read one file. Placement effect unproven; see the docs-schema design.

| Home | Holds | Never holds |
|---|---|---|
| `specs/` | What the system is and must do; edited in place | Proposals, dated evidence, steps |
| `planning/` | Proposals, roadmaps, plans under review (`status:`) | What exists today |
| `decisions/` | One numbered decision per file, immutable once accepted | Narrative design |
| `references/` | Lookup tables, listings, glossaries | Procedures, opinions |
| `guides/` | How-to and operating procedures | Lookup tables, design |
| `reports/` | Dated evidence: runs, reviews, audits, releases | Instructions, living specs |
| `assets/` | Non-Markdown files cited by a document | Markdown |
| `archive/` | Superseded or retired documents | Live documents |
| `other/` | Unsorted inbox with `owner:` and `review-by:` | Anything with a clear home |

## Which home

The first line that matches wins.

1. Picture, diagram source or data file: `assets/`.
2. Evidence of something that happened on a date: `reports/`.
3. One choice with its reasons: `decisions/`.
4. A proposal, roadmap or plan under review: `planning/`.
5. Steps a person follows: `guides/`.
6. A table, listing or glossary you look things up in: `references/`.
7. What the system is or must do: `specs/`.
8. Retired or superseded: `archive/`.
9. None of the above, or unsure: `other/`.

## Adding a document

1. Pick the home above; [the layout](layout.md) lists any extra homes.
2. Name it lowercase kebab-case; reports lead with `YYYY-MM-DD-`.
3. Run the onboard setup again to refresh the links below.
4. Put dated evidence in its own file under `reports/`. Do not add it to an entry file.

## Contents

- [README.md](README.md)
- [specs/](specs/AGENTS.md)
- [planning/](planning/AGENTS.md)
- [references/](references/AGENTS.md)
- [reports/](reports/AGENTS.md)
- [other/](other/AGENTS.md)
<!-- sdlc-lite:managed:end -->
