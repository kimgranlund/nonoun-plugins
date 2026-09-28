## Task goal
`plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest` gains a case where the payload is a JSON boolean true but the hook exits with a code other than 2 (for example 0 or 1); the probe must exit 1 with a reason naming the hook exit code. Removing the `hook_rc != 2` check (line ~223) must turn the selftest red.

## Step 1: Add selftest case (e) for a non-2 hook exit
level: L2
### Do
In `plugins/sdlc-lite/scripts/hook-live-probe.sh`, in the selftest block only:
- Add a stub mode `nodeny` to the heredoc stub claude. It behaves like `hook`, but runs the registered hook with `SDLC_HEADLESS` unset, for example `printf '%s' "$STUB_PAYLOAD" | env -u SDLC_HEADLESS -u SDLC_ROLE "$cmd" 2>/dev/null`. `block-background.sh` then exits 0 for the boolean-true payload, so the payload is good and the hook rc is not 2.
- Update the header comment listing `STUB_MODE` and the section comment "cases (a) to (d)" so both name case (e).
- After case (d), or before it, add `# (e)`: `probe nodeny "$good"`. Assert `$prc -eq 1`. Assert `grep -q "^verdict: FAIL: hook exit code 0, not 2" <<<"$pout"`.
- Do not touch cases (a) to (d), live mode, or the `elif [[ "$hook_rc" != "2" ]]` check.
- CLAUDE.md and `.claude/agents/sdlc-lite-author.md` only say "`--selftest` (offline)" and do not list cases, so leave them unchanged.
### Acceptance criteria
- `plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest` exits 0 and prints `hook live probe selftest: PASS`.
- `grep -q "(e)" plugins/sdlc-lite/scripts/hook-live-probe.sh` (red now: no case (e) exists).
- Mutation check: `t=$(mktemp -d) && cp -R plugins/sdlc-lite/scripts plugins/sdlc-lite/hooks "$t"/ && sed -i '' '/"\$hook_rc" != "2"/,+1d' "$t/scripts/hook-live-probe.sh" && ! bash "$t/scripts/hook-live-probe.sh" --selftest >/dev/null; rc=$?; rm -rf "$t"; exit $rc`. It is red now, because the mutated selftest still passes with exit 0, and it goes green once case (e) exists. The `sed -i ''` form is the BSD/macOS one this repo runs on.
- `plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest` output has no `temp dir left behind` line, and the run leaves no `hook-live-probe*` entries in a fresh `TMPDIR` (case (d) and the existing cleanup check still pass).
- `git diff HEAD -- plugins/sdlc-lite/scripts/hook-live-probe.sh` shows changes only above the `# Live mode.` banner (guard: live mode unchanged): `git diff -U0 HEAD -- plugins/sdlc-lite/scripts/hook-live-probe.sh | grep -E '^@@' | awk '{split($3,a,","); sub(/\+/,"",a[1]); if (a[1]+0 > 115) bad=1} END{exit bad}'`.
- `plugins/sdlc-lite/scripts/check.sh` exits 0.
