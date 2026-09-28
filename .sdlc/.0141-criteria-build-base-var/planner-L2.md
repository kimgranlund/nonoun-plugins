<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Builder and verifier runs get `SDLC_BASE_SHA`, the commit the step's build started from. It stays put when the work is committed separately and moves past a resync merge, and plans use it for scope criteria in place of `HEAD~1 HEAD` or a bare `HEAD`.

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

## Step 2: steps.py sets SDLC_BASE_SHA for guard and swap spans
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py`, run every span with `SDLC_BASE_SHA` set in its env, so a criterion that names it runs the same under `split --only` and `swap` as under a builder or verifier. Always set the value, never inherit it from the caller's env.
- In `run_guards`/`run_guard`, for `split --only`: set it to `git rev-parse HEAD` at the git toplevel. No build has started, so HEAD is the base.
- In `swap`: set it to the first line of `<step dir>/base-sha` when that is a valid commit, else HEAD.
- Outside git, leave it unset.

Update the module docstring and help text. Add selftest cases:
- `split --only` passes a guard `test "$SDLC_BASE_SHA" = "$(git rev-parse HEAD)"`;
- a `swap` new span sees the stored `base-sha` value;
- `lint` does not flag a criterion `git diff --name-only "$SDLC_BASE_SHA"` as pinning a sha. `pins_sha` already allows it; the case pins that.

Run criteria from the git toplevel.
### Acceptance criteria
- `sp=$PWD/plugins/sdlc-lite/scripts/steps.py && d=$(mktemp -d) && git -C "$d" init -q && git -C "$d" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q --allow-empty -m i && mkdir "$d/t" && printf '## Goal\ng\n' >"$d/t/handoff.md" && printf '## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- (guard) \140test "$SDLC_BASE_SHA" = "$(git rev-parse HEAD)"\140\n\n## Risks\nNone\n' >"$d/t/planner-L2.md" && python3 "$sp" split --only 1 "$d/t" && test -f "$d/t/step-1/handoff.md"`
- `grep -q SDLC_BASE_SHA plugins/sdlc-lite/scripts/steps.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`

## Step 3: Planner rule, role prompts, docs, and check.py guard for SDLC_BASE_SHA
level: L2
### Do
- `plugins/sdlc-lite/agents/planner.md` rule 6: name `$SDLC_BASE_SHA` as the build-start base. run.sh exports it to builder and verifier: HEAD at the step's first builder run, kept in the step dir's `base-sha`, moved past a resync merge. `steps.py split --only` and `swap` set it too. Scope criteria (which files the step changed) use `git diff --name-only "$SDLC_BASE_SHA"` plus `git ls-files --others --exclude-standard`. They never use `git diff HEAD~1 HEAD`, because builders never commit except on Merge steps, and never a bare `git diff HEAD`, which goes vacuous once the work is committed separately.
- Rule 13: its `git diff --quiet HEAD -- <path>` becomes `git diff --quiet "$SDLC_BASE_SHA" -- <path>`.
- `plugins/sdlc-lite/agents/builder.md` item 8 and `plugins/sdlc-lite/agents/verifier.md` item 4: the pre-build HEAD is `$SDLC_BASE_SHA` (still `HEAD^1` on a merge step), e.g. `git worktree add --detach "$SDLC_TMP_WORKTREES/base" "$SDLC_BASE_SHA"`.
- `plugins/sdlc-lite/scripts/check.py`: add an `'SDLC_BASE_SHA'` entry to `PLAN_DEFECT_DOCS` covering `agents/planner.md`, `agents/builder.md`, `agents/verifier.md`, `scripts/run.sh`, and `scripts/steps.py`, and describe it in the docstring's item 5.
- Repo-root `CLAUDE.md` (run.sh and steps.py paragraphs, plus the plan-defect Decision where the planner rules are listed) and `.claude/agents/sdlc-lite-author.md`: describe `SDLC_BASE_SHA` and the `base-sha` file.
- No em dashes.
### Acceptance criteria
- `grep -qF 'git diff --name-only "$SDLC_BASE_SHA"' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'SDLC_BASE_SHA' plugins/sdlc-lite/agents/builder.md`
- `grep -qF 'SDLC_BASE_SHA' plugins/sdlc-lite/agents/verifier.md`
- `grep -qF 'SDLC_BASE_SHA' CLAUDE.md`
- `grep -qF 'SDLC_BASE_SHA' .claude/agents/sdlc-lite-author.md`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite "$d/p" && perl -pi -e 's/SDLC_BASE_SHA/X/g' "$d/p/agents/planner.md" && python3 "$d/p/scripts/check.py" "$d/p" 2>&1 | grep 'agents/planner.md' | grep -q SDLC_BASE_SHA`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`

## Step 4: gates green
level: L2
### Do
Run `bash plugins/sdlc-lite/scripts/check.sh` and every gate below, and fix any red the earlier steps introduced. `scripts/hook-selftest.sh` is left out of the guards on purpose. At plan time it failed 2 of 3 runs with exit 141 (SIGPIPE) on block-repo-format "verifier allows" fixtures, and this ticket does not touch hooks. Run it once, and report its outcome and any 141 in Notes as a pre-existing flake. Do not fix it here.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/skills/decompose/scripts/coverage_check.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/order.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh plugins/sdlc-lite/scripts/check.sh`
- (guard) `claude plugin validate plugins/sdlc-lite`

## Risks
- The refresh rule assumes that any first-parent merge after the base is a resync. If the step's work was committed and main was merged in afterwards, the new base sits past that work, so the scope diff misses it. A merge step's own merge commit also moves the base, which is harmless only because merge-step criteria use `HEAD^1`.
- The ticket's alternative, `git merge-base HEAD <target>`, was not chosen because run.sh does not know the target branch. Fanout lanes would need to pass `--integration` in to make it work.
- `hook-selftest.sh` flakes with exit 141 before any change, so `check.sh` as a whole can be red for reasons unrelated to this work. Step 4 guards list its other gates individually.
- The run.sh fixture criteria in Step 1 run a stub `claude` in a mktemp repo. They depend on run.sh writing `base-sha` before the claude call. If run.sh writes it only after a successful result, those criteria stay red, because the stub prints no result.
