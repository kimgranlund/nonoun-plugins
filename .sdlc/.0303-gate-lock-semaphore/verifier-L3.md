<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0 with real child processes (three holders on 2 slots, SIGKILL steal, SDLC_GATE_WORKERS, exit status, timeout 3): pass. Evidence:
  - Built tree: rc=0, stdout `gate_lock selftest: PASS` (3.9 s). The holders are real `subprocess.Popen` runs of the script wrapping `sh -c` (gate_lock.py:259-264, 327).
  - Each clause seen red with a one-line mutant copy under `$SDLC_TMP_WORKTREES/mut`, selftest rc=1 every time:
    - Cap widened in `slot_range` (gate_lock.py:89-90): `three holders with two slots: ['the third holder started at once with two slots held']`.
    - `holder_alive` forced True: `steal: the next run took the dead holder's slot, rc=3`.
    - SDLC_GATE_WORKERS export deleted: `workers: 2 slots gives 10, got '\n'`.
    - Exit status forced to 0: `exit status: exit 7 gives 7, got 0` and `kill -9 $$ gives 137, got 0`.
    - Timeout `return 3` changed to `return 4`: `timeout: exits 3 with one stderr line naming the holder, got rc=4`.
  - Live probes with a private TMPDIR:
    - `run -- sh -c 'echo W=$SDLC_GATE_WORKERS; exit 9'` printed `W=10` (20 cpus, 2 slots), rc=9.
    - `status` printed `slot 0  pid 69793  name probe-a  age 1s` while held, `no holders` after.
    - SIGINT gave rc=130 and SIGHUP rc=129; in both the child was dead and status read `no holders`.

- Negative control shown once (copy with the slot cap removed lets the third holder start at once, so the case fails): pass. Evidence:
  - The built selftest prints `gate_lock selftest: negative control observed (no slot cap): the third holder started at once with two slots held`.
  - Independent copy with the cap removed, running its own selftest: rc=1 on the three-holder case (line quoted above).
  - The control itself bites: with the cap line rewritten so the selftest's replace misses it, the selftest goes red, rc=1, `negative control: with the slot cap removed the three-holder case must fail, got []`.
  - The biting variable is the cap in `slot_range`. The `mutant_src != src` expect at gate_lock.py:312 can never fail, because the replace matches its own string literal at line 311. The `got []` assertion covers that gap.

- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, a case shows a `--gate` runs through gate_lock, and `--no-gate-lock` skips it: pass. Evidence:
  - Built tree: rc=0, `fanout selftest: PASS` (75 s). Cases 1 to 20 also run their gates through the wrapper, since the selftest strips `SDLC_GATE_*` and uses a private TMPDIR (fanout.py `gate_env`).
  - Mutants in a throwaway worktree at HEAD with the built files copied in:
    - Wrapper never applied (`if False:` in `gate_argv`): rc=1, only case 21 `on` and `slots3` fail, gate log `W=[] H=[]`.
    - `--no-gate-lock` ignored in `preflight`: rc=1, only case 21 `flag` fails. Its log shows the wrapped gate: `W=[10] H=[1]` and the slot file `{"pid": 61884, ..., "name": "alpha/T-0001", ...}`.
  - So both the env marker and the lock dir were observed, and the flag path is observed to skip them.
  - Dependent traced: `plan_check.py` builds its fanout parser from fanout.py's `ap.add_argument(` block (plan_check.py:152-163); `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` gives `PASS (46 checks)`.

- sdlc-internals.md and agents/conductor.md name `gate_lock.py run` for heavy gates; check.py and `codex_roles.py generate --check` exit 0: pass. Evidence:
  - conductor.md:48 reads `Heavy gates (npm test, browser shards, tsc) run through scripts/gate_lock.py run --name <what> -- <cmd>`.
  - sdlc-internals.md:71 (under `## scripts/gate_lock.py`, line 69) has `gate_lock.py run --name <lane>/<id> --` and `heavy gates (npm test, browser shards, tsc)`.
  - Red at base: `git show $SDLC_BASE_SHA:<file> | grep -c 'gate_lock.py run'` gives 0 for both files.
  - `python3 plugins/sdlc-lite/scripts/check.py`: `ok: 19 role levels, 9 agents checked`, rc=0.
  - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: `Codex agent definitions verified`, rc=0.
  - Both gates seen red in the throwaway worktree:
    - toml restored to base content: `generated agent drift: .../sdlc-conductor-l1.toml`, rc=2.
    - conductor.md without the phrase: `FAIL check.py: gate lock: conductor missing "gate_lock.py run"`.
    - check.sh without the selftest line: `FAIL check.py: gate lock: check.sh missing "gate_lock.py" selftest"`, rc=1.

No `builder-*.md` exists in the artifacts dir, so every result above is from my own runs. Tree state after verification matches the start: same `git status`, HEAD 33b76e3, tmp prefix empty, no leftover processes.

Steelman: draft fail "skills/fanout/SKILL.md argument-hint omits `--no-gate-lock`". Rebuttal: the handoff's docs requirement names only sdlc-internals.md and conductor.md, and the one code dependent that parses fanout flags (plan_check.py) reads them from fanout.py at run time and passes its selftest. Dropped.

## Out of scope changes
- `plugins/sdlc-lite/scripts/check.py` item 34 (a new gate-lock guard): the requirements asked only for the check.sh selftest line. Harmless by check: check.py is green on the built tree, each of its negative controls must fire for that (check.py:803-805), and two of its failure lines were observed red above.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`: in scope, since the handoff calls for regeneration when an agent body changes; `generate --check` is green on the built tree and rc=2 with the base toml.
- `.sdlc/0303-gate-lock-semaphore/base-sha` and `verifier-L3.attempt.json`: runner artifacts, not builder changes.
- Also run as neighbors: `git diff --check` rc=0, `bash -n plugins/sdlc-lite/scripts/check.sh` rc=0, `python3 scripts/check-packaging.py` PASS.

## For the next attempt
None
