## Task goal
Make the verifier model-family rule fire for a verifier launched at the task directory, on Claude and on Codex.

## Step 3: Pre-fix negative control and live run report
level: L2
### Do
This replans the first step 3 attempt (`.sdlc/0195-runner-family-task-dir/step-3.superseded-1/builder-L2.md`, Status blocked, `plan defect:`).
- That attempt ran the live builder and verifier. Its evidence is committed in `docs/reports/runner-family-task-dir-live-run/fam/` (commit e2978f5): builder `model=sonnet effort=low`, verifier `model=opus effort=medium`.
- Its negative control archived `$SDLC_BASE_SHA`, which was the step-2 checkpoint aa59ebc. That commit already holds the fix, so the committed `dry-run-base.txt` shows `--model opus` and does not discriminate.
- This attempt reruns only the two dry runs, with no model call, then writes the report and the index line. Never rerun a live role: the live proof passed, and a rerun is the user's call.

Targets:
- `docs/reports/runner-family-task-dir-live-run/dry-run-base.txt` and `docs/reports/runner-family-task-dir-live-run/dry-run-fixed.txt`: rewritten only by shell redirection, never by hand.
- `docs/reports/runner-family-task-dir-live-run.md` (new), modeled on `docs/reports/plan-reviewer-live-run.md`.
- One line in `docs/README.md`.
- `docs/reports/runner-family-task-dir-live-run/fam/` stays exactly as committed.

Depends on: steps 1 and 2, committed in d87cc4b and aa59ebc.

Settled decisions, with evidence:
- The pre-fix commit is the first line of `.sdlc/0195-runner-family-task-dir/step-1/base-sha`: 171e13b72a516ccad2472d866f072add289079cf (`T-0195 plan split`, the parent of the step-1 commit d87cc4b). run.sh wrote it as step 1's build-start base. `git diff 171e13b HEAD -- plugins/sdlc-lite/scripts/run.sh` is exactly the step 1 change. The pre-fix run.sh blob is dc34865ecd542cb3e55516cc4803a7071f3b7364.
- Never take the base from `$SDLC_BASE_SHA` in this step, because it names a commit that already holds the fix.
- The fixed run.sh is this worktree's `plugins/sdlc-lite/scripts/run.sh`, blob e5308edf87a23bd02eb179eab631250a1bf24819 at replan time. The live runs used that same blob (the first attempt's Checks). Nothing edits run.sh in this step.
- The dry runs use a rebuilt project, not the first attempt's temp project. That project's task dir now holds `verifier-L1.md`, so a dry run there names `verifier-L1-2.md`, which is not the state the live verifier started from.
- A planner probe ran items 3 to 5 in a temp dir:
  - the base run printed `--agent sdlc-lite:verifier --model sonnet --effort medium`;
  - the fixed run printed `--model opus --effort medium`;
  - neither wrote anything under the project's `.sdlc/fam/`, because run.sh exits for a dry run at line 316, before the base-sha write.

1. Record, for the report:
   - `claude --version`;
   - `git rev-parse --short HEAD`;
   - `git hash-object plugins/sdlc-lite/scripts/run.sh`;
   - `b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha)` and `git rev-parse "$b:plugins/sdlc-lite/scripts/run.sh"`.
2. Define a shell function `W` as the first attempt did. It runs `env` with `-u CLAUDECODE`, one `-u` for every set variable named `CLAUDE_CODE_*` or `SDLC_*`, then `SDLC_BACKEND=claude`, then its own arguments. A nested dry run then inherits no attempt name, base sha, or role. `<repo>` below is this worktree's absolute path.
3. Rebuild the project at `P=$(mktemp -d)/claude`, outside this repository:
   - `git init`, a `.gitignore` holding `.sdlc/` and `.worktrees/`, and one commit `init`;
   - copy `docs/reports/runner-family-task-dir-live-run/fam/handoff.md` to `$P/.sdlc/fam/handoff.md`;
   - copy `fam/step-1/handoff.md`, `fam/step-1/builder-L1.md`, and `fam/step-1/runs.jsonl` from the same folder to `$P/.sdlc/fam/step-1/`;
   - copy nothing else. The task dir then holds no builder or verifier result, which is the state the live verifier started from.
4. Extract the pre-fix plugin: `X=$(mktemp -d)`, then `git archive "$b" plugins/sdlc-lite | tar -x -C "$X"`.
5. From `$P`, with no model call:
   - `W SDLC_DRY_RUN=1 bash "$X/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/fam/handoff.md > <repo>/docs/reports/runner-family-task-dir-live-run/dry-run-base.txt`
   - `W SDLC_DRY_RUN=1 bash <repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md > <repo>/docs/reports/runner-family-task-dir-live-run/dry-run-fixed.txt`
   - Expected: the base file holds `--model sonnet --effort medium` and the fixed file holds `--model opus --effort medium`. If the base file does not hold Sonnet, write no report. End with Status blocked and the first Notes line `negative control failed: <what>`.
6. Remove `$P` and `$X`. Leave the first attempt's temp dir `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.PDQbvWuqBm` in place: it is outside this repository, and its removal was denied before.
   - If it still exists, read only the `"model"` field of the init event in its `claude/.sdlc/fam/verifier-L1.log` and `claude/.sdlc/fam/step-1/builder-L1.log`.
   - Otherwise cite the ids in the first attempt's Checks: `claude-sonnet-5-5` for the builder, `claude-opus-5-5` for the verifier.
7. Write the report `docs/reports/runner-family-task-dir-live-run.md`:
   - `# Runner family task dir live run`, a blank line, then `Recorded: <YYYY-MM-DD>` alone on its line.
   - An intro paragraph: for T-0195, a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in `step-1/`, where the pre-fix run.sh kept Sonnet.
   - `## Environment`:
     - Claude Code 2.1.286 at the live run, and the version from item 1;
     - the live runs at commit aa59ebc, with steps 1 and 2 committed in d87cc4b and aa59ebc (not uncommitted);
     - the run.sh blob from item 1, used by the live runs and the fixed dry run;
     - the pre-fix commit `$b` (at least its first 7 characters) and its run.sh blob, used by the base dry run;
     - the HEAD from item 1, where the dry runs were rerun;
     - macOS, Darwin 25.6.0, the temp project paths, and the log model ids from item 6.
   - `## Method`:
     - the wrapper `W`;
     - the live project and its two commands from the first attempt: `W bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/fam/step-1/handoff.md`, then `W bash <repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md`;
     - the rebuilt dry-run project and the two commands of item 5;
     - one sentence saying that the first negative control used the step-2 checkpoint, which already held the fix, and that this one replaced it.
   - `## Results`: a table of arm, result, and evidence, with one row each for:
     - the builder header (`model=sonnet effort=low`);
     - the verifier header and its `runs.jsonl` line (`model=opus effort=medium`, backend claude);
     - the log model ids;
     - the base dry run (`--model sonnet`, pre-fix run.sh);
     - the fixed dry run (`--model opus`).

     Below the table, exactly one line `Result: pass`.
   - `## Limits`:
     - one trial, on Claude only;
     - Codex is covered by `codex-selftest.py` and a dry run, not a live run;
     - the live run has one step, so the choice across steps by number is exercised only by the selftests;
     - the dry runs ran in a rebuilt project at a later commit than the live runs, with the same run.sh blob as the live runs.
   - No em dash (U+2014). Copied evidence files stay verbatim.
8. In `docs/README.md`, add this line directly after the `- [Messages wait live run](validation/messages-wait-live-run.md): ...` line (line 40 at replan time). It is a shared file, so the check is membership only.
   `- [Runner family task dir live run](validation/runner-family-task-dir-live-run.md): dated live run for T-0195 showing that a Claude Code verifier launched at the task dir runs on Opus after a Sonnet build in step-1/, where the pre-fix run.sh kept Sonnet.`

Focused checks: the criteria below. This step changes no code, so no selftest runs here. Step 4 runs them all.
### Acceptance criteria
- `grep -qF -- '--agent sdlc-lite:verifier --model sonnet --effort medium' docs/reports/runner-family-task-dir-live-run/dry-run-base.txt`
- `f=docs/reports/runner-family-task-dir-live-run.md; grep -qE "^Recorded: 2026-[0-9]{2}-[0-9]{2}$" "$f" && for h in "## Environment" "## Method" "## Results" "## Limits"; do grep -qxF "$h" "$f" || exit 1; done`
- `grep -qxF 'Result: pass' docs/reports/runner-family-task-dir-live-run.md`
- `grep -qF "$(git hash-object plugins/sdlc-lite/scripts/run.sh)" docs/reports/runner-family-task-dir-live-run.md`
- `b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha); f=docs/reports/runner-family-task-dir-live-run.md; test -n "$b" && grep -qF "${b:0:7}" "$f" && grep -qF "$(git rev-parse "$b:plugins/sdlc-lite/scripts/run.sh")" "$f"`
- `f=docs/reports/runner-family-task-dir-live-run.md; test -f "$f" && ! grep -qF "$(printf '\342\200\224')" "$f"`
- `grep -qF 'validation/runner-family-task-dir-live-run.md' docs/README.md`
- (guard) `grep -qF -- '--agent sdlc-lite:verifier --model opus --effort medium' docs/reports/runner-family-task-dir-live-run/dry-run-fixed.txt`
- (guard) `d=docs/reports/runner-family-task-dir-live-run; n() { sed -E 's/ --plugin-dir [^ ]+ / /; s/ --model [a-z]+ / /; s/ --append-system-prompt-file [^ ]+ / /' "$1"; }; test -s "$d/dry-run-base.txt" && test "$(n "$d/dry-run-base.txt")" = "$(n "$d/dry-run-fixed.txt")"`
- (guard) `r=$PWD; e=docs/reports/runner-family-task-dir-live-run/fam; b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha); t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; git archive "$b" plugins/sdlc-lite | tar -x -C "$t" && git init -q "$t/p" && git -C "$t/p" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit -q --allow-empty -m init && mkdir -p "$t/p/.sdlc/fam/step-1" && cp "$e/handoff.md" "$t/p/.sdlc/fam/" && cp "$e/step-1/handoff.md" "$e/step-1/builder-L1.md" "$e/step-1/runs.jsonl" "$t/p/.sdlc/fam/step-1/" && o1=$(cd "$t/p" && SDLC_BACKEND=claude SDLC_DRY_RUN=1 bash "$t/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/fam/handoff.md 2>/dev/null) && o2=$(cd "$t/p" && SDLC_BACKEND=claude SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" verifier L1 .sdlc/fam/handoff.md 2>/dev/null) && printf '%s\n' "$o1" | grep -qF -- '--agent sdlc-lite:verifier --model sonnet --effort medium' && printf '%s\n' "$o2" | grep -qF -- '--agent sdlc-lite:verifier --model opus --effort medium'`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- docs/reports/runner-family-task-dir-live-run/fam && test -z "$(git ls-files --others --exclude-standard -- docs/reports/runner-family-task-dir-live-run/fam)"`
- (guard) `d=docs/reports/runner-family-task-dir-live-run/fam; test "$(head -n 1 "$d/step-1/builder-L1.md")" = "<!-- role=builder level=L1 model=sonnet effort=low -->" && test "$(head -n 1 "$d/verifier-L1.md")" = "<!-- role=verifier level=L1 model=opus effort=medium -->" && tail -n 1 "$d/runs.jsonl" | jq -e '.role == "verifier" and .level == "L1" and .model == "opus" and .effort == "medium" and .backend == "claude"' >/dev/null && jq -e '.status == "completed" and .model == "opus"' "$d/verifier-L1.attempt.json" >/dev/null && test -z "$(find "$d" -maxdepth 1 -name 'builder-*.md')"`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/README.md -e docs/reports/runner-family-task-dir-live-run.md -e docs/reports/runner-family-task-dir-live-run/dry-run-base.txt -e docs/reports/runner-family-task-dir-live-run/dry-run-fixed.txt)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF docs/reports/runner-family-task-dir-live-run.md)"`
