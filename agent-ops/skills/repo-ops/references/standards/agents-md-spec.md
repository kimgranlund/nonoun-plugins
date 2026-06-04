---
date: 2026-04-27
coverage: canonical
peers:
  - claude-md-convention.md
  - cross-tool-matrix.md
primary_sources:
  - https://agents.md — canonical home of the spec
  - https://openai.com/index/agentic-ai-foundation/ — Agentic AI Foundation announcement (Dec 2025)
  - https://techcrunch.com/2025/12/09/openai-anthropic-and-block-join-new-linux-foundation-effort-to-standardize-the-ai-agent-era/
  - https://developers.openai.com/codex/guides/agents-md
  - https://docs.devin.ai/onboard-devin/agents-md
  - https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/
  - https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/
status: research-verified
---

# AGENTS.md — the canonical entry-file standard

## What AGENTS.md is

`AGENTS.md` is a Markdown file at the repo root that instructs an LLM coding agent on how to work in the repo. The format **emerged August 2025** out of a working group of OpenAI Codex, Amp (Sourcegraph), Jules (Google), Cursor, and Factory. As of **December 2025 it is stewarded by the Agentic AI Foundation (AAIF) under the Linux Foundation**, alongside Anthropic, OpenAI, Block, Google, Microsoft, AWS, Bloomberg, and Cloudflare. Adoption (as of April 2026) is **60,000+ open-source projects**.

Canonical home: [agents.md](https://agents.md).

## What the spec actually requires

**Almost nothing.** The spec is deliberately format-light — _"just standard Markdown, no required fields."_ Authority is governance (AAIF/Linux Foundation steward), not schema. Any sectioning convention (e.g., "Where to find things") is **opinionated overlay**, not spec compliance.

This skill recommends the structure below — but it is _our_ recommendation, layered on top of a deliberately permissive spec.

## Recommended structure (this skill's overlay)

````markdown
# AGENTS.md

This file gives instructions to LLM coding agents (Codex, Devin, Cursor,
Windsurf, Copilot, Aider, Continue, Jules, Junie — and Claude Code via
symlink/pointer) working in this repo.

_Last reviewed: 2026-04-27_

## Project overview

One paragraph: what this repo does, who uses it.

## Build / test / run

```bash
pnpm install
pnpm test
pnpm build
```

## Conventions

- TypeScript strict mode; ESM only
- Vitest for tests; Playwright for E2E
- Conventional Commits

## Trust boundaries

- DO NOT modify: `db/migrations/`, `legal/`, `LICENSE`
- DO modify: `src/`, `tests/`, `.brain/` (with care for ADRs)

## Where to find things

- **Architecture:** `ARCHITECTURE.md`
- **Active plan:** `.brain/PLAN.md`
- **Roadmap:** `.brain/ROADMAP.md`
- **Architecture Decision Records:** `.brain/adrs/` (see also `.brain/adrs/README.md` for the index)
- **Post-mortems:** `.brain/postmortems/`
- **Runbooks:** `.brain/runbooks/`
- **Released changes:** `CHANGELOG.md`
- **Contributor guide:** `CONTRIBUTING.md`

## Memory primitives

- **Before making architectural decisions**, read `.brain/adrs/` newest-first.
- **When debugging a production issue**, search `.brain/postmortems/`.

````

The "Where to find things" section is **load-bearing for navigation** even if not strictly required by the spec. Without it, the agent sees only `AGENTS.md` and has to guess where everything else lives.

## Adoption matrix (April 2026)

| Tool | Reads AGENTS.md natively? | Notes |
| --- | --- | --- |
| **OpenAI Codex** | **Yes** — primary | Plus `~/.codex/AGENTS.md`, `AGENTS.override.md` |
| **Cognition Devin** | **Yes** — primary | docs.devin.ai/onboard-devin/agents-md |
| **Cursor** | **Yes** | Plus `.cursor/rules/*.mdc` (newer) and `.cursorrules` (deprecated, still works) |
| **Windsurf** (Cognition-owned since Dec 2025) | **Yes** | Plus `.windsurfrules`, `.windsurf/rules/` |
| **GitHub Copilot** (coding agent + CLI) | **Yes** (added 2025-08-28) | Also reads `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` |
| **VS Code agent mode** | **Yes** |  |
| **Google Jules / Gemini CLI** | **Yes** |  |
| **JetBrains Junie** | **Yes** |  |
| **Sourcegraph Amp** | **Yes** | Founding member of the agents.md working group |
| **goose, Factory, Kilo, Antigravity, OpenClaw** | **Yes** | All listed on agents.md adopters page |
| **Aider** | Configurable via `--read CONVENTIONS.md` | Default is `CONVENTIONS.md`, AGENTS.md only via config |
| **Continue.dev** | **Not yet** | Issue #6716 open |
| **Claude Code** (Anthropic) | **NOT natively as of April 2026** | Issue [#31005](https://github.com/anthropics/claude-code/issues/31005) — workaround: symlink `ln -s AGENTS.md CLAUDE.md` or thin pointer file |

## Why AGENTS.md vs CLAUDE.md / .cursorrules / .windsurfrules

| Approach | Problem |
| --- | --- |
| `CLAUDE.md` only | Codex / Devin / Cursor / Windsurf / Copilot don't read it natively. Drift between tools. |
| `.cursorrules` only | Other tools don't read it. Same problem inverted. |
| One file per tool | N copies of the same content, guaranteed to drift over time. |
| **`AGENTS.md` + thin pointers/symlinks** | One source of truth; tool-specific files are 3-line redirects (or symlinks). |

## Audit checks for AGENTS.md

When auditing a repo:

1. **Existence** — does `AGENTS.md` exist at the repo root?
2. **Recommended sections present** — project overview, build/test/run, conventions, trust boundaries, where-to-find-things, memory primitives. (None are spec-mandated; all are recommended for navigability.)
3. **Pointer integrity** — does each `.brain/...` reference point to a real path?
4. **Freshness** — `_Last reviewed:_` line or YAML frontmatter `date:` present?
5. **Other entry files are thin pointers or symlinks** — if `CLAUDE.md` / `.cursorrules` / `.windsurfrules` exist, they should redirect to (or symlink to) `AGENTS.md`, not duplicate content. See `claude-md-convention.md`.
6. **Length** — under ~200 lines is the ergonomic target (per Anthropic's own CLAUDE.md guidance, which ports cleanly to AGENTS.md). Long instructions degrade adherence; push detail into `.brain/` subfolders.

## Common anti-patterns

- **Naked AGENTS.md** — just a project overview, no `Where to find things` section. Agent has nothing to navigate to.
- **Duplicate content** — AGENTS.md and CLAUDE.md both contain full instructions, drifted apart. Pick one canonical, make the others pointers/symlinks.
- **Stale build commands** — `npm install` listed but project moved to pnpm a year ago. Audit catches this by comparing to `package.json` / lockfiles.
- **No trust boundaries** — agent edits files it shouldn't (migrations, legal, generated code). Trust-boundary section prevents this.
- **No memory primitives section** — agent doesn't know to read ADRs before architectural decisions.
- **Bloated AGENTS.md** — 800-line instruction dump that nobody (human or agent) reads. Compress, link out.

## Cross-references

- CLAUDE.md as thin pointer / symlink: `claude-md-convention.md`
- Cross-tool compatibility matrix (full): `cross-tool-matrix.md`
- Audit checks: `../audit-patterns/entry-file-coverage.md`
- Greenfield setup recipe: `../recipes/greenfield-setup.md`
- LLM-doc-writing guidance: `../guidance/llm-doc-writing.md`
