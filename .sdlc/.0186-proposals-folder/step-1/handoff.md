## Task goal
Repeated failures in past runs become evidence-backed candidate proposals in a folder, and nothing is applied without an eval.

## Step 1: Add proposals.py with scan, list, show, the three transitions, and its selftest
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: none.

Create `plugins/sdlc-lite/scripts/proposals.py`:
- Executable (`chmod +x`), shebang `#!/usr/bin/env python3`, standard library only, Python 3.9 compatible (the host runs 3.9.6: no `X | Y` annotations, no `match`), no em dashes. The module docstring documents the file format and the CLI. `main()` runs only under `if __name__ == '__main__'`.
- Set `sys.dont_write_bytecode = True` at module level, so loading evals.py never writes a `__pycache__` under `plugins/` (step 2 hashes `plugins/` before and after a live scan).
- Import no plugin script at module level. Load `<plugin>/scripts/evals.py` with `importlib.util.spec_from_file_location` only inside `accept`, and call its declared API `validate_eval(path, repo)` (evals.py docstring, "Python API"; T-0185 named this caller). Run `<plugin>/scripts/tickets.py` as a subprocess in `promote`. A mutant copy in a temp dir then still finds both through `--plugin`.

In `plugins/sdlc-lite/scripts/check.sh`, add `python3 "$root/scripts/proposals.py" selftest || fail=1` after the `evals.py` line, and add `proposals.py` after `evals.py` in the header comment's list of selftests. Nothing else pins check.sh (`git grep` over `plugins` and `scripts`), and evals.py and tickets.py are only called, never changed.

Global options come before the subcommand, as in `evals.py [--root DIR] [--plugin DIR] <cmd>`:
- `--root DIR`: the `.sdlc` folder, default `.sdlc`. The repo dir is the resolved `<root>`'s parent. Every path proposals.py writes (evidence, pattern subjects, `eval`) is relative to the repo dir in posix form. Resolve both sides first, because macOS `mktemp -d` paths sit under the `/var` to `/private/var` symlink.
- `--proposals DIR`: where proposals live, default `<root>/proposals`. Step 2 uses it to scan this repository's `.sdlc/` read-only while writing the candidates to a temp dir.
- `--plugin DIR`: the dir holding `scripts/evals.py` and `scripts/tickets.py`, default the parent of this script's dir.

Sources and walk:
- `scan` walks `<root>` with `os.walk`: names sorted, symlinks not followed, dot folders included (closed tickets are `.NNNN-<slug>`). It skips the top-level `proposals`, `messages`, `runtime`, and `dogfood` dirs and the `--proposals` dir. The last three are git-ignored (`.gitignore`) and are not records.
- Every source read goes through this one helper, so the read-only mutant has exactly one line to target:

  ```
  def read_source(path):
      """The text of one source file (a role result, a runs.jsonl, or notes.md). Never writes."""
      return Path(path).read_text(encoding='utf-8', errors='replace')  # rule: read-only
  ```

- `runs.jsonl` files: each line goes through `json.loads`. A blank or unparsable line, a non-object, or a line whose `role` or `level` is not a string is skipped. `file` is optional: 166 of this repository's 1073 run lines have none (counted).
- Role results: file names that fullmatch `(builder|verifier)-L[1-5](-[A-Za-z0-9-]+)?\.md`. This takes `verifier-L1-2.md` and the legacy `verifier-L1-attempt1.md`, and never `fresh-filer-L1.md` (both exist under `.sdlc`). Sections parse as in results.py: a heading matches when `line.rstrip() == '## <Name>'`, its body runs to the next line starting with `## `, and its key value is the first non-blank body line, stripped and lowercased. A verifier failed when the `## Verdict` key value is `fail`. A builder is blocked when the `## Status` key value is `blocked`.
- `<root>/notes.md`: lines that fullmatch `- (fix-now|decide):[ \t]*(\S.*)`, with the tag matched case-insensitively and stored lowercased. This is the form `tickets.py close` appends (tickets.py docstring: one `- <tag>: <text>` line per item under `## <id>: <title> (<date>)`).
- Text helpers:
  - `clean(t)` replaces each U+2014 em dash with `-`, then collapses whitespace runs to one space and strips.
  - A quote is `clean(text)`, cut to `text[:157].rstrip() + '...'` when longer than 160 characters. A title part is cut the same way at 60 (`[:57]`).
  - `drop(line)` strips the line and removes one leading `- ` or `* `.
- A subject path is the repo-relative dir, with the leading dot dropped from each path component that fullmatches `\.\d{4}-.+`. A ticket folder renamed on close (`tickets.py close` renames `NNNN-<slug>` to `.NNNN-<slug>`) then keeps its pattern. Evidence paths stay real.

Patterns. `KINDS` is this tuple, in this order: `verifier-fail`, `replan`, `builder-bump`, `next-attempt`, `plan-defect`, `follow-up`. Each kind collects occurrences under a key, and a key with two or more occurrences becomes a candidate. The `pattern` value is `<kind> <subject>`, or the bare kind `plan-defect`. One evidence line per occurrence, `- <path>:<line> (<where>) "<quote>"`, with a 1-based line number. Evidence lines sort by (path, line number).

| kind | subject (the key) | one occurrence | where | quote |
|---|---|---|---|---|
| `verifier-fail` | the dir holding the result | a verifier result there with Verdict `fail`; the line is the key value's | `## Verdict` | `fail` |
| `replan` | the dir holding the runs.jsonl | a line with `role` `planner` | `run` | `role=<role> level=<level>`, plus ` file=<file>` when `file` is a non-empty string |
| `builder-bump` | the dir holding the runs.jsonl | the first line of each distinct `level` among `role` `builder` lines, so two levels are a bump | `run` | as for `replan` |
| `next-attempt` | the normalized text | per dir, the first verifier result in name order whose `## For the next attempt` normalizes to it; the line is the first non-blank body line | `## For the next attempt` | the joined text |
| `plan-defect` | none: one global pattern | each line whose `drop()` starts with `plan defect:`, in a verifier result with Verdict `fail` or a builder result with Status `blocked` | the nearest `## ` line above, rstripped, else `(top)` | the `drop()` text |
| `follow-up` | `<tag> <clean(text).lower()>` | each matching notes.md line | the nearest `## ` line above, rstripped, else `(top)` | the line without its leading `- ` |

- Next-attempt joined text: each body line through `drop()`, the non-empty ones joined with one space, then `clean()`. Any verdict counts. The normalized text is the joined text lowercased. Skip it when it is empty or `re.match(r'none(\.(\s|$)|$)', text)` holds (tickets.py `is_none`), so the usual `None` never forms a pattern.
- The `plan-defect` filter keeps prose mentions out: `.sdlc/.0085-port-thinking-depth/step-1/*.md` quote `plan defect:` mid-sentence in passing results.

Proposal file:
- The path is `<proposals>/<slug>/proposal.md`. The slug is `<kind>-<first 8 hex of sha256(pattern in UTF-8)>`. When that folder already holds a proposal.md, add the first free `-<k>` suffix from 2.
- Front matter `FIELDS`, in this order: `id`, `title`, `status`, `pattern`, `occurrences`, `created`, `eval`, `accepted`, `rejected`, `reason`, `promoted`, `ticket`.
  - The first seven are always written. `eval` is empty on a candidate and is written as the bare line `eval:`, with no trailing space.
  - Each later field is written only once stamped.
  - Values are bare and one line.
- Parse: a `---` line, one line per field that fullmatches `([a-z]+):(?: (.*))?`, a `---` line, then the body.
- Titles, fixed at creation:
  - `verifier-fail`: `Repeated verifier fails in <subject>`
  - `replan`: `Repeated planner runs in <subject>`
  - `builder-bump`: `Builder level bump in <subject>`
  - `next-attempt`: `Repeated next-attempt advice: <quote of the first evidence line, cut at 60>`
  - `plan-defect`: `Repeated plan defect verdicts`
  - `follow-up`: `Repeated <tag> follow-up: <clean(text) of the first evidence line, cut at 60>`
- Proposed change, fixed at creation: one line saying what to examine, never a patch.
  - `verifier-fail`: `Examine why this step failed verification more than once: its criteria, its level, or its handoff.`
  - `replan`: `Examine what the first plan missed and whether a planner rule or the level rubric would have caught it.`
  - `builder-bump`: `Examine why the lower builder level could not finish this step and whether the planner picked too low a level.`
  - `next-attempt`: `Examine whether this repeated advice belongs in a role contract or a planner rule.`
  - `plan-defect`: `Examine the planner rules behind these criteria and whether steps.py lint could refuse them.`
  - `follow-up`: `Examine whether this repeated follow-up needs one ticket or a rule instead of more notes.`
- The exact text, for two `fail` verifier results in `.sdlc/a/step-1` (the sha256 prefix of `verifier-fail .sdlc/a/step-1` is `87151acc`, so the folder is `verifier-fail-87151acc`):

  ```
  ---
  id: P-0001
  title: Repeated verifier fails in .sdlc/a/step-1
  status: candidate
  pattern: verifier-fail .sdlc/a/step-1
  occurrences: 2
  created: 2026-10-04
  eval:
  ---

  ## Evidence

  - .sdlc/a/step-1/verifier-L1-2.md:2 (## Verdict) "fail"
  - .sdlc/a/step-1/verifier-L1.md:2 (## Verdict) "fail"

  ## Proposed change

  Examine why this step failed verification more than once: its criteria, its level, or its handoff.
  ```

- A proposal is invalid for the first of these reasons, in order:
  - `no front matter`
  - `bad front matter line <n>`
  - `unknown field <name>`
  - `duplicate field <name>`
  - `missing field <name>`, for an empty `id`, `title`, `status`, `pattern`, `occurrences`, or `created`
  - `bad field <name>: <value>`: an `id` not `P-\d{4}`, a `status` other than `candidate`, `accepted`, `rejected`, `promoted`, an `occurrences` that is not digits, a `created` that `datetime.date.fromisoformat` refuses, or a `pattern` whose first word is not in `KINDS`
  - `missing ## Evidence`, `missing ## Proposed change`

`scan`:
- It loads every `<proposals>/*/proposal.md`. An invalid one, or an `id` used twice, refuses: `proposals.py: <repo-relative path>: <reason>` on stderr, exit 1, nothing written.
- It visits the collected patterns sorted by (`KINDS` index, pattern):
  - `if len(evidence) < 2:  # rule: threshold` skips the pattern.
  - `if pattern in known:  # rule: known` updates the known proposal. It re-renders the file with `occurrences` set to the number of evidence lines and the new evidence, keeping every other field and the existing `## Proposed change` text. It writes only when the bytes differ (`updated`); otherwise the proposal is `unchanged`. scan never changes a status.
  - Otherwise it creates a proposal: `id` is `P-%04d`, one above the highest existing id (`P-0001` first); `status` is `candidate`; `created` is today; `eval` is empty.
- It creates the proposals dir only when it writes a proposal. It never deletes a proposal, and it leaves a known pattern that fell below two occurrences as it is.
- Every proposal write goes through one helper that raises on a path outside the proposals dir.
- Output lines, exact: `new <id> <folder> (<n> occurrences)`, `updated <id> <folder> (<n> occurrences)`, and a last line `proposals scan: <a> new, <b> updated, <c> unchanged`. Exit 0.

`list` prints one tab-separated line per proposal, sorted by id and then folder: `<id>`, `<status>`, `<occurrences>`, `<folder>`, `<title>`. An invalid proposal prints `<folder>\tinvalid: <reason>`. It always exits 0, including with no proposals dir.

`show <id>` writes the proposal.md text to stdout unchanged.

`show`, `accept`, `reject`, and `promote` look an id up among the valid proposals: none gives `no proposal <id>`, two give `id <id> is used twice: <path>, <path>`.

Transitions:
- The allowed moves are `FORWARD = {('candidate', 'accepted'), ('candidate', 'rejected'), ('accepted', 'promoted')}`.
- All three commands first call one helper whose test is `if (cur, new) not in FORWARD:  # rule: forward`, refusing with `cannot move <id> from <cur> to <new>`. This one rule refuses promote before accept and every backward move.
- No command moves a proposal to `candidate` or applies anything.
- `accept <id> [--eval PATH]`:
  - `--eval` is optional in argparse, so the refusal is a code rule that a mutant can remove. A required flag would exit 2 before any rule runs.
  - PATH resolves from the cwd. The first problem, in this order:
    1. `no eval given: pass --eval <file in .sdlc/evals/>` (the evals dir, repo-relative)
    2. `no such eval: <PATH>`
    3. `eval <PATH> is not in .sdlc/evals/`, when its resolved parent is not `<root>/evals` resolved
    4. `invalid eval <PATH>: <validate_eval reason>`
  - `if reason:  # rule: eval` refuses.
  - On success it stamps `status: accepted`, `eval: <repo-relative path>`, and `accepted: <today>`, and prints `accepted <id> (eval <path>)`.
- `reject <id> [--reason TEXT]`:
  - `--reason` is optional in argparse for the same reason. The text is `clean(reason or '')`.
  - `if not text:  # rule: reason` refuses with `reject needs --reason TEXT`.
  - On success it stamps `status: rejected`, `rejected: <today>`, and `reason: <text>`, and prints `rejected <id>`.
- `promote <id>`:
  1. Apply the forward rule.
  2. Run `[sys.executable, <plugin>/scripts/tickets.py, '--root', <root as given>, 'new', 'idea', <folder name>, <title>]`. A nonzero exit refuses with `tickets.py new failed: <its stderr, stripped>`, and the proposal stays unchanged.
  3. The last non-blank stdout line is the new handoff path. Read its `id:` line.
  4. Replace the `## Goal` body with the Proposed change line and the `## Context` body with the block below. A section the template lacks is appended at the end. `new` has already regenerated the roadmap, which reads front matter only.
  5. Stamp `status: promoted`, `promoted: <today>`, and `ticket: <T-id>`, and print `promoted <id> as <T-id> (<repo-relative handoff path>)`.

  The CLI is used rather than `cmd_new(context=)`, because the handoff names `tickets.py new idea` and `cmd_new` is internal. The Context block:

  ```
  From proposal <id> (`<repo-relative proposal path>`): pattern `<pattern>`, <occurrences> occurrences, accepted with eval `<eval>`.

  Evidence:

  <the proposal's evidence lines, unchanged>
  ```

Exit codes: 0 for ok, 1 for a refusal, 2 for an argparse usage error. Refusals print `proposals.py: <reason>` on stderr.

`selftest` uses temp dirs only. Every command runs as a subprocess of this file (or of a mutant) with explicit `--root` and `--plugin <the real plugin dir>`. It prints `ok: <name>` per case, then `proposals selftest: PASS`, and exits 0. Otherwise it prints `FAIL: <name>: <detail>` per miss, then `proposals selftest: FAIL`, and exits 1.

The seeded project for case 1 holds exactly one instance of each kind:
- a step with two `fail` verifier results
- a task runs.jsonl with two planner lines
- a step runs.jsonl with builder lines at L2, L2, and L3
- two step dirs whose verifier `## For the next attempt` texts differ only in case, spacing, and a list marker
- a blocked builder and a failing verifier that each hold a `plan defect:` line
- a notes.md with the same `decide:` text under two headings

It also holds a single instance of each kind that must not form a candidate: one fail in another step, one planner line, one `fix-now:` line, and a passing verifier with a `plan defect:` line.

The case names, exactly:
1. `scan files one candidate per seeded pattern with its evidence lines`: exactly six proposals, `P-0001` to `P-0006` in `KINDS` order, each file's whole text equal to the expected text.
2. `a pattern seen once files no candidate`: a project with one occurrence of each kind gives `proposals scan: 0 new, 0 updated, 0 unchanged`, and the proposals dir is not created.
3. `a second scan leaves the tree byte-identical`: every path and sha256 in the case 1 project is unchanged, and the output ends `0 new, 0 updated, 6 unchanged`.
4. `scan updates a known pattern instead of duplicating it`: after a third fail result is added to the step, a rescan prints `updated P-0001`, and the file has `occurrences: 3`, three evidence lines, the same `id`, `title`, and `created`, and still six proposal folders.
5. `scan keeps the pattern of a ticket folder renamed on close`: a replan in `NNNN-x/` is scanned, the folder is renamed to `.NNNN-x/`, and a rescan updates the same proposal. Its `pattern` is unchanged, and its evidence paths now start with `.sdlc/.NNNN-x/`.
6. `scan writes only under the proposals dir`: after scan, list, show, accept, and reject, every file outside the proposals dir is byte-identical, and none was added.
7. `scan with --proposals writes there and nothing under the root`
8. `scan refuses an invalid proposal and writes nothing`: a proposal.md without front matter gives exit 1, the path, and `no front matter`, with the tree unchanged. `list` prints its `invalid:` line and exits 0.
9. `list and show print the proposals`: the exact list lines in id order. `show` prints the file text. An unknown id exits 1 with `no proposal`.
10. `accept without an eval is refused`
11. `accept with a missing eval file is refused`
12. `accept with an eval outside the evals folder is refused`: a valid eval text written outside `<root>/evals`.
13. `accept with an invalid eval is refused`
14. `accept with a valid eval stamps status, eval, and date`: `status: accepted`, `eval: .sdlc/evals/<file>`, and `accepted: <today>`, with every other line unchanged.
15. `reject without a reason is refused`
16. `reject with a reason stamps status, reason, and date`
17. `promote before accept is refused`: exit 1 with `cannot move`, no ticket folder, no `roadmap.md`, and the proposal byte-identical.
18. `promote after accept files an idea ticket and records its id`:
    - The handoff has `id: T-0001`, `type: idea`, the title, the Proposed change under `## Goal`, and the evidence lines under `## Context`.
    - The proposal has `status: promoted`, `promoted: <today>`, and `ticket: T-0001`.
    - `tickets.py --root <root> check` exits 0.
19. `a backward move is refused`: accept on a promoted proposal, accept on a rejected one, reject on an accepted one, reject on a promoted one, and promote on a rejected one. Each exits 1 with `cannot move`, and the proposal is byte-identical.
20. `no command changes a source file`: the sha256 of every runs.jsonl, role result, and notes.md in every fixture project, after every subprocess. It runs last and is reported in 20th place.
21. `negative control: without the eval rule accept passes with no eval`: the mutant's `accept P-0001` with no `--eval` exits 0, and the file says `status: accepted`.
22. `negative control: without the reason rule reject passes with no reason`
23. `negative control: without the forward rule promote passes on a candidate`
24. `negative control: without the forward rule accept passes on a promoted proposal`
25. `negative control: without the threshold a pattern seen once files a candidate`: case 2's project.
26. `negative control: without the known-pattern match a second scan duplicates`: a second proposal with the same `pattern:` line appears.
27. `negative control: a proposals.py that writes a source file fails the source check`: the helper case 20 uses reports at least one changed source after the mutant's scan.

Hash tracking for case 20, as evals.py's `track()` does:
- The selftest's own fixture edits (case 4's third fail result, case 5's folder rename, any fixture written between commands) re-baseline the tracked hashes, so case 20 reports only writes made by a proposals.py run.
- Case 27's mutant runs on its own fixture project, which case 20 does not track. Case 27 asserts the change through the same manifest helper, not through case 20's violation list.

Each negative control:
1. Write a copy of this file's text to a temp dir. For an `if` rule, replace the whole marked line, matched by a regex from `if <cond>:` to its marker, with `if False:` and the same marker.
2. For the read-only rule, replace the marked `return <expr>` line with `t = <expr>; Path(path).write_text(t + 'x', encoding='utf-8'); return t`, keeping the indent.
3. Assert that exactly one line matched, so a rule that moved fails the control loudly.
4. Run the copy with `--plugin <the real plugin dir>` on the case's fixture, after first showing that the real script refuses or keeps that fixture.

Build each marker string by concatenation (`'# rule' + ': eval'`), so the selftest's own text holds no copy of it. The markers are `threshold`, `known`, `forward`, `eval`, `reason`, and `read-only`, each on exactly one line.

Focused checks: `python3 plugins/sdlc-lite/scripts/proposals.py selftest`, and the criteria below. Probes 3 to 9 passed against a throwaway prototype of this spec in `/tmp`, and they failed when its threshold or eval rule was removed.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/proposals.py selftest`
- `out=$(python3 plugins/sdlc-lite/scripts/proposals.py selftest) && for n in "scan files one candidate per seeded pattern with its evidence lines" "a pattern seen once files no candidate" "a second scan leaves the tree byte-identical" "scan updates a known pattern instead of duplicating it" "scan keeps the pattern of a ticket folder renamed on close" "scan writes only under the proposals dir" "scan with --proposals writes there and nothing under the root" "scan refuses an invalid proposal and writes nothing" "list and show print the proposals" "accept without an eval is refused" "accept with a missing eval file is refused" "accept with an eval outside the evals folder is refused" "accept with an invalid eval is refused" "accept with a valid eval stamps status, eval, and date" "reject without a reason is refused" "reject with a reason stamps status, reason, and date" "promote before accept is refused" "promote after accept files an idea ticket and records its id" "a backward move is refused" "no command changes a source file" "negative control: without the eval rule accept passes with no eval" "negative control: without the reason rule reject passes with no reason" "negative control: without the forward rule promote passes on a candidate" "negative control: without the forward rule accept passes on a promoted proposal" "negative control: without the threshold a pattern seen once files a candidate" "negative control: without the known-pattern match a second scan duplicates" "negative control: a proposals.py that writes a source file fails the source check"; do printf '%s\n' "$out" | grep -qxF "ok: $n" || exit 1; done`
- `t=$(mktemp -d) && P=plugins/sdlc-lite/scripts/proposals.py && mkdir -p "$t/.sdlc/a/step-1" "$t/.sdlc/b/step-1" && printf '## Verdict\nfail\n' >"$t/.sdlc/a/step-1/verifier-L1.md" && cp "$t/.sdlc/a/step-1/verifier-L1.md" "$t/.sdlc/a/step-1/verifier-L1-2.md" && cp "$t/.sdlc/a/step-1/verifier-L1.md" "$t/.sdlc/b/step-1/verifier-L1.md" && python3 "$P" --root "$t/.sdlc" scan >/dev/null && f="$t/.sdlc/proposals/verifier-fail-$(printf %s 'verifier-fail .sdlc/a/step-1' | shasum -a 256 | cut -c1-8)/proposal.md" && for l in 'id: P-0001' 'title: Repeated verifier fails in .sdlc/a/step-1' 'status: candidate' 'pattern: verifier-fail .sdlc/a/step-1' 'occurrences: 2' "created: $(date +%F)" 'eval:' '## Evidence' '- .sdlc/a/step-1/verifier-L1-2.md:2 (## Verdict) "fail"' '- .sdlc/a/step-1/verifier-L1.md:2 (## Verdict) "fail"' '## Proposed change'; do grep -qxF -- "$l" "$f" || exit 1; done && test -z "$(find "$t/.sdlc/proposals" -name proposal.md ! -path "$f")" && h=$(find "$t" -type f -exec shasum {} + | sort) && python3 "$P" --root "$t/.sdlc" scan >/dev/null && test "$h" = "$(find "$t" -type f -exec shasum {} + | sort)"`
- `t=$(mktemp -d) && P=plugins/sdlc-lite/scripts/proposals.py && mkdir -p "$t/.sdlc/c/step-1" && printf '%s\n' '{"role":"planner","level":"L2","file":"planner-L2.md"}' '{"role":"planner","level":"L3"}' >"$t/.sdlc/c/runs.jsonl" && printf '%s\n' '{"role":"builder","level":"L2","file":"builder-L2.md"}' '{"role":"builder","level":"L2","file":"builder-L2-2.md"}' '{"role":"builder","level":"L3","file":"builder-L3.md"}' >"$t/.sdlc/c/step-1/runs.jsonl" && python3 "$P" --root "$t/.sdlc" scan >/dev/null && r="$t/.sdlc/proposals/replan-$(printf %s 'replan .sdlc/c' | shasum -a 256 | cut -c1-8)/proposal.md" && b="$t/.sdlc/proposals/builder-bump-$(printf %s 'builder-bump .sdlc/c/step-1' | shasum -a 256 | cut -c1-8)/proposal.md" && for l in 'id: P-0001' 'title: Repeated planner runs in .sdlc/c' 'pattern: replan .sdlc/c' 'occurrences: 2' '- .sdlc/c/runs.jsonl:1 (run) "role=planner level=L2 file=planner-L2.md"' '- .sdlc/c/runs.jsonl:2 (run) "role=planner level=L3"'; do grep -qxF -- "$l" "$r" || exit 1; done && for l in 'id: P-0002' 'title: Builder level bump in .sdlc/c/step-1' 'pattern: builder-bump .sdlc/c/step-1' 'occurrences: 2' '- .sdlc/c/step-1/runs.jsonl:1 (run) "role=builder level=L2 file=builder-L2.md"' '- .sdlc/c/step-1/runs.jsonl:3 (run) "role=builder level=L3 file=builder-L3.md"'; do grep -qxF -- "$l" "$b" || exit 1; done && ! grep -qF 'runs.jsonl:2' "$b"`
- `t=$(mktemp -d) && P=plugins/sdlc-lite/scripts/proposals.py && mkdir -p "$t/.sdlc/d/step-1" "$t/.sdlc/d/step-2" "$t/.sdlc/e/step-1" "$t/.sdlc/e/step-2" "$t/.sdlc/e/step-3" && printf '## Verdict\nfail\n\n## For the next attempt\nRerun  the gate first.\n' >"$t/.sdlc/d/step-1/verifier-L1.md" && printf '## Verdict\npass\n\n## For the next attempt\n- rerun the gate FIRST.\n' >"$t/.sdlc/d/step-2/verifier-L2.md" && printf '## Status\nblocked\n\n## Notes\nplan defect: the scope guard misses a path.\n' >"$t/.sdlc/e/step-1/builder-L2.md" && printf '## Verdict\nfail\n\n## Criteria\n- plan defect: criterion 2 is stale.\n' >"$t/.sdlc/e/step-2/verifier-L1.md" && printf '## Verdict\npass\n\n## Criteria\nplan defect: not counted on a pass.\n' >"$t/.sdlc/e/step-3/verifier-L1.md" && python3 "$P" --root "$t/.sdlc" scan >/dev/null && n="$t/.sdlc/proposals/next-attempt-$(printf %s 'next-attempt rerun the gate first.' | shasum -a 256 | cut -c1-8)/proposal.md" && d="$t/.sdlc/proposals/plan-defect-$(printf %s 'plan-defect' | shasum -a 256 | cut -c1-8)/proposal.md" && for l in 'id: P-0001' 'title: Repeated next-attempt advice: Rerun the gate first.' 'pattern: next-attempt rerun the gate first.' 'occurrences: 2' '- .sdlc/d/step-1/verifier-L1.md:5 (## For the next attempt) "Rerun the gate first."' '- .sdlc/d/step-2/verifier-L2.md:5 (## For the next attempt) "rerun the gate FIRST."'; do grep -qxF -- "$l" "$n" || exit 1; done && for l in 'id: P-0002' 'title: Repeated plan defect verdicts' 'pattern: plan-defect' 'occurrences: 2' '- .sdlc/e/step-1/builder-L2.md:5 (## Notes) "plan defect: the scope guard misses a path."' '- .sdlc/e/step-2/verifier-L1.md:5 (## Criteria) "plan defect: criterion 2 is stale."'; do grep -qxF -- "$l" "$d" || exit 1; done && ! grep -qF 'not counted' "$d"`
- `t=$(mktemp -d) && P=plugins/sdlc-lite/scripts/proposals.py && mkdir -p "$t/.sdlc" && printf '# Notes\n\n## T-0001: One (2026-10-01)\n\n- decide: Pick  a format\n\n## T-0002: Two (2026-10-02)\n\n- decide: pick a FORMAT\n- fix-now: only once\n' >"$t/.sdlc/notes.md" && python3 "$P" --root "$t/.sdlc" --proposals "$t/out" scan >/dev/null && test ! -e "$t/.sdlc/proposals" && f="$t/out/follow-up-$(printf %s 'follow-up decide pick a format' | shasum -a 256 | cut -c1-8)/proposal.md" && for l in 'id: P-0001' 'title: Repeated decide follow-up: Pick a format' 'pattern: follow-up decide pick a format' 'occurrences: 2' '- .sdlc/notes.md:5 (## T-0001: One (2026-10-01)) "decide: Pick a format"' '- .sdlc/notes.md:9 (## T-0002: Two (2026-10-02)) "decide: pick a FORMAT"'; do grep -qxF -- "$l" "$f" || exit 1; done && test -z "$(find "$t/out" -name proposal.md ! -path "$f")" && python3 "$P" --root "$t/.sdlc" --proposals "$t/out" list | grep -qxF "$(printf 'P-0001\tcandidate\t2\t%s\tRepeated decide follow-up: Pick a format' "$(basename "$(dirname "$f")")")"`
- `t=$(mktemp -d) && P=plugins/sdlc-lite/scripts/proposals.py && mkdir -p "$t/.sdlc/a/step-1" "$t/.sdlc/evals" "$t/x" && printf '## Verdict\nfail\n' >"$t/.sdlc/a/step-1/verifier-L1.md" && cp "$t/.sdlc/a/step-1/verifier-L1.md" "$t/.sdlc/a/step-1/verifier-L1-2.md" && printf -- '---\nrole: builder\n---\n' >"$t/.sdlc/evals/0000-bad.md" && printf -- '---\nrole: builder\nlevel: L2\nmodel: opus\neffort: low\nhost: claude\ntask_set: s\npass_rate: 1/1\ncost_usd: unknown\ndate: 2026-10-01\nevidence: https://example.com/e\n---\n## Method\n\nm\n\n## Result\n\nr\n' >"$t/x/0001-ok.md" && python3 "$P" --root "$t/.sdlc" scan >/dev/null && f="$t/.sdlc/proposals/verifier-fail-$(printf %s 'verifier-fail .sdlc/a/step-1' | shasum -a 256 | cut -c1-8)/proposal.md" && cp "$f" "$t/before" || exit 1; for c in "|no eval given" "$t/.sdlc/evals/0009-none.md|no such eval" "$t/x/0001-ok.md|is not in" "$t/.sdlc/evals/0000-bad.md|invalid eval"; do e=${c%%|*}; w=${c#*|}; if test -n "$e"; then out=$(python3 "$P" --root "$t/.sdlc" accept P-0001 --eval "$e" 2>&1); else out=$(python3 "$P" --root "$t/.sdlc" accept P-0001 2>&1); fi; test $? -eq 1 || exit 1; printf '%s\n' "$out" | grep -qF "$w" || exit 1; done; cmp -s "$t/before" "$f"`
- `t=$(mktemp -d) && P=plugins/sdlc-lite/scripts/proposals.py && mkdir -p "$t/.sdlc/a/step-1" "$t/.sdlc/evals" && printf '## Verdict\nfail\n' >"$t/.sdlc/a/step-1/verifier-L1.md" && cp "$t/.sdlc/a/step-1/verifier-L1.md" "$t/.sdlc/a/step-1/verifier-L1-2.md" && printf -- '---\nrole: builder\nlevel: L2\nmodel: opus\neffort: low\nhost: claude\ntask_set: s\npass_rate: 1/1\ncost_usd: unknown\ndate: 2026-10-01\nevidence: https://example.com/e\n---\n## Method\n\nm\n\n## Result\n\nr\n' >"$t/.sdlc/evals/0000-ok.md" && python3 "$P" --root "$t/.sdlc" scan >/dev/null && s=verifier-fail-$(printf %s 'verifier-fail .sdlc/a/step-1' | shasum -a 256 | cut -c1-8) && f="$t/.sdlc/proposals/$s/proposal.md" || exit 1; python3 "$P" --root "$t/.sdlc" promote P-0001 >/dev/null 2>&1; test $? -eq 1 || exit 1; test ! -e "$t/.sdlc/$s" || exit 1; python3 "$P" --root "$t/.sdlc" accept P-0001 --eval "$t/.sdlc/evals/0000-ok.md" >/dev/null && grep -qxF 'status: accepted' "$f" && grep -qxF 'eval: .sdlc/evals/0000-ok.md' "$f" && grep -qxF "accepted: $(date +%F)" "$f" && python3 "$P" --root "$t/.sdlc" promote P-0001 >/dev/null && grep -qxF 'status: promoted' "$f" && grep -qxF "promoted: $(date +%F)" "$f" && grep -qxF 'ticket: T-0001' "$f" && h="$t/.sdlc/$s/handoff.md" && grep -qxF 'id: T-0001' "$h" && grep -q '^type: idea' "$h" && grep -qxF 'title: "Repeated verifier fails in .sdlc/a/step-1"' "$h" && grep -qF -- '- .sdlc/a/step-1/verifier-L1.md:2 (## Verdict) "fail"' "$h" && cp "$f" "$t/before" || exit 1; python3 "$P" --root "$t/.sdlc" accept P-0001 --eval "$t/.sdlc/evals/0000-ok.md" >/dev/null 2>&1; test $? -eq 1 || exit 1; cmp -s "$t/before" "$f"`
- `t=$(mktemp -d) && P=plugins/sdlc-lite/scripts/proposals.py && mkdir -p "$t/.sdlc/a/step-1" "$t/.sdlc/evals" && printf '## Verdict\nfail\n' >"$t/.sdlc/a/step-1/verifier-L1.md" && cp "$t/.sdlc/a/step-1/verifier-L1.md" "$t/.sdlc/a/step-1/verifier-L1-2.md" && printf '%s\n' '{"role":"planner","level":"L2"}' '{"role":"planner","level":"L3"}' >"$t/.sdlc/a/runs.jsonl" && printf '# Notes\n\n## T-0001: One (2026-10-01)\n\n- decide: x\n- decide: x\n' >"$t/.sdlc/notes.md" && printf -- '---\nrole: builder\nlevel: L2\nmodel: opus\neffort: low\nhost: claude\ntask_set: s\npass_rate: 1/1\ncost_usd: unknown\ndate: 2026-10-01\nevidence: https://example.com/e\n---\n## Method\n\nm\n\n## Result\n\nr\n' >"$t/.sdlc/evals/0000-ok.md" && src=$(find "$t/.sdlc/a" "$t/.sdlc/notes.md" -type f -exec shasum {} + | sort) && python3 "$P" --root "$t/.sdlc" scan >/dev/null && f="$t/.sdlc/proposals/verifier-fail-$(printf %s 'verifier-fail .sdlc/a/step-1' | shasum -a 256 | cut -c1-8)/proposal.md" && cp "$f" "$t/before" || exit 1; python3 "$P" --root "$t/.sdlc" reject P-0001 >/dev/null 2>&1; test $? -eq 1 || exit 1; cmp -s "$t/before" "$f" || exit 1; python3 "$P" --root "$t/.sdlc" reject P-0001 --reason 'not worth it' >/dev/null && grep -qxF 'status: rejected' "$f" && grep -qxF 'reason: not worth it' "$f" && grep -qxF "rejected: $(date +%F)" "$f" && cp "$f" "$t/before" || exit 1; python3 "$P" --root "$t/.sdlc" accept P-0001 --eval "$t/.sdlc/evals/0000-ok.md" >/dev/null 2>&1; test $? -eq 1 || exit 1; cmp -s "$t/before" "$f" && python3 "$P" --root "$t/.sdlc" list >/dev/null && python3 "$P" --root "$t/.sdlc" show P-0002 >/dev/null && python3 "$P" --root "$t/.sdlc" accept P-0002 --eval "$t/.sdlc/evals/0000-ok.md" >/dev/null && python3 "$P" --root "$t/.sdlc" promote P-0002 >/dev/null && python3 "$P" --root "$t/.sdlc" scan >/dev/null && test "$src" = "$(find "$t/.sdlc/a" "$t/.sdlc/notes.md" -type f -exec shasum {} + | sort)"`
- `test -x plugins/sdlc-lite/scripts/proposals.py && grep -qF 'scripts/proposals.py" selftest' plugins/sdlc-lite/scripts/check.sh`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/proposals.py -e plugins/sdlc-lite/scripts/check.sh | { ! grep -q .; }`
