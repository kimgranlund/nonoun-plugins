## Task goal
Add `tickets.py migrate-layout [--dry-run] [--rewrite-refs]` for flat to topics migration.

## Step 2: migrate-layout guidance and upgrade note, then gates green
level: L2
guard timeout: 1450
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/AGENTS.md`
### Do
1. In `docs/references/sdlc-internals.md`, add one passage on `migrate-layout [--dry-run] [--rewrite-refs]` to the `scripts/tickets.py` entry (line 39). Cover:
   - the preconditions: git work tree, clean tree, no loose root file, no existing target;
   - the moves;
   - the cite scan and its rewrite rule: relative forms are re-expressed from the citing file's new location, and managed blocks and `docs/reports/` are never rewritten;
   - the two config lines, the regeneration and closing `check`, and the `nothing to migrate` second run.

   This is the implementation reference, so state only what step 1 built.
2. In `plugins/sdlc-lite/skills/ticket/SKILL.md`, the `argument-hint` (line 4) gains `| migrate-layout [--dry-run] [--rewrite-refs]`. Rules gains one bullet, the consumer upgrade note:
   - a flat `.sdlc/` keeps working, and `check` warns;
   - to move, commit everything and run `tickets.py migrate-layout --dry-run` to see each move and citing file;
   - then run `migrate-layout --rewrite-refs` (or fix the cites by hand), commit, and run `onboard.py setup` to refresh the root `AGENTS.md` block;
   - `docs/reports/` records are never rewritten;
   - a `layout: flat` line in `.sdlc/config` keeps the flat layout and silences the warning.

   A release's upgrade notes go into its dated `docs/reports/release-*.md` when it ships (precedent: `docs/reports/release-0.20.2.md:20`), and a release is a non-goal here, so this bullet is the shipped note. Leave to T-0207 (its handoff Do) the path text in skills and docs that still names `.sdlc/roadmap.md` or `.sdlc/notes.md`, including the config line list in `skills/handoff-format/SKILL.md:39` and this skill's `ticket_root` bullet.
3. Gates. Run every guard below and fix any red that step 1 or this step introduced, inside the allowed files.
   - No agent preloads `skills/ticket`: `grep -n "^skills:" -A8 plugins/sdlc-lite/agents/*.md` names no ticket skill. So `codex_roles.py generate --check` should stay green with no regeneration.
   - At plan time (HEAD 44168d55) every gate was green: `check.sh` rc 0 in 474 s, plus `check-packaging.py`, `codex_roles.py generate --check`, and `tickets.py --root .sdlc check` at rc 0.
   - A gate already red at the build-start HEAD comes back as Status `inherited red`.
   - Never run `migrate-layout` on this repository (handoff Constraints).

Depends on: step 1.
### Acceptance criteria
- `grep -qF 'migrate-layout [--dry-run] [--rewrite-refs]' docs/references/sdlc-internals.md`
- `sed -n '/^argument-hint:/p' plugins/sdlc-lite/skills/ticket/SKILL.md | grep -qF 'migrate-layout [--dry-run] [--rewrite-refs]' && grep -F migrate-layout plugins/sdlc-lite/skills/ticket/SKILL.md | grep -F 'onboard.py setup' | grep -qF 'layout: flat'`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite docs/maintenance`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'plugins/sdlc-lite/scripts/tickets\.py|docs/maintenance/sdlc-internals\.md|plugins/sdlc-lite/skills/ticket/SKILL\.md')"`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
