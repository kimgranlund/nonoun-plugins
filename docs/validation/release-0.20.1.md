# Release 0.20.1

Recorded: 2026-09-30. SDLC Lite 0.20.1. Progressive Context stays at 0.1.2 (no change since 0.20.0). Previous release: SDLC Lite 0.20.0 (6803899).

## What changed for consumers

Two Claude model changes, made so the model table fits the maintainer's Claude Max login, plus the checks that follow.

| Change | Detail | Ticket |
| --- | --- | --- |
| Scout pinned to a real Haiku | On Claude Code 2.1.285 with a Max login the alias `haiku` resolves to Sonnet 5.5, so the scout was never on a Haiku. `run.sh` now pins `claude-haiku-4-5` at effort low. A live scout run showed `claude-haiku-4-5` as the only model. See `docs/validation/haiku-alias-2026-09-30.md` | T-0172 |
| Planner L3 on Opus xhigh | Planner L3 (cross-cutting plans and every replan) was Fable xhigh and is now Opus xhigh. The plan-reviewer must avoid the planner's family, so a review of a plan by planner L2 or L3 now runs on Fable high; only a plan by the Sonnet planner L1 is reviewed on Opus high. Some Fable spend moves from planner to reviewer. A live planner and review run showed `opus xhigh` then `fable high`. See `docs/validation/planner-l3-opus-2026-09-30.md` | T-0173 |
| Checks | `check.py` parses and compares pinned model ids such as `claude-haiku-4-5` (shown as `Haiku 4.5`) between `run.sh` and the level rubric, with a negative control; selftests cover the new rows | T-0172, T-0173 |

Both changes were built by a builder role and checked by an independent verifier role through `scripts/run.sh` and the `/fix` lane. No Codex model or effort changed. The Codex planner profiles were regenerated because the level rubric is preloaded into them.

## Upgrading

- Reinstall Codex agents after upgrading (`codex_roles.py install <project>`; `install <project> --check` only reports stale definitions and writes nothing). The planner and plan-reviewer profiles embed the level rubric and changed.
- Claude scout runs now use `claude-haiku-4-5`. Claude planner L3 runs now use Opus xhigh.

## Known limits

- The quality of Opus xhigh plans against Fable plans is not measured. The change rests on recorded cost (Fable was about 31% of recorded cost across 912 role runs, planner L3 the largest item), not on a quality comparison.
- The scout pin ties the row to Haiku 4.5. If that model is retired, scout runs fail until the row changes. `claude-haiku-5-5` was not recognized on the tested CLI.
- The Agent-tool seat list still says `haiku` for mechanical in-session spawns. The Agent tool takes an alias, so that seat runs Sonnet 5.5 on the tested login; the rubric now says so.
- One machine and one login (Claude Code 2.1.285, Max plan). Other plans may resolve the `haiku` alias differently.
- Carried from 0.20.0: neither the Codex allocation nor the plan-reviewer is measured against an alternative; a caller that skips `steps.py review` still splits an unreviewed plan; hook enforcement does not cover Codex.
- Open: T-0174, a `block-disk-scan.sh` false positive on a quoted mention inside a compound command, observed by the 0.20.0 verifier and not yet reproduced with its exact command.

## Checks run for the release

Run on branch `release-0.20.1` on 2026-09-30, from the repository root, all exit 0:

- `bash plugins/sdlc-lite/scripts/check.sh` (shellcheck skipped, not installed)
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `git diff --check main -- . ":(exclude).sdlc"`
- Version parity across each plugin's Claude and Codex manifests

An independent whole-release verifier pass follows; its record is `.sdlc/release-0.20.1/`.
