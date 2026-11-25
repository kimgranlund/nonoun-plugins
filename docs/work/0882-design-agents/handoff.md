---
id: T-0882
title: "design: import the 11 designer agents from the MacBook"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The design plugin ships the 11 designer agents from the user's MacBook share, so Claude Code users of `design@nonoun` can call them as `design:<name>`.

## Intent
- Do: copy the 11 agent files unchanged into `plugins/design/agents/`, register them, pass packaging, and show Claude Code discovers them.
- Non-goals: Codex agents for design (no generator; say Claude Code only in the docs); editing the agents' text; the `massimo-ui` skill (the user chose to leave it out); any skill change.
- Done when: the criteria below hold.

## Context
- Source: `/Volumes/kimba/.claude/agents/*.md`, 11 files dated 2026-11-23: `dieter-rams`, `ive-newson`, `jan-tschichold`, `john-maeda`, `karl-gerstner`, `le-corbusier`, `max-bill`, `muller-brockmann`, `muriel-cooper`, `naoto-fukasawa`, `wim-crouwel`. Each has front matter `name`, `description`, `model: opus` and a body of about 110 lines (principles, method, craft standards). `/Volumes/kimba` is read-only: never write, touch or create anything under it. Copy with `cp /Volumes/kimba/.claude/agents/*.md plugins/design/agents/`.
- The user decided on 2026-11-24 to import all 11 into `design`, Claude Code only.
- Claude Code finds a plugin's agents in its `agents/` folder with no manifest field; `plugins/sdlc/agents/` is the working example (its `plugin.json` has no `agents` key). The design plugin has no `agents/` folder yet.
- Register: an `## Agents` section in `plugins/design/AGENTS.md` (one row per agent: name and one-line use from its description; say Claude Code only and that the source is the MacBook share), an `### Added` line under `## [Unreleased]` in `plugins/design/CHANGELOG.md`, and the design entry of any user-facing listing that enumerates what the plugin ships (root `README.md`, both `plugin.json` descriptions, both marketplace files) only if it already enumerates contents; keep the two hosts in parity.
- `scripts/check-packaging.py` may not know about design agents. If it flags them, report the exact output; change the packaging script only if a plain rule (for example a list of plugins allowed to ship `agents/`) needs the design plugin added, and keep that change minimal.
- Discovery proof: `claude plugin validate plugins/design` if the CLI has it, else `claude --plugin-dir plugins/design -p --max-turns 1 "List the subagent types you can launch whose name starts with design:, one per line, nothing else."` or the nearest working form; quote its output. If no host run is possible, say so and report the gap.

## Do
1. Copy the 11 files into `plugins/design/agents/`.
2. Register them in the guidance, changelog and any listing that enumerates contents.
3. Run packaging and the discovery proof.

## Acceptance criteria
- `ls plugins/design/agents/*.md | wc -l` prints 11, and `diff -rq /Volumes/kimba/.claude/agents plugins/design/agents` prints nothing.
- `grep -c -E 'dieter-rams|ive-newson|jan-tschichold|john-maeda|karl-gerstner|le-corbusier|max-bill|muller-brockmann|muriel-cooper|naoto-fukasawa|wim-crouwel' plugins/design/AGENTS.md` prints 11 or more, and `grep -q 'agents' plugins/design/CHANGELOG.md` exits 0.
- `python3 scripts/check-packaging.py` exits 0 and `git diff --check` is clean.
- The report quotes a host command's output that names the design agents, or states that none could run and why.

## Constraints
- Never write under `/Volumes/kimba`.
- Do not edit the agent files or any skill.
