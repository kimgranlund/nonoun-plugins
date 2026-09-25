## Task goal
`tickets.py close <slug> --skip N[,N...]` never skips the wrong follow-ups: if the filer file's Follow-ups list changed after the `--dry-run` that produced the indices, close refuses and writes nothing instead of applying stale indices.

Done when: a dry run prints a token that identifies the exact follow-up list it indexed; `close --skip` checks it against the current list and refuses on a mismatch (stderr names the drift, nothing written); /file (skills/file/SKILL.md step 3) passes the token through; the selftest proves the guard bites (edit the filer file between dry run and --skip → refusal, unchanged → close succeeds); CLAUDE.md's tickets.py line and the usage/docstring describe it; `scripts/check.sh` passes.
(gap: mechanism not specified; default: dry run prints a short content digest of the ordered follow-up titles, `close` takes `--expect <digest>`, and `--skip` without `--expect` refuses. Planner may pick an equivalent mechanism if it states why.)

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
