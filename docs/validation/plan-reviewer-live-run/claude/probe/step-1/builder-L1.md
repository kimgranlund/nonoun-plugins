<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- greet.sh: replaced `echo hello` with `name=${1:-world}` and `echo "hello $name"`. The shebang line is unchanged.

## Checks
- `bash greet.sh Ada` printed `hello Ada`. Pass.
- `bash greet.sh` printed `hello world`. Pass.
- `bash greet.sh Ada Lovelace` printed `hello Ada`. Pass.
- The `git diff --name-only` criterion, run with `$SDLC_BASE_SHA` and excluding `.sdlc`, listed only `greet.sh`. Pass.
- Guard `bash -n greet.sh` passed.
- Guard on line 1 being `#!/usr/bin/env bash` passed.

## Notes
None
