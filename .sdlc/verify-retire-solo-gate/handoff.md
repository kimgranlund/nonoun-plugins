# Re-verify T-0361 (finish the headless retirement) on main

## Goal
Independently re-verify T-0361 at main HEAD. The first verifier of T-0288 (.sdlc/verify-retire-solohigh/verifier-L3.md) failed three criteria; T-0361 claims to fix them. You are a different family from the builder (solo sonnet).

## Intent
- Do: read the closed folder .sdlc/.0361-retire-solo-gate/handoff.md and check every Done-when criterion with an observed command in a throwaway git archive copy (git-initialised, under your tmp prefix; no worktrees), with a red control for each guard. Specifically re-run the verifier's original observations: (1) with SDLC_CLAUDE_EXEC unset and a stub `claude` on PATH, `solo_run.py run --exec --no-worktree --task-dir <dir> --tier L1 --brief b` must exit 2 with one line pointing to fanout.py prep or dispatch.py prepare and must not start the stub; with SDLC_CLAUDE_EXEC=1 it must start as before; `fanout.default_driver(handoff,'solo','L1'|'L2')` must refuse without the flag; `fanout.py prep` and `land` and `--driver CMD` still work. (2) deleting the SDLC_CLAUDE_EXEC gate lines inside fanout.default_driver must turn check.py red. (3) grep for stale text named in the ticket (legacy default, until T-0288, fanout --driver help, skills/fanout/SKILL.md, agents/solo.md and the generated solo-L*.md, docs/references/sdlc-internals.md) finds none. Also run `bash plugins/sdlc-lite/scripts/check.sh` result from /tmp/checksh-main5.log if present, and confirm nothing else (any model or effort row) changed: `git diff dc4f32aa HEAD -- plugins/sdlc-lite/adapters`.
- Non-goals: editing anything.
- Done when: pass or fail per criterion with the command and output.

## Constraints
Read-only. No em or en dashes.
