## Task goal
A repository that adopts SDLC Lite gets entry files that route into `docs/` and explain `.sdlc/`, plus a stated docs layout, without losing anything it already wrote.

## Step 4: Live run on Claude Code and Codex
level: L3
### Do
Run the design's live run gate in throwaway Git repositories in a temp directory outside this repository. Never commit transcripts.

For each host:
1. Run `git init` to create a project.
2. In it, run `python3 <repo>/plugins/sdlc-lite/scripts/onboard.py setup`.
3. Start a session at the project root with tools disabled.
4. Ask it to quote the line that begins "Managed by SDLC Lite onboard" if that line is in its context, and to answer ABSENT otherwise.

Host settings:
- Claude Code: headless `claude -p` with tools disabled.
- Codex: `codex exec` with a read-only sandbox, running no command, and `-m gpt-6-astra`. The default models are rejected on this account (T-0163).

Negative control: the same project with the root managed block deleted from `AGENTS.md` must not report the line.

Record the results in a new dated report, `docs/reports/onboard-live-run.md`. Include the date, host versions, models, the exact commands and prompt, and one trial per arm. Add this table with one row per arm, writing "reported" or "not reported" for what was actually observed:

| Host | Arm | Result |
| --- | --- | --- |
| Claude Code | managed block present | reported |
| Claude Code | managed block deleted | not reported |
| Codex | managed block present | reported |
| Codex | managed block deleted | not reported |

If an arm does not match the expected result, record what was observed truthfully and report Status blocked. Link the report from the Evidence list in `docs/repo-onboarding/README.md`, and from `docs/README.md` next to the other onboarding validation entries.
### Acceptance criteria
- `f=docs/reports/onboard-live-run.md; for r in "| Claude Code | managed block present | reported |" "| Claude Code | managed block deleted | not reported |" "| Codex | managed block present | reported |" "| Codex | managed block deleted | not reported |"; do grep -qF "$r" "$f" || exit 1; done`
- `grep -qF "gpt-6-astra" docs/reports/onboard-live-run.md`
- `grep -qF "../validation/onboard-live-run.md" docs/repo-onboarding/README.md`
- `grep -qF "validation/onboard-live-run.md" docs/README.md`
