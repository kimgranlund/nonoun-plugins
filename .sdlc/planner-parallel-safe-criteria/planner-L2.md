<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `steps.py split`/`lint` refuse two parallel-lane-fragile criterion shapes: a pinned commit sha and a fixed count over a changing set. Also teach the planner all three rules from T-0100 (pinned sha, fixed count, global aggregate budget) and guard that doc text in check.py.

## Step 1: Lint pinned shas and fixed set counts, and add the three parallel-lane planner rules
level: L3
### Do
All paths are relative to the repo root. The failing tests land in this same step, as selftest cases, together with the fix.

1. `plugins/sdlc-lite/scripts/steps.py`: extend `lint_steps` so each command-like criterion span that parses under `bash -n` gets two more checks on its raw span text. Use regexes on the raw text, not shlex tokens, because the real case sits inside a quoted `"$(...)"` that shlex keeps as one token. Each hit adds one finding, and `lint_or_fail` still ends the refusal with the `PLAN_DEFECT` line. Keep the existing parse and `||` checks unchanged.
   - Pinned sha. The span holds the word `git` and a run of 7 to 40 lowercase hex chars with a non-alphanumeric char (or string edge) on each side. The run must hold at least one digit and at least one letter a-f. It also matches inside a revision expression such as `<sha>..HEAD`, `<sha>^`, or `<sha>~2`. The finding text reads `steps: <plan> step <n>: acceptance criterion pins a commit sha fixed at plan time: <span>`, followed by a hint line saying to compare against HEAD at build start (`HEAD`, `HEAD~1`), because a fixed sha goes stale on the first sync from main. `HEAD`, `HEAD~1`, `HEAD^1`, branch names, and `%H` never match.
   - Fixed set count. The span holds all three of the following, and the finding text reads `steps: <plan> step <n>: acceptance criterion compares a count over a changing set with a fixed number: <span>`, followed by a hint line saying to derive the set at run time or check only this step's own items.
     - A count tool: `wc -l`, `grep -c`, or `grep --count`.
     - A set source: a `*` glob char, or `ls` or `find` as a word.
     - A comparison of a literal integer of 2 or more: `-eq`, `-ne`, `-ge`, `-gt`, `-le`, `-lt`, `=`, `==`, or `!=`, followed by optional whitespace and an optional quote.

     `-eq 0` and `-eq 1` pass, and so do a count over a single named file and `wc -w`. The merge-step template must stay lint-clean (check.py checks it).
   - Update the module docstring's `lint` and `split` paragraphs to name both new refusals.
   - Add selftest cases next to `(k2)`. Two cases check that split and lint each refuse, write nothing, and name `plan defect`: one on a pinned sha (bare and in a `<sha>..HEAD` range), labelled so the output holds `pins a commit sha`, and one on a glob count compared with 26, labelled so it holds `fixed number`. A third case checks that these pass: `git diff --quiet HEAD -- src`, `git log -1 --format=%H HEAD~1`, `test "$(grep -c foo x.txt)" -eq 2`, a glob count `-eq 0`, and the merge-step two-parent criterion.
2. `plugins/sdlc-lite/agents/planner.md`: under `## Criteria that can pass`, add three numbered rules after rule 5. Renumber the replan rules to 9 and 10, and fix any in-file references to their numbers.
   - Rule 6: compare against HEAD at build start, never a sha fixed at plan time. `git diff --quiet <sha> -- ...` goes stale on the first main sync, and `steps.py split` refuses a criterion that pins a commit sha.
   - Rule 7: never compare a count over a set other lanes change (tickets, handoffs, files under a glob) with a fixed number. Derive the set at run time, or check only the items this step adds. `steps.py split` refuses a glob, `ls`, or `find` count compared with a literal of 2 or more.
   - Rule 8: a criterion over a generated or aggregate budget (a catalog token size, an exact deviation list, a total across all tickets) belongs only to the ticket that owns that budget. Any other step checks only its own delta ("adds no new deviation") against a `git worktree add <tmp> HEAD` copy, as in rule 3. The text must contain the exact phrases `sha fixed at plan time`, `derive the set at run time`, and `owns that budget`.
3. `plugins/sdlc-lite/scripts/check.py`: add entries to `PLAN_DEFECT_DOCS`. `sha fixed at plan time` goes to `('agents/planner.md', 'scripts/steps.py')`, and `owns that budget` goes to `('agents/planner.md',)`. Also update check.py's header comment list if it enumerates these guards.
4. Repair stale records in the same change:
   - `CLAUDE.md`, the `scripts/steps.py` bullet, which lists what split refuses as a `plan defect`: add that split refuses a criterion that pins a commit sha and one that compares a count over a changing set with a fixed number. The text must contain `pins a commit sha`.
   - `.claude/agents/sdlc-lite-author.md`, the Plan-defect route line: name both new lint checks. The text must contain `pins a commit sha`.
### Acceptance criteria
- `s=$(printf %s 3f9c 2ab) && d=$(mktemp -d) && printf "## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- (guard) \x60git diff --quiet %s -- src\x60\n\n## Risks\nNone\n" "$s" > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md" 2>"$d/err" && grep -q "plan defect" "$d/err" && grep -q "pins a commit sha fixed at plan time" "$d/err"`
- `s=$(printf %s 3f9c 2ab) && d=$(mktemp -d) && printf "## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \x60git diff --quiet %s..HEAD -- src\x60\n\n## Risks\nNone\n" "$s" > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md" 2>"$d/err" && grep -q "pins a commit sha fixed at plan time" "$d/err"`
- `d=$(mktemp -d) && printf "## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \x60test \"\$(ls %s | wc -l)\" -eq %s\x60\n\n## Risks\nNone\n" ".sdlc/$(printf "\x2a")/handoff.md" "$((20+6))" > "$d/planner-L2.md" && ! python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md" 2>"$d/err" && grep -q "plan defect" "$d/err" && grep -q "compares a count over a changing set with a fixed number" "$d/err"`
- (guard) `d=$(mktemp -d) && printf "## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \x60git diff --quiet HEAD -- src\x60\n- \x60git log -1 --format=%%H HEAD~1\x60\n\n## Risks\nNone\n" > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- (guard) `d=$(mktemp -d) && printf "## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \x60test \"\$(grep -c foo x.txt)\" -eq 2\x60\n\n## Risks\nNone\n" > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- (guard) `d=$(mktemp -d) && printf "## Goal\ng\n\n## Step 1: a\nlevel: L1\n### Do\nx\n### Acceptance criteria\n- \x60test \"\$(ls %s | wc -l)\" -eq 0\x60\n\n## Risks\nNone\n" ".sdlc/$(printf "\x2a")/handoff.md" > "$d/planner-L2.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/planner-L2.md"`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -q "pins a commit sha"`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -q "fixed number"`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `grep -q "sha fixed at plan time" plugins/sdlc-lite/agents/planner.md`
- `grep -q "derive the set at run time" plugins/sdlc-lite/agents/planner.md`
- `grep -q "owns that budget" plugins/sdlc-lite/agents/planner.md`
- `grep -q "sha fixed at plan time" plugins/sdlc-lite/scripts/check.py`
- `grep -q "owns that budget" plugins/sdlc-lite/scripts/check.py`
- `grep -q "pins a commit sha" CLAUDE.md`
- `grep -q "pins a commit sha" .claude/agents/sdlc-lite-author.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (green on the current tree, about 170s).
- Observable: in `plugins/sdlc-lite/agents/planner.md`, the rules under `## Criteria that can pass` are numbered 1 to 10 with no gaps, and the text holds no stale "rule 6" or "rule 7" reference to the replan rules.

## Risks
- Rule 3 of the ticket (aggregate budget ownership) is semantic, so it is a planner prompt rule plus a check.py text guard, not a lint. The ticket's "each lintable" holds only for rules 1 and 2.
- Both lints are heuristics on raw span text:
  - A legit criterion that names a specific commit on purpose (for example `git merge-base --is-ancestor <real sha> HEAD`) will now be refused as a plan defect.
  - A count over a single file that happens to contain `*` in a regex, compared with 2 or more, will also be refused.
  - The criteria above avoid literal hex runs and literal set counts, so this plan stays lint-clean under the new rules on a replan.
- The check.sh guard takes about 170s against the 300s `--guard-timeout`. A loaded host could time it out at `split --only 1`, which would be a false plan defect.
- The renumbering in planner.md changes the rule numbers other docs might cite. The builder must grep for "rule 6" and "rule 7" across `plugins/sdlc-lite` and `CLAUDE.md`.
