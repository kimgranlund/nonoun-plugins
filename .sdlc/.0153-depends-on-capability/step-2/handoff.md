## Task goal
A ticket can depend on the specific fix it needs (a capability or file) instead of a serial integration ticket, so parallel work is not blocked until a human overrides the dependency.

## Step 2: Document the depends forms and provides
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
1. **`plugins/sdlc-lite/skills/handoff-format/SKILL.md`:**
   - In the front matter block, change the depends line to show `depends: [T-NNNN, file:<path>, cap:<name>, ...]`.
   - Add the line `provides: [name, ...]   # optional, capability names this ticket delivers` after `from:`.
   - In the paragraph after the block, add one or two sentences on what satisfies each form:
     - `file:` is repo-relative and met once the path exists; it never orders tickets.
     - `cap:` is met once a `done` ticket provides it, and orders the ticket after every provider.
     - `check` fails a malformed entry or an unprovided `cap:`.
2. **`plugins/sdlc-lite/skills/ticket/SKILL.md`:** add one Rules bullet stating the same forms, `provides:`, the `(unmet)` roadmap marking, and that a roadmap goes stale when a named file lands or a provider closes, so rerun `roadmap`.
3. **Templates:** in every template under `plugins/sdlc-lite/skills/ticket/templates/` with a `depends:` line, change only the trailing comment to name the forms, e.g. `# T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]`. Keep `depends: []` itself.
4. **`docs/references/sdlc-internals.md`:** in the `scripts/tickets.py` entry, add one sentence describing the `file:<path>`/`cap:<name>` entries and `provides`.
### Acceptance criteria
- `grep -qF 'cap:<name>' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qE '^provides: .*optional' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'cap:<name>' plugins/sdlc-lite/skills/ticket/SKILL.md`
- `grep -qF 'provides:' plugins/sdlc-lite/skills/ticket/SKILL.md`
- `for f in plugins/sdlc-lite/skills/ticket/templates/*.md; do if grep -q '^depends:' "$f"; then grep -E '^depends:' "$f" | grep -qF 'cap:<name>' || exit 1; fi; done`
- `grep -qF 'cap:<name>' docs/references/sdlc-internals.md`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
