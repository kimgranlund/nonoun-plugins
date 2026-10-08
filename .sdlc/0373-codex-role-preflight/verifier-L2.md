<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
fail

## Criteria
- 1. `codex-selftest.py -k preflight` passes five cases and was seen failing first: pass. Evidence: `python3 plugins/sdlc-lite/scripts/codex-selftest.py -k preflight` on the built tree gives "Ran 5 tests ... OK", exit 0. The five tests are `test_preflight_current_definitions_stale_live_catalog_is_not_ready`, `..._stale_definitions_with_older_roles_loaded_is_not_ready`, `..._fresh_session_with_required_role_is_ready`, `..._unknown_role_and_edited_definition_need_launcher_repair_and_install_check_unchanged` and `..._cli_requires_a_supplied_catalog`. To see it fail first, I copied the new test file into a throwaway worktree at `$SDLC_BASE_SHA` (687d169e) and ran it against the unchanged `codex_roles.py`: "FAILED (failures=1, errors=4)", with `AttributeError: module 'codex_roles' has no attribute 'preflight'` four times and `invalid choice: 'preflight'` once. Negative control: in the throwaway copy of the built `codex_roles.py` I changed `if role not in catalog:` to `if False:`. The cli, stale-catalog and stale-definitions tests then failed (failures=3). So the catalog check is what makes the not-ready cases go red, and they cannot pass vacuously.
- 2. `install --check` behavior unchanged: pass. Evidence: `git diff -U0 plugins/sdlc-lite/scripts/codex_roles.py` shows only the hunk headers `@@ -277,0 +278,35 @@`, `@@ -283,0 +319,3 @@` and `@@ -288,0 +327,13 @@`. All three are additions after the end of `install()`, so `install()` itself is untouched. `codex-selftest.py -k test_install_is_idempotent_and_preserves_edits` gives "Ran 1 test ... OK". The launcher-repair test (codex-selftest.py:157-167) asserts that a preflight on an edited definition reports `refusing to overwrite`, that the user edit is kept, and that `install(check=True)` still raises.
- 3. Readiness section in instructions.md, routing from three files, and the bars: fail. Evidence:
  - The section is complete. `adapters/codex/instructions.md:27` holds "# Readiness and resume for conductors". Line 29 has the parent-supplied catalog and says "there is no host introspection API". Line 31 has `preflight ... --catalog`/`--catalog-file`, and the exact missing role with the generation, fresh-session or launcher-repair action. Line 33 bars substituting a builder, falling back to Claude and starting a nested Codex CLI, and has the native solo `solo-<level>-<attempt>.request.json` check. Lines 35-41 hold the resume packet.
  - The routing clause fails. `grep -l "Readiness and resume" plugins/sdlc-lite/agents/solo.md plugins/sdlc-lite/skills/agent/SKILL.md plugins/sdlc-lite/skills/sdlc-lite/SKILL.md` matches only `skills/sdlc-lite/SKILL.md` (line 67). `agents/solo.md:44` and the `solo` row of `skills/agent/SKILL.md:16` repeat the preflight command inline. Neither names the section or `instructions.md`. A reader following `/agent solo` to solo.md therefore never reaches the resume packet, the request-file check after a fresh session, or the full not-ready action list.
  - Steelman, rebuttal checked and rejected: the generated Codex TOMLs embed the section (`grep -c` gives 1 in `sdlc-solo-l2.toml` and in `sdlc-conductor-l1.toml`), so Codex agents do receive it. But the criterion names these three files as the routing surface, and two of them do not point to it. The criterion can be met, so this is not a plan defect.
- 4. All six gates pass: pass. Evidence:
  - `python3 plugins/sdlc-lite/scripts/check.py`: "ok: 19 role levels, 9 agents, 22 generated definitions checked", exit 0.
  - `tickets.py check`: "ok: 370 tickets, roadmap current", exit 0. Its warnings are only about closed tickets and the flat layout.
  - `codex_roles.py generate --check`: "Codex agent definitions verified", exit 0.
  - `claude_roles.py generate --check`: "Claude agent definitions verified (22 files)", exit 0.
  - `bash plugins/sdlc-lite/scripts/run-selftest.sh`: "run selftest: PASS", exit 0.
  - `codex-selftest.py`: "Ran 32 tests ... OK", exit 0.
- 5. Live Codex fresh-session behavior recorded as unverified: pass. Evidence: `adapters/codex/instructions.md:31` says "live behavior stays unverified until the first request file appears". The CLI's ready line also prints "(live behavior unverified)" (codex_roles.py, preflight branch of main), observed in the selftest assertion `ready: sdlc-solo-l2`. No Codex host was run here.

## Out of scope changes
None. Dismissals, each with its check:
- The 28 changed `adapters/codex/agents/*.toml` files are generator output of the `instructions.md` edit. The sdlc-builder-l1.toml diff shows only the inserted Readiness section, and `codex_roles.py generate --check` passes.
- `agents/solo-L1.md`, `solo-L2.md` and `solo-L3.md` are generator output of the `solo.md` edit. The diffs are the same one-line insertion, and `claude_roles.py generate --check` passes.
- `.sdlc/0373-codex-role-preflight/handoff.md` gained only the `## Acceptance criteria` section (`git diff` of that file).
- `git diff --check` is clean, and no added non-generated line contains an em or en dash (grep for U+2013/U+2014 in added lines returned 0).

## For the next attempt
Criterion 3, routing clause. Two files need a pointer to the "Readiness and resume for conductors" section of `adapters/codex/instructions.md`:
- The Codex paragraph of `plugins/sdlc-lite/agents/solo.md` (line 44). Then run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` so `solo-L1.md`, `solo-L2.md` and `solo-L3.md` follow.
- The `solo` row of `plugins/sdlc-lite/skills/agent/SKILL.md` (line 16).

Each pointer should name the section and say that the resume packet and the request-file check after a fresh session are there. Nothing else in the build needs to change. Afterwards re-run `check.py`, both `generate --check` commands and `codex-selftest.py`.
