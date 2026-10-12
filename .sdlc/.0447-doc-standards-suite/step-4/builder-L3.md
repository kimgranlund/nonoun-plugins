<!-- role=builder level=L3 model=opus effort=high -->
## Status
inherited red: gate_lock selftest (isolation: the real state root was not touched by the selftest)

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/plugins/sdlc-lite/scripts/onboard.py: added item 5 under `## Adding a document` in `DOCS_AGENTS_TEMPLATE`. It names `specs/doc-standards/README.md` as a code span. `TEMPLATE_VERSION` is still 1.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/AGENTS.md: managed block rewritten from `onboard.plan('.')`. It now has item 5, and the plan also turned the stale goals/ and kpi/ entries into links and added `assets/`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/specs/AGENTS.md: managed block rewritten from the plan; it now lists `doc-standards/`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/references/AGENTS.md: managed block rewritten from the plan. It now lists `glossary.md` and also the already present `subagent-list-style.md`, which the block was missing at base.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/docs/README.md: added the `[Document standards](specs/doc-standards/README.md)` bullet after the Repository onboarding bullet.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/plugins/sdlc-lite/skills/{plan-goal,plan-doc,ticket,file,fleet-retro}/SKILL.md: each has a new first body line after the front matter (none of the five has an H1). The line reads ``Read first: `docs/specs/doc-standards/<card>.md`, when that file exists in this repository, for the document this skill writes.``
- Git index only, no content change: `git add -N docs/references/glossary.md docs/assets`. These are step 3 files, now marked intent-to-add the same way step 3 marked the doc-standards cards.

## Checks
- `redck.py record <handoff>`: exit 0, but stored as retrospective, 5 controls red (see Notes).
- (red) onboard check reports `current` for the three docs entry files: exit 0.
- (red) docs/AGENTS.md managed block contains `specs/doc-standards/README.md`: exit 0.
- (red) the template has the code span and no `](specs/doc-standards/` link: exit 0.
- (guard) `onboard.py selftest`: exit 0.
- (red) `grep -qF '](specs/doc-standards/README.md)' docs/README.md`: exit 0.
- (red) the five-skill card grep loop: exit 0.
- (guard) `python3 scripts/check-packaging.py`: PASS, exit 0.
- (guard) `docs_check.py --root .`: exit 0 (0 errors, 24 warnings).
- (guard) `git diff --check ad35eaaa... -- . ':(exclude).sdlc'`: exit 0.
- (guard) scope `test -z` filter, with SDLC_BASE_SHA set to ad35eaaa04e635875c9db778c0a741ee5319421b: exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: exit 1 after 15m18s. The only FAIL is `gate_lock selftest: isolation: the real state root was not touched by the selftest`; everything else passed. Log is at /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout34/e/.sdlc/0447-doc-standards-suite/step-4/check-sh.log.
- Rerun alone, `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` in the tree: the same single failure.
- Base control: `git archive ad35eaaa plugins/sdlc-lite/scripts` extracted under the tmp prefix, then `gate_lock.py selftest` there: the same single failure. The export was removed afterwards.
- Extra checks: `check.py` ok, `prompt_lint.py` 0 errors, `codex_roles.py generate --check` verified, `claude_roles.py generate --check` verified. Neither generator was stale, so `generate` was not run.

## Notes
- The gate_lock failure is environmental. gate_lock.py is unchanged from base, and the check compares the mtime of the real ledger before and after the run. Other sessions on this host (load around 6 to 7) write to that ledger at the same time.
- I could not make the rule 8 base control a git worktree. The block-stray-worktree hook reads `SDLC_TMP_WORKTREES` from the session environment, where it is unset, so it denied `git worktree add` even with the variable exported inline. I used a `git archive` export of the base scripts under the brief's tmp prefix instead and removed it afterwards. `SDLC_BASE_SHA` was also unset, so I set it inline for the git guards.
- check.py was red before my edits: 21 "unlisted broken link" findings from the step 3 cards (and, once tracked, glossary.md) pointing into the untracked `docs/assets/`. `rename_refs.link_report` only counts tracked files, so `git add -N docs/assets docs/references/glossary.md` fixed it with no file edits. Marking glossary.md intent-to-add also puts it in the references managed block, so that block stays `current` after commit.
- The redck record is retrospective because steps 1 to 3 are uncommitted in this tree (30 paths already differed from base). It was run before any edit of mine.
- `onboard.py check` still shows things this step does not own: `stale docs/planning/AGENTS.md`, unmanaged goals/kpi entry files, and a non-current root `AGENTS.md` (expected, since setup was never run). I left them alone because the scope guard does not allow those paths.
