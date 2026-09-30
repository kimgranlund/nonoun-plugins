<!-- role=planner level=L3 model=fable effort=xhigh -->
## Goal
`greet.sh` prints `hello <name>` for the name given as its first argument and `hello world` when no argument is given.

## Step 1: greet.sh greets the first argument, defaulting to world
level: L1
### Do
Edit `greet.sh`, the only script in the repo (2 lines at HEAD: `#!/usr/bin/env bash` then `echo hello`). Keep line 1 as it is. Replace `echo hello` with two lines: `name=${1:-world}` and `echo "hello $name"`. Settled interface: the script keeps its `#!/usr/bin/env bash` shebang (greet.sh:1) and stays invoked as `bash greet.sh ...` with no executable bit (mode 644 at HEAD, and the handoff Goal names `bash greet.sh Ada`); it reads only the first positional argument, quoted, so `bash greet.sh Ada Lovelace` prints `hello Ada` (handoff Goal: "the name given as its first argument"); the default `world` comes from the `${1:-world}` idiom, so an empty first argument also prints `hello world` (the handoff Goal names only the given-argument and no-argument cases, and this step does not check the empty-string case). Change no other file (handoff Constraints: "one file"). Depends on: none. This is a one-step plan, so it is also the gates green step: the project has no test suite, lint, or check script (the tree holds only `greet.sh` and `.gitignore`, and no `shellcheck` binary is on this host), so the only gate is the `bash -n` syntax check below. Focused checks: run the three `bash greet.sh` invocations in the criteria and compare the output.
### Acceptance criteria
- `out=$(bash greet.sh Ada 2>&1) && test "$out" = "hello Ada"`
- `out=$(bash greet.sh 2>&1) && test "$out" = "hello world"`
- `out=$(bash greet.sh Ada Lovelace 2>&1) && test "$out" = "hello Ada"`
- `test "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc")" = "greet.sh"`
- (guard) `bash -n greet.sh`
- (guard) `test "$(head -n1 greet.sh)" = "#!/usr/bin/env bash"`

## Assumptions
- `greet.sh` prints `hello` and ignores its arguments at HEAD: verified by `cat -v greet.sh` (line 2 is `echo hello`) and by the three behavior criteria all exiting 1 on the current tree.
- The scope criterion is red now for the right reason (no change yet) and turns green after the intended edit: verified by running it on the current tree (exit 1, empty output) and in a scratch `git init` copy of the repo after applying the Do (exit 0).
- Both guards can go red: verified by `bash -n` on a mktemp fixture with an unterminated string (exit 2) and by the shebang test on a mktemp fixture whose first line is `echo hello` (exit 1); both are green on the current tree and leave the work tree unchanged (`git status --short` empty after the probe run).
- The plan passes structural validation: verified by `steps.py lint` (`steps lint: ok`) and `steps.py split --only 1` (exit 0, guards green) on a copy of this plan in a scratch repo holding the same `greet.sh`, `.gitignore`, and `handoff.md`.
- No `AGENTS.md` exists in the repo: verified by `find . -name AGENTS.md -not -path './.git/*'` returning nothing, so the step has no Read first subsection.
- The project has no test, lint, or check gate beyond bash syntax: verified by `git ls-files` (only `.gitignore` and `greet.sh`) and `command -v shellcheck` (not found).

## Risks
None.
