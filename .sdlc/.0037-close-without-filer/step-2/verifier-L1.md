<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -c -- '--reason'` shows at least 1 in each of the three files: pass. Evidence: working tree gives `plugins/sdlc-lite/skills/ticket/SKILL.md:2`, `.claude/agents/sdlc-lite-author.md:1`, `CLAUDE.md:1`. I also confirmed the check can fail: `git show HEAD:<f> | grep -c -- '--reason'` gives 0 for all three files at HEAD. The content matches the Do list:
  - SKILL.md line 4: `argument-hint` now includes `[--reason "<text>"]`.
  - SKILL.md line 12: the close item now reads "closes a ticket finished by other work, skips the filer, files no follow-ups, and appends a `## Closed` section".
  - CLAUDE.md line 25: the tickets.py bullet now mentions `close <slug> --reason "<text>"`.
  - sdlc-lite-author.md line 16: adds "keep `--reason` in sync across tickets.py, the /ticket skill, and CLAUDE.md".
- `plugins/sdlc-lite/scripts/check.sh` passes, with only the expected CLAUDE.md validate warning allowed: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` exited 0. Its output includes "ok: 18 role levels, 8 agents checked", "tickets selftest: PASS", "board selftest: PASS", "steps selftest: PASS", "run selftest: PASS", "ok: shellcheck" and "ok: plugin validate". `grep -in warn` on the output matched nothing, so no warning at all was printed.
- `git diff --stat` touches only the four named files, plus `.sdlc` if the ticket was closed: pass. Evidence: the tracked changes are `.claude/agents/sdlc-lite-author.md`, `CLAUDE.md`, `plugins/sdlc-lite/scripts/tickets.py` (step 1), `plugins/sdlc-lite/skills/ticket/SKILL.md` and `.sdlc/0037-close-without-filer/handoff.md`. The only untracked files are task artifacts under `.sdlc/0037-close-without-filer/`. `skills/file/SKILL.md` is unchanged, as the step required. The ticket is not closed, yet `.sdlc/0037-close-without-filer/handoff.md` has a diff. That diff only fills in the `## Intent` section, which is task-record content written before the build, not by this step's builder. It does not touch project code.

## Out of scope changes
None from this step. `.sdlc/0037-close-without-filer/handoff.md` has an Intent-section diff that this step did not make: it is the conductor's task record, and the builder report says the same.

## For the next attempt
None
