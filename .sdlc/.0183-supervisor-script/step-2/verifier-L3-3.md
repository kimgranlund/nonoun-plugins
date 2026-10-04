<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- AC1 (selftest prints all 32 `ok:` labels and `supervisor selftest: PASS` last, main checkout's `.sdlc/supervisor` unchanged, no `./.sdlc/supervisor`): pass. Evidence:
  - Verbatim command in the built tree: rc=0 in 26.6 s at load about 25. A separate run printed the 32 `ok:` lines and `PASS`, and `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.sdlc/supervisor` does not exist before or after.
  - Red at base: in a throwaway worktree at `$SDLC_BASE_SHA` the same command gives rc=2 (`can't open file ... supervisor.py`). The biting conjunct there is `out=$(python3 ... selftest)`.
  - The selftest itself bites, shown on three mutated copies in a temp folder:
    - debounce control patch made a no-op: `FAIL: control: a copy without the debounce wakes a young message: the case passed on the patched copy`, rc=1;
    - `run_enabled` changed to return `True` in the source: `FAIL: dry-run: no call without --run: dry-run called the host: the stub was called 1 times`, rc=1;
    - `poll` holding `pending_ids` in a default argument: `FAIL: control: a copy that counts raw files is not idle: the case passed on the patched copy`, rc=1, so the call-time lookup rule is enforced.
  - Each of the 16 controls fails for its rule's reason, not a crash. I re-ran every case against its patched copy and printed the raw reason: all 16 start with the expected prefix (for example `a second watcher ran: exit 0, stderr ''` and `a bad limit was accepted: poll_seconds: exit 0`).
  - The selftest's argv, prompt, scrub list, limits, and `.gitignore` literals (`supervisor.py:964-979`, `1205-1238`) match `docs/ticket-stages/watcher-design.md:52-57`, `:63`, `:112`, `:119-129`.
- AC2 (`import messages`, `messages.wait_ready(`, `messages.mailbox(`, no forbidden `def`): pass. Evidence: verbatim command rc=0, with matches at `supervisor.py:141`, `:451`, `:323`. Red at base rc=1 (file missing). Fixture copies: with `def check(` appended rc=1; with the import line changed to `import messages as m` rc=1.
- AC3 (exactly one `if __name__ == '__main__':` line): pass. Evidence: verbatim command rc=0, the one line is `supervisor.py:1916`. Red at base rc=1; a fixture copy with a second guard line rc=1.
- AC4 (no `shell=True`, `os.system(`, `os.popen(`, or em dash): pass. Evidence: verbatim command rc=0; the grep finds no match. Red at base rc=1; fixture copies with `shell=True` and with an em dash each rc=1.
- AC5 (help metavar, the four `watch` options, `reset --receiver`): pass. Evidence: verbatim command rc=0. `--help` prints `usage: supervisor.py [-h] [--root DIR] {init,watch,status,reset,selftest} ...`, `watch --help` lists `--run`, `--once`, `--now TIMESTAMP`, `--driver PATH`, and `reset --help` lists `--receiver NAME`. Red at base rc=2; a copy with the metavar changed rc=1; a copy with `--now` renamed fails the option loop on `--now`.
- AC6 (both `check.sh` edits): pass. Evidence: verbatim command rc=0. The diff shows the header change and `python3 "$root/scripts/supervisor.py" selftest || fail=1` right after the `messages.py` line. Red at base rc=1, where `check.sh` exists without those lines.
- AC7 (guard, changed and untracked files): pass. Evidence: verbatim command rc=0. `git diff --name-only "$SDLC_BASE_SHA"` lists only the two step 1 docs and `check.sh`; the only untracked file is `plugins/sdlc-lite/scripts/supervisor.py`. It can go red: in the throwaway base worktree it was rc=0 clean, rc=1 with a stray untracked `stray.py`, and rc=1 with `messages.py` modified.

Neighbor checks run:
- `bash plugins/sdlc-lite/scripts/check.sh`: rc=0 in 735 s, including `messages selftest: PASS` and `supervisor selftest: PASS`. shellcheck is not installed, so that part printed `skip`.
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`: `messages selftest: PASS`.
- `python3 scripts/check-packaging.py`: `PASS`.
- `git diff --check` on `check.sh` and `bash -n`: both rc=0.
- `git grep` found no script that reads `check.sh` contents and no reference to `supervisor.py` outside `check.sh` and the design docs, so there is no other dependent to run.

Builder claims I checked in a throwaway repo (not criteria):
- Each refusal exits 1 with one `supervisor.py:` line: missing init, `--now` without `--once`, `reset` without `--receiver`. A missing subcommand exits 2.
- `status` prints `watcher: not running` and `status: none yet`, then `bob	waking	1	<stamp>	-` during a wake.
- `reset` during a running watcher prints `supervisor.py: a watcher is running; stop it first`; a second watcher prints `another watcher holds <lock path>`.
- TERM to the watcher ended the stub and its grandchild `sleep`, recorded `result: stopped`, and wrote `stopping: true`. I could not read that watcher's exit code directly; `case_lock` asserts exit 0 after TERM (`supervisor.py:1704`).
- A second `init` prints nothing, and `hosts.local.json` and `lock` are git-ignored.

Steelman pass: I drafted one fail reason and dropped it. Draft: `status` prints `-` for a null reason while the handoff's line format says `<reason>`. Rebuttal: the handoff gives no rendering for a null reason, the selftest pins the `-` output, and no criterion contradicts it. The rebuttal holds.

## Out of scope changes
None. The diff holds `check.sh` and the new `supervisor.py`, which the step calls for, plus the two step 1 docs the guard allows. `messages.py` is unchanged (`git diff --stat "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/messages.py` is empty). The `.sdlc/0183-supervisor-script/` entries are run records.

## For the next attempt
None
