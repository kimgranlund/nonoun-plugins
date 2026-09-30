<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/validation/entry-files-live-run.md`: new dated report for T-0162. It covers the environment, projects, method and commands, which runs came from which attempt at which plugin commit, the results table with 8 rows (all `yes`), and a limits section.
- `docs/README.md`: added the report's link line right after the onboard live run line.
- `docs/repo-onboarding/design.md`: linked the report from the "How roles reach an entry" section.
- Outside the repository: added the wrapper `/tmp/entry-probe.bh1AfI/run-role2`, which unsets every `SDLC_*` and `CLAUDE_CODE_*` variable and `CLAUDECODE`. Refreshed the Codex project agents and added `verifier-L3-2.*` to the Codex project's step-1 folder.

## Checks
- Reuse gate: `git diff --quiet "$(cat .sdlc/.../step-5.superseded-1/base-sha)" HEAD -- plugins/sdlc-lite/agents plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/adapters/codex/instructions.md` exited 0 (f20877a to 470f645), so reuse was allowed. Both projects still held the planner result, the step-1 and step-2 handoffs, and the builder log. The Claude project also held its verifier log.
- `codex --version` gave codex-cli 0.154.0. `claude --version` gave 2.1.285.
- In the Codex project, `codex_roles.py install --check .` exited 2 (13 agents missing or stale plus `.gitignore`). `install .` then installed 19 agents, and `install --check .` exited 0.
- `codex_roles.py resolve verifier L3 .sdlc/entry-probe/step-1` printed `gpt-6-astra high shared`.
- `PROBE_BACKEND=codex run-role2 verifier L3 .sdlc/entry-probe/step-1/handoff.md` (sets `SDLC_BACKEND=codex`) exited 0 and wrote `verifier-L3-2.md`:
  - Its header is `<!-- role=verifier level=L3 model=gpt-6-astra effort=high shared_with_builder=yes -->`.
  - It has a `## Verdict` section with value `pass`.
  - Its `runs.jsonl` line holds `"shared_with_builder":true`.
  - Its log shows `cat pkg/AGENTS.md` with the rule text in the output.
- I checked the evidence for all 8 arms directly in the handoffs and role logs:
  - Claude builder: a `Read` of `/tmp/entry-probe.bh1AfI/claude/pkg/AGENTS.md`.
  - Claude verifier: a Bash command `cat pkg/AGENTS.md; od -c ...`.
  - Codex builder: `pwd; cat pkg/AGENTS.md; ...`.
  - Codex verifier: as in the previous item.
  - Both step-1 handoffs list `pkg/AGENTS.md` under `### Read first`. Both step-2 handoffs give `grep -c 'Read first'` = 0.
- Acceptance criteria 1 to 8 each exited 0, including the 8-row loop in criterion 5.
- Criterion 9: the evidence column quotes a read of `pkg/AGENTS.md` by the builder and the verifier on each host (4 matches).
- Criterion 10: the report names `/tmp/entry-probe.bh1AfI/codex`. The result file's first line holds `model=gpt-6-astra` and `shared_with_builder=yes`, and the file has a `## Verdict` section. All checked with exit 0.
- Negative control for criterion 5: with the Codex verifier row changed to `no` in a temp copy, the loop exited 1.
- Final checks:
  - `git diff --check` exited 0.
  - The new file has no trailing whitespace.
  - The relative link in `design.md` resolves.

## Notes
- The limits section words the planner restatement per host, to match the logs. The Claude planner restated the `pkg` rule in the Do text. The Codex planner only spelled out the target line with the marker (`value: 2 ZEBRA-7`) and did not state the rule. Both are recorded, and the report still says the evidence is the read in the log, not rule compliance.
- The Codex project still has three untracked `sdlc-verifier-l*-alternate.toml` files from the first attempt's install, which `install .` did not remove. The Codex verifier noticed them, dated them before the build, and did not count them against the builder. The report records this.
- Codex event streams do not name the model. The report takes Codex models from the runner's result headers, `runs.jsonl`, and attempt records, and says so.
- Nothing is committed (not a merge step). The throwaway projects and logs stay in `/tmp/entry-probe.bh1AfI`, outside the repository.
