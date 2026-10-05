# Plan skills live run (T-0249 to T-0251)

Date: 2026-10-05. Host: Claude Code headless (`claude -p --plugin-dir plugins/sdlc-lite`, `SDLC_HEADLESS=1`, cap $2 per call), in a throwaway git project with three proposed chore tickets (T-0001 to T-0003, size M).

| Skill | Output (committed) | Check | Result |
|---|---|---|---|
| `/sdlc-lite:plan-goal` | `plan-skills-live-run.d/goal.txt` | `plan_check.py goal` on the returned block, run by me | passes, exit 0 |
| `/sdlc-lite:plan-loop` | `plan-skills-live-run.d/loop.txt` | `plan_check.py loop`, run by me | passes, exit 0; the skill itself flagged `:00` and `:30` timing |
| `/sdlc-lite:plan-fanout` | `plan-skills-live-run.d/fanout.txt` | `plan_check.py fanout` on the two-line block; `fanout.py run ... --dry-run` run by me on an earlier output | passes with three `no-budget` warnings; an earlier output of the same flag shape was dry-run by me with exit 0 (not a committed artifact; rerun `fanout.py run --dry-run <specs>` to reproduce) |

Defects found and fixed during the run: the skills asked for a temp file, which the host denied, so they now pipe the block to `plan_check.py` on stdin; the fanout dry-run permission pattern was too narrow and is widened to `fanout.py run:*`; the fanout skill returned one command while the validator requires a dry-run line first, so the skill now returns both lines. The goal and loop outputs in this directory are from before the stdin change, so `loop.txt` is the second loop run (checked by the skill itself) and `goal.txt` the first goal run.

Not exercised: `/goal` and `/loop` cannot run headlessly, so their host syntax is validated by `plan_check.py` only; Codex behavior is unverified; the fanout command was dry-run but not launched.

Verifier (L3 Fable) found write-capable tool grants in the skills and three inaccurate fanout rule statements; both were fixed in a follow-up commit (grants narrowed to `tickets.py check`, `fanout.py run --dry-run`, `steps.py lane`, which records skips.md). Known gap: `plan_check.py selftest` has no mutant for 15 of the rules.
