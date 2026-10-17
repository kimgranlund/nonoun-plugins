<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
fail

## Criteria
- `grep -n "membership or structure" .claude/agents/sdlc-lite-author.md` finds a match: pass. Evidence: it matched line 18 with rc=0. At HEAD, `git diff HEAD` shows the phrase only on the added `+` line, so the check was red before the build.
- `grep -n "can go red" .claude/agents/sdlc-lite-author.md` finds a match: pass. Evidence: it matched line 18 with rc=0. The phrase exists only on the `+` line of the diff, so the check was red at HEAD.
- `git diff --quiet HEAD -- ...` exits 1 and `grep -c '^-[^-]'` is `0`: pass. Evidence: `quiet_rc=1`, and the count is `0`.
  - Blind spot: the removed line is the bullet itself. Git shows it as `-- Plan-defect ...`, and `^-[^-]` can never match a removed markdown bullet.
  - So I checked "existing wording unchanged" a second way. A Python compare of `git show HEAD:` against the working file: both are 45 lines, only index 17 (line 18) differs, and the new line starts with the old line verbatim. The existing wording is kept.
- `git diff --stat HEAD | awk '{print $1}'` lists only `.claude/agents/sdlc-lite-author.md`, and `git ls-files --others --exclude-standard` prints nothing: fail. Evidence:
  - The diff stat also lists `.sdlc/0134-mirror-the-extended-planner-rules/handoff.md` and a `2` from the summary line.
  - The untracked list shows `planner-L1.md`, `runs.jsonl`, `step-1/builder-L1.md`, `step-1/handoff.md` and `step-1/runs.jsonl`.
  - Steelman (the builder's rebuttal, which holds): the builder did not make these files.
    - The task `handoff.md` mtime is 23:46:16 local (06:46Z). The planner record is `ts 06:47:58Z`. The builder started at about 06:48:21Z (end `07:31:37Z` minus `duration_ms` 2596394).
    - The `step-1/` files are output from `steps.py split`, the builder and run.sh.
  - So the build is right. The criterion cannot pass inside a /chain run, because the pipeline always leaves its own `.sdlc/` artifacts uncommitted.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: `check_rc=0`. The tail shows `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.

## Out of scope changes
None from the builder. The changes outside `.claude/agents/sdlc-lite-author.md` are all pipeline artifacts that existed before or around the build (timestamps above):
- the task `.sdlc/0134-mirror-the-extended-planner-rules/handoff.md`, whose Goal and Constraints were filled in
- `planner-L1.md`
- `runs.jsonl`
- `step-1/`

## For the next attempt
plan defect: criterion 4 (`git diff --stat HEAD | awk '{print $1}'` plus an empty `git ls-files --others --exclude-standard`) can never pass inside a /chain run. The planner's own uncommitted `.sdlc/<task>/` artifacts (task handoff edits, `planner-L1.md`, `runs.jsonl`, `step-<n>/`) are always in the tree, so the check fails whatever the builder does. The build itself needs no change.
swap old: `git diff --stat HEAD | awk '{print $1}'`
swap new: `test "$(git diff --name-only HEAD -- . ':!.sdlc')" = ".claude/agents/sdlc-lite-author.md" && test -z "$(git ls-files --others --exclude-standard -- . ':!.sdlc')"` exits 0 (only the target file changed outside the `.sdlc/` pipeline artifacts, and no new file was added outside `.sdlc/`).

How I tested the swap:
- It parses under `bash -n` and exits 0 on the built tree.
- In a throwaway worktree at HEAD under `$SDLC_TMP_WORKTREES`:
  - As checked out it exits 1. That is the red for the new behavior.
  - With the built target file copied in, it exits 0.
  - With an untracked `stray.txt` added, it exits 1.
  - With `CLAUDE.md` also modified, it exits 1.

Also noted: criterion 3's `grep -c '^-[^-]'` cannot see a removed markdown bullet line, because the diff shows it as `--`. It passes here, and I confirmed the wording is kept with a prefix compare. The next planner should keep this blind spot in mind.
