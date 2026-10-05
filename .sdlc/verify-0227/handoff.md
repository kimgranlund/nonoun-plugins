# Verify T-0227: orient a harness

## Goal
Independently verify `git diff main...HEAD` on branch orient (T-0227): the root AGENTS.md gains a "Map and how work is done here" section, and docs/AGENTS.md and docs/CLAUDE.md are new.

## Acceptance criteria
1. `AGENTS.md` is at most about 80 lines (`wc -l AGENTS.md`), every section that existed on main is still present with its text unchanged (compare `git show main:AGENTS.md` against HEAD: the diff must be additive only), and the new section contains the philosophy quoted exactly ("Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction."), the lane rule naming `steps.py lane`, `solo` as the default for size S and M, `/fix` only on request or when the lane script prints `fix`, and the full chain only with a stated reason, plus a map of `plugins/`, `docs/`, `scripts/`, `.sdlc/` and a do-not-read line.
2. Every relative link in `AGENTS.md` and `docs/AGENTS.md` resolves to an existing file or folder (check each; links in docs/AGENTS.md are relative to docs/). `docs/CLAUDE.md` is exactly one line, `@AGENTS.md`.
3. Every claim in the new text is true of this repository: the lane rule matches `plugins/sdlc-lite/agents/conductor.md` and `plugins/sdlc-lite/scripts/steps.py lane`, each docs/ folder row matches what the folder actually holds (`ls docs/<folder>`), and no fact is copied from another file where a link would do.
4. `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0; `git diff --check main..HEAD` is clean; no em dash appears in any changed text file (no added line in AGENTS.md, docs/AGENTS.md, docs/CLAUDE.md or .sdlc/.0227-orient-entry-files/handoff.md contains an em dash (U+2014); scope the check to those files so this brief is excluded).
5. The ticket handoff `.sdlc/.0227-orient-entry-files/handoff.md` has no placeholder template text and its claim that `onboard.py setup` would add a root block contradicting the lane rule is true (read `plugins/sdlc-lite/scripts/onboard.py` root block text).

## Notes
Read-only. Do not edit files. Report pass or fail per criterion with evidence.
