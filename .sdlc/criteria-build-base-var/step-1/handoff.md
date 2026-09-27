## Task goal
A step's scope criteria compare against the tree the build started from, and that works whether or not anything gets committed later.

## Step 1: run.sh records and exports SDLC_BASE_SHA
level: L3
### Do
In `plugins/sdlc-lite/scripts/run.sh`, only for roles `builder` and `verifier`, and only on a real run (after the `SDLC_DRY_RUN` exit, so a dry run writes nothing), resolve a base and store it in `$dir/base-sha`. `$dir` is the handoff dir, which is the step dir.
1. Read the first line of `$dir/base-sha`. It is valid when `git rev-parse -q --verify "<v>^{commit}"` succeeds and `git merge-base --is-ancestor <v> HEAD` holds.
2. Missing or invalid (junk, a sha that is not an ancestor after a reset or rewrite): base = `git rev-parse HEAD`.
3. Valid: base = the stored sha. Builders commit only on merge steps, so any commit since the base is either the step's work committed separately (keep the base) or a resync merge. So when `git rev-list --first-parent --merges <stored>..HEAD` is non-empty, base = its first line, the newest resync merge on the first-parent chain.
4. Write the base to `$dir/base-sha` when it was missing or changed.
5. Pass `SDLC_BASE_SHA="$base"` in the role's env next to `SDLC_ROLE` on the claude call. For every other role, remove `SDLC_BASE_SHA` from the role's env even when the caller exported it (a verifier running a fixture must not leak its own value), and write no `base-sha`.

Document this in the header comment, including one caveat: on a merge step, the builder's own merge commit moves the base on the verifier run, and merge-step criteria use `HEAD^1` instead.

In `plugins/sdlc-lite/scripts/run-selftest.sh`, add the failing cases together with the fix (ticket constraint) and extend its header comment. Use a stub claude that records `${SDLC_BASE_SHA:-unset}`. The cases:
- the first builder run writes `base-sha` equal to HEAD and the stub sees the same value;
- after a plain commit, a verifier run still sees the old base;
- after a `git merge --no-ff` of a side branch, the next run sees the merge commit and `base-sha` is rewritten to it;
- a `base-sha` holding junk, or a commit that is not an ancestor, is replaced by HEAD;
- a planner run sees `unset` and writes no `base-sha`, even with `SDLC_BASE_SHA` exported by the caller;
- a builder dry run writes no `base-sha`.

Run every criterion from the git toplevel.
### Acceptance criteria
- `rs=$PWD/plugins/sdlc-lite/scripts/run.sh && d=$(mktemp -d) && mkdir -p "$d/bin" "$d/r/s" && printf '%s\n' '#!/usr/bin/env bash' 'echo "${SDLC_BASE_SHA:-unset}" >"$STUB_OUT"' >"$d/bin/claude" && chmod +x "$d/bin/claude" && echo '## Goal' >"$d/r/s/handoff.md" && git -C "$d/r" init -q && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q -m i && (cd "$d/r" && STUB_OUT="$d/out" PATH="$d/bin:$PATH" bash "$rs" builder L1 s/handoff.md >/dev/null 2>&1; true) && test "$(cat "$d/out")" = "$(git -C "$d/r" rev-parse HEAD)" && test "$(cat "$d/r/s/base-sha")" = "$(git -C "$d/r" rev-parse HEAD)"`
- `rs=$PWD/plugins/sdlc-lite/scripts/run.sh && d=$(mktemp -d) && mkdir -p "$d/bin" "$d/r/s" && printf '%s\n' '#!/usr/bin/env bash' 'echo "${SDLC_BASE_SHA:-unset}" >"$STUB_OUT"' >"$d/bin/claude" && chmod +x "$d/bin/claude" && echo '## Goal' >"$d/r/s/handoff.md" && g() { git -C "$d/r" -c user.name=t -c user.email=t@t -c commit.gpgsign=false "$@"; } && g init -q && g add -A && g commit -q -m i && b0=$(g rev-parse HEAD) && r() { (cd "$d/r" && STUB_OUT="$d/out" PATH="$d/bin:$PATH" bash "$rs" "$1" L1 s/handoff.md >/dev/null 2>&1; true); } && r builder && echo w >"$d/r/w.txt" && g add w.txt && g commit -q -m work && r verifier && test "$(cat "$d/out")" = "$b0" && g branch -q side "$b0" && g checkout -q side && g commit -q --allow-empty -m main && g checkout -q - && g merge -q --no-ff -m sync side && r verifier && test "$(cat "$d/out")" = "$(g rev-parse HEAD)" && test "$(cat "$d/r/s/base-sha")" = "$(g rev-parse HEAD)"`
- (guard) `rs=$PWD/plugins/sdlc-lite/scripts/run.sh && d=$(mktemp -d) && mkdir -p "$d/bin" "$d/r/s" && printf '%s\n' '#!/usr/bin/env bash' 'echo "${SDLC_BASE_SHA:-unset}" >"$STUB_OUT"' >"$d/bin/claude" && chmod +x "$d/bin/claude" && echo '## Goal' >"$d/r/s/handoff.md" && git -C "$d/r" init -q && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q -m i && (cd "$d/r" && STUB_OUT="$d/out" PATH="$d/bin:$PATH" bash "$rs" planner L1 s/handoff.md >/dev/null 2>&1; true) && test "$(cat "$d/out")" = unset && test ! -e "$d/r/s/base-sha"`
- `grep -q SDLC_BASE_SHA plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`
