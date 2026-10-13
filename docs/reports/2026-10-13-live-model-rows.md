# Live Claude check: the model rows changed by T-0519 and T-0520, and `effort:` in the messenger and conductor front matter

Date: 2026-10-13. Ticket: T-0522. Plugin: this repository at commit `35fdddae` (`plugin.json` still reads 0.22.6; the rows are the ones T-0519 and T-0520 landed for 0.22.7), loaded with `--plugin-dir plugins/sdlc-lite`. Host: Claude Code 2.1.296, `claude -p`, a throwaway git project under `/tmp`, the parent session's `CLAUDE_*` and `SDLC_*` variables removed from the environment. The solo agent on T-0522 ran every command below and read the host's transcripts itself.

## How the model and effort were read

- Model: the `message.model` field of each assistant record in the host's transcript (`<projects>/<project>/<session>.jsonl`, and `<session>/subagents/agent-<id>.jsonl` for a sub-agent). The agent's own answer is a second, weaker source.
- Effort: the `effort` field of the same transcript records, and `$CLAUDE_EFFORT` as the agent's Bash tool saw it. Calibration: three sessions started with `--model haiku --effort low`, `high` and `max` reported `effort=low`, `effort=high` and `effort=max` in both places, so both signals follow the session's effort.
- Probe sent to every agent: [probe.txt](2026-10-13-live-model-rows/probe.txt). Every run with its session id, transcript model, transcript effort and cost: [session-starts.txt](2026-10-13-live-model-rows/session-starts.txt).

## Sub-agent rows

One driver session (`--model haiku --effort max`, so an inherited value would show as Haiku or `max`) spawned each agent type once with the Agent tool, passing only `subagent_type`, `description`, `prompt` and `run_in_background`. The driver's transcript shows no `model` or `effort` key on any spawn. Prompt: [driver-prompt.txt](2026-10-13-live-model-rows/driver-prompt.txt). Driver answer: [driver-output.txt](2026-10-13-live-model-rows/driver-output.txt). Transcript read: [transcript-models.txt](2026-10-13-live-model-rows/transcript-models.txt).

| Agent type | Table row | Transcript model | Transcript effort | Verdict |
|---|---|---|---|---|
| `sdlc-lite:planner-L1` | sonnet, high | `claude-sonnet-5-5` | high | verified |
| `sdlc-lite:planner-L3` | opus, high | `claude-opus-5-5` | high | verified |
| `sdlc-lite:architect-L1` | opus, xhigh | `claude-opus-5-5` | xhigh | verified |
| `sdlc-lite:plan-reviewer-L1` | fable, high | `claude-fable-5-1` | high | verified |
| `sdlc-lite:verifier-L1` | opus, low | `claude-opus-5-5` | low | verified |
| `sdlc-lite:verifier-L3` | fable, xhigh | `claude-fable-5-1` | xhigh | verified |
| `sdlc-lite:scout-L1` | sonnet, low | `claude-sonnet-5-5` | low | verified |
| `sdlc-lite:researcher-L1` | sonnet, high | `claude-sonnet-5-5` | high | verified |
| `sdlc-lite:filer-L1` | sonnet, low | `claude-sonnet-5-5` | low | verified |
| `sdlc-lite:ui-designer-L1` | opus, medium | `claude-opus-5-5` | medium | verified |
| `sdlc-lite:messenger` (sub-agent) | sonnet, low (front matter) | `claude-sonnet-5-5` | low | verified |

Each agent's own answer and its `$CLAUDE_EFFORT` matched the transcript. No row launched with the wrong model, so no bug is filed.

## Session agents (`--agent`)

Started with `claude -p --plugin-dir plugins/sdlc-lite --agent <name>` and the same probe.

| Start | Transcript model | Transcript effort |
|---|---|---|
| no agent, no flags (the user's default) | `claude-opus-5-5` | medium |
| no agent, `--setting-sources project` (no user settings) | `claude-opus-5-5` | medium |
| `--agent sdlc-lite:conductor` | `claude-opus-5-5` | medium |
| `--agent sdlc-lite:conductor --effort low` | `claude-opus-5-5` | low |
| `--agent sdlc-lite:conductor --model haiku` | `claude-haiku-5-5` | medium |
| `--agent sdlc-lite:conductor --setting-sources project` | `claude-opus-5-5` | medium |
| `--agent sdlc-lite:messenger` | `claude-sonnet-5-5` | medium |
| `--agent sdlc-lite:messenger --setting-sources project` | `claude-sonnet-5-5` | medium |
| project settings `sonnet`, `high`: no agent, `--setting-sources project` | `claude-sonnet-5-5` | high |
| project settings `sonnet`, `high`: `--agent sdlc-lite:conductor --setting-sources project` | `claude-opus-5-5` | high |
| project settings `sonnet`, `high`: `--agent sdlc-lite:messenger --setting-sources project` | `claude-sonnet-5-5` | high |

The last three rows ran with `.claude/settings.json` in the scratch project set to `{"model":"sonnet","effortLevel":"high"}`, so the default differs from the conductor's front matter on both fields.

| Front matter line | Verdict | Reason |
|---|---|---|
| messenger `model: sonnet`, started as a session agent | verified, honored | the session ran Sonnet while the default is Opus |
| messenger `effort: low`, started as a session agent | verified, ignored | the session ran at the default each time: medium with and without the user settings file, high under the project settings |
| messenger `effort: low`, spawned as a sub-agent | verified, honored | low under a driver at `max` (table above) |
| conductor `model: opus` | verified, honored | the session ran Opus when the project default was Sonnet |
| conductor `effort: medium` | verified, ignored | the session ran at high when the project default was high; its medium under the user's settings is that default, not the front matter |

A `--model` or `--effort` flag overrides the conductor front matter.

## What this does and does not show

- It shows that on this host and account every checked row, spawned by agent type alone, runs the model and effort the level table names, and that `fable` resolves to `claude-fable-5-1`, `opus` to `claude-opus-5-5` and `sonnet` to `claude-sonnet-5-5`.
- It shows `effort:` in agent front matter is honored for a sub-agent spawn and ignored for a session started with `--agent`. The messenger runs as a sub-agent, so its line takes effect. The conductor is a session agent: its `effort: medium` matches this account's default by coincidence, and with a default of high it ran at high. The session path was only tried with `claude -p --agent`; the `"agent"` key in `.claude/settings.json` was not tried.
- It shows `model:` in agent front matter is honored on both paths: the conductor ran Opus and the messenger Sonnet against a default of the other model.
- One run per row, one account, one host version. The probe did no role work: it shows what launches, not that a role performs well at its row.
- Not checked: planner L2, verifier L2, researcher L2 and L3, ui-designer L2, builder, solo and archaeologist rows (not in the ticket's list), the production path where `dispatch.py prepare` passes `model` to the spawn, and Codex (T-0316).
- Total cost of the check: 3.90 USD at list prices, as the host reported it.

## Follow-up for the maintainer

- The conductor's `effort: medium` front matter has no effect when the conductor is the session agent. Either drop the line, or document that the session effort comes from the user's setting or `--effort`. This is not a wrong-model launch, so it is noted here and not filed as a bug.
