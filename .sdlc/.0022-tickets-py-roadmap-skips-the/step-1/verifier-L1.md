<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest exits 0 with the new roadmap-numbered cases: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exited 0. The diff adds four cases at tickets.py ~698-709: refusal via flag, refusal via config, plain roadmap ignoring the mismatch, and a matching `0001-alpha` passing `roadmap --numbered`. The pass output does not list individual expectations, so I saw these only in the diff.
- Manual check in a temp root: pass. Evidence, in a fresh temp root with `alpha` renamed to `0005-alpha`:
  - `roadmap --numbered` exited 1 with `0005-alpha: folder prefix 0005- does not match id 'T-0001' (want T-0005)` and `roadmap not written`. The roadmap.md md5 stayed `9fa5f2dd…`.
  - With `ticket_folders: numbered` in config, plain `roadmap` gave the same refusal and rc=1, and the md5 was unchanged.
  - With the config line removed, plain `roadmap` gave rc=0 and wrote the file.
- `grep -n "roadmap \[--numbered\]"` matches in both files: pass. Evidence: matches at tickets.py:5 and SKILL.md:4.
- No change to roadmap output text or `write_roadmap`: pass. Evidence: the tickets.py diff touches only the `cmd_roadmap` signature and `problems` call, the `run` docstring and dispatch, the argparse subparser and `kw` passing, the top docstring, and selftest.
- `check.sh` passes: pass. Evidence: rc=0; output ends `selftest: PASS`, `tickets selftest: PASS`, `board selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.
- Docs updated: pass. Evidence: the SKILL.md argument-hint and numbered-mode bullet, plus the CLAUDE.md tickets.py bullet, all match the handoff. `.claude/agents/sdlc-lite-author.md` has no numbered or roadmap mention (my grep returned nothing), so leaving it unchanged is correct.
- Negative control (does the check go red?): pass, weakly. Evidence: I reverted `problems(ts, numbered)` to `problems(ts)` in `cmd_roadmap`, in a copy run from /tmp. The selftest did not pass; it crashed with FileNotFoundError, so I did not see the clean per-expectation failure. Separately, the manual runs above show the refusal directly, and the builder reports the two refusal cases failing under the same revert.

## Out of scope changes
`.sdlc/0022-tickets-py-roadmap-skips-the/handoff.md` (Goal, Context, Constraints filled in) is modified. This is task bookkeeping, not product code. `planner-L1.md`, `runs.jsonl` and `step-1/` are untracked artifacts. Nothing else changed.

## For the next attempt
None
