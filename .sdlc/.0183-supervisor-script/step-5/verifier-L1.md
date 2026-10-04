<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- AC1, the selftest with the supervisor folder unchanged, the final line, and the five required `ok:` lines: pass. I ran the full command and it exited 0 (`AC1=0`). The checked lines include `ok: prompt: Claude Code is told its only Bash commands` and `ok: control: a copy with the v0.2 prompt fails the Bash rule check`. The `control:` line only prints `ok` when the case fails with the `BASH_RULE` prefix, so the check can go red. I did not run it separately against the old prompt in a throwaway worktree.
- AC2, `wake_prompt("bob", 2)` prefix, added sentence, and suffix: pass. The `python3 -c` assertions exited 0 (`AC2=0`).
- AC3, `watcher-design.md` greps: pass. All three greps exited 0 (`AC3=0`). Lines 63 and 64 hold the new `- Text:` line and the "added after the first live run" item.
- (guard) diff and untracked-file whitelist: pass. It exited 0 (`G=0`) with `SDLC_BASE_SHA` set to 72ac9a3.
- `if __name__ == '__main__':` appears once in `supervisor.py`: pass. `grep -c` returned 1.
- No em dash in either file: pass. The em-dash count was 0 in both `supervisor.py` and `watcher-design.md`.
- Builder claims: accepted only where I re-ran the same commands above. The `git diff --check` claim I did not re-run.

## Out of scope changes
None. Every modified or untracked non-`.sdlc` file is on the guard's whitelist; the guard passed. I left `probe.py` alone because the handoff says it is untouched.

## For the next attempt
None. Steelman: I drafted a fail because the `watcher-design.md` diff against the base SHA is huge. The builder would rebut that the diff comes from the earlier steps (steps 1 to 4), and the file is whitelisted. I dropped the finding.
