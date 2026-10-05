# Evals live run

Recorded: 2026-10-04. Live run for ticket T-0185: a change to the model table (`run.sh` for Claude, `models.json` for Codex) fails `check.py` until a new, later eval is added and locked. No model call was made.

## Environment

- Date: 2026-10-04.
- Host OS: macOS 26.6.2, Darwin 25.6.0.
- `python3 --version`: `Python 3.9.6`.
- Repo commit: `433125d` (`git rev-parse --short HEAD`). The copy includes this ticket's uncommitted changes from steps 1 to 3 in the working tree.
- Throwaway copy: a `mktemp -d` directory under `/var/folders/.../T/`, outside this repository, removed at the end.

## Commands

Setup, then every arm from `$T/repo`:

```sh
T=$(mktemp -d)
rsync -a --exclude .git --exclude .worktrees "$(git rev-parse --show-toplevel)/" "$T/repo/"
cd "$T/repo"
```

Arm 1, baseline:

```sh
python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite
```

Arm 2, negative control on a Claude row (builder L2 effort low to medium, with the level-rubric row kept in step):

```sh
sed -i '' 's/^  builder:L2)       model=opus;   effort=low ;;/  builder:L2)       model=opus;   effort=medium ;;/' plugins/sdlc-lite/scripts/run.sh
sed -i '' 's/^| L2 | Opus low |/| L2 | Opus medium |/' plugins/sdlc-lite/skills/level-rubric/SKILL.md
python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite
```

Arm 3, a reused eval is refused:

```sh
python3 plugins/sdlc-lite/scripts/evals.py lock --eval .sdlc/evals/0000-baseline.md
```

Arm 4, a new eval passes:

```sh
python3 plugins/sdlc-lite/scripts/evals.py add live-probe --role builder --level L2 --model opus --effort medium --host claude --task-set evals-live-run --pass-rate 0/0 --cost-usd unknown --date "$(date +%F)" --evidence docs/reports/planner-l3-opus-2026-09-30.md --method "Live run probe: builder L2 effort raised in a throwaway copy." --result "No model call; records the table change for the evals guard."
python3 plugins/sdlc-lite/scripts/evals.py lock --eval .sdlc/evals/0001-live-probe.md
python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite
```

Arm 5, negative control on Codex (scout L1 effort low to medium in `models.json`):

```sh
sed -i '' 's/"scout": {"L1": \["gpt-5.6-terra", "low"\]}/"scout": {"L1": ["gpt-5.6-terra", "medium"]}/' plugins/sdlc-lite/adapters/codex/models.json
python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite
```

Arm 6, revert, from the real repository:

```sh
rm -rf "$T"
git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json
python3 plugins/sdlc-lite/scripts/evals.py check
```

## Evidence

| Arm | Command | Result |
|---|---|---|
| 1 | `check.py` | exit 0, `ok: 19 role levels, 9 agents checked` |
| 2 | `check.py` after the `run.sh` edit | exit 1, `FAIL evals: .sdlc/evals/table-lock.json: model table changed: sha256 713fc786... is not the locked ab3aa58b...; add an eval, then run evals.py lock --eval <file>`. The only other FAIL line is the summary `FAIL: 19 role levels, 9 agents checked`. |
| 3 | `evals.py lock --eval .sdlc/evals/0000-baseline.md` | exit 1, `evals.py: eval .sdlc/evals/0000-baseline.md date 2026-09-30 is not later than the cited eval .sdlc/evals/0000-baseline.md date 2026-09-30; a changed table needs a new eval` |
| 4 | `evals.py add live-probe ...` | exit 0, wrote `.sdlc/evals/0001-live-probe.md` |
| 4 | `evals.py lock --eval .sdlc/evals/0001-live-probe.md` | exit 0, `locked .sdlc/evals/0001-live-probe.md (table sha256 713fc786...)` |
| 4 | `check.py` | exit 0, `ok: 19 role levels, 9 agents checked` |
| 5 | `check.py` after the `models.json` edit | exit 1, `FAIL evals: .sdlc/evals/table-lock.json: model table changed: sha256 87a83e18... is not the locked 713fc786...` |
| 6 | `git diff --quiet "$SDLC_BASE_SHA" -- run.sh models.json` | exit 0 |
| 6 | `evals.py check` | exit 0, `evals check: ok (1 evals, lock cites .sdlc/evals/0000-baseline.md)` |

A first pass of the same arms redirected `check.py` output to a path that was an existing directory, so arms 1 and 4 reported a shell redirect error instead of the check's exit. All arms were rerun in a fresh copy; the table above is that rerun. Arms 2, 3, and 5 gave the same results in both passes.

## Limits

- One machine, one run.
- The hash covers parsed rows, not comments or layout, so a comment or whitespace edit in `run.sh` or `models.json` is not detected.
- URLs cited as evidence are not fetched.
- A hand edit of `table_sha256` alone in `table-lock.json` is not detected.
- Only `check.py`, not the full `check.sh`, ran in the copy.
