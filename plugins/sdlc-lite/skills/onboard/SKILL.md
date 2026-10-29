---
name: onboard
description: "Set up or check the entry files (AGENTS.md, CLAUDE.md) and the docs layout for a repository adopting SDLC Lite, keeping anything the repository already wrote. NOT for moving existing documents into the layout."
argument-hint: "[setup [--init [--local]] [--force] | check]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py:*), Bash(git init:*)
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

## Arguments

| Argument | Meaning | Default | Example |
|---|---|---|---|
| `setup` | Refresh only: show the diff of every managed block the repository already holds, then write it on approval | the default | `setup` |
| `--init` | With `setup`: also create missing entry files and `docs/layout.md`, append a block to an unmanaged entry file, record `ticket_root: tickets` in `.sdlc/config` of a new repo (no ticket folder, config line or id ref yet), and declare `"agent": "sdlc-lite:conductor"` in `.claude/settings.json`. Only when the user asks to onboard the repository | off | `setup --init` |
| `--local` | With `setup --init`: declare the conductor agent in `.claude/settings.local.json` (personal, not committed) instead of `.claude/settings.json` (shared, committed) | off | `setup --init --local` |
| `--force` | With `setup`: also replace a managed block edited by hand | off | `setup --force` |
| `check` | Report the state of each managed file and write nothing. When an AGENTS.md names a `.agents/skills/<name>/SKILL.md` path yet no skill route resolves, it also prints `warning: AGENTS.md names <skill path> but no skill route resolves; see steps.py routes` on stderr; the exit code does not change | - | `check` |

Commands, all run from the repository root:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py setup --dry-run [--init [--local]]` prints a unified diff of every change and writes nothing.
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py setup [--init [--local]] [--force]` writes the same changes; `--force` also replaces a managed block edited by hand.
- With `--init`, setup adds `"agent": "sdlc-lite:conductor"` to `.claude/settings.json` (`--local`: `.claude/settings.local.json`) and keeps every other key. When either settings file already names an agent, it leaves it and prints `agent: kept <value> in <path>`; a malformed settings file is reported and left untouched. Under Codex (`SDLC_BACKEND=codex`), which has no session-agent setting, it writes no settings and prints one `agent:` line saying so.
- Without `--init`, setup refreshes the managed blocks that files already hold and changes nothing else. It prints one `--init would create <path>` or `--init would append a block to <path>` line on stderr for each file `--init` would add, and `--init would set agent in <path>` when the conductor declaration is missing.
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onboard.py check` reports the state of each file as one `<label> <path>` line and writes nothing. Labels: `missing`, `malformed`, `newer`, `edited`, `current`, `stale`, `unmanaged`, and `present` for `docs/layout.md`. It exits 1 unless every entry file is `current` and `docs/layout.md` is `present`. One more line reports the session-agent declaration: `current <path>` when the effective settings file (`.claude/settings.local.json` before `.claude/settings.json`) names `sdlc-lite:conductor`, `other <path>` when it names another agent, `malformed <path>` for unreadable JSON, and `missing .claude/settings.json` when neither file names one; this line never changes the exit code.

Workflow:
1. With `check` as the argument, run `onboard.py check`, report its lines and any stderr, and stop.
2. Otherwise run `onboard.py setup --dry-run` (add `--init` only when the user asked to onboard the repository) and show the diff and any stderr reports, the `--init would` lines included. An empty diff means nothing to change; say so and stop.
3. Ask the user once whether to apply it. Pass `--force` only when the user asks to replace an `edited` block.
4. On approval, run `onboard.py setup` with the same flags and report its output.

Not a Git work tree: when `onboard.py` exits 1 with `not a Git work tree`, it wrote nothing. Make one AskUserQuestion call (header `Not a repo`) with these options, each with a one-line consequence:
- `Run git init here (Recommended)`: creates a repository in this folder and onboards it.
- `Use another folder`: reruns onboarding from the folder you name.
- `Stop`: changes nothing.

On the first, run `git init`, then continue at step 2 with `--init` (the user asked to onboard). On the second, rerun from the folder the user names. On the third, stop. Never run `git init` unless the user chose it. With no AskUserQuestion (headless), ask the same question as numbered plain text.

Rules:
- The script writes every file. Write no file text yourself, and never hand-edit the managed blocks or `docs/layout.md` output to work around a report.
- On a parse error (exit 1 naming a file and line), report the file and line and stop. Do not retry or patch the file.
- The default homes include `goals/` and `kpi/`; setup lists them in `docs/AGENTS.md` and never creates either folder empty, and `docs_check.py` rules G-1 to G-5 check the files a repository puts there.
- The default homes include `designs/` for write-once grill designs. A `docs/layout.md` that lists its homes gains `designs/` only when the repository adds it under `## Homes` (and its `## Kinds` row, when the layout has that table); setup does not rewrite an existing `docs/layout.md`.

## Standing authorization: managed-block refresh

Maintainer decision 2026-10-09. A conductor may refresh stale managed blocks in its own repository without asking, under this rule and nothing broader:
1. Run `onboard.py check`, then `onboard.py setup --dry-run`.
2. If the diff touches only `<!-- sdlc-lite:managed:start -->` blocks inside `docs/**/AGENTS.md` and the CLAUDE.md pairs of those files, run `onboard.py setup --yes` and commit the result in that repository. This replaces the step 3 question.
3. Never run setup when the dry-run shows the root `AGENTS.md`, a template change, or a new managed file. Never pass `--init`, and never `--force` over a hand-edited block. Never run `tickets.py migrate-size --apply` under this rule. Never run it in another repository.
4. Otherwise report to the maintainer with the dry-run diff and stop.
