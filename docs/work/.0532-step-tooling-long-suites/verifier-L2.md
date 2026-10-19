<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 selftest exits 0 incl. (g) --supersede and solo-dir swap cases: pass. Evidence: `python3 plugins/sdlc-lite/scripts/steps.py selftest` rc=0, last line "steps selftest: PASS". Negative controls run on a /tmp copy of the plugin (git worktree add was blocked: SDLC_TMP_WORKTREES unset): neutralizing `if done and supersede:` (steps.py:1876) made selftest FAIL on "(g) --supersede: step-2 moves to step-2.superseded-1..." and "(g) ... next free k"; replacing `solo = b is None and order.newest(d, 'solo') is not None` (steps.py:3314) with `solo = False` made it FAIL on "swap: a solo task dir with solo-L2.md ...". The no-flag refusal case ("--supersede negative control ... refuses, writes nothing") is in the run and passed.
- #2 grep -c 'supersede\|solo task dir' >= 5: pass. Evidence: count printed 17 (>= 5); the new "(g) --supersede" lines (4) and "swap: a solo task dir ..." line are among the matches.
- #3 grep -n shard verifier.md prints rule 5's line: pass. Evidence: `grep -n shard plugins/sdlc-lite/agents/verifier.md` prints line 22, the rule 5 sentence naming the 600000 ms cap, Playwright --shard, and reporting each shard.
- #4 claude_roles/codex_roles generate --check exits 0: pass. Evidence: "Claude agent definitions verified (23 files)" and "Codex agent definitions verified", rc=0. git diff shows verifier-L1/L2/L3.md, verifier.md and the six sdlc-verifier-l*.toml changed one line each (the rule), matching the source.
- #5 check.sh exits 0: pass. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` rc=0; tail shows run selftest PASS, hook selftest PASS, hook live probe selftest PASS, ok: shellcheck, ok: plugin validate.

## Out of scope changes
None. The diff holds steps.py, verifier.md and its generated agents (the files the ticket names). The .sdlc/0532 handoff.md gained the "## Acceptance criteria" section (the criteria under check) and the dir has run-record files; both are ticket bookkeeping. `criteria_indexed` gained a defaulted `heads` parameter, so its other callers are unchanged (full selftest and check.sh green).

## For the next attempt
None

## Notes
- plugins/sdlc-lite/scripts/steps.py:355-358: the swap usage text now runs a sentence on one overlong line (starts "light path). A solo task dir ..."), cosmetic only.
