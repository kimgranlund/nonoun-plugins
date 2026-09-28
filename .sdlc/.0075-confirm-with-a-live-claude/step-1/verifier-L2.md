<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `test -x plugins/sdlc-lite/scripts/hook-live-probe.sh`: pass. Evidence: ran it, exit 0.
- Selftest prints `hook live probe selftest: PASS`: pass. Evidence: ran the command from the handoff, exit 0, output `hook live probe selftest: PASS`.
  - Bite check: in throwaway copies I removed the string-type check (M1), removed the cleanup (M4) and removed the timeout (M5). Each went red with the expected reason: `(b) string type: FAIL line does not name the type`, `temp dir left behind: <paths>`, and `(d) timeout: took 48s, want <= 20`.
  - The check also bites on `SDLC_HEADLESS=1` (M2). My own env already has `SDLC_HEADLESS=1`, so the first mutant run wrongly stayed green. Re-run with the ambient `SDLC_ROLE` and `SDLC_HEADLESS` unset, the original passed and the mutant failed with `(a) boolean true: exit 1, want 0`.
- `SDLC_PROBE_CLAUDE=/usr/bin/true ... --timeout 20; test $? -eq 1`: pass. Evidence: printed `verdict: FAIL: no Bash call captured`, exit 1. Case (c) of the selftest also asserts exit 1 with that reason.
- `grep -q "hook-live-probe.sh\" --selftest" check.sh`: pass. Evidence: exit 0. The line is `bash "$root/scripts/hook-live-probe.sh" --selftest || fail=1`, placed after the hook-selftest line, and the header comment was updated (git diff).
- `! grep hook-live-probe check.sh | grep -v "^#" | grep -qv -- --selftest`: pass. Evidence: exit 0. Every non-comment mention of the probe in check.sh carries `--selftest`.
- `grep -q hook-live-probe CLAUDE.md`: pass. Evidence: exit 0. The diff adds a Commands bullet (what it proves, one model call, `check.sh` runs only `--selftest`), extends the check.sh bullet, and adds a sentence to the `block-background.sh` Layout bullet.
- `grep -q hook-live-probe .claude/agents/sdlc-lite-author.md`: pass. Evidence: exit 0. The diff adds the probe to the check.sh list on line 24 and a sentence in the block-background hazard bullet.
- `shellcheck --severity=warning hook-live-probe.sh`: pass. Evidence: exit 0.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: I ran it, exit 0. It printed `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
- Script read (live mode and selftest): pass. Evidence from `hook-live-probe.sh`:
  - Live mode runs `env -u SDLC_ROLE SDLC_HEADLESS=1 "$claude" -p ... --settings "$tmp/settings.json"` (lines 191-193).
  - `--plugin-dir` appears only in a comment (line 16).
  - The settings file and capture wrapper live in the `mktemp -d` dir.
  - A python3 runner bounds the run with `p.wait(timeout=limit)` and kills the process group.
  - The cleanup trap covers EXIT, INT and TERM (lines 129-131).
  - Selftest cases (a) through (d) exist at lines 83, 91, 96 and 103 and assert exit 0, 1, 1 and 1.
  - Case (a) checks `verdict: PASS`, the heading, the `hook exit code: 2` line, and that the last line of the `--out` report is the verdict.
  - Case (b) checks that the FAIL line names `string`.
  - Case (d) allows up to 20s rather than "a few seconds", which the builder disclosed and explained; the stub sleeps 47s, so the bound still bites (M5 fails at 48s).
  - Leftover temp dirs are checked at lines 110-112, and M4 showed that check goes red.
- (guard) `hook-selftest.sh`: pass. Evidence: it printed `hook selftest: PASS`, and it also ran inside check.sh.

## Out of scope changes
- `.sdlc/0075-confirm-with-a-live-claude/handoff.md` has the Goal and Constraints filled in. The diff shows this is the conductor's clarification of the task, not a builder edit outside the step. Not out of scope.
- The step and task artifacts (`step-*/`, `planner-L2.md`, `runs.jsonl`) are untracked pipeline files. Not out of scope.
- Nothing else beyond the four files the step named (the probe, check.sh, CLAUDE.md, sdlc-lite-author.md).

## For the next attempt
None. A non-blocking gap: no selftest case makes the hook-exit-code-not-2 branch fail. Removing that check (M3) left the selftest green, but the handoff does not require a case for it.
