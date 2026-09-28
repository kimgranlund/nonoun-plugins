<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make the `steps.py` `||` lint (in `split` and `lint`) also check compound criteria (`for`/`while`/`until`/`if`/`{`) that end in a trailing redirect or pipe after their closing keyword, such as `while read x; do ...; done < f`. Allowed `||` forms must still pass, and the selftest and the docs must cover the new case.

## Step 1: Lint compound criteria with a trailing redirect or pipe
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py`, `is_command` treats a compound span as a command only when the span ends in its closing keyword (`COMPOUND_END`: `done`, `fi`, `}`). As a result, `while read x; do test -f x || echo m; done < f` and `for ...; done | cat` are not linted today. This was confirmed on the current tree: `is_command` returns False for both, while `or_fallback` already returns True.

Extend the compound branch of `is_command` so it also accepts a span where the closing keyword (as a whole word, preceded by start, whitespace, `;`, `&`, or `|`) is followed by optional whitespace and then a trailing tail that starts with one of these:
- a redirect operator: `<`, `>`, `>>`, `<<<`, an fd-prefixed form such as `2>` or `2>&1`, or `&>`
- a single pipe `|`, but not `||`

Prose that starts with those head words must stay a non-command. Keep the `done`/`fi`/`}` end-of-span rule as it is. Do not change `or_fallback`, `fails_fast`, or the other lint checks. Every existing selftest case must keep its result.

Update the `is_command` docstring and the module usage text near line 46 ("A for, while, or until span ending in done ...") to say that a trailing redirect or pipe after the closing keyword also counts. Use the literal phrase `trailing redirect or pipe` in both places.

Add selftest cases to the `(k2)` block of `selftest()`:
- `lint` refuses `while read x; do test -f x || echo m; done < f` and `for p in a b; do grep -q a "$p" || grep -q b "$p"; done | cat` with `plan defect` and `joins two checks with ||`.
- A fail-fast form with a trailing redirect, `while read x; do test -f x || exit 1; done < f`, lints ok and is returned by `command_spans`.
- Prose such as `for each file done < f` stays a non-command.

Give at least one new check name the text `trailing redirect` so it appears in the selftest output.

In the repo root `CLAUDE.md` `scripts/steps.py` bullet, change "`for`/`while`/`until`/`if`/`{` criteria are linted too" so it also states that such criteria are linted when they end in a trailing redirect or pipe after the closing keyword (for example `done < f`). Use the literal phrase `trailing redirect or pipe`. No other doc (sdlc-lite-author.md, planner.md, handoff-format) describes this coverage today, so none needs a change.

Run every criterion from the git toplevel.
### Acceptance criteria
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; B = lambda t: "### Acceptance criteria\n- " + chr(96) + t + chr(96); sys.exit(0 if steps.lint_steps("p", {1: B("while read x; do test -f x || echo m; done < f")}) else 1)'` exits 0 (a `while ... done < f` criterion with a `|| echo` fallback now gets a lint finding).
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; B = lambda t: "### Acceptance criteria\n- " + chr(96) + t + chr(96); sys.exit(0 if steps.lint_steps("p", {1: B("for f in a b; do grep -q a x || grep -q b x; done | cat")}) else 1)'` exits 0 (a piped `for ... done | cat` criterion with a fallback gets a finding).
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; B = lambda t: "### Acceptance criteria\n- " + chr(96) + t + chr(96); t = "while read x; do test -f x || exit 1; done 2>/dev/null"; sys.exit(0 if steps.is_command(t) and not steps.lint_steps("p", {1: B(t)}) else 1)'` exits 0 (a trailing-redirect compound span is a command, and its fail-fast `|| exit 1` stays allowed).
- (guard) `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import steps; sys.exit(0 if not steps.is_command("for each file done < f") else 1)'` exits 0 (prose stays a non-command).
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "trailing redirect"` exits 0 (the selftest passes and prints the new case).
- `grep -qF 'trailing redirect or pipe' plugins/sdlc-lite/scripts/steps.py`
- `grep -qF 'trailing redirect or pipe' CLAUDE.md`

## Step 2: Gates green
level: L1
### Do
Run the project's whole gate, `bash plugins/sdlc-lite/scripts/check.sh`, from the git toplevel. Fix any red that step 1 introduced (for example, a check.py doc-sync guard or a shellcheck finding), and keep step 1's behavior. If a gate was already red at `$SDLC_BASE_SHA`, report builder Status `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0.

## Risks
- This is scoped to a trailing redirect or pipe, as the ticket asks. A compound span followed by `&&`, `;`, or `||` after its closing keyword (for example `done || echo x`) stays unlinted, and a follow-up may want it.
- Widening `is_command` could turn a prose criterion into a command span if the prose starts with `for`/`while`/`if` and contains `done <`/`fi |`. Such a span would then face `bash -n` and could be refused. The prose guard covers only one shape.
- I did not see the two gate guards go red on this host. Their red state is the gates' own nonzero exit on a failed check, which a read-only probe cannot produce.
