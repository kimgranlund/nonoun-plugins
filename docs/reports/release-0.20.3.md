# Release 0.20.3

Recorded: 2026-10-04. SDLC Lite 0.20.3. Progressive Context stays at 0.1.2 (no change since 0.19.0). Previous release: SDLC Lite 0.20.2 (2a428cc, tag `v0.20.2`). Released from commit dd14392 on main.

## What changed for consumers

| Change | Detail | Ticket |
| --- | --- | --- |
| `messages.py wait` | `messages.py wait --receiver NAME [--timeout SECONDS] [--interval SECONDS]` blocks until a message is in `new/<receiver>/`, prints one line per message (id and absolute path, tab separated), and exits 0. It exits 3 with `no new messages` on timeout. Timeout is 1 to 600 seconds (default 120) and interval is at least 1 second (default 5). It never claims or moves a message and never prints a body. `agents/messenger.md` now loops on `wait --timeout 100 --interval 10` instead of polling `count` itself, and the Codex agent `sdlc-messenger-l1` is regenerated from it | T-0181 |
| Idle-host limit stated | The mailbox docs, `agents/messenger.md`, `docs/specs/ticket-stages/design.md` and `docs/references/codex-role-execution.md` now say that a subagent, including the messenger, can report only into a parent turn that is still running and cannot wake an idle host on Claude Code or Codex. The mailbox entry text, `agents/messenger.md` and `docs/specs/ticket-stages/design.md` also say that `wait` returns only into an active parent. `docs/reports/messages-idle-host-limit-2026-10-01.md` corrects the 0.20.2 record, which shipped without this limit | T-0180, T-0188 |
| One result schema per role | New `scripts/results.py` (`schema`, `key`, `validate`, `selftest`) owns each role's result schema: key section, allowed first values, a header line `<!-- role=... level=... model=... effort=... -->`, and declared section order. `run.sh` writes the header and validates every result through `results.py validate`, exiting 3 with one stderr line when a result fails. `steps.py` calls `results.py structure_error` and prints `invalid result: <path>: <reason>` when the newest plan, plan-reviewer, builder or verifier result does not match. Neither `run.sh` nor `steps.py` keeps a copy of the schema table, and `check.py` checks each agent body against it. `skills/chain/SKILL.md` and `skills/fix/SKILL.md` now tell the conductor to stop on `invalid result` | T-0184 |
| `footprint.py` | New `scripts/footprint.py` prints a ticket folder's files, bytes, markdown bytes, steps, planner bytes and role runs per role and level, and `footprint.py check <ticket dir> [--max-files N] [--max-bytes N]` exits 1 when a limit is exceeded. Read-only. It is the measuring tool for the lean SDLC design; no flow calls it yet | T-0193 |
| Lean lane text and coarse-step rule | `skills/chain/SKILL.md` has a `## Lean chain` section: lean conditions, the cases where the full chain is mandatory, and that the lean lane always runs the filer. `agents/planner.md` has a `## Coarse steps` rule (one step per independently verifiable outcome, at most 12 criteria per step). `steps.py lint` prints a warning on stderr, with unchanged stdout and exit code, when a plan that meets the lean conditions has more than two steps or a step with one criterion. No script computes the lane yet; the conductor reads the text. Planner Codex agents are regenerated | T-0194 |
| Lean SDLC design and filed work | `docs/lean-sdlc/design.md` (v0.4) and two independent review records, the watcher design (`docs/planning/ticket-stages/watcher-design.md`) and its review, and filed tickets. T-0183, T-0185, T-0186, T-0187 and T-0195 to T-0208 are not built in this release; T-0189 to T-0192 are closed as superseded by the lean build tickets | T-0182, T-0189 to T-0192 |

Every code change above was built by a builder role and checked by an independent verifier through `scripts/run.sh`. T-0184, T-0193 and T-0194 each also had a whole-branch L3 verifier whose result is committed (`.sdlc/verify-t0184`, `.sdlc/verify-t0193`, `.sdlc/verify-t0194`); the T-0184 whole-branch verifier needed three attempts, because two ended without a verdict when the earlier account hit its weekly limit. T-0181's whole-branch verification result is not committed, so this record does not rely on it. The version bump and this record were made by hand and fact-checked by an independent L3 verifier on Fable, whose result is committed at `.sdlc/verify-release-0.20.3/step-1/verifier-L3.md`; its first completed pass listed defects that are corrected here.

## Upgrade notes

- Codex projects that installed generated agents should run `python3 plugins/sdlc-lite/scripts/codex_roles.py install <project>` for each project to receive the regenerated `sdlc-messenger-l1` and planner agents.
- Role results already carry the header line `run.sh` has always written, so existing results validate. A check of every `<role>-L<n>.md` result under `.sdlc/` in this repository found one refusal, the hand-recovered closed result `.0163`, whose header line carries a trailing recovery note that the header pattern does not accept; closed tickets are not read by the pipeline and the T-0184 branch verifier accepted it.
- The `check.sh` suite now also runs the `results.py` and `footprint.py` selftests.
- No migration command is needed. Layout is unchanged.

## Known limits

- The T-0184 ticket (`.sdlc/.0184-role-result-schema`) is still `ready` in this commit even though its code is merged and verified and is not closed in this commit.
- The Codex backend arm of the T-0184 live run was not made: no `SDLC_BACKEND=codex` run showed the result check after a Codex role run (`docs/reports/role-result-schema-live-run.md`).
- `wait` cannot wake an idle host, and the external watcher that would is a design only (`docs/planning/ticket-stages/watcher-design.md`, reviewed as ready after fixes). The supervisor (T-0183), `evals/` (T-0185), `proposals/` (T-0186) and the board overview (T-0187) are not built.
- The `wait` live runs (`docs/reports/messages-wait-live-run.md`) ran once per host on one machine, on plugin commit bc21b53 with three uncommitted files that were later committed. The whole-branch verifier result for T-0181 is not committed.
- The lean runner family rule, batched verification, skips guard, replan by delta, carry-forward sections, the fanout overlap check, the topic-folder layout and its migration are filed (T-0195 to T-0208) and are not in this release. The `steps.py` coarse-step check is a warning only.
- `shellcheck` is not installed, so `run.sh` and `run-selftest.sh` were not shellchecked.

## Checks run for the release

Run from the release worktree on branch `release-0.20.3` (commit dd14392 plus the version bump and this record), 2026-10-04, all exit 0:

- `bash plugins/sdlc-lite/scripts/check.sh` (shellcheck skipped, not installed)
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` (208 tickets, roadmap current)
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`
- `python3 plugins/sdlc-lite/scripts/results.py selftest`
- `python3 plugins/sdlc-lite/scripts/footprint.py selftest`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- `git diff --check`
- Version parity: both SDLC Lite manifests read 0.20.3; both Progressive Context manifests read 0.1.2.
