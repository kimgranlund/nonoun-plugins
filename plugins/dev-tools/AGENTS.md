# Dev Tools maintenance

Read [repository guidance](../../AGENTS.md) first. This plugin ships skills for machine, repo and harness care. It has no hooks, subagents, model mapping or SDLC Lite dependency.

| Skill | Use | Source (2026-10-25) |
|---|---|---|
| `closed-loop-run` | Bounded verify, diagnose, repair and learn cycles | `~/.claude/skills/closed-loop-run` |
| `flaky-gates` | Decide whether a red gate is contention or a regression | `~/.claude/skills/flaky-gates` |
| `port-zombie-sweep` | Find dev servers that outlived their session | `~/.claude/skills/port-zombie-sweep` |
| `git-bare-repo-setup` | Bare clone with sibling worktrees: set up, operate, migrate | `~/.claude/skills/git-bare-repo-setup` |
| `macos-build-and-verify` | Build and visually verify the LG Controls Mac app (project-specific) | `/Volumes/kimba/.codex/skills/macos-build-and-verify` |
| `author-cross-harness-plugins` | One-source plugins for Claude Code and Codex | `~/.claude/skills/author-cross-harness-plugins` |
| `skill-report-card` | Evidence-backed skill performance report cards | `~/.codex/skills/skill-report-card` |

- `flaky-gates` and `port-zombie-sweep` name each other; keep both here.
- `closed-loop-run/references/ui-feedback.md` is referenced by name from the design plugin (`dev-tools:closed-loop-run`); keep its path.
- A link to a skill in another plugin is written by name (`context:context-fog-of-war` and the file path), never as a relative link.
- Keep each `SKILL.md` under the size limit in `scripts/check-packaging.py`; move whole sections into `references/` instead of trimming them.
- Do not ship `.DS_Store`, `__pycache__`, `node_modules` or dated evidence trees.

For any change, run `python3 scripts/check-packaging.py` from the repository root (identity, skill sizes, relative links) and `git diff --check`. Run a skill's own tests (for example `skill-report-card/scripts/test_*.py`) when its scripts change.
