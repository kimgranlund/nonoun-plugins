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
