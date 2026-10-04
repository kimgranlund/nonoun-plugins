## Task goal
Add `steps.py lane`, extract `review_required()`, and write the lane and skip history to skips.md.

## Step 2: steps.py lane and the skips.md lane history
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets:
- `plugins/sdlc-lite/scripts/steps.py`: a new `# --- lane ---` section after `# --- review ---`, `main`, the module docstring, a few small helpers, and `selftest`.
- `docs/maintenance/sdlc-internals.md`: the `## scripts/steps.py` paragraph.

Depends on: step 1 (`review_required`).

Settled decisions:

**CLI.**
- Add a `lane` subparser with one positional `task`. Its help text names `skips.md`.
- `main` dispatches to `cmd_lane(a.task)`.
- The docstring `Usage:` line gains `lane <task dir>` after `review <task dir>`.
- The docstring gains an entry starting `  lane      lane <task dir>: ...` with the rules below. `-h` prints only the first docstring line (`description=__doc__.split('\n')[0]` in `main`), so the docstring is checked directly.

**Functions.**
- `lane_action(task)` returns `(lane, point, reasons, read)` and writes nothing.
- `record_lane(task, lane, point, reasons)` writes `skips.md`.
- `cmd_lane(task)` calls both, then prints:
  1. the lane
  2. one `reason: <r>` line per reason
  3. one `read: <path>` line per file read: `<task>/handoff.md` when it exists, the plan when there is one, and `<task>/skips.md` when it existed before the write

  It exits 0.
- A task path that is not a dir raises `Fail('steps lane: no such directory: <task>')`. That prints one stderr line, nothing on stdout, exits 1, and writes nothing.
- An `OSError` while writing `skips.md` gives a single `steps lane: cannot write <path>: <error>` line on stderr, exit 1, and nothing on stdout.

**Facts read.**
- **Size.** Read `<task>/handoff.md` as UTF-8 and take `(tickets.parse(text) or {}).get('size')`. The size is valid only when it is in `tickets.ENUMS['size']`. A missing handoff.md gives no size without calling `tickets.parse`.
  - The `or {}` is required. `tickets.parse` returns `None` for text with no front matter block (tickets.py:227-232, `if not m: return None`), so a bare `tickets.parse(text).get('size')` raises `AttributeError` on a handoff with no front matter. That was observed at plan time. With `or {}`, that handoff gives no size, which rule 2 below turns into `full`.
  - `tickets.parse` is the one front matter parser: board.py:53 and fanout.py:182 import it for that.
- **Import tickets lazily.** Put `import tickets` inside `lane_action`, with a comment explaining why. The results.py selftest copies `steps.py` beside only `order.py` and `results.py` (results.py:193) and runs `steps.py next`. A top-level `import tickets` makes that copy fail with `ModuleNotFoundError`, which breaks its negative control. This was observed red at plan time.
- **Plan** is `order.newest(t, 'planner')`, or `None`.
- **Point**:
  - `before planning` when there is no plan
  - `after plan review` when there is a plan and the handoff has a line equal to `## Plan review`
  - `after planning` otherwise
- **Sticky**: true when `skips.md`, inside its `## Lane` section, has a line starting `- lane: full;`.
- **Plan reading is lenient**, like `plan_facts`: no `results.structure_error` check, because split, lint, and review refuse a bad plan.

**Rules.** Collect the full reasons in this order, with these exact strings:
1. Sticky: `skips.md already records full, and a lane never returns from full`
2. Invalid size (no handoff, no front matter, no `size` key, or a value outside `tickets.ENUMS['size']`): `handoff.md front matter has no size of S, M, L, or XL`

Before planning, size alone decides. This is the handoff's first decision point. The reason is `size <v> decides before planning (no planner result yet)`:
- S gives `fix`.
- M gives `lean`.
- L or XL gives `full`.
- If the sticky or no-size reason is present, the lane is `full` and only those reasons print.

After planning, these reasons follow, in order:
3. `size <v> is above M, and lean takes only size S or M` for L or XL.
4. `<pname> lists an unresolved assumption: "<first item>"` when `review_required` returns unresolved items.
5. Every string in `review_required(plan, t)[1]`, verbatim.
6. `<pname> has steps that do not parse (steps.py lint names why)` when `parse_steps` raises `Fail`. Skip rules 7 to 12 in that case.
7. `<k> steps, and lean allows at most 2` when k > `LANE_MAX_STEPS = 2`.
8. Per step, in plan order: `step <n> has <k> acceptance criteria, and lean allows at most 12` when k > `LANE_MAX_CRITERIA = 12`.
9. `step <n> has no scope allow-list in a form steps.py widen recognizes, so its files are unknown`.
10. `step <n> scope entry is not a repo-relative path: <entry>`.
11. `step <n> scope names a contract other roles parse: <path>`.
12. `scoped files span <k> AGENTS.md owners: <owners sorted, joined by ", ">` when there is more than one owner.

No reasons after planning gives `lean`, with the one reason `every lean condition holds: size <v>, planner L<level>, <k> steps at L1 to L3, one AGENTS.md owner (<owner>)`. After planning the lane is never `fix`. Any reason gives `full`.

The thresholds 2 and 12 are design.md:50 resolved default 4. A ticket that meets a mandatory condition becomes `full` from that point. That is the handoff's own sentence, and it is why a recorded `full` is sticky.

**Criterion count.** Add `criteria_count(block)`: the number of `criteria_lines(block)` lines matching `^[-*] `. This is the rule `lean_warnings` uses today. Make `lean_warnings` call it.

**Scope parsing.** Use the forms `widen` recognizes (steps.py:1505-1548). Add two helpers and make `widen` call both:
- `is_scope_span(span)`: `'git diff --name-only' in span and INVERT_GREP_RE.search(span)`
- `repo_path_ok(p)`: widen's path rule. It must match `WIDEN_PATH_RE`, not start with `-` or `/`, and hold no `..` component.

`scope_entries(block)` returns `None` when no list-item criterion line has a scope span with a `widen_forms` match. Otherwise it returns every entry of every form on those spans:
- F words come from `widen_listed`, quotes stripped.
- E and A alternatives come from `widen_listed`. Delete each backslash pair from an alternative. If what is left holds any of `^$*+?()[]{}`, keep the alternative raw: it is a pattern, not a path. Otherwise remove each backslash escape. An unescaped `.` is a literal dot.

Every entry must pass `repo_path_ok`. Otherwise it is rule 10.

**Owner rule.** The root is `guard_cwd(t)`: the git toplevel, else the task dir. The owner of path p is the nearest dir from `(root/p).parent` up to root that holds `AGENTS.md`. When there is none, the owner is root. The label is the path relative to root, posix form, `.` for root. Collect owners over all valid paths of all steps.

This approximates the design's "one nearest AGENTS.md owner, or one script and its tests" (design.md:81) on the safe side. A script and its tests under one owner pass. Anything else is `full`. The user asked for the safest defaults (design.md:48).

**Contract list.** `LANE_CONTRACTS` is exactly this tuple. An entry ending in `/` matches by prefix; any other entry matches exactly.
- `plugins/sdlc-lite/agents/`
- `plugins/sdlc-lite/skills/`
- `plugins/sdlc-lite/hooks/`
- `plugins/sdlc-lite/adapters/codex/`
- `plugins/sdlc-lite/scripts/run.sh`
- `plugins/sdlc-lite/scripts/run_lifecycle.py`
- `plugins/sdlc-lite/scripts/readiness.py`
- `plugins/sdlc-lite/scripts/codex_roles.py`
- `plugins/sdlc-lite/scripts/steps.py`
- `plugins/sdlc-lite/scripts/tickets.py`
- `plugins/sdlc-lite/scripts/results.py`
- `plugins/sdlc-lite/scripts/order.py`
- `plugins/sdlc-lite/scripts/check.py`
- `plugins/sdlc-lite/scripts/check.sh`
- `scripts/check-packaging.py`

Evidence:
- design.md:81 names role output sections, `run.sh` tables, `steps.py`, `tickets.py`, and hooks.
- design.md:86 names role behavior, runner invariants, hooks, and checks.
- design.md:87 names generated Codex agents.
- plugins/sdlc-lite/AGENTS.md:7 says skills hold the workflow and output contracts. Lines 10, 13, 19, and 42 name results.py, codex_roles generation, order.py, and readiness and run_lifecycle.

**skips.md layout.** This is the format T-0198 will read. Lane owns only its `## Lane` section.
- Each record is one line: `- lane: <lane>; point: <point>; reasons: <reasons joined by "; ">`.
- A missing file is written as `# Skips`, a blank line, `## Lane`, the line, and a final newline.
- A file whose `## Lane` section already exists gets the line inserted after that section's last non-blank line, the same way `add_scope_widened` appends.
- A file with no `## Lane` section gets three lines (`## Lane`, the record, a blank line) before its first `## ` line. With no `## ` line, it gets a blank line, `## Lane`, and the record at the end.
- Every other line is kept byte for byte. Every call appends, duplicates included.

**Docstring entry.** It states the stdout shape, every rule above with its reason meaning, the skips.md layout, the lenient plan read, and the error exits. It names `review_required()` as the function `review` uses, and names `LANE_CONTRACTS`.

**Internals doc.** In `docs/maintenance/sdlc-internals.md`, add one `lane <task dir>` clause to the steps.py paragraph, right after the `review <task dir>` clause that ends with "(/chain 3 runs it after each planner run)". It names `fix`/`lean`/`full`, the `reason:` and `read:` lines, `review_required()`, the size-only rule before planning, the after-planning conditions, the sticky `full`, and the `- lane:` line under `## Lane` in `skips.md`.

**Selftest.** Print exactly these labels through `check(...)`. Use a temp git repo (`git init`, as the `(o)` and `(r)` cases do) with the ticket at `<repo>/.sdlc/0001-x/`. The lean fixture has:
- a handoff with front matter `size: M`
- `planner-L2.md` with two steps at L2 and L3
- step 1 with exactly 12 criteria, including one F-form scope criterion `grep -vxF -e docs/a.md -e docs/b.md`
- step 2 with a scope criterion
- no AGENTS.md below the repo root

The labels:
- `(lane) before planning, size alone decides: S fix, M lean, L and XL full, no size full`: five handoffs (S, M, L, XL, and one with no front matter block at all, only `## Goal` and a line) and no planner. Each writes a `- lane: ...; point: before planning; ...` line. The no-front-matter handoff gives `full` with the reason `handoff.md front matter has no size of S, M, L, or XL` and raises nothing; it is the case the `or {}` guards.
- `(lane) a two-step size M plan at L1 to L3 inside one AGENTS.md owner is lean, for scope forms F, E, and A`: the lean fixture in three variants. Step 2's scope is F `-e docs/c.md`, E `grep -vxE "docs/c\.md"`, or A `grep -vE "^(docs/c\.md)$"`. Each gives `lean` with the every-lean-condition reason.
- `(lane) negative: the same two-step plan with one step at L4 is full`: reason `a step is at builder L4 or L5`.
- `(lane) negative: a lean ticket whose handoff gains a ## Plan review line is full on the next call`: the first call gives `lean`. After appending `## Plan review` and a line to the handoff, the next call gives `full`, with reason `handoff.md holds ## Plan review` and point `after plan review`.
- `(lane) every plan steps.py review requires a review or a stop for is full, with each review_required reason`. Seven variants of the lean fixture, each with a results.py header so review reads it: a planner L3 file, a step at L4, a step at L5, a `Merge x` step, two planner results, a `## Plan review` line, and an unresolved assumption. In each, review's first line is `review L1` or `stop`, lane's first line is `full`, and every `review_required` string appears as a `reason:` line. The unresolved case also shows the quoted item.
- `(lane) full after planning: size L, three steps, a 13-criterion step, no recognized scope allow-list, a non-path scope entry, a contract path, or two AGENTS.md owners`. One variant each, with its own reason line:
  - E entry `docs/.*`
  - F entry `plugins/sdlc-lite/scripts/steps.py`
  - A form `grep -vE "^(docs/a\.md|pkg/x\.py)$"` with `pkg/AGENTS.md` present, which gives owners `., pkg`
- `(lane) skips.md: each call appends one - lane: line to ## Lane and keeps every other line`. Three cases:
  - a missing file is created exactly
  - a file `# Skips`, blank, `## Lane`, one record, blank, `## Skipped`, `- x` gets the new record right after the old one, with `## Skipped` and `- x` kept
  - a file holding only `## Skipped` and `- x` gets `## Lane` inserted before `## Skipped`

  The `read:` lines name skips.md only when it existed before the call.
- `(lane) a recorded full stays full when the facts give lean`: the lean fixture plus a `- lane: full; ...` record. Gives `full`, with the sticky reason first.
- `(lane) a missing dir: one steps lane: line on stderr, nothing on stdout, exit 1, nothing written`.

Contract dependents:
- `results.py` selftest: kept green by the lazy import. Run as a guard below.
- check.py's `SCHEMA_COPY` regex (check.py:435): do not add `REVIEW_VERDICTS`, `startswith('inherited red:')`, or `first_word(path, 'Status'` or `'Verdict')` to steps.py.
- `widen`'s refactor: covered by the widen selftest cases.
- `lean_warnings`: covered by `(lean)`.
- Nothing reads `skips.md` today (`git grep` hits only the lean design docs).
- `footprint.py` counts `skips.md` as one more ticket file, which the design accepts.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md` lists every file a task dir holds in its Layout block. This step leaves it untouched on purpose: step 3 adds the `skips.md` entry there with the other guidance.
- Chain and conductor text are left to step 3 and T-0199.

Focused checks: `python3 plugins/sdlc-lite/scripts/steps.py selftest` and `python3 plugins/sdlc-lite/scripts/results.py selftest`.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lane) before planning, size alone decides: S fix, M lean, L and XL full, no size full"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lane) a two-step size M plan at L1 to L3 inside one AGENTS.md owner is lean, for scope forms F, E, and A"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lane) negative: the same two-step plan with one step at L4 is full"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lane) negative: a lean ticket whose handoff gains a ## Plan review line is full on the next call"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (lane) every plan steps.py review requires a review or a stop for is full, with each review_required reason"`
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && for l in "(lane) full after planning: size L, three steps, a 13-criterion step, no recognized scope allow-list, a non-path scope entry, a contract path, or two AGENTS.md owners" "(lane) skips.md: each call appends one - lane: line to ## Lane and keeps every other line" "(lane) a recorded full stays full when the facts give lean" "(lane) a missing dir: one steps lane: line on stderr, nothing on stdout, exit 1, nothing written"; do printf "%s\n" "$out" | grep -qF "ok: $l" || exit 1; done`
- `d=$(mktemp -d) && printf "%s\n" "---" "size: M" "---" "" "## Goal" "g" > "$d/handoff.md" && out=$(python3 plugins/sdlc-lite/scripts/steps.py lane "$d") && test "$(printf "%s\n" "$out" | head -n 1)" = lean && grep -qxF -e "- lane: lean; point: before planning; reasons: size M decides before planning (no planner result yet)" "$d/skips.md"`
- `d=$(mktemp -d) && printf "%s\n" "## Goal" "g" > "$d/handoff.md" && out=$(python3 plugins/sdlc-lite/scripts/steps.py lane "$d") && test "$(printf "%s\n" "$out" | head -n 1)" = full && printf "%s\n" "$out" | grep -qxF "reason: handoff.md front matter has no size of S, M, L, or XL" && grep -qxF -e "- lane: full; point: before planning; reasons: handoff.md front matter has no size of S, M, L, or XL" "$d/skips.md"`
- `python3 -c 'import inspect, sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; d = steps.__doc__; sys.exit(0 if "review_required(" in inspect.getsource(steps.lane_action) and "\n  lane " in d and "skips.md" in d else 1)'`
- `grep -qF "skips.md" docs/maintenance/sdlc-internals.md && grep -qF "review_required" docs/maintenance/sdlc-internals.md`
- (guard) `python3 plugins/sdlc-lite/scripts/results.py selftest`
- (guard) `! grep -qF "—" plugins/sdlc-lite/scripts/steps.py docs/maintenance/sdlc-internals.md`
- (guard) `! { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/steps.py -e docs/maintenance/sdlc-internals.md | grep -q .`
