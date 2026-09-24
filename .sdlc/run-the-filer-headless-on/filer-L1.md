<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0007: Confirm the live headless filer emits Follow-ups that tickets.py close accepts

## PR body
### Summary
This spike checks a risk left open by T-0003. `tickets.py close` refuses Follow-ups written as prose, and nobody had tested whether a live headless filer emits bullets. It does. The fresh run and every earlier filer output in the repo emit Follow-ups as top-level bullets or exactly `None`, and `close` accepts them. No code changed.

### Changes
- Added `.sdlc/run-the-filer-headless-on/evidence.md` with the results of the fresh run, the close run, the negative control, and a scan of all filer outputs in the repo.
- Added `.sdlc/run-the-filer-headless-on/fresh-filer-L1.md`. This is the output of `scripts/run.sh filer L1` on a scratch copy of `.sdlc/ticket-numbered-folders`, with the id changed to T-0099 and its old filer output removed. The scratch folder was deleted afterwards.
- Appended the run line to `runs.jsonl`. Added the verification step under `step-1/`. Updated the task `handoff.md`.

### Verification
Step 1 was checked by an independent verifier (L1, Sonnet medium). Verdict: pass.
1. `fresh-filer-L1.md` is a real filer output with all five sections. Its Follow-ups section is three top-level `- ` lines, one line each.
2. In a mktemp ticket root, `tickets.py --root <tmp>/root close spike` exited 0 and created 3 tickets, each with `type: idea` and `status: proposed`. The spike ticket became `done`.
3. Negative control: with Follow-ups rewritten as one prose sentence, `close` exited 1 with "Follow-ups is prose with no top-level bullet". It wrote no ticket and left the status at `ready`.
4. All 11 `.sdlc/*/filer-L*.md` files were parsed with `tickets.py`'s own `section`/`is_none`/`bullets`. 2 have `None` and 9 have bullets, which matches `evidence.md`.
5. `git status --short plugins/` is empty.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Confirmed that the live headless filer (L1) emits Follow-ups as bullets or `None`, and that `tickets.py close` accepts them. The prose refusal stays in place to catch a regression (T-0007).

## Follow-ups
None
