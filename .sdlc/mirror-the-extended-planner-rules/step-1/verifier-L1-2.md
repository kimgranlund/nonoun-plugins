<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -n "membership or structure" .claude/agents/sdlc-lite-author.md` finds a match: pass. Evidence: the match is on `18:- Plan-defect route: ...` with rc=0. The check bites: `git show HEAD:.claude/agents/sdlc-lite-author.md | grep -c "membership or structure\|can go red"` prints `0`, so the phrase is absent at HEAD.
- `grep -n "can go red" .claude/agents/sdlc-lite-author.md` finds a match: pass. Evidence: the match is on line 18 with rc=0. It bites: in a throwaway worktree at HEAD under `$SDLC_TMP_WORKTREES`, `grep -q "can go red"` gives rc=1.
- `git diff --quiet HEAD -- .claude/agents/sdlc-lite-author.md` exits 1, and `git diff HEAD -- ... | grep -c '^-[^-]'` is `0`: pass. Evidence:
  - The first conjunct gives `quiet=1` on the built tree and `headquiet=0` in the HEAD worktree, so it bites.
  - The second conjunct gives `0`. Its blind spot: the removed bullet line shows as `-- Plan-defect ...`, which `^-[^-]` cannot match.
  - So I checked "existing wording unchanged" a second way, with a Python compare of `git show HEAD:` against the working file. Output: `45 45 [17] True`. Both have 45 lines, only line 18 differs, and every new line starts with its old line verbatim. Only text was appended.
- `test "$(git diff --name-only HEAD -- . ':!.sdlc')" = ".claude/agents/sdlc-lite-author.md" && test -z "$(git ls-files --others --exclude-standard -- . ':!.sdlc')"` exits 0: pass. Evidence: `rc4=0` on the built tree and `headrc4=1` in the HEAD worktree, so it bites. This is the criterion from the earlier verifier's swap, now in the handoff.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: `check=0`. The tail shows `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
- Content check against the Do: the diff appends two sentences to the bullet on line 18.
  - "A `(guard)` is a check that can go red: the planner sees it red first, un-negated or on a fixture, before writing it."
  - "A file other lanes also change (a generated index, a registry, a catalog, a shared config) is checked by membership or structure, never by an exact line or a whole-file comparison."
  - Both match rules (a) and (b) in the Do.

## Out of scope changes
None.
- `git status --short` also shows a modified `.sdlc/mirror-the-extended-planner-rules/handoff.md` and untracked `planner-L1.md`, `runs.jsonl` and `step-1/`. These are /chain pipeline artifacts under `.sdlc/`, which criterion 4 excludes on purpose.
- The earlier verifier traced them to the planner and split by timestamp. Nothing outside `.sdlc/` changed except the target file (criterion 4 run above, rc=0).

## For the next attempt
None.
