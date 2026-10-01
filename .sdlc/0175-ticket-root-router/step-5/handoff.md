## Task goal
`tickets.py` can use a `tickets/` ticket root under `.sdlc/` when `<root>/config` says `ticket_root: tickets`, and `tickets.py roadmap` keeps a managed router block in `.sdlc/AGENTS.md` current, so an agent reads one short file and opens only the tickets in the stage it needs.

## Step 5: traces ingest and ticket reader follow the ticket root
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Change `plugins/sdlc-lite/scripts/traces/ingest.py`, `plugins/sdlc-lite/scripts/traces/sources/tickets.py`, and `plugins/sdlc-lite/scripts/traces/selftest.py`. Depends on: step 1. This is the small fix the handoff allows for another script that lists task folders under `.sdlc`.
- `ingest.task_dirs(sdlc)`: when `tickets.ticket_dir(pathlib.Path(sdlc))` is not that root, leave the name `tickets` out of the root listing. Add one `tickets/<name>` entry per dir under the ticket dir, by the same name filter, after the root names, each part sorted. A `tickets.Fail` lists the root only. `run()` already joins names with `os.path.join` (ingest.py:175-176), so `task_rel` becomes `.sdlc/tickets/<name>` and `table.dir_parts` keeps working, since it splits on the last `/`.
- `sources/tickets.read(root)`: set `ts = tickets.load(<ticket dir>)`, where the ticket dir is `tickets.ticket_dir(Path(root))`, falling back to `root` on `tickets.Fail`. `problems`, `external`, and `notes` keep reading `root`, because config and notes.md stay there.
- Docstrings: ingest's "handoff dirs" paragraph and the reader's `by_slug` line.
- Selftest: append cases named `tickets: ...`, so that `traces.py selftest -k tickets` runs them, with fixtures written by `_write`. Cases:
  - `task_dirs` lists `tickets/<name>` and the root tasks, and not `tickets`.
  - The reader's `by_slug` comes from `tickets/`.

  Negative control: with no config line, a `tickets` dir is a plain task dir name.
- Contract dependent: the corpus case (selftest.py around line 1896) walks this repo's `.sdlc`, which has no `ticket_root` line, so it is unchanged.
- Focused checks: `python3 plugins/sdlc-lite/scripts/traces.py selftest -k tickets`, then the full `traces.py selftest`.
### Acceptance criteria
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc/tickets/0001-a" "$t/.sdlc/side" && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && printf -- '---\nid: T-0001\ntitle: "A"\ntype: feature\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-30\n---\n' > "$t/.sdlc/tickets/0001-a/handoff.md" && printf '## Goal\nx\n' > "$t/.sdlc/side/handoff.md" && cd plugins/sdlc-lite/scripts && python3 -c "import sys; from traces import ingest; from traces.sources import tickets as tr; n = ingest.task_dirs(sys.argv[1]); assert 'tickets/0001-a' in n and 'side' in n and 'tickets' not in n, n; r = tr.read(sys.argv[1]); assert r['by_slug'] == {'0001-a': ('T-0001', 'ready')}, r" "$t/.sdlc"`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite/scripts "$t/a" && cp -R plugins/sdlc-lite/scripts "$t/b" && python3 -c "import sys; p = sys.argv[1]; s = open(p).read(); k = 'def ticket_dir(root):\n'; assert s.count(k) == 1, s.count(k); open(p, 'w').write(s.replace(k, k + '    return root\n'))" "$t/b/tickets.py" && python3 "$t/a/traces.py" selftest -k tickets >/dev/null 2>&1 && ! python3 "$t/b/traces.py" selftest -k tickets >/dev/null 2>&1`
- (guard) `t=$(mktemp -d) && mkdir -p "$t/.sdlc/0001-a" "$t/.sdlc/_templates" "$t/.sdlc/tickets" && cd plugins/sdlc-lite/scripts && python3 -c "import sys; from traces import ingest; n = ingest.task_dirs(sys.argv[1]); assert n == ['0001-a', 'tickets'], n" "$t/.sdlc"`
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/tickets.py|plugins/sdlc-lite/scripts/board.py|plugins/sdlc-lite/scripts/traces/ingest.py|plugins/sdlc-lite/scripts/traces/sources/tickets.py|plugins/sdlc-lite/scripts/traces/selftest.py" | { ! grep -q .; }`
