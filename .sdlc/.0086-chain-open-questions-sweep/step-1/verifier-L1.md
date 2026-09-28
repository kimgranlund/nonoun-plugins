<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- File exists: pass. Evidence: `test -f plugins/sdlc-lite/skills/open-questions/SKILL.md` printed c1. The file is untracked, so at HEAD it does not exist and this check would fail there.
- Frontmatter (line 1 `---`, `name: open-questions`, non-empty description, `allowed-tools` includes AskUserQuestion): pass. Evidence: the compound command printed c2. I read the frontmatter directly: `argument-hint: [task dir]` and `allowed-tools: Read, Grep, Glob, AskUserQuestion`. The description has the trigger phrases and NOT clauses that point only at /clarify and /ticket.
- No forbidden names: pass. Evidence: `test -f` plus `! grep -nE 'harness|write-handoff|find-intent|file-leftovers|close-session|find-open-questions'` printed c3. The `test -f` guard stops the negated grep passing on a missing path.
- Required content (nothing open, unattended, Plan review, gap:): pass. Evidence: the compound grep printed c4.
- No em dashes: pass. Evidence: `! grep -n '—'` printed c5, and I saw no em dashes when reading the full file.
- Observable body behavior: pass. Evidence: I read the file. Section 3 says exactly ONE AskUserQuestion call with 1 to 4 questions of 2 to 4 options. Recommended goes first only where a default or lean was stated. More than 4 items means ask the top 4 and name the count of the rest. Stale items are dropped in section 1. Section 4 says a declined question is not re-asked. An Unattended section covers `SDLC_HEADLESS` and `SDLC_ROLE`. A good/bad example is included.
- (guard) `check.sh` exits 0: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` returned exit 0. Its output ended with "ok: shellcheck" and "ok: plugin validate".

## Out of scope changes
None from the build. `git status --short plugins CLAUDE.md` shows only the untracked `plugins/sdlc-lite/skills/open-questions/`. The other changes are under `.sdlc/0086-chain-open-questions-sweep/`, which is `handoff.md` (modified), `planner-L2.md`, `runs.jsonl` and the step folders. These are chain bookkeeping artifacts, not step files.

## For the next attempt
None
