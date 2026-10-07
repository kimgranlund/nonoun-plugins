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
- decide: Whether to update `docs/planning/repo-onboarding/reorganization.md` to v0.7 with the "Rules to change" list (plan file outside `.sdlc/`, the `Date:` frozen-candidate test, the added plan fields, regenerate and compare for N15).
- fix-now: Freeze `docs/other/claude-handoff.md` and `docs/other/claude-response.md` in a real `docs/layout.md` before any reorganization of this repository uses the plan.
- note: The two-sources-one-destination collision code path in `reorg_plan.py` was never exercised on this tree.
- note: A broad glob such as `claude-*.md` pulls the placed file `docs/references/claude-hooks.md`, so the design's glob rules need a warning for it.

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
- note: `docs/reports/native-codex-smoke.json` hashes the deleted alternate TOMLs. It was left as historical evidence, and it may look stale next to the current agent set.
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

## T-0156: Keep gate logs per attempt, never overwrite (2026-09-29)

- note: driver logs (`<lane>-<id>.log`) are still overwritten on a fanout rerun. The planner left this to T-0157 or a later follow-up.
- note: shellcheck is not installed on this host, so `check.sh` skipped shell lint for this change.

## T-0149: A step that changes a shared contract pulls its dependents into scope (2026-09-29)

- decide: Run a focused live run of the planner and verifier contract-dependents rule on a throwaway project, since this change proves only wording and the `check.py` gate, not role behavior.
- note: The ticket's Intent section was empty, so the planner vs. verifier split is the planner's own reading of the Goal; both roles got the rule.
- note: The planner did not read the source run's evidence (gen-ui-system-svelte-lite lane logs), so the contract kinds listed may miss the exact shape that broke there.

## T-0150: Resuming a chain restarts at the blocked step, not the newest step (2026-09-29)

- decide: The ticket's Repro and Actual were placeholders, and gen-ui's lane logs and `stepn.sh` were never available. If gen-ui's conductor picked the right step dir and `next` misread it, this fix does not cover that case. Someone should compare against the gen-ui evidence.
- note: The resume rule in the chain skill (including running `run_lifecycle.py recover` first) is prose. No automated check proves a conductor follows it before `resume`.
- note: shellcheck is not installed on the host, so `check.sh` skipped that part and it stayed unverified.

## T-0153: Ticket depends can name a capability or file, not only a whole ticket (2026-09-29)

- note: shellcheck is not installed on the build machine, so the shellcheck part of `check.sh` was skipped and is unverified.
- note: fanout lane scheduling does not read `depends`, so `file:` and `cap:` entries do not affect lane scheduling. The ticket lists this as a non-goal.

## T-0154: Builders inside a lane leave nested tmp worktrees behind (2026-09-29)

- note: The reaper keeps a stale prefix whose dead pid was reused by an unrelated live process until that process exits. This is conservative and never destructive.
- note: The root cause of the 2026-09-28 leftovers is inferred from the code. The lane logs in the other repo were not reachable, and a live claude's shutdown time under TERM is not shown by the selftests.
- note: `check.sh` skipped shellcheck because it is not installed on the build host, so the new shell scripts were not linted.

## T-0152: External agents (Codex) get lane integration and reserved ticket ids (2026-09-29)

- note: For an external ticket whose merge brings in nothing new (a second ticket on the same branch), the report's Commit cell shows the previous close commit, not a merge commit. Step 5 reworded the docs to say so.
- note: Live host validation on Codex was not run for this change. Only the shared-script selftests and `check.sh` covered it.
- note: The step 1 builder's six mutation checks and three of the step 2 builder's five were not re-run by the verifiers. The base-SHA red runs and two re-run mutations cover the behavior.

## T-0159: Lifecycle and codex selftests time out under host load (2026-09-29)

- note: The verifier did not independently re-check the builder's claim that `codex_exec.py` kills the stub on timeout (the stub sleep is now 600 s). A `pgrep` after the runs found no orphans.
- note: The negative-control guard fails as a whole only if every test passes against the old `run_lifecycle.py`. It already fails through `test_sigkill_recovers_claude_but_codex_native_refuses` and `test_exit_zero_without_result_fails`, so loosening one of those tests would go unnoticed while the other still fails.

## T-0157: review-sdlc-traces: find SDLC-caused waste and bugs in project traces (2026-09-30)

- decide: the done-condition run on the gen-ui-system-svelte-lite traces of 2026-09-28 (batch 3, T-0148 to T-0154) was never run; the architect could not find that repo or `sdlc-feedback-batch3.md` on this machine, and no step's artifacts show the run. Supply the corpus or accept the synthetic and self-repo evidence.
- decide: the handoff asks for scout or archaeologist at L2 for diagnosis, but the architect found only L1 for those roles in `run.sh`. The artifacts do not show how the skill settled this, so a person must accept L1 or authorize a model change.
- note: the `overwritten-gate-log` corpus branch has never run here, because `.worktrees/fanout-night/logs` is absent on this host.

## T-0171: Independent plan-reviewer role before implementation (2026-09-30)

- decide: `steps.py review` is enforced only by docs, the `check.py` route words, and the `split` refusal, so a conductor that skips it on a plan with no reviewer result still splits and no script catches that.
- note: `verifier_alternates` and `shared_with_builder` keep their names while also serving the plan-reviewer, so the names understate their scope.
- note: `/chain` 4.2 mid-build replans still go straight to `steps.py split --only` without `steps.py review`, and the 4.2 item text was left unchanged (step 3 builder note).
- note: The bench comparison against the same tasks without the reviewer is not done, and it is required before any claim the reviewer helps.

## T-0177: Mailbox core: messages.py, lifecycle, schema, and run.sh notice (2026-10-01)

- note: shellcheck is not installed on this host, so `check.sh` skipped it. `run.sh` and `run-selftest.sh` were not shellchecked.
- note: the selftest race control catches a non-atomic claim only when the copy and delete straddle the barrier. If the copy and delete both run after the barrier, the selftest passes. The verifier saw this as a plain-unlink variant failing in 1 of 3 full runs.
- note: live host validation of the mailbox is T-0179. The messenger agent is T-0178. Neither was exercised here.

## T-0178: Messenger agent: declared agent, Codex mapping, and check.py coverage (2026-10-01)

- note: `check.sh` skipped shellcheck in both step runs because it is not installed, so the shell checks there were not run.
- note: the step 3 `run.sh` unchanged guard compared against `SDLC_BASE_SHA`, which equalled HEAD, so it could not go red there. The `run.sh` diff was not otherwise independently inspected in the artifacts.
- note: the messenger has not been run live on Claude or on Codex. That evidence is T-0179's scope.
## T-0175: Opt-in tickets/ root and generated .sdlc/AGENTS.md router (2026-09-30)

- decide: `scripts/fanout.py` does not support `ticket_root` for regular lanes (builder step 8 and the verifier both flag it), so fanout lanes in a `tickets/` repo may miss tickets.
- note: the fresh-role live run in `docs/reports/ticket-root-router-live-run.md` is recorded unverified, because the role got `tickets/AGENTS.md` by nested-memory loading and the `, claimed by` state was only replayed.
- note: `render()` raises `Fail` for an external caller on an unsupported `ticket_root` value. All in-repo callers resolve the root first.

## T-0179: Messages entry files and fresh-role live validation (2026-10-01)

- decide: The Codex messenger spawn check in `docs/reports/messages-live-run/probe.py` prints `messenger_spawned=yes` even when no agent spawned, because the entry file it prints names the agent. Decide whether to base it on the subagent rollout's `session_meta` (`agent_role` plus `parent_thread_id`).
- decide: A Claude messenger can return "polling" with no claim, and a parent that stops at the first report misses the message. Decide whether `messages/AGENTS.md` or the messenger agent should state the spawn-again rule.
- note: The Claude path-only live arm ran in safe mode, so nested `CLAUDE.md` loading of the mailbox files was not exercised there.
- note: The negative control and every arm ran one trial each on one machine, and the negative control ran on Claude Code only.

## T-0194: Lean lane text and coarse-step rule in chain and planner (2026-10-04)

- note: Lean eligibility in `steps.py lint` covers only plan-time facts, because ticket size and the nearest-AGENTS.md-owner condition cannot be computed there; T-0197 owns `steps.py lane`.
- note: `steps.py -h` now uses `RawDescriptionHelpFormatter` with an epilog, added so the warning literal appears in help; subcommand help was reported unchanged.
- note: `shellcheck` is not installed on the build host, so that part of `check.sh` was skipped in this run.
## T-0193: footprint.py: measure and gate a ticket's footprint (2026-10-04)

- note: Step 2 builder did not run the three `grep -qF` criteria itself; the step 2 verifier ran them and they passed, so nothing is open.
- note: The planner run reported a stray worktree and branch `t0185` (`.worktrees/t0185`); clean it up if it is no longer needed.
- note: The exact-count criteria for the four closed dot folders go red if any of those folders is edited on main, for example by the T-0190 layout migration. Re-baseline them if that happens.

## T-0197: steps.py lane, review_required(), and skips.md (2026-10-04)

- note: no artifact shows `steps.py lane` run on a real ticket dir or a live Codex host; all evidence is selftests, temp dirs and static checks, so live evidence is left to T-0208.
- note: a repeated `lane` call appends a duplicate record line to `skips.md` (step 2 builder smoke run); T-0198's guard should expect this.
## T-0203: fanout.py merge-time file-overlap check (2026-10-04)

- note: An overlap first visible after a later lane has started its merge is not reordered. The docstring and `sdlc-internals.md` state this limit.
- note: `check.sh` skipped `shellcheck` (not installed), so shell lint did not run for this change.
- note: Planned-scope overlap in `--dry-run` always lists an external lane's tickets as not planned, because their step folders live on the external branch.
## T-0195: Runner: verifier family rule for a task-dir verifier (2026-10-04)

- decide: `steps.py split --only` has a 300 s default guard timeout, but `check.sh` took 417 s on this host. Nothing in the chain skill or the agents says to pass `--guard-timeout` (grep of `plugins/sdlc-lite/skills` and `plugins/sdlc-lite/agents` for `guard-timeout` printed nothing). Plans with a `check.sh` guard criterion hit the plan-defect refusal. The plan reviewer's step-4 finding in this task was this case.
- note: shellcheck is not installed on this host, so the shellcheck pass in `check.sh` was skipped and `run.sh` and `run-selftest.sh` were not shellchecked.
- note: the first step-3 attempt's throwaway temp dir `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.PDQbvWuqBm` still exists outside the repo. The builder's cleanup was denied by permissions.

## T-0202: Carry forward section in scout, researcher, architect, archaeologist (2026-10-04)

- decide: Step 2's live run never passed its own metric (criteria 2 and 9). Choose whether T-0208's live evidence re-proves the planner-reads-scout behavior with a probe that detects reads through a glob.
- fix-now: The scout result in run 1 listed both call sites without naming the search or scope that produced the list, which the scout contract asks for on a complete list. Check the contract wording for that clause.
- note: The branch verification at `.sdlc/verify-t0202/step-1` (verifier-L3) has no verdict, so no independent branch-level verdict exists beyond the step 1 L2 pass.
- note: A role's own em dash cannot be reproduced in a report that forbids the character. The report writes it as `--`.

## T-0198: skips.md guard in tickets.py check and close (2026-10-04)

- note: Post-feature lean or fix tickets whose conductor never ran `steps.py lane` have no lane record and stay unguarded until T-0199 adds the conductor rule that runs `lane` first.
- note: Once T-0199 makes `/fix` run `lane`, every `/fix` close needs planner and filer `## Skipped` entries or `close --reason` refuses, so T-0199 must write them.
- note: The exemption reads "closed before the guard's introduction marker" as "has no lane record". If a date or version marker was meant, the step 1 exemption rule changes.
## T-0196: Step state for a whole-ticket (batched) verifier result (2026-10-04)

- note: Nothing instructs a task-dir verifier to write `## Verified` yet, so batching is inert until the conductor, chain and verifier text change (T-0199).
- note: Gates and last-step exclusion is heuristic (title contains `gates green`, or highest step number). A non-last gates step with another title could be batch-verified, and a stricter marker would be a planner contract change.
- note: A step handoff with no `## Step <n>:` line counts as an empty title, so it is not excluded and can be batch-verified. The handoff does not cover this case.
- note: A conductor that reruns a batch after a partial fail must re-list the passing steps, or they fall back to per-step `verify`. This costs one extra verify and is deliberate.

## T-0210: Spec gate A1: specgate.py check, run.sh plan-reviewer refusal, plan guard-timeout line (2026-10-04)

- fix-now: `check.py` order check uses the first `specgate.py check` line in `run.sh`, which is the header comment at run.sh:63, not the command at line 265; point it at the command line so it can't pass on the comment.
- note: On macOS, where `timeout` is not on PATH, `steps.py` does not treat a span starting with the bare word `timeout` as a command, so `specgate.py` does not see it either. The `timeout N` prefix only counts inside a span that already counts as a command, for example `cd . && timeout 900 bash scripts/check.sh`.
- note: A plan with more than one `guard timeout:` line outside its step blocks uses the first positive value, and 0 or less is skipped.
## T-0204: fanout.py resolves lane tickets through ticket_dir (2026-10-04)

- note: The `ticket_root` lane selftest fixture relies on `tickets.py close` succeeding in a fresh repo with no router files, so a later change to close's router handling could turn it red for a reason outside `fanout.py`.
- note: shellcheck is not installed on the build host, so the shell lint leg of `check.sh` was never exercised for this change.

## Release 0.20.8: prepared, not published (2026-10-05)
- Branch `release-0.20.8` (worktree `.worktrees/release-0.20.8`) is cut from main 2e91432 with the 0.20.8 manifest bump and `docs/reports/release-0.20.8.md`. No tag exists and nothing was pushed; `origin/main` is still 9146596.
- Full check set passed on 87ebde0 (check.sh full run, packaging, generate --check, check.py, tickets check, 13 selftests, diff --check). Later commits are docs only.
- Fact-check passes (independent read-only Opus, detached): pass 1 FAIL (4 factual, 1 unsupported, all fixed), pass 2 FAIL (2 factual, fixed), pass 3 narrow PASS with no factual finding (one wording nit, fixed). The overnight goal says to publish only if the fact-check passes and to stop if it fails after one round of fixes; pass 2 failed after the first fix round, so publishing was left for a decision.
- To publish from the release commit `git rev-parse release-0.20.8`: annotated tag v0.20.8, `git push origin ${SHA}:refs/heads/main` (fast-forward only), push the tag, `gh release create v0.20.8 --verify-tag --title "SDLC Lite 0.20.8" --notes-file docs/reports/release-0.20.8.md`, merge the branch back into local main.

## Decisions recorded 2026-10-06 (user, via /sdlc-lite:ask)
- 0.21.0 publish is authorized once T-0287's live evidence and the independent fact-check pass; fast-forward only, never force.
- maison may contact maison-testing (T-0002) for the T-0106 tar handoff; the sdlc-lite author stays out of that session.
- The nine parked tickets (T-0187, T-0200, T-0201, T-0205 to T-0208, T-0211, T-0213) get a per-ticket review; stale ones are dropped, with the table in docs/reports/parked-tickets-review-2026-10-06.md.
- 2026-10-06 (user, via AskUserQuestion): the fleet skills (/sdlc-lite:fleet-retro T-0305 to T-0308, /sdlc-lite:fleet-status T-0310 to T-0312) ship as 0.20.12 tonight, ahead of 0.21.0, on the same publish terms as the earlier patches (fast-forward only, never force, independent fact-check first). Plan: merge branch `fleet-status` (based on `fleet`, which holds retro and config) into main, verify, prepare the release with the 0.20.11 procedure, publish.
- 2026-10-06 (user, via /sdlc-lite:ask): red-under-load rule approved as verifier policy: a browser-test red under measured load above the stop line re-runs once, alone; green alone is recorded as a load flake. Ticket T-0317. gen-ui-kit onboarding is skipped (it does not use the .sdlc pipeline; the conductor stops asking). dom-charts' local commit 09c0c16 stays local.

## T-0205: layout key and one resolver for ticket dir, roadmap, notes (2026-10-06)

- decide: this repo's own `.sdlc/config` has no `layout:` line, so every `tickets.py check` now prints the migrate-layout warning; choose between adding `layout: flat` and migrating (T-0206 or T-0207).
- note: `ROUTER_FLAT_INTRO` duplicates the first paragraph still inside `ROUTER_TEMPLATE`, and `router_bodies` swaps them by string match; editing one without the other leaves a topics tree with the flat paragraph (the `tp-new` selftest case catches it).
- note: the builder edited two selftest asserts the handoff did not list, in the numbered-config warning block. Each now checks `'ticket_folders: numbered' not in out + err`, because every flat root now warns.
- note: `check.py` guards, listed among the ticket's owning files, were not touched, and the artifacts show no guidance-doc update (the AGENTS.md files). The Done-when line says affected guidance is updated, so confirm whether anything was needed.

## T-0206: tickets.py migrate-layout (2026-10-06)

- note: This repo's `.sdlc` has not been migrated. The command would refuse today because the tree is dirty and `.sdlc/pause-2026-10-06.md` is a loose root file. Move or remove that file and commit before any real run.
- note: After a migration the managed `AGENTS.md` block reads `stale` until `onboard.py setup` runs. This is by design and is stated in the upgrade note.
- note: The `ticket_root` bullet and the `.sdlc/roadmap.md` and `.sdlc/notes.md` path text in the docs were left to T-0207 (readers and docs).
- note: The tickets selftest now takes about 37 s, up from about 31 s at HEAD.

2026-10-07: 0.21.0 published (v0.21.0, 027da15a) under the standing authorization after T-0287 live evidence (docs/reports/2026-10-07-subagent-mode-live.md) and two detached Opus fact-checks (second pass found one record omission, fixed before tagging). Open: T-0288 (retire the headless path), the account-switch spanning-run criterion of T-0287, resume ladder, background sub-agents, session-limit behavior, Codex live evidence; tickets T-0275, T-0279, T-0280, T-0284, T-0286 and T-0326 to T-0332 closed without a verifier verdict file.
