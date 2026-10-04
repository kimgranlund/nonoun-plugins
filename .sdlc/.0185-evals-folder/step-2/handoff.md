## Task goal
Model and effort choices are backed by recorded experiments, and a change to the model table cannot land without citing one.

## Step 2: Add the .sdlc/evals folder: entry files, the baseline eval, the lock, and the router line
level: L2
### Read first
- `.sdlc/AGENTS.md`
### Do
Depends on: step 1. Run from the repository root. Change nothing outside `.sdlc/evals/` and `.sdlc/AGENTS.md`, and use no em dashes.

1. Write `.sdlc/evals/CLAUDE.md` as exactly `@AGENTS.md` and a newline.
2. Write `.sdlc/evals/AGENTS.md`. It must be self-contained, so a role that reads only this file can add, list, check, and lock (handoff Common rules: no skill is added). Its sections, in order:
   - `# Evals`, then one paragraph:
     - The folder holds dated records of model and effort experiments.
     - A change to a model or effort row in `plugins/sdlc-lite/scripts/run.sh` (the `case "$role:$level"` rows) or to `plugins/sdlc-lite/adapters/codex/models.json` lands only with a new eval and `evals.py lock`, else `python3 plugins/sdlc-lite/scripts/check.py` fails.
     - Model and effort defaults stay user decisions; an eval never changes one.
     - Run commands from the repository root.
   - `## File format`: the name rule, each FIELDS entry with its rule from step 1, what `all` means, the evidence forms, the `## Method` and `## Result` body, and one example eval.
   - `## Table lock`:
     - the three keys
     - the canonical text, spelled out as in step 1: the `role:level model effort` rows from the run.sh regex, sorted, one per line, then models.json as `json.dumps(..., sort_keys=True, separators=(',', ':'))` and a newline, hashed to sha256 hex
     - the rules that `evals.py check` and `check.py` enforce
   - `## Procedures`:
     - Add an eval: `python3 plugins/sdlc-lite/scripts/evals.py add ...` with every option.
     - List: `evals.py list`.
     - Check: `evals.py check`.
     - Hash: `evals.py hash`.
     - Change the model table: run the experiment, `evals.py add` it, change the row (a user decision), `evals.py lock --eval .sdlc/evals/<file>`, then run `check.py`.
     - Never edit `table-lock.json` by hand.
   - `## Limits`:
     - URLs are checked for form only.
     - A hand edit of `table_sha256` alone is not detected, so the lock is reviewed in the diff.
     - The date rule allows one table change per day per lock chain.
     - Eval numbers are not unique across parallel worktrees; `check` reports a duplicate after a merge.
3. Create the baseline:
   - The command:

     ```
     python3 plugins/sdlc-lite/scripts/evals.py add baseline --role all --level all --model all --effort all --host all --task-set pre-eval-baseline --pass-rate 0/0 --cost-usd unknown --date 2026-09-30 --evidence docs/validation/haiku-alias-2026-09-30.md --evidence docs/validation/planner-l3-opus-2026-09-30.md --evidence docs/validation/codex-account-models-2026-09-30.md --method "<method>" --result "<result>"
     ```

   - It writes `.sdlc/evals/0000-baseline.md`, because the folder holds no eval yet.
   - The date is the date of the three deciding records, so a later eval dated 2026-10-01 or after can replace it.
   - Method: no experiment was run. This record marks the model table, as it stood when evals.py landed, as the pre-eval baseline, decided by the three dated records cited as evidence.
   - Result, one line per record:
     - haiku-alias: the Claude scout runs the pinned `claude-haiku-4-5`, because the `haiku` alias ran Sonnet 5.5.
     - planner-l3-opus: Claude planner L3 moved from Fable xhigh to Opus xhigh.
     - codex-account-models: these are the Codex defaults in `models.json`, with `gpt-6.1-sol` as the verifier alternate.
   - Close the Result with this line: no pass rate or cost was measured, and every later table change cites a newer eval.
   - Afterwards edit only the body text, if anything, and rerun `evals.py check`.
4. Run `python3 plugins/sdlc-lite/scripts/evals.py lock --eval .sdlc/evals/0000-baseline.md`. It writes `.sdlc/evals/table-lock.json` with `previous_eval` null.
5. In `.sdlc/AGENTS.md`, append the lines below after the `<!-- sdlc-lite:managed:end -->` line, outside the generated block. Do not edit inside the block.

   ```

   ## Other records

   - Evals: `evals/` holds the dated model and effort experiments and `table-lock.json`; read `evals/AGENTS.md` before changing a model or effort row in `plugins/sdlc-lite/scripts/run.sh` or `plugins/sdlc-lite/adapters/codex/models.json`.
   ```

   The line goes outside the block, not into `tickets.py`'s `ROUTER_TEMPLATE`, for two reasons:
   - `tickets.py` keeps every byte outside the markers (its docstring, line 140). A temp-root probe showed that a line appended after the end marker survives `tickets.py roadmap`, and that `tickets.py check` stays ok.
   - The lock covers this repository's plugin table, so the line does not belong in the router that every consumer project gets.

The lock and the eval files must stay tracked, not git-ignored. `.gitignore` ignores only `.sdlc/dogfood/`, `.sdlc/runtime/`, and `.sdlc/messages/` under `.sdlc`.
### Acceptance criteria
- `test "$(cat .sdlc/evals/CLAUDE.md)" = '@AGENTS.md'`
- `for s in "## File format" "## Table lock" "## Procedures" "## Limits" "role:level model effort" "sort_keys" "table_sha256" "previous_eval" "evals.py add" "evals.py list" "evals.py check" "evals.py lock" "task_set" "pass_rate" "cost_usd" "evidence" "## Method" "## Result"; do grep -qF "$s" .sdlc/evals/AGENTS.md || exit 1; done`
- `python3 -c 'import sys, pathlib; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import evals; r = evals.validate_eval(pathlib.Path(".sdlc/evals/0000-baseline.md"), pathlib.Path(".")); print(r); sys.exit(r is not None)'`
- `f=.sdlc/evals/0000-baseline.md && grep -qx 'pass_rate: 0/0' "$f" && grep -qx 'cost_usd: unknown' "$f" && grep -qx 'date: 2026-09-30' "$f" && grep -qx 'host: all' "$f" && for e in haiku-alias-2026-09-30 planner-l3-opus-2026-09-30 codex-account-models-2026-09-30; do grep -q "^evidence: .*docs/validation/$e\.md" "$f" || exit 1; done`
- `python3 -c 'import json,sys; d=json.load(open(".sdlc/evals/table-lock.json")); sys.exit(not (sorted(d) == ["eval", "previous_eval", "table_sha256"] and d["eval"] == ".sdlc/evals/0000-baseline.md" and d["previous_eval"] is None))'`
- `test "$(python3 -c 'import json; print(json.load(open(".sdlc/evals/table-lock.json"))["table_sha256"])')" = "$(python3 -c 'import re,json,hashlib; r=open("plugins/sdlc-lite/scripts/run.sh").read(); rows=sorted("%s:%s %s %s" % m for m in re.findall(r"^\s*([\w-]+):(L\d)\)\s*model=([\w-]+);\s*effort=(\w+)", r, re.M)); j=json.dumps(json.load(open("plugins/sdlc-lite/adapters/codex/models.json")), sort_keys=True, separators=(",", ":")); print(hashlib.sha256(("".join(x + "\n" for x in rows) + j + "\n").encode()).hexdigest())')"`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- `python3 plugins/sdlc-lite/scripts/evals.py list | grep -q '^0000-baseline\.md'`
- `awk '/sdlc-lite:managed:end/{e=1; next} e && /evals\/AGENTS\.md/{f=1} END{exit !f}' .sdlc/AGENTS.md`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `for f in .sdlc/evals/table-lock.json .sdlc/evals/0000-baseline.md .sdlc/evals/AGENTS.md .sdlc/evals/CLAUDE.md; do ! git check-ignore -q "$f" || exit 1; done`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/evals.py -e plugins/sdlc-lite/scripts/check.sh | { ! grep -q .; }`
