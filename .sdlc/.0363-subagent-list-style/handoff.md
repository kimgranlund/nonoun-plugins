---
id: T-0363
title: "Make spawn names, prompt first lines and descriptions follow the sub-agent list style guide"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A person reading the host's background agent list can tell sdlc-lite rows apart: names, prompt first lines and descriptions follow docs/references/subagent-list-style.md.

## Intent
- Do: change `dispatch.py agent_name` and the prompt built by `dispatch.py prepare` (and the equivalents in `solo_run.py` and `fanout.py`) per the guide: ticket id first in the name with the attempt suffix last, a one-line title (at most 50 characters) as the first prompt line, `Handoff: <path>` on line 2, description of 3 to 5 words. Keep `dispatch.py resume` finding agents by the new names, the spawn gate accepting the prompt, and old attempt files readable. Also fix the retro finding that `prepare verifier` prints the build commit as `Base sha` (record the pre-build sha in the solo dispatch file and have prepare read it) only if it is the same function; otherwise leave it.
- Non-goals: model or effort changes; the host's own columns.
- Done when:
  - A selftest prints names and first prompt lines for two attempts of two tickets and asserts the first 24 name characters differ and each first line is at most 50 characters (observed failing first).
  - hook-selftest.sh, dispatch, solo_run and fanout selftests, check.py, both generate --check pass.

## Context
User asked for a style guide on 2026-10-08 after seeing near-identical truncated rows in a maison session. The guide is committed; this ticket makes the scripts follow it. Changing the name format touches resume matching and the generated Codex text if any embeds names.

## Constraints
No em or en dashes. No push or publish.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and prints four `list row:` lines (two attempts of two tickets) whose first 24 name characters differ, whose first prompt lines are at most 50 characters and start with the ticket id, and whose line 2 is `Handoff: <path>`.
- The same selftest case fails on the pre-change `agent_name` (names began `builder-L3-0153-harness-cov`, so the first 24 characters matched across tickets).
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0: the spawn gate accepts `<ticket>-<role>-L<n>[-<k>]`, refuses the old `<role>-L<n>-<slug>` form and a wrong role or level, and `dispatch.py resume` finds an attempt by its new name.
- `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` and `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0; a solo or fanout dispatch has the title as line 1, `Handoff:` as line 2 and a 3 to 5 word description.
- `python3 plugins/sdlc-lite/scripts/check.py`, `codex_roles.py generate --check` and `claude_roles.py generate --check` exit 0.
- No em or en dash appears in the added lines of `git diff` (the count of added lines holding one is 0).
- The `Base sha` item is already met by T-0366 (`build_base` reads the solo dispatch file's `base_sha`), so it was left alone.

## Closed

2026-10-08: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
