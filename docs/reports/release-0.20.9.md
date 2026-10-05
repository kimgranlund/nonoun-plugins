# Release 0.20.9

Recorded: 2026-10-05. SDLC Lite 0.20.9. Progressive Context stays at 0.1.2 (`git diff --name-only v0.20.8 HEAD -- plugins/progressive-context` prints nothing). Previous release: SDLC Lite 0.20.8 (tag `v0.20.8`). Built from main commit d2f473b; the release branch adds one stale-context repair commit (c6f091e), the manifest bump and this record with its docs index entry.

This record states only what a committed file or a command run for it shows. Where a record does not say something, it says so.

## What changed for consumers

| Change | Evidence | Ticket |
| --- | --- | --- |
| `/sdlc-lite:ask` sweeps the thread, task folder, tickets and notes for open questions and blockers and asks them in one `AskUserQuestion` round with reasoned options; `check.py` guard 29 | `skills/ask/SKILL.md`; `docs/reports/ask-skill-live-run.md` | T-0231 |
| `scripts/inventory.py` is a read-only document inventory (flags `orphan`, `stale`, `duplicate`, `oversized`, `misplaced`, `broken_links`) with a procedure doc for turning it into a reorganization plan; nothing is moved; guard 30 | `scripts/inventory.py`; `docs/repo-onboarding/reorganization-plan-procedure.md` | T-0232 |
| `scripts/docs_check.py` runs deterministic checks D-1 to D-12 against a repository's `docs/`; `onboard.py` reads the optional `## Kinds`, `## Decide` and `## Legacy` sections of `docs/layout.md`; guard 33 and a selftest in `check.sh` | `scripts/docs_check.py`; `docs/docs-schema/design.md`; `docs/reports/2026-10-05-docs-check-run.md` | T-0240, T-0241, T-0242 |
| `/sdlc-lite:plan-goal`, `/sdlc-lite:plan-loop` and `/sdlc-lite:plan-fanout` each return one runnable block (`/goal`, `/loop`, the `fanout.py run` command with a dry run first), checked by the new `scripts/plan_check.py`; guard 31 | the three skill folders; `docs/reports/plan-skills-live-run.md` | T-0249, T-0250, T-0251 |
| The fanout report names the real solo model per backend, and a lane gate that runs zero tests stops the merge unless `--allow-empty-gate` is passed | `scripts/fanout.py`; fanout selftest case 19 | T-0230 |
| `fanout.py` copies an untracked `.sdlc/config` into its worktrees, so a numbered close resolves `ticket_root` and the lane continues | `scripts/fanout.py`; `docs/reports/defect-fixes-0.20.9.md` | T-0258 |
| `steps.py precheck <task dir>` refuses a task handoff with no `## Goal`; `run.sh` calls it before a planner or plan-reviewer starts (exit 2) | `scripts/steps.py`, `scripts/run.sh`; same report | T-0261 |
| `steps.py next` prints `resplit` for a builder blocked with Notes starting `stale lane:` (rebase the lane, supersede the step dir, `steps.py split --only <n>`), not `replan`. `builder.md`, the chain skill, `conductor.md` and the level rubric name it | `scripts/steps.py` selftest "next resplit"; c6f091e repairs the conductor and rubric text | T-0263 |

Repository maintenance, not shipped to consumers: `docs/validation/` is now `docs/reports/` and `AGENTS.md` and the references were rewritten (T-0246; `scripts/rename_refs.py` rewrites references, counts broken links and checks that none remain; 364 paths under `docs/` show as renames in `git diff --name-status v0.20.8 HEAD`). T-0257 makes the link counter skip code and allowlists the 12 remaining broken links, with a baseline guard (`check.py` item 32; `docs/reports/broken-links-cleanup.md`, `docs/reports/broken-links-allowlist.md`). T-0255 and T-0256 add a solo lane contract and assessment (`docs/lean-sdlc/solo-lane-contract.md`, `docs/lean-sdlc/solo-lane-assessment.md`) and a status banner and vocabulary table on the generative-constructs specs.

Eleven Codex agent files changed, all regenerated from the role bodies: `sdlc-builder-l1` to `l5`, `sdlc-conductor-l1`, `sdlc-plan-reviewer-l1`, `sdlc-plan-reviewer-l1-alternate`, `sdlc-planner-l1` to `l3`. `adapters/codex/models.json` is unchanged and no model or effort value was edited in this release.

## Upgrade notes

- Codex projects that installed the generated agents need `python3 plugins/sdlc-lite/scripts/codex_roles.py install <project>` to receive the eleven changed agents.
- Anything that cites `docs/validation/` in this repository now cites `docs/reports/`.
- `run.sh` can now exit 2 for a planner or plan-reviewer on a task handoff with no `## Goal`, before an attempt record is written.
- `steps.py next` can now print `resplit`; a caller that only knows `replan` for a blocked builder should follow the chain skill.

## Verification

Each ticket below has a verifier or review record in its closed folder under `.sdlc/` (closed folders are not read for this record beyond the files named here).

- T-0258, T-0261, T-0263: one L3 verifier, pass; it reverted each fix in a throwaway worktree and saw each regression test fail (`docs/reports/defect-fixes-0.20.9.md`). Its note that `conductor.md` and the level rubric still said "blocked -> replan" is repaired in c6f091e.
- T-0231, T-0232, T-0241, T-0242, T-0246, T-0257: each has a closed ticket folder with verifier or verification records; T-0257 and T-0231 passed after a rework.
- T-0230, T-0249 to T-0251: the wave-b verifier results are in the commits `f550b8d` and `8dbb2b6`.
- Live runs recorded as evidence: `ask-skill-live-run.md`, `plan-skills-live-run.md`, `2026-10-05-docs-check-run.md`.

## Known limits

- T-0243 (branch boundary checks) is not merged and not in this release; it goes to 0.20.10.
- T-0233, T-0244, T-0245, T-0248 and T-0252 to T-0254, the build follow-ups of the docs schema, the reorg apply and the Progressive Context gap analysis, are open tickets in `.sdlc/` and not in this release. T-0259, T-0260, T-0262, T-0264 to T-0272 are field defects filed and not fixed.
- The docs schema is a design plus `docs_check.py` and the layout parser; the migration and promotion helpers are tickets, not code.
- Live evidence is one run per feature on one machine; no live Codex run was made for this release. `shellcheck` is not installed, so no shell script is shellchecked.
- The independent verifiers ran on their own branches, not on the release tree.

## Checks run for the release

Run from the release worktree on branch `worktree-agent-aaf7cd0fac455cb08` at the commit that adds the manifest bump, this record and its docs index entry, 2026-10-05:

- `bash plugins/sdlc-lite/scripts/check.sh`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `git diff --check`
- Version parity: both sdlc-lite manifests read 0.20.9, both Progressive Context manifests read 0.1.2.

Results are in the release summary given with the publish; an independent read-only Opus pass over this record ran before publication and its review text is not committed.
