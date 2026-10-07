## Goal
Each Codex level runs on the model tier that mirrors its Claude level, with the same effort, and Codex verifier independence mirrors the Claude rule.

## Context
User decision, 2026-09-30: Claude Opus maps to `gpt-6.1-sol`, Fable to `gpt-6-astra`, Sonnet to `gpt-6-luna`, Haiku to `gpt-5.6-terra` (the only Terra the account lists). Effort mirrors the Claude row. The Claude table is in `plugins/sdlc-lite/scripts/run.sh` (`case "$role:$level"`). The Claude verifier rule: a verifier never shares its builder's model family, and after a Fable or Sonnet build it becomes Opus; on Codex that is `verifier_alternates`, mapping luna and astra to `gpt-6.1-sol`. Account discovery: `docs/reports/codex-account-models-2026-09-30.md`. The Codex conductor is not in the Claude table and keeps `gpt-6-astra` medium.

## Constraints
`scripts/run.sh` and every Claude model and effort stay unchanged. Only the Codex mapping, its generated agents, the Codex selftest fixtures, and `docs/references/codex-role-execution.md` change.
