## Task goal
Merge the `feature` lane into `main` so both lanes' behavior survives.

## Step 1: Merge feature
level: L2
### Do
Run `git merge --no-ff feature` on a tree with no uncommitted tracked changes. Resolve every conflict so both lanes' intent survives, run the gates below, and create the merge commit. Never push.
Both lanes' intent: `main` added a `-l` loud flag to `greet.sh`; `feature` made the name default to `World`. After the merge `sh greet.sh` prints `Hello, World`, `sh greet.sh Ann` prints `Hello, Ann`, and `sh greet.sh -l Bo` prints `HELLO, Bo!`. `test.sh` keeps both lanes' checks.
### Acceptance criteria
- `test "$(git rev-list --parents -n1 HEAD | wc -w)" -eq 3`
- `git merge-base --is-ancestor feature HEAD`
- (guard) `! git rev-parse -q --verify MERGE_HEAD`
- (guard) `git diff -z --name-only --diff-filter=d HEAD^1 HEAD | xargs -0 sh -c 'test $# -eq 0 || ! git grep -nE "^(<<<<<<<|>>>>>>>)( |$)" -- "$@"' sh`
- (guard) `sh test.sh` shows no new findings versus the first parent: run the same command in a `git worktree add <tmp> HEAD^1` copy and compare.
- `sh test.sh` prints `ok`, `ok-default`, and `ok-loud` and exits 0.
