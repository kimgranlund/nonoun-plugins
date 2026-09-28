<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add a case to `fanout.py selftest` that runs the stub driver end to end with the default lanes dir (`<toplevel>/.worktrees/fanout`, no `--lanes-dir`). It must prove lane commits, merges and closes, and that `git status` in the main tree stays clean. `fanout.py run` does not change.

## Step 1: Full stub-driver run in the default lanes dir, with main-tree status checks
level: L2
### Do
Edit only `plugins/sdlc-lite/scripts/fanout.py`, in `selftest()` and its docstring. Leave `run` behavior (everything above `# ---------- selftest ----------`) untouched.

1. Add a new numbered case (6) after case 5, inside the same `tempfile.TemporaryDirectory()` block:
   - Build a throwaway repo with `make_repo(...)`, passing `{'.gitignore': '.worktrees/\n'}` as `extra`. Give it at least two `ready` tickets on two lanes, or on one lane with two tickets.
   - Run `fanout(repo, ...)` with `--integration fanout/<name>`, the existing `STUB` script as `--driver` (reuse `stub`, or write a new stub file the same way), and `--gate true`. Pass no `--lanes-dir`.
2. Assert all of the following with `expect(...)`, every label carrying the observed value:
   - The run exits 0.
   - `.worktrees/fanout/report.md` exists and every ticket's outcome is `merged`.
   - Each lane branch `fanout/<name>-<lane>` holds a commit whose subject is exactly `<id>: <title>` for each of its tickets, e.g. `T-0001: Ticket a`. Use `git log --format=%s <lane branch>`.
   - The integration branch has one `--no-ff` merge commit per ticket (`rev-list --merges --count`) and holds each ticket's `<id>.txt`.
   - `.sdlc/<slug>/handoff.md` on the integration branch says `status: done` for each ticket.
   - `main`'s sha is unchanged, and `HEAD` is still `refs/heads/main`.
   - `git status --porcelain --untracked-files=all` in the main repo is exactly `''`. Put the porcelain output into the label so a stray file is named on failure.
   - Non-vacuity: `git status --porcelain --ignored` in the main repo lists `.worktrees/`. This proves the lanes really lived inside the tree.
   - `git worktree list` in the main repo shows the lane and integration worktrees under `.worktrees/fanout/`.
3. Update the `selftest` paragraph of the module docstring (lines about 74 to 85). Add one sentence saying that a full stub-driver run in the default lanes dir under `.worktrees/fanout` proves lane commits `<id>: <title>`, merges and closes, with `git status` in the main tree left clean. Use the literal words `default lanes dir`.
4. Leave CLAUDE.md alone. Its fanout paragraph already says "`selftest` proves it on throwaway repos with a stub driver", and that stays true.

Run all commands from the git toplevel.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- Sabotage probe: a run that leaves a stray file in the main tree only when the lanes dir sits under `.worktrees/` must be caught, with the stray file named in the selftest output. This exits non-zero at HEAD and must exit 0 after the step: `d=$(mktemp -d) && trap 'rm -rf "$d"' EXIT && cp -R plugins/sdlc-lite/scripts "$d/scripts" && python3 -c "import sys,pathlib; p=pathlib.Path(sys.argv[1]); s=p.read_text(); a=\"    (ctx['lanes_dir'] / 'report.md').write_text(text, encoding='utf-8')\n\"; assert s.count(a) == 1; p.write_text(s.replace(a, a + \"    if ctx['lanes_dir'].parent.name == '.worktrees': (ctx['lanes_dir'].parent.parent / 'fanout-stray.txt').write_text('x')\n\"))" "$d/scripts/fanout.py" && python3 "$d/scripts/fanout.py" selftest 2>&1 | grep -q 'fanout-stray.txt'`
- Sabotage probe: a wrong lane commit subject (`<id> <title>` instead of `<id>: <title>`) must fail the selftest. This exits non-zero at HEAD and must exit 0 after the step: `d=$(mktemp -d) && trap 'rm -rf "$d"' EXIT && cp -R plugins/sdlc-lite/scripts "$d/scripts" && python3 -c "import sys,pathlib; p=pathlib.Path(sys.argv[1]); s=p.read_text(); a=\"f'{t.id}: {t.title}'\"; assert s.count(a) == 1; p.write_text(s.replace(a, \"f'{t.id} {t.title}'\"))" "$d/scripts/fanout.py" && ! python3 "$d/scripts/fanout.py" selftest`
- `sed -n '/^selftest$/,/^"""/p' plugins/sdlc-lite/scripts/fanout.py | grep -q 'default lanes dir'`
- `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/tickets.py plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/scripts/board.py`
- Observable: in `git diff HEAD -- plugins/sdlc-lite/scripts/fanout.py`, every hunk falls inside the module docstring, the `STUB` constant or `selftest()`. No line above `# ---------- selftest ----------` changes, except in the docstring.

## Risks
- The selftest already takes about 55s, and `check.sh` about 70s. A new full run adds a few seconds, which is well under the 300s per-call `fanout()` timeout.
- The first sabotage probe depends on the exact report-write line in `report()`, and the second on the exact `f'{t.id}: {t.title}'` literal. If either changes, the probe's `assert` fails and the criterion reads red for a stale-anchor reason, not a real regression.
- The existing case 4 already writes into `.worktrees/fanout` inside its repos. The new case must use its own repo and its own integration branch name so it cannot collide with it.
