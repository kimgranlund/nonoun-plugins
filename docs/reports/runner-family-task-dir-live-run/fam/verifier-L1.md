<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `test "$(bash greet.sh Ada)" = "hello Ada"`: pass. Evidence: on the built tree the check exits `c1=0` and `bash greet.sh Ada` prints `hello Ada`. In a throwaway worktree at base `4513a5e` it exits `c1=1` and prints `hello`, so the check goes red without the change.
- `test "$(bash greet.sh)" = "hello world"`: pass. Evidence: on the built tree the check exits `c2=0` and `bash greet.sh` prints `hello world`. At base `4513a5e` it exits `c2=1`, so this check also goes red without the change.

## Out of scope changes
None. `git status` shows only `greet.sh` modified. `git diff` shows it replaced `echo hello` with `name=${1:-world}` and `echo "hello $name"`, which is what the step asked for. The builder's two passed checks in `builder-L1.md` match the runs above. I removed the throwaway worktree afterwards, and `git worktree list` now shows only the main checkout.

## For the next attempt
None
