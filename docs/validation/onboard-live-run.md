# Onboard live run

Recorded: 2026-09-29. Live run gate from the [repository onboarding design](../repo-onboarding/design.md), ticket T-0160. One trial per arm.

## Environment

- Claude Code 2.1.285, headless `claude -p`, all tools disabled, model `claude-fable-5-1` (the default, read from the JSON result). User settings and plugins at their defaults.
- Codex CLI 0.154.0, headless `codex exec`, read-only sandbox, model `gpt-6-astra`. The default models are rejected on this account (T-0163).
- macOS, Darwin 25.6.0. Throwaway Git repositories in a temp directory outside this repository. Transcripts are not kept in this repository.

## Method

For each host:

1. `git init` in an empty folder.
2. `python3 <repo>/plugins/sdlc-lite/scripts/onboard.py setup`. It created `AGENTS.md`, `CLAUDE.md`, `docs/AGENTS.md`, `docs/CLAUDE.md`, and `docs/layout.md`. The root `AGENTS.md` managed block holds the visible line `Managed by SDLC Lite onboard, template 1.`
3. Present arm: a session at the project root with the prompt below.
4. Deleted arm: in the same project, the root managed block was deleted from `AGENTS.md`, start and end markers included, with `sed -i '' '/<!-- sdlc-lite:managed:start/,/<!-- sdlc-lite:managed:end -->/d' AGENTS.md`. A `grep -rn "Managed by" . --exclude-dir=.git` then found no match in the project. The same prompt was run again.

Prompt, identical for every arm:

```text
Do not run any command or read any file. If a line that begins with "Managed by SDLC Lite onboard" is in your context, quote that whole line exactly as it appears. Otherwise answer ABSENT. Answer with the quoted line or ABSENT only.
```

Commands, run from the project root:

```sh
claude -p "$(cat prompt.txt)" --tools "" --output-format json
codex exec -s read-only -m gpt-6-astra --json -o last-message.txt "$(cat prompt.txt)" < /dev/null
```

The prompt names only the start of the line, so an answer counts as reported only when it quotes the rest of the line, `, template 1.`, which appears nowhere in the prompt.

## Results

| Host | Arm | Result |
| --- | --- | --- |
| Claude Code | managed block present | reported |
| Claude Code | managed block deleted | not reported |
| Codex | managed block present | reported |
| Codex | managed block deleted | not reported |

Observed answers:

| Host | Arm | Answer |
| --- | --- | --- |
| Claude Code | managed block present | `Managed by SDLC Lite onboard, template 1.` |
| Claude Code | managed block deleted | `ABSENT` |
| Codex | managed block present | `Managed by SDLC Lite onboard, template 1.` |
| Codex | managed block deleted | `ABSENT` |

Each Claude Code session ended in one turn. Each Codex event stream held one agent message and no `command_execution` item, so Codex ran no command. Its other items were host notices about hook trust and shortened skill descriptions.

## Limits

- One trial per arm, on one machine and one account.
- The Claude Code arms were first run with a shorter prompt that lacked the opening sentence. Those runs gave the same answers. The Codex present arm was first run with stdin left open. It was repeated in a fresh project from the same setup with stdin closed, and gave the same answer. The recorded trials use the prompt and commands above.
- The run checks that the root managed block reaches the model at the project root. It does not check nested entry files or a role run.
