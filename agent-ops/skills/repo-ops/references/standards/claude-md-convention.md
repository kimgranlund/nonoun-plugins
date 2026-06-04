---
date: 2026-04-27
coverage: canonical
peers:
  - agents-md-spec.md
  - cross-tool-matrix.md
primary_sources:
  - https://code.claude.com/docs/en/best-practices — Anthropic Claude Code best practices
  - https://github.com/anthropics/claude-code/issues/31005 — request to support AGENTS.md (Apr 2026: still open, no Anthropic response)
  - https://github.com/anthropics/claude-code/issues/6235 — parent issue (3,020 upvotes, 224 comments, 7 months open)
  - https://www.humanlayer.dev/blog/writing-a-good-claude-md
status: research-verified
---

# CLAUDE.md — thin pointer or symlink to AGENTS.md

> **The canonical pattern.** When `AGENTS.md` is present, `CLAUDE.md` should be either (a) a 3-5 line redirect, or (b) a symlink: `ln -s AGENTS.md CLAUDE.md`. The same pattern applies to `.cursor/rules/*.mdc`, `.windsurfrules`, `.github/copilot-instructions.md`.

## How Claude Code actually reads CLAUDE.md

Claude Code loads CLAUDE.md with this **precedence** (highest → lowest):

1. **Managed enterprise policy** (org-level)
2. **`~/.claude/CLAUDE.md`** (user global)
3. **`CLAUDE.md`** (project root)
4. **`CLAUDE.local.md`** (personal overrides, gitignored)

It also walks parent directories, supports `@import` syntax, and reads `.claude/rules/` for path-scoped rules.

## The load-bearing caveat — Claude Code does NOT read AGENTS.md natively

As of April 2026, **Claude Code does not natively read `AGENTS.md`**. The community has been requesting this since at least September 2025; [issue #31005](https://github.com/anthropics/claude-code/issues/31005) and the parent issue #6235 (3,020 upvotes, 224 comments, 7 months open) both have **zero Anthropic response**.

Two clean workarounds:

**Workaround A — Symlink** (minimal repo footprint):

```bash
ln -s AGENTS.md CLAUDE.md
git add CLAUDE.md
```

**Caveat:** symlinks across `.claude/skills/` ↔ `.agents/skills/` and similar directory pairs have known compatibility quirks; verify on the platforms you target. Windows + WSL contributors may also have issues with symlinks committed to git.

**Workaround B — Thin pointer file** (the safe default):

```markdown
# CLAUDE.md

This repo's instructions for LLM coding agents live in [`AGENTS.md`](./AGENTS.md).
Please read that file. The contents apply identically to Claude Code.

_Last reviewed: 2026-04-27_
```

Three to five lines. Same shape works for:

```text
# .cursor/rules/instructions.mdc
This repo's instructions live in AGENTS.md at the root. Please read it.
```

```text
# .windsurfrules
This repo's instructions live in AGENTS.md at the root. Please read it.
```

```text
# .github/copilot-instructions.md
This repo's instructions live in AGENTS.md at the root. Please read it.
```

(Note: GitHub Copilot already reads AGENTS.md natively, but a thin pointer here is harmless and helps consistency.)

## Anthropic's own guidance for CLAUDE.md

Per [Anthropic's Claude Code best practices](https://code.claude.com/docs/en/best-practices) and the widely-cited [HumanLayer post](https://www.humanlayer.dev/blog/writing-a-good-claude-md):

- **Keep CLAUDE.md under ~200 lines.** Instruction quality decreases as count increases.
- **Only universally-applicable instructions.** Path-specific rules belong in `.claude/rules/<path>/CLAUDE.md`.
- **Prefer hooks over advisory text** for deterministic behavior — hooks always execute; CLAUDE.md text is advisory.
- **Iterate by telling Claude to add corrections to CLAUDE.md itself.** Treat it as live, not frozen.

These guidelines port cleanly to AGENTS.md — same ergonomics regardless of filename.

## Anti-pattern: divergent CLAUDE.md and AGENTS.md

The most common stale-docs failure: CLAUDE.md was written first, then AGENTS.md added later, and now they have drifted. Different build commands. Different conventions. Different trust boundaries.

Audit signal:

- Both files exist
- Both are non-trivial in size (>15 lines each)
- A diff shows substantive content differences

Fix: pick one canonical (AGENTS.md), demote the other to a pointer or symlink.

## Migration recipe — turning a fat CLAUDE.md into a thin pointer

If you have a fat `CLAUDE.md` and no `AGENTS.md`:

1. **Copy** `CLAUDE.md` → `AGENTS.md` (`cp CLAUDE.md AGENTS.md`).
2. **Generalize the wording.** Replace "Claude Code" / "Claude" with "LLM coding agents (Claude Code, Codex, Devin, Cursor, Windsurf, etc.)".
3. **Add a `Where to find things` section** if missing.
4. **Trim AGENTS.md to under ~200 lines.** Push detail into `.brain/`.
5. **Replace `CLAUDE.md`** with either a symlink (`rm CLAUDE.md && ln -s AGENTS.md CLAUDE.md`) or a thin pointer file.
6. **Add `.cursor/rules/instructions.mdc`, `.windsurfrules`, `.github/copilot-instructions.md`** as thin pointers if those tools are used.
7. **Commit clearly:** `docs: split CLAUDE.md → AGENTS.md (canonical) + CLAUDE.md (pointer)`.

## Audit checks for CLAUDE.md

1. **If `AGENTS.md` exists**, `CLAUDE.md` should be either a symlink to it OR a thin pointer (≤15 lines). Anything else is drift.
2. **If `AGENTS.md` does not exist**, recommend creating one and demoting `CLAUDE.md` to a pointer.
3. **If both exist as fat files**, flag as drift risk — diff them and recommend consolidation.
4. **If `CLAUDE.md` references files that don't exist**, flag broken pointers.
5. **CLAUDE.md > 200 lines** — flag as a length smell. Anthropic's own guidance recommends shorter.

## Cross-references

- AGENTS.md spec: `agents-md-spec.md`
- Full cross-tool compatibility matrix: `cross-tool-matrix.md`
- LLM-doc-writing guidance (length, content quality): `../guidance/llm-doc-writing.md`
- Audit checks: `../audit-patterns/entry-file-coverage.md`
- Migration recipe in detail: `../recipes/audit-existing-repo.md`
