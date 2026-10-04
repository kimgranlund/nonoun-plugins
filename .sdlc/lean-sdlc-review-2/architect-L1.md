<!-- role=architect level=L1 model=fable effort=high -->
## Approach

Verdict: ready after fixes. v0.2 and v0.3 resolve nine of the twelve first-review findings and partly resolve three (1, 2, 5, plus the build order in 8). No finding needs a new user decision; every fix below is author work on the design text. Four tickets can be filed today from the current table (A0, B, C3, D0); the rest wait for the fixes because their scope lines are wrong as written. The design is read against the plugin tree at a7c5685, identical to main for `plugins/` (`git diff main --stat -- plugins/` is empty). The decomposition (`.sdlc/lean-sdlc-review-2/decompose/manifest-v1.json`, 17 leaves, 33 actions, coverage clean in strict mode) is the re-cut build order; its report names the quadrant: unhosted actions.

Status of the twelve. 1 partly (names fixed; `lint`, `review`, `lane` not routed through the merge, finding 1). 2 partly (family rule fixed by row V; the chain cannot consume a batched verdict, finding 3). 3 resolved. 4 resolved as a decision; implementation gaps are findings 5, 6, 7. 5 partly (the shared function does not exist yet and the pre-plan facts are thinner than stated, finding 8). 6 resolved (decision 2). 7 resolved. 8 partly (file ownership still overlaps, finding 4). 9 resolved. 10 resolved; `check.py:330` needs no code change, `fix_lint_bad` matches the suffix `/step-1/handoff.md` only (check.py:326-327), so only its message string names the flat path. 11 resolved. 12 resolved.

New findings, numbered, severity, evidence.

1. major. The delta mechanism covers `split` and `resolve` only, but every dir-target reader picks the newest planner file alone: `find_plan` (steps.py:236-243) feeds `cmd_lint` (913-916), and `review_action` reads `plan_facts(plans[-1])` (1223-1226). After a delta, `lint` lints only the changed steps, and `review` cannot see a base `unresolved:` assumption or a base step at L4 (1227-1233); `lane`, which the design says calls the same function, inherits the blindness. Fix: C1 adds a merged view that `find_plan` returns for a dir target, used by split, lint, review, lane, and resolve.

2. major. "A replan is the next `planner-L<n>-<k>.md`" is false for the normal replan. run.sh suffixes `-k` only when the same role and level reruns (run.sh:187-192); the chain replans at planner L3 (chain SKILL.md:35, 49), and `review` routes replan to L3 (steps.py:1263). An L2 plan's first replan is `planner-L3.md`. `revises:` must be allowed across levels, and the "delta at most a quarter" target must hold for an L3 delta. Also `steps.py split` without `--only` refuses when `step-1/` already holds results (863-889), so the lean chain text must say the replan split is `--only <changed steps>` after the supersede rename, as 4.2 does today.

3. major. Batched verification has no step-state mechanics. `next` and `resume` read `step-<n>/` only (steps.py:1016-1053, 1123-1145); board renders per step (board.py:104-137); `counts_after` compares line ranks inside one `runs.jsonl` (order.py:103-110) and run.sh writes `runs.jsonl` per handoff dir (run.sh:470). A verifier launched at the task dir is invisible: `resume` prints `verify` for every step and the chain re-verifies each one, so the batching rule saves nothing and a rebuild after the batch is never detected. Row V fixes the family rule only. Fix: a `steps.py` rule (a task-dir verifier result lists the builder result files it verified; `next` treats a listed, unchanged step as verified) in the V or A1 ticket, and resolved decision 1 reads "after row V and that rule".

4. major. File ownership still overlaps and one guard sits in the wrong file. `steps.py` is written by A1, B, C1, C2; `agents/planner.md` by B, C2, C3; `fanout.py` by D0 and by section 4 Parallelize, which has no build row at all (the overlap check at launch and at merge is unhosted). "The `check.py` guard" for `skips.md` cannot live in `check.py`, which checks plugin contracts (check.py:1-40); a closed consumer ticket is checked by `tickets.py check` (1508-1514) and `close` (1300), so A1 writes `tickets.py`, D1's file. The guard must also exempt tickets closed before the feature (every existing `/fix` ticket has no `skips.md`), or `check` goes red on upgrade.

5. major. `layout: topics` as an implicit `ticket_root: tickets` breaks id uniqueness. Other worktrees and external branches are resolved by their own config through `ticket_dir` (tickets.py:375-385) and `branch_tickets` reads the branch's config blob for the `ticket_root` line (388-420); board.py:213, traces/ingest.py:68, traces/sources/tickets.py:20 read `ticket_root` too. A migrated tree that writes only `layout: topics` is seen as flat by every other tree. Fix: `migrate-layout` writes both lines and `layout` governs only roadmap, notes, `work/`, and strays.

6. major. The onboard template bump contradicts decision 5. `TEMPLATE_VERSION` (onboard.py:219) is part of the start marker; a bump makes every existing consumer's block row 6 `stale` (581-582), which `--check` reports and a rerun replaces (684). "Existing repos are untouched until they migrate" does not hold. Fix: render the block text from the repo's resolved paths without a bump for flat repos, or state the upgrade cost in the transition section.

7. minor. Path residue the change table misses: `traces/sources/tickets.py:28` hardcodes `root / 'notes.md'`; the router template names `roadmap.md` and `notes.md` at root (tickets.py:894); `write_roadmap` also regenerates `messages/AGENTS.md` (842-846) so D1 owns that text. Migration step 3 reuses the citing-file scan "for every moved folder", but `outside_refs` scans for folder literals `<rel>/<slug>` (510-535); the two file moves need their own cite scan, and the ten outside citers include five dated `docs/validation/` records that AGENTS.md says not to rewrite. Name which files are rewritten.

8. minor. `lane` facts. Front matter has `size` and no owner or subsystem field (tickets.py:185-190), so decision point 1 can use size only; "files touched" after the plan must come from the scope criterion's allow-list, parsed with the forms `widen` already recognizes (steps.py:1460-1485). `review_action` inlines its reasons (1230-1242) and returns an action; A1 must extract a `review_required()` function and keep selftest (r) at 2647 green. Order A1 before B leaves `lane` printing `lean` with no lean lane in the chain; B goes first.

9. minor. Every swap and widen appends to `## Plan review` (chain SKILL.md:45, 55, 56) and any `## Plan review` heading makes review required (steps.py:1239-1242), so a lean ticket flips to full on its first swap. Consistent with the design's rule, but the footprint target should be measured on a fixture that swaps once.

10. minor. Validation plan. "A fixture that writes extra files fails the target check" names a check no row builds (A0 is measurement only). "A ticket that changes `steps.py` is routed to full" is true only at decision point 2. Row V's negative control is buildable: run-selftest.sh already dry-runs the verifier family rule on a step fixture (132-147); a task-dir fixture prints `--model sonnet` today and `--model opus` after; codex-selftest resolve cases (256-262) take a directory argument, and `resolve` returns the configured model with `shared` False when no builder is found (codex_roles.py:109-120), which is the pre-fix bug. "Newest builder of every `step-*/`" should read "any step's newest builder, superseded dirs excluded".

11. minor. The plan-reviewer read rule should follow `revises:` transitively or read `steps.py resolve` output; a chain of two deltas otherwise drops the base. The `plan: 2` version line is unnecessary: key delta handling on the presence of `revises:`.

## Interfaces

Build tickets I would file, superseding T-0189 to T-0192 (owning files, plan level, depends).

- L1 `footprint` (A0): `scripts/footprint.py` and selftest. L2. No deps. File now.
- L2 `lean-lane-text` (B): `skills/chain`, `agents/planner.md` coarse-step rule, `steps.py lint` warning. L2. No deps. File now.
- L3 `runner-family-task-dir` (V): `run.sh:198-207`, `codex_roles.resolve`, run-selftest and codex-selftest cases with the pre-fix negative control. L3. No deps. File after finding 10's wording.
- L4 `batch-state` (new): `steps.py next` and `resume` rule for a task-dir verifier result naming the builder results it verified; `board.py` rendering. L3. Depends L3.
- L5 `lane` (A1a): `steps.py lane`, `review_required()` extracted from `review_action`, `skips.md` writer; Codex host skill mention. L3. Depends L2.
- L6 `skips-guard` (A1b): `tickets.py check` and `close` guard with the pre-feature exemption. L2. Depends L5.
- L7 `conductor-rules` (A1c): `agents/conductor.md`, chain batching and skip text, filer-always, AskUserQuestion for non-permitted skips; `codex_roles.py generate`. L2. Depends L4, L6.
- L8 `plan-merge` (C1): `steps.py` merged view for `find_plan` dir targets, `resolve`, cross-level `revises:`, missing-step refusal, `plan-reviewer.md` read rule. L3. Depends L5.
- L9 `anchor` (C2): planner anchor rule, `steps.py lint` anchor check. L2. Depends L8.
- L10 `carry-forward` (C3): four producing contracts, planner and builder reader rule, regenerate, focused live run. L3. No deps. File now.
- L11 `fanout-overlap` (new, from section 4 Parallelize): merge-time `git diff --name-only` overlap check in `fanout.py`. L2. No deps.
- L12 `fanout-resolver` (D0): fanout lane paths through `tickets.ticket_dir`. L2. Depends L11 (same file). File now if L11 is dropped.
- L13 `layout-resolver` (D1): `tickets.py` `layout` key, resolver for ticket dir, roadmap, notes; strays; router text; `onboard.py` for new repos without a bump for flat repos. L3. Depends L12.
- L14 `migrate-layout` (D2): including the file-cite scan for roadmap.md and notes.md and the list of rewritten citers. L3. Depends L13.
- L15 `layout-readers-docs` (D3): `board.py`, `statusline.sh`, `traces/sources/tickets.py:28`, docs and skills. L2. Depends L14.
- L16 `live-evidence`: one lean and one full ticket on Claude and Codex with footprint recorded. L2. Depends L7, L9, L15.

Changed design text: section 2.1 (replan naming and `--only` split), section 4 Batch (step-state rule and decision 1 wording), section 3 What changes (`ticket_root` stays explicit; traces notes path; router text; onboard without a bump), Build order (table above), Validation plan (finding 10).

## Constraints and assumptions

- Result names and `-k` suffixing are per role and level: verified by run.sh:187-192.
- `order.py` ranks within one dir's `runs.jsonl` and run.sh writes it per handoff dir: verified by order.py:26-42, 103-110 and run.sh:470.
- `steps.py next`, `resume`, and `board.py` read `step-<n>/` only: verified by steps.py:1016-1053, 1123-1145, board.py:80-81, 104-137.
- `review_action` reads the newest planner file only and counts two files as a replan: verified by steps.py:1220-1238; selftest (r) at 2647.
- `check.py` is the plugin contract checker, not a consumer check: verified by check.py:1-40; consumer checks are tickets.py:1508-1514.
- Cross-tree id resolution reads `ticket_root` from each tree's and branch's own config: verified by tickets.py:375-420.
- Onboard version bump marks existing blocks stale and replaces them: verified by onboard.py:219, 581-582, 684.
- The family rule's negative control is buildable with a dry run: verified by run-selftest.sh:132-147 and codex_roles.py:109-120.
- The cited branch verifier ran with no builder result in its dir: verified by `ls .sdlc/verify-ticket-stages/step-1/`.
- Ten files outside the plugin cite `.sdlc/roadmap.md` or `.sdlc/notes.md`: verified by git grep (list in the log); five are dated validation records.
- Lean thresholds and footprint targets are right for the other repo: unverified, as the first review said; `footprint.py` is still unbuilt.

## Rejected alternatives

- Keep batching as a conductor rule with `skips.md` entries for the skipped per-step verifiers: `resume` would still print `verify` for every step, so the rule would be prose against the decision core.
- Make `layout: topics` imply `ticket_root: tickets` everywhere: six readers plus the cross-branch blob parser would change; two config lines cost nothing.
- Put the skips guard in `check.py`: it never runs in a consumer repo.
- Mark the design not ready: no finding needs a user decision, and four tickets can start now.

## Risks

- The step-state rule for a batched verifier (finding 3) may grow into a larger `steps.py` change than row V; if it does, resolved decision 1 should defer batching to a later release rather than ship a half rule.
- A delta-aware merged view changes what `lint` and `review` see for every existing task with two planner files; the selftests at steps.py:2647 and the three closed tickets with two planner files in `.sdlc/` are the regression set.
- If the onboard block cannot avoid a bump, every consumer sees a stale report on upgrade and decision 5's "untouched" promise needs rewording before the tickets are filed.
