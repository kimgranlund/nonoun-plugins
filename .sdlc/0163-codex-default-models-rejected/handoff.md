---
id: T-0163
title: "Codex rejects gpt-6-sol and gpt-6-luna on a ChatGPT account"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
It is known whether SDLC Lite's Codex defaults work on a ChatGPT account, and a role launched at a default level either runs or fails with a message that names the cause.

## Repro
1. On a machine where Codex is signed in with a ChatGPT account, run `codex exec -m gpt-6-sol --sandbox read-only --ephemeral --json "Reply with the single word OK."` in any Git repository.
2. Repeat with `-m gpt-6-luna` and `-m gpt-6-astra`.

## Expected
Each model in `plugins/sdlc-lite/adapters/codex/models.json` completes a turn.

## Actual
Observed 2026-09-29 with Codex CLI 0.154.0:

- `gpt-6-sol`: status 400, "The 'gpt-6-sol' model is not supported when using Codex with a ChatGPT account."
- `gpt-6-luna`: status 400, "The 'gpt-6-luna' model is not supported when using Codex with a ChatGPT account."
- `gpt-6-astra`: completed and replied OK.

## Context
Found while running the loading probe recorded in `docs/validation/nested-entry-file-loading.md`. `gpt-6-sol` is also the default model in this machine's Codex configuration.

`plugins/sdlc-lite/adapters/codex/models.json` uses `gpt-6-sol` for most builder, planner, verifier, researcher, archaeologist, filer, and conductor levels, and `gpt-6-luna` for scout.

Not tested: a role launched through `scripts/run.sh` with the Codex backend. The failure of role runs is inferred from the direct `codex exec` result. Also not tested: an API key account, where these models may be accepted.

Guess: the limit is on the account type and not on the CLI version.

## Constraints
Model and effort defaults are user decisions. This ticket does not change `models.json` without the user's choice of replacement. The failing test lands before or with the fix, never after.
