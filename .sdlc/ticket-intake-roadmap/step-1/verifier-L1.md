<!-- role=verifier level=L1 model=sonnet effort=medium -->
All changes are within scope (new files only, in the ticket skill directory and the sdlc task artifacts). No tracked files modified. Everything checks out.

## Verdict
pass

## Criteria
- `ls plugins/sdlc-lite/skills/ticket/templates/` lists exactly `bug.md chore.md feature.md idea.md spike.md`: pass. Evidence: `ls plugins/sdlc-lite/skills/ticket/templates/` → `bug.md chore.md feature.md idea.md spike.md`.
- Each template has `id: T-0000`, `title: ""`, `created: YYYY-MM-DD` each occurring exactly once, and `type:` matching its own filename: pass. Evidence: looped `grep -c` over all 5 files, each printed `1 1 1` and `type:` line matched filename (bug.md→`type: bug`, chore.md→`type: chore`, feature.md→`type: feature`, idea.md→`type: idea`, spike.md→`type: spike`).
- `grep -n 'gen-ui\|svelte\|Panda' plugins/sdlc-lite/skills/ticket/templates/*.md` prints nothing: pass. Evidence: command produced no output, exit code 1. Negative control confirmed the check can go red: appended "gen-ui test line" to a copy of feature.md and reran the grep, which matched line 25 and exited 0.
- `plugins/sdlc-lite/skills/ticket/SKILL.md` contains `name: ticket`, the `tickets.py` allowed-tools entry, and a line saying the roadmap is never hand-edited: pass. Evidence: file read shows `name: ticket` (line 2), `allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py:*)` (line 5), and "Never hand-edit `.sdlc/roadmap.md`." (line 14).
- `plugins/sdlc-lite/scripts/check.sh` exits 0, including `ok: plugin validate`: pass. Evidence: ran `bash plugins/sdlc-lite/scripts/check.sh` → output includes `ok: 18 role levels, 8 agents checked`, `selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`, exit code 0.

Additional spot checks: all 5 templates' front matter fields (`status`, `size`, `priority`, `depends: []`, inline `# allowed values` comments) match the feature template's pattern, and body sections match the handoff's spec per type (feature/chore: Goal/Intent/Context/Constraints; bug: Goal/Repro/Expected/Actual/Context/Constraints; spike: Question/Goal/Context/Constraints; idea: Goal/Context/Constraints). Front matter fields match `plugins/sdlc-lite/skills/handoff-format/SKILL.md` lines 25-41 ("Ticket front matter").

## Out of scope changes
None. `git status --porcelain=v1` shows only two untracked paths: `plugins/sdlc-lite/skills/ticket/` (all files required by this step) and `.sdlc/ticket-intake-roadmap/` (sdlc task/run artifacts, not project code). No tracked files were modified (`git diff --stat` empty).

## For the next attempt
None.
