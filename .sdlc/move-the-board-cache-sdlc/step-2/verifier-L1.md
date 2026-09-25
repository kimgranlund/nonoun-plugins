<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -rn "board-state" plugins/sdlc-lite/skills CLAUDE.md` shows only text about the new location or the legacy note: pass. Evidence: I ran `grep -rn "board-state" plugins .claude CLAUDE.md`. Its only hit under skills/ is `plugins/sdlc-lite/skills/handoff-format/SKILL.md:34`, the new bullet: "Board cache: lives in `${XDG_CACHE_HOME:-~/.cache}/sdlc-lite/board-state/`, outside the repo ... only matters for older versions that wrote it there." CLAUDE.md has no hits. The other hits are `board.py` (step 1) and an old bench result, both outside the criterion's paths. The stated location matches the code: `board.py:250-260` `state_path()` uses `XDG_CACHE_HOME or ~/.cache` / `sdlc-lite/board-state`. The CLAUDE.md Feed line now carries the clause: grep for "per-user cache dir outside the repo (`SDLC_BOARD_STATE_DIR` overrides it)" gives 1 now and 0 at HEAD.
- The ignore code block in `handoff-format/SKILL.md` no longer lists `.sdlc/.board-state.json`: pass. Evidence: I pulled the fenced blocks out with `awk '/^```$/{f=!f;next} f' | grep -n board-state`. At HEAD (`git show HEAD:...`) this printed `15:.sdlc/.board-state.json`, so the check can go red. On the working tree it printed nothing (rc=1).
- `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: `check exit 0`. Its output included "ok: 18 role levels, 8 agents checked", "selftest: PASS", "tickets selftest: PASS", "board selftest: PASS", "ok: shellcheck" and "ok: plugin validate".
- `git diff -U0 | grep '^+' | grep -c '—'` prints 0: pass. Evidence: it printed `emdash: 0`. To show the pipeline can go red, I fed it a probe line `+x — y` and it printed 1.

## Out of scope changes
None. `board.py` is step 1's change, and `.sdlc/move-the-board-cache-sdlc/handoff.md` is the task's own brief. `.claude/agents/sdlc-lite-author.md` and `skills/board/SKILL.md` never mention the cache (`grep -ni cache` found nothing), so leaving them alone was correct. The root `.gitignore` is unchanged, as the step asked.

## For the next attempt
None
