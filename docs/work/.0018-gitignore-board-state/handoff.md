---
id: T-0018
title: "Recommend ignoring .sdlc/.board-state.json"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1
priority: P2
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Projects that commit their .sdlc/ trail don't get a dirty tree from /board.

## Intent
- Do: in `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, next to the existing "Add `.sdlc/` to the project's `.gitignore`" sentence, add a fenced `.gitignore` block for projects that commit the `.sdlc/` trail: `.sdlc/.board-state.json`, `.sdlc/**/*.running`, `.sdlc/**/*.log`, each explained in one short line (board cache rewritten on every /board render; live-run marker; raw role transcript). Keep the results `.md` and `runs.jsonl` committed, matching this repo's own `.gitignore`.
- Non-goals: moving `.board-state.json` out of the tree (changes board.py and statusline behavior; left as a follow-up); editing this repo's own `.gitignore`; any script change.
- Done when: the skill shows the block; each pattern, checked with `git check-ignore` in a scratch repo that uses the block, ignores `.sdlc/.board-state.json`, `.sdlc/t/builder-L1.running`, `.sdlc/t/builder-L1.log` and does not ignore `.sdlc/t/builder-L1.md`, `.sdlc/t/runs.jsonl`, `.sdlc/t/handoff.md`; `plugins/sdlc-lite/scripts/check.sh` passes; `git diff --stat` lists only the skill file and this ticket folder.

## Context
Requested by the setup-sdlc-lite-generative-ui session. `board.py` rewrites `.sdlc/.board-state.json` on every render; in /Users/kimba/Projects/nonoun/gen-ui-system-svelte-lite that dirtied the tree and made a verifier fail a step's "git diff lists only docs" criterion. `skills/handoff-format` recommends ignoring all of `.sdlc/` but gives no lines for projects that commit the trail. Add recommended .gitignore lines there (at least `.sdlc/.board-state.json`, `*.running`, `*.log`), matching this repo's own .gitignore. Consider also moving the cache out of the tree.

## Constraints
No script, agent, or level-table change. No em dashes.
