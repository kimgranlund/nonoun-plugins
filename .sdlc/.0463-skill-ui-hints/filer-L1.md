<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective: attempt dcd1ff7ec23a4c84b0223cb8367448d4, handoff sha256 e6c0f2984805, 5 of 5 (red) criteria without a pre-edit red control. This is step 2 (`step-2/process-deviations.md`). The recorder ran before the builder's first edit but reported that 4 source paths already differed from HEAD. Those 4 paths are step 1's uncommitted edits, which step 2 inherits by design, so the record is a base control and not a red-before-edit checkpoint. Step 2's verifier passed it. `step-2/red-checkpoint.jsonl` shows the same span exit 1 before the edits, but the passing verdict does not clear the deviation.
- Both steps passed (step 1 verifier L2 pass, step 2 verifier L2 pass). Step 1 ran twice. The first attempt (`step-1.superseded-1`) was blocked with a `plan defect:` on criterion 3, because the `^FAIL` guard also matched the `FAIL: N role levels` summary line. The replan changed the guard to `^FAIL ` with a trailing space, and the second attempt passed.
- Nothing is committed. All changes sit in the working tree.
- Codex-only hint behavior is unverified. The ticket's non-goals say to state this, and no artifact shows a Codex run.

## PR title
T-0463: Standardize skill argument hints, add Arguments tables, and lint hints against real flags

## PR body
Summary: Every user-invocable skill that reads `$ARGUMENTS` now has an `argument-hint` in one POSIX-style grammar and a single `## Arguments` table. Question wording follows one UI style. A new `check.py` lint (rules H-1 to H-7) keeps hints and the real script flags in agreement. This is wording, hints, tables and one lint only. No skill changes what it does.

Changes:
- `docs/specs/doc-standards/prompts.md`: new section `## Skill arguments and questions`, with the hint grammar, hint rules H-1 to H-7, the Arguments table shape, and seven question rules. No new card was added, because a card would force a managed-index regeneration this ticket does not own.
- `docs/specs/doc-standards/README.md`: the `| Skill |` row's Check cell now names `check.py argument hints (H-1 to H-7)`. Enforcement stays `enforced`.
- `plugins/sdlc-lite/AGENTS.md`: one skill-authoring bullet under Contracts and routing that names `argument-hint`, the Arguments table, the `prompts.md` section, and `check.py` item 60.
- `plugins/sdlc-lite/scripts/check.py`: item 60 adds lint rules H-1 to H-7 and a `HINT_ALLOW` allowlist for flags that only some subcommands take (`ticket`, `board`, `fanout`, `onboard`, `fleet-retro`, `review-traces`). Each rule has an in-memory mutant control, and the positive controls include a clean reader, a 100-character hint, and a usage flag carried by an `[options]` table.
- 29 skills under `plugins/sdlc-lite/skills/`: 24 `argument-hint` lines rewritten, 5 already conformed (`handoff`, `run-plan`, `onboard`, `fleet-status`, `review-traces`), and an `## Arguments` table added to each. Six question-wording lines changed, in `ask`, `fleet-status`, `open-questions` (two lines), `plan-loop` and `plan`.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-architect-l1.toml`: regenerated after the `decompose` edit.
- `.sdlc/0463-skill-ui-hints/hints.md`: table of each skill's old and new hint (33 rows: 29 readers plus 4 stubs marked `unchanged (stub)`). The 4 stubs, the 4 reference skills and the `sdlc-lite` router are unchanged against base.
- Behavior change to disclose: the `plan` kind question went from 5 options to 4 to satisfy question rule 4. `fanout` is now named in the question text for the Other box. The pinned strings `steps|doc|goal|campaign|fanout` and `Write it in chat` are intact. The step 2 verifier accepted this.
- `report` (T-0460) and the merged `plan` (T-0467, T-0468) are on the tree and standardized here, so there is no follow-up for them.

Verification:
- Step 1: before the skills were fixed, `check.py` exited 1 with 78 `argument hints` FAIL lines. That includes the six named findings (agent H-2, build H-2, ticket H-3, report H-4, fleet-retro H-5, board H-6) and no stub or reference skill flagged. The verifier also ran ten single-line mutants of `hints_bad` and `hint_parses` on a copy under `/tmp`. Each mutant tripped its own control, except that the H-6 "heading check off" mutant was isolated only by a second control.
- Step 2: `check.py` exit 0; `check.sh` exit 0 (run selftest and hook selftest PASS, shellcheck ok, plugin validate ok); `scripts/check-packaging.py` PASS; `prompt_lint.py` 73 files, 0 errors, 8 warnings; `codex_roles.py` and `claude_roles.py generate --check` both verified; `docs_check.py` 0 errors, 30 warnings; `git diff --check` clean.
- The verifier read the whole skills diff (29 files, 265 insertions, 30 deletions) and found only hint lines, Arguments sections and the six question-wording lines. No step, command or decision changed.
- Limits: the red-before-edit controls for step 2 are retrospective (see Warnings). Codex-only hint behavior is unverified.

## Changelog entry
- sdlc-lite: every skill that reads `$ARGUMENTS` now has a one-grammar `argument-hint` and an `## Arguments` table, and `check.py` lints hints against skill bodies and script usage text (rules H-1 to H-7). The `plan` kind question now offers 4 options (`fanout` moves to the Other box).

## Follow-ups
- decide: the `plan` kind question dropped from 5 clickable options to 4 to meet question rule 4 (2 to 4 options). `fanout` is now reachable only through the Other box. Decide whether that is acceptable or rule 4 should allow 5 for this one question.
- note: the old/new hint table for the ticket notes is in `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout59/x/.sdlc/0463-skill-ui-hints/hints.md`. The ticket's Done-when asks for it in the ticket notes, so copy or link it at close.
- note: 12 other skills that name `AskUserQuestion` were read and left unchanged, including `grill`, which marks its first option `(Recommended)` with a tradeoff. The verifier's spot-read found no clear rule violation, but question-rule conformance has no command-level check.
