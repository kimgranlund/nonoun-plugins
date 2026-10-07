## Task goal
Make fanout.py resolve lane ticket paths through tickets.ticket_dir so it supports `ticket_root`.

## Step 1: Route fanout lane ticket paths through tickets.ticket_dir, selftest it, and run the gates
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: none. This is a one-step plan, so it is also the gates green step.

Implementation targets are in `plugins/sdlc-lite/scripts/fanout.py`. Line numbers are at HEAD 07ed688 and will drift, so find each one by its symbol.

1. Preflight (`preflight`, near `ts = tickets.load(root)`, line ~283):
   - Set `tdir = tickets.ticket_dir(root)` and `ts = tickets.load(tdir)`.
   - Add `except tickets.Fail as e: raise Refuse(str(e))` beside the existing `(OSError, UnicodeDecodeError)` handler. `ticket_dir` raises `Fail` on an unsupported value, per tickets.py:300-322.
   - Set `trel = tdir.relative_to(top)`.
   - The regular-lane miss message becomes `no ticket under {tdir} has this id`.
   - External lanes keep `tickets.branch_tickets(root, ext)` unchanged, because that function already resolves `ticket_root` per branch (tickets.py:389-393).
2. In the handoff-at-start check (line ~409, `relp = rel.as_posix()` before `missing`), use `trel` for the committed-handoff path.
3. Add `'trel': trel` to the returned ctx dict.
4. Replace `ctx['rel']`/`rel` with `ctx['trel']` everywhere a path names a ticket folder:
   - `driver_for` (`default_driver((ctx['rel'] / t.slug / 'handoff.md'))`)
   - the `missing` check in `setup` (`lane.dir / ctx['rel'] / t.slug / 'handoff.md'`, twice)
   - `run_ticket`'s `FANOUT_HANDOFF` and `inherited_red(wt / rel / t.slug)`
   - `merge_gate_close`'s `src, dst` copy paths and its `git clean -fdq -- (rel / t.slug)` path
5. Keep these unchanged:
   - The close command `tickets.py --root rel close <slug>`, because tickets.py resolves `ticket_dir` itself.
   - The `close <id>` commit's `git add -A -- relp`. It covers `<root>/tickets/` and the router files close writes.
   - `FANOUT_ROOT=str(wt / rel)`. It stays the lane root that holds `config`, as the docstring says ("FANOUT_ROOT (absolute lane root)"). The ticket folder is `dirname "$FANOUT_HANDOFF"`. The existing selftest STUBs keep `$FANOUT_ROOT/$FANOUT_SLUG` because their fixtures are flat. These are contract dependents, deliberately left as they are.
6. In `print_plan`, only when `trel != rel`, add a line `ticket folders in each worktree: <trel posix>` right after the `ticket root in each worktree:` line. Flat dry-run output stays byte-identical, which the handoff requires ("Flat layout behavior unchanged").
7. In the module docstring:
   - In the preflight text, change "resolves through tickets.load(root)" to "resolves through tickets.load(tickets.ticket_dir(root))".
   - Note that handoff, step, and filer paths in each worktree use that ticket dir, with `<root>/tickets` under `ticket_root: tickets`.
   - In the driver env text, say that FANOUT_HANDOFF sits in the ticket folder.

Selftest: in `selftest()`, add a case whose `expect` labels all start with `ticket_root lane`. The fixture is a repo with `.sdlc/config` = `ticket_root: tickets` and `.sdlc/tickets/x/handoff.md` (T-0001, ready), committed. It runs with `--lanes-dir` outside the repo and a stub driver that writes `filer-L1.md` into `$(dirname "$FANOUT_HANDOFF")` and one file at the worktree top. The case asserts:
- The dry run exits 0 and prints `ticket folders in each worktree: .sdlc/tickets`.
- The run exits 0 with outcome `merged`.
- `fanout/<integration>:.sdlc/tickets/x/handoff.md` says `status: done`.
- The integration tip subject is `close T-0001`.
- No folder `.sdlc/x` exists on the integration branch.

The negative control is the same fixture against the base fanout.py, which refuses with `no ticket under ... has this id`. I observed this at plan time, and criterion 2 below re-runs it against `$SDLC_BASE_SHA`.

Guidance: in `docs/references/sdlc-internals.md` line ~51, replace the last sentences of the fanout paragraph, "Regular lanes do not follow `ticket_root` yet. With the line set, preflight finds no ticket under `<root>` for their ids and refuses. This is a follow-up.", with a sentence starting "Regular lanes follow `ticket_root`". It says that ids resolve through `tickets.ticket_dir(<root>)` and that handoff, step-dir, and filer paths in each worktree use that dir. It also says `FANOUT_ROOT` stays `<root>` and the dry run adds a `ticket folders in each worktree:` line when the dir differs.

Deliberately left untouched:
- `.sdlc/notes.md` (dated history of the T-0175 close)
- `docs/lean-sdlc/design.md:167` (a design record, not current-behavior guidance)

Focused checks: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` and the fixture criterion. Then run every gate below and fix any red this step introduced.
### Acceptance criteria
- `F=${F:-$PWD/plugins/sdlc-lite/scripts/fanout.py}; t=$(mktemp -d) && r=$t/repo && mkdir -p $r/.sdlc/tickets/x && printf 'ticket_root: tickets\n' > $r/.sdlc/config && printf -- '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n' > $r/.sdlc/tickets/x/handoff.md && git -C $r init -q -b main && git -C $r config user.name t && git -C $r config user.email t@e.invalid && git -C $r config commit.gpgsign false && git -C $r add -A && git -C $r commit -qm f && (cd $r && python3 "$F" run a=T-0001 --integration fanout/t --lanes-dir $t/lanes --driver 'printf "## Warnings\nNone\n\n## Follow-ups\nNone\n" > "$(dirname "$FANOUT_HANDOFF")/filer-L1.md"; echo x > x.txt') && git -C $r show fanout/t:.sdlc/tickets/x/handoff.md | grep -q "^status: done" && test "$(git -C $r log -1 --format=%s fanout/t)" = "close T-0001"`
- Negative control: the criterion above, run with `F` set to the fanout.py in a `git archive "$SDLC_BASE_SHA" plugins/sdlc-lite/scripts` copy extracted into a temp dir, exits nonzero and its output contains `no ticket under`.
- `grep -qF "tickets.load(tickets.ticket_dir(root))" plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF "ticket_root lane" plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF "Regular lanes follow" docs/references/sdlc-internals.md`
- `! grep -qF "Regular lanes do not follow" docs/references/sdlc-internals.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/fanout.py -e docs/references/sdlc-internals.md)"`
- `test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/fanout.py docs/references/sdlc-internals.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
