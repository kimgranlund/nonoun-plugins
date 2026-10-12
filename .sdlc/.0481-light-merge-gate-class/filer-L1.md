<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- None of the planned steps failed. The verifier passed step 1 (L2 verifier, all 12 criteria), and no `process-deviations.md` exists.
- The criterion-9 negative control did not run in a `git worktree add --detach` copy as the plan says. `block-stray-worktree.sh` denied the add because `SDLC_TMP_WORKTREES` is unset, so the builder and the verifier each ran it from a `cp -R` copy of `plugins/sdlc-lite`. In both runs `gate_class` forced to full made `fanout.py selftest` exit 1, with 5 `T-0481` labels under `these did not hold:`.

## PR title
T-0481: fanout.py land: light gate class from light_scope globs, --light-gate, cover with gate-ledger.jsonl

## PR body
### Summary
`fanout.py land` now runs a light gate set when every path a lane merges matches the `light_scope` globs in `.sdlc/config` and `merge_gate: light` is declared. The new `fanout.py cover` runs the full gates at the integration tip and appends a committed `gate-ledger.jsonl` entry. `settle --require-covered` gates the fast-forward on that ledger. A merge is never ungated: a light class with no `--light-gate` runs the full set, and the vacuous-gate refusal is unchanged. `roll` ignores the light class and always runs `--gate`.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - Adds `light_scope_globs(root)` and `merge_gate_declared(root)` beside `hash_bound_globs`, plus their patterns.
  - Documents both config lines in the config docstring.
- `plugins/sdlc-lite/scripts/fanout.py`:
  - `gate_class` runs inside `merge_gate_close` and reuses the `steps.declared_hits` matcher.
  - A repeatable `--light-gate CMD` is carried through run/prep, land, and `land_command`. `roll` always gets an empty list.
  - `light_refusal` exits 2 when `--light-gate` is given without the declaration.
  - The land `say` line and the `land.jsonl` entry now carry the gate class.
  - A solo lane's `## Closed` note ends with `; gate: <class>`.
  - New `cover` subcommand: the first red gate stops the run, the ledger commits with `git add -f` in the integration tree, and a red run prints the bisect line and exits 1.
  - `settle` gains `--root` and `--require-covered`.
  - Adds selftest case 34 (T-0481).
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: with `merge_gate: light`, `cover` then `settle --require-covered` replace the manual fast-forward in section 5. `--light-gate` is in the argument-hint and the run and land text.
- `docs/references/sdlc-internals.md`: documents the gate class, `cover`, `settle --require-covered`, and the ledger fields.
- `docs/planning/light-merge-lane.md`: status changed from `proposed` to `built`.

### How each was verified
- Red first: before any edit, 8 pre-edit controls were recorded red at base 01a8cca7. With only the case 34 test added, selftest failed on all 10 `T-0481` labels, and `land` exited 2 with `unrecognized arguments: --light-gate true`.
- The verifier ran all 8 `(red)` criteria as written and they pass, which covers:
  - the `--help` flags
  - the two tickets.py defs
  - `land_command` emitting `--light-gate true`
  - the SKILL.md and sdlc-internals.md text
  - the `T-0481` marker
- Negative control: `gate_class` forced to full makes `fanout.py selftest` exit 1 with 5 `T-0481` labels listed. The unmodified tree passes. It ran from a `cp -R` copy (see Warnings).
- Guards: the scope diff shows only the 5 allowed paths. `fanout.py selftest` exits 0 (`fanout selftest: PASS`). `check.py` exits 0. `tickets.py selftest` and `report.py selftest` pass. `git diff --check` is clean.
- Not checked live: no focused run in a throwaway project was done, only selftests.

## Changelog entry
- fanout: `land` runs a light gate set when every merged path matches the `light_scope` globs and `merge_gate: light` is declared in `.sdlc/config`. Pass `--light-gate CMD` (repeatable) to set it. New `fanout.py cover` runs the full gates at the integration tip and appends `gate-ledger.jsonl`. `settle --require-covered` refuses a fast-forward until a green cover entry exists. `roll` and any light class without `--light-gate` still run the full gates.

## Follow-ups
- note: `roll` now prints `gate: full (roll)` and a solo roll's close reason ends `; gate: full`, because `merge_gate_close` is shared. The behavior is intended, and roll gating is unchanged.
- note: `block-stray-worktree.sh` denies `git worktree add --detach` under the brief's tmp prefix when `SDLC_TMP_WORKTREES` is unset. The plan's negative control therefore falls back to a `cp -R` copy.
- note: A red `cover` still appends and commits its ledger entry, and `settle --require-covered` also checks a branch already merged by hand. These choices are the builder's, where the handoff left room.
- note: The design doc `docs/planning/light-merge-lane.md` still names `steps.gate_class` in its Interfaces text, but the classifier lives in `fanout.py`, and its line numbers are about 20 low.
