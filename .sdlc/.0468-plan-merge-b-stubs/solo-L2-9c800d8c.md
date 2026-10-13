<!-- role=solo level=L2 model=sonnet effort=high -->
## Output
T-0468 is built and every check named in the ticket passes. The one independent verifier failed one criterion, and that was a defect in my own criterion, not in the build.

**Changes**
- The four old plan skills (`plan-goal`, `plan-campaign`, `plan-doc`, `plan-fanout`) are now 12-line redirect stubs. Each description reads "Redirect: run `/sdlc-lite:plan <kind>`; removed in the next minor." Their four old `references/` files are deleted.
- `scripts/check.py`: items 31, 48 and 51 now point at `skills/plan/`. A new item 58 pins the stubs. I moved the `PLAN_KINDS` definition ahead of item 31 so both item 31 and item 57 use it.
- `agents/conductor.md` line 21 and `skills/sdlc-lite/SKILL.md` (the plan rows and the Codex `plan doc` note) now route to `plan <kind>` and `plan-loop`.
- `codex_roles.py generate` was rerun and `sdlc-conductor-l1.toml` is regenerated.
- The `goal-rules.md` links in `plan-doc-executor.md` and `plan-verification.md` now point at `plan/references/goal.md`. `docs/README.md` line 32 notes the rename.
- `skills/clarify/SKILL.md` pointed at the deleted `plan-doc-format.md`, so I retargeted that link to `plan/references/doc.md`.
- There is no changelog file in the repo. I put the changelog line and the compatibility note in a new section of `docs/references/plugin-compatibility.md`.
- I wrote `## Acceptance criteria` into the handoff, with `verifier: L3` because `steps.py verifier-level` gives L3 for a merge ticket.

**Checks**
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0. I observed each of these red on the real files and restored them each time:
  - stub kind token replaced
  - `## 1. Gather` regrown in a stub
  - `references/` folder regained
  - stub deleted
  - `plan-rules.md` removed from the plan skill
  - `outcome-block.md` removed from `goal.md`
  - `Goal line` removed from `doc.md`
  - `/sdlc-lite:plan doc` removed from the conductor
- `python3 scripts/check-packaging.py` exit 0.
- `codex_roles.py generate --check` exit 0, and `claude_roles.py generate --check` passes.
- `rename_refs.py links` exit 0. `check.py` item 32 confirms the 12 broken links equal the 12 allowlist rows.
- `bash plugins/sdlc-lite/scripts/check.sh` exit 0.
- `git diff --check` exit 0.

**Verifier**
- **Verdict:** L3 verifier fail on criterion 7 only. The span `grep -c 'plan doc' ...conductor.md` already printed 1 at the base sha, so it could not go red for the route change.
- **Fix:** I swapped it for `grep -c '/sdlc-lite:plan doc' ...conductor.md`. The verifier's copy showed it prints 1 on the built tree and 0 at the base; I confirmed it prints 1 on the built tree. The other criteria passed.
- **Not rerun:** I did not rerun the verifier after the swap.
- **check.sh:** the verifier did not rerun it because of machine load. It read my log, which shows exit 0.

`solo-report.md` passes `results.py solo-report`.

**Still open**
- Tests-gate does not apply (no `(red)` criterion), so `verify: needed` stands. The corrected criterion 7 has not been through a second verifier run.
- Nothing is committed, as instructed. `.sdlc/0468-plan-merge-b-stubs/` holds untracked records: `base-sha`, `skips.md`, `solo-report.md` and the `verifier-L3.*` files.
- Whether the host prefers `plan` over a stub from the description alone is unmeasured, since no routing corpus exists. Ticket D (removing the stubs and item 58) is later work, as is the prose sweep of old names in the specs.
