## Goal
Independently verify T-0246: `git diff e5909f7..HEAD` in this worktree renamed docs/validation to docs/reports (and moved docs/readiness-recovery-validation.md into it) and rewrote references with plugins/sdlc-lite/scripts/rename_refs.py.

## Acceptance criteria
1. Sample at least 15 rewritten references of different kinds (code such as specgate.py, entry file such as AGENTS.md, relative Markdown link, ticket handoff under .sdlc, release record under docs/reports, shell/regex forms like `f=docs/...`, `|docs/...`) by comparing `git show e5909f7:<file>` to the working file: only path text changed, anchors kept, link targets resolve to existing files.
2. Tag-bound text (e.g. `v0.20.7:docs/validation/...`) and URLs were not rewritten; `git grep -n "docs/validation"` shows only allowlisted hits (.sdlc/0246-*, reorganization.md, docs/reports/rename-validation-to-reports.md) plus tag-bound text.
3. Run `python3 plugins/sdlc-lite/scripts/rename_refs.py check docs/validation --allow '.sdlc/0246-*' --allow docs/planning/repo-onboarding/reorganization.md --allow docs/reports/rename-validation-to-reports.md` (expect 0), `... links` (expect 95 broken, same as main), `... selftest`. Show a negative control: add a stale reference in a throwaway edit, see check fail, revert it.
4. Check the before/after numbers in docs/reports/rename-validation-to-reports.md against git (files under docs/reports, `git show e5909f7` counts); freeze sentence in docs/planning/repo-onboarding/reorganization.md amended; no em dashes in the added tool/note; `git diff --check e5909f7`.
5. `python3 plugins/sdlc-lite/scripts/specgate.py selftest` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` pass.

## Constraints
Read-only except throwaway experiments you revert. No push or publish.
