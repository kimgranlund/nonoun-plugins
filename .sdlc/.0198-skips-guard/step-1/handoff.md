## Task goal
Add a skips.md guard to tickets.py check and close, exempting tickets closed before the feature.

## Step 1: skips.md guard in tickets.py check and close, with selftest and docs
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Implementation targets: `plugins/sdlc-lite/scripts/tickets.py` (a new `skip_problems` helper, `cmd_check`, `cmd_close`, the module usage docstring's `check` and `close` entries, a new selftest block), `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (Layout), and `docs/maintenance/sdlc-internals.md` (the `scripts/tickets.py` section). Depends on: none. T-0197 already ships `steps.py lane` and is merged at 026622f.

Settled decisions:

1. **Lane source.** The lane is the last line starting `- lane: ` inside the `## Lane` section of `<ticket dir>/skips.md`. Take the value up to the first `;`. Evidence: `steps.py` `lane_record` writes `- lane: <lane>; point: ...; reasons: ...`, and `lane_text` appends one line per call (steps.py:1579-1605), so a file can read `lean` and later `full`. The last line wins. The guard applies only when that lane is `lean` or `fix`.

2. **Pre-feature exemption.** All of these cases are exempt (no problem reported):
   - no `skips.md`;
   - a `skips.md` with no `## Lane` section;
   - a `## Lane` section with no `- lane:` line;
   - a last lane of `full`.

   No date marker is used. Evidence:
   - A plain close writes no close date. `cmd_close` appends `## Closed` only for `--reason` and `--ack-warnings` (tickets.py:1336-1345, 1468-1474).
   - `skips.md` is written only by `steps.py lane` (`git grep skips.md` outside `.sdlc` finds only steps.py, handoff-format and docs).
   - No ticket in this repo has a `skips.md` (`ls .sdlc/*/skips.md` matched nothing).

   So a lane record is the feature's introduction marker, and `tickets.py --root .sdlc check` stays green on the 214 existing tickets.

3. **Roles the full chain would have run.** These are planner, verifier and filer, evaluated in that order:
   - planner: missing when the ticket dir holds no file whose name matches `order.RESULT` with role `planner`.
   - verifier: checked per live step dir. A live step dir is a direct child named exactly `step-<digits>` (`step-<n>.superseded-<k>` is ignored, per handoff-format SKILL.md "A live step dir is exactly `step-<digits>`"). Verifier step n is missing when `step-<n>/` holds no `verifier-*` result file.
   - filer: missing when the ticket dir holds no `filer-*` result file.

   Use `run_order.ordered(dir, role)`, which tickets.py already imports as `run_order` and uses for the filer.

   Builder is not checked, because every step dir is a builder's step. Plan-reviewer, scout, researcher and architect are not checked: `steps.py` `lane_action` returns `full` whenever `review_required()` returns any reason, so a ticket recorded `lean` or `fix` never had a required review. The optional roles are not part of the full chain.

4. **Entry format.** Entries are lines in a `## Skipped` section of `skips.md`. The section starts at a line that is exactly `## Skipped` and ends at the next `## ` line. Each entry has the form `- skip: <role>; step: <n or all>; reason: <why>; decided: <who>`.
   - Parse an entry by splitting on `;`. The first field is the role after `- skip: `. Later fields are `key: value`.
   - An entry counts only when its `reason` and `decided` values are non-empty. Unknown extra fields are ignored, so T-0199 can extend the line.
   - Planner and filer are covered by any counting entry for that role, whatever its `step` value.
   - Verifier step n is covered by a counting `verifier` entry whose `step` is `n` or `all`.
   - `steps.py` owns only `## Lane` (steps.py:178-183) and its selftest fixtures already use a `## Skipped` section (steps.py:3260).

5. **Problem text.** One line per ticket, with missing roles in the order planner, `verifier step <n>` (ascending n), filer, joined by `, `: `<folder>: skips.md records lane <lane> but has no ## Skipped entry for <roles>`. Example: `lean-a: skips.md records lane fix but has no ## Skipped entry for planner, filer`.

6. **Hook points.** Add a new function `skip_problems(td, ts)` that covers only tickets with status `done` (dropped tickets are excluded). Do not add it to `problems()`, because `roadmap`, `archive`, `number` and `close` also call `problems()`, and the handoff scopes the guard to `check` and `close`.
   - `cmd_check`: raise `Fail` with these lines after the router-problems check, so the existing failure order is kept.
   - `cmd_close`: evaluate the one ticket being closed as if it were done, right after the existing `status == 'done'` refusal and before `outside_refs` or any write. It applies on every path: plain, `--reason`, `--ack-warnings` and `--dry-run`. On a problem, raise `Fail` with the problem line plus `; add one "- skip: <role>; step: <n or all>; reason: <why>; decided: <who>" line per role under ## Skipped in <path to skips.md>; nothing written`.
   - This adds one refusal after the existing ones and changes none of them, as the handoff Constraints require. Use the folder name from `load()`, so the `.NNNN-<slug>` closed folders are handled.

7. **Selftest.** Add a block whose labels start with `(skips)`. It covers:
   - check: a fix ticket missing planner and filer entries fails;
   - check: the same ticket with both entries passes;
   - check: a done ticket with no `skips.md` passes (exemption);
   - check: a `skips.md` with only `## Skipped` and no lane passes;
   - check: a lane history `lean` then `full` with no entries passes;
   - check: a lean ticket whose `step-1/` lacks a verifier fails naming `verifier step 1`, while `step-2.superseded-1/` without a verifier is not named;
   - check: `step: all` covers a verifier;
   - check: an entry with an empty `reason` does not count;
   - close `--reason` on a fix ticket missing entries refuses and leaves `status` unchanged;
   - close (filer path) on a lean ticket with no planner result refuses;
   - close `--reason` with entries succeeds.

8. **Docs.** There is one authoritative place for each fact:
   - handoff-format SKILL.md Layout: extend the `skips.md` line to say it also holds `## Skipped`, with the entry format above verbatim. This is the only place the format is written out.
   - tickets.py usage docstring `check` and `close` entries: one sentence each on the guard and the exemption, pointing to handoff-format for the format.
   - sdlc-internals.md `scripts/tickets.py` section: one sentence naming the `## Skipped` guard and the no-lane-record exemption.

Contract dependents:
- `skills/fix/SKILL.md` closes with `--reason` and runs no `steps.py lane`, so its tickets have no lane record and stay exempt. It is left untouched on purpose, because T-0199 owns the conductor and skill skip text.
- `scripts/fanout.py` calls `tickets.py close` on the integration branch. Its selftest fixtures have no `skips.md`, so they stay exempt. Left untouched.
- `scripts/check.py` FINISH_FILES (check.py:180) greps `scripts/tickets.py` for the follow-up tag words. The docstring edit must keep them; step 2's `check.sh` guard covers this.
- `steps.py` is not changed.

Focused checks: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` (about 35 s) and the fixture criteria below.
### Acceptance criteria
- `T=$PWD/plugins/sdlc-lite/scripts/tickets.py; R=$(mktemp -d)/.sdlc; python3 $T --root $R new feature lean-a >/dev/null && python3 $T --root $R new feature old-b >/dev/null && mkdir -p $R/lean-a/step-1 && : > $R/lean-a/step-1/builder-L1.md && : > $R/lean-a/step-1/verifier-L1.md && printf "# Skips\n\n## Lane\n- lane: fix; point: before planning; reasons: size S\n" > $R/lean-a/skips.md && perl -pi -e "s/^status:\\s*\\S+/status: done/" $R/lean-a/handoff.md $R/old-b/handoff.md && python3 $T --root $R roadmap >/dev/null && out=$(python3 $T --root $R check 2>&1); rc=$?; test $rc -eq 1 && printf "%s\n" "$out" | grep -qF "lean-a: skips.md records lane fix but has no ## Skipped entry for planner, filer" && ! printf "%s\n" "$out" | grep -qF old-b`
- (guard) `T=$PWD/plugins/sdlc-lite/scripts/tickets.py; R=$(mktemp -d)/.sdlc; python3 $T --root $R new feature lean-a >/dev/null && python3 $T --root $R new feature old-b >/dev/null && mkdir -p $R/lean-a/step-1 && : > $R/lean-a/step-1/builder-L1.md && : > $R/lean-a/step-1/verifier-L1.md && printf "# Skips\n\n## Lane\n- lane: fix; point: before planning; reasons: size S\n\n## Skipped\n- skip: planner; step: all; reason: fix lane has no plan; decided: steps.py lane\n- skip: filer; step: all; reason: fix lane closes by reason; decided: steps.py lane\n" > $R/lean-a/skips.md && perl -pi -e "s/^status:\\s*\\S+/status: done/" $R/lean-a/handoff.md $R/old-b/handoff.md && python3 $T --root $R roadmap >/dev/null && python3 $T --root $R check`
- `T=$PWD/plugins/sdlc-lite/scripts/tickets.py; R=$(mktemp -d)/.sdlc; python3 $T --root $R new feature lean-a >/dev/null && mkdir -p $R/lean-a/step-1 $R/lean-a/step-2.superseded-1 && : > $R/lean-a/planner-L2.md && : > $R/lean-a/filer-L1.md && : > $R/lean-a/step-1/builder-L2.md && : > $R/lean-a/step-2.superseded-1/builder-L2.md && printf "# Skips\n\n## Lane\n- lane: lean; point: after planning; reasons: x\n" > $R/lean-a/skips.md && perl -pi -e "s/^status:\\s*\\S+/status: done/" $R/lean-a/handoff.md && python3 $T --root $R roadmap >/dev/null && out=$(python3 $T --root $R check 2>&1); rc=$?; test $rc -eq 1 && printf "%s\n" "$out" | grep -qF "lean-a: skips.md records lane lean but has no ## Skipped entry for verifier step 1" && ! printf "%s\n" "$out" | grep -qF "step 2"`
- `T=$PWD/plugins/sdlc-lite/scripts/tickets.py; R=$(mktemp -d)/.sdlc; python3 $T --root $R new feature lean-a >/dev/null && mkdir -p $R/lean-a/step-1 && : > $R/lean-a/step-1/builder-L1.md && : > $R/lean-a/step-1/verifier-L1.md && printf "# Skips\n\n## Lane\n- lane: fix; point: before planning; reasons: size S\n" > $R/lean-a/skips.md && python3 $T --root $R roadmap >/dev/null && out=$(python3 $T --root $R close lean-a --reason x 2>&1); rc=$?; test $rc -eq 1 && printf "%s\n" "$out" | grep -qF "no ## Skipped entry for planner, filer" && grep -q "^status: proposed" $R/lean-a/handoff.md`
- `T=$PWD/plugins/sdlc-lite/scripts/tickets.py; R=$(mktemp -d)/.sdlc; python3 $T --root $R new feature lean-a >/dev/null && mkdir -p $R/lean-a/step-1 && : > $R/lean-a/step-1/builder-L2.md && : > $R/lean-a/step-1/verifier-L1.md && printf "## Warnings\nNone\n\n## Follow-ups\nNone\n" > $R/lean-a/filer-L1.md && printf "# Skips\n\n## Lane\n- lane: lean; point: after planning; reasons: x\n" > $R/lean-a/skips.md && python3 $T --root $R roadmap >/dev/null && out=$(python3 $T --root $R close lean-a 2>&1); rc=$?; test $rc -eq 1 && printf "%s\n" "$out" | grep -qF "no ## Skipped entry for planner" && grep -q "^status: proposed" $R/lean-a/handoff.md`
- (guard) `T=$PWD/plugins/sdlc-lite/scripts/tickets.py; R=$(mktemp -d)/.sdlc; python3 $T --root $R new feature lean-a >/dev/null && mkdir -p $R/lean-a/step-1 && : > $R/lean-a/step-1/builder-L1.md && : > $R/lean-a/step-1/verifier-L1.md && printf "# Skips\n\n## Lane\n- lane: fix; point: before planning; reasons: size S\n\n## Skipped\n- skip: planner; step: all; reason: fix lane has no plan; decided: steps.py lane\n- skip: filer; step: all; reason: fix lane closes by reason; decided: steps.py lane\n" > $R/lean-a/skips.md && python3 $T --root $R roadmap >/dev/null && python3 $T --root $R close lean-a --reason x && grep -q "^status: done" $R/lean-a/handoff.md`
- `grep -qF "(skips)" plugins/sdlc-lite/scripts/tickets.py`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- `grep -qF "## Skipped" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF "## Skipped" docs/maintenance/sdlc-internals.md`
- `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/tickets.py -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e docs/maintenance/sdlc-internals.md)"`
