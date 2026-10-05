## Task goal
Model and effort choices are backed by recorded experiments, and a change to the model table cannot land without citing one.

## Step 5: Live run in a throwaway copy of the repository
level: L2
### Do
Depends on: steps 1 to 3. Record the run in `docs/reports/evals-live-run.md`, with no em dashes, in the shape of `docs/reports/role-result-schema-live-run.md`. No model call is needed.

Setup:
- Run `T=$(mktemp -d)`.
- Run `rsync -a --exclude .git --exclude .worktrees "$(git rev-parse --show-toplevel)/" "$T/repo/"`. This copies the working tree, including the steps' uncommitted changes.
- Run every arm from `$T/repo`.
- Never edit the real repository's `run.sh`, `models.json`, level-rubric, or `.sdlc/evals/`.

Record each arm's exact command and exit code:
1. Baseline: `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite` gives exit 0.
2. Negative control on a Claude row:
   - In the copy's `plugins/sdlc-lite/scripts/run.sh`, change `builder:L2` from `effort=low` to `effort=medium`.
   - In the copy's `plugins/sdlc-lite/skills/level-rubric/SKILL.md`, change the builder `| L2 | Opus low |` row to `Opus medium`, so the level-rubric guard stays green.
   - `check.py` gives exit 1, and its only FAIL line is the `FAIL evals: ... model table changed ...` line.
3. A reused eval is refused: `python3 plugins/sdlc-lite/scripts/evals.py lock --eval .sdlc/evals/0000-baseline.md` gives exit 1 with `is not later than`.
4. A new eval passes:
   - `python3 plugins/sdlc-lite/scripts/evals.py add live-probe --role builder --level L2 --model opus --effort medium --host claude --task-set evals-live-run --pass-rate 0/0 --cost-usd unknown --date "$(date +%F)" --evidence docs/reports/planner-l3-opus-2026-09-30.md --method "<text>" --result "<text>"` writes `.sdlc/evals/0001-live-probe.md`.
   - `evals.py lock --eval .sdlc/evals/0001-live-probe.md` gives exit 0.
   - `check.py` then gives exit 0.
5. Negative control on Codex: change scout L1's effort from `low` to `medium` in the copy's `models.json`. `check.py` gives exit 1 with `model table changed`.
6. Revert:
   - Run `rm -rf "$T"`.
   - In the real repository, `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json` gives exit 0.
   - `python3 plugins/sdlc-lite/scripts/evals.py check` still cites `.sdlc/evals/0000-baseline.md`.

An arm that cannot run is recorded as unverified, never replaced by a fixture.

The doc has these sections, holding the exact strings the criteria grep for:
- `## Environment`: the date (`2026-..-..`), the OS, `python3 --version`, the repository commit (`git rev-parse --short HEAD`), and a note that the copy includes this ticket's uncommitted changes.
- `## Commands`: the exact commands, including `evals.py add` and `evals.py lock`.
- `## Evidence`: for each arm, the exit code written as `exit 0` or `exit 1`, and the relevant output line (`model table changed`, `is not later than`).
- `## Limits`:
  - one machine
  - the hash covers parsed rows, not comments or layout
  - URLs are not fetched
  - a hand edit of `table_sha256` alone is not detected
  - only `check.py`, not the full `check.sh`, ran in the copy
### Acceptance criteria
- `f=docs/reports/evals-live-run.md && for s in "## Environment" "## Commands" "## Evidence" "## Limits" "check.py" "evals.py add" "evals.py lock" "model table changed" "is not later than" "exit 0" "exit 1" "models.json"; do grep -qF "$s" "$f" || exit 1; done`
- `grep -qE "2026-[0-9]{2}-[0-9]{2}" docs/reports/evals-live-run.md`
- `python3 -c 'import json,sys; d=json.load(open(".sdlc/evals/table-lock.json")); sys.exit(not (sorted(d) == ["eval", "previous_eval", "table_sha256"] and d["eval"] == ".sdlc/evals/0000-baseline.md" and d["previous_eval"] is None))'`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/evals.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/check.py -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/AGENTS.md -e docs/codex-role-execution.md -e docs/reports/evals-live-run.md | { ! grep -q .; }`
