## Task goal
Finish the opt-in numbered-folder mode in `plugins/sdlc-lite/scripts/tickets.py` by making the NNNN-/id rule fire only in numbered mode (`check --numbered` or `<root>/config`), then update the docs, with plain-slug behavior byte-for-byte unchanged.

Task handoff (Intent, deltas, constraints): .sdlc/0016-ticket-numbered-folders/handoff.md
Previous blocked attempt of this step: .sdlc/0016-ticket-numbered-folders/old-step-3/

## Step 3: `check` enforces the NNNN-/id match in numbered mode only
level: L3
### Do
This is a replan of the blocked step. The earlier attempt (`.sdlc/0016-ticket-numbered-folders/step-3/attempt.txt`) made the rule unconditional, which rejects plain-mode folders like `0007-gamma` (id T-0003) that the task's Constraints keep legal. The handoff's Intent now says: enforce only in numbered mode. Build it that way in `plugins/sdlc-lite/scripts/tickets.py`:

- `problems(ts, numbered=False)`: when `numbered` is true, for every `(slug, m)` whose folder name matches `^(\d{4})-` and whose `id` is a string, append `f'{slug}: folder prefix {NNNN}- does not match id {m["id"]!r} (want T-{NNNN})'` if `m['id'] != f'T-{NNNN}'`. With `numbered=False` the function is exactly today's, so plain-mode `check`, `roadmap`, `new`, `close` output does not change. Plain-slug folders are never checked for a prefix in either mode.
- `cmd_check(root, numbered=False)`: `numbered = numbered or config_numbered(root)`, then `problems(ts, numbered)`. The roadmap staleness check is unchanged.
- In numbered mode `cmd_new` and `cmd_close` run the same rule: pass `numbered` to their pre-check `problems(ts, ...)` calls (so, like any other ticket problem, a mismatched existing `NNNN-` folder makes them refuse with "fix the problems above first" and write nothing) and to the `problems(ts + [(name, meta)], ...)` call inside `stamp()`. In plain mode these calls stay `problems(ts)`.
- `run()`: pass `**kw` to `cmd_check` too (docstring: "kw goes to new, close and check").
- `main()`: add `--numbered` to the `check` subparser (help: "also fail a NNNN-<slug> folder whose id is not T-NNNN (also on via <root>/config)"). Build `kw` with `getattr(a, 'numbered', False)` for `cmd in ('new', 'close', 'check')`: when no subcommand is given, `cmd` defaults to `'check'` but the namespace has no `numbered` attribute (argparse only sets subparser defaults when that subparser runs), so `a.numbered` would raise AttributeError.
- Module docstring: `check [--numbered]` in the Usage line; extend the `check` description with one clause: numbered mode also fails a `NNNN-<slug>` folder whose id is not `T-NNNN`.
- Leave `cmd_roadmap` alone (the Intent scopes the rule to `new`, `close`, `check`).
- `selftest()`: add these cases, keeping every existing case byte-identical, in particular `plain mode still takes a digit-led slug as-is` and `(i) plain close keeps bare slugs`, which the always-on rule broke. The `mutations` loop runs plain `check`, so the mismatch cases go in their own block (a folder rename makes the roadmap stale, so run `roadmap` on the copy before `check`):
  1. `prefix mismatch (flag)`: copy of base with `alpha` renamed to `0005-alpha`, `roadmap`, then `run(root, 'check', numbered=True)` gives rc 1 and stderr containing `0005-alpha: folder prefix 0005- does not match id 'T-0001'`.
  2. `prefix mismatch (config)`: same tree plus `config` = `ticket_folders: numbered\n`, plain `run(root, 'check')` gives the same failure.
  3. `prefix mismatch is not checked in plain mode`: same renamed tree, no config, `run(root, 'check')` gives rc 0, stdout `ok: 2 tickets, roadmap current`, and `'prefix' not in err`.
  4. `matching 0001-alpha passes check --numbered`: `alpha` renamed to `0001-alpha`, `roadmap`, `check numbered=True` rc 0.
  5. `plain slugs get no prefix error in numbered mode`: untouched base, `check numbered=True` rc 0. Also extend the existing `numbered_ok` helper so the mixed tree (`alpha`, `beta`, `0003-gamma`) must pass `run(root, 'check', numbered=True)[0] == 0` as well as plain check.
  6. `digit-led plain slug: plain check passes, check --numbered names it`: after the existing `new feature 0007-gamma` plain case, `run(root, 'check')` rc 0 and `run(root, 'check', numbered=True)` rc 1 with `0007-gamma` in stderr.
  7. `numbered new refuses on an existing prefix mismatch and writes nothing`: config numbered plus the `0005-alpha` tree (roadmap regenerated), `snap` before, `run(root, 'new', ('feature', 'gamma'))` gives rc 1, stderr contains `0005-alpha: folder prefix` and `fix the problems above first`, and `snap(root)` is unchanged. Same for `run(root, 'close', ('beta',))` (the problems pre-check fires before the missing-filer refusal): rc 1, prefix error, snapshot unchanged.
  8. Negative control for 7: the same `0005-alpha` tree without config, `run(root, 'new', ('feature', 'gamma'))` rc 0 and `root / 'gamma' / 'handoff.md'` exists.
- Steps 1 and 2 are uncommitted in the working tree. Never run `git checkout`, `git restore`, or `git stash` on `tickets.py` (the last attempt wiped them that way); back out an edit by editing.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 and prints `tickets selftest: PASS`.
- `grep -c "prefix mismatch" plugins/sdlc-lite/scripts/tickets.py` is at least 3, and `grep -n "plain mode still takes a digit-led slug as-is\|(i) plain close keeps bare slugs\|(i) numbered close\|new --numbered: folder" plugins/sdlc-lite/scripts/tickets.py` finds all four earlier labels (steps 1 and 2 intact).
- Red-then-green on a throwaway copy placed next to `tickets.py` (so templates resolve) and deleted afterwards: with the prefix rule removed from `problems()`, the selftest fails listing the two `prefix mismatch` cases; with the rule made unconditional (ignore the `numbered` argument), it fails listing `prefix mismatch is not checked in plain mode`, `plain mode still takes a digit-led slug as-is`, and `(i) plain close keeps bare slugs`.
- CLI sequence in a temp dir, `S=plugins/sdlc-lite/scripts/tickets.py; R=$(mktemp -d)/.sdlc`:
  - `python3 $S --root $R new feature foo "Foo" --numbered` creates `$R/0001-foo/handoff.md` with `id: T-0001`; `python3 $S --root $R check --numbered` prints `ok: 1 tickets, roadmap current`, rc 0.
  - Edit `id: T-0001` to `id: T-0009` in that file, run `python3 $S --root $R roadmap`; then `python3 $S --root $R check` prints `ok: 1 tickets, roadmap current` with rc 0, and `python3 $S --root $R check --numbered` exits 1 with stderr `0001-foo: folder prefix 0001- does not match id 'T-0009' (want T-0001)`.
  - `printf 'ticket_folders: numbered\n' > $R/config`; `python3 $S --root $R check` now exits 1 with the same line; `python3 $S --root $R new feature bar` exits 1, stderr contains that line and `fix the problems above first`, and `ls $R` shows only `0001-foo`, `config`, `roadmap.md`.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc` (no subcommand) both exit 0 and print the same `ok: N tickets, roadmap current` line (21 today).
- `plugins/sdlc-lite/scripts/check.sh` exits 0.
- `git status --short` shows no changes outside `plugins/sdlc-lite/scripts/tickets.py` and the `.sdlc/0016-ticket-numbered-folders/` task artifacts.

## Risks (from the replan)
- Step 3 makes numbered-mode `new` and `close` refuse on any existing mismatched `NNNN-` folder, not only on the ticket they write. This follows the existing "fix the problems above first" contract; if the user wanted the rule only on the written ticket, drop `numbered` from the two pre-check `problems(ts)` calls and cases 7 and 8.
- `roadmap` does not apply the rule (the Intent lists `new`, `close`, `check`), so with the config on, `roadmap` can regenerate while `check` fails. A follow-up ticket if that matters.
- Steps 1 and 2 exist only as uncommitted working-tree changes; any `git checkout`, `git restore`, or `git stash` in the step-3 build loses them. Step 3's criteria grep for their labels to catch that.
- The default no-subcommand path (`cmd = a.cmd or 'check'`) has no `numbered` attribute; a builder that reads `a.numbered` directly breaks `python3 tickets.py --root .sdlc`, which the statusline and `/ticket` with no args use. The criterion runs that form.
- The repo ticket count (21) in a criterion can drift if the conductor files tickets meanwhile; the check is rc 0 and matching lines from both forms, not the number.
