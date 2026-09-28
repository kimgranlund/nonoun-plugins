<!-- role=planner level=L3 model=fable effort=xhigh -->
## Goal
`python3 plugins/sdlc-lite/scripts/steps.py selftest` turns red when a done L3 build no longer maps to `verify L2`, so a mutant that maps L3 to verifier L3 fails the selftest by name.

## Step 1: Add the L3 build → verify L2 selftest case
level: L1
### Do
In `plugins/sdlc-lite/scripts/steps.py`, in `selftest()`, right after the `next verify: build L4 done, no verifier -> verify L3` check (the `check(...)` call ending near line 997), add, in the same two-line style as its neighbours:
`check('next verify: build L3 done, no verifier -> verify L2', nxt(step(3, [('builder-L3.md', DONE)]), 'verify L2'))`

The work tree already holds exactly this 2-line addition from the superseded attempt (`step-1.superseded-1/builder-L1.md`; `git diff -- plugins/sdlc-lite/scripts/steps.py` shows it, uncommitted; the verifier there found the build correct and only the criteria defective). If it is there at that position, leave it, report Changes as none needed, and run the checks. If it is missing, add it. Touch nothing else: not `verifier_level`, not `next_action`, no file outside steps.py. Never commit.

For the mutant check, copy the whole `plugins/sdlc-lite/scripts/` directory, never steps.py alone: steps.py does `import order` from its sibling module, so a lone copy dies with `ModuleNotFoundError` before any case runs. The criterion below writes the mutant with `sed` into the copy and never touches the tree.
### Acceptance criteria
- `grep -q "build L3 done, no verifier -> verify L2" plugins/sdlc-lite/scripts/steps.py`: the case is present. (The planner confirmed the same grep exits 1 against HEAD's copy of the file via git show HEAD:plugins/sdlc-lite/scripts/steps.py; it is green on the current work tree only because the superseded attempt's edit is still there, uncommitted.)
- Mutant check, in a temp copy of the whole scripts dir, never on the tree: `tmp=$(mktemp -d) && cp -R plugins/sdlc-lite/scripts "$tmp/scripts" && sed 's/else 2 if build_level == 3 else 3/else 3/' plugins/sdlc-lite/scripts/steps.py > "$tmp/scripts/steps.py" && ! cmp -s plugins/sdlc-lite/scripts/steps.py "$tmp/scripts/steps.py" && ! python3 "$tmp/scripts/steps.py" selftest > "$tmp/out" 2>&1 && grep -q 'build L3 done, no verifier -> verify L2' "$tmp/out"` exits 0: the copy's `verifier_level` maps a L3 build to verifier 3 (the copy differs from the tree), the copy's selftest exits non-zero, and its FAIL list names the `build L3 done, no verifier -> verify L2` case. (Planner observation: the same mutant applied to HEAD's steps.py leaves the selftest at PASS, which is the gap this step closes.)
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1) && printf '%s\n' "$out" | tail -1 | grep -q '^steps selftest: PASS$'`: the tree's selftest exits 0 and ends with `steps selftest: PASS` (about 40 s, writes only under a temp dir).
- (guard) `test "$(git diff -- plugins/sdlc-lite/scripts/steps.py | grep -c '^-[^-]')" -eq 0`: the steps.py diff versus HEAD deletes no line.
- (guard) `! git diff -U0 -- plugins/sdlc-lite/scripts/steps.py | grep '^@@' | grep -qv 'def selftest'`: every hunk in the steps.py diff versus HEAD sits inside `selftest()` (git's hunk headers name the enclosing top-level def), so `verifier_level` and `next_action` are untouched.
- (guard) `test -z "$(git --no-optional-locks status --porcelain -- . ':(exclude).sdlc' ':(exclude)plugins/sdlc-lite/scripts/steps.py')"`: no path outside `.sdlc/` other than steps.py is modified, staged, or untracked. `.sdlc/` is excluded on purpose: the task handoff was edited before the plan and role runs write there.
- `plugins/sdlc-lite/scripts/check.sh` exits 0 on the tree and shows no new findings versus HEAD: run the same command in a `git worktree add <tmp> HEAD` copy and compare the two outputs' FAIL, error, and warn lines. Not tagged (guard) on purpose: it takes about 140 s on this host, too close to the 300 s `split --only` guard timeout under load.

## Risks
- The work tree already holds the built change, so the two new-behavior criteria are green on the current tree and red only versus HEAD. If the conductor reverts the tree before the rebuild, the builder adds the two lines again; both paths satisfy every criterion.
- The "nothing else dirty outside `.sdlc/`" guard goes red if another process writes outside `.sdlc/` in this worktree during the step (a stray scratch file, a parallel lane sharing the checkout). That is a real finding about the tree, not a defect in the plan; the verifier should name the path.
- The hunk-header guard relies on git's default funcname heuristic naming `def selftest():` for hunks inside it; verified on the current diff (`@@ -997,0 +998,2 @@ def selftest():`). A future edit at column 0 inside `selftest()` is impossible in Python, so the heuristic holds for this file.
- The `git worktree add <tmp> HEAD` comparison for check.sh adds and removes a temporary worktree; that is the comparison method this repo's rules name, and it touches no branch or commit.
