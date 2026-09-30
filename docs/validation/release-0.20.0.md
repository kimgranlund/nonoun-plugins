# Release 0.20.0

Recorded: 2026-09-30. SDLC Lite 0.20.0. Progressive Context stays at 0.1.2 (no change since 0.19.0). Previous release: SDLC Lite 0.19.0 (89e7ab8).

## What changed for consumers

| Area | Change | Ticket |
| --- | --- | --- |
| New role | `plan-reviewer`: judges a plan before any builder starts and reports `pass`, `replan`, or `blocked`; required for a planner L3 plan, a step at builder L4 or L5, a merge step, or any replan; `steps.py review` prints the next action and `steps.py split` refuses a rejected plan; Claude Opus high (Fable high after an Opus planner), Codex Astra high (Sol 6.1 high after an Astra plan) | T-0171 |
| Models | Codex defaults follow a role-based allocation on `gpt-6.1-sol`, `gpt-6-astra`, `gpt-6-luna`, and `gpt-5.6-terra`; `verifier_alternates` maps luna and astra to `gpt-6.1-sol`; Claude models are unchanged | Codex model work |
| Hooks | `block-role-spawn.sh` (PreToolUse Agent): in a conductor session it denies spawning a role agent or another plugin's builder, verifier, reviewer, planner, or checker through the Agent tool; `block-disk-scan.sh` (PreToolUse Bash): role runs refuse `find /` and home-folder scans. Claude Code only | T-0166, T-0169 |
| Runner | A role that edits `run.sh` during its own run still saves its result; a run that exits 0 with no result is recorded as failed; role runs no longer leave throwaway worktrees under `.worktrees/tmp`; `reap-tmp-worktrees.sh` | T-0170, T-0154 |
| Steps | `steps.py widen` rewrites the scope guard when the conductor widens a step; `steps.py resume` restarts a chain at the lowest unfinished step; the planner puts a shared contract's dependents in the same step | T-0148, T-0150, T-0149 |
| Fanout | Refuses a ticket when the integration tree is dirty; lanes can run a branch owned by an outside agent (`<lane>@<branch>=<ids>`); per-run `[fanout-<id>]` log prefixes; gate logs per attempt | T-0151, T-0152, T-0155, T-0156 |
| Tickets | `depends:` accepts `file:<path>` and `cap:<name>`, and tickets may declare `provides:` | T-0153 |
| Traces | New `/sdlc-lite:review-traces` skill and `scripts/traces.py`: ingest a project's run traces and flag sdlc-lite waste and bugs with evidence; the first two stages spend no model calls | T-0157 |
| Docs | Recipe for running a role from a clean temporary worktree | T-0167 |
| Tests | `lifecycle-selftest.py` and `codex-selftest.py` poll with a deadline, so `check.sh` stays green on a loaded host | T-0159 |
| Spike | Read-only reorganization prototype on this repository; ships no production code and records which reorganization rules to keep or change | T-0161 |

Every code change above was built by a builder role and checked by an independent verifier role through `scripts/run.sh`, through `/chain`, `/fix`, or a fanout lane. The Codex model work was built and verified through `/fix`, and the Codex session reviewed its mapping and found four stale statements, which were fixed.

## Upgrading

- Codex defaults changed. Roles now run on `gpt-6.1-sol`, `gpt-6-astra`, `gpt-6-luna`, and `gpt-5.6-terra`. On a ChatGPT account these ran on Codex CLI 0.159.2; on 0.154.0 three of them returned HTTP 400. Check `codex --version` and your account's models before relying on them (`docs/validation/codex-account-models-2026-09-30.md`).
- Regenerate and reinstall Codex agents after upgrading (`codex_roles.py install <project> --check`). A project that installed 0.18.0 Codex agents keeps the three `sdlc-verifier-lN-alternate.toml` files from 0.18.0; they are outside the receipt, so remove them by hand.
- The new hooks apply to Claude Code only.

## Known limits

- Neither the Codex allocation nor the plan-reviewer has been measured against the alternative. No same-task comparison exists, and no benefit is claimed.
- `steps.py split` gates only on a rejecting review. A caller that skips `steps.py review` still splits an unreviewed plan; no script catches a skip.
- `/chain` 4.2 mid-build replans still go straight to `steps.py split --only` without a review.
- Hook enforcement (`block-role-spawn.sh`, `block-disk-scan.sh`) does not cover Codex.
- One account and one machine for every Codex observation. API-key accounts and native named-agent transport are not established.
- The conductor routing probe did not reproduce the reported bypass with 0.18.0 or 0.19.0 (`docs/validation/role-routing-probe.md`); the hook is the enforcement added for it.

## Checks run for the release

Run on branch `release-0.20.0` on 2026-09-30, from the repository root, all exit 0:

- `bash plugins/sdlc-lite/scripts/check.sh` (shellcheck skipped, not installed)
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `git diff --check main -- . ":(exclude).sdlc"`
- Version parity across each plugin's Claude and Codex manifests

An independent whole-release verifier pass follows; its record is `.sdlc/release-0.20.0/`.
