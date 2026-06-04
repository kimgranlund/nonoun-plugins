---
date: 2026-04-27
coverage: canonical
peers:
  - llm-doc-writing.md
  - ../audit-patterns/token-waste-detection.md
  - ../standards/agents-md-spec.md
primary_sources:
  - https://code.claude.com/docs/en/best-practices — Anthropic's CLAUDE.md guidance
  - https://docs.anthropic.com/en/docs/about-claude/models — Claude model context windows
  - https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/
status: research-verified
---

# Context budget (delivers Promise 2)

> **The premise.** Every token in AGENTS.md / CLAUDE.md / loaded docs is a token _not_ available for the actual code being worked on. "Token-and-context-optimized" means treating the agent's context window as a budget — and refusing to spend it on prose that could be a link.

## The math

Claude model context windows (April 2026):

| Model             | Context window            |
| ----------------- | ------------------------- |
| Claude Opus 4.7   | **1M tokens** (1,000,000) |
| Claude Sonnet 4.6 | 200K tokens               |
| Claude Haiku 4.5  | 200K tokens               |

That sounds like a lot. It isn't — once you load:

- AGENTS.md / CLAUDE.md (load every session — Anthropic loads CLAUDE.md automatically)
- The files the agent is editing (often 3-10 files, 200-2000 lines each)
- The files the agent is _reading_ to make decisions (10-50 files easily)
- Tool-call results (test output, lint errors, build logs)
- The conversation transcript itself (can grow to 30K+ tokens in long sessions)

A naked 800-line AGENTS.md costs **~10K tokens** — 5% of Sonnet's window, just for the entry file. If `ARCHITECTURE.md` is 1500 lines and gets loaded too, that's another 18K. Now you've spent 14% of the window on metadata before doing any work.

The Opus 4.7 1M window changes the math but not the principle. **Token economy is good engineering regardless of window size** — bigger window means tokens are cheaper, not free.

## Anthropic's load-bearing rule

> Keep CLAUDE.md under ~200 lines. Instruction quality decreases as count increases.
>
> — [Anthropic Claude Code best practices](https://code.claude.com/docs/en/best-practices)

The **same ergonomic ceiling applies to AGENTS.md.** This isn't an arbitrary number — it's where empirical observation says adherence drops. Long files are skimmed, ignored, or contradicted by their own later sections.

GitHub's [analysis of 2,500+ AGENTS.md files](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/) confirms this — the most-effective files cluster around 50-150 lines.

## Layered docs (the navigability principle)

The ceiling forces a structural choice: **detail goes into linked subfolders, not into the entry file**.

```text
AGENTS.md  (~150 lines: agent persona, build/test/run, conventions, trust
            boundaries, where-to-find-things, memory primitives)
   ↓ links to
ARCHITECTURE.md  (~500 lines: system overview, component map,
                  data-flow diagrams, deployment topology)
   ↓ links to
.brain/adrs/0001-*.md  (each ADR ~100 lines: one decision in depth)
.brain/postmortems/2026-04-*.md  (each ~150 lines: one incident)
.brain/runbooks/*.md  (each ~100 lines: one procedure)
```

The agent loads AGENTS.md every session (~150 lines, ~2K tokens). It loads ARCHITECTURE.md _only when needed_ (~7K tokens). It loads a specific ADR _only when about to make a related decision_ (~1K tokens).

**Total cost in the common case: 2K tokens. Total cost when deeply needed: ~10K tokens.** Compare to a flat 800-line AGENTS.md (10K every session, even when not relevant).

## The budget breakdown for a healthy repo

A target shape:

| Surface | Line ceiling | Token cost (approx) | When loaded |
| --- | --- | --- | --- |
| AGENTS.md | 200 | 2-3K | Every session |
| CLAUDE.md | 15 (thin pointer or symlink) | 0-200 | Every session (Claude Code) |
| README.md | 200-300 | 3-5K | Sometimes (human-facing) |
| ARCHITECTURE.md | 500 | 6-8K | When agent needs system overview |
| .brain/PLAN.md | 200 | 2-3K | When agent needs current priorities |
| `.brain/adrs/<one>.md` | 100-200 | 1-3K each | When agent makes architectural decisions |
| `.brain/postmortems/<one>.md` | 100-200 | 1-3K each | When agent debugs production issues |
| `.brain/runbooks/<one>.md` | 100-200 | 1-3K each | When agent runs operational procedures |
| `CHANGELOG.md` | (any) | varies | When agent needs version history |

The rule of thumb: **anything an agent needs _every session_ must be tiny; everything else can be large but must be reachable on demand**.

## What violates the budget (the trip-wires)

The token-waste-detection audit (Promise 2) flags these specifically:

1. **AGENTS.md or CLAUDE.md > 200 lines** — hard cap.
2. **AGENTS.md or CLAUDE.md > 150 lines** — warning (approaching cap).
3. **A `.brain/` file > 500 lines that isn't in `.brain/adrs/`, `.brain/postmortems/`, or `.brain/architecture/`** — likely a place where one big doc should be a folder of smaller ones.
4. **Repeated content** — the same command listed in AGENTS.md, README.md, AND CONTRIBUTING.md. Pick one canonical, link from the others.
5. **Verbose prose where bullets would work** — 8 paragraphs explaining what could be a 3-bullet checklist.
6. **Generated content checked in** — TypeDoc / JSDoc / API reference generated docs that should be regenerated, not committed.

## What does NOT violate the budget

- **Long ADRs** — an ADR should be as long as the decision warrants. Some are 30 lines; some are 300. Don't compress for compression's sake.
- **Long post-mortems** — same: an incident with a complex root cause needs depth.
- **CHANGELOG.md** — append-only history, expected to grow without bound. Agents rarely load all of it.
- **Long ARCHITECTURE.md** — within reason; if it gets >1500 lines, split into `.brain/architecture/`.

## How to reduce a bloated AGENTS.md (the recipe)

Bloated AGENTS.md is the most common failure. Recipe to compress:

1. **Strip "we use TypeScript" lines.** If `tsconfig.json` is present, the agent already knows.
2. **Strip personal preferences.** Move to `CLAUDE.local.md` (gitignored) or `~/.claude/CLAUDE.md` (user-global).
3. **Strip TODOs / WIP notes.** Move to `.brain/PLAN.md` and link.
4. **Strip long history / motivation.** Move to `README.md` or `ARCHITECTURE.md`.
5. **Compress prose to bullets.** "Run tests with Vitest, our preferred test runner" → "Tests: Vitest".
6. **Replace inline detail with a link.** "Our deployment uses Cloud Run with the following 14 steps..." → "Deployment: see `.brain/runbooks/deploy.md`".
7. **Audit for self-contradictions.** A file that contradicts itself is worse than incomplete.
8. **Re-read the file as if you were the agent.** Anything that doesn't change behavior gets cut.

A 600-line AGENTS.md typically reduces to 120-150 lines without losing instructional value.

## The Anthropic feedback loop applied to context budget

When AGENTS.md grows past 200 lines, two patterns work:

**Pattern A — extract to a linked file.** A "Conventions" section growing past 30 lines becomes `.brain/CONVENTIONS.md` linked from AGENTS.md. The link is permanent; the file can grow.

**Pattern B — ask Claude to compress.** "AGENTS.md is 280 lines. Compress to 180 while preserving all instructional content. Move detail to linked subfolders if needed." This is the inverse of the iterate-pattern: instead of _adding_ corrections, _delete_ what no longer earns its tokens.

Run pattern B quarterly. The audit can prompt this with a finding: `WARN: AGENTS.md is 240 lines. Run quarterly compression pass.`

## Cross-references

- LLM-doc-writing (companion guidance on content quality): `llm-doc-writing.md`
- Token-waste detection (the audit pattern that catches violations): `../audit-patterns/token-waste-detection.md`
- AGENTS.md spec: `../standards/agents-md-spec.md`
- Self-healing hooks (the pre-commit length check): `../recipes/self-healing-hooks.md`
