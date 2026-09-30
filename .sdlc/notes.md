# Notes

`tickets.py close` appends follow-ups that did not become tickets.

## T-0105: Find out why the T-0072 background hook did not stop the run in... (2026-09-26)

- note: the Monitor tool name in the `PreToolUse` payload is assumed to be exactly `"Monitor"` (matching the hooks.json matcher and block-background.sh's check); no live probe covers it, same as the planner's Risks and the T-0076 non-goal it inherits.
- note: step 7's builder accidentally ran `git checkout` on `run.sh` mid-mutation-test, discarding its uncommitted steps 1-6 changes, and restored it from a manual `/tmp` backup taken before the mutation; the verifier independently confirmed the restore was exact (matching diff stats and intact heading-pick and timeout-floor lines), but the near-loss is worth knowing about if this pattern recurs.

## T-0160: Onboard skill: entry files, docs layout, and check mode (2026-09-29)

- decide: The house linter `skill_lint.py` flags F2 (`disable-model-invocation` and `user-invocable` not declared) and W2 (no "Use when" phrasing) on the `onboard` and `progressive-context` skills, and no repo or host skill validator has run on either; decide whether to adopt those rules.
- note: The step 4 and step 5 builders and the step 4 verifier left throwaway projects in the OS temp folder, because `rm -rf` was denied.
- note: The design's "Unsettled" items are not covered by any artifact: whether an installed plugin can read its own template version on both hosts, and the token cost of nested entries in a real role run.
- note: The selftest's `digest()` mutant survives, since the gates only compare marker and text with each other; the real hashes were confirmed once by `shasum`, not by a gate.

## T-0161: Spike: read-only reorganization plan on this repository (2026-09-29)

- decide: Whether to build apply for the reorganization or drop it. The spike recommends deferring, since a reviewed plan is 2 moves and 13 line edits by hand. Revisit only when a repository's plan is too large to carry out by hand.
- decide: Whether to update `docs/repo-onboarding/reorganization.md` to v0.7 with the "Rules to change" list (plan file outside `.sdlc/`, the `Date:` frozen-candidate test, the added plan fields, regenerate and compare for N15).
- fix-now: Freeze `docs/claude-handoff.md` and `docs/claude-response.md` in a real `docs/layout.md` before any reorganization of this repository uses the plan.
- note: The two-sources-one-destination collision code path in `reorg_plan.py` was never exercised on this tree.
- note: A broad glob such as `claude-*.md` pulls the placed file `docs/maintenance/claude-hooks.md`, so the design's glob rules need a warning for it.

## T-0169: A role's whole-disk find hung a planner run for 25 minutes (2026-09-29)

- decide: Codex roles have no guard against whole-disk searches, because the hook is Claude-only; a line in the shared role contracts (needs `codex_roles.py generate`) was left out of this S-sized ticket.
- note: `scripts/check-packaging.py` still passes when a hook registered in `hooks.json` points at a missing script; only `check.sh` catches it (the step-2 verifier found this, and it predates this change).
- note: The hook bypasses are `cd / && find .`, a scan reached through a script, and a variable path such as `p=/; find "$p"`. There is no live role-session probe of the hook.

## T-0167: Document running a role from a temporary worktree (2026-09-29)

- decide: A live model run of the recipe (for example `scout L1`) in a throwaway bare-clone repo was not made, so the ticket's "runs end to end" is proven with the stub only; decide whether to require live evidence.
- decide: A committed (not git-ignored) `.sdlc/` inside a dirty primary still dirties that checkout on every run; decide whether to support a `.sdlc/` home outside every checkout.
- note: A headless conductor under fanout (`SDLC_ROLE=conductor`) cannot use the recipe because `hooks/block-stray-worktree.sh` denies the worktree add; the doc scopes it out and the hook was not changed.
- note: `shellcheck` is not installed on the build host, so `check.sh` skips its shellcheck stage and the literal shellcheck guard fails there; it was verified only through a `pipx` shim.

## T-0166: Warn when the conductor spawns another plugin's role agent (2026-09-29)

- decide: The interactive `.claude/settings.json` conductor path was never observed; only `--agent sdlc-lite:conductor` was live-tested, so it is unknown whether `agent_type` is set there and the hook fires.
- note: `git diff --check` skips untracked files, so `block-role-spawn.sh` and the live-run report were not whitespace-checked; run it once they are added.
- note: Rerunning `hook-live-probe.sh --conductor --out` overwrites the live-run report and drops its hand-written note under the heading.

## T-0170: A builder that edits run.sh loses its own result (2026-09-29)

- note: the fix protects only a `run.sh` child that has already started. A role that corrupts `run.sh` still breaks later runs, and the hook option to refuse role writes to `run.sh` and `run_lifecycle.py` was not built.
- note: the criteria's one-line worktree negative controls are blocked by `block-stray-worktree.sh` in role runs, so verifiers must split them into separate commands.
- note: shellcheck was not installed, so the changed `run.sh` was never shellchecked.
## T-0162: Planner names the entry files each step needs (2026-09-29)

- note: `check.sh` skipped shellcheck (not installed), so the shell-lint part of the release gate was not run for this change.
- note: The Codex live run put builder and verifier on one model (`gpt-6-astra`, `shared_with_builder=yes`), so it does not show independent verification on Codex.
- note: In the live run, the Codex reads were combined `cat` commands, and the report records that the evidence is the read, not rule compliance.

## T-0163: Codex rejects gpt-6-sol and gpt-6-luna on a ChatGPT account (2026-09-29)

- decide: Scout L1 still uses `gpt-6-luna`, which a ChatGPT account rejects, so Codex scout runs fail there until the user picks a replacement or accepts it.
- decide: No live `scripts/run.sh` run with the Codex backend on a ChatGPT account was made. The root AGENTS.md asks for a focused live run in a throwaway project for changed role behavior.
- note: `docs/validation/native-codex-smoke.json` hashes the deleted alternate TOMLs. It was left as historical evidence, and it may look stale next to the current agent set.
- note: Projects that installed the old agents keep stale `sdlc-verifier-lN-alternate` TOMLs in `.codex/agents/`, because `install` does not remove files it no longer generates. They are unused while no alternate is configured.

## T-0151: fanout.py never discards uncommitted edits when it resets the integration tree (2026-09-29)

- note: The `integration status failed: ...` outcome in `fanout.py` was added beyond the plan, and only the dirty path has a selftest case; the status-failure path is untested.
- note: The merge-commit assertion in selftest case 5d passes even with the guard removed, so only the outcome-row and edit-survives assertions catch a regression.
- note: The guard ignores untracked files in the integration tree by design, since `reset --hard` leaves them alone.

## T-0155: Attempt id on lane and gate log lines (2026-09-29)

- decide: The ticket says to use `SDLC_ATTEMPT_ID`, but fanout mints its own `fanout-<hex>` id, so T-0157's join by attempt id needs a rule for how fanout run ids relate to role attempt ids.
- note: Lane and gate log files are still overwritten on resume, and only `logs/fanout.log` keeps history. T-0156 owns per-attempt gate logs and may rename the `gate-<lane>-<id>-<k>.log` path the probe reads.
- note: Driver and gate log lines now carry a `[<run_id>] ` prefix that T-0157's trace ingest must strip. Nothing in the repo parses lane logs today.

## T-0148: Conductor scope decisions update the acceptance criteria, not just prose (2026-09-29)

- decide: `steps.py widen` refuses the exact `test "$(git diff ...)" = "<file>"` and prefix `grep -v '^path$'` scope-guard forms that past plans used, so those steps take the slower L3 replan. Decide whether to add those forms or standardize the planner's guard form.
- note: The step-3 verifier saw one unexplained non-zero `check.sh` exit that did not reproduce, and no log was saved. If it recurs, capture the log and check whether it depends on concurrent runner activity.
- note: The live conductor behavior for widening in an unattended lane is untested, and no throwaway-project live run was done. AGENTS.md asks for live evidence when changed host behavior is claimed.
