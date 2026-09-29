---
id: T-0163
title: "Codex rejects gpt-6-sol and gpt-6-luna on a ChatGPT account"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
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

## Decision
User decision, 2026-09-29: replace `gpt-6-sol` with `gpt-6-astra` in `plugins/sdlc-lite/adapters/codex/models.json`, keeping each level's effort. The user chose this option knowing its stated consequence: the Codex verifier then shares the builder's model, or needs a third model.

Consequence found in the code: `codex_roles.resolve` hardcodes the verifier's alternate model. After a `gpt-6-astra` build it switches the verifier to `gpt-6-sol`, which the account rejects. Replacing the model in `models.json` alone therefore does not let a Codex verifier run.

Required change:

1. `models.json`: every `gpt-6-sol` becomes `gpt-6-astra`. `gpt-6-luna` (scout L1) is not part of the decision and stays; it is also rejected on this account, which is recorded here and left for the user.
2. `codex_roles.resolve`: the verifier's alternate model comes from configuration in `models.json`, not from a literal in the code. When no alternate other than the builder's model is configured, the verifier keeps the builder's model and the runner records that verification shared the builder's model. Documented in the level rubric and in `docs/codex-role-execution.md`.
3. Regenerate the Codex agents and update the Codex selftest.

Found blocking T-0162 step 5 (`.sdlc/0162-entry-files-in-step-handoffs/step-5/builder-L3.md`, Notes).

## Constraints
Model and effort defaults are user decisions. The user has chosen the replacement above. Claude model defaults in `run.sh` do not change. The failing test lands before or with the fix, never after.
