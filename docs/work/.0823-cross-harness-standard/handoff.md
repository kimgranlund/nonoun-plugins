---
id: T-0823
title: "Cross-harness plugin standard: a doc-standards card and a current compatibility reference"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-30
claimed_by: nonoun-author 2026-10-30
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Making a plugin surface work in both Claude Code and Codex is a first-class repo standard: the document-standards registry has a row and a card for plugin packaging (manifests, skills, agents, commands, hooks, MCP, scripts), and `docs/references/plugin-compatibility.md` describes the four plugins as they ship at 1.0.0.

## Context
- The user asked (2026-10-30) whether a cross-harness standard exists and chose "card + refresh".
- The rules already live in the shipped skill `plugins/dev-tools/skills/author-cross-harness-plugins/` (SKILL.md, `references/surface-matrix.md`, `behavioral-fidelity.md`, `evidence-contract.md`, `claude-code.md`, `codex.md`, `scripts/validate_cross_harness.py`) and are enforced for this repo by `scripts/check-packaging.py` (run in `check.sh`).
- `docs/references/plugin-compatibility.md` is dated 2026-09-27 and names SDLC 0.16.0 and two plugins; the repo now ships `sdlc` 1.0.0, `context`, `design` and `dev-tools` in marketplace `nonoun`.
- SDLC's own pattern: shared skills with a Codex adapter line; agents generated per host (`claude_roles.py`, `codex_roles.py`); Claude hooks in `adapters/claude/hooks.json`, none for Codex; two manifests with matching identity.
- Registry: `docs/specs/doc-standards/README.md`; cards follow `core.md`.

## Do
1. Add a card `docs/specs/doc-standards/plugins.md`: the standard for a plugin surface that ships to both hosts. Link the skill's references as the authority for the method (do not copy them), state this repo's layout rules (two manifests per plugin with matching identity, both marketplace catalogs in parity, shared skills with the Codex adapter line, generated per-host agents, Claude-only hooks outside Codex discovery, host-only gaps recorded), and name `scripts/check-packaging.py` and `validate_cross_harness.py` as the checks.
2. Add one registry row for it in `docs/specs/doc-standards/README.md` (Enforcement: enforced, Check: check-packaging.py), and list the card in `docs/specs/doc-standards/AGENTS.md` outside any managed block.
3. Rewrite the shipped-scope and maintenance parts of `docs/references/plugin-compatibility.md` for the four plugins at their current versions and the `nonoun` marketplace; move the 2026-09-27 validation evidence under a dated heading rather than deleting it.

## Acceptance criteria
- `test -f docs/specs/doc-standards/plugins.md && grep -q 'plugins.md' docs/specs/doc-standards/README.md`
- `grep -q 'check-packaging.py' docs/specs/doc-standards/plugins.md && grep -q 'author-cross-harness-plugins' docs/specs/doc-standards/plugins.md`
- `! grep -q 'SDLC 0.16.0' docs/references/plugin-compatibility.md || grep -q '^## .*2026-09-27' docs/references/plugin-compatibility.md`
- `python3 plugins/sdlc/scripts/docs_check.py --root .` reports 0 errors.
- `python3 scripts/check-packaging.py` exits 0.

## Outcome

2026-10-30 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: e3b7806d966e
- Changed: see commits
- Commits: 337b2fc T-0823: Cross-harness plugin standard; 6d305c3 T-0823: record lane T-0823-t0823
- Check: 1 card exists and README links it: pass
- Check: 2 card names check-packaging.py and author-cross-harness-plugins: pass
- Check: 3 no stale `SDLC 0.16.0` outside a dated 2026-09-27 section: pass
- Check: 4 docs_check 0 errors: pass
- Check: 5 check-packaging exits 0: pass
- Follow-up: note: docs/specs/doc-standards/plugins.md:27 and... -> notes.md
