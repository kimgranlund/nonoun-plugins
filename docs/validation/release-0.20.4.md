# Release 0.20.4

DRAFT. Placeholders marked [[PENDING ...]] depend on T-0215 and T-0210 reaching main and on the fixed release commit. Remove every marker and this line before the commit.

Recorded: [[PENDING date]]. SDLC Lite 0.20.4. Progressive Context stays at 0.1.2 (no change since 0.19.0). Previous release: SDLC Lite 0.20.3 (82a6a54, tag `v0.20.3`). Released from commit [[PENDING fixed commit sha]] on main.

## What changed for consumers

Nothing here is on by default except the lane text and the runner rule. The supervisor, the evals lock, proposals and the solo agent are opt-in or maintainer-facing.

| Change | Detail | Ticket |
| --- | --- | --- |
| Lane per ticket | `scripts/steps.py lane <task dir>` prints `fix`, `lean`, or `full` first, then one `reason:` line per deciding fact, and appends each result to the task's `skips.md` (a lane never returns from `full`). The `sdlc-lite` skill says to run it before work on a ticket and follow the first line, and `skills/chain/SKILL.md` describes what the script now computes | T-0197 |
| Skips guard | `tickets.py check` and `close` fail a done ticket whose `skips.md` records lane `lean` or `fix` but lacks a `## Skipped` entry for a role the full chain would have run, or lacks the verifier or filer evidence the lane requires. A ticket with no `skips.md`, or no lane record, is exempt | T-0198 |
| Verifier family rule at the task dir | A verifier launched at the task directory (no builder result in its own handoff dir) now takes the newest builder result of the highest-numbered live `step-<n>/` (not `step-<n>.superseded-<k>/`), so the family-independence rule fires. `run.sh` and `codex_roles.py resolve` apply the same rule | T-0195 |
| Batched verification state | `steps.py next` calls a step done through a task-dir verifier whose `## Verified` section lists the step's newest build with Verdict `pass`, only for builds that qualify (the rule is `steps.batch_verified`). `board.py` renders it as `pass · builder <level> · batch verifier <level>` | T-0196 |
| Carry forward | `scout`, `researcher`, `architect` and `archaeologist` results end with a `## Carry forward` section (at most 15 lines, each with a path:line or source); the planner reads it first and searches only what it does not answer. `check.py` requires the section in the four producing roles | T-0202 |
| Fanout | `fanout.py` prints a planned-scope overlap report after the lanes (`overlap (planned scope): ...`) and waits when planned paths overlap; lane tickets resolve through `tickets.ticket_dir(root)`, so `ticket_root: tickets` works | T-0203, T-0204 |
| Idle-host watcher | `scripts/supervisor.py` (`init`, `watch [--run] [--once]`, `status`, `reset`, `selftest`) is deterministic code with no model call. It polls the mailbox through `messages.py` functions, never claims, moves or reads a message body, and when mail waits for a configured receiver starts a headless host session for it. Default wake mode is a fresh ephemeral session per wake; attached and notify are opt-in. It is a dry run unless `--run`, and a wake follows unattended-run rules (`SDLC_HEADLESS=1`, never push or publish). Limits (cooldown, wakes per hour and per day, timeout, reply depth, failures) are in `limits.json` | T-0183 |
| Evals and the model-table lock | `scripts/evals.py` records model and effort experiments in `.sdlc/evals/` and a lock (`table-lock.json`) that ties the `run.sh` and `models.json` table to one eval. `check.py` fails when a model-table change has no new eval and lock. This is a maintainer rule for this repository's plugin, and no default changed | T-0185 |
| Proposals | `scripts/proposals.py` (`scan`, `accept`, `reject`, `promote`, `selftest`) mines run records and `notes.md` for repeated failures and writes candidate proposals under `.sdlc/proposals/`. Nothing is applied automatically | T-0186 |
| Maintainer guidance | The plugin `AGENTS.md` opens with the project philosophy and a rule to prefer the lean lane or `/fix`, running the full chain only with a stated reason. `agents/builder.md` adds a completion rule (smallest change that meets the criteria; report blocked instead of looping). The maintainer agent file carries the standing objective | T-0209 |
| Spec gate | [[PENDING T-0210: describe the final merged behavior and the files, from the merged diff]] | T-0210 |
| Solo operator | [[PENDING T-0215: describe the final merged behavior: the `solo` session agent and its tiers, the lane default (`solo` for size S and M), the Codex tiers, the `check.py` guard, and the eval cited for the table lock; from the merged diff]] | T-0215 |
| Design records | `docs/lean-sdlc/cost-control.md` (v0.3, with its review record and the user decisions), `docs/other/orchestration-optimization-question.md`, and updates to `docs/ticket-stages/watcher-design.md`. These are design and reference only. T-0187, T-0199 to T-0201, T-0205 to T-0208, T-0211 to T-0214 are not built [[PENDING: update this list after T-0199, T-0212, T-0214 and T-0216 statuses at the fixed commit]] | none |

Every code change above was built by a builder role under `scripts/run.sh` and checked by a verifier role; the exceptions and the verifiers that were skipped under the burn-down rules are listed under Known limits.

## Upgrade notes

- Codex projects that installed generated agents should run `python3 plugins/sdlc-lite/scripts/codex_roles.py install <project>` for each project: the builder (L1 to L5), planner, researcher, scout, architect and archaeologist agents were regenerated for the new text [[PENDING: add the new solo agents once T-0215 is on main]].
- No migration is needed. A ticket with no `skips.md` is exempt from the skips guard, and `steps.py lane` is opt-in per ticket.
- The supervisor is opt-in. To try it: `python3 plugins/sdlc-lite/scripts/supervisor.py init`, edit `hosts.local.json`, then `watch` (a dry run) before `watch --run`.
- The `check.sh` suite now also runs the `evals.py`, `proposals.py` and `supervisor.py` selftests [[PENDING: add any selftest T-0210 and T-0215 add]].

## Known limits

- Supervisor: one run per arm, one machine and one account per host. The first run's Codex wake arm failed and passed in the earlier run, so the outcome varied. After a prompt fix it passed 3 of 3 reruns, and the other six arms were not rerun on the fixed prompt. The attached idle signal cannot tell an idle open terminal from a closed one. Codex MCP and connector tools are not blocked by the wake command. A push stopped before git runs, or one using `--no-verify` or another `core.hooksPath`, is not seen by the pre-push hook (`docs/validation/supervisor-live-run.md`).
- Evals: the hash covers parsed table rows, not comments or layout; a hand edit of `table_sha256` alone in `table-lock.json` is not detected; URLs are not fetched; one machine, one run (`docs/validation/evals-live-run.md`).
- Proposals: `promote` ran only in the selftest and no ticket was filed in the live run; one machine, one run (`docs/validation/proposals-live-run.md`).
- Carry forward: Claude Code only, Codex was not run. The probe's metrics are heuristics over tool inputs, and the first two attempts at step 2 failed on the probe's own metric, so the limit is recorded and no third cycle ran. One small fixture, where the saving was one search (`docs/validation/carry-forward-live-run.md`).
- Runner family rule at the task dir: one trial on Claude only. Codex is covered by `codex-selftest.py` and a dry run, and the choice across steps by number is exercised only by the selftests (`docs/validation/runner-family-task-dir-live-run.md`).
- Skips guard: it covers only tickets with a recorded lane. A lean or fix ticket whose conductor never ran `steps.py lane` has no `skips.md` and is not covered. T-0199 would close that gap and is not in this release [[PENDING: confirm at the fixed commit]].
- Verifier coverage: T-0186 and parts of T-0183 and T-0198 were merged under the course-correction cost rules with per-step verifiers and no whole-branch L3 verifier [[PENDING: confirm from each ticket's records at the fixed commit]]. The T-0183 whole-branch L3 verifier passed.
- Solo operator and spec gate: [[PENDING: no live run for solo until T-0216; state what T-0210 and T-0215 recorded]].
- A solo-versus-lean benchmark is in progress and is not part of this release [[PENDING: link it if its record is on main at the fixed commit]].
- `shellcheck` is not installed, so shell scripts were not shellchecked.

## Checks run for the release

[[PENDING: run on the release branch after the fixed commit is chosen and the version is bumped; list each command and its exit code]]
