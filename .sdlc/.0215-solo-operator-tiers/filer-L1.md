<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
The one planned step, step 1, passed verification (verifier L2). Two gaps remain from the ticket's own done condition:
- No live run per host has been made, so "one live run per host shows a size-M ticket delivered by solo with a batched verifier" is unmet.
- The lane output has not been recorded.

## PR title
T-0215: Add solo session agent with tiers S, M, L and make it the default lane for size S and M

## PR body
### Summary
Adds `solo`, a session agent that delivers one ticket end to end in a single session. It has three tiers keyed to ticket size. The lane script (`steps.py lane`) now gives `solo` as the default before planning for size S and M tickets. Size L and XL stay `full`. The lean and full chains are not removed.

Tier models, per the user's 2026-10-04 decision:

| Tier | Claude | Codex |
|---|---|---|
| S | Sonnet low | gpt-6.1-sol low |
| M | Sonnet xhigh | gpt-6.1-sol high |
| L | Opus xhigh | gpt-6.1-sol xhigh |

Tiers M and L end with one independent batched verifier on a different model family. Tier S has no verifier.

### Changes
- `plugins/sdlc-lite/agents/solo.md`: new session agent, 33 lines. It holds the Claude tier table and the typed-brief loop. It pins no model in its front matter.
- `adapters/codex/models.json`: new `solo` entry (L1, L2, L3 map to tiers S, M, L). No existing row changed.
- `scripts/codex_roles.py`: `solo` gets `workspace-write`.
- `adapters/codex/agents/`: new `sdlc-solo-l1..l3.toml`, generated. `sdlc-conductor-l1.toml` is regenerated because `conductor.md` changed.
- `scripts/steps.py`: before planning, S and M give `solo`. The help text, docstring and selftest cases are updated.
- `scripts/check.py`: new item 17 covers the solo agent file, the `solo` models.json entry and the three TOMLs, with negative controls. `solo` is excluded from the run.sh agreement check like conductor and messenger.
- `agents/conductor.md`: one lane-choice line. T-0199 will reconcile it later.
- `plugins/sdlc-lite/AGENTS.md` and `docs/references/sdlc-internals.md`: session-agents sentence, lane text, and a new `solo` entry.
- `.sdlc/evals/0001-solo-tiers.md` and `table-lock.json`: new eval for the T-0185 model-table rule, then relocked. The eval records a user decision with no experiment (pass_rate 0/0, cost unknown).

### Verification
Verifier L2 (Sonnet) returned pass, and all acceptance criteria passed:
- Files and tables: solo.md exists and names Sonnet and Opus. The `solo` models.json assert passes. The three TOMLs exist.
- Lane: `steps.py lane` prints `solo` for sizes S and M, and `full` for size L. The verifier read the diff and saw the old code gave `fix` for S and `lean` for M.
- `steps.py selftest`: PASS.
- `check.py plugins/sdlc-lite`: `ok: 19 role levels, 9 agents checked`.
- Negative control on a temp copy: changing `Opus xhigh` in solo.md was flagged, and so was deleting `sdlc-solo-l2.toml`. The unmodified copy passed.
- `evals.py check`: ok, and the lock cites 0001.
- `codex_roles.py generate --check`: verified.
- `scripts/check-packaging.py`: PASS.
- `bash plugins/sdlc-lite/scripts/check.sh`: rc 0. It skipped shellcheck (not installed) and the evals lock guard. The guard was run directly instead.
- `git diff --check main -- plugins docs`: clean.

### Limits
- No live run on either host. This is a known limit.
- The runner's family rule does not cover solo, because solo writes no builder result under `step-<n>/`. solo.md pairs the tiers with a different-family verifier directly. Tier M (Sonnet) runs `verifier L3` (Fable). Tier L (Opus) runs `verifier L2` (Sonnet). Codex runs `sdlc-verifier-l3` (gpt-6-astra, not sol).
- solo.md tells tiers M and L to write `## Acceptance criteria` into the task handoff when it has none, so the verifier has criteria. The step did not ask for this. The verifier judged it acceptable.

## Changelog entry
- Added the `solo` session agent with tiers S, M and L (Claude: Sonnet low, Sonnet xhigh, Opus xhigh; Codex: gpt-6.1-sol low, high, xhigh). `steps.py lane` now names `solo` as the default before planning for size S and M tickets. Tiers M and L end with one batched verifier on a different model family.

## Follow-ups
- fix-now: Update the prose that still says the lane prints `fix`, in `plugins/sdlc-lite/skills/chain/SKILL.md:27`, `skills/handoff-format/SKILL.md:21`, and `docs/lean-sdlc/design.md` lines 68 and 283.
- decide: Choose whether `run.sh` should ever see a solo run. Today it does not, so the family swap never fires and solo.md pins the different-family verifier itself.
- note: The ticket's done condition still needs one live run per host (size-M ticket delivered by solo with a batched verifier) and the lane output recorded.
- note: conductor.md now has both the "Size S → /fix" line and the new solo line, and T-0199 is to reconcile them.
- note: Eval 0001 records a user decision with no experiment (pass_rate 0/0), so the solo tier models have no benchmark backing yet.
