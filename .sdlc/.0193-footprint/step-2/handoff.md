## Task goal
Add scripts/footprint.py that measures a ticket's footprint and can gate on it.

## Step 2: Wire into check.sh, document, record baseline, gates green
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1.
- In `plugins/sdlc-lite/scripts/check.sh`:
  - Add the line `python3 "$root/scripts/footprint.py" selftest || fail=1` directly after the `messages.py` selftest line.
  - Add `footprint.py` to the selftest list in the header comment (the `# Plugin checks: ... messages.py selftests` line).
- In `docs/references/sdlc-internals.md`, add a `## \`scripts/footprint.py\`` entry directly after the `## \`scripts/order.py\`` entry. Keep it to 2 to 4 sentences:
  - what it measures (files, bytes, `.md` bytes, steps as `step-<n>` dirs with superseded dirs excluded, planner bytes, and role runs from every `runs.jsonl` by role and level);
  - that `check --max-files N --max-bytes N` exits 1 and names the exceeded limit;
  - that it is read-only on ticket folders;
  - that `check.sh` runs its selftest.
  The doc must name `--max-files`. Do not copy the Baseline table; `docs/lean-sdlc/design.md` stays its one home.
- Run `python3 plugins/sdlc-lite/scripts/footprint.py <dir>` for `.sdlc/.0188-tighten-idle-note`, `.sdlc/.0164-fix-skill-lints-task-folder`, `.sdlc/.0181-messages-wait`, and `.sdlc/.0175-ticket-root-router`. Paste the four outputs verbatim into this step's builder result, with one line stating that they match the design's Baseline table (`docs/lean-sdlc/design.md` "Baseline (measured 2026-10-03)").
- This is the gates green step. Run every gate below. If step 1 introduced any red, fix it inside `footprint.py`. Change no model or effort defaults, and make no version bump.
### Acceptance criteria
- `grep -qF 'scripts/footprint.py" selftest || fail=1' plugins/sdlc-lite/scripts/check.sh`
- `grep -qF 'scripts/footprint.py' docs/references/sdlc-internals.md`
- `grep -qF -- '--max-files' docs/references/sdlc-internals.md`
- `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/footprint.py -e plugins/sdlc-lite/scripts/check.sh -e docs/references/sdlc-internals.md)"`
- This step's builder result holds the `footprint.py` output for each of the four tickets T-0188, T-0164, T-0181, and T-0175, and those values match the design's Baseline table: steps, role runs, files, bytes, and `.md` bytes.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`
