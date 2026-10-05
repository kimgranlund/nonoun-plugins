## Task goal
Document `supervisor.py` where a maintainer or consumer looks for it, with the smallest change that meets the criteria.

## Step 11: Document the supervisor
level: L2

### Do
Make the smallest change that meets the criteria: no refactors, no extra tests, no edits outside the three files below. If a criterion cannot be met, report blocked instead of looping.

Edit only `docs/maintenance/sdlc-internals.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, and `plugins/sdlc-lite/AGENTS.md`.
1. `docs/maintenance/sdlc-internals.md`: add one entry `## scripts/supervisor.py` in the style of its neighbors. Read the module docstring of `plugins/sdlc-lite/scripts/supervisor.py` and `.sdlc/supervisor/AGENTS.md` text it generates (`init`), and summarize: what it is (a deterministic watcher, no model call), commands, defaults (dry run unless `--run`, modes `ephemeral` default, `attached`, `notify`), limits, the lock, the `STOP` file, `status.json`, that it never claims or moves a message, that a woken host follows unattended rules, and the live-run record `docs/reports/supervisor-live-run.md`. Keep it to one dense paragraph in the file's existing style.
2. `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: in the layout block add one line for `.sdlc/supervisor/` (written by `supervisor.py init`; `hosts.local.json`, `state.json`, `status.json`, `lock`, and `STOP` stay local), and in the ignore list add the entries the supervisor docstring says to ignore.
3. `plugins/sdlc-lite/AGENTS.md`: add one bullet under Behavioral invariants: the supervisor never claims, moves, or reads a message body, and a wake follows unattended-run rules (never push or publish).
No em dash anywhere.

### Acceptance criteria
- `grep -q 'scripts/supervisor.py' docs/maintenance/sdlc-internals.md`
- `grep -q '.sdlc/supervisor/' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -q 'supervisor' plugins/sdlc-lite/AGENTS.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `! grep -q "$(printf '\342\200\224')" docs/maintenance/sdlc-internals.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "docs/maintenance/sdlc-internals.md|plugins/sdlc-lite/skills/handoff-format/SKILL.md|plugins/sdlc-lite/AGENTS.md" | { ! grep -q .; }`
