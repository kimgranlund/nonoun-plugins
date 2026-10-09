<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py` passes, including the five handshake and fingerprint tests: pass. Evidence:
  - The built tree gives rc=0 and `OK`. The diff at `plugins/sdlc-lite/scripts/codex-selftest.py:169-199` adds five tests covering equal -> `ready`, differs -> `refused` with "Start a fresh Codex session", and absent or not-first-line -> `unknown` with "Handshake required". The other two tests cover the fingerprint embed and the CLI exit codes 0/2/3.
  - **Bite at base:** I copied the new selftest into a throwaway worktree at `$SDLC_BASE_SHA` e2a96eeb. Result: `FAILED (errors=5)`, all five new tests.
  - **Mutation NC1:** I applied the built patch and made `check_loaded` skip the mismatch branch. Result: `FAIL: test_handshake_cli_exit_codes` and `FAIL: test_handshake_different_fingerprint_is_refused_with_fresh_session_action`.
  - **Mutation NC2:** I swapped the first-line `re.fullmatch` for `re.search` over the whole report. Result: `FAIL: test_handshake_absent_fingerprint_is_unknown_and_requires_handshake`. So the not-first-line conjunct bites too.
  - **process-deviations.md:** this file does not exist in the artifacts dir. The red run above is my own.
- `codex_roles.py generate --check`, `claude_roles.py generate --check`, `check.py` and `tickets.py --root .sdlc check` pass: pass. Evidence:
  - `codex_roles.py generate --check`: "Codex agent definitions verified", rc=0.
  - `claude_roles.py generate --check`: "Claude agent definitions verified (22 files)", rc=0.
  - `check.py`: "ok: 19 role levels, 9 agents, 22 generated definitions checked", rc=0.
  - `tickets.py --root .sdlc check`: rc=0, with warnings only about closed-ticket placeholders and the flat layout.
- Every `adapters/codex/agents/*.toml` ends with a `# Profile fingerprint` note whose `profile:` equals `codex_roles.py fingerprint <name>`: pass. Evidence:
  - I looped over all 28 tomls, comparing the tail `# Profile fingerprint` and the `exactly \`profile: X\`` value with `codex_roles.py fingerprint <name>`. Output: `tomls=28 bad=0`. Example: sdlc-solo-l2 ends with `profile: 0.22.0+289fe91aa9d5`.
  - **NC:** in the throwaway tree I changed that toml's fingerprint to `0.21.3+...`. The loop reported `got=0.21.3+289fe91aa9d5 want=0.22.0+289fe91aa9d5`, and `generate --check` exited 2 with "generated agent drift".
- `install --check` code path unchanged; `instructions.md`, `agents/solo.md` and `skills/agent/SKILL.md` describe the handshake: pass. Evidence:
  - **install:** `git diff -U0 codex_roles.py` has hunks only at lines 85, 130 (the `definitions`/`raw_definitions` split), 371, 379 and 397 in `main`. `def install` sits at line 286 and has no hunk.
  - **Selftest:** the existing install --check tests still pass, for example "refusing to overwrite".
  - **Docs:** each of the three docs has a handshake passage. `instructions.md` has a "Profile handshake." paragraph. `solo.md` says "first line must be `profile: <fingerprint>`, checked with `codex_roles.py handshake` before any edit is accepted (mismatch: fresh Codex session; absent: `live freshness unknown`)". `SKILL.md` has the equivalent text in the solo row.
- The T-0287 answer is recorded in this file: pass. Evidence: the handoff `## Result (solo, 2026-10-08)` second bullet says T-0378 first shipped in v0.22.0, so a pre-0.22 profile carries no red-checkpoint instruction. It calls this a plausible cause and leaves maison's actual loaded version unverified. The live Codex behavior is also marked unverified there.
- **Constraint (no em or en dashes):** `git diff --word-diff=porcelain` added words matching U+2013 or U+2014 give a count of 0.

## Out of scope changes
None.
- `agents/solo-L1.md`, `solo-L2.md` and `solo-L3.md` are generated from `solo.md`. `claude_roles.py generate --check` passing means they had to change.
- The 28 `adapters/codex/agents/*.toml` files are generated. `codex_roles.py generate --check` passes on them.
- The handoff Result section is the T-0287 record the criteria ask for.

## For the next attempt
None
