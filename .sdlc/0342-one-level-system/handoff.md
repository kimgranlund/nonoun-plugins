---
id: T-0342
title: "One level system: L1 to L5 everywhere; retire the S/M/L tier and size vocabularies (solo-S/M/L, ticket size S/M/L/XL)"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0325, T-0338]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
One level vocabulary across skills, agents, hooks, scripts, adapters and docs: L1 to L5 (L1 small, L2 medium, L3 large, L4 extra large, L5 reserved). The S/M/L tier and size vocabularies are retired, with read-compatible aliases so existing tickets and consumer repos stay valid.

## Intent
- Do (user decision 2026-10-07, "Both, with aliases"):
  1. Solo tiers: rename the solo agents solo-S/M/L to solo-L1/L2/L3 (S=L1, M=L2, L=L3) keeping each tier's model and effort exactly as today (a model or effort change is a user decision; this is a rename). Update `adapters/claude/levels.json`, `scripts/claude_roles.py` and the 22 generated definitions, `adapters/codex/models.json` and generated TOML, `hooks/block-role-spawn.sh` (allow solo-L1|L2|L3; keep accepting solo-S|M|L as deprecated aliases for one release so a cached 0.21.x conductor still spawns), `dispatch.py`, `solo_run.py` (`--tier` accepts L1|L2|L3 and S|M|L), `fanout.py` (prep and land), `run.sh` rows, `check.py` guards, selftests.
  2. Ticket size: `tickets.py` size values become L1, L2, L3, L4 (XL maps to L4; L5 reserved); the old S, M, L, XL are accepted on read as aliases and normalized on write; add `tickets.py migrate-size` (dry run by default) that rewrites front matter in this repo; lane rules reword to level terms (`steps.py lane`: level L1 and L2 go to solo, L3 and above to the chain, wording and output kept stable for callers; read the existing lane thresholds first and keep their behavior exactly).
  3. Scrub every skill, command, agent, reference and doc under plugins/ and docs/ (not dated reports under docs/reports, not closed ticket folders, not tag or release text) for the competing wording: 'tier S/M/L', 'size S/M/L/XL', 'size S and M', 'S|M|L', 'solo-S/M/L'; reword to L1 to L5, and where a skill talks about a ticket's size say 'ticket level (L1 to L5)'. Update docs/maintenance/sdlc-internals.md and the level rubric skill so one table defines the system.
  4. Add a `check.py` guard that fails when a plugin skill, agent or command file reintroduces the retired vocabulary (a regex list, with the deprecated-alias lines in the hook and tickets.py allowed by an explicit allowlist), with a planted-term negative control observed failing.
  5. Codex parity (user request 2026-10-07, "make sure this is updated for CODEX versions as well"): Codex already names its solo agents by level (`adapters/codex/agents/sdlc-solo-l1|l2|l3.toml`, `adapters/codex/models.json` solo L1 to L3), so the work is the mapping and wording that still speaks S/M/L: `scripts/codex_roles.py` (the S/M/L to level mapping and its generated TOML text), `adapters/codex/instructions.md` (the Codex prelude), the Codex adapter text in `skills/sdlc-lite/SKILL.md` and every skill's Codex host paragraph, `docs/codex-role-execution.md`, `scripts/codex-selftest.py`, and the `check.py` Codex parity guards. Ticket `size:` values and lane rules apply to Codex unchanged, since `steps.py lane` is host-neutral. Regenerate with `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` (generated TOML files are never hand-edited) and run `codex_roles.py generate --check` and `codex-selftest.py`; keep the managed-agent install ownership checks. The new `check.py` guard also scans the Codex adapter text and the generated TOML.
- Non-goals: any model or effort change; renaming roles; changing lane thresholds; rewriting closed tickets or dated reports; Codex behavior beyond the mapping rename.
- Done when:
  - `python3 plugins/sdlc-lite/scripts/check.py`, `tickets.py check`, `codex_roles.py generate --check`, `claude_roles.py generate --check` (or its equivalent), `docs_check.py`, `bash plugins/sdlc-lite/scripts/check.sh` pass, and dispatch, fanout, solo_run, tickets, steps and hook selftests pass with cases for both the new names and the old aliases.
  - Codex: `codex_roles.py generate --check` and `codex-selftest.py` pass; the generated Codex agents and the prelude contain no retired S/M/L tier wording; a live Codex run (`codex exec` in a throwaway project, solo L1 through the Codex adapter, per docs/codex-role-execution.md) is recorded as observed, or, if the Codex account or CLI cannot run it, listed as UNVERIFIED in the release record (never substituted by an offline fixture).
  - The new guard's negative control fails on a planted 'tier S' line (observed).
  - A live headless run in a throwaway project (no "claude" in the path, `claude -p --plugin-dir`) spawns one solo-L1 sub-agent through dispatch.py prepare, Agent and record (observed, record the transcript model field), and a second with the deprecated solo-S alias is still accepted.
  - `grep -rIE "tier (S|M|L)\b|size (S|M|L|XL)\b|solo-(S|M|L)\b" plugins/sdlc-lite/{agents,skills,commands}` returns only allowlisted alias lines.

## Context
Rework of 0.21.x naming: the user asked on 2026-10-06 for the l1-l3 system instead of s/m/l, but 0.21.0 shipped solo-S/M/L and ticket size S/M/L/XL, which compete with the L1 to L5 role levels. 334 tickets carry `size:` front matter; consumer repos too, so aliases are required. Depends on T-0325 (skills self-contained) and T-0338 (dispatch record) landing first because they edit the same skills and dispatch.py.

## Constraints
No em or en dashes. No push, tag or publish. Model and effort defaults unchanged. Do not edit or move runtime scripts while a lane or benchmark uses them: this ticket starts after T-0325 and T-0338 merge.
