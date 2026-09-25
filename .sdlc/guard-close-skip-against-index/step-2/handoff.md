## Task goal
`tickets.py close <slug> --skip N[,N...]` never skips the wrong follow-ups: if the filer file's Follow-ups list changed after the `--dry-run` that produced the indices, close refuses and writes nothing instead of applying stale indices.

Done when: a dry run prints a token that identifies the exact follow-up list it indexed; `close --skip` checks it against the current list and refuses on a mismatch (stderr names the drift, nothing written); /file (skills/file/SKILL.md step 3) passes the token through; the selftest proves the guard bites (edit the filer file between dry run and --skip → refusal, unchanged → close succeeds); CLAUDE.md's tickets.py line and the usage/docstring describe it; `scripts/check.sh` passes.
(gap: mechanism not specified; default: dry run prints a short content digest of the ordered follow-up titles, `close` takes `--expect <digest>`, and `--skip` without `--expect` refuses. Planner may pick an equivalent mechanism if it states why.)

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
