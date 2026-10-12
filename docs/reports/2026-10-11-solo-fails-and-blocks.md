# Solo first-round fails and builder blocks, 2026-10-08 to 2026-10-11

Recorded: 2026-10-11, for T-0450. Repos: ui-kit-maison, agent-ui, ultimate-tokens and sdlc-lite (main checkout). Read-only against every inspected repo. Outcome measure: K-005 (`docs/kpi/005-solo-first-pass-rate.md`, baseline from `docs/reports/2026-10-11-solo-campaign-baseline.md`): 89 of 123 first-pass (72 percent), target 85 percent or more.

Result in one line: of 34 first-round non-passes, 22 are builder gaps, 9 are criterion defects, 2 are environment, 1 is other and 0 are verifier over-reach. Two solo.md rules would have reached 13 of the 34. Builder blocked notes are mostly the designed outcome: the plan defects they name are already covered by planner rules that shipped earlier.

## Sample

Sample size: 34 first-round verifier non-passes (all of them) and 20 of the 39 builder blocked notes in the window (a stratified read, k = 2).

How it was drawn: `.sdlc/.0450-review-traces-solo-fails-and-blocks/sample.py` (rerun it from the repo root; its output is kept beside it as `sample.txt`). It reuses `solo_stats.py` and `fleet_collect.py`, so it follows the baseline method:
- A solo ticket has a `solo` row in a `runs.jsonl` inside the window, at or after 2026-10-08 and up to 2026-10-11T20:00:00Z. That `--until` instant is the one that reproduces the baseline counts.
- Only each repo's main checkout `.sdlc` is read, worktree copies are left out, hidden closed `.NNNN-*` folders are read, and ui-kit-maison's `ticket_root: tickets` layout is honoured.
- Verifier rounds are ordered by round number, then level (`verifier-L2.md`, `-2`, `-3`), never by name.
- First-round non-pass: the first verifier file's verdict is not `pass`. All 34 later passed (20) or closed (14), so the "later passed or closed" filter removes none. The script prints 166 solo tickets and 123 verified, matching the baseline, and 34 non-passes, matching the baseline's 123 minus 89.
- Builder blocked note: a `builder-L<n>[-<k>].md` anywhere in a ticket folder (step and superseded step folders included) whose `## Status` starts with `blocked`, in a ticket folder with a `builder` row inside the window. It is tagged mechanically by its lines: `plan defect:`, `stale lane:`, `inherited red`, else other.
- Read sample: per repo, the blocked notes in sorted path order, every 2nd one (index 0, 2, 4 and so on). Per repo: ui-kit-maison 29 notes, 15 read; agent-ui 2 notes, 1 read; ultimate-tokens 8 notes, 4 read; sdlc-lite 0 notes, 0 read.

Count differences:
- Builder blocked notes. The handoff counted 173 notes, 55 of them naming a plan defect. That is every blocked note on disk, with no window. The same script with `--since 2000-01-01 --until none` prints 174 notes (56 plan defect, 11 inherited red, 4 stale lane, 103 other). The one extra note was written after the count. Inside the window there are 39 notes (16 plan defect, 3 stale lane, 20 other). That matches the handoff's per-repo context: maison 29, ultimate-tokens 8, agent-ui 2.
- Non-passes. With no `--until`, the script prints 175 solo tickets and 128 verified, and still 34 first-round non-passes.

Commands run, all from this tree:
- `python3 plugins/sdlc-lite/scripts/traces.py ingest <repo>`, then `traces.py detect --repo <repo>`, then `traces.py clusters --max 5 --repo <repo>`, for each of the four repos. All exited 0. Output went to the gitignored `.sdlc/runtime/traces/<repo-key>`, and the stdout copies are in `.sdlc/.0450-review-traces-solo-fails-and-blocks/scratch/`. No `--rerun-criteria` was passed.
- `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --since 2026-10-08` for each repo, with stdout kept in the same scratch folder.
- `python3 .sdlc/.0450-review-traces-solo-fails-and-blocks/sample.py`, and the same with `--since 2000-01-01 --until none` for the all-time count.

Each non-pass was read through its `## Verdict`, the failing lines of `## Criteria`, and `## For the next attempt`. Each sampled blocked note was read through its `## Notes`. Ticket minutes and priced dollars are summed over every role's rows in the ticket's `runs.jsonl` inside the window. The collector records durations for sdlc-lite and ui-kit-maison only, and prices sdlc-lite solo runs only (K-001), so minutes and dollars are a floor, and outside sdlc-lite they are mostly 0.

Cross-check with the detect clusters: `agents/planner.md` is a severity-3 cluster in all four repos (maison 69, sdlc-lite 47, agent-ui 12, ultimate-tokens 10). The `plan-defect-refusal` detector counts maison 39, sdlc-lite 39, ultimate-tokens 8 and agent-ui 7. That agrees with plan defects being the largest tagged block cause. No cluster names `agents/solo.md`: the detectors read run rows, not verifier text, so the solo causes below come from reading the verifier files.

## Classified counts

First-round non-passes (34), one category each:

| Category | Sub-cause | Count | Minutes | Priced $ |
|---|---|---|---|---|
| builder gap | missed a contract dependent or sibling site | 6 | 108 | 7.62 |
| builder gap | exact criterion span or repo gate not run before done | 4 | 73 | 5.36 |
| builder gap | Do item or deliverable left incomplete | 4 | 11 | 4.52 |
| builder gap | defect found only by the verifier's own probe | 4 | 144 | 15.70 |
| builder gap | bulk mechanical rewrite broke tables and meaning | 3 | 0 | 0 |
| builder gap | scope widened (src edits beyond the decision) | 1 | 76 | 0 |
| criterion defect | lane-unsatisfiable row (integration-owned regeneration or full gate) or circular | 4 | 0 | 0 |
| criterion defect | command can never pass on the host (padded `wc -l`, selftest prints only misses) | 2 | 196 | 28.28 |
| criterion defect | handoff template unfilled or targets an unmerged branch | 2 | 0 | 0 |
| criterion defect | needs a live run | 1 | 0 | 2.26 |
| environment | stale base, inherited red | 2 | 0 | 0 |
| other | plan scope left out a contract dependent | 1 | 0 | 0 |
| verifier over-reach | none found | 0 | 0 | 0 |

Totals: builder gap 22, criterion defect 9, environment 2, other 1, verifier over-reach 0.

No verifier over-reach was found. The closest cases still fail on a checkable fact, so they stay builder gaps:
- 0446 fails on a count that disagrees with its own list ("items 6 to 8" over a 7-item list).
- 0216 fails on missing follow-up owners in the item map.

Ticket assignments (verifier file under `## Ranked changes` where a change uses it):
- builder gap, dependent or sibling site: maison 0274, 0275, 0318; ultimate-tokens ui-polish-controls; sdlc-lite 0368, 0373.
- builder gap, criterion span not run: maison 0286; ultimate-tokens peer-luminosity-diagnose; sdlc-lite 0372, 0378.
- builder gap, incomplete deliverable: maison 0216, 0321, 0446; sdlc-lite 0410.
- builder gap, probe-found defect: maison 0323, 0366; sdlc-lite 0381, 0426.
- builder gap, bulk rewrite: agent-ui skills-em-dash-1, -2, -3.
- builder gap, scope widened: maison 0138.
- criterion defect: maison 0154, 0221, 0317, 0319 (lane-unsatisfiable or circular); sdlc-lite 0356, 0398 (never passes); maison 0329, 0331 (unfilled handoff); sdlc-lite 0438 (live run).
- environment: maison 0324 (stale base: the schema change T-0307 was not in the lane), maison 0233 (inherited red, same failures at base).
- other: maison 0333 (a contract dependent outside the plan's scope).

Builder blocked notes, read sample of 20, one class each:

| Class | Count | Notes |
|---|---|---|
| plan defect | 8 | 4 scope left out a needed file or dependent, 2 criterion contradicts the Do or the step base, 2 red criterion already green or stale against the step base |
| environment | 4 | 2 resource or browser admission withheld, 1 stale lane, 1 waiting on another owner's receipts |
| other | 8 | owner questions, cross-lane red after an integration merge, partial repairs, an upstream generator defect |

The mechanical tags over all 39 window notes give plan defect 16, stale lane 3 and other 20. The read sample moves 0351 (stale lane) and 0375 into environment.

## Ranked changes

Ranked by count, then by minutes. Each change names the agent file and rule, the smallest wording, and a measure. The K-005 movements are upper bounds: they assume the change turns each named first round into a pass [U].

### 1. solo.md: search contract dependents and sibling sites before the change (7 tickets, 108 minutes, $7.62 priced)

Cause: the change renamed, removed or added a shared name and left a consumer stale. The verifier found the consumer with `git grep` (verifier rule 2); solo has no matching rule. Six builder gaps:
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0274-component-switchgroup/verifier-L2.md`: the rule names `maison/switch`, which is not in the contract's `dependencies`, and `lib.mjs:282` rejects it.
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0318-component-app-header/verifier-L2.md`: the same validator, `maison/heading` missing from Row's `dependencies`.
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0275-e1-burn-down/verifier-L2.md`: a removed `#theme-status` id is still read by `examples/navigation/page.js:184`.
- `~/Projects/nonoun/ultimate-tokens/.sdlc/ui-polish-controls/verifier-L2.md`: one select site (the inspector example) missed, and the smoke probe excluded it.
- `~/Projects/nonoun/sdlc-lite/.sdlc/.0368-prune-flag/verifier-L2.md`: two launcher skills miss the new `dispatch.py prune` line.
- `~/Projects/nonoun/sdlc-lite/.sdlc/.0373-codex-role-preflight/verifier-L2.md`: `solo.md` and `skills/agent/SKILL.md` lack the routing pointer.

One "other" with the same mechanism: `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0333-intent-serializer-ships-in-tar/verifier-L3.md` (the moved serializer breaks `verification-cycle/run.mjs` fallback, outside scope).

Rule: `plugins/sdlc-lite/agents/solo.md` `## Loop` step 2. Smallest wording, after "Touch no file outside the ticket's scope.": "When the change adds, renames or removes a shared name (a contract id or dependency, a schema key, an element id, a selftest label, a command line other files repeat), `git grep` it first and fix or name each dependent it can break; a dependent outside the ticket's scope is reported as `blocked: plan defect: scope misses <path>`." This is the solo form of the planner's `## Contract dependents` (T-0149).

Measure: K-005 up to 96 of 123 (78 percent) [U]. Changes 1 and 2 together reach 13 of the 34 [U]. Status: propose a ticket.

### 2. solo.md: run every acceptance criterion verbatim before `verify: needed` (6 tickets, 269 minutes, $33.64 priced)

Cause: solo reported done while a criterion span, or the repo gate the handoff names, was red on the built tree. Either solo never ran it, or it ran a paraphrase. Four are builder gaps:
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0286-lane-ledger-and-spend/verifier-L2.md`: the em dash guard fails on a literal em dash at `scripts/lane-ledger.mjs:505`.
- `~/Projects/nonoun/ultimate-tokens/.sdlc/peer-luminosity-diagnose/verifier-L2.md`: `npm test` fails on the citation gate, 3 stale citation lines in the new report.
- `~/Projects/nonoun/sdlc-lite/.sdlc/.0378-red-checkpoint-builder/verifier-L2.md`: the exact criterion span exits 1. Two selftest labels carry a `control: ` prefix the criterion does not.
- `~/Projects/nonoun/sdlc-lite/.sdlc/.0372-codex-solo-native-transport/verifier-L2.md`: the documented `solo_run.py` invocation is not runnable as written.

Two are criterion defects that the same run would have exposed before the verifier round:
- `~/Projects/nonoun/sdlc-lite/.sdlc/.0356-verifier-routing-by-level/verifier-L3.md`: on macOS `wc -l` pads its count, so `grep -qx 4` never matches.
- `~/Projects/nonoun/sdlc-lite/.sdlc/.0398-fanout-stale-verifier-result/verifier-L2.md`: the selftest prints only misses, so no output can hold the required ok lines.

Rule: `plugins/sdlc-lite/agents/solo.md` `## Loop` step 3 ("Run every check command") and `## Verification` (L2 and L3). Smallest wording, appended to Loop step 3: "Before `verify: needed`, run each `## Acceptance criteria` and Done-when command span exactly as written, the same text and not a paraphrase, and list each with its exit code in the report. A span that cannot exit 0 on a correct tree (a padded count, output that never prints) is a criterion defect: report `blocked: plan defect: <criterion> <why>` instead of `verify: needed`."

Measure: K-005 up to 95 of 123 (77 percent) on the baseline window [U]. Detect rule: a solo report with `verify: needed` that lacks one exit-code line per acceptance criterion span. Status: propose a ticket.

### 3. solo.md: mark lane-unsatisfiable criteria with an owner (4 tickets, 0 recorded minutes)

Cause: the ticket held rows that no lane can pass, such as the hash-bound regeneration, `npm run check` after it, and the testing-repo entry. So the first round failed as a plan defect instead of holding them:
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0319-component-avatar/verifier-L2.md`: the verifier says rows 7 to 12 "cannot pass in a lane build".
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0317-component-alert-banner/verifier-L2.md`: "what remains is integration and probe work".
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0221-rca-m6/verifier-L2.md`: AC3 red because the regeneration was not run, "or record AC3 as owned by that step".
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0154-wire-standalone-scripts-and-regenerate-once/verifier-L3-4.md`: criterion 2 is circular against the adoption review.

Rule: `plugins/sdlc-lite/agents/solo.md` `## Verification`, where solo writes `## Acceptance criteria` when the handoff has none. Smallest wording: "A criterion your lane cannot run (a regeneration or gate owned by the integration step, an entry in another repository) ends with `[owner: <stage>]`, so the verifier holds it as `deferred` instead of failing it." `verifier.md` rule 7 already reads that bracket (T-0408).

Measure: K-005 does not move, because a held criterion still gives Verdict `fail`. Measure instead the first-round fails whose `## For the next attempt` starts with `plan defect:` on a regeneration or full-gate row, against those starting with `deferred:`. On the baseline window that is 4 plan defects against 0 deferred [U for the 0]. Status: propose a ticket.

### 4. solo.md: review a bulk rewrite per hunk in tables, fences and descriptions (3 tickets, agent-ui)

Cause: a scripted em dash replacement turned table placeholder cells into `,`, changed code fences, and shifted description meaning:
- `~/Projects/nonoun/agent-ui/.sdlc/skills-em-dash-1/verifier-L2.md`
- `~/Projects/nonoun/agent-ui/.sdlc/skills-em-dash-2/verifier-L2.md`
- `~/Projects/nonoun/agent-ui/.sdlc/skills-em-dash-3/verifier-L2.md`

Rule: `agents/solo.md` Loop step 3. One sentence: "A bulk scripted rewrite is read hunk by hunk where it touches a table cell, a code fence or a front matter description before you report." All three are one repo and one task series, so this ranks below the cap. Measure: K-005 up to 92 of 123 [U].

### 5. Builder blocked notes: no new wording; the plan defects they name are covered (16 of 39 window notes tagged plan defect)

Read sample, plan defect class:
- Scope left out a needed file or dependent:
  - `~/Projects/nonoun/ultimate-tokens/.sdlc/native-dom-charts/step-2/builder-L3.md` (the scope excludes `scripts/bundle.mjs`, which the gate runs)
  - `~/Projects/nonoun/ultimate-tokens/.sdlc/geometry-maison-ladder/step-13.superseded-1/builder-L3.md` (a citation gate red at base outside the step's files)
  - `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0307-native-element-discovery-contracts/step-1/builder-L3.md`
  - `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0378-integration-wave-3/step-2/builder-L4.md` (a full gate inside an allowlist)
- Criterion contradicts the Do:
  - `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0152-manifest-driven-renderers/step-3.superseded-1/builder-L3.md`
  - `~/Projects/nonoun/ultimate-tokens/.sdlc/match-peer-lightness/step-2.superseded-1/builder-L5.md`
- Red criterion already green or stale against the step base:
  - `~/Projects/nonoun/agent-ui/.sdlc/response-type-selection/step-10/builder-L2.md`
  - `~/Projects/nonoun/ultimate-tokens/.sdlc/geometry-compound-insets/step-4.superseded-1/builder-L3.md`

Each class maps to a `plugins/sdlc-lite/agents/planner.md` rule already in place:
- `## Contract dependents` (T-0149) pulls dependents into scope.
- Rule 14 keeps whole gates on the final step.
- Rule 11 with `specgate.py red` refuses a `(red)` span green at base.
- Rule 1 runs each criterion at plan time.

The block is the designed exit: the builder stops before a wrong build. The environment and other classes are mostly ui-kit-maison's own admission and owner-question policy:
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/0349-gen-ui-host-bindings/step-2/builder-L4.md`
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/0399-nextwave-preview/step-3/builder-L3.md`
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/0351-gen-ui-element-traceability/schema-replan/step-4/builder-L4.md`

Those classes are not an sdlc-lite agent rule. Whether the blocked runs used a plugin version that already held these planner rules is [U].

Measure: the `plan-defect-refusal` detector count per repo per window (now maison 39, sdlc-lite 39, ultimate-tokens 8, agent-ui 7, all with a last-seen date of 2026-10-08 or later), and K-003 (blocked builders per wave). No change is ranked here.

### Not ranked

These have no single agent rule that would have prevented them; the verifier caught them as designed:
- Probe-found defects (4): `~/Projects/nonoun/sdlc-lite/.sdlc/0381-runner-wrong-lane-base/verifier-L2.md`, `~/Projects/nonoun/sdlc-lite/.sdlc/.0426-record-removes-tmp-prefix/verifier-L2.md`, `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0323-component-file-dropzone/verifier-L2.md`, `~/Projects/maison/ui-kit-maison/.sdlc/tickets/0366-table-expansion-header-text/verifier-L2.md`.
- Incomplete deliverables (4): 0216, 0321, 0446, 0410.
- Scope widened (1): 0138.

Two more criterion defect cases are not ranked:
- `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0329-example-preview-hygiene/verifier-L2.md` and `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0331-form-adapter-test-hardening/verifier-L2.md` are unfilled handoff templates. `solo.md` `## Brief` already says a missing done criterion means `blocked:`. A one-line addition ("a Goal or Done when that still holds template placeholder text counts as missing") would reach 2 tickets.
- `~/Projects/nonoun/sdlc-lite/.sdlc/.0438-executor-live-run-fixes/verifier-L2.md` (a rehearsal as a verifier criterion) is covered by T-0439.

## Already covered

- T-0412 (`record` leaves the attempt running when no result file exists yet): covers the `no-verdict-verifier` and early-record pattern (1 sdlc-lite finding). It touches none of the 34 non-pass causes.
- T-0413 (`prepare --tree` names the lane worktree as Tree and base): covers the wrong-base environment class. An example is the dispatch `base-sha` pointing at candidate-8, noted in the 0286 verifier file, which produced a spurious scope red. Whether the maison lanes went through `prepare --tree` is [U]. The stale-base case 0324 (a schema change not yet in the lane) is a dependency order question that T-0413 does not cover.
- T-0438 (plan-doc executor live-run gaps): its own first round is one of the 34. Its Done-when asked for a rehearsal run, a "needs a live run" criterion.
- T-0439 (land carries the verifier record): it moved the rehearsal out of the verifier's criteria ("a separate rehearsal plan run is the maintainer's live check, not a verifier criterion"). That covers the needs-a-live-run class for this pattern.
- T-0441 (per-level overlays, builder L1 and L5): gives builder L1 an ordered procedure and gap defaults. It covers neither solo (overlays for other roles are T-0443, proposed) nor the builder L2 to L4 blocks in the sample. None of the four ranked solo changes is covered by it.
- T-0448 (clarify v2): makes each Done when runnable or `unverifiable: <why>` and lints the clarify output. That covers the unfilled-template class (0329, 0331) and the needs-a-live-run class when a ticket passes through clarify. It does not make solo run each criterion (change 2) or catch a host-specific command such as a padded `wc -l` (0356).
- Also already in place, outside the six named tickets:
  - `verifier.md` rule 7 (T-0408, 2026-10-09) holds `[owner: ...]` criteria as `deferred`, which is why change 3 is solo-side only.
  - `planner.md` `## Contract dependents` (T-0149) covers the planner side of change 1.
  - `solo.md` Loop step 2 runs `specgate.py red` before the first edit, which covers a `(red)` criterion green at base.

## Unverified

- Stages 2 to 4 of review-traces (diagnose, verify, propose) ran inside this builder, not as separate archaeologist, verifier or planner dispatches, to keep the ticket within its $10 budget. The ticket's one independent verifier samples the evidence pointers above. Every classification is one reader's judgment.
- Each verifier file was read through its fail lines and `## For the next attempt`, not in full. Tickets with more than one failing row were given the category of the row the verifier led with [U].
- Whether solo or the conductor wrote the defective criteria in 0356 and 0398 is [U]. Change 2 helps either way, because solo runs the span before the verifier round.
- The K-005 movements in changes 1, 2 and 4 are upper bounds, not observed effects [U]. Whether 0 of the 34 first rounds used `deferred:` is from the 34 files read, not from a detector [U].
- Minutes and dollars are floors. Outside sdlc-lite most ticket rows carry no duration or price (K-001). The cost of this builder run itself was not measured.
- The detect findings are not windowed by the detectors. The cluster cross-check uses them as recorded.
- Whether the ui-kit-maison, agent-ui and ultimate-tokens runs used plugin versions that already held the rules listed under `## Already covered` is [U].
