<!-- role=architect level=L1 model=fable effort=high -->
## Approach

Verdict: not ready. The baseline and most code citations hold, but two load-bearing mechanics in the design do not match the pipeline's decision core, and the batching section weakens verifier independence while claiming it is unchanged. Findings, most severe first:

1. Blocker. `plan.md` and `plan-rev-<k>.md` cannot exist as planner outputs. `run.sh` fixes every result name to `<role>-<level>[-k].md` (`plugins/sdlc-lite/scripts/run.sh:186-191`) and requires `## Goal` in a planner result (`run.sh:20`). `order.py` only ranks files matching `^<role>-L<n>(-k)?.md` (`order.py:22`). `steps.py review` detects a replan as `len(plans) >= 2` over `planner-*.md` (`steps.py:1237`), and `split` reads only the newest planner file (`steps.py:8-9`). The plan-reviewer reads the newest `planner-*.md` and earlier ones only via `## Plan review` (`agents/plan-reviewer.md:10`). A delta written as the newest planner result becomes the whole plan for split and the reviewer; a file named `plan.md` is invisible to all three. Section 2 change 1 and build steps C1 and C2 must be re-specified: the delta is the newest `planner-L3-k.md` carrying a `revises:` header, `split` merges base plus deltas, and the reviewer's read rule changes.

2. Blocker. Whole-ticket batched verification (section 4) has no independence enforcement. The family rule reads `order.py newest "$dir" builder` where `$dir` is the verifier's own handoff dir (`run.sh:198-207`). A verifier launched at the task dir finds no builder there, so the rule never fires. Evidence: the branch verifier the design cites as its model ran in `.sdlc/verify-ticket-stages/step-1/` with only `verifier-L3.md` and no builder result; its family was unenforced. Verifier L1 and L2 are sonnet and builder L1 is sonnet (`run.sh:102,111-112`), so a batched L1 verifier of L1 builds shares the family. The validation row "a forced same-family run is refused by run.sh" is false: run.sh remaps silently and has no refusal path (no `refus` in the file; exits 2 and 3 are usage, missing handoff, missing section). Codex has the same shape: `codex_roles.resolve` reads the newest builder in the given dir (`codex_roles.py:100-120`).

3. Major. Step handoffs by reference (C2) target the wrong component. `split` writes `## Task goal`, the goal, and the step block verbatim (`steps.py:897`); it adds no plan context. In T-0181 step 1 the goal is 166 bytes and the planner-authored step block is the other 12,900 (`### Do` runs lines 8 to 94). The restatement is written by the planner inside the step, so the fix is a planner rule plus a lint, and "L3 because it changes split" is mis-sized.

4. Major. Moving `roadmap.md` and `notes.md` is not covered by "the layout change is in the code that finds the task directory". `tickets.py` hardcodes `root / 'roadmap.md'` and `root / 'notes.md'` at lines 842, 851, 1231, 1308, 1547, 1595; `ticket_dir` documents that they "stay at <root> either way" (`tickets.py:304`); the citing-file scan skips `<rel>/roadmap.md` by that path (`tickets.py:535`); `onboard.py:252` prints `.sdlc/roadmap.md` inside the managed AGENTS.md block, so every consumer's managed template gets a version bump; `tickets.py roadmap` also regenerates `.sdlc/messages/AGENTS.md` (`messages.py:210`). Ten files outside the plugin cite `.sdlc/roadmap.md`, including the repository root `AGENTS.md`. Answer to open question 3 is yes.

5. Major. "The mandatory list matches `steps.py review` exactly" is incomplete. Review also requires a review when `handoff.md` holds a `## Plan review` line (`steps.py:1239-1242`) and stops on an `unresolved:` assumption (`steps.py:1227-1229`). Every swap, widen and replan appends `## Plan review` (chain 4.2, 4.8, 4.9), so a lean ticket flips to review-required mid-run. "No replan" is also a lean condition that cannot be known at plan time. `steps.py lane` needs a defined decision point and a re-evaluation rule, or it will disagree with `review` on the second call.

6. Major. `tickets.py close --reason` is documented as "for a ticket whose work other tickets did: it skips the filer (no filer needed, warnings and follow-ups ignored)" (`tickets.py:83-85`). Nothing in `close` reads builder or verifier notes, so "unless the builder or verifier reported follow-ups or warnings, then the filer runs" is prose with no gate. Either the filer always runs on the lean lane (sonnet medium, one run, about 2 KB) or the `skips.md` check must read the verifier result's follow-ups.

7. Major. The `Files:` overlap check cannot run when fanout launches. Lanes run `/chain` on the ticket handoff (`fanout.py:432`) and plan inside the lane, so at launch no plan exists. The planner already lists files in each step's scope criterion (planner rules 6 and 35), so a second `Files:` line duplicates a fact, against principle 2. Derive overlap from scope criteria of planned tickets, or check at merge time from `git diff --name-only`.

8. Major. Ticket cut. C1 and C2 both edit `steps.py split` (two writers, one file). C3 changes five role contracts and needs `codex_roles.py generate` plus a focused live run; by the design's own mandatory list it is full-chain work, not L2. D1 and D2 both edit `tickets.py` ticket-root code.

9. Minor. The target layout lists `evals/ proposals/ supervisor/` from T-0183 to T-0187, which are open tickets (`.sdlc/0183-*` to `0187-*` are proposed), and omits `runtime/` and `dogfood/` which are git-ignored today (`.gitignore:9,12`). `messages/` is the ignored mailbox (`.gitignore:13`).

10. Minor. "Refuses when ticket ids clash across worktrees" is not a migrate precondition: each worktree's ticket root is resolved by its own config (`tickets.py:122-129`), so a migrated tree next to a flat one keeps ids unique; `check` catches a clash after merge. `check.py:330` pins the literal `.sdlc/<slug>/step-1/handoff.md` in the fix skill and will need the resolved form.

11. Minor. Codex parity: the Codex host skill `skills/sdlc-lite/SKILL.md` has zero `steps.py` mentions, so `steps.py lane` reaches Codex only if that skill is changed; the design lists no Codex skill change.

12. Minor. Lint of a dangling anchor on a step handoff needs a resolution rule: `lint` today takes a plan or a task dir, and a step handoff carries no plan reference.

Verified as stated: every Baseline number (files 8/8/51/69, bytes 8,010/10,050/214,502/224,330, `.md` 4,521/6,586/185,323/187,209, role runs 2/2/15/21 with the stated role mix, planner sizes 22,152/33,296/50,094, step-1 handoff 13,079 vs ticket handoff 8,333, builder 2,073 and verifier 3,931), 70,671 contract bytes, 38 citing files, no hook names `.sdlc` (`grep -rl` over `hooks/` is empty), `fanout.py` has no `ticket_root` (`grep` empty; `notes.md:145`), `board.py:213`, `traces/ingest.py:68` and `traces/sources/tickets.py:20` resolve through `tickets.ticket_dir`, `steps.py:103` carries the L3/L4-L5/merge/replan rule, planner rule 14 is the `gates green` step.

The decomposition (`.sdlc/lean-sdlc-review/decompose/manifest-v1.json`, 21 leaves, 30 actions, coverage clean in strict mode) re-cuts the build so that each file has one writer and the two unhosted needs above have homes: a `batch-verify` leaf that extends run.sh's family rule to read every `step-*/` builder when the verifier runs at the task dir, and a `layout-resolver` leaf that owns roadmap and notes paths. The handoff's Context line was not added because the review forbids editing other files.

Decisions still needed from the user: whether batched verification may ship before the run.sh family rule is extended, or is pinned to verifier L3; whether the lean lane always runs the filer or gets a new close gate; whether roadmap.md and notes.md move at all given the ten outside cites and the managed template bump; and open questions 1, 4 and 5 as written.

## Interfaces

- `plugins/sdlc-lite/scripts/steps.py lane <task dir>`: new; stdout `fix|lean|full`, `reason:` lines, `read:` lines; must restate when it is re-run (after `## Plan review` appears).
- `plugins/sdlc-lite/scripts/steps.py split`: merges the newest `planner-L*.md` carrying `revises: <planner file>` with its base; refuses a delta naming a missing step with a `plan defect:` last line; new `steps.py resolve <task dir>` prints the merged plan. Result file names unchanged.
- `plugins/sdlc-lite/agents/plan-reviewer.md:10`: read rule gains "and the file its `revises:` line names".
- `plugins/sdlc-lite/scripts/run.sh:198-207`: family rule reads the newest builder of every `step-*/` under the handoff dir when the handoff dir holds no builder, so a task-dir verifier is guarded; `run-selftest.sh` case plus negative control.
- `plugins/sdlc-lite/scripts/tickets.py`: `layout: topics|flat` config key beside `ticket_root`; one function returning ticket dir, roadmap path, notes path; `migrate-layout [--dry-run] [--rewrite-refs]`; `check` guards for entry files and strays; `skips.md` guard on closed lean and fix tickets.
- `plugins/sdlc-lite/scripts/fanout.py`: lane ticket paths through `tickets.ticket_dir` (`fanout.py:432,508-510,668,678,736,746`).
- `plugins/sdlc-lite/scripts/footprint.py`: new; prints files, bytes, md bytes, role runs for a ticket dir; selftest.
- `plugins/sdlc-lite/agents/{scout,researcher,archaeologist,architect}.md`: `## Carry forward` section; `codex_roles.py generate` afterwards.
- `plugins/sdlc-lite/skills/{chain,fix}/SKILL.md`, `agents/conductor.md`, `agents/planner.md`: lane call, coarse-step rule, anchor-citing rule, batched-verification conditions.
- `plugins/sdlc-lite/scripts/onboard.py`: managed template prints resolved roadmap path; template version bump.
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: Codex host calls `steps.py lane`.

## Constraints and assumptions

- run.sh fixes result names and required sections, so a planner cannot emit `plan.md`: verified by `run.sh:17-21,186-191`.
- A replan is detected by counting `planner-*.md` files: verified by `steps.py:1237` and `order.py:22`.
- The verifier family rule only sees a builder in the verifier's own dir: verified by `run.sh:198-207` and the builder-less `.sdlc/verify-ticket-stages/step-1/`.
- run.sh never refuses a same-family run: verified by grep for `refus` and the exit paths at `run.sh:98,99,136,138,139,226,261,485`.
- `split` adds only the goal to a step block: verified by `steps.py:897` and the T-0181 step-1 byte split (166 goal, rest step block).
- roadmap and notes paths are hardcoded at the root: verified by `tickets.py:304,535,842,851,1231,1308,1547,1595`.
- `close --reason` skips every filer gate: verified by `tickets.py:83-85,1252`.
- Fanout lanes plan inside the lane, so no plan exists at launch: verified by `fanout.py:432` and chain section 3.
- Baseline numbers: verified by `find`, `stat` and `runs.jsonl` counts on `.sdlc/.0188-*`, `.0164-*`, `.0181-*`, `.0175-*`.
- 38 citing files, no hook cites, 70,671 contract bytes: verified by `grep -rl` and `wc -c`.
- Codex host skill does not call `steps.py`: verified by `grep -c steps.py skills/sdlc-lite/SKILL.md` = 0.
- The other repo's four complaints are fully stated by the ticket handoffs: unverified (only the pasted sentences exist).
- Lean thresholds (two steps, 12 criteria) are right for consumers: unverified; no fixture measured yet.

## Rejected alternatives

- Keep `plan.md` as a planner output and teach run.sh a per-role file name: touches run.sh, order.py, steps.py, the plan-reviewer, traces and board for a naming preference; the `revises:` header inside the existing naming gives the same delta with none of that.
- Enforce batched-verification independence by conductor prose only: the rule the design relies on is a script rule (T-0005 user decision), and the cited branch verifier shows prose did not apply it.
- Drop batched verification entirely: the fast lane already proves one verifier per ticket is sound when the family rule holds; fixing run.sh is smaller than the batching benefit lost.
- Leave roadmap.md and notes.md at the root (as `ticket_dir` already assumes): a legitimate option that removes finding 4 and the template bump, but it contradicts the stated goal that the root holds only entry files; left as the user's decision.
- A `Files:` line in the plan for overlap: duplicates the scope criterion and is unavailable at fanout launch; derive from scope criteria or merge-time diffs.
- One ticket per design section as the build order: C1 plus C2 and D1 plus D2 each put two writers on one file; the manifest re-cuts by owning file.

## Risks

- If the user rules that `.sdlc/` artifacts need not stay compatible with existing trails, the delta-plan design could instead change run.sh naming, and findings 1 and 3 would be re-scoped rather than fixed.
- If batched verification is restricted to verifier L3 (fable), independence holds by the current level table alone and finding 2 reduces to a documentation gap; any later change to the table silently breaks it.
- The lane script depends on facts (step levels, merge steps) that exist only after planning; if the user wants the lane decided before the planner runs, `lane` must work from ticket front matter alone and the lean conditions shrink to size and owner.
- The migration path assumes consumers keep `.sdlc/` committed; a repo with an ignored `.sdlc/` has no citing files to rewrite and the dirty-tree refusal may block on unrelated changes.
- Footprint targets (14 files, 60 KB) are unmeasured; if a fixture lean ticket lands above them, the targets rather than the design are what move.
