# Lean SDLC design review

Recorded: 2026-10-03. Independent review of `docs/lean-sdlc/design.md` v0.1 (commit 6fcc9eb on branch `lean-sdlc`), tickets T-0189 to T-0192. The reviewer was the `architect` role, `run.sh architect L1`, model `fable` effort high (from `runs.jsonl`), a different family from the author (Claude Sonnet). It was read-only in the repository except for its own result and `decompose/` output. Raw result: `.sdlc/lean-sdlc-review/architect-L1.md`; its 21-leaf decomposition is in `.sdlc/lean-sdlc-review/decompose/`.

## Verdict

Not ready at v0.1. The Baseline numbers and most code citations held (every figure in the Baseline table, the 70,671 contract bytes, the 38 citing files, no hook naming `.sdlc/`, `fanout.py` without `ticket_root`, the `steps.py:103` rule). Two load-bearing mechanics did not match the pipeline's decision core. v0.2 applies every finding; no finding was dismissed. The design is not built.

## Findings and what v0.2 did

| # | Severity | Finding | v0.2 |
| --- | --- | --- | --- |
| 1 | blocker | `plan.md` and `plan-rev-<k>.md` cannot exist: `run.sh:17-21, 186-191`, `order.py:22`, `steps.py:1237`, `plan-reviewer.md:10` fix result names and replan detection | Deltas are `planner-L<n>-<k>.md` with a `revises:` header; `split` merges; `steps.py resolve` added; reviewer read rule extended |
| 2 | blocker | Batched verification has no independence enforcement: the family rule reads builders only in the verifier's own dir (`run.sh:198-207`, `codex_roles.py:100-120`), the cited branch verifier ran builder-less, and `run.sh` never refuses | Batching needs a runner change (build row V) first; until then pinned to verifier L3; validation row corrected to assert a remap, not a refusal |
| 3 | major | Step handoffs by reference target the wrong component: `split` adds only the goal (`steps.py:897`); the restatement is planner-written | Now a planner rule plus a `steps.py lint` anchor check; C2 sized L2 |
| 4 | major | Moving `roadmap.md` and `notes.md` is not "code that finds the task directory": hardcoded at `tickets.py:842, 851, 1231, 1308, 1547, 1595`, assumed by `ticket_dir` (`:304`), the scan (`:535`), `onboard.py:252`, and ten outside cites | One path resolver owns the paths; the move is user decision (open question 3) |
| 5 | major | "Matches `steps.py review` exactly" was incomplete: a `## Plan review` line and an `unresolved:` assumption also require review or stop; "no replan" is unknowable at plan time | Mandatory list extended; `lane` calls the same function as `review`, has three decision points, and recomputes |
| 6 | major | `close --reason` skips every filer gate and reads no builder or verifier notes (`tickets.py:83-85`), so "filer only with follow-ups" had no gate | Open question 6: lean lane always runs the filer (recommended) or `close` gains a gate |
| 7 | major | The `Files:` overlap check cannot run at fanout launch (`fanout.py:432`), and duplicates the scope criterion | Dropped `Files:`; derive from scope criteria, or check at merge time from `git diff --name-only` |
| 8 | major | Ticket cut: C1 and C2 both edit `steps.py`; C3 is full-chain work by the design's own list; D1 and D2 both edit `tickets.py` | Build order re-cut by owning file, sequenced where files are shared, levels corrected |
| 9 | minor | Layout listed unbuilt folders and omitted git-ignored `runtime/` and `dogfood/` | Layout marks T-0183 to T-0187 folders as planned and lists the ignored folders |
| 10 | minor | "Refuses on id clash across worktrees" is not a precondition (`tickets.py:122-129`); `check.py:330` pins a literal path | Precondition removed; `check.py:330` named in the change table |
| 11 | minor | Codex host skill has no `steps.py` mention (`skills/sdlc-lite/SKILL.md`) | Codex skill change added to the lane ticket and the change table |
| 12 | minor | A dangling-anchor lint needs a resolution rule | The step block names its plan file in `plan: <file>#<anchor>`; lint resolves it |

## Decisions still needed from the user

1. Batched verification: ship only after the runner change, or earlier pinned to verifier L3; and whether it is acceptable for L3 builds at all.
2. Lean close-out: always run the filer (recommended), or add a `close` gate.
3. Whether `roadmap.md` and `notes.md` leave the `.sdlc/` root.
4. Open questions 1, 4, and 5 in the design (lean thresholds, migration default for existing repos, who may record a skip).

## Limits

- The review checked the design against the code at main d4fb850. It built and ran nothing.
- The reviewer's note: the other repo's four complaints are known only from the pasted sentences; the lean thresholds (two steps, 12 criteria) and the footprint targets (14 files, 60 KB) are unmeasured until `footprint.py` exists.
- Findings were applied by the author, not re-reviewed. A second review before the first build ticket is advisable.
