## Task goal
`tickets.py` can use a `tickets/` ticket root under `.sdlc/` when `<root>/config` says `ticket_root: tickets`, and `tickets.py roadmap` keeps a managed router block in `.sdlc/AGENTS.md` current, so an agent reads one short file and opens only the tickets in the stage it needs.

## Step 8: Gates green and the repo's own router
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 to 7.
1. Run `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap` once from the repository root. It regenerates `.sdlc/roadmap.md`, which is stale at the build-start HEAD because the T-0176 handoff's size changed. It also creates `.sdlc/AGENTS.md` and `.sdlc/CLAUDE.md`. Never edit them by hand. The repo has no `ticket_root` line, so the router reads `Ticket folders: next to this file`.
2. Run every gate below. Fix any red that steps 1 to 7 introduced, within the scope list below. A gate already red at the build-start HEAD comes back as `inherited red`.
3. The fanout, board, traces, and onboard selftests run inside `check.sh` and are the contract dependents of the router writes. If one is red, name the cause in the builder result.
4. In the result, name `scripts/fanout.py` regular-lane support for `ticket_root` as a follow-up.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import onboard; f = onboard.find_block(open('.sdlc/AGENTS.md').read()); assert f.status == 'block' and onboard.digest(f.block.text) == f.block.digest, f" && grep -qx '@AGENTS.md' .sdlc/CLAUDE.md && grep -qxF -- '- Ticket folders: next to this file.' .sdlc/AGENTS.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; echo .sdlc/AGENTS.md; echo .sdlc/CLAUDE.md; } | python3 -c "import sys, pathlib; bad = [p for p in (l.strip() for l in sys.stdin) if p and pathlib.Path(p).is_file() and chr(8212) in pathlib.Path(p).read_text(encoding='utf-8')]; print('\n'.join(bad)); sys.exit(1 if bad else 0)"`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/tickets.py|plugins/sdlc-lite/scripts/board.py|plugins/sdlc-lite/scripts/traces/ingest.py|plugins/sdlc-lite/scripts/traces/sources/tickets.py|plugins/sdlc-lite/scripts/traces/selftest.py|docs/maintenance/sdlc-internals.md|plugins/sdlc-lite/skills/handoff-format/SKILL.md|plugins/sdlc-lite/skills/ticket/SKILL.md|docs/ticket-stages/design.md|docs/ticket-stages/README.md|docs/README.md|docs/validation/ticket-root-router-live-run.md" | { ! grep -q .; }`
