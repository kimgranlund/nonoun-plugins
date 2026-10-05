## Task goal
A role working on a plan step reads the entry files that govern the files it changes, on Claude Code and on Codex alike.

## Step 5: Live run on Claude Code and Codex
level: L3
### Do
Read `AGENTS.md` and `docs/codex-role-execution.md` first. Use `docs/reports/onboard-live-run.md` as the model for the report.

Build a throwaway git project in a temp folder outside this repository:
- a root `AGENTS.md`
- a `CLAUDE.md` holding `@AGENTS.md`
- `pkg/AGENTS.md`, holding one distinctive rule sentence
- `pkg/value.txt`
- a root `notes.txt`

Write a task handoff at `.sdlc/entry-probe/handoff.md` whose goal needs two steps: one that changes `pkg/value.txt` and one that changes only `notes.txt`.

For each host, run these from the project root with this repository's `plugins/sdlc-lite/scripts/run.sh`:
1. The planner.
2. `steps.py split` on the task dir.
3. The builder and then the verifier on the `pkg/value.txt` step.

Levels and models:
- Claude Code: the default backend, planner L2, builder L1, verifier L1.
- Codex: `SDLC_BACKEND=codex`, planner L3, builder L4, verifier L3. These levels map to `gpt-6-astra`, which this account accepts (T-0163). Install or point at the Codex agents as that guide says.

Run every role in the foreground with a Bash timeout of 600000 or more. Use a fresh project per host, or a fresh task dir per host.

For each host, confirm four things, and quote a short excerpt from the role log as evidence:
- The `pkg` step handoff lists `pkg/AGENTS.md` under `### Read first`.
- The builder log shows a read of `pkg/AGENTS.md`.
- The verifier log shows a read of `pkg/AGENTS.md`.
- The `notes.txt` step handoff has no `### Read first`.

Write `docs/reports/entry-files-live-run.md` with:
- the recorded date, 2026-09-29, and ticket T-0162
- the environment: host versions and the models taken from the logs
- the method and the exact commands
- a results table with the header `| Host | Arm | Result | Evidence |`
- one row per host and arm. Use the host labels `Claude Code` and `Codex`, the arm labels `handoff lists the entry`, `builder read the entry`, `verifier read the entry`, and `root-only step has no Read first`, and a Result of `yes` or `no`.
- a limits section

Record what actually happened. A `no` stays a `no`. If a host cannot run, Status is blocked with the evidence, and nothing is fabricated.

Add a link line for the report to `docs/README.md`, and link the report from the "How roles reach an entry" section of `docs/repo-onboarding/design.md`. Transcripts stay out of the repository.
### Acceptance criteria
- `test -f docs/reports/entry-files-live-run.md`
- `grep -qF 'validation/entry-files-live-run.md' docs/README.md`
- `grep -qF 'entry-files-live-run.md' docs/repo-onboarding/design.md`
- `grep -qF '| Host | Arm | Result | Evidence |' docs/reports/entry-files-live-run.md`
- `for h in "Claude Code" Codex; do for a in "handoff lists the entry" "builder read the entry" "verifier read the entry" "root-only step has no Read first"; do grep -qF "| $h | $a | yes |" docs/reports/entry-files-live-run.md || exit 1; done; done`
- `grep -qF 'gpt-6-astra' docs/reports/entry-files-live-run.md`
- The report's evidence column or sections quote log excerpts that show a read of `pkg/AGENTS.md` by the builder and by the verifier on each host.
