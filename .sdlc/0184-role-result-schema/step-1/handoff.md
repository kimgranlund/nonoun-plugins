## Task goal
Every role result file is validated against one declared schema before the pipeline advances, and a malformed result is refused so the pipeline does not move.

## Step 1: Add results.py with the schema table, validator, CLI, and selftest
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Create `plugins/sdlc-lite/scripts/results.py` (python3, stdlib only, executable, no em dashes) and wire its selftest into `plugins/sdlc-lite/scripts/check.sh`. Depends on: none.

Settled table `SCHEMA` (the only copy in the repo). Each role has `key` (the gating section), `allowed` (tuples of token, regex, display; empty for roles with no allowed set) and `sections` (the declared output order, taken from the `## ` lines of each `agents/<role>.md` output template):
- builder: key Status; allowed done, blocked, and inherited (regex `inherited red: .+`, display `inherited red: <tests>`); sections Status, Changes, Checks, Notes
- verifier: key Verdict; allowed pass, fail, inherited (same regex and display); sections Verdict, Criteria, Out of scope changes, For the next attempt
- plan-reviewer: key Verdict; allowed pass, replan, blocked; sections Verdict, Findings, Missing decisions
- planner: key Goal; sections Goal, Assumptions, Risks (`## Step <n>: ...` headings are not declared and are ignored)
- researcher: key Answer; sections Answer, Findings, Conflicts and gaps
- scout: key Map; sections Map, Entry points, Not found
- archaeologist: key Summary; sections Summary, Decisions, Landmines, Inferred
- architect: key Approach; sections Approach, Interfaces, Constraints and assumptions, Rejected alternatives, Risks
- filer: key Warnings; sections Warnings, PR title, PR body, Changelog entry, Follow-ups

Only the key section is required to be present. Every other declared section is optional, but when two or more declared sections are present, their first occurrences must follow the declared order. Evidence that keeps every previously valid result valid:
- `run-selftest.sh` lines 256 to 276 pin `## Verdict\npass` alone and `## Status\ninherited red: test_a` alone as exit 0.
- A scan of all 8645 result files under `.sdlc/` and `.worktrees/*/.sdlc/` of the main checkout with these exact rules found 0 order violations, 0 missing key sections, and 0 disallowed values. The only failures are copies of one closed history file (see Assumptions).

Parsing rules (they match `run.sh` lines 472 to 482 and `steps.py` `section()` at line 942):
- A heading matches when `line.rstrip() == '## <Name>'`.
- A key section's body runs to the next line starting with `## `.
- Its value is the first non-blank line, stripped and lowercased, and must `re.fullmatch` one allowed regex.
- An empty key body passes for roles with no allowed set (as `run.sh` accepts today).

Header rule: the first line, rstripped, must fullmatch this regex:

```
^<!-- role=([a-z-]+) level=(L[1-5]) model=(\S+) effort=(\S+)((?: [a-z_]+=\S+)*) -->$
```

Extra `key=value` tokens are accepted, such as `shared_with_builder=yes` written by `run.sh` line 460.

Python API, which steps 2 to 4 rely on:
- `validate(path, role=None)` returns `None` when the result is valid, else one reason string.
- `structure_error(path, role=None)` runs the same checks except the key-section presence and value checks for roles that have an allowed set (builder, verifier, plan-reviewer). For every other role it still requires the key section.
- `key_value(path, role)` returns the token (`done`, `blocked`, `inherited`, `pass`, `fail`, `replan`) for the key value, or `None`, and never raises. It reads only the key section and ignores the header line, so a headerless file still classifies. Its dependents settle this: `traces/selftest.py` line 351 asserts that a headerless verifier reads verdict `pass`. `traces/sources/bench.py`, `traces/rerun.py`, and `traces/detectors/escalation.py` read results through `steps.build_status_or_none` and `steps.verdict_or_none`, which step 3 routes through `key_value`.
- `ROLES` is the tuple of the nine roles.

With no `role`, the role is read from the header.

Settled reason strings, checked in this order:
1. `no such file`
2. `empty result` (zero bytes, or only whitespace)
3. `first line is not a <!-- role=<r> level=<L> model=<m> effort=<e> --> header`
4. `unknown role <x> in header`
5. `header role=<x> does not match --role <r>`
6. `lacks ## <Key>` for a missing key section, with ` (<display values joined by |>)` appended when the role has an allowed set, for example `lacks ## Status (done|blocked|inherited red: <tests>)`
7. `## <Key> first line "<value>" is not one of <display joined by |>`
8. `## <B> comes before ## <A>`, naming the two sections in the order they appear in the file. Walk the present declared sections in file order (by first occurrence). A is the first one whose declared position is earlier than that of the present section just above it, and B is that section just above it. Examples: a verifier file with `## Criteria` above `## Verdict` gives `## Criteria comes before ## Verdict`, and a builder file with `## Checks` above `## Changes` gives `## Checks comes before ## Changes`.

Reasons 6 and 7 contain `lacks ## <Key>` and `## <Key>`, which the existing greps in `run-selftest.sh` (lines 257, 264, 266, 275) and `codex-selftest.py` line 102 (`lacks ## Map`) need.

CLI (handoff Intent):
- `results.py validate <result.md> [--role R]` exits 0 silently. On an invalid result it prints exactly one stderr line, `results.py: <file>: <reason>`, with `<file>` as given on the command line, and exits 1.
- `results.py schema [--role R]` prints one tab-separated line per role in the table order above: `<role>\t<key>\t<allowed displays joined by | or ->\t<sections joined by |>`.
- `results.py key <role>` prints the key section name, for example `Status`. `run.sh` uses it in step 2.
- `results.py selftest` prints `ok: <name>` per case, then `results selftest: PASS` and exits 0. Otherwise it names the misses and exits 1.
- Usage errors (unknown subcommand or role) exit 2.

Selftest cases (temp files only):
- A valid result for each of the nine roles passes, including one with ` shared_with_builder=yes`.
- `inherited red: test_a` is accepted for builder and verifier. Bare `inherited red` is rejected.
- Each of these fails with its exact reason from the list above: a missing key section, a disallowed first value (builder `maybe`, verifier `maybe`, plan-reviewer `maybe`), no header, an empty file, a role mismatch, and a verifier with `## Criteria` before `## Verdict` (reason `## Criteria comes before ## Verdict`).
- `structure_error` ignores a builder's missing Status but still reports a planner's missing Goal.
- A case named exactly `key_value reads the key value of a headerless result`: `key_value` returns `pass` for a headerless `## Verdict\npass` file with role verifier, and `inherited` for a headerless `## Status\ninherited red: t` file with role builder.

In `check.sh`, add `python3 "$root/scripts/results.py" selftest || fail=1` before the steps.py line, and add `results.py` to the header comment's selftest list.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/results.py selftest`
- `python3 plugins/sdlc-lite/scripts/results.py schema | grep -qxF "$(printf 'plan-reviewer\tVerdict\tpass|replan|blocked\tVerdict|Findings|Missing decisions')"`
- `python3 plugins/sdlc-lite/scripts/results.py schema | grep -qxF "$(printf 'builder\tStatus\tdone|blocked|inherited red: <tests>\tStatus|Changes|Checks|Notes')"`
- `test "$(python3 plugins/sdlc-lite/scripts/results.py key scout)" = Map`
- `f=$(mktemp) && printf '<!-- role=builder level=L1 model=sonnet effort=low -->\n## Status\ndone\n' >"$f" && python3 plugins/sdlc-lite/scripts/results.py validate "$f"`
- `f=$(mktemp) && printf '## Status\ndone\n' >"$f" && out=$(python3 plugins/sdlc-lite/scripts/results.py validate "$f" --role builder 2>&1); rc=$?; test "$rc" -eq 1 && test "$(printf '%s\n' "$out" | wc -l)" -eq 1 && printf '%s\n' "$out" | grep -qF "results.py: $f: first line is not a"`
- `f=$(mktemp) && : >"$f" && python3 plugins/sdlc-lite/scripts/results.py validate "$f" --role scout 2>&1 | grep -qxF "results.py: $f: empty result"`
- `f=$(mktemp) && printf '<!-- role=verifier level=L1 model=sonnet effort=medium -->\n## Criteria\nx\n\n## Verdict\npass\n' >"$f" && python3 plugins/sdlc-lite/scripts/results.py validate "$f" 2>&1 | grep -qxF "results.py: $f: ## Criteria comes before ## Verdict"`
- `f=$(mktemp) && printf '<!-- role=plan-reviewer level=L1 model=opus effort=high -->\n## Verdict\nmaybe\n' >"$f" && python3 plugins/sdlc-lite/scripts/results.py validate "$f" 2>&1 | grep -qF 'is not one of pass|replan|blocked'`
- `python3 plugins/sdlc-lite/scripts/results.py selftest | grep -qxF 'ok: key_value reads the key value of a headerless result'`
- `for f in $(git ls-files -- '.sdlc/*' ':(exclude).sdlc/.*' | grep -E '/(builder|verifier|planner|plan-reviewer|researcher|architect|scout|archaeologist|filer)-L[1-5](-[0-9]+)?\.md$'); do python3 plugins/sdlc-lite/scripts/results.py validate "$f" || exit 1; done`
- `grep -qF 'scripts/results.py" selftest' plugins/sdlc-lite/scripts/check.sh`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh | { ! grep -q .; }`
