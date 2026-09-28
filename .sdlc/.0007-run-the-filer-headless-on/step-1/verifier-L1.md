<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- 1. `fresh-filer-L1.md` is a real filer output with a bullets-only Follow-ups: pass. Evidence: The file has a `role=filer level=L1` header and the five sections `## Warnings`, `## PR title`, `## PR body`, `## Changelog entry` and `## Follow-ups`. Follow-ups is exactly three top-level `- ` lines, each on one line and each ending at the end of its line, with no continuation lines.
- 2. `close` on the copied file exits 0 and files one proposed idea ticket per bullet: pass. Evidence: In a mktemp root, `tickets.py --root <tmp>/root close spike` printed `T-0099 done; 3 follow-up ticket(s): tickets-py-roadmap-does-not, numbered-mode-new-and-close, planner-criteria-that-grep-for` with rc=0. The root held 3 new folders. All 3 have `type: idea` and `status: proposed`. The spike ticket became `status: done`.
- 3. Negative control with prose Follow-ups: pass. Evidence: In a second temp copy, Follow-ups was replaced with one prose sentence. `close` exited rc=1 with "Follow-ups is prose with no top-level bullet ... nothing written". The root still held only `spike`, and its status was still `ready`. The branch that fired is the prose refusal, seen in the stderr text, not just the exit code.
- 4. Every repo filer output parses, and counts match `evidence.md`: pass. Evidence: I ran `section`, `is_none` and `bullets` from `tickets.py` over the 10 `.sdlc/*/filer-L*.md` files plus `fresh-filer-L1.md`. All 11 have `## Warnings` and `## Follow-ups`. 2 are None and 9 have at least one bullet. That matches the "11 total, 2 None, 9 bullets" in `evidence.md`.
- 5. No file under `plugins/` changed: pass. Evidence: `git status --short plugins/` printed nothing (0 lines).

## Out of scope changes
None. The repo shows only `.sdlc/0007-run-the-filer-headless-on/` changes: a modified `handoff.md`, the new `evidence.md`, `fresh-filer-L1.md`, `runs.jsonl` and `step-1/`. All of them belong to this spike.

## For the next attempt
None
