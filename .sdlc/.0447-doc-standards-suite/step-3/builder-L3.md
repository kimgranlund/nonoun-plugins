<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/README.md (new: the registry. 35 rows, which are the 30 source-list types plus Agent file, Skill, Overlay, Handoff and Tool description. Below the table, one line per S-1 to S-7 and P-1 to P-6 rule)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/core.md (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/intent.md (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/design.md (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/work-items.md (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/delivery.md (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/knowledge-ops.md (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/prompts.md (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/references/glossary.md (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/schemas/kpi.json (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/schemas/ticket.json (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/schemas/test-case.json (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/templates/bug.tmpl (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/templates/feature-request.tmpl (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/templates/spike.tmpl (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/templates/pr-body.tmpl (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/templates/postmortem.tmpl (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/templates/runbook.tmpl (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/assets/templates/adr.tmpl (new)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/AGENTS.md (new: written from `onboard.plan('.')`, with its purpose line put in place of the generated placeholder)
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/doc-standards/CLAUDE.md (new: written from `onboard.plan('.')` unchanged)

## Checks
- `python3 redck.py record step-3/handoff.md`, run before the first edit: exit 0, "recorded 9 retrospective control(s) red".
- C1 `for f in README core ... CLAUDE; do test -f ...`: rc=0
- C2 registry types, S/P ids and card names (`python3 -c "import re; src=..."`): rc=0
- C3 `test -f .../README.md && python3 docs_check.py --root . --only standards`: "0 errors, 0 warnings", rc=0
- C4 (guard) `python3 docs_check.py --root .`: "0 errors, 24 warnings (B-2a 10, B-3a 7, D-10 3, D-11 4)", rc=0. The counts are the same as before this step.
- C5 glossary rows and "unapproved": rc=0
- C6 schema `required` and enums against `docs_check.KPI_REQUIRED` and the ticket enums: rc=0
- C7 seven `.tmpl` files exist: all present.
- C8 `onboard.py check` prints `current docs/specs/doc-standards/AGENTS.md` and `current docs/specs/doc-standards/CLAUDE.md`: rc=0
- C9 required phrases in prompts.md, delivery.md, core.md and work-items.md: rc=0
- C10 no em or en dash and no trailing whitespace in docs/specs/doc-standards, glossary.md and docs/assets: rc=0
- C11 (guard) diff scope against `SDLC_BASE_SHA=ad35eaaa04e635875c9db778c0a741ee5319421b`: rc=0
- `git diff --check`: clean. A grep of the new files for the retired product spellings in check.py's `NAME_BANNED` list found none.
- Confirmed `docs/specs/doc-standards/README.md` is in `docs_check.Repo('.').files`, so C3 checked the real registry and did not pass on an empty file list.

## Notes
- I ran `git add -N docs/specs/doc-standards` (intent-to-add, nothing committed) on all 10 files there. `onboard.py` lists documents and entry files with `git ls-files`, so with the files untracked the handoff's `onboard.plan` snippet produced no entry files and C8 could not pass. In `git status` those 10 files show as ` A`. `docs/assets/` and `docs/references/glossary.md` are still untracked.
- The redck record says "retrospective" because steps 1 and 2 are uncommitted in this lane, so 9 source paths already differed from base. The record was taken before any edit in this step.
- `SDLC_BASE_SHA` was empty in the shell, so I exported `ad35eaaa04e635875c9db778c0a741ee5319421b` inline to run C11.
- This step made `onboard.py check` report `stale docs/specs/AGENTS.md`: its managed block does not list the new doc-standards topic. That file is outside this step's guard scope, so step 4 or an onboard refresh must update it. `docs/references/AGENTS.md` was already stale at base and still does not list glossary.md.
- The glossary has nine rows. Beyond the seeded eight I added `fanout lane`, so that `lane` keeps one sense (the fix, solo or chain route) as the glossary's own rule requires. Unapproved aliases leave out words the cards use as real terms (issue, tier, reviewer, stage, runbook).
- On mixed rows (Agent file, Skill, Overlay), the convention is written under the registry table: a row is `enforced` when any rule in its Check cell fails a gate. Each rule's own tier is listed in the rule lines below the table: S-*, G-* and P-1 to P-3 are enforced, and P-4 to P-6 are advisory.
- Seven template stems are named in the handoff. `runbook.tmpl` carries `doc-type: runbook` and is not Markdown, so docs_check does not read it.
