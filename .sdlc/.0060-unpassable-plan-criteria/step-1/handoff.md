## Task goal
A plan criterion that cannot pass is caught before any build, and a plan defect goes to replan instead of a rebuild.

## Step 1: steps.py lints criterion commands and refuses a plan that does not parse
level: L3
### Do
In `plugins/sdlc-lite/scripts/steps.py`:
- Add `lint_steps(plan, steps)` returning a list of finding strings (empty when clean). For each block from `parse_steps`:
  - Take the lines after a line whose stripped text is `### Acceptance criteria`, up to the next line starting with `## ` or `### `, or the block end. Skip lines inside a ``` fence.
  - On each such line, find Markdown code spans with the regex (`+)(.+?)\1 (a run of backticks to the next run of the same length, non-greedy); strip one space on each side of the content. Skip a span with no whitespace inside (a path or an identifier).
  - Command head: split the content on whitespace; skip leading tokens matching `^[A-Za-z_][A-Za-z0-9_]*=` and a leading `!`; the next token is the head. The span is command-like when `shutil.which(head)` finds it, or the head contains `/`, or it ends with `.py` or `.sh`, or it is one of the builtins `cd`, `test`, `[`, `echo`, `printf`, `export`, `set`, `true`, `false`, `time`, `type`, `command`, `eval`, `exec`, `source`, `.`, or when a skipped assignment token contains `$(`. Every other span (prose, JSX, a `--flag` fragment, `close <slug>`) is skipped. Measured on the 41 plans under `.sdlc/` and `bench/results/`: this keeps 538 of 800 spans and flags three, each a span split by a backtick inside it, which a planner should rewrite anyway.
  - Replace each `<placeholder>` (regex `<[^<>\s][^<>]*>`) with `PLACEHOLDER`, then run `subprocess.run(['bash', '-n', '-c', '--', text], capture_output=True, text=True, timeout=5)`. The `--` is load-bearing: without it bash reads a span starting with `--` as its own option. `bash -n` parses and never executes.
  - A nonzero exit is one finding: `steps: <plan> step <n>: acceptance criterion command does not parse: <span>` followed by bash's stderr lines indented two spaces.
- `split` calls `lint_steps` after `parse_steps` and before the step-dir refusal loop; a non-empty list raises `Fail` with the findings joined by newlines and a last line `plan defect: replan this step (/chain 3)`. Every check still runs before any write.
- Add a `lint <planner.md | task dir>` subcommand: `find_plan`, `parse_steps`, `lint_steps`, nothing written, no `handoff.md` needed. Exit 0 prints `steps lint: ok`; exit 1 prints the same refusal text on stderr.
- Update the module docstring (the `lint` subcommand and the `split` refusal) and `main`.
- Module-level fixtures, importable by the verifier: `BROKEN_CRITERION`, one criterion line whose code span is a grep whose pattern has an unbalanced single quote (the text is `- ` then a span holding `grep -c 'foo' bar'`), and `BROKEN_PLAN`, which is `PLAN` with step 1's `- one works` replaced by `BROKEN_CRITERION`.
- Selftest cases, same style as (a) to (i):
  - (j) `BROKEN_PLAN` in a task dir: `split` is refused (rc 1, stderr non-empty, stdout empty, no file written, via `refused`) and stderr contains `plan defect`, `step 1`, and `does not parse`; `lint` on the plan file exits 1 with `plan defect` on stderr; `lint` on the task dir picks the plan the same way `split` does (a `runs.jsonl` naming the older file as the newest record, as in (c)).
  - (k) a plan whose step 1 criteria hold a multi-token command with quotes (`grep -c "x" scripts/steps.py`), a single-token span (`scripts/steps.py`), a placeholder span (`python3 scripts/board.py --root <tmp>`), an env-prefixed span (`SDLC_DRY_RUN=1 scripts/run.sh builder L3 x.md`), a `$(...)` assignment span (`d=$(mktemp -d) && ls "$d"`), a flag fragment (`--sort recent`), and a prose span with parentheses (`duplicate of T-0002 (beta)`): `split` writes both handoffs and `lint` exits 0 printing `steps lint: ok`.
  - (l) `BROKEN_CRITERION` placed under `### Do` of step 1 instead of under the criteria: `split` writes normally.
  - (m) `BROKEN_CRITERION` inside a ``` fenced block under `### Acceptance criteria`: skipped, `split` writes normally.

In `plugins/sdlc-lite/skills/plan/SKILL.md`: add `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py:*)` to `allowed-tools`, and in step 4 run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint <result path>` after reading the result and report its outcome; a refusal is reported to the user as a plan defect.

In the repo-root `CLAUDE.md`, the `scripts/steps.py` layout bullet: `split` refuses, with `plan defect` on stderr, a plan whose criterion command spans do not parse under `bash -n`, and `lint <planner.md | task dir>` runs the same check and writes nothing.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 and its stdout has an `ok:` line for each of (j), (k), (l), and (m).
- Negative control: `cd plugins/sdlc-lite/scripts && python3 -c "import steps; steps.lint_steps = lambda *a, **k: []; raise SystemExit(steps.selftest())"` exits 1 and its stderr names case (j) and no other case.
- `cd plugins/sdlc-lite/scripts && d=$(mktemp -d) && python3 -c "import steps, sys; open(sys.argv[1] + '/handoff.md', 'w').write(steps.HANDOFF); open(sys.argv[1] + '/planner-L2.md', 'w').write(steps.BROKEN_PLAN)" "$d" && python3 steps.py split "$d"; echo "rc=$?"; ls "$d"` prints `rc=1`, its stderr contains `plan defect` and `step 1`, and the listing has no `step-1`.
- `python3 plugins/sdlc-lite/scripts/steps.py lint .sdlc/0060-unpassable-plan-criteria/planner-L3.md` exits 0 and prints `steps lint: ok` (this plan passes its own lint).
- `python3 plugins/sdlc-lite/scripts/steps.py --help` lists `lint`.
- `grep -n 'scripts/steps.py' CLAUDE.md | grep -c 'plan defect'` prints `1`, and `grep -c 'steps.py lint' plugins/sdlc-lite/skills/plan/SKILL.md` prints at least `1`.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0.
