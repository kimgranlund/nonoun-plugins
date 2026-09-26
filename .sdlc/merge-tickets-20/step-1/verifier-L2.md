<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`: pass. Evidence: ran the command in the tree, output `3`; `git rev-list --parents -n1 HEAD` shows `ca69fc4 5a7881e d476465` (two parents plus the commit itself).
- `git merge-base --is-ancestor tickets-20 HEAD`: pass. Evidence: command exit 0 in the tree.
- (guard) `! git rev-parse -q --verify MERGE_HEAD`: pass. Evidence: exit 0 in the tree (no MERGE_HEAD present, `git status --short` shows a clean merge state). Bites confirmed: in a throwaway worktree (`$SDLC_TMP_WORKTREES/premerge`) at pre-merge HEAD `5a7881e`, running `git merge --no-ff tickets-20` produced real conflicts and `git rev-parse -q --verify MERGE_HEAD` then printed a sha with exit 0, which would flip this guard red; worktree removed afterward.
- (guard) `out=$(git diff-tree --cc HEAD) && ! printf "%s\n" "$out" | grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"`: pass. Evidence: exit 0 in the tree. Bites confirmed: in the same throwaway worktree, resolving the real conflict but leaving git's own inserted markers unresolved in `CLAUDE.md` (committed with `--no-verify`) made the guard fail (`GUARD_FAIL` observed); a synthetic marker appended after an `--ours` checkout did not trip it, which is the documented accepted limitation in this repo's own CLAUDE.md ("no conflict-marker lines the merge itself added... an accepted limitation that the check.py probe pins") — not a defect in this build.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: ran it in the tree at HEAD, full output ends `ok: shellcheck` / `ok: plugin validate`, exit 0; includes steps/fanout/tickets selftests all `PASS`.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check` exits 0: pass. Evidence: ran it, output `ok: 140 tickets, roadmap current`, exit 0.

Beyond the listed criteria, spot-checked the actual conflict resolutions against the handoff's "keep both lanes' intent" instruction:
- `.sdlc/roadmap.md`: regenerated (matches `tickets.py check`'s "roadmap current").
- `.sdlc/find-out-why-the-t/handoff.md`: `git show` on both parents vs merged file confirms main's evidence paragraph in Context plus tickets-20's `## Question`/`## Evidence` sections and richer `## Goal`/`## Constraints` all survived.
- `plugins/sdlc-lite/scripts/check.py`: both `PLAN_DEFECT_DOCS` entries (`clean porcelain status`, `` nonzero `exit` ``) present in merged file, one each side.
- `plugins/sdlc-lite/scripts/steps.py`: both parents' `(k6)` selftest blocks (porcelain-guard on main, bare-assignment on tickets-20) both present in merged file, tickets-20's relabeled to `(k7)` as the builder stated; `check.sh`'s "steps selftest: PASS" line confirms both still execute and pass.
- `plugins/sdlc-lite/scripts/fanout.py`: merged docstring and selftest now assert a WIP commit and clean lane tree for the inherited-red outcome (matching main/T-0126's stated intent), with the lane tip `wip(T-0001): inherited red: step-1: test_a` and non-ancestor checks added; `check.sh`'s "fanout selftest: PASS" confirms it runs green.
- File-scope check: diffed `5a7881e..HEAD` (217 files) against the union of files touched on each side vs their merge-base (282 files) — no file appears in the merge diff outside that union.
- Plugin version: `plugins/sdlc-lite/.claude-plugin/plugin.json` still reads `0.12.0` (not bumped, per the handoff's instruction).
- No push occurred: `merge-20` is a local-only branch with no upstream tracking; `origin/main` (in the main checkout) is untouched at a different commit.

## Out of scope changes
None. Working tree shows only `.sdlc/merge-tickets-20/step-1/builder-L3.md` and `runs.jsonl` untracked — the builder's own run artifacts for this task, not part of the merge commit or the tracked tree.

## For the next attempt
None.
