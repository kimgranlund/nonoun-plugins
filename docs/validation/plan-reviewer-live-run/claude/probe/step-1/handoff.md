## Task goal
`greet.sh` prints `hello <name>` for the name given as its first argument (`bash greet.sh Ada` prints `hello Ada`) and `hello world` with no argument.

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
