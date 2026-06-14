---
date: 2026-04-27
coverage: canonical
peers:
  - pointer-validation.md
  - orphan-detection.md
  - ../standards/cross-tool-matrix.md
primary_sources:
  - https://agents.md — AGENTS.md canonical spec
  - https://github.com/anthropics/claude-code/issues/31005 — Claude Code AGENTS.md request (open Apr 2026)
  - https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/
  - https://cursor.com/docs/rules — Cursor rules format
  - https://docs.continue.dev/customize/deep-dives/rules
status: research-verified
---

# Audit pattern: entry-file coverage

> **The first audit pass.** Before checking pointers, freshness, or orphans, verify that the right entry files exist and are well-formed.

## What this pattern checks

| # | Check | Pass criterion |
| --- | --- | --- |
| 1 | `AGENTS.md` exists at repo root | Yes |
| 2 | `AGENTS.md` has a "Where to find things" section | Yes — non-trivial section listing doc subfolders |
| 3 | `AGENTS.md` has a "Memory primitives" section | Yes — points to ADRs, decisions, traces |
| 4 | `AGENTS.md` has a `_Last reviewed:_` line or YAML `date:` | Yes |
| 5 | If `CLAUDE.md` exists, it's a thin pointer (≤15 lines, references AGENTS.md) | Yes |
| 6 | If `.cursor/rules` or `.cursorrules` exists, it's a thin pointer | Yes |
| 7 | If `.windsurfrules` exists, it's a thin pointer | Yes |
| 8 | If `.aider.conf.yml`, `.continue/`, etc., exist — examined for drift | Yes |
| 9 | If `README.md` exists, it links to AGENTS.md (or AGENTS.md links from it) | Yes |
| 10 | No two entry files contain conflicting content (drift detection) | Yes |

## Files to enumerate

The following should be examined as candidate entry files for LLM coding agents:

| Path | Tool / convention | Reads AGENTS.md natively? |
| --- | --- | --- |
| `AGENTS.md` | The canonical multi-tool standard (AAIF/Linux Foundation, Aug 2025) | n/a |
| `CLAUDE.md` | Anthropic Claude Code | **No** (issue #31005) |
| `~/.claude/CLAUDE.md` | Claude Code user-global; `CLAUDE.local.md` for personal overrides | **No** |
| `.cursorrules` | Cursor (deprecated, still works) | Yes, also reads AGENTS.md |
| `.cursor/rules/*.mdc` | Cursor (current) | Yes, also reads AGENTS.md |
| `.windsurfrules`, `.windsurf/rules/` | Windsurf (Cognition since Dec 2025) | Yes |
| `.aider.conf.yml` + `CONVENTIONS.md` | Aider | Configurable (not auto) |
| `.continue/rules/*.md` | Continue.dev | **Not yet** (issue #6716) |
| `.github/copilot-instructions.md`, `.github/instructions/**/*.instructions.md` | GitHub Copilot | Yes (added 2025-08-28); also reads CLAUDE.md, GEMINI.md |
| `README.md` | Human + LLM landing | n/a |
| `CONTRIBUTING.md` | Contributor guide (often agent-relevant) | n/a |
| `GEMINI.md` | Google Gemini CLI / Jules | Yes — primary |
| `~/.codex/AGENTS.md`, `AGENTS.override.md` | OpenAI Codex (user-global, override) | Yes — primary |

> **Not in this matrix:** `HERMES.md` doesn't exist as a convention (NousResearch's Hermes Agent uses `~/.hermes/skills/`, not a project file). `GAS_TOWN.md` doesn't exist either (Gas Town is Steve Yegge's multi-agent orchestrator, not an agent). See `../standards/cross-tool-matrix.md`.

Some of these may not apply to a given repo; that's fine. The audit checks them and reports presence/absence.

## How to run the check (procedural)

```text
1. List files at repo root with names matching the entry-file table above.
2. For each found file:
   a. Get size, last-modified date.
   b. Read content.
   c. Classify: "fat" (>15 lines, looks like instructions) vs "thin" (≤15 lines, looks like a redirect).
   d. Extract any relative-path references (./docs/..., docs/...).
3. Determine canonical:
   a. If AGENTS.md exists and is fat → AGENTS.md is canonical.
   b. If AGENTS.md missing but CLAUDE.md is fat → recommend "promote CLAUDE.md → AGENTS.md".
   c. If multiple fat entry files exist → flag drift; recommend consolidation.
4. Verify thin-pointer expectation:
   a. For every entry file that is NOT canonical, check it is thin.
   b. If thin: pass.
   c. If fat: flag as drift risk.
5. For the canonical file, verify required sections:
   a. "Where to find things" / equivalent
   b. "Memory primitives" / equivalent
   c. Build / test / run commands
   d. Trust boundaries (optional but recommended)
   e. Date or "Last reviewed" line.
```

## Output shape (the gap-report row)

For each finding, emit a row like:

```markdown
- **MISSING — AGENTS.md** (severity: high)
  - The repo has no `AGENTS.md` at the root.
  - `CLAUDE.md` exists and is 240 lines, looks canonical.
  - **Recommendation:** rename `CLAUDE.md` → `AGENTS.md`, then create a thin `CLAUDE.md` redirecting to it.
  - **Recipe:** see `recipes/audit-existing-repo.md` step 4.

- **DRIFT — CLAUDE.md vs .cursorrules** (severity: medium)
  - Both files contain non-trivial instructions but differ.
  - `CLAUDE.md`: 180 lines, lists `pnpm` build commands.
  - `.cursorrules`: 95 lines, lists `npm` build commands. Probably stale.
  - **Recommendation:** consolidate into AGENTS.md; demote both to thin pointers.

- **NAKED ENTRY — AGENTS.md** (severity: medium)
  - `AGENTS.md` exists but has no "Where to find things" section.
  - Doc subfolders exist (`.agents/brain/adrs/`, `PLAN.md`) but are unreachable from the entry file.
  - **Recommendation:** add a "Where to find things" section listing the subfolders. See `standards/agents-md-spec.md`.
```

## Severity rubric

| Severity | Meaning | Examples |
| --- | --- | --- |
| **Critical** | Entry-file is missing entirely; no LLM agent can read this repo | No AGENTS.md AND no CLAUDE.md AND no README.md with instructions |
| **High** | Canonical entry-file missing; substantive content lives in a non-canonical file | No AGENTS.md, but fat CLAUDE.md exists |
| **Medium** | Canonical exists but is incomplete or has drift risk | Fat AGENTS.md + fat CLAUDE.md (drift); naked AGENTS.md (no pointers) |
| **Low** | Canonical and pointers correct, but missing dated metadata | AGENTS.md has no `_Last reviewed:_` line |

## Cross-references

- AGENTS.md spec details: `../standards/agents-md-spec.md`
- CLAUDE.md thin-pointer pattern: `../standards/claude-md-convention.md`
- Pointer validation (next audit pattern): `pointer-validation.md`
- Full audit recipe: `../recipes/audit-existing-repo.md`
