<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/l/plugins/sdlc-lite/scripts/tickets.py: adds `light_scope_globs(root)` and `merge_gate_declared(root)` next to `hash_bound_globs`. Also adds the `LIGHT_SCOPE_RE` and `MERGE_GATE_RE` patterns and mentions both config lines in the config docstring.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/l/plugins/sdlc-lite/scripts/fanout.py:
  - `gate_class(ctx, ref)` is called in `merge_gate_close` right after the diff and stores the class on `lane.gate`. A light merge runs `light_gates`; the vacuous-gate refusal and the reset are unchanged.
  - The `say` line reads `gate: light` or `gate: full (<reason>)`, and the `land.jsonl` line has a new `gate` key.
  - `close_reason(ctx, t, gate=None)` appends `; gate: <class>` for solo lanes.
  - `light_refusal` exits 2 in `preflight` and `land_preflight`.
  - `--light-gate` is on the run/prep and land parsers and is carried as `ctx['light_gates']` in all three context builders (roll always `[]`). `land_command` emits it, and the `print_plan`/`print_prep` output shows it as `light gate <k>:` lines.
  - New `cover` subcommand (`cmd_cover`) writes `gate-ledger.jsonl`.
  - `settle` gains `--root` and `--require-covered` (`require_covered`).
  - USAGE, the module docstring (new Gate class and cover sections, the settle flag, case 34) and selftest case 34 (T-0481) are updated.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/l/plugins/sdlc-lite/skills/fanout/SKILL.md:
  - `--light-gate` appears in the argument-hint, the dry-run text and the land text.
  - Section 5 has a new paragraph: with `merge_gate: light`, `fanout.py cover` then `fanout.py settle <integration> --require-covered` replace the manual `git merge --ff-only`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/l/docs/references/sdlc-internals.md: a gate-class paragraph after the merge-class paragraph, and a paragraph with the `cover` and `settle --require-covered` syntax and the ledger fields after the `run` paragraph.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/l/docs/planning/light-merge-lane.md: `status: proposed` became `status: built`, with a note naming T-0481.

## Checks
- `redck.py record <handoff>` before the first edit: exit 0, 8 pre-edit controls recorded red.
- `fanout.py selftest` with only the case 34 test added (implementation not yet written): exit 1 (6 min 10 s). All 10 `T-0481` labels failed and nothing else did; the land run failed with `fanout.py land: error: unrecognized arguments: --light-gate true` (exit 2).
- `fanout.py selftest` after the build: exit 0, `fanout selftest: PASS`.
- The 8 `(red)` criteria, run as written after the build: all exit 0.
- `(guard)` scope diff command, run with `SDLC_BASE_SHA=01a8cca7`: exit 0. Changed files are only the 5 allowed paths.
- `(guard)` `check.py && tickets.py selftest && report.py selftest`: exit 0.
- `git diff --check`: clean.
- Negative control: a copy of the built plugin with `gate_class` forced to return `('full', 'mutant')`, then `fanout.py selftest` from that copy. It exited 1 and listed 5 `T-0481` labels under `these did not hold:`. The unmodified built tree passes (run above).

## Notes
- The negative control did not run in a `git worktree add --detach` copy as the criterion says. `block-stray-worktree.sh` denied the add because `SDLC_TMP_WORKTREES` is unset in this session; it was denied even with the literal tmp-prefix path from the brief. I ran it instead from a `cp -R` copy of the built `plugins/sdlc-lite` under the tmp prefix, which the selftest treats the same way because it builds its own temp repos. For the planner: the brief gives a worktree prefix that the hook does not accept.
- Scratch under `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/l/.worktrees/tmp/0481-s1-builder-L3/` (gitignored) is left in place, since the handoff says never delete anything. It holds the edit scripts, `st1.txt` (green selftest), `negctl/` (the mutant copy) and `negctl.txt` (the mutant run output).
- Roll now shows the class too, because `merge_gate_close` is shared: it prints `gate: full (roll)` and a solo roll's close reason ends `; gate: full`. Roll's gating is unchanged and always uses `--gate`; the roll selftest cases stay green.
- `cover` decisions where the handoff left room:
  - **Lanes dir:** the default is the integration worktree's parent, where `land` keeps `merge.lock`.
  - **Gates and rc:** the first red gate stops the run. A vacuous gate counts as red unless `--allow-empty-gate` is given.
  - **`log`:** points at the last gate log that ran.
  - **Red runs:** a red `cover` still appends and commits its ledger entry, as the design says.
- `settle --require-covered` also checks a branch that is already merged by hand (the check runs before the ancestor test).
- `land.jsonl` writes `gate: full` when the class was never computed, for example on `no changes` or `integration dirty`.
