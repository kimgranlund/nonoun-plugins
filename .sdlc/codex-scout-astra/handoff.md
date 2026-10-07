## Goal
The Codex scout runs on a model this account accepts.

## Context
User decision, 2026-09-30: scout L1 on Codex uses `gpt-6-astra` at effort `high`. Probes on 2026-09-29 and 2026-09-30 showed `gpt-6-luna`, `gpt-5-6-luna`, and every other candidate rejected on a ChatGPT account; `gpt-6-astra` is the only model accepted. `docs/reports/release-0.19.0.md` and `docs/references/codex-role-execution.md` record the luna default as pending a user decision; that decision is now made. Claude models in `run.sh` do not change.

## Constraints
Only the Codex mapping, its generated agents, and the two records change.
