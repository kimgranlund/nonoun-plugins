<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0117: fanout.py: opt-in --rewrite-refs so numbered-mode closes survive citing files

## PR body
### Summary
In a numbered-mode repo, `fanout.py` closed each merged ticket with a plain `tickets.py close <slug>`. A file citing the ticket folder made the close refuse, so the outcome was `merged, close refused` and the ticket stayed open. This PR adds an opt-in `fanout.py run --rewrite-refs` flag. It is passed through to `tickets.py close`, and the `close <id>` commit carries the rewritten files. The default is unchanged: without the flag the close is still refused. References are never rewritten silently.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`
  - New `--rewrite-refs` flag (argparse, usage line, module docstring). `ctx` now carries `rewrite_refs` and `numbered`.
  - `--dry-run` prints one `close:` line for the mode: with the flag, without it in numbered mode (noting that a citing file refuses the close and the flag rewrites), or plain.
  - The flag is appended to the `tickets.py close` argv when set.
  - When a refusal names `--rewrite-refs` and the flag was not given, the outcome gains `; fanout.py run --rewrite-refs rewrites them`.
  - The `close <id>` commit no longer runs `git add -A -- <rel>`. A new `porcelain()` helper snapshots `git status --porcelain` before and after the close. The commit stages `rel` plus every path outside it that the close changed, so rewritten files outside `.sdlc/` are committed and the integration worktree stays clean.
  - New selftest case 4 on a numbered-mode throwaway repo.
- `plugins/sdlc-lite/skills/fanout/SKILL.md`
  - `argument-hint` gains `[--rewrite-refs]`.
  - Step 1 notes that the `close:` line shows numbered mode.
  - Step 2 (Confirm) offers the flag as a separate choice only when the plan says `numbered folders`, and never adds it unless the user picks it.
  - Step 2 also explains what a `merged, close refused` outcome naming the flag means.
- `CLAUDE.md`: the `scripts/fanout.py` bullet has the flag in its usage plus a sentence describing it.
- `.claude/agents/sdlc-lite-author.md`: a new line describes the flag.
- `tickets.py` is unchanged, as the ticket required.

### How each was verified
Step 1 (`fanout.py`, verifier L1: pass). The verifier re-ran every acceptance command itself:
- `fanout.py run --help` lists `--rewrite-refs`. The same check against HEAD's `fanout.py` finds no match.
- With the flag, in a numbered-mode throwaway repo:
  - the report row is `merged`, the tip commit is `close T-0001`, and `docs/spec.md` holds the dot path and changed in that commit;
  - `.sdlc/.0001-x/handoff.md` is present and the integration worktree is clean.
- Without the flag:
  - the run exits 1 and the row reads `merged, close refused: .*--rewrite-refs`;
  - the ticket status is still `ready`, `docs/spec.md` is unchanged, and the worktree is clean.
- The dry run shows the expected `close:` line, with and without the flag in numbered mode, and creates no `.worktrees`.
- The selftest holds a numbered-mode case. HEAD has none.
- Guards pass: `fanout.py selftest`, `git diff --quiet HEAD -- tickets.py` (no change), and `scripts/check.sh` (exit 0, including shellcheck and plugin validate).

Step 2 (docs, verifier L1: pass). The verifier checked each grep in the tree (exit 0) and at HEAD (exit 1):
- the flag is in `SKILL.md` step 2;
- the flag is in `argument-hint`;
- the flag is in the `CLAUDE.md` fanout bullet;
- the flag is in `sdlc-lite-author.md`.

For the prose-only criterion, the verifier read the step 2 text. Its trigger phrase matches the dry-run output at `fanout.py:313`, which prints `numbered folders` only in numbered mode without the flag. `scripts/check.sh` passed again.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `fanout.py run --rewrite-refs` (opt-in, numbered mode): passes `--rewrite-refs` to `tickets.py close`, so merged tickets close even when other files cite their folder. The `close <id>` commit now stages every file the close rewrote, including files outside the ticket root. The dry-run plan shows the close mode. Without the flag, a citing file still gives `merged, close refused`, and that outcome now names the flag. `/fanout` offers the flag at its Confirm step in numbered mode only.

## Follow-ups
None
