---
name: onboard
description: "Set up or check the entry files (AGENTS.md, CLAUDE.md) and the docs layout for a repository adopting SDLC Lite, keeping anything the repository already wrote. NOT for moving existing documents into the layout."
argument-hint: "[setup [--force] | check]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py:*)
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

Commands, all run from the repository root:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py setup --dry-run` prints a unified diff of every change and writes nothing.
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py setup [--force]` writes the same changes; `--force` also replaces a managed block edited by hand.
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py check` reports the state of each file as one `<label> <path>` line and writes nothing. Labels: `missing`, `malformed`, `newer`, `edited`, `current`, `stale`, `unmanaged`, and `present` for `docs/layout.md`. It exits 1 unless every entry file is `current` and `docs/layout.md` is `present`.

Workflow:
1. With `check` as the argument, run `onboard.py check`, report its lines and any stderr, and stop.
2. Otherwise run `onboard.py setup --dry-run` and show the diff and any stderr reports. An empty diff means nothing to change; say so and stop.
3. Ask the user once whether to apply it. Pass `--force` only when the user asks to replace an `edited` block.
4. On approval, run `onboard.py setup` and report its output.

Rules:
- The script writes every file. Write no file text yourself, and never hand-edit the managed blocks or `docs/layout.md` output to work around a report.
- On a parse error (exit 1 naming a file and line), report the file and line and stop. Do not retry or patch the file.
- Outside a Git work tree the script exits 1 and writes nothing; report the reason.
- The default homes include `goals/` and `kpi/`; setup lists them in `docs/AGENTS.md` and never creates either folder empty, and `docs_check.py` rules G-1 to G-5 check the files a repository puts there.
