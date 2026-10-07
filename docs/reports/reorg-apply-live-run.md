# Reorganization apply live run

Recorded: 2026-10-06. Live run for ticket T-0233: `reorg.py apply` moved four loose documents in a clone of this repository, in two batches, from the plan this repository already wrote in [the docs schema design](../docs-schema/design.md) (the `references/` and `other/` rows). This repository was not changed by the run. Evidence is in [`reorg-apply-live-run/`](reorg-apply-live-run/); the claims below name the file that shows each one.

## What ran

- `reorg.py` from the T-0233 worktree, uncommitted at the time, run with `--root <clone>`. Selftest: [`selftest.txt`](reorg-apply-live-run/selftest.txt), 30 `ok` lines for 15 gates and `reorg selftest: PASS`, on Python 3.9.6.
- Clone: `git clone -q` of this repository at `0b58bd23` into a temp folder outside the repository. In the clone I wrote `docs/layout.md` with an empty `## Homes` section and three frozen paths (`docs/reports/`, `plugins/sdlc-lite/bench/results/`, `plugins/sdlc-lite/adapters/codex/agents/`) and committed it as `49be510d`. Its text: [`clone-layout.txt`](reorg-apply-live-run/clone-layout.txt).
- Plan: [`plan.json`](reorg-apply-live-run/plan.json). Batch `references` moves `docs/codex-role-execution.md` and `docs/plugin-compatibility.md` to `docs/references/`; batch `other` moves `docs/claude-handoff.md` and `docs/claude-response.md` to `docs/other/`. No link fixes.
- Dry run, then apply with the printed digest: `reorg.py apply plan.json --root <clone> --dry-run`, then `reorg.py apply plan.json --root <clone> --approve <digest>`. Outputs: [`dry-run.txt`](reorg-apply-live-run/dry-run.txt) and [`apply.txt`](reorg-apply-live-run/apply.txt) (stdout and stderr).

## Results

- No refusal. The dry run listed 19 rewrites for batch `references` and 4 for batch `other`, two baseline links, and digest `b6403009...` ([`dry-run.txt`](reorg-apply-live-run/dry-run.txt)). That is the listing the plan expected from a read-only simulation before the build: the root `AGENTS.md` and `README.md`, `docs/AGENTS.md` (two on one line), `docs/README.md`, the four relative links inside the moved `codex-role-execution.md`, and the cites in `docs/generative-constructs/`, `docs/maintenance/`, `docs/docs-schema/design.md`, and both plugins' entry and notes files. `docs/plugin-compatibility.md` has no relative link that needed a change, so it has no rewrite line.
- `docs/claude-response.md:60` was rewritten once per batch: to `references/codex-role-execution.md` when its target moved, then to `../references/codex-role-execution.md` when the file itself moved ([`dry-run.txt`](reorg-apply-live-run/dry-run.txt)).
- The two baseline links are the known ones to the sibling UI project, in `docs/generative-constructs/README.md` and `progressive-context-plugin.md` ([`dry-run.txt`](reorg-apply-live-run/dry-run.txt)).
- Apply printed the same listing and digest, then `commit 240bf77c... references`, `commit 56e99a4d... other`, and `final check: pass` ([`apply.txt`](reorg-apply-live-run/apply.txt)). The clone's HEAD after the run is `56e99a4db400fed029bcb6358c2421047ec4695b`, and its tree was clean.
- Each commit is `reorg: <name>` with one `move` line per move and the `plan digest` line, and Git records the moves as renames (`docs/{ => references}/...` in [`git-log.txt`](reorg-apply-live-run/git-log.txt)). Batch `references` changed 13 files, batch `other` 3.
- Broken links, counted with this tree's `rename_refs.py links` from the clone root: 838 checked, 12 broken before and after, the same 12 ([`links.txt`](reorg-apply-live-run/links.txt)).
- History: `git log --follow --oneline -- docs/references/codex-role-execution.md` in the clone printed 19 lines, the first `reorg: references` and the rest commits from before the move, so Git followed the rename ([`follow.txt`](reorg-apply-live-run/follow.txt)). The file has 87 lines and the apply rewrote 4 of them. This is one measurement, not a rule: the plan review saw a 3-line file with one rewritten line that Git did not follow.
- Edited document refuses: in a second clone reset to the same layout commit `49be510d`, a dry run printed the same digest; after an edit to the unrelated `docs/sdlc-lite/pillars.md`, apply with that digest printed `reorg.py: refused: digest mismatch: ...`, exited 1, and left HEAD at `49be510d` ([`refuse-digest.txt`](reorg-apply-live-run/refuse-digest.txt)).
- Missing approval refuses: the same clone, clean, with no `--approve`, printed `reorg.py: refused: no --approve; run with --dry-run, review the listing, and pass its digest`, exited 1, and left the tree unchanged ([`refuse-approve.txt`](reorg-apply-live-run/refuse-approve.txt)).

## Limits

- One run on one repository, one plan with four moves and no link fixes. No failed final check or restore happened live; restore is proven by the selftest's `restore` gate only ([`selftest.txt`](reorg-apply-live-run/selftest.txt)).
- None of the rewritten files holds an onboard managed block, so the managed-block hash refresh was not exercised live; the selftest's `managed` gate is its only proof.
- `docs/docs-schema/design.md:368` and `:370` were rewritten to the new paths ([`dry-run.txt`](reorg-apply-live-run/dry-run.txt)). They are the from-column of a proposal table and name the old paths on purpose, but they are repo-root path tokens, and rule 3 in `reorg.py`'s header rewrites every such token. A citation that means the old path is not distinguished.
- Glob classification and `onboard plan` are not built; the plan was written by hand from the design's table.
- The clone's commits were made with a clone-local Git identity (`builder`), visible in [`git-log.txt`](reorg-apply-live-run/git-log.txt).
- The design and status of apply are in [the reorganization rules](../repo-onboarding/reorganization.md).
