<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
`fanout.py land` runs a light gate set when every path a lane merges matches the `light_scope` globs declared in `.sdlc/config`. `fanout.py cover` runs the full set at the integration tip and appends a committed `gate-ledger.jsonl` entry, and `settle --require-covered` gates the fast-forward on that ledger.

guard timeout: 800

## Step 1: Light gate class, --light-gate, cover with gate-ledger.jsonl, settle --require-covered
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/AGENTS.md`
### Do
Implementation targets. Read `docs/planning/light-merge-lane.md` (Approach, Interfaces, Risks; its line numbers are about 20 lines low against the current `fanout.py`). Then build the following.

1. `plugins/sdlc-lite/scripts/tickets.py`: add `light_scope_globs(root)` and `merge_gate_declared(root)` next to `hash_bound_globs` (tickets.py:448).
   - `light_scope_globs` parses every `light_scope: <glob> [<glob>...]` line in `<root>/config` with the same grammar as `HASH_BOUND_RE` (tickets.py:271): file order, deduplicated, blank lines, `#` lines and trailing comments skipped.
   - `merge_gate_declared` returns True only for an uncommented `merge_gate: light` line.
   - Mention both lines in the config docstring near tickets.py:154.

2. `plugins/sdlc-lite/scripts/fanout.py`, the gate class. The class is computed in `merge_gate_close` (fanout.py:1421), not in steps.py. The handoff Intent scopes this to fanout.py and says "computed in `merge_gate_close`". The design doc is `status: proposed`, not a ratified design.md, and `roll` never uses the class, so a shared steps.py helper has no second consumer. steps.py stays untouched.
   - Right after the `git diff --name-only HEAD...{ref}` at :1438, compute the class with a module helper `gate_class(ctx, ref)` that returns `('light', '')` or `('full', reason)`.
   - The class is light only when all of these hold:
     - `ctx.get('roll')` is false;
     - `tickets.merge_gate_declared(ctx['root'])` is true;
     - `tickets.light_scope_globs(ctx['root'])` is non-empty;
     - `ctx.get('light_gates')` is non-empty;
     - the merged paths outside the ticket root (`ctx['rel']`, as in the design's Approach (1)) are non-empty and every one is in `steps.declared_hits(integ, globs, f'HEAD...{ref}')`. That is the same `:(top,glob)` matcher, which answers the "matcher looser than git's" risk.
   - Any `ValueError` from `declared_hits` means full.
   - A light class with no `--light-gate` is full (reason `no --light-gate`). This keeps "a merge is never ungated".
   - The gate list is `ctx['light_gates']` when light, else `ctx['gates']`. The vacuous-gate refusal and the reset logic stay exactly as they are.

3. `--light-gate CMD`, repeatable:
   - Add it to the shared `run`/`prep` parser `ap` and to the `land` parser `lp` in `main`. `roll` gets no flag.
   - Carry it as `ctx['light_gates']` in the three context builders: `preflight` (gates at :852), `land_preflight` (:2031), and `roll_preflight` (:2265, always `[]`). A missing key there would be a KeyError mid-land.
   - Emit one `--light-gate <cmd>` per entry in `land_command` (:1743), after the `--gate`s, reading only `ctx.get('light_gates') or []`.
   - Refuse (`Refuse`, exit 2, nothing created) in `preflight` and `land_preflight` when `--light-gate` is given and `merge_gate_declared(root)` is false.
   - Update `USAGE`, the module docstring, and the `print_plan`/`print_prep` gate lines so the light gates show.

4. Reporting the class:
   - The `say` line reads `gate: light` or `gate: full (<reason>)`.
   - The `land.jsonl` line written in `cmd_land` (:2193) gains a `'gate': 'light'|'full'` key. To get the class to `cmd_land`, have `merge_gate_close` store it on the lane object (for example `lane.gate`); its return signature stays the same.
   - `close_reason` (:899) appends `; gate: <class>` for solo lanes. `tickets.py close` writes a `## Closed` section only on the `--reason` path (tickets.py:2006), so a full-chain lane's class lives in `land.jsonl` and the land report only. Do not pass `--reason` for non-solo lanes, because it skips the filer.

5. New `cover <integration> [--root .sdlc] [--lanes-dir DIR] --gate CMD... [--gate-need ...] [--no-gate-lock] [--allow-empty-gate]` subcommand, wired into `main`, `USAGE` and the docstring.
   - Find the integration worktree the way `cmd_settle` does (`git worktree list --porcelain`). Refuse with exit 2 when there is no worktree or no `--gate`.
   - Under `MergeLock(<lanes-dir>/merge.lock)`, in that tree, run every `--gate` at the tip with the same gate runner as `merge_gate_close` (`gate_argv`/`run_logged`), logging under `<lanes-dir>/logs/`.
   - Append one JSON line to `<integration tree>/<rel>/gate-ledger.jsonl` with these keys:
     - `at`, `run_id`, `integration`;
     - `from`: the previous entry's `to`, else `git merge-base <integration> HEAD` from the cwd;
     - `to`: the tip the gates ran on;
     - `gates`, `rc`, `log`;
     - `merges`: `[{sha, ticket}]` from the first-parent commits in `from..to` whose subject matches `Merge <branch>: <id>`.
   - Commit the ledger in the integration tree with `git add -f <rel>/gate-ledger.jsonl` and message `cover <to7>: rc=<rc>`. It never touches the primary checkout.
   - On red, also print `git bisect start <to> <from> --first-parent` and exit 1. Exit 0 on green.

6. `settle` gains `--root` (default `.sdlc`) and `--require-covered`. With the flag, before the fast-forward:
   - read the ledger with `git show <integration>:<rel>/gate-ledger.jsonl`;
   - refuse with exit 2 (branch kept, nothing merged) unless the newest entry has `rc == 0` and either `to` equals the integration tip or `git diff --name-only <to> <integration>` lists only the ledger path. The ledger commit moves the tip past `to`, so that second condition is what lets settle pass after `cover`;
   - print the uncovered range `<from-or-to>..<tip>` in the refusal.

7. `plugins/sdlc-lite/skills/fanout/SKILL.md` section 5 (the settle paragraph at :51). When `.sdlc/config` has a `merge_gate: light` line, the main step replaces the manual `git merge --ff-only <integration>` with two commands:
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py cover <integration> --gate "<cmd>"...`
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fanout.py settle <integration> --require-covered`, which then performs the fast-forward.

   Name `--light-gate` beside `--gate` in the argument-hint and the run/land text. Keep every phrase check.py item 24 requires, and use no `plugins/` paths (check.py item 42). Prompt wording elsewhere stays unchanged.

8. `docs/references/sdlc-internals.md`:
   - Next to the merge-class paragraph (:147), add a gate-class paragraph that defines `merge_gate: light`, `light_scope`, `--light-gate`, the full fallback, and that `roll` ignores the class.
   - Add the `cover` and `settle --require-covered` syntax to the command list (:151), including `gate-ledger.jsonl` and its fields.
   - Change the `docs/planning/light-merge-lane.md` front matter `status: proposed` to `status: built`, with a one-line note naming T-0481.

9. Selftest. Add a `T-0481` case to `fanout.py selftest`, every label prefixed `T-0481`. Write it first and observe it red on the unmodified code: today `--light-gate` exits 2. Record that in the builder result. The case must cover:
   - Config `merge_gate: light` and `light_scope: src/components/** src/registry.ts`, a solo lane (`worktree-<id>-solo`) touching only `src/components/x/a.txt` and `src/registry.ts`, landed with `--gate false --light-gate true`. Expect outcome `merged`, `"gate": "light"` in `land.jsonl`, and `gate: light` in the ticket's `## Closed` note.
   - Negative control: the same lane also touching `README.md` gives `red: false rc=1`.
   - Negative control: the same config without `merge_gate: light` and without `--light-gate` gives `red: false rc=1`.
   - Negative control: `--light-gate` without the declaration exits 2.
   - `land_command` with `light_gates` emits `--light-gate`.
   - `cover` appends exactly one ledger entry whose `merges` names the ticket, committed in the integration tree.
   - `settle --require-covered` exits 2 before `cover` and 0 after it.
   - A red `cover` (`--gate false`) prints the bisect line.

Contract dependents (searched with `git grep -n "land_command\|'settle'\|fanout.py settle\|land\.jsonl"` over plugins, scripts and docs/references):
- `report.py` reads `land.jsonl` (report.py:1147). The new `gate` key is additive and report.py is left untouched; `report.py selftest` runs as its check.
- The existing settle selftest cases (fanout.py:4216-4280) call settle without the new flag and must stay green.
- `check.py` items 24 and 42 pin phrases in the fanout skill; `check.py` runs.

Depends on: none.

Validation scope: the T-0481 selftest case, `fanout.py selftest`, `tickets.py selftest`, `report.py selftest`, `check.py`. The full `check.sh` is owned by the `fanout.py land` gates of this wave and is not run here. Leave scratch only under `$SDLC_TMP_WORKTREES`; never delete anything.
### Acceptance criteria
- (red) `python3 plugins/sdlc-lite/scripts/fanout.py land --help | grep -qF -- --light-gate && python3 plugins/sdlc-lite/scripts/fanout.py prep --help | grep -qF -- --light-gate`
- (red) `python3 plugins/sdlc-lite/scripts/fanout.py cover --help | grep -qF -- --gate`
- (red) `python3 plugins/sdlc-lite/scripts/fanout.py settle --help | grep -qF -- --require-covered`
- (red) `grep -qE '^def light_scope_globs\(root\)' plugins/sdlc-lite/scripts/tickets.py && grep -qE '^def merge_gate_declared\(root\)' plugins/sdlc-lite/scripts/tickets.py`
- (red) `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import fanout, pathlib as p; c = dict(integration='i', start='s', lanes_dir=p.Path('/x'), root=p.Path('/r/.sdlc'), top=p.Path('/r'), cwd=p.Path('/r'), gates=['false'], gate_needs=[], allow_empty_gate=False, rewrite_refs=False, light_gates=['true']); s = fanout.land_command(c, 'b', 'T-1'); assert '--light-gate true' in s, s"`
- (red) `grep -qF -- '--require-covered' plugins/sdlc-lite/skills/fanout/SKILL.md && grep -qF 'fanout.py cover' plugins/sdlc-lite/skills/fanout/SKILL.md`
- (red) `grep -qF 'light_scope' docs/references/sdlc-internals.md && grep -qF 'gate-ledger.jsonl' docs/references/sdlc-internals.md`
- (red) `grep -qF 'T-0481' plugins/sdlc-lite/scripts/fanout.py`
- Negative control, observed: in a `git worktree add --detach` copy of the built tree, make `gate_class` always return full, then run `fanout.py selftest`. It exits 1 and lists at least one `T-0481` label under `these did not hold:`. The unmodified built tree passes.
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE 'plugins/sdlc-lite/scripts/(fanout|tickets)\.py|plugins/sdlc-lite/skills/fanout/SKILL\.md|docs/references/sdlc-internals\.md|docs/planning/light-merge-lane\.md'`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py && python3 plugins/sdlc-lite/scripts/tickets.py selftest && python3 plugins/sdlc-lite/scripts/report.py selftest`

## Assumptions
- The merged paths are known in `merge_gate_close` before the gates run, and `lane.files` is filled from `git diff --name-only HEAD...<ref>`: verified at plugins/sdlc-lite/scripts/fanout.py:1438-1440 and gates at :1451.
- `steps.declared_hits(cwd, globs, *diff)` is the `:(top,glob)` matcher the class must reuse: verified at plugins/sdlc-lite/scripts/steps.py:2296-2310.
- `ctx['gates']` is set at fanout.py:852 (`preflight`), :2031 (`land_preflight`) and :2265 (`roll_preflight`), and `land_command` re-emits the gates at :1743-1757: verified by `grep -n "'gates'"` over fanout.py.
- `tickets.py close --reason` is the only path that writes `## Closed` with free text, and it skips the filer, so the class reaches the Closed note for solo lanes only: verified at tickets.py:1898 and :2006-2015, with `close_reason` returning None for non-solo lanes at fanout.py:899-906.
- `report.py` reads `land.jsonl` lines as JSON, so an added key is additive: verified at report.py:1147-1149.
- The fanout skill fast-forwards main by hand before settle: verified at plugins/sdlc-lite/skills/fanout/SKILL.md:49-51.
- The guards are green at the base HEAD 01a8cca7. Probes run at plan time: `fanout selftest: PASS` in 241 s, check.py ok in 7 s, tickets and report selftests PASS in 81 s, and the scope guard rc 0. Its un-negated form went red (matched an injected `README.md`).
- Every `(red)` criterion was observed red at the base for the right reason: an unknown subcommand or flag, a missing def, or an AssertionError on the missing `--light-gate`.
- The handoff `merge_gate: full` per-ticket override from the design doc is out of scope: the handoff Intent does not name it.

## Risks
- `fanout.py selftest` took 241 s here against 8 to 71 s in earlier records, so host load varies. The step's guard timeout is 800 s, but a heavily loaded host could still hit it.
- The skill change replaces the manual `git merge --ff-only` with `settle --require-covered` only when light is declared. If check.py item 24 pins wording in that paragraph, the builder must keep the pinned phrases.
- `cover` commits on the integration branch. A concurrent `land` is serialized by the shared `merge.lock`, but a `cover` run outside fanout's lock path (a hand commit) could make `to` stale. The settle rule then refuses, which is the safe failure.
- The design doc's `steps.gate_class` and `docs/references` placement differ from this plan, which keeps the classifier in fanout.py. The design doc is updated only in status, so its Interfaces text still names steps.py. That is cosmetic.
- A plan-time probe script was left at `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout44/l/.worktrees/tmp/0481-planner-L2/probe.sh`. It was not removed, per the no-delete rule.
