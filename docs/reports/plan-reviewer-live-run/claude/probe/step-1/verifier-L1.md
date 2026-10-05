<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `out=$(bash greet.sh Ada 2>&1) && test "$out" = "hello Ada"`: pass. Evidence: this exits with rc=0 on the built tree. The check bites: at base 0d76272, run in a throwaway worktree, it gives rc=1 because the script prints `hello`.
- `out=$(bash greet.sh 2>&1) && test "$out" = "hello world"`: pass. Evidence: rc=0 on the built tree and rc=1 at base.
- `out=$(bash greet.sh Ada Lovelace 2>&1) && test "$out" = "hello Ada"`: pass. Evidence: rc=0 on the built tree and rc=1 at base. It also catches an all-arguments mutant (`echo "hello ${1:-world} $2"`), which gives rc=1.
- `test "$(git diff --name-only "$SDLC_BASE_SHA" ...; git ls-files --others ...)" = "greet.sh"`: pass. Evidence: rc=0 on the built tree. The check bites in three cases:
  - At base with no changes: rc=1.
  - At base with only an untracked `extra.txt`: rc=1.
  - With greet.sh changed plus `extra.txt`: rc=1.
  - With greet.sh changed and nothing else: rc=0.
- (guard) `bash -n greet.sh`: pass. Evidence: rc=0 on the built tree and at base. Its fixture form bites: a file with an unterminated quote gives rc=2.
- (guard) `test "$(head -n1 greet.sh)" = "#!/usr/bin/env bash"`: pass. Evidence: rc=0 on the built tree and at base. Its fixture form bites: a file whose first line is `#!/bin/sh` gives rc=1.

## Out of scope changes
None. `git status --short` shows only ` M greet.sh`. `git diff` matches the Do exactly: the shebang is kept, and `echo hello` is replaced by `name=${1:-world}` and `echo "hello $name"`. The file mode is still 644 (`stat -f %Lp greet.sh`). I ran every check myself, and the results match the builder's claims in builder-L1.md.

## For the next attempt
None
