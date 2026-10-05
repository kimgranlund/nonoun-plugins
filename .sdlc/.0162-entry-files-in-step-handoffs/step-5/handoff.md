## Task goal
A role working on a plan step reads the entry files that govern the files it changes, on Claude Code and on Codex alike.

## Step 5: Live run on Claude Code and Codex
level: L3
### Do
Read `AGENTS.md` and `docs/codex-role-execution.md` first. Use `docs/reports/onboard-live-run.md` as the model for the report.

This replaces the blocked first attempt, `.sdlc/0162-entry-files-in-step-handoffs/step-5.superseded-1/builder-L3.md`. That attempt got seven of the eight arms. The Codex verifier failed because it resolved to `gpt-6-sol`. T-0163 has since mapped every Codex level to `gpt-6-astra` in `plugins/sdlc-lite/adapters/codex/models.json` and left `verifier_alternates` empty. The Codex verifier now keeps the builder's model, and `run.sh` records `shared_with_builder=yes` in the verifier result header and `"shared_with_builder": true` in `runs.jsonl`.

Projects:
- Reuse the blocked attempt's throwaway projects, `/tmp/entry-probe.bh1AfI/claude` and `/tmp/entry-probe.bh1AfI/codex`, when they still hold its `.sdlc/entry-probe/` results: the planner result, the `step-1` and `step-2` handoffs, the step-1 builder log, and, in the Claude project, the step-1 verifier log.
- Reuse holds only while the role bodies the arms exercise are unchanged. Run `git diff --quiet "$(cat .sdlc/0162-entry-files-in-step-handoffs/step-5.superseded-1/base-sha)" HEAD -- plugins/sdlc-lite/agents plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/adapters/codex/instructions.md` in this repository. Exit 0 means reuse is allowed. Any other exit means every arm reruns in fresh projects.
- A host whose project or logs are missing gets a fresh throwaway git project in a temp folder outside this repository: a root `AGENTS.md`, a `CLAUDE.md` holding `@AGENTS.md`, `pkg/AGENTS.md` holding one distinctive rule sentence, `pkg/value.txt`, a root `notes.txt`, and a task handoff at `.sdlc/entry-probe/handoff.md` whose goal needs two steps: one that changes `pkg/value.txt` and one that changes only `notes.txt`.

Runs, for each host, from the project root with this repository's `plugins/sdlc-lite/scripts/run.sh`:
1. The planner.
2. `steps.py split` on the task dir.
3. The builder and then the verifier on the `pkg/value.txt` step.

In a reused project, run only the roles that have no result yet. In the reused Codex project, that is only the verifier.

Levels and models:
- Claude Code: the default backend, planner L2, builder L1, verifier L1.
- Codex: `SDLC_BACKEND=codex`, planner L3, builder L4, verifier L3. All three run on `gpt-6-astra`.
- Before any Codex role, run `python3 <this repo>/plugins/sdlc-lite/scripts/codex_roles.py install .` in the Codex project. The agents the blocked attempt installed there are stale, and `install --check` reports them.
- Before the Codex verifier, run `python3 <this repo>/plugins/sdlc-lite/scripts/codex_roles.py resolve verifier L3 .sdlc/entry-probe/step-1` from the project root. It must print `gpt-6-astra high shared`. If it prints anything else, or Codex rejects the model, stop with Status blocked and quote the output.
- The failed `gpt-6-sol` attempt record in the reused step-1 dir stays in place. The rerun writes a new attempt beside it.

Run each role through a wrapper that unsets the parent run's `SDLC_*` and `CLAUDE_CODE_*` session variables, as `/tmp/entry-probe.bh1AfI/run-role` does. That way a nested run never inherits this step's base sha, attempt id, or temp-worktree prefix. Run every role in the foreground with a Bash timeout of 600000 or more.

For each host, confirm the four things below. Check them in the handoffs and role logs themselves, not in the superseded builder report, and quote a short log excerpt as evidence for each:
- The `pkg` step handoff lists `pkg/AGENTS.md` under `### Read first`.
- The builder log shows a read of `pkg/AGENTS.md`.
- The verifier log shows a read of `pkg/AGENTS.md`.
- The `notes.txt` step handoff has no `### Read first`.

Write `docs/reports/entry-files-live-run.md` with:
- the recorded date, 2026-09-29, and ticket T-0162
- the environment: host versions, the models taken from the logs, and the Codex verifier's `shared_with_builder=yes` header
- the method and the exact commands
- the throwaway project paths
- which runs came from the blocked attempt and which ran in this attempt, with the plugin commit each ran at
- a results table with the header `| Host | Arm | Result | Evidence |`
- one row per host and arm. Use the host labels `Claude Code` and `Codex`, the arm labels `handoff lists the entry`, `builder read the entry`, `verifier read the entry`, and `root-only step has no Read first`, and a Result of `yes` or `no`.
- a limits section that states at least these:
  - One trial ran per arm.
  - The Codex verifier shared the builder's model, so that verification was not model-independent.
  - The planners also restated the `pkg` rule in the step's Do text. The evidence for the mechanism is therefore the read in the log, not rule compliance.

Record what actually happened. A `no` stays a `no`. If a host cannot run, Status is blocked with the evidence, and nothing is fabricated.

Add a link line for the report to `docs/README.md`, next to the onboard live run line. Link the report from the "How roles reach an entry" section of `docs/repo-onboarding/design.md`. Transcripts and role logs stay out of the repository.
### Acceptance criteria
- `test -f docs/reports/entry-files-live-run.md`
- `grep -qF 'validation/entry-files-live-run.md' docs/README.md`
- `grep -qF 'entry-files-live-run.md' docs/repo-onboarding/design.md`
- `grep -qF '| Host | Arm | Result | Evidence |' docs/reports/entry-files-live-run.md`
- `for h in "Claude Code" Codex; do for a in "handoff lists the entry" "builder read the entry" "verifier read the entry" "root-only step has no Read first"; do grep -qF "| $h | $a | yes |" docs/reports/entry-files-live-run.md || exit 1; done; done`
- `grep -qF 'gpt-6-astra' docs/reports/entry-files-live-run.md`
- `grep -qF 'shared_with_builder' docs/reports/entry-files-live-run.md`
- `grep -qF 'T-0162' docs/reports/entry-files-live-run.md`
- The report's evidence column or sections quote log excerpts that show a read of pkg/AGENTS.md by the builder and by the verifier on each host.
- The report names the throwaway Codex project path. The Codex verifier result file in that project's .sdlc/entry-probe/step-1 folder has a Verdict section, and its first line is a header holding model=gpt-6-astra and shared_with_builder=yes.
