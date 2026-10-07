# Docs schema migration of this repository (T-0244)

Recorded: 2026-10-06. Ticket: T-0244, size M, solo lane. Design: `docs/docs-schema/design.md` (Mappings, Migration). Tools: `plugins/sdlc-lite/scripts/inventory.py`, `docs_check.py`, `rename_refs.py` (extended here), `onboard.py`.

## Deviations from the ticket text

- The gated apply step (T-0233) is not built and not on main. As T-0246 did, the batches run through `rename_refs.py`: `plan` (dry run and citing-file scan over every tracked text file, code and entry files included), `apply` (rewrite before the move), `git mv`, `check` (stale references with an allowlist), and `links` (broken-link count). T-0233 is therefore not added to `depends`.
- "One commit per batch, undo by `git revert`" did not happen: the solo brief forbids commits, and the lane is committed once by `fanout.py`. Each batch below records its map, counts and results, so a batch can be redone or reversed by its map (swap OLD and NEW and rerun `apply`, then `git mv` back).

## Baseline (read-only, before any change)

| Measure | Value |
| --- | --- |
| `inventory.py` | 570 documents, 2171 skipped; flags broken_links 6, duplicate 296, misplaced 3, orphan 171, oversized 1; 15 folders with many documents and no entry file |
| `docs_check.py` | 174 errors, 15 warnings (B-1a 61, B-2a 2, B-3a 5, D-1 6, D-10 4, D-11 4, D-12 28, D-2 4, D-3 68, D-5 1, D-7 1, D-9 5) |
| `rename_refs.py links` | 839 links checked, 12 broken (the `check.py` baseline, guard 32) |
| `check.sh` | red before the change: `codex_roles.py generate --check` reports generated-agent drift in `adapters/codex/agents/` and the Codex and lifecycle selftests that load them fail (`FAILED (failures=5, errors=1)`, `FAILED (failures=3)`); every other step passes. Not part of this ticket. |

## Plan

The mapping table in the design, applied by what each file is. Moves not in the table, or that depart from it, are marked.

| Today | Becomes | Why |
| --- | --- | --- |
| `docs/codex-role-execution.md`, `docs/plugin-compatibility.md` | `docs/references/` | table row |
| `docs/maintenance/sdlc-internals.md`, `claude-hooks.md` | `docs/references/` | table row; both are per-script and per-hook descriptions with no steps, so nothing goes to `guides/` and the name `maintenance/` is retired |
| `docs/repo-onboarding/layered-context-pattern.md` | `docs/references/` | table row |
| `docs/claude-handoff.md`, `docs/claude-response.md` | `docs/other/` | table row; `owner:` and `review-by:` added |
| `docs/other/orchestration-optimization-question.md` | stays | `owner:` and `review-by:` added |
| `docs/sdlc-lite/` | `docs/specs/sdlc-lite/` | table row |
| `docs/sdlc-lite/subagent-mode.md` | `docs/planning/sdlc-lite/` | departs from the table: it states "Proposal; nothing here is built"; `status: proposed` added |
| `docs/ticket-stages/` | `docs/specs/ticket-stages/` | table row |
| `docs/ticket-stages/watcher-design.md` | `docs/planning/ticket-stages/` | departs from the table: "not built yet"; `status: proposed` added |
| `docs/repo-onboarding/` (design.md, README.md) | `docs/specs/repo-onboarding/` | table row |
| `docs/repo-onboarding/reorganization.md` | `docs/planning/repo-onboarding/` | table row; `status: proposed` added |
| `docs/repo-onboarding/reorganization-plan-procedure.md` | `docs/planning/repo-onboarding/` | not in the table; it describes the unbuilt apply step (T-0233); `status: proposed` added |
| `docs/generative-constructs/` | `docs/specs/generative-constructs/` | table row |
| `docs/generative-constructs/05-*.md`, `06-*.md` | `docs/planning/generative-constructs/` | the table names them as candidates and the inventory has no hint; both open with "Status: proposed v0.1"; `status: proposed` added |
| `docs/docs-schema/` | `docs/planning/docs-schema/` | table row; `status: proposed` added; no `## Legacy` line needed |
| `docs/reports/` | stays | renamed by T-0246 |

## Other decisions

- `docs/layout.md` is written from the default template, with this repository's frozen paths and a `## Legacy` list of the existing report paths that break the date or naming rule. Legacy is an explicit list of exact paths and folders (a `*` glob cannot say "not starting with a date"), so a new report with a conformant name is fully checked and a new non-conformant one is not exempt.
- B-1a (61 findings, all inside a report's evidence folder): the rule now skips a path inside an evidence folder, the same zone D-9 already treats as evidence, and still flags the same name directly under any other home. Legacy still never exempts B-1a. The design's B-1a row is amended in the same change.
- `docs/reports/AGENTS.md` is written by hand (one routing rule, no per-file list), as the design says.
- Citing scan: every tracked text file (Markdown, Python, shell, JSON, TOML), including `check.py`, root and plugin `AGENTS.md`, `README.md`, both `HARNESS-NOTES.md`, skills, closed tickets and dated reports, as in T-0246. This ticket's handoff and the design's own Today column are not rewritten.
- `rename_refs.py` gains two things the moves need: a link from a moved Markdown file to a file that stays is recomputed (every move here changes depth; T-0246 did not), and `--skip GLOB`. Both have selftest cases with a negative control.

## Batches

Each batch: `rename_refs.py plan` (the dry run, which is also the citing scan), `apply`, `git mv`, then `links`, `docs_check.py` and `check.py`. The maps and the `--skip` are in the shell scripts named below; every batch skipped `.sdlc/0244-docs-schema-migration/*`. The scan covered every tracked text file, with no frozen file touched (`bench/results/` and `adapters/codex/agents/` are not cited by any moved path).

| Batch | Moves | Files rewritten | References | Broken links after | `docs_check.py` errors after |
| --- | --- | --- | --- | --- | --- |
| baseline | none | - | - | 12 | 174 |
| 1: references and other | `codex-role-execution.md`, `plugin-compatibility.md`, `maintenance/sdlc-internals.md`, `maintenance/claude-hooks.md`, `repo-onboarding/layered-context-pattern.md` to `references/`; `claude-handoff.md`, `claude-response.md` to `other/` (all three `other/` files got `owner:` and `review-by: 2026-12-15`) | 434 | 1006 | 12 | 170 |
| 2: sdlc-lite and ticket-stages | `sdlc-lite/` to `specs/sdlc-lite/` (`subagent-mode.md` to `planning/sdlc-lite/`), `ticket-stages/` to `specs/ticket-stages/` (`watcher-design.md` to `planning/ticket-stages/`); `status: proposed` added to the two planning files | 124 | 407 | 12 | 171 |
| 3: repo-onboarding and generative-constructs | `repo-onboarding/` to `specs/repo-onboarding/` (`reorganization.md` and `reorganization-plan-procedure.md` to `planning/repo-onboarding/`), `generative-constructs/` to `specs/generative-constructs/` (`05-*` and `06-*` to `planning/generative-constructs/`); `status: proposed` added to the four planning files | 111 | 307 | 12 after hand-editing two allowlist targets (below) | 172 |
| 4: docs-schema | `docs-schema/` to `planning/docs-schema/`; `status: proposed` added | 44 | 85 | 12 | 171 |

The error count moved little until the entry files, `docs/layout.md` and the B-1a change landed, because most findings were D-3, D-12 and D-9 on existing report names (Legacy) and B-1a. 33 files moved in total (32 renames and the repo-onboarding README, which git shows as a delete and an add).

Hand edits the tool cannot do:

- `docs/reports/broken-links-allowlist.md` rows for `docs/specs/generative-constructs/README.md` and `progressive-context-plugin.md`: the broken link to the sibling repository needs one more `../` after the one-level-deeper move. Guard 32 caught it.
- The design's Mappings table (`Today` column) was restored to the designed text after the rewrite changed it, and a note records the applied state and the departures.
- `docs/specs/repo-onboarding/design.md`: its example layout and document-type table named `maintenance/` and `reference/`; they now name `guides/` and `references/`.
- `docs/planning/repo-onboarding/reorganization.md`: the two sentences that said `reports/`, `bench/results/` and the Codex agents were "to be listed as frozen" now say they are listed.

## Layout, entry files and index

- `docs/layout.md` was written by `onboard.py setup` from the default template (nine homes, `## Kinds`, `## Decide`), then extended: frozen paths `docs/reports/`, `plugins/sdlc-lite/bench/results/`, `plugins/sdlc-lite/adapters/codex/agents/`, and a `## Legacy` list of 75 lines, exact report paths plus two evidence folders (`reports/plan-skills-live-run.d/**`, `reports/workflow-stage-pilot/**`), derived from the D-3, D-9 and D-12 findings of this run. They are the existing names that break the date or naming rule. A new report is fully checked.
- `onboard.py setup` also wrote 8 entry files and their `CLAUDE.md` stubs (`specs/`, `planning/`, `references/`, `other/` and the four topic folders with two or more documents); their one-line topic descriptions were written by hand. The root `AGENTS.md` block it would append was not applied: this repository's root file is hand-written and `onboard.py check` keeps reporting it `unmanaged`. `docs/reports/AGENTS.md` and its stub were written by hand (one routing rule, no per-file list).
- `docs/AGENTS.md` keeps a hand-written topic router (rewritten for the new homes) above the managed block that setup wrote; `docs/README.md` gains this record.

## B-1a

All 61 B-1a findings sat inside a report's evidence folder (copies of `runs.jsonl`, `skips.md` and role results kept as evidence). The rule now skips a path inside an evidence folder, the zone D-9 already uses, and still flags the same name anywhere else. Legacy still never exempts it. Selftest: the existing rule cases moved from the evidence folder to `references/`; a new positive case (`runs.jsonl` and `builder-L1-2.md` in an evidence folder are not flagged), a new negative control (`docs/specs/runs.jsonl` is flagged), and a mutated variant that ignores the exemption must fail the gate. The design's B-1a row says so.

## rename_refs.py

Two additions, each with a selftest case and a negative control: a link from a moved Markdown file to a file that stays is recomputed from the new folder (every move here changes depth; without it, moving `docs/old/x.md` to `docs/specs/old/x.md` breaks `../README.md`, which the selftest observes before the fix is applied), and `--skip GLOB`.

## Gate in check.sh

`check.sh` runs `docs_check.py --root` on this repository, only where `docs/layout.md` and a Git checkout sit beside the plugin. Guard 33 in `check.py` requires the line (negative control: the phrase removed is flagged). Observed negative control: a stray `docs/stray-note.md` made the gate exit 1 with `error D-2 docs/stray-note.md: file directly in docs/ ...`; removed, the gate exits 0.

## Result

| Measure | Before | After |
| --- | --- | --- |
| `docs_check.py` | 174 errors, 15 warnings | 0 errors, 10 warnings (B-2a 2, B-3a 3, D-10 3, D-11 2; all existing, none new) |
| `rename_refs.py links` | 839 checked, 12 broken | 880 checked, 12 broken (the same twelve, the allowlist rows updated) |
| Stale references to the 10 moved paths | 154 | 0 outside the allowlist below |

Allowlist for the stale-reference check (`rename_refs.py check`): `.sdlc/*0244*` (this ticket's handoff), this record and the design's Today column (they name the old paths on purpose), `.sdlc/.*` (closed ticket folders), `.sdlc/verify-*`, `.sdlc/wave-*` and `.sdlc/lean-sdlc-review-2/*` (run workspaces and logs, where `path:line` and escaped forms follow the path), `docs/reports/reorg-inventory-live-run/*` (the maison plan names maison's own `docs/maintenance/`), and three dated reports that quote a tool's output or name a retired folder in prose (`2026-10-05-docs-check-run.md`, `naming-sdlc-lite.md`, `release-0.20.11.md`).

## Limits

- The 154 stale references that remain are in history: they use forms the rewriter does not touch (`path:line`, regex-escaped paths, text bound to an old tag, a quoted tool output) or sit in a record that is about the old path. `naming-sdlc-lite.md` line 43 now reads `docs/references/sdlc-internals.md` for the file and still quotes the old path inside a quoted error line.
- Tags and release pages published before this change keep the old paths, as they did for `docs/validation/`.
- `docs/` files that cite `.sdlc/` (B-3a, 3 warnings) and the D-10 and D-11 warnings are existing and unchanged by this ticket.
- `check.sh` was red before this ticket (generated Codex agents drift, see Baseline) and fails on exactly the same items after it; see Verification.
- One commit per batch was not possible (see Deviations); the lane commit is made by `fanout.py`.

## Verification

Final `bash plugins/sdlc-lite/scripts/check.sh`: exit 1 on the same items as the baseline and on nothing else (the `codex_roles.py generate --check` drift, `FAILED (failures=5, errors=1)` in `codex-selftest.py`, `FAILED (failures=3)` in `lifecycle-selftest.py`); `docs_check.py selftest`, `rename_refs.py selftest`, `onboard.py selftest`, `check.py` and the new `docs_check.py --root` gate pass; `python3 scripts/check-packaging.py` passes; `git diff --check HEAD` is clean. One independent verifier (L3, a different model family from the solo session) ran the eight acceptance criteria in a throwaway worktree, including mutation reds for the B-1a exemption and for both `rename_refs.py` additions, and returned `pass`: `.sdlc/0244-docs-schema-migration/verifier-L3.md`.
