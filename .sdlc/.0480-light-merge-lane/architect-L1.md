<!-- role=architect level=L1 model=fable effort=high -->
## Approach

The maison request conflates two axes that the code keeps apart. `steps.py lane` (`plugins/sdlc-lite/scripts/steps.py:2903` `lane_action`, `:3084` `cmd_lane`) picks the execution lane, solo, lean or full, from the handoff size, the plan shape and the scope owners, and it runs before any work exists: it never sees a diff. The gate set for a merge is a property of the diff, and the diff is first known inside `merge_gate_close` (`plugins/sdlc-lite/scripts/fanout.py:1422-1424`, `lane.files` from `git diff --name-only HEAD...<ref>`), right before the gates run (`:1439`). The plugin already has a merge-time classifier driven by declared config globs: `steps.merge_class` (`steps.py:2276`) with `tickets.hash_bound_globs` (`tickets.py:448`) and `declared_hits` (`steps.py:2296`) decides `rolling` versus `integration` for `fanout.py roll`. The light merge lane is a second merge-time property of the same kind, not a new value of `steps.py lane`.

Recommendations, one per question:

(1) Lane types. No. Keep `steps.py lane` as it is. Add a merge-time gate class, `light` or `full`, computed in `fanout.py` from the merged paths against declarations in `.sdlc/config`: a lane is light when `merge_gate: light` is declared and every changed path outside the ticket root (`ctx['rel']`, the records `commit_lane_records` adds at `fanout.py:2044`) matches a declared `light_scope: <glob> [<glob>...]` line (same grammar and parser shape as `hash_bound:`, `tickets.py:271`, `:448`). Nothing is inferred from the diff alone: the owner declares the scope, the diff is checked against it, and a handoff line `merge_gate: full` forces the full set for one ticket. The maison refinement "one component folder plus registration files" is how the owner writes the globs (`src/components/*/** src/registry.ts`), not a plugin rule; a mechanical one-folder count is listed under rejected alternatives. The class is reported beside the merge class in the land report, the `land.jsonl` line (`fanout.py:2169`) and the ticket's `## Closed` note (`tickets.py:2010` appends the close text; the reason text already carries the lane kind), so an uncovered light merge is visible on the ticket.

(2) Ledger. One repo-level, append-only `<root>/gate-ledger.jsonl` beside `.sdlc/config`, committed by the cadence run with `git add -f` (the precedent for a gitignored `.sdlc/`: `fanout.py:2052`). Not `<lanes-dir>/logs/land.jsonl`: that journal is per lanes dir, gitignored, and the lanes dir is scratch that `settle` retires (`fanout.py:2310`); a ledger that bisect reads a week later must outlive it. Not per-ticket `runs.jsonl`: `budget.py:81` and `board.py:108` read it as role-run cost records, one line per attempt, and a cadence run covers many tickets whose folders have already moved to `.NNNN-` at close. One entry per cadence run: `{at, run_id, integration, from, to, gates, rc, merges: [{sha, ticket}], log}`, where `from` is the previous entry's `to` (else the integration base) and `merges` is derived from the first-parent merge commits in `from..to` whose subject is `Merge <branch>: <id>` (the format `merge_gate_close` writes at `fanout.py:1426`), so no per-ticket bookkeeping is needed. A red entry is appended too, with `rc` and the range; `fanout.py cover` then prints `git bisect start <to> <from> --first-parent`.

(3) Per-lane gate commands. Yes, but keyed by gate class, not by lane: a lane holds tickets whose diffs differ. `--gate CMD` stays the full set; a repeatable `--light-gate CMD` is the light set, selected in `merge_gate_close` when the class is light. `--gate-need [PREFIX::]RES=N` (`fanout.py:525-541`) already proves a per-gate attribute threads through all three context builders (`run` at `:845`, `land_preflight` at `:2011`, `roll` at `:2245`) and `land_command` (`:1723-1737`, the land line `prep` prints for sub-agent lanes); `--light-gate` must be added at the same four sites or a `prep`-generated land silently drops it. Two refusals: `--light-gate` with no `merge_gate: light` declared is exit 2, and a light class with no `--light-gate` given runs the full set (a merge is never ungated; the vacuous-gate refusal at `:1461` stays). `roll` ignores the light class and always runs `--gate`: it fast-forwards main (`fanout.py` docstring, roll section), and a light set there would loosen the full-gate-before-ff rule the handoff keeps.

(4) Owner step for the wave count fixture. Project-side. The plugin cannot know the fixtures, and the slot already exists: a component ticket's count criterion carries `[owner: integration]` (`steps.py:1961`, T-0408), the verifier reports `deferred integration`, T-0472 lets close accept it, and the binding is a last ticket in the wave with `depends:` on the component tickets, landed through the full set because it touches the shared file (declare that file outside `light_scope`, or let the handoff say `merge_gate: full`). Nothing new in the plugin.

Cadence, and the standing rule. The light lane changes only what runs per merge into the integration branch. The cadence gate is `fanout.py cover <integration> --gate CMD...`: under the merge lock, in the integration worktree, run the full set at the tip, append the ledger entry, commit it. The ff to main keeps its full gate because `cover` at the tip is that gate: `settle --require-covered` refuses the fast-forward unless the ledger's newest entry has `to` equal to the integration tip and `rc` 0. When to run `cover` (every N light merges, every M hours, or before each settle) is a project loop; the plugin ships the command and the refusal, not the schedule.

Pillar effect. Cost and performance up: the per-merge floor drops from the 75 to 90 minute full gate to the light set, and only the cadence runs pay the full price. Resilience down unless three things hold: merges stay `--no-ff` per ticket (`fanout.py:1426`), so `git bisect --first-parent` over a red range is linear in tickets; the ledger records the red range, since `merge_gate_close` can `reset --hard` one merge (`:1467`) but a red over N merges cannot be reset; and `settle` reads the ledger. Quality: a cross-component break lands in integration undetected until the next `cover`; the close note's `gate: light` and the ledger make it findable, and the full set still stands between integration and main.

Stays project-side: the `light_scope` globs and the `merge_gate: light` line (owner's written approval); the light gate commands; the cadence schedule; the fixture-binding ticket; the `check:adapters` and `check:renderers` gate contents (T-0470 finding 11).

Smallest first build, one ticket, size L3: "fanout.py land: a light gate class from `.sdlc/config` `light_scope` globs, `--light-gate CMD`, and `cover` with `<root>/gate-ledger.jsonl`". Red check, a `fanout.py selftest` case: config `merge_gate: light` and `light_scope: src/components/** src/registry.ts`, a lane touching only `src/components/x/a.txt` and `src/registry.ts`, `--gate false --light-gate true`: today argparse refuses the unknown flag (exit 2), and with the flag dropped the outcome is `red: false rc=1`; wanted `merged` with `gate: light` in the land journal line. Negative controls in the same case: the same lane also touching `README.md` stays `red: false rc=1`; the same config without the `merge_gate: light` line stays `red: false rc=1`; `cover` after the light merge appends one ledger entry whose `merges` names the ticket, and `settle --require-covered` refuses before `cover` and passes after. A second ticket (L2) can follow for `board.py --lanes` showing uncovered light merges; not in the first build.

## Interfaces

- `.sdlc/config` (consumer, read by `tickets.py`): new lines `merge_gate: light` (opt-in) and `light_scope: <glob> [<glob>...]` (repeatable; git `:(glob)` pathspecs relative to the repo root, parsed like `hash_bound:` at `plugins/sdlc-lite/scripts/tickets.py:271`, `:448`). A handoff front matter or body line `merge_gate: full` forces the full set for that ticket.
- `plugins/sdlc-lite/scripts/tickets.py`: `light_scope_globs(root)` and `merge_gate_declared(root)` beside `hash_bound_globs`.
- `plugins/sdlc-lite/scripts/steps.py`: `gate_class(files, globs, rel, declared, forced_full)` returning `('light', '')` or `('full', reason)`, defined next to `merge_class` (`:2276`) and documented in `docs/references/sdlc-internals.md` under the fanout merge class.
- `plugins/sdlc-lite/scripts/fanout.py`: repeatable `--light-gate CMD` on `run`, `land` and `prep`, carried as `ctx['light_gates']` at the three context builders (`:845`, `:2011`, `:2245`) and in `land_command` (`:1723`); `merge_gate_close` (`:1405`) computes the class from `lane.files` before `:1439` and picks the set; the `say` line, the land report and the `land.jsonl` line (`:2169`) gain `gate: light|full`; the close reason text names the class. New `cover <integration> [--root .sdlc] [--lanes-dir DIR] --gate CMD... [--gate-need ...]`: full set at the tip under the merge lock, appends `<root>/gate-ledger.jsonl`, commits it with `git add -f`, prints the bisect line on red. `settle` gains `--require-covered` (reads the ledger; refuses with exit 2 and the uncovered range). `roll` is unchanged.
- `<root>/gate-ledger.jsonl` (consumer repo, committed): one JSON object per `cover` run with the fields named under (2).
- `docs/planning/light-merge-lane.md`: the design text above, moved there by the planner or conductor (this role writes no file outside the artifacts dir).

## Constraints and assumptions

- `steps.py lane` never reads a diff; it reads `handoff.md`, the newest planner result and `skips.md`: verified by reading `lane_action` (`steps.py:2903-2985`).
- The merged paths are first known in `merge_gate_close` before the gates run: verified at `fanout.py:1422-1424` and `:1439`.
- Gates are one list `ctx['gates']` set at `fanout.py:845`, `:2011`, `:2245` and re-emitted by `land_command` (`:1729`): verified by grep `'gates'` over `fanout.py`.
- `--gate-need [PREFIX::]RES=N` is the precedent for a per-gate attribute: verified at `fanout.py:525-541`, `:1731`.
- `roll` fast-forwards main after its gates: verified in the `fanout.py` docstring, roll section (`fanout.py:76-86`).
- `hash_bound:` globs are parsed from `<root>/config` by `tickets.hash_bound_globs`: verified at `tickets.py:271`, `:448-465`.
- `land.jsonl` lives under `<lanes-dir>/logs` and is gitignored scratch; `lanes.py close_lane` removes worktrees and branches, never the logs dir: verified by grep `rmtree|logs` in `lanes.py` (hits at `:24`, `:338`, `:1824` only).
- `tickets.py close` writes a `## Closed` section with the reason text: verified at `tickets.py:2010`.
- `runs.jsonl` is read as role-run cost records: verified at `budget.py:81`, `board.py:108`.
- The `[owner: <stage>]` clause and `deferred <owner>` exist (T-0408) and close acceptance is T-0472: verified at `steps.py:1961`, `.sdlc/.0472-close-accepts-stage-deferred/handoff.md`.
- Maison's full gate is 75 to 90 minutes per merge: from the handoff Context and `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`; unverified against maison's logs.
- `git bisect --first-parent` over the ledger range is linear in tickets because each ticket is one `--no-ff` merge: verified at `fanout.py:1426`; the bisect itself was not run.

## Rejected alternatives

- New `steps.py lane` values `light` and `full`: the lane decision runs before the diff exists and names who does the work, not what gates the merge; overloading it would make `lane_decision` (`fanout.py:855`) and the `skips.md` lane record mean two things.
- Inferring light from the diff with no config line: the handoff forbids it, and a repo with no declared scope would get light merges by accident.
- A mechanical "exactly one component folder" rule in the plugin: the plugin cannot know what a component is; the owner's globs express it, and a count rule would refuse legitimate two-folder refactors the owner wants light.
- Ledger in `<lanes-dir>/logs/land.jsonl`: per lanes dir, gitignored, retired with the integration tree; bisect needs it later and in the primary checkout.
- Ledger in per-ticket `runs.jsonl`: a cost record with one line per role attempt; a cadence run covers many closed tickets.
- Ledger as git tags or notes: carries no command, rc or range in a form `settle` can read cheaply, and notes do not travel on push.
- Per-lane gate sets keyed by lane name (`--lane-gate alpha::CMD`): a lane carries several tickets with different diffs; the class is per merge.
- Light set on `roll`: puts work on main behind a partial gate, which is the non-goal.
- A plugin-owned cadence timer: the schedule is a project policy; the plugin ships `cover` and the `settle` refusal.
- A plugin-owned fixture owner step: the fixtures are project knowledge; the `[owner:]` clause plus a final `depends:` ticket already give the slot.

## Risks

- Glob semantics: `light_scope` must use the same `:(glob)` pathspec matching as `declared_hits`, or a path the owner believes is in scope is classed full (safe) or, worse, a registration file outside the globs is classed light because the matcher is looser than git's. The selftest's `README.md` negative control guards the second case.
- A light merge that breaks another component sits in integration until the next `cover`; other lanes rebase onto it. Mitigation is the ledger and the `settle` refusal, not detection; the owner accepts this by declaring `merge_gate: light`.
- `cover` red over N merges cannot reset like a single merge; if the owner never bisects, the integration branch is stuck and `settle --require-covered` keeps refusing. Without `--require-covered` by default, a plain `settle` still fast-forwards, so the first build must make the fanout skill (`plugins/sdlc-lite/skills/fanout/SKILL.md:49`) run settle with the flag when the config declares light.
- `land_command` and `prep`: if `--light-gate` is missed in the printed land line, sub-agent lanes land with the full set silently (safe but defeats the lane) or, if `ctx['light_gates']` is missing at one builder, a KeyError mid-land.
- A gitignored `.sdlc/` and the ledger commit: `git add -f` of `<root>/gate-ledger.jsonl` in the integration worktree depends on the worktree holding the file; `cover` must write it in the integration tree, not the primary checkout, so the commit rides the branch to main.
- The 75 to 90 minute saving is maison's number; this repo's own gates are already cheap (T-0456), so the local selftest proves mechanics, not the saving.

## Carry forward

- `steps.py lane` reads handoff, plan and skips.md only, never a diff: `plugins/sdlc-lite/scripts/steps.py:2903-2985`.
- Merged paths are known at `plugins/sdlc-lite/scripts/fanout.py:1422-1424`; gates run from `:1439`; a red resets at `:1467`; the merge commit subject is `Merge <branch>: <id>` at `:1426`.
- `ctx['gates']` is built at `fanout.py:845`, `:2011`, `:2245` and re-emitted by `land_command` at `:1723-1737` (grep `'gates'` over `plugins/sdlc-lite/scripts/fanout.py`).
- `--gate-need` prefix parsing and precedence: `fanout.py:525-541`; threaded at `:1731`.
- `roll` fast-forwards main after its gates: `fanout.py:76-86` (docstring); `cmd_roll` at `:2352`.
- `settle` fast-forwards with `git merge --ff-only` and closes the integration tree: `fanout.py:2310-2349`.
- `land.jsonl` line format and location: `fanout.py:2167-2171`; `read_journal` at `:2078`.
- `hash_bound:` config grammar and parser: `plugins/sdlc-lite/scripts/tickets.py:271`, `:448-465`; `merge_class` at `steps.py:2276`; `declared_hits` at `:2296`.
- `.sdlc/config` lane keys are parsed separately by `lanes.config` with `CONFIG_KEYS` at `plugins/sdlc-lite/scripts/lanes.py:134`, `:215`.
- Ticket records enter the lane branch with `git add -f` at `fanout.py:2052`; `.sdlc/config` is copied untracked into worktrees at `:2028-2031`.
- `tickets.py close` appends `## Closed` at `tickets.py:2010` and refuses held criteria at `:1962-1966` (T-0472 changes the latter).
- `runs.jsonl` is a cost record: `plugins/sdlc-lite/scripts/budget.py:81`, `plugins/sdlc-lite/scripts/board.py:108`.
- The `[owner: <stage>]` clause: `steps.py:1961`; T-0472 handoff at `.sdlc/.0472-close-accepts-stage-deferred/handoff.md`.
- The design text for `docs/planning/light-merge-lane.md` is this result; the first build ticket is one L3 fanout.py ticket named under Approach.
