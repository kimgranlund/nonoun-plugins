---
date: 2026-04-27
coverage: extended
peers:
  - ../standards/agents-md-spec.md
  - ../standards/claude-md-convention.md
primary_sources:
  - https://code.claude.com/docs/en/best-practices — Anthropic Claude Code best practices
  - https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/ — empirical study of 2,500+ AGENTS.md files
  - https://www.humanlayer.dev/blog/writing-a-good-claude-md
status: research-verified
---

# Writing AGENTS.md / CLAUDE.md content well

> **The empirical case for short, specific, navigable.** Not a style guide — a set of load-bearing constraints distilled from Anthropic's own best practices and GitHub's analysis of 2,500+ AGENTS.md files in the wild.

## Length

**Anthropic's own guidance for CLAUDE.md is "under ~200 lines."** The same ergonomic ceiling applies to AGENTS.md — instruction quality drops as count rises. Long files are skimmed, ignored, or contradicted by their own later sections.

If you have more than 200 lines of relevant content, push detail into linked subfolders (`ARCHITECTURE.md`, `.agents/brain/adrs/`, `.agents/brain/runbooks/`). The entry file should _navigate to_ depth, not _contain_ depth.

## What to include (per GitHub's 2,500-repo study)

The most-effective AGENTS.md files share these sections:

1. **Project overview** — one paragraph, what + who + why.
2. **Build / test / run commands** — exact shell commands, no prose. Wrong commands are worse than missing commands.
3. **Coding conventions** — short bullets. Style, types, formatting.
4. **Trust boundaries** — what to modify, what not to. Critical for preventing destructive edits.
5. **Where to find things** — pointers to subfolders. The skill's load-bearing recommendation.
6. **Memory primitives** — when to read ADRs, when to check post-mortems.

Sections that don't help LLM agents (move elsewhere):

- Long history / motivation / vision (move to `README.md` or `ARCHITECTURE.md`).
- Detailed architecture diagrams (move to `ARCHITECTURE.md`; reference from AGENTS.md).
- Personal preferences (move to `CLAUDE.local.md` or `~/.claude/CLAUDE.md`, gitignored).

## What to delete

Per Anthropic's best-practices doc and HumanLayer's writeup:

- **Delete instructions Claude already follows correctly without being told.** "Use TypeScript" in a TS-only repo is noise.
- **Delete instructions that contradict each other.** Diff your own AGENTS.md for self-contradictions.
- **Delete TODOs, comments, work-in-progress notes.** Use `.agents/brain/PLAN.md` instead.
- **Delete commands that fail.** A wrong `npm test` is worse than no `npm test`.

## Iteration pattern

Anthropic recommends treating AGENTS.md as **live, not frozen**: when the agent makes a mistake, ask it to add a correction to AGENTS.md itself. Over a few weeks the file converges on what's load-bearing.

Don't write AGENTS.md from scratch in one session — author the skeleton, then iterate by **deleting** as Claude proves it doesn't need a given line.

## Hooks > advisory text (where possible)

Per Anthropic: prefer **hooks** for deterministic behavior, not AGENTS.md text. A hook always executes; advisory text is suggestion.

Examples:

- "Run `pnpm typecheck` before committing" → write a `pre-commit` hook in `.husky/pre-commit`.
- "Don't edit `db/migrations/`" → enforce via CODEOWNERS or branch protection, not AGENTS.md prose.

AGENTS.md should explain _why_ and reference the hook; the hook does the work.

## The "agent persona + boundaries + commands" pattern

GitHub's empirical study found this three-part shape works well:

```markdown
# AGENTS.md

## You are
A senior Rust engineer working on a high-throughput web service.
Prioritize correctness over cleverness.

## Boundaries
- DO NOT: modify `migrations/`, generated code under `gen/`, `Cargo.lock`
- DO: write tests for every public function; run `cargo fmt` and `cargo clippy` before committing
- ASK: before changing anything in `crates/core/`

## Commands
build:  `cargo build --release`
test:   `cargo test --workspace`
lint:   `cargo clippy --all-targets -- -D warnings`
fmt:    `cargo fmt --all -- --check`
run:    `cargo run --bin server`

## Where to find things
- Architecture overview: `ARCHITECTURE.md`
- ADRs: `.agents/brain/adrs/`
- Postmortems: `.agents/brain/postmortems/`
- Runbooks: `.agents/brain/runbooks/`
- Active plan: `.agents/brain/PLAN.md`

_Last reviewed: 2026-04-27_
```

50-60 lines. Sufficient for most repos.

## Anti-patterns (what shows up in stale AGENTS.md / CLAUDE.md)

1. **The 800-line dump.** Nobody reads it; the agent doesn't either.
2. **The "we use TypeScript" file.** Noise — it's already in `tsconfig.json`.
3. **Stale build commands.** Repo migrated to pnpm a year ago; AGENTS.md still says `npm`. The audit catches this by comparing to the lockfile.
4. **The duplicated CLAUDE.md.** AGENTS.md and CLAUDE.md both fat, drifted apart.
5. **No "Where to find things."** Naked entry; agent has nothing to navigate to.
6. **Personal preferences in the committed file.** "I like 2-space indents" → move to `CLAUDE.local.md` (gitignored).
7. **TODOs that never got done.** "// TODO: document the auth flow" sitting in AGENTS.md for a year.

## Cross-references

- AGENTS.md spec: `../standards/agents-md-spec.md`
- CLAUDE.md as thin pointer / symlink: `../standards/claude-md-convention.md`
- Audit checks: `../audit-patterns/entry-file-coverage.md`
- Staleness detection tooling: `../audit-patterns/staleness-tooling.md`
