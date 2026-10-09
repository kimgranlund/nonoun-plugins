<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
fail

## Criteria
- `bash plugins/sdlc-lite/scripts/run-selftest.sh 2>&1 | tail -1 | grep -qx 'run selftest: PASS'`: pass. Evidence: in the built tree, under bash, `c1=0` and the last line is `run selftest: PASS`. I checked that the test can fail: I copied the new run-selftest.sh into a throwaway worktree at d85d9eef (the pre-build run.sh) and it printed `run selftest: FAIL: base shared handoff, lane prerequisite: SDLC_BASE_SHA is 'f3eb65b7...', want the stored lane commit 96c831b7...`. So the new case was red before the change.
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1 | grep -c '^ok: a main-checkout handoff run from the lane' | grep -qx 2`: pass. Evidence: rc=0, count `2`, `dispatch selftest: PASS`. I checked that it can fail: in the throwaway copy I made `exec_tree` always `return directory`, and all four shared-shape cases printed `FAIL:` while the negative control stayed `ok`.
- `grep -q 'base shared handoff, lane prerequisite' plugins/sdlc-lite/scripts/run-selftest.sh && grep -q 'SDLC_BASE_SHA refused' plugins/sdlc-lite/scripts/run.sh`: fail. Evidence: under bash, `a=0` and `b=1`. The message at run.sh:476 is `supplied SDLC_BASE_SHA $supplied refused: ...`, which puts the sha between `SDLC_BASE_SHA` and `refused`, so the literal string is not in the file. I steelmanned this first: the builder would say the refusal message exists. It does, but the criterion as written is red. The builder wrote this criterion, so changing the message or the criterion are both simple fixes.
- `python3 plugins/sdlc-lite/scripts/check.py && ... tickets.py --root .sdlc check && ... codex_roles.py generate --check && ... claude_roles.py generate --check`: pass. Evidence: under bash, check.py rc=0 (`ok: 19 role levels, 9 agents, 22 generated definitions checked`), tickets t=0 (warnings only), cx=0 (`Codex agent definitions verified`), cl=0 (`Claude agent definitions verified (22 files)`). This is a gate, so the bite test does not apply.
- Codex host unverified live; the Codex native request path reaches the same run.sh base block: pass, by source read, and Codex is UNVERIFIED live as the handoff allows. Evidence: run.sh:423 sets `cmd=(python3 .../codex_exec.py ...)` before the base block at run.sh:434-487. run.sh:631 launches `env ... ${base_env[@]} ... "${cmd[@]}"` for both backends. Nothing between them branches on the backend.
- Done when, discriminating rerun (handoff in MAIN, lane on a different commit, a supplied base; the request base equals the lane merge-base): fail. Evidence: I built a fixture under the tmp prefix. The main repo is r0, c0, m1; a detached lane worktree from c0 adds c1 and c2, so the lane merge-base is c0 (85ec2258). I ran `dispatch.py prepare builder L3 <main>/.sdlc/w/handoff.md --dry-run` from the lane. run.sh:466-485 holds the same rule, and the selftest gives run.sh the same results.
  - a) Nothing supplied and nothing stored gave the lane HEAD c2 (5b30c1c2), not the merge-base c0.
  - b) Supplied `SDLC_BASE_SHA=r0` was refused, but the base became the lane HEAD c2, not the merge-base c0.
  - c) Supplied c0 gave c0.
  - d) Stored r0 gave c2.
  - e) Stored c1, a valid ancestor that is not the merge-base, was kept as c1. The Do says to refuse it unless the handoff names it.
  - Nothing reads a base named in the handoff; run.sh and dispatch.py only look at the env var and base-sha. That leaves the T-0295 case open: the handoff names 4022eee64 and the request carried da6e1f2.
  - The selftests prove that a valid supplied base is now kept (the T-0152 case) and that git runs in the lane. They do not prove the "equals the lane merge-base" outcome. In run-selftest the stale and supplied-stale cases expect the lane HEAD or the stored lane commit, not the fork.
  - Steelman: the builder would say that falling back to HEAD is the T-0376 "build start" rule and that a merge-base base would pull earlier tickets' lane commits into the scope diff. That conflict is real when a lane runs several tickets without merging back. But the Do settles it explicitly: the merge-base is taken against the "recorded integration or named base", and the build does not use the recorded integration either; its floor is the main checkout HEAD or SDLC_BASE_REF. So the finding stands.
- Done when, a shared handoff in MAIN with the lane as cwd keeps the right base for steps.py, dispatch.py and run.sh: fail for steps.py, pass for dispatch.py and run.sh (selftest cases above).
  - The diff does not touch steps.py, and no check covers it in the shared shape.
  - By source read, `base_sha(top, d)` at steps.py:686-698 uses `top = git_toplevel(<step dir in MAIN>)` (steps.py:2631, 2827). It reads base-sha when the file exists but falls back to `rev_commit(top, 'HEAD')`, which is the MAIN HEAD, not the lane.
  - No run evidence exists for steps.py.

## Out of scope changes
- `.sdlc/0381-runner-wrong-lane-base/handoff.md`: the solo run appended its own `## Acceptance criteria` section. The file mtime is 15:28:59, inside the solo run window (runs.jsonl ts 22:32:23Z with duration 1829 s, so it started about 15:02 local). That is a handoff edited after a role read it and criteria written by the builder itself. I judged the ticket's Done when items alongside those criteria for that reason.
- `docs/references/sdlc-internals.md`: in scope. I read the diff: one sentence in the run.sh paragraph describing the T-0381 base rule, which is the required reference update for a behavior change.
- Not changed but affected: `plugins/sdlc-lite/scripts/solo_run.py:125` records `base_sha=head_sha(task_dir)`. With the task dir in MAIN, that is the MAIN HEAD in the shared shape (solo_run.py:98-101). It is not named in the Do, so this is a follow-up, not a fail.

## For the next attempt
1. Make criterion 3 green. Either reword run.sh:476 to contain the literal `SDLC_BASE_SHA refused` (for example `run.sh: SDLC_BASE_SHA refused: supplied <sha> is not ...`, and do the same at dispatch.py `say(...)` for parity), or fix the criterion.
2. Implement the Do's base rule in run.sh (run.sh:466-485) and dispatch.py `build_base`:
   - The base is the merge-base of the execution tree (lane) HEAD with the recorded integration or named base.
   - A supplied or stored value that is a valid ancestor but not that merge-base is refused unless the handoff names it explicitly.
   - Today the fallback is the lane HEAD, a stored valid ancestor such as c1 is kept, and a base named in the handoff is never read.
   - Add a selftest case that reproduces the ledger shape and was red before the fix: handoff in MAIN, lane with commits after the fork, a wrong but valid supplied or stored base, expecting the lane merge-base.
   - If that rule conflicts with T-0376's build-start-HEAD rule for lanes with several tickets, that is a design question for the conductor to settle before building. Do not decide it silently.
3. Cover steps.py in the shared shape. `base_sha` and `git_toplevel` at steps.py:686 resolve from the step dir in MAIN and fall back to the MAIN HEAD. Either run steps.py's git in the lane cwd, or add a check showing it keeps the lane base, as Done when item 2 requires.
