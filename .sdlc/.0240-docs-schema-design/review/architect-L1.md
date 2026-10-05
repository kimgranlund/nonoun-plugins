<!-- role=architect level=L1 model=fable effort=high -->
## Approach

Verdict: ready after fixes. The schema's shape is sound (nine homes that are mutually exclusive for Markdown kinds, a decision table, name-only checks), but three rules as written would make a harness or a person do the wrong thing, and each has a concrete fix the author can apply without a new user decision. I decomposed the design along two planes (structure as written versus the needs the tooling and the two docs trees actually impose) and the crossing found eleven needs with no home plus four rules that host a need in name only; the findings below are those gaps, verified against the files cited.

Blockers:

1. B-2 contradicts the tooling and the design's own Promotion section. `design.md:36` says a design review "does not live in `.sdlc/`", while `design.md:43` names "an architect result" as a `.sdlc/` artifact to promote, and `run.sh:4-7` writes every role result into the handoff dir where `steps.py` and `order.py` read it (this review is `.sdlc/0233-docs-schema-design/review/architect-L1.md`). A conductor following B-2 literally bypasses `run.sh` or moves the result. Fix: a role result in the dir `run.sh` wrote it to is a record; the reader deliverable is its promoted copy.
2. D-7 demands an entry file the tool cannot create. `design.md:166` errors on a home with two documents and no `AGENTS.md`; `repo-onboarding/design.md:58` says a home gets no entry file, and `onboard.py:463` skips every path under a listed home, so neither `specs/AGENTS.md` nor `specs/lean-sdlc/AGENTS.md` is ever written. Build ticket 2 (`design.md:259`) changes the template and `docs/AGENTS.md` text only. Fix: extend ticket 2 to the model at `onboard.py:452-476` (entries for homes and for topics under a home) and gate D-7 on that.
3. Grandfathering by first-commit date is vacuous where it matters. `design.md:231` treats a file it cannot date as grandfathered; an untracked file has zero `git log --diff-filter=A` lines (measured on `docs/docs-schema/design.md`), so a new uncommitted file passes D-3 and D-12 and the negative control at `design.md:251` never fires pre-commit. A shallow clone yields a wrong date, not a missing one. After the ordered `git mv validation/ reports/` (`design.md:197`), every moved record gets a new first-commit date at its new path unless `--follow` is used, un-grandfathering the 48 files the rule protects. Fix: a `## Legacy` glob list in `docs/layout.md`, same backticked form as `## Frozen paths`; unlisted or untracked means new. `adopted:` and `mode:` then host nothing and go.

Non-blockers:

4. `mode: adopt` voids the quarantine. `design.md:156` makes every error a warning with exit 0, and both repositories would run in `adopt` indefinitely (`design.md:233`), so D-5 and D-6 never bite and `other/` is not enforceable in practice. Resolved by finding 3 (scope by legacy list, no mode).
5. Two mechanisms bind a folder to a kind and `## Homes` has no stated role. `## Kinds` (`design.md:137`) and `extra-homes:` (`design.md:143`) do the same thing; D-1 (`design.md:160`) checks "nine homes or a listed extra-home" and never reads `## Homes`, which the parser requires (`onboard.py:117-119`). Fix: `## Homes` is the one list of folders; a non-default name needs a `## Kinds` line; drop `extra-homes:`.
6. D-9 and the depth rule reject real evidence. `docs/validation/dual-host-readiness-recovery.json` and `native-codex-smoke.json` sit at the home root; maison pairs each report with a `.sha256`; `docs/validation/plan-reviewer-live-run/claude/probe/step-1/` is depth 7 against `design.md:102`; maison's `gen-ui-audit-2026-10-03/audit-snapshot.json` has no same-stem Markdown at all (`design.md:216`). Say which checks the legacy list exempts and allow same-stem sidecars and any depth inside an evidence folder.
7. B-1a misses retries. `design.md:172` matches `*-L[0-9].md`; `run.sh:6` writes `<role>-L<n>-<k>.md` (49 tracked). Also `budget-ack.md` (`budget.py:33`) and `decompose/` (`agents/architect.md:9`) are records B-2a does not list, and `.sdlc/fix-protocol-controls/` has no root `handoff.md`.
8. Planning to archive on `status: superseded` (`design.md:76`) is a status-triggered move, which `repo-onboarding/design.md:189` forbids in so many words. The split can stay (user may change), but that sentence must be amended in the same change, or `planning/` folds into `specs/` with `status:`.
9. Migration risk missing: `check.py:613` reads `docs/maintenance/claude-hooks.md` by path at run time, and the rewriter in `reorganization.md:87` covers tracked Markdown only. Root `AGENTS.md`, `plugins/sdlc-lite/AGENTS.md`, `README.md` and both `HARNESS-NOTES.md` cite moving paths.
10. `reorganization.md:143,46` says `docs/validation/` is frozen and "not a defect to fix by moving"; `design.md:197` moves it. Pick one and amend the other.
11. Promotion step 3 (`design.md:47`) writes into a ticket's `handoff.md`, which is frozen once a role reads it (root `AGENTS.md`, hook named at `check.py:607`) and hidden after close. `notes.md` or the `source:` key alone suffices.
12. B-3a as written warns on 101 files in `docs/validation/` and on `lean-sdlc/cost-control.md:34,208`, `lean-sdlc/design.md:201`, `ticket-stages/watcher-design.md:34`. State whether the legacy list covers links.
13. The design's own file fails D-1 (tenth top-level folder) and D-4 (no `status:`); add its mapping row.
14. D-12 cannot prove "never reused" (`design.md:101`) across `decisions/<topic>/` subfolders; add a uniqueness pass.
15. maison `reference/` is 30 tracked files (2 READMEs), not 32; the 32 counted `.DS_Store`.

Checked and clean: counts at `design.md:10` (69 entries, 48 Markdown, 19 folders, 2 other, 8 dated, 5 loose, 7 folders before `docs-schema/`), root `AGENTS.md` 78 lines (`design.md:103`); the parser claim at `design.md:131` (ran `_parse_layout_text` on the proposed text: `## Kinds` and `## Schema` ignored; a `###` heading inside `## Homes` does not reset the section); `tickets.py close` refuses path cites without `--rewrite-refs` (`tickets.py:40-48`); maison homes and dated report names (`design.md:11,214-218`); B-4 and B-5 match `budget.py`, `evals.py` lock and `supervisor.py:223`.

## Interfaces

- `docs/layout.md`: `## Kinds` (`- \`<home>/\` is \`<kind>\``) and `## Legacy` (one backticked glob per line) added; `## Schema` with `mode:`, `adopted:`, `extra-homes:` dropped. `Layout` in `plugins/sdlc-lite/scripts/onboard.py:46` gains `kinds` and `legacy`; `## Homes` and `## Frozen paths` forms unchanged.
- `plugins/sdlc-lite/scripts/onboard.py:452-476` (`model`): entry files for homes and for topics nested under a home; D-7 depends on it.
- `plugins/sdlc-lite/scripts/docs_check.py` (new): B-1a pattern `<role>-L<n>(-<k>)?.md`, `budget-ack.md`, `*.request.json`, `*.log`; B-2a record list with `decompose/` and step-only task folders; D-9 same-stem sidecars and any evidence depth; D-12 decision-number uniqueness; exit 1 on any error, legacy-listed files exempt.
- `docs/docs-schema/design.md`: B-2 reworded (finding 1); mapping row for itself; `docs/repo-onboarding/design.md:189` and `docs/repo-onboarding/reorganization.md:143` amended in the same change.
- Migration apply: citing scan over code and entry files, not only tracked Markdown (`check.py:613`).

## Constraints and assumptions

- An older `onboard.py` ignores `## Kinds`, `## Schema`, `## Legacy`: verified by running `_parse_layout_text` on the proposed text.
- `run.sh` writes `<role>-L<n>.md` and `-<k>` retries into the handoff dir: verified by `run.sh:4-7,193-199` and 49 tracked retry files.
- Setup never writes an entry under a home: verified by `onboard.py:463` and `repo-onboarding/design.md:58`.
- An untracked file has no first-commit date: verified by `git log --diff-filter=A -- docs/docs-schema/design.md` (0 lines); this clone is not shallow.
- `check.py` reads a docs path at run time: verified by `check.py:613`.
- Consumer repos track `.sdlc/`: verified for maison (10 tracked files), so B-2a applies there.
- `git mv` resets the add date without `--follow`: unverified (standard git behavior, not measured here).

## Rejected alternatives

- Git first-commit date with `--follow`: still blind to untracked files, wrong on shallow clones, and 400 subprocess calls per run; a listed glob needs no git and matches the existing Frozen form.
- Keeping `mode: adopt`: a global warning switch is what prevents `other/` from ever expiring; per-file scope through the legacy list gives the same migration grace with checks that still fail.
- Keeping `extra-homes:` beside `## Kinds`: two spellings of one binding, and D-1 reading neither `## Homes` nor the parser's required section.
- Folding `planning/` into `specs/` with `status:` only: avoids the status-triggered move but loses the fixed-name signal the user asked for; left as the user's choice, with the principle amendment as the minimum.
- Moving role results out of `.sdlc/` to satisfy B-2: breaks `steps.py` and `order.py` reads and the result check in `run.sh:17`.

## Risks

- The legacy list grows stale if the migration renames files without pruning it; the apply step must rewrite it like any citer.
- Extending setup to homes and nested topics changes `docs/AGENTS.md` output for every adopter (maison included); row 6 of the upsert table will replace their managed blocks on the next setup.
- If the user keeps `planning/` and the principle is not amended, two live documents contradict each other and a later role will follow whichever it read first.
- D-9 with same-stem sidecars still rejects maison's audit JSONs unless that folder is declared a report's evidence folder; the mapping row needs a named report.

## Carry forward

- Manifest: `.sdlc/0233-docs-schema-design/review/decompose/manifest-v2.json`; coverage_check exit 0, also under `--strict` (v1, the design as written: 11 UNHOSTED); report at `decompose/report.md`.
- Parser ignores unknown level-2 headings: `onboard.py:94-96`; required sections `onboard.py:117-119`.
- Setup skips everything under a listed home: `onboard.py:463`; homes get no entry: `repo-onboarding/design.md:58`.
- Role result and retry names: `run.sh:4-7,193-199`; retry count 49 from `git ls-files .sdlc | grep -cE -- '-L[0-9]-[0-9]+\.md$'`.
- `budget-ack.md` written by `budget.py:33`; `decompose/` written by `agents/architect.md:9`.
- `check.py:613` reads `docs/maintenance/claude-hooks.md` by path; `check.py:607` names the handoff-edit hook.
- `tickets.py close` path-cite refusal: `tickets.py:40-48`.
- `docs/validation/`: 69 entries, 48 `.md`, 19 folders, 2 `.json` at root, 8 dated, 18 `<name>.md`/`<name>/` pairs, max depth 7.
- Validation files citing `.sdlc/` paths: 101, from `grep -rlE '\.sdlc/[0-9A-Za-z._-]+/' docs/validation | wc -l`.
- Docs with YAML front matter: 4, all fixtures under `docs/validation/`; `Recorded:` lines in 45 files.
- maison: `docs/reference/` 30 tracked files, `reports/` 4 reports with `.sha256` sidecars, `maintenance/gen-ui-audit-2026-10-03/` holds 3 JSON and 2 Markdown, `.sdlc/` tracked (10 files).
- `reorganization.md:143` freezes `docs/validation/`; `design.md:197` moves it.
- Principle text that forbids status-triggered moves: `docs/repo-onboarding/design.md:189`.
