---
id: T-0112
title: "Formatter rule is prompt-only: check.py proves only that the phrase..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0102
---

## Goal
Inside a builder run, a repo-wide formatter, `--fix` linter, or format script (including one reached through a project script such as `npm run format`) is stopped by code before it runs, so builder rule 6 no longer rests on the prompt alone.

## Intent
Literal ask: "Formatter rule is prompt-only: check.py proves only that the phrase is in builder.md, so a builder can still run a repo-wide formatter through a project script such as `npm run format`."
Deltas:
- No goal or done-condition (template placeholder): defaulted: the goal above; done = a code gate plus selftest fixtures that bite.
- Mechanism (hook, run.sh post-build diff check, or verifier prompt): gap: user did not pick; default: a PreToolUse(Bash) hook in the style of `hooks/block-pattern-kill.sh`, because command text is available before the write happens and the sibling T-0102 follow-up was solved the same way. A post-build diff check cannot tell step files from formatter collateral, and a verifier rule is prompt-only again.
- Which roles: defaulted: only `SDLC_ROLE=builder` (the only role with Edit/Write and the owner of rule 6); every other role and an interactive session pass unchanged.
- What counts as repo-wide: defaulted: (a) a project script whose name is a format/fix script (`npm|pnpm|yarn|bun run` or `make` with a target named format, fmt, prettier, lint:fix, lint-fix, fix, or starting with `format`/`fmt`) with no explicit file path arguments after it; (b) a known formatter or fixer run in write/fix mode with no file argument or with a directory or glob argument (`.`, `src/`, `**`): prettier `--write`/`-w`, eslint `--fix`, black, ruff `format` or `check --fix`, gofmt `-w`/`-l -w`, `go fmt ./...`, `cargo fmt`, rustfmt without files, biome `format --write`/`check --write`, `dprint fmt`, `stylelint --fix`, `clang-format -i` with a glob. Explicit file paths pass (`prettier --write a.ts b.ts`, `npm run format -- a.ts`).
- Parse safety: defaulted: follow block-pattern-kill.sh (masking, command position, fail closed on heredoc, shell/evaluator word, or parse failure).
Do: add `hooks/block-repo-format.sh`, register it in `hooks/hooks.json` under the Bash matcher, add fixtures to `scripts/hook-selftest.sh` (blocked forms, allowed explicit-path forms, and allowed with no role and with a non-builder role), make the block message name rule 6 and say to pass the changed paths explicitly, and update `agents/builder.md` rule 6 to mention the hook, the check.sh header, `CLAUDE.md` (Layout bullet and check.sh line), and `.claude/agents/sdlc-lite-author.md` so the records stay in sync. `scripts/check.sh` stays green.
Non-goals: resolving what a project script actually runs (reading package.json or Makefile bodies); blocking formatters for non-builder roles; a post-build diff audit; changing pattern-kill, publish, or worktree hooks.
Done when: `scripts/check.sh` exits 0; `hook-selftest.sh` shows the new hook denies `npm run format`, `pnpm format`-style `run` forms, `prettier --write .`, `eslint --fix src`, `cargo fmt`, `go fmt ./...` with `SDLC_ROLE=builder` (exit 2) and passes `prettier --write a.ts`, `npm run format -- a.ts`, `npm test`, and every blocked form with no role; with the hook body replaced by `exit 0` the selftest fails.

## Context
Follow-up from T-0102 (builder-scope-hygiene/filer-L1.md):

Formatter rule is prompt-only: check.py proves only that the phrase is in builder.md, so a builder can still run a repo-wide formatter through a project script such as `npm run format`.

## Constraints
Interactive sessions and non-builder roles are unaffected. Existing hooks and their selftests stay unchanged and green. No commit, push, or publish.
