# Claude Code compatibility

Use the same v2 evidence contract and CLI engineering workflow. No Claude-specific shell is needed. The adapter is based on the supplied Claude parity report (versions 2.1.289–2.1.295), with synthetic regression fixtures; it has not been verified against an original Claude transcript in this project.

## Discover and hydrate

```sh
python3 scripts/discover.py --host claude --repo /project
python3 scripts/discover.py --host claude --repo /project --session-id UUID
python3 scripts/fog.py hydrate --host claude --trace /absolute/UUID.jsonl --repo /snapshot --out /output/session.json
python3 scripts/engineer.py diagnose --data /output/session.json
```

Invoke scripts by absolute path beneath the loaded skill. Discovery uses `~/.claude/projects/<cwd-with-slashes-replaced-by-dashes>/*.jsonl`; `--sessions` overrides the projects root. It scans JSON record envelopes to find identity/cwd and the latest user/assistant timestamp, not mtime. JSON parsing necessarily reads the record bytes, including message fields, but discovery does not return, analyze, or retain those bodies. It scans only this project's folder. Equal latest timestamps are ambiguous. A relocated session whose archive remains under a different project folder requires an explicit trace. Current Claude identity must come from an explicit transcript path or known session ID: `--current` never guesses latest. `discover.py --trace PATH` accepts a user-selected trace.

Hydration defaults to `--host auto`, sniffing up to 100 records for a Codex session_meta or Claude sessionId-bearing message/attachment. Ambiguous/unknown inputs require explicit host selection. Relative and absolute file paths map using each call's recorded cwd, so later results cannot accidentally remap a call after a worktree move. `--trace-root` explicitly overrides the mapping root. Current snapshot content is not substituted for missing historical output.

## Exposure and context

- Tools pair by `tool_use_id`, independently of order. Failed, unmatched, missing and duplicate results do not establish file returns. Calls and results remain separate timeline events.
- Structured text Read results establish full/partial returns from recorded line metadata. Edit/Write results establish mutations, not reads.
- Bash needs explicit `is_error: false`, returned text and a single conservative literal read for read exposure. Unknown success remains unknown; spilled/truncated output is partial and never opened from disk.
- Glob/Grep filename results are candidates. Numbered Grep content returns are partial. ToolSearch matches are tool candidates. Supported external URL returns remain partial.
- Injected skill text is a partial returned SKILL.md source plus explicit inclusion. It does not prove byte equality with the full skill file. sourceToolUseID links are recorded; adjacency never becomes attribution.
- nested_memory/file contents and instruction attachments support inclusion. Path-only instruction entries support inclusion by explicit attachment, without inventing returned file bytes. Display-only messages are inspectable but excluded from candidate/context extraction.
- Catalog attachments remain context events. Explicit added/removed string arrays support tool/agent catalog inclusion/removal. Other shapes, hook outputs, reminders, task lifecycle, user decisions and unknown MCP records remain inspectable without speculative exposure extraction.
- Compaction `preservedMessages.allUuids` is recorded as `messageRetention`, separate from source-level `contextRecords`. It does not prove that all historical file contents survived. Reasoning removals remain inspectable metadata; reasoning bytes are omitted.

Privacy defaults omit thinking/signatures, image/document bytes, credential_org, prompt snapshots, accounting/history records and known artifact-ledger fields. `--include-system-prompt` includes prompt snapshots intentionally. This is structural omission, not a general secret scanner: ordinary prose and tool output can still contain sensitive information.

## Child sessions

Agent results with an explicit agentId identify `<parent-trace-stem>/subagents/agent-ID.jsonl`. Only that bounded path is eligible; symlink escapes, unsafe IDs, cycles and depth beyond eight are rejected. `--no-children` disables loading. A parent `--through-line` cutoff omits child bodies because no equivalent child cutoff can be inferred. Missing children remain explicit unavailable links.

`childSessions` carries agentId, parent call event, result event, status and a separately hydrated report. No child exposure is copied into the parent. Parent result content remains the only observed returned content; child context is not presumed inherited. Named SendMessage and asynchronous notifications remain inspectable but are not automatically attributed without a verified identity mapping.

`fog.py render` emits child HTML/JSON alongside the parent and an `index-sessions.json` relationship manifest (or the chosen output stem). Each uses the existing shell. This release does not add a nested child-session canvas. `engineer.py diagnose` records separate child diagnoses inside the durable parent run and lists their counts. Compare child runs independently when investigating child behavior; aggregate parent success does not establish child correctness.

Run records carry host, adapter version and extraction warnings. Comparisons qualify changed host/adapter/coverage rather than interpreting different instrumentation as improvement. Legacy reports without host metadata are treated as Codex/legacy. Existing experiment, evidence verification, immutable storage and comparison commands work unchanged.

## Host selection

Moved from SKILL.md on 2026-10-16.

For Claude Code, read the Claude adapter (this file). Use `discover.py --host claude` and `fog.py hydrate --host claude` (or auto-detection for a selected trace). Explicit transcript paths and known session IDs take precedence. Claude has no assumed current-session environment variable. Keep child sessions and message retention separate from parent file exposures. Use the same CLI diagnosis/experiment/comparison workflow for either host.
