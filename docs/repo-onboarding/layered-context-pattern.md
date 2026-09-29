# Layered context pattern for agent harnesses

Status: reference, corrected 2026-09-29. Claims marked observed come from the [loading probe](../validation/nested-entry-file-loading.md). Claims marked unverified have not been tested in this repository.

## 1. Overview

The layered context pattern, also called progressive disclosure, keeps instructions close to the code they govern. A harness loads a small root contract first and picks up narrower rules only for the part of the tree being worked on. This saves tokens and keeps rules from drifting away from what they describe.

The pattern uses plain files and no symlinks.

```text
my-project/
├── AGENTS.md                      # Layer 1: root contract
├── CLAUDE.md                      # Claude Code notes + @AGENTS.md
├── .claude/
│   └── skills/
│       └── global-deploy/
│           └── SKILL.md
├── apps/
│   ├── backend/
│   │   ├── AGENTS.md              # Layer 2: domain scope
│   │   ├── CLAUDE.md              # local Claude notes + @AGENTS.md
│   │   ├── GEMINI.md              # Antigravity override (unverified)
│   │   └── src/
│   │       └── auth/
│   │           ├── AGENTS.md      # Layer 3: component scope
│   │           └── CLAUDE.md      # @AGENTS.md
│   └── frontend/
│       ├── AGENTS.md              # Layer 2: domain scope
│       ├── CLAUDE.md              # local Claude notes + @AGENTS.md
│       └── .claude/
│           └── skills/            # domain skills (unverified)
│               └── component-audit/
│                   └── SKILL.md
└── scripts/
    └── tools/
        └── shared_runner.py       # one runtime script
```

In this pattern every folder that has an `AGENTS.md` also has a `CLAUDE.md`. Without an import, Claude Code does not load a nested `AGENTS.md`.

## 2. How each harness resolves context

The harnesses do not resolve context the same way. Two of them were measured.

| Harness | What triggers loading | What is loaded | Status |
| --- | --- | --- | --- |
| Claude Code 2.1.284 | Reading a file | The `CLAUDE.md` in that file's folder and in each parent folder up to the root. A nested `AGENTS.md` loads only through an `@` import in a `CLAUDE.md` that is itself loaded. | Observed |
| Codex CLI 0.154.0 | The working directory at session start | Every `AGENTS.md` from the repository root down to the working directory. Reading a file in another folder loads nothing more. `CLAUDE.md` is not read. | Observed |
| Google Antigravity | `AGENTS.md` and `GEMINI.md` scanning | Not tested | Unverified |

Consequences:

- A Codex session started at the repository root sees only the root `AGENTS.md`, whatever files it later edits. To reach a nested entry it must be started in that folder or follow a link and read the file.
- How each harness settles a conflict between a nested rule and a root rule is unverified. Do not rely on a nested file overriding the root. Write nested rules so they narrow the root rules and never contradict them.

## 3. Rules per layer

### Layer 1: root contract

- `AGENTS.md` holds the stack, the directory layout, shared rules, and links to the Layer 2 entries.
- `CLAUDE.md` holds notes meant only for Claude Code and ends with the import.

```markdown
# Claude Code notes
- Use concise terminal output.
- Do not run continuous watch scripts.

@AGENTS.md
```

### Layer 2: domain scope

- `AGENTS.md` holds domain boundaries, language settings, test setup, and links to the Layer 3 entries.
- `CLAUDE.md` holds local Claude Code notes and the import.

```markdown
# Backend notes
- Build: npm run build --workspace=backend
- Test: npm run test --workspace=backend

@AGENTS.md
```

### Layer 3: component scope

- `AGENTS.md` holds implementation rules and edge cases for one component.
- `CLAUDE.md` holds the one-line import.

## 4. Linking between layers

Use `@` only to import the `AGENTS.md` in the same folder. Use an ordinary Markdown link to point at another layer.

```markdown
# apps/backend/AGENTS.md

For authentication changes, read [the auth rules](src/auth/AGENTS.md).
For database changes, read [the database rules](src/database/AGENTS.md).
```

Reasons, both observed in Claude Code:

- An `@` import is expanded as soon as the file holding it loads. A parent that imports its children with `@` pulls every child into context at once, which removes the benefit of layering.
- An `@` import written inside backticks is not evaluated at all.

A parent import such as `@../../AGENTS.md` is unnecessary. The root entry is already loaded when the session starts.

## 5. Skills as thin wrappers

Do not copy implementation logic into harness-specific wrappers. A skill states when it applies and which rules govern the work, then calls a shared script for the mechanical part.

```markdown
---
name: run-isolated-audit
description: Use when auditing local components for structural compliance.
allowed-tools: Bash(python3 ./scripts/tools/shared_runner.py:*)
---

1. Run `python3 ./scripts/tools/shared_runner.py --task audit --path <target_directory>`.
2. Report the script's output.
```

A skill that is pure guidance, with nothing mechanical to run, needs no script.

## 6. Maintenance

1. Avoid symlinks. Use the `@AGENTS.md` import in each `CLAUDE.md`. The claim that Antigravity rejects symlinks is unverified.
2. Keep skills at `.claude/skills/<name>/SKILL.md`. Whether Claude Code discovers skills in a nested `.claude/skills/` folder is unverified.
3. Keep entry files short. The original limit was 300 lines. The [onboarding design](design.md) proposes 60 lines for a root entry and 30 for a nested one. Move procedure into scripts.
4. Each nested entry costs tokens whenever it loads. In the probe, two 25-line entries added about 1,600 input tokens on Claude Code and about 1,800 on Codex, so roughly 800 to 900 per entry.

## Changes from the original text

- Removed the claim that Claude Code treats `@` imports of child folders as on-demand lookups. They load at once.
- Removed the claim that Codex resolves rules upward from the target file. It resolves from the root down to the working directory.
- Added a `CLAUDE.md` beside the Layer 3 `AGENTS.md`, which Claude Code needs.
- Marked the Antigravity, conflict handling, and nested skill claims as unverified.
- Replaced `allowed-tools: [bash]` with the form Claude Code skills use.
