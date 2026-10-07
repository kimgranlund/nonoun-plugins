# Verify T-0222: fanout solo lane writes the ## Skipped entries the skips guard needs

## Goal
Independently verify the diff `git diff main...HEAD` on branch fanout-skips (T-0222).

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and prints `fanout selftest: PASS`. Case 16 runs two solo tickets in one lane through the real `steps.py lane`, the default driver (a `claude` shim on PATH is the only stand-in) and the real `tickets.py close`, and asserts both tickets are `status: done` and skips.md holds `- lane: solo` plus `- skip: planner; step: all;` and `- skip: filer; step: all;`.
2. Negative control, by running it yourself: with the `write_solo_skips` call in `run_ticket` removed or `FANOUT_SELFTEST_NO_SKIPPED=1` set for a real two-ticket solo lane, the close is refused (`close refused`, `no ## Skipped entry`). Show that the same run without the env var closes both tickets.
3. The skips guard is unchanged: `git diff main -- plugins/sdlc-lite/scripts/tickets.py` is empty, and `write_solo_skips` writes only when skips.md already holds a `- lane:` line, is idempotent, and writes nothing for a missing skips.md.
4. `bash plugins/sdlc-lite/scripts/check.sh` exits 0, and `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0.
5. `docs/reports/fanout-solo-live-run.md` addendum: every number it states (4 minutes 27 seconds, 18:01:11 to 18:05:38, exit 0, 24/24, four close commits, lane starts 18:01:12/15/18/21, models, 753 to 6,153 output tokens, $2.20) is backed by a file under `docs/reports/fanout-solo-live-run/rerun-t0222/`, and `git ls-tree -r HEAD docs/reports/fanout-solo-live-run/rerun-t0222` lists them (none is gitignored: `git check-ignore` prints nothing for them).
6. plugins/sdlc-lite/skills/fanout/SKILL.md no longer says "4 to 6 lanes", says up to 4 lanes (the default cap), and both the skill and docs/references/sdlc-internals.md state that the overlap refusal reads only `step-<n>/` handoffs and cannot fire for solo tickets.
7. `git diff --check main..HEAD` is clean and no em dash appears in the changed text files.
