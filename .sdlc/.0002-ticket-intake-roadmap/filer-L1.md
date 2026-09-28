<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None. All three steps have a verifier verdict of pass: step 1 at L1, step 2 at L2 (Fable), and step 3 at L1.

## PR title
Add /ticket: typed tickets with next id, generated roadmap, and check (T-0002)

## PR body
### Summary
This adds a `/ticket` skill backed by `scripts/tickets.py`. It stamps a typed ticket with the next id and generates `.sdlc/roadmap.md` in dependency order from ticket front matter. It also validates tickets and fails when the roadmap is stale. Free-text briefs stay with `/handoff`.

### Changes
1. Skill and templates (step 1)
   - `plugins/sdlc-lite/skills/ticket/SKILL.md`: the `/ticket` skill. With no args it runs `check`. It says the roadmap is never edited by hand.
   - `skills/ticket/templates/{feature,bug,chore,spike,idea}.md`: one template per type. Each carries the handoff-format front matter and placeholder lines (`id: T-0000`, `title: ""`, `created: YYYY-MM-DD`).
2. `scripts/tickets.py` (step 2): stdlib-only Python 3, with `--root` defaulting to `.sdlc`.
   - `new <type> <slug> ["title"]`
     - Assigns max id + 1.
     - Looks for the template in `<root>/_templates/<type>.md` first, then the plugin's templates.
     - Refuses an existing slug, an unknown type, or existing bad tickets.
     - Regenerates the roadmap.
   - `roadmap`: writes a byte-stable table in topological order, with ties broken by id (Kahn's algorithm with a min-heap).
   - `check` fails on:
     - a missing field or a bad enum value
     - a bad id or bad `created`
     - a duplicate id
     - a dangling `depends` or `from`
     - a cycle or self-cycle
     - a stale roadmap
   - A handoff with no front matter is skipped silently.
   - `selftest`: one mutation per failure class, plus a negative control.
   - `scripts/check.sh` now runs `tickets.py selftest`.
3. Docs and routing (step 3)
   - `handoff-format/SKILL.md`: adds `roadmap.md` and `_templates/` to the layout, and names `tickets.py` as the only front matter parser.
   - `CLAUDE.md`: adds `/ticket` and a `tickets.py` bullet, and notes the selftest in the check.sh description.
   - `conductor.md`: adds the route line.
   - `sdlc-lite-author.md`: its check.sh list now includes the tickets selftest.

### How each was verified
- Step 1 (verifier L1, pass)
  - The template listing is exact, and each template has each placeholder exactly once with a matching `type:`.
  - A grep for gen-ui text finds nothing. A copy of a template seeded with gen-ui text was used to confirm the grep does match.
  - `check.sh` exits 0, including `ok: plugin validate`.
- Step 2 (verifier L2, pass)
  - `selftest` passes. A copy of the script with cycle detection switched off makes selftest fail, so the selftest can go red.
  - Fixture run: `new` gives T-0001 then T-0002. Adding a dependency makes `check` report stale. After `roadmap`, the T-0002 row comes before the T-0001 row.
  - Running `roadmap` twice leaves the file byte-identical (`cmp` exits 0).
  - All nine negative controls exit 1 with a stderr line naming the problem. The cycle case prints no traceback.
  - A plain handoff with no front matter still passes `check`.
  - `new` refuses an existing slug and leaves the file unchanged (same md5). `new` with an unknown type lists the five types.
  - `check.sh` exits 0 and shows `tickets selftest: PASS`. At HEAD that line is absent.
  - `board.py` still exits 0.
- Step 3 (verifier L1, pass)
  - All grep criteria pass.
  - The statement that `run.sh` and `board.py` do not parse front matter is still true.
  - `check.sh` exits 0.
  - The diff touches only the files named in the plan. The `check.sh` change comes from step 2.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `/ticket` (`scripts/tickets.py`). `new` stamps a typed ticket (feature, bug, chore, spike, idea) with the next `T-NNNN` id. `roadmap` generates `.sdlc/roadmap.md` in dependency order. `check` validates ticket front matter and fails on a stale roadmap. `check.sh` now runs the tickets selftest.

## Follow-ups
- Bring this repo's backlog under `/ticket`. It lives in flat files (`.sdlc/tickets/T-*.md`), and `tickets.py` does not scan them. Their ids also collide with task dirs (T-0002 is used by both). This is from the plan's Risks.
- Add `close` to `tickets.py`. It was left out because it belongs to T-0003.
