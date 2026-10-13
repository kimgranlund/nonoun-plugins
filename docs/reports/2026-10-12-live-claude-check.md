# Live Claude check: agent discovery, scout dispatch and the handoff freeze

Date: 2026-10-12. Closes the unverified live criteria of T-0503 (criterion 5) and T-0505 (criterion 6) for the Claude host. Plugin: the main checkout of this repository at the commit after the wave 54 merges (`--plugin-dir plugins/sdlc-lite`). Host: `claude -p --model sonnet --effort medium`, `SDLC_HANDOFF_EDIT_MODE=deny`, a throwaway git project in the session scratchpad. Prompt: [prompt.txt](2026-10-12-live-claude-check/prompt.txt). The session's own answer: [session-output.txt](2026-10-12-live-claude-check/session-output.txt). The run was one session driven by a Sonnet agent that reported its own results; I read them and did not rerun a step.

## Result

| Step | What was checked | Observed |
|---|---|---|
| 1 | agent discovery (T-0503 criterion 5) | the session listed 34 agent types starting `sdlc-lite:`; no YAML load error was reported |
| 2 | `dispatch.py prepare scout L1` | exit 0, dispatch JSON returned |
| 3 | handoff guard during a prepared attempt (T-0505 criterion 6) | an Edit of `handoff.md` was blocked with `handoff freeze: ... is being read by scout-L1`; `scout-L1.running` existed beside the handoff |
| 4 | one scout spawn with the printed `subagent_type`, `model`, `prompt` | `sdlc-lite:scout-L1` finished and named `README.md`, first line `# live` |
| 5 | `dispatch.py record` | exit 0; wrote `scout-L1.md` and a `runs.jsonl` line; removed `.running`; warned the run is unpriced (no `--transcript`) |
| 6 | the same edit after record | allowed; the freeze released |

## What this does and does not show

- It shows a fresh Claude session discovers the generated agents after the T-0503 YAML fix, completes one prepared scout dispatch and record, and that the T-0505 guard is active between prepare and record and released after.
- The scout's header read `model=claude-haiku-5-5`: the row was still the old one. Whether the `haiku` alias resolved to Haiku or Sonnet was not checked.
- One session on one project. It does not show that the agents failed to load before the fix (the old baseline was not run), so T-0503's claim about the old impact stays unverified.
- Step 6 ran the record and the edit in the same turn; the order is implied by the file listing, not by a timestamp.
- Codex was not exercised (T-0507 criterion 7 and T-0316 stay open).
