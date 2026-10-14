## Task goal
Records dir: part A of SDLC Lite 0.23.0 lean work records (wave 1).

## Step 4: Layout docs, Codex resume packet, and gates green
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1, 2 and 3.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, the layout block :9-78:
  - The task folder holds `handoff.md` and `skips.md` and is committed. `skips.md` moves later (T-0542 or T-0543, per the 2026-10-13 decision).
  - `.sdlc/runtime/tasks/<task-slug>/` (the folder name without a leading dot) holds the role results, `runs.jsonl`, the attempt, dispatch, running, log and limit files, `base-sha`, `budget-ack.md`, and the `step-N/` dirs. It is ignored through `runtime/.gitignore`.
  - Write the legacy rule in one sentence, and name `${CLAUDE_PLUGIN_ROOT}/scripts/order.py records-dir <task dir>`. check.py item 42 refuses a `plugins/` or `../` path in a skill.
  - Replace the paragraph "Keep the results .md files, runs.jsonl, and *.attempt.json committed..." with "records are local and ignored". Drop the now-redundant per-file ignore list.
  - Keep the rest minimal. The docs specs belong to T-0545.
- `plugins/sdlc-lite/adapters/codex/instructions.md` resume packet (:37): leave the packet in the records dir that `order.py records-dir <task dir>` prints, not in the ticket folder. Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` if `generate --check` reports stale output.
- Gates:
  - Run `bash plugins/sdlc-lite/scripts/check.sh` (about 1320 s on record; slower under load).
  - Fix any red that steps 1 to 3 introduced by pointing the failing read or fixture at `order.records_dir` (or at `order.task_dir` for `skips.md`). Never fix it by moving a writer back.
  - A gate that is red at the build-start HEAD is `inherited red`.
  - Then run `python3 scripts/check-packaging.py` and `git diff --check`.
### Acceptance criteria
- (red) `grep -qF ".sdlc/runtime/tasks/<task-slug>/" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (red) `! grep -qE "Keep the results .{1,2}\.md.{1,2} files, .{1,2}runs\.jsonl" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (red) `sed -n '/^Resume packet/,/^$/p' plugins/sdlc-lite/adapters/codex/instructions.md | grep -qF "records-dir"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/.*)$" | { ! grep -q .; }`
