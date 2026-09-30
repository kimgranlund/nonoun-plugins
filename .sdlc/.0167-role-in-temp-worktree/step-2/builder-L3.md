<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run-selftest.sh`: added a `Temporary worktree recipe:` header paragraph. Added one line to the shared stub `claude` (`pwd -P >"$tmp/cwd"`) so it records the directory the role ran in. Added the recipe case just before the final PASS line. The case builds a source repo with `.gitignore` holding `.sdlc/`, makes a `git clone --bare` to `proj.git`, and adds a primary worktree on the default branch plus a `user-work` worktree. It makes the primary dirty, puts the handoff at `.sdlc/t/handoff.md`, and takes the snapshots. Then it runs the recipe: a `mktemp -d` path, a detached add from the bare repo, `run.sh scout L1 <abs handoff>` from inside it, and a remove without `--force` followed by `rmdir` of the mktemp parent. It then checks every assertion listed in the handoff. Each fail reason starts with `temporary worktree recipe:`.
- The `chain/SKILL.md` and `run-operations.md` diffs in the tree are from step 1. This step did not touch them.

## Checks
- AC1 `grep -qF 'Temporary worktree recipe' ... && grep -qF 'clone --bare' ... && bash plugins/sdlc-lite/scripts/run-selftest.sh`: printed `run selftest: PASS`, rc=0.
- AC2 `out=$(bash plugins/sdlc-lite/scripts/run-selftest.sh 2>&1) && printf '%s\n' "$out" | tail -1 | grep -qx 'run selftest: PASS'`: rc=0.
- Negative control 1 (run.sh runs from the primary). I used Edit to change the case's run line to `(cd "$primary" && STUB_RESULT=... "$here/run.sh" scout L1 "$primary/.sdlc/t/handoff.md"` and ran `bash plugins/sdlc-lite/scripts/run-selftest.sh`. Result: `run selftest: FAIL: temporary worktree recipe: the role ran in '/private/var/folders/.../tmp.ga8D7CYdK7/proj/main', want the temporary worktree /private/var/folders/.../recipe.kQYMXj/wt`, rc=1.
- Negative control 2 (handoff copied into the temporary worktree). I used Edit to add `mkdir -p "$wt/.sdlc/t" && cp "$primary/.sdlc/t/handoff.md" "$wt/.sdlc/t/handoff.md"` and point run.sh at `"$wt/.sdlc/t/handoff.md"`, then ran `bash plugins/sdlc-lite/scripts/run-selftest.sh`. Result: `run selftest: FAIL: temporary worktree recipe: /private/var/folders/.../tmp.GnV1Ir9tUn/proj/main/.sdlc/t/scout-L1.md is missing`, rc=1.
- Restore: I used Edit to put back `(cd "$wt" && ... scout L1 "$primary/.sdlc/t/handoff.md"`. After that, AC1 and AC2 above passed.
- Guard, run literally: `command -v shellcheck >/dev/null && shellcheck --severity=warning plugins/sdlc-lite/scripts/run-selftest.sh` gave rc=1, because shellcheck is not installed on this host (`command -v shellcheck` rc=1, and none in /opt/homebrew/bin or /usr/local/bin).
- Guard with shellcheck provided: I put a temporary shim on PATH that runs `pipx run --spec shellcheck-py shellcheck` (ShellCheck 0.11.0) and ran the same guard command. rc=0, no findings. The base version of the file (`git show $SDLC_BASE_SHA:...`) also gave rc=0.
- Shellcheck control: the same pipx shellcheck on a scratch file reported SC2034, SC2115 and SC2154 at warning severity, so it does catch problems.
- `git diff --check`: rc=0.

## Notes
- The shellcheck guard fails as written on this host only because the tool is missing; that is the host setup, not the change. The verifier needs shellcheck on PATH to run it, for example through a shim that runs `/Users/kimgranlund/Library/Python/3.9/bin/pipx run --spec shellcheck-py shellcheck "$@"`. With that shim the guard passes. `check.sh` skips shellcheck when it is not installed.
- I added one assertion beyond the handoff's list: the stub records `pwd -P`, and the case checks that the role ran in `$wt`. Without it, negative control 1 would still pass, because `.sdlc/` is ignored in the primary and a run from there changes nothing the listed assertions check. The handoff says that control must fail, so the check is needed.
- The case works under `rtmp=$(cd "$tmp" && pwd -P)` so paths compare as physical paths on macOS (`/var` resolves to `/private/var`). The mktemp parent is created under `$rtmp`, not the system temp dir.
- No worktree-add text went into any Bash call. The case and both controls were written with the Edit tool (an earlier heredoc attempt was blocked by the hook before it wrote anything). No live model run was made.
