<!-- role=planner level=L2 model=opus effort=medium -->
Planning is done: two steps, first the guard with its selftest in tickets.py, then syncing the docs. Final plan below.

## Goal
Make `tickets.py close <slug> --skip N[,N...]` refuse and write nothing when the filer file's Follow-ups list has changed since the `--dry-run` that produced the indices. The dry run prints a digest of the list, the skip call must pass it back as `--expect <digest>`, and the docs and /file flow are updated to match.

## Step 1: Add the follow-up digest and the --expect guard to tickets.py, with selftest cases
level: L2
### Do
Everything in this step is in `plugins/sdlc-lite/scripts/tickets.py`. Use the default mechanism from the handoff, with one change: the digest hashes the full ordered bullet texts, not the titles. `follow_up_title` cuts titles at 70 characters, so an edit past that point would leave the titles unchanged while the item that gets filed changes. Hashing the full `items` catches reordering, adding, removing, and rewording.

1. Add `import hashlib` next to the other imports.
2. Add a helper near `parse_skip`: `def follow_digest(items): return hashlib.sha256('\n'.join(items).encode('utf-8')).hexdigest()[:12]`. Its docstring should say it is the token that ties `--skip` indices to the exact Follow-ups list a dry run showed. `items` is the `bullets(follow)` list, or `[]` when Follow-ups is None.
3. Change `cmd_close(...)`:
   - Add a new parameter `expect=None`.
   - Extend the first guard so `--reason` also refuses with `--expect`: `reason is not None and (dry_run or skip is not None or expect is not None)`. Update the message to name `--expect`.
   - After `items` is computed and before the `--skip` range check:
     - Set `digest = follow_digest(items)`.
     - If `skip is not None and not dry_run and expect is None`, raise Fail: `{slug}: --skip needs --expect <digest> from the dry run that listed the indices (run close --dry-run first); nothing written`.
     - If `expect is not None and expect.strip() != digest`, raise Fail: `{slug}: --expect {expect} does not match the current Follow-ups in {filer.name} (digest {digest}); the list changed since the dry run, so the --skip indices may point at other items; rerun close --dry-run; nothing written`.
     - `--expect` is also checked on a plain close or a dry run when given. Plain `close` without `--skip` still needs no token.
   - Dry-run output: keep the header line and the item lines unchanged. Append one final line `expect <digest>` after the optional `rename` line.
   - Update the docstring to cover `expect`.
4. Change `main()`:
   - Add `p.add_argument('--expect', metavar='DIGEST', help=...)` to the close parser. The help text should say: the digest from the dry run's last line; required with `--skip`; close refuses when the Follow-ups list changed.
   - Pass `kw['expect'] = a.expect`.
   - Add `--expect` to the `--skip` help ("needs --expect").
5. Update the module docstring (the Usage line and the close paragraph). Add `[--expect DIGEST]`, the `expect <digest>` dry-run line, the rule that `--skip` needs `--expect`, the mismatch refusal, and that `--reason` refuses with `--expect`.
6. Update the existing selftest cases:
   - (p): check the item lines as `lines[1:-1]`, and check `lines[-1] == 'expect ' + follow_digest([...the three items...])`.
   - (q): pass `expect=` equal to the fixture's digest. Get it with `follow_digest(bullets(three))` or by parsing the last line of a dry run.
   - (r): for `dry=False`, pass the matching `expect` so the range refusal is still the one under test.
   - (t): add `{'expect': 'x'}` to the combinations that `--reason` refuses.
7. Add a new selftest case (v), guard bites:
   - (v1) Dry run on `three`, parse the digest from the last line, then rewrite the filer file so the Follow-ups list changes, e.g. `- Quote the docs\n- Add retry to fetch\n- Split the runner` (reordered). Then `close --skip 2 --expect <old digest>` must return rc 1, with stderr containing `does not match`, the filer name, and `nothing written`. The tree must be unchanged (`snap(root) == before`, status still `proposed`).
   - (v2) Same fixture, unchanged: `close --skip 2 --expect <digest>` returns rc 0, the ticket is done, and 2 follow-ups are filed.
   - (v3) `close --skip 2` with no `--expect` returns rc 1, stderr contains `--expect` and `nothing written`, and nothing is written.
   - (v4) Plain `close` with no `--skip` and no `--expect` still succeeds. Existing case (s) may already cover this; mention it in the case comment.
   - (v5) A reworded item that keeps its position and title prefix (text changed past char 70) also refuses. This proves the digest covers the full item, not the title.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints `tickets selftest: PASS` and exits 0.
- Negative control: temporarily make the mismatch check a no-op, e.g. change `expect.strip() != digest` to `False`, in a scratch copy. Running the copy's `selftest` must fail on case (v1). Do not commit this change.
- Run in a temp root with a ticket and a `filer-L1.md` holding 3 follow-ups:
  - `close <slug> --dry-run` output ends with a line matching `^expect [0-9a-f]{12}$`.
  - `close <slug> --skip 2` exits 1, and stderr ends with `nothing written`.
  - After editing the Follow-ups list, `close <slug> --skip 2 --expect <old>` exits 1, stderr names the drift (`does not match`) and ends with `nothing written`, and `git status`/`find` shows no new or changed files.
  - With the list unchanged, `close <slug> --skip 2 --expect <digest>` exits 0.
- `python3 plugins/sdlc-lite/scripts/tickets.py close --help` lists `--expect DIGEST`.
- `grep -n "expect" plugins/sdlc-lite/scripts/tickets.py | head` shows `--expect` in the module Usage line and in the close paragraph of the docstring.
- Existing behavior is unchanged: selftest cases (a) through (u) still pass as part of the PASS above. Plain `close <slug>` with no flags still works without a token.

## Step 2: Sync /file, /ticket, and CLAUDE.md with the --expect guard
level: L1
### Do
1. `plugins/sdlc-lite/skills/file/SKILL.md` step 3:
   - Sub-step 1: the dry run's last line is `expect <digest>`. Keep that digest.
   - Sub-step 4: the command becomes `close <slug> --skip <unselected indices> --expect <digest>`. Plain `close <slug>` needs no token when nothing is skipped. If close refuses with `does not match`, the filer file changed: rerun the dry run and ask again. Do not retry with the new digest blindly.
   - Sub-step 5 (unattended): pass `--expect <digest>` with `--skip` too.
2. `plugins/sdlc-lite/skills/ticket/SKILL.md`:
   - Add `[--expect DIGEST]` to the `argument-hint` close form.
   - In item 4, say that `--dry-run` ends with an `expect <digest>` line, that `--skip` needs `--expect <digest>` and refuses, writing nothing, when the Follow-ups list changed since that dry run, and that `--reason` does not combine with `--expect` either.
3. `CLAUDE.md` (repo root), the `scripts/tickets.py` bullet: extend the `close --dry-run` / `--skip` clause to say the dry run prints an `expect <digest>` line of the ordered follow-ups, that `--skip` requires `--expect <digest>`, and that close refuses, writing nothing, when the digest no longer matches. Add `--expect` to the flags that do not combine with `--reason`.
4. `.claude/agents/sdlc-lite-author.md`: its line 16 sync rule already covers `close --dry-run`/`--skip` across the four files. Change it only to add `--expect` to the flags named in that rule. No other edits.
### Acceptance criteria
- `grep -c -- "--expect" plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md` gives a count of at least 1 for each file.
- The /file step 3.4 command text contains both `--skip` and `--expect <digest>`. Step 3.5 mentions `--expect`.
- `grep -n "argument-hint" plugins/sdlc-lite/skills/ticket/SKILL.md` shows `[--expect DIGEST]`.
- `grep -c "—" plugins/sdlc-lite/skills/file/SKILL.md plugins/sdlc-lite/skills/ticket/SKILL.md CLAUDE.md` shows no increase over the pre-change count (no new em dashes).
- `plugins/sdlc-lite/scripts/check.sh` exits 0. It runs the tickets selftest, shellcheck, and plugin validate; the known CLAUDE.md validate warning is expected.

## Risks
- The digest covers the ordered full bullet texts, not only the titles; the handoff default said titles. Both refuse on a reorder, add, or remove. The full-text digest is stricter: it also refuses on a reworded bullet whose title does not change, which is intended. If the user wants whitespace-only edits to pass, note that `bullets()` already normalizes line joins and stripping, so only real text changes shift the digest.
- A dry run combined with `--skip` does not require `--expect`, because it writes nothing. If the verifier reads "--skip without --expect refuses" as covering dry runs too, it may flag this. The plan scopes the refusal to writing closes on purpose, and it keeps the existing (r) dry-run cases working.
- Selftest cases (p), (q), and (r) change their expectations, so the "existing selftest cases passing" constraint is met by updating them, not by leaving them untouched. The verifier should check that each one still asserts what it did before.
- /file is instructions only, so whether a session actually passes the token depends on the session reading SKILL.md. The code guard is what enforces it: `--skip` without `--expect` refuses.
