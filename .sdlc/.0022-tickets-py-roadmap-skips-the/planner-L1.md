<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
`tickets.py roadmap` applies the same numbered-mode prefix/id check as `check`, by taking `--numbered` or reading `<root>/config`, so the two commands never disagree on a valid ticket set.

## Step 1: Make roadmap honor numbered mode, with selftest and docs
level: L2

### Do
In `plugins/sdlc-lite/scripts/tickets.py`:
- Change `cmd_roadmap(root, numbered=False)` to set `numbered = numbered or config_numbered(root)` and call `problems(ts, numbered)`. Leave the output format and `write_roadmap` alone.
- Add a `--numbered` flag to the `roadmap` argparse subparser (~line 882), matching how `check` passes it. Make sure `run()` forwards `kw` to `cmd_roadmap` (`run` currently calls `cmd_roadmap(root)` with no kw).
- Update the top docstring: the usage line becomes `roadmap [--numbered]`, and the roadmap description says it refuses on any ticket problem, including the numbered prefix/id rule.
- In `selftest`, add cases near the NNNN-/id block (~line 677 on). Reuse the `renamed`, `config`, `both`, `case` and `snap` helpers.
  - With a `0005-alpha` mismatch, `roadmap` with `numbered=True` returns rc 1, the error contains `0005-alpha: folder prefix 0005- does not match id 'T-0001'` and `roadmap not written`, and `snap` is unchanged.
  - The same holds when numbered mode comes from a config line instead of the flag.
  - Plain `roadmap` on the mismatched set still succeeds, so plain mode is unchanged.
  - A matching `0001-alpha` set passes `roadmap --numbered`.
- Check that the existing helpers still work. `renamed()` calls `run(root, 'roadmap')`, which now reads config. Every call should either run before the config line is written or still see a consistent set. Fix the ordering in `both(...)` if any existing case breaks.

Docs that go stale:
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: change the argument-hint to `roadmap [--numbered]`. Where the body describes numbered mode, mention that `roadmap` follows it too.
- Repo-root `CLAUDE.md`, tickets.py bullet: change the flag list to `--numbered` on `new`/`close`/`roadmap`/`check`, and add that `roadmap` refuses on the prefix rule in numbered mode.
- `.claude/agents/sdlc-lite-author.md`: update any line that describes numbered mode or the roadmap so it matches.

Do not commit.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0, and the new roadmap-numbered cases are among the passing expectations.
- Manual check in a temp root with two tickets: rename `alpha` to `0005-alpha` and run `tickets.py --root <tmp> roadmap --numbered`. It exits 1, prints the prefix mismatch, and leaves `roadmap.md` unchanged. Add `ticket_folders: numbered` to `<tmp>/config` and run plain `roadmap`: same refusal. Remove the config line and run plain `roadmap`: it succeeds.
- `grep -n "roadmap \[--numbered\]" plugins/sdlc-lite/scripts/tickets.py plugins/sdlc-lite/skills/ticket/SKILL.md` matches in both files.
- `git diff` shows no change to the roadmap output text or `write_roadmap`.
- `plugins/sdlc-lite/scripts/check.sh` passes. The CLAUDE.md validate warning is expected.

## Risks
- Existing selftest helpers such as `renamed` call `roadmap` while the config or flag may already be set. That could make old cases refuse, so the ordering may need adjusting.
- Other callers of `cmd_roadmap` or `run(..., 'roadmap')` may exist in scripts or skills. The builder should grep for them.
