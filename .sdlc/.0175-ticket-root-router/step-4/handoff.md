## Task goal
`tickets.py` can use a `tickets/` ticket root under `.sdlc/` when `<root>/config` says `ticket_root: tickets`, and `tickets.py roadmap` keeps a managed router block in `.sdlc/AGENTS.md` current, so an agent reads one short file and opens only the tickets in the stage it needs.

## Step 4: board.py task discovery follows the ticket root
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Change only `plugins/sdlc-lite/scripts/board.py`. Depends on: step 1 (`tickets.ticket_dir`, `tickets.Fail`).
- Add `task_dirs(root)`. It returns today's candidates, the dirs directly under `root` holding a `handoff.md` (board.py:206 and 902). When `tickets.ticket_dir(root)` is not `root`, it adds the dirs directly under that ticket dir that hold a `handoff.md`. A `tickets.Fail` (an unsupported value) counts `root` only, because the board is display-only and never fails on config.
- `main` (the candidates) and `summary` use `task_dirs`, and `lanes` gets it through `summary`. Task names stay folder names, so `--task 0001-a` still matches.
- Docstring: the "A task dir is .sdlc/<task>/" line gains the `ticket_root: tickets` case.
- Selftest: append cases. Write the fixtures by hand, as the existing cases do, because the selftest must pass from a copy of `scripts/*.py` alone, with no `skills/` folder (criterion 3). Cases:
  - A ticket under `tickets/` and a plain task at the root both render.
  - `--task` finds the ticket.
  - `--summary` names the ticket.

  Negative controls: with no config line, a `tickets/<dir>` folder is not a task; with an unsupported value, root tasks are still listed.
- Focused check: `python3 plugins/sdlc-lite/scripts/board.py selftest`.
### Acceptance criteria
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc/tickets/0001-a" "$t/.sdlc/side" && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && printf -- '---\nid: T-0001\ntitle: "A"\ntype: feature\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-30\n---\n\n## Goal\nx\n' > "$t/.sdlc/tickets/0001-a/handoff.md" && printf '## Step 1: x\nlevel: L1\n' > "$t/.sdlc/tickets/0001-a/planner-L1.md" && printf '## Goal\ny\n' > "$t/.sdlc/side/handoff.md" && printf '## Step 1: y\nlevel: L1\n' > "$t/.sdlc/side/planner-L1.md" && out=$(SDLC_BOARD_STATE_DIR="$t/state" python3 plugins/sdlc-lite/scripts/board.py --root "$t/.sdlc") && printf '%s\n' "$out" | grep -qF '| T-0001 | 0001-a | ready |' && printf '%s\n' "$out" | grep -qF '| side |' && SDLC_BOARD_STATE_DIR="$t/state" python3 plugins/sdlc-lite/scripts/board.py --root "$t/.sdlc" --task 0001-a | grep -qF '0001-a'`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc/tickets/0001-a" && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && printf -- '---\nid: T-0001\ntitle: "A"\ntype: feature\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-30\n---\n' > "$t/.sdlc/tickets/0001-a/handoff.md" && printf '## Step 1: x\nlevel: L1\n' > "$t/.sdlc/tickets/0001-a/planner-L1.md" && test "$(SDLC_BOARD_STATE_DIR="$t/state" python3 plugins/sdlc-lite/scripts/board.py --root "$t/.sdlc" --summary)" = '0001-a 0% (0/1)'`
- `t=$(mktemp -d) && for c in a b; do mkdir -p "$t/$c/scripts" && cp plugins/sdlc-lite/scripts/*.py "$t/$c/scripts/" || exit 1; done && python3 -c "import sys; p = sys.argv[1]; s = open(p).read(); k = 'def ticket_dir(root):\n'; assert s.count(k) == 1, s.count(k); open(p, 'w').write(s.replace(k, k + '    return root\n'))" "$t/b/scripts/tickets.py" && python3 "$t/a/scripts/board.py" selftest >/dev/null 2>&1 && ! python3 "$t/b/scripts/board.py" selftest >/dev/null 2>&1`
- (guard) `t=$(mktemp -d) && mkdir -p "$t/.sdlc/tickets/0001-a" && printf -- '---\nid: T-0001\ntitle: "A"\ntype: feature\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-30\n---\n' > "$t/.sdlc/tickets/0001-a/handoff.md" && printf '## Step 1: x\nlevel: L1\n' > "$t/.sdlc/tickets/0001-a/planner-L1.md" && ! SDLC_BOARD_STATE_DIR="$t/state" python3 plugins/sdlc-lite/scripts/board.py --root "$t/.sdlc" | grep -qF '0001-a'`
- (guard) `t=$(mktemp -d) && mkdir -p "$t/.sdlc/0001-a" && printf 'ticket_root: work\n' > "$t/.sdlc/config" && printf -- '---\nid: T-0001\ntitle: "A"\ntype: feature\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-30\n---\n' > "$t/.sdlc/0001-a/handoff.md" && printf '## Step 1: x\nlevel: L1\n' > "$t/.sdlc/0001-a/planner-L1.md" && SDLC_BOARD_STATE_DIR="$t/state" python3 plugins/sdlc-lite/scripts/board.py --root "$t/.sdlc" | grep -qF '| T-0001 | 0001-a |'`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/tickets.py|plugins/sdlc-lite/scripts/board.py" | { ! grep -q .; }`
