<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Every fanout lane and gate log line names the fanout run that wrote it, so a line left by an earlier stopped run never reads as a new failure after a resume.

## Step 1: Run id on fanout lane and gate log lines, with a resume selftest
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
All changes go in `plugins/sdlc-lite/scripts/fanout.py`, plus the matching docs in `docs/maintenance/sdlc-internals.md` (the `scripts/fanout.py` entry) and, if it states the line or log format, `plugins/sdlc-lite/skills/fanout/SKILL.md`.

Why fanout mints its own id: `run_lifecycle.py` sets `SDLC_ATTEMPT_ID` only for a `run.sh` role process. A fanout run is never a role attempt. The roles its driver launches already record their own `attempt_id` in `*.attempt.json` and `runs.jsonl`, and that part stays untouched. Fanout must not reuse an inherited `SDLC_ATTEMPT_ID` either. When a builder or verifier runs `fanout.py selftest`, it inherits one id, so two fanout runs would then share the same id and a resumed run would be indistinguishable. This is the ticket's "separate identifier for fanout lines that have no role attempt."

1. In `cmd_run`, after preflight and only for a non-dry run, mint `ctx['run_id'] = 'fanout-' + uuid.uuid4().hex[:12]` on every invocation. Always mint it; never read it from `SDLC_ATTEMPT_ID`.
2. `say()` prints `[<run_id>] [<lane>] <id> <event>`. It also appends that same line, under the existing `PRINT` lock, to `<lanes-dir>/logs/fanout.log`. Open that file in append mode so earlier runs' lines survive a resume. Pass the run id to `say()` through `ctx` or the lane, whichever is cleaner.
3. Driver output (`logs/<lane>-<id>.log`) and each gate's output (`logs/gate-<lane>-<id>-<k>.log`) are written line by line as `[<run_id>] <line>`:
   - Use `subprocess.Popen` with `stdout=PIPE, stderr=STDOUT`, read binary lines, and write the prefix plus each line.
   - A final line without a trailing newline still gets the prefix.
   - Keep today's overwrite (`'wb'`) file mode and names. Per-attempt gate log files are T-0156's scope, not this step's.
   - Exit codes, the `stdin=DEVNULL`, cwd and env behavior stay as they are.
4. Export `FANOUT_RUN_ID=<run_id>` in the driver env and in the gate env (the gate env is `dict(ENV, FANOUT_RUN_ID=...)`).
5. `report.md` gains a line `` - Run: `<run_id>` `` in its header list.
6. Update the module docstring (the run section, and the selftest section for the new case), the `sdlc-internals.md` fanout entry, and the fanout skill where it describes lines or logs. Together they must state:
   - the `[<run_id>] ` prefix on printed lines and on lane and gate log lines;
   - the append-only `logs/fanout.log`;
   - `FANOUT_RUN_ID`;
   - why fanout mints its own id instead of `SDLC_ATTEMPT_ID`.
7. Fix any existing selftest assertion that the new printed line format breaks. Keep each assertion's intent.
8. Add selftest case 9, whose expect labels start with `resume case`. It mirrors the probe criterion below:
   - One lane `alpha=T-0001` and a driver that exits 3 on the first run.
   - Resume: `git worktree remove --force` on the integration and lane worktrees, `git branch -D` on the lane branch, then rerun with the same `--integration` (reused) and `--lanes-dir`. The driver now succeeds and writes a valid `filer-L1.md`.
   - `logs/fanout.log` holds the old `[A] [alpha] T-0001 driver failed rc=3` line and a new `[B] [alpha] T-0001 merged` line, with A != B, both matching `fanout-[0-9a-f]{12}`.
   - Every lane log line and every gate log line of the second run starts with `[B] `, and the driver saw `FANOUT_RUN_ID=B`.
   - Negative control: temporarily make the id constant, observe that the resume case fails, restore it, and record that red run in the builder result.

This step is also the gates green step: run every gate below and fix any red this step introduced.
### Acceptance criteria
- Resume probe (fails now because `logs/fanout.log` does not exist and `FANOUT_RUN_ID` is empty): `t=$(mktemp -d); r=$t/r; mkdir -p $r/.sdlc/a; printf -- '---\nid: T-0001\ntitle: "A"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\na\n' >$r/.sdlc/a/handoff.md; export GIT_AUTHOR_NAME=p GIT_AUTHOR_EMAIL=p@x.invalid GIT_COMMITTER_NAME=p GIT_COMMITTER_EMAIL=p@x.invalid; git -C $r init -qb main; git -C $r add -A; git -C $r -c commit.gpgsign=false commit -qm f; F=$PWD/plugins/sdlc-lite/scripts/fanout.py; d="if test -e $t/ok; then echo rid=\$FANOUT_RUN_ID; printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' >\"\$FANOUT_ROOT/\$FANOUT_SLUG/filer-L1.md\"; else exit 3; fi"; (cd $r && python3 $F run alpha=T-0001 --integration fanout/p --lanes-dir $t/l --driver "$d" --gate "echo gated" >$t/o1 2>&1); touch $t/ok; git -C $r worktree remove --force $t/l/integration; git -C $r worktree remove --force $t/l/alpha; git -C $r branch -qD fanout/p-alpha; (cd $r && python3 $F run alpha=T-0001 --integration fanout/p --lanes-dir $t/l --driver "$d" --gate "echo gated" >$t/o2 2>&1); L=$t/l/logs; A=$(sed -nE 's/^\[(fanout-[0-9a-f]{12})\] \[alpha\] T-0001 driver failed rc=3$/\1/p' $L/fanout.log); B=$(sed -nE 's/^\[(fanout-[0-9a-f]{12})\] \[alpha\] T-0001 merged$/\1/p' $L/fanout.log); test -n "$A" && test -n "$B" && test "$A" != "$B" && ! grep -vqE '^\[fanout-[0-9a-f]{12}\] ' $L/fanout.log && grep -qxF "[$B] rid=$B" $L/alpha-T-0001.log && ! grep -vqF "[$B] " $L/alpha-T-0001.log && grep -qxF "[$B] gated" $L/gate-alpha-T-0001-1.log && grep -qxF "[$B] [alpha] T-0001 merged" $t/o2 && grep -qF "$B" $t/l/report.md`
- `grep -qF "resume case" plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF "FANOUT_RUN_ID" plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF "logs/fanout.log" docs/maintenance/sdlc-internals.md`
- `grep -qF "FANOUT_RUN_ID" docs/maintenance/sdlc-internals.md`
- The builder result records the resume case's negative control: with a constant run id, `fanout.py selftest` failed on a `resume case` label; after the fix it passed.
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/fanout.py|docs/maintenance/sdlc-internals.md|plugins/sdlc-lite/skills/fanout/SKILL.md")"`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`

## Risks
- The ticket says to "use the existing `SDLC_ATTEMPT_ID`". This plan reads that as "role runs keep their lifecycle attempt id" and gives fanout lines their own minted id, because no fanout run is a role attempt and an inherited id would repeat across a resume. If the user wanted fanout to adopt an inherited `SDLC_ATTEMPT_ID`, the done condition cannot hold under a builder or verifier run.
- Prefixing every driver line changes the raw lane log format. T-0157's trace ingest has to strip the `[<run_id>] ` prefix. Nothing in the repo parses lane logs today.
- Lane and gate log files are still overwritten on a resume, which is T-0156's scope. Only `logs/fanout.log` keeps earlier runs' lines. If T-0156 lands first and renames or appends the gate logs, the probe's `gate-alpha-T-0001-1.log` path may need that ticket's new name.
- The probe needs local `git` and `python3`, and it writes only under a `mktemp` dir.
