<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0198: skips.md guard in tickets.py check and close

## PR body
### Summary
`tickets.py check` and `tickets.py close` now guard tickets recorded as lane `lean` or `fix`. Such a ticket must have a `## Skipped` entry in its `skips.md` for each full-chain role it did not run. The guard lives in `tickets.py`, not `check.py`, so it runs in consumer repos. This is the L6 row of the lean SDLC design and depends on T-0197.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - New helpers `skip_section`, `skip_missing`, `skip_line` and `skip_problems`.
  - The lane is the last `- lane:` line in the `## Lane` section of `skips.md`. The guard applies only when that lane is `lean` or `fix`.
  - The roles checked are planner, verifier (once per live `step-<n>` dir, ignoring `step-<n>.superseded-<k>`) and filer.
  - An entry has the form `- skip: <role>; step: <n or all>; reason: <why>; decided: <who>`. It counts only when `reason` and `decided` are non-empty.
  - `cmd_check` runs the guard after the router-problems check, for `done` tickets only.
  - `cmd_close` runs it right after the existing `status == 'done'` refusal and before any write. It covers the plain, `--reason`, `--ack-warnings` and `--dry-run` paths. The existing refusals are unchanged.
  - A new `(skips)` selftest block with 11 cases, plus docstring sentences for `check` and `close`.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the Layout `skips.md` line now covers `## Skipped` and gives the entry format. This is the one place the format is written out.
- `docs/references/sdlc-internals.md`: one sentence on the guard and its exemption.

Exemption: a ticket is exempt when it has no `skips.md`, no `## Lane` section, no `- lane:` line, or a last lane of `full`. The planner read "closed before the guard's introduction marker" as "has no lane record". A plain close writes no close date, so a date marker could not be derived. No existing ticket has a `skips.md`, so the 214 tickets stay green.

### Verification
Both steps got an independent verifier verdict of pass.
- **Step 1** (verifier L1) ran every criterion:
  - The `check` fixtures:
    - A fix ticket missing planner and filer entries exits 1 with `lean-a: skips.md records lane fix but has no ## Skipped entry for planner, filer`, and the pre-feature ticket `old-b` is not named.
    - The same ticket with both entries exits 0.
    - A lean ticket reports `verifier step 1` and ignores `step-2.superseded-1`.
  - The `close` fixtures:
    - `close --reason` on a fix ticket missing entries refuses and leaves `status: proposed`.
    - A filer-path close of a lean ticket with no planner result refuses and leaves `status: proposed`.
    - `close --reason` with entries succeeds and sets `status: done`.
  - `tickets.py selftest` printed PASS.
  - `tickets.py --root .sdlc check` printed `ok: 214 tickets, roadmap current`.
  - Only the three allowed files changed.
- **Negative controls:** the planner ran the red-now criteria at HEAD before the build. `check` exited 0, `close` succeeded and the greps found nothing, so each failed for the missing behavior. After the build the verifier saw them pass.
- **Step 2** (verifier L1) ran the gates on the built tree. The builder needed no fixes.
  - `bash plugins/sdlc-lite/scripts/check.sh` exited 0, with shellcheck skipped because it is not installed.
  - `python3 scripts/check-packaging.py` printed PASS.
  - `codex_roles.py generate --check` printed `Codex agent definitions verified`.
  - `tickets.py --root .sdlc check` printed `ok: 214 tickets, roadmap current`.
  - `git diff --check` and the scope check passed.
  - The verifier observed negative controls in a throwaway worktree for the `tickets.py check`, `git diff --check` and scope-check gates.
  - `check.sh`, `check-packaging.py` and `codex_roles.py generate --check` were not shown red on this host. Those runs prove only that the gates pass.

No version bump, tag, push or publish. No live per-ticket run, per the burn-down brief.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `tickets.py check` and `close` now require a `## Skipped` entry in `skips.md` for each full-chain role (planner, verifier per step, filer) skipped by a ticket recorded as lane `lean` or `fix`. Tickets with no lane record are exempt. The entry format is documented in the handoff-format skill.

## Follow-ups
- note: Post-feature lean or fix tickets whose conductor never ran `steps.py lane` have no lane record and stay unguarded until T-0199 adds the conductor rule that runs `lane` first.
- note: Once T-0199 makes `/fix` run `lane`, every `/fix` close needs planner and filer `## Skipped` entries or `close --reason` refuses, so T-0199 must write them.
- note: The exemption reads "closed before the guard's introduction marker" as "has no lane record". If a date or version marker was meant, the step 1 exemption rule changes.
