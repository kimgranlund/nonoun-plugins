<!-- role=solo level=L1 model=sonnet effort=low -->
## Output
🟢 T-0509 is done: the recovery guidance and the Codex agent counts now match the code. L1, so no independent verifier ran. Nothing is committed.

**Changes**
- `plugins/sdlc-lite/agents/conductor.md`: the no-result sentence is corrected. `record` with no result exits 2 and leaves the attempt running, so it can be retried. `--no-result` closes it failed explicitly (exit 1), and a failed attempt can't be recorded again. This matches `dispatch.py`.
- `docs/references/codex-role-execution.md`: the count now reads 28 total / 24 base (4 alternates). `sdlc-solo-l1` through `sdlc-solo-l3` are listed. I counted 28 and 4 from the generated TOMLs in the `adapters/codex/agents` directory.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`: regenerated from the conductor prose, not hand-edited.

**Checks**
- `claude_roles.py generate --check` and `codex_roles.py generate --check` pass.
- `dispatch.py selftest` passes. It covers the no-result case, the failed-sub-agent case and the invalid-report case.
- `scripts/check-packaging.py` passes.
- `git diff --check` is clean.
- The two changed docs contain no changed links, so there was nothing to inspect there. The dated Astra review report is untouched.

**Open**
- I added no new dated validation report.
- `.sdlc/0509-operator-recovery-agent-inventory/skips.md` is an untracked file I didn't write. I left it alone.
- I didn't run the live-host checks.
