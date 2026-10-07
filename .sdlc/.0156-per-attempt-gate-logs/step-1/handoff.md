## Task goal
A retried gate keeps every attempt's log, so the first failure survives.

## Step 1: Per-attempt gate log files in fanout.py
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
A ticket is retried by running `fanout.py run` again after it went red, with the same lanes dir and a reused integration branch. Today that rerun overwrites `logs/gate-<lane>-<id>-<k>.log`: `run_ticket` in `plugins/sdlc-lite/scripts/fanout.py` (around line 607) builds a fixed path, and `run_logged` opens it with `'wb'`. I ran a probe with a red first run and a green rerun. It found only `attempt-two` in the single gate log. sdlc-lite owns this overwrite, so this ticket is not "not-sdlc".

1. In `run_ticket`, pick an attempt number `n` for each gate log. `n` is 1 plus the highest attempt already in `ctx['logs']` for `gate-<lane>-<id>-<k>-a*.log`, parsed with a regex, never ordered by mtime, and 1 when there is none. Write the gate output to `logs/gate-<lane>-<id>-<k>-a<n>.log`. The name has two parts:
   - `<k>` still numbers the gates.
   - `a<n>` numbers the attempts.
   
   Only one lane runs a given ticket, and gates run under the merge lock, so two writers can never race for the same name. `run_logged` keeps writing a fresh file, and every line keeps its `[<run_id>] ` prefix. Leave driver logs (`<lane>-<id>.log`) as they are; they are out of scope.
2. Update the module docstring:
   - The step 5 line that names `logs/gate-<lane>-<id>-<k>.log` gets the new name and says the attempt number grows on each rerun.
   - The sentence "Driver and gate log files keep their names and are overwritten" becomes: driver logs are overwritten, and gate logs are never overwritten, one file per attempt.
   - Fix the `run_logged` docstring if it says otherwise.
3. Update the fanout entry in `docs/references/sdlc-internals.md` the same way: replace `logs/gate-<lane>-<id>-<k>.log` with the per-attempt name and say earlier attempts survive.
4. Selftest in the same file:
   - In the resume case (case 9), rename the `'gate-alpha-T-0001-1.log'` references to the attempt-1 name. The gate first runs in that case's second run.
   - Add a case 10, commented `# 10. Gate retry case`, whose expect labels start with `gate retry case`. The setup is one lane `alpha=T-0001` with the stub-style driver (it writes a file and a `filer-L1.md` with `## Warnings` and `## Follow-ups`). The gate prints `attempt-one` and exits 1 until a marker file exists, then prints `attempt-two`.
   - Run 1 is red and exits 1. Then create the marker, remove the integration and lane worktrees and the lane branch as case 9 does, and run 2 merges and exits 0.
   - Expect `gate-alpha-T-0001-1-a1.log` to hold `attempt-one` and `gate-alpha-T-0001-1-a2.log` to hold `attempt-two`.
   - Add one line about case 10 to the docstring's selftest paragraph.

This step is also the gates green step: run `bash plugins/sdlc-lite/scripts/check.sh` and `python3 scripts/check-packaging.py` and fix any red this step introduced.
### Acceptance criteria
- Two-run probe. Every command runs in a `mktemp -d` dir outside the work tree, and the probe is red on the current tree:
  - Setup: a throwaway repo, one ready ticket T-0001, and a driver that writes `f.txt` and a two-section `filer-L1.md`.
  - The gate is red until a marker file exists.
  - Run 1 exits 1. Then touch the marker, remove both worktrees and the lane branch, and run 2 succeeds.
  - Pass condition: `attempt-one` and `attempt-two` are found in two different `gate-alpha-T-0001-1*.log` files.
  
  Run it as this one command, from the repository root:
  ```
  bash -c 'F=$PWD/plugins/sdlc-lite/scripts/fanout.py; d=$(mktemp -d) && git init -q -b main "$d/r" && cd "$d/r" && git config user.email t@e.invalid && git config user.name t && git config commit.gpgsign false && mkdir -p .sdlc/a && printf -- "---\nid: T-0001\ntitle: \"x\"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n" > .sdlc/a/handoff.md && git add -A && git commit -qm f && g="if test -e $d/ok; then echo attempt-two; else echo attempt-one; exit 1; fi" && dr="echo hi > f.txt; printf \"## Warnings\nNone\n\n## Follow-ups\nNone\n\" > \"\$FANOUT_ROOT/\$FANOUT_SLUG/filer-L1.md\"" && { python3 "$F" run alpha=T-0001 --integration fanout/p --lanes-dir "$d/l" --driver "$dr" --gate "$g" >/dev/null 2>&1; test $? -eq 1 || exit 1; } && touch "$d/ok" && git worktree remove --force "$d/l/integration" && git worktree remove --force "$d/l/alpha" && git branch -qD fanout/p-alpha && python3 "$F" run alpha=T-0001 --integration fanout/p --lanes-dir "$d/l" --driver "$dr" --gate "$g" >/dev/null 2>&1 && a=$(grep -l attempt-one "$d"/l/logs/gate-alpha-T-0001-1*.log) && b=$(grep -l attempt-two "$d"/l/logs/gate-alpha-T-0001-1*.log) && test "$a" != "$b"'
  ```
- `grep -qF "gate retry case" plugins/sdlc-lite/scripts/fanout.py`
- `! grep -qF "gate-<lane>-<id>-<k>.log" plugins/sdlc-lite/scripts/fanout.py docs/references/sdlc-internals.md`
- `! grep -qF "Driver and gate log files keep their names and are overwritten" plugins/sdlc-lite/scripts/fanout.py`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" ":(exclude)plugins/sdlc-lite/scripts/fanout.py" ":(exclude)docs/references/sdlc-internals.md"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check`
