## Task goal
Make the verifier model-family rule fire for a verifier launched at the task directory, on Claude and on Codex.

## Step 3: Live run of a task-dir verifier on Claude Code
level: L2
### Do
Targets:
- `docs/reports/runner-family-task-dir-live-run.md`, modeled on `docs/reports/plan-reviewer-live-run.md`.
- The evidence folder `docs/reports/runner-family-task-dir-live-run/`, holding `fam/` (a copy of the throwaway task dir), `dry-run-base.txt`, and `dry-run-fixed.txt`.
- One line in `docs/README.md`.

Depends on: steps 1 and 2.

This step runs this worktree's fixed `plugins/sdlc-lite/scripts/run.sh` on purpose, because that file is what is under test. Nothing edits run.sh during this step, and the conductor still launches this builder from the main checkout's run.sh.

1. Record these, for the report:
   - `claude --version` (2.1.286 at plan time);
   - `git rev-parse --short HEAD`;
   - `git hash-object plugins/sdlc-lite/scripts/run.sh`, which binds the evidence to the run.sh blob assessed;
   - `git status --porcelain -- plugins/`. Steps 1 and 2 are uncommitted because builders never commit, and the report says so.
2. Define a shell function `W` that runs `env` with these arguments, in order:
   - `-u CLAUDECODE`;
   - one `-u` for every set variable named `CLAUDE_CODE_*` or `SDLC_*`;
   - `SDLC_BACKEND=claude`;
   - then W's own arguments.

   Calls look like `W bash <run.sh> ...` and `W SDLC_DRY_RUN=1 bash <run.sh> ...`. A nested run then inherits no base sha, attempt id or name, lifecycle-child flag, or temp-worktree prefix (precedent: the Method section of `plan-reviewer-live-run.md`). `<repo>` below is this worktree's absolute path.
3. Build the throwaway project at `P=$(mktemp -d)/claude`, outside this repository:
   - `git init`;
   - `greet.sh` holding `#!/usr/bin/env bash` and `echo hello`;
   - `.gitignore` holding `.sdlc/` and `.worktrees/`;
   - one commit, `init`.

   Then write two handoffs by hand:
   - `.sdlc/fam/handoff.md`:
     - a Goal section: `greet.sh` prints `hello <name>` for its first argument and `hello world` with none;
     - a Context section: one step, built in `step-1/`; verify the whole task against the criteria below;
     - an Acceptance criteria section with the two checks `test "$(bash greet.sh Ada)" = "hello Ada"` and `test "$(bash greet.sh)" = "hello world"`.
   - `.sdlc/fam/step-1/handoff.md`, in the step template:
     - a `## Step 1: Name argument for greet.sh` line;
     - `level: L1`;
     - a Do subsection saying to use `name=${1:-world}` and print `hello $name`;
     - an Acceptance criteria subsection with the same two checks.

   No builder result is ever written in `.sdlc/fam/` itself.
4. From `$P`, run `W bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/fam/step-1/handoff.md`. This is a live Sonnet low run. It must exit 0, and its result's first line must be `<!-- role=builder level=L1 model=sonnet effort=low -->`. Any Status is acceptable for this evidence.
5. Negative control, with no model call:
   - Extract the base plugin with `git archive "$SDLC_BASE_SHA" plugins/sdlc-lite | tar -x -C <tmp>`.
   - From `$P`, run `W SDLC_DRY_RUN=1 bash <tmp>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md` and redirect stdout to `dry-run-base.txt`.
   - Run the same command with `<repo>/plugins/sdlc-lite/scripts/run.sh`, stdout to `dry-run-fixed.txt`.
   - Write both files only by redirection, never by hand. Expected: the base file holds `--model sonnet --effort medium` and the fixed file holds `--model opus --effort medium`.
6. From `$P`, run `W bash <repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md` (live).
   - Expect exit 0. Verdict pass or fail are both fine, because the evidence is the model.
   - The result's first line must be `<!-- role=verifier level=L1 model=opus effort=medium -->`.
   - Read the `"model"` field of the init event in `.sdlc/fam/verifier-L1.log` (expected `claude-opus-*`) and record it. Do the same for the builder log. Logs never enter this repo.
7. Copy the task dir with `rsync -a --exclude '*.log' --exclude '*.running' --exclude '.run.lock' "$P/.sdlc/fam/" docs/reports/runner-family-task-dir-live-run/fam/`. Then remove `$P` and the base extract.
8. Outcomes:
   - The live proof failed if item 4 or item 6 exits non-zero, or if item 6's header is not `model=opus effort=medium`. In that case:
     - still write the report, with `Result: fail`;
     - end with Status blocked, with the first Notes line `live proof failed: <what>`;
     - never rerun a live role, because a rerun is the user's call at the replan.
   - Otherwise the result is `Result: pass`.
9. Write the report `docs/reports/runner-family-task-dir-live-run.md`:
   - `# Runner family task dir live run`, a blank line, then `Recorded: <YYYY-MM-DD>`.
   - An intro paragraph: for T-0195, a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in `step-1/`.
   - `## Environment`: the versions, the commit, the run.sh blob hash, the uncommitted step 1 and 2 changes, macOS, the temp project path, and the log model ids.
   - `## Method`: the wrapper, the project setup, and the exact commands of items 4 to 6.
   - `## Results`: a table of arm, result, and evidence for:
     - the builder header;
     - the base dry run (Sonnet) and the fixed dry run (Opus);
     - the verifier header and its `runs.jsonl` line;
     - the log model ids.

     Below the table, exactly one line `Result: pass` or `Result: fail`.
   - `## Limits`:
     - one trial, on Claude only;
     - Codex is covered by `codex-selftest.py` and a dry run, not a live run;
     - the live run has one step, so the choice across steps by number is exercised only by the selftests.
   - No em dash (U+2014). If a quoted evidence line holds one, write it as `\u2014` and say so under Limits. Copied evidence files stay verbatim.
10. In `docs/README.md`, add this line directly after the `- [Messages wait live run](validation/messages-wait-live-run.md): ...` line (line 40). It is a shared file, so the check is membership only.
    `- [Runner family task dir live run](validation/runner-family-task-dir-live-run.md): dated live run for T-0195 showing that a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in step-1/, where the pre-fix run.sh kept Sonnet.`
### Acceptance criteria
- `test "$(head -n 1 docs/reports/runner-family-task-dir-live-run/fam/step-1/builder-L1.md)" = "<!-- role=builder level=L1 model=sonnet effort=low -->"`
- `tail -n 1 docs/reports/runner-family-task-dir-live-run/fam/step-1/runs.jsonl | jq -e '.role == "builder" and .level == "L1" and .model == "sonnet" and .file == "builder-L1.md"'`
- `test "$(head -n 1 docs/reports/runner-family-task-dir-live-run/fam/verifier-L1.md)" = "<!-- role=verifier level=L1 model=opus effort=medium -->"`
- `tail -n 1 docs/reports/runner-family-task-dir-live-run/fam/runs.jsonl | jq -e '.role == "verifier" and .level == "L1" and .model == "opus" and .effort == "medium" and .file == "verifier-L1.md" and .backend == "claude"'`
- `jq -e '.status == "completed" and .model == "opus"' docs/reports/runner-family-task-dir-live-run/fam/verifier-L1.attempt.json`
- `test -d docs/reports/runner-family-task-dir-live-run/fam && test -z "$(find docs/reports/runner-family-task-dir-live-run/fam -maxdepth 1 -name 'builder-*.md')"`
- `grep -qF -- '--agent sdlc-lite:verifier --model sonnet --effort medium' docs/reports/runner-family-task-dir-live-run/dry-run-base.txt && grep -qF -- '--agent sdlc-lite:verifier --model opus --effort medium' docs/reports/runner-family-task-dir-live-run/dry-run-fixed.txt`
- `f=docs/reports/runner-family-task-dir-live-run.md; grep -qE "^Recorded: 2026-[0-9]{2}-[0-9]{2}$" "$f" && for h in "## Environment" "## Method" "## Results" "## Limits"; do grep -qxF "$h" "$f" || exit 1; done`
- `grep -qxF 'Result: pass' docs/reports/runner-family-task-dir-live-run.md`
- `grep -qF "$(git hash-object plugins/sdlc-lite/scripts/run.sh)" docs/reports/runner-family-task-dir-live-run.md`
- `f=docs/reports/runner-family-task-dir-live-run.md; test -f "$f" && ! grep -qF "$(printf '\342\200\224')" "$f"`
- `grep -qF 'validation/runner-family-task-dir-live-run.md' docs/README.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e docs/references/sdlc-internals.md -e plugins/sdlc-lite/scripts/codex_roles.py -e plugins/sdlc-lite/scripts/codex-selftest.py -e docs/references/codex-role-execution.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/reports/runner-family-task-dir-live-run(\.md|/)")"`
