## Task goal
Add the `layout` config key and one resolver for ticket dir, roadmap path, and notes path, plus stray checks and onboard variants.

## Step 1: tickets.py layout line, resolver, router variants, and stray check
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
All edits are in `plugins/sdlc-lite/scripts/tickets.py`. Line numbers are at HEAD 264be0cb and drift, so re-read them before editing.

1. Config line and resolver. Add `LAYOUT_RE = re.compile(r'\s*layout\s*:\s*(\S+)\s*(?:#.*)?')` beside `TICKET_ROOT_RE` (line 209). Near `ticket_dir` (line 308), add `LayoutPaths = collections.namedtuple('LayoutPaths', 'layout tickets roadmap notes work')` and `def layout_paths(root)`. Blank lines, `#` comment lines, and a missing config file follow `ticket_dir`'s rules.
   - No `layout:` line, or only `layout: flat` lines, gives `('flat', ticket_dir(root), root/'roadmap.md', root/'notes.md', root)`.
   - `layout: topics` gives `('topics', root/'tickets', root/'tickets'/'roadmap.md', root/'notes'/'notes.md', root/'work')`.
   - A value other than `flat` or `topics`, or both values in one file, raises `Fail` naming the config path and the offending line, ending `nothing written`, the way `ticket_dir` refuses an unsupported `ticket_root` (line 327).
   - `layout: topics` without a `ticket_root: tickets` line raises `Fail` that names `ticket_root: tickets`. The reason is design.md:165: other worktrees, external branches, board.py, and traces resolve the ticket root from `ticket_root` alone, so a tree that wrote only `layout: topics` would look flat to all of them.
   - `layout_paths` calls `ticket_dir`, never the reverse. `ticket_dir` keeps its signature and its return value for every config. It also resolves other trees (`worktree_pairs` and branch reading, lines 375-428), where a bad `layout` line in one tree must not break another tree's resolution. Its importers (board.py:61, budget.py:29, fanout.py:252, steps.py:1708, solo_run.py:174, traces/ingest.py:33, traces/sources/tickets.py:14, traces/detectors/hygiene.py:45) stay unchanged; their readers move in T-0207.
2. Callers. These change:
   - `render` (about line 914): the roadmap link prefix is `''` when `tickets == roadmap.parent` and `tickets/` otherwise, so under topics the links read `<slug>/handoff.md`.
   - `write_roadmap` (926) and `stale` (935) use `layout_paths(root).roadmap`; `write_roadmap` creates the folder first.
   - `append_notes` (1315) writes `layout_paths(root).notes` and creates its folder.
   - The three `outside_refs(..., roadmap=root / 'roadmap.md')` calls (1396, 1640, 1688) pass `layout_paths(root).roadmap`.
   - `cmd_check` keeps its `roadmap.md: stale or missing` message.
3. Router text. In a flat tree (no `layout` line or `layout: flat`, with or without `ticket_root: tickets`), every managed file's output stays byte-identical. The reason is that `onboard.TEMPLATE_VERSION` is shared with these blocks and must not be bumped (onboard.py:1528-1529). A topics tree changes as follows:
   - The root `AGENTS.md` block: the first paragraph of `ROUTER_TEMPLATE` (line 978) becomes the topics paragraph below, and the ticket folders line is `ROUTER_TICKETS`, as for `ticket_root: tickets`.
   - In the procedures, as rendered for both the root and `tickets/AGENTS.md`, the substring ``go to `notes.md` `` becomes ``go to `<R>/notes/notes.md` `` before `<R>` is substituted.
   - `router_files` adds `work/AGENTS.md`, `work/CLAUDE.md`, `notes/AGENTS.md`, and `notes/CLAUDE.md` (kinds `agents` and `claude`), and `router_bodies` returns the two blocks below. `write_router` writes them and `router_problems` reports a missing or stale one the way it reports `tickets/AGENTS.md` (lines 1017-1024 hold the nested pattern to follow).

   ```text
   Topics root paragraph (replaces the first paragraph of ROUTER_TEMPLATE):
   This folder holds SDLC Lite records in topic folders: `tickets/` (ticket folders and `tickets/roadmap.md`), `work/` (task folders with no ticket), `notes/` (`notes/notes.md`), and `messages/`, beside `config` and `_templates/`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `tickets/roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

   work/AGENTS.md block:
   # Work

   One folder per task with no ticket: release records, verification handoffs, dogfood runs. Ticket folders are in `../tickets/`. `tickets.py roadmap` generates this block: do not edit inside it.

   notes/AGENTS.md block:
   # Notes

   `notes.md` holds the follow-ups `tickets.py close` appends: `note:` items and the `decide:` items not filed as tickets. It names no folder paths. `tickets.py roadmap` generates this block: do not edit inside it.
   ```
4. Strays. `strays(root)` (line 332) stays as is, so `roadmap` and `check` still refuse a ticket folder outside the ticket root. Add `root_strays(root)` and call it only from `cmd_check`, never from `cmd_roadmap`, so a loose file never blocks `new` or `close`. Under topics it returns one line per entry directly under `<root>` that is not allowed, skipping names `strays` already reports, in this form: `<name>: stray entry at the root; <root>/config sets layout: topics, so move it into tickets/, work/, or notes/`. Under flat it returns `[]`. The allowed entries are:
   - `AGENTS.md`, `CLAUDE.md`, `config`, `layout.md`, `board.md`, `tickets`, `work`, `notes`, `messages`, `evals`, `proposals`, `supervisor`, `runtime`, and `dogfood`;
   - every `_`-prefixed entry;
   - every `.`-prefixed entry except a closed-ticket folder matching `DOT_RE`, which is a stray because it belongs in `tickets/`.

   Evidence: design.md:141-155 (target layout); docs/planning/docs-schema/design.md:194 (`.sdlc/layout.md`) and :334 with docs_check.py:45-46, where `board.md` is a known loose record, so flagging it would fail `check` in every topics repo that has one.
5. Flat warning. When `layout_paths(root).layout` is `flat` and `<root>/config` has no explicit `layout: flat` line, `cmd_check` appends this line after the `ok:` line and the existing warnings: `warning: <root> uses the flat layout; tickets.py migrate-layout moves it to topic folders (add 'layout: flat' to <root>/config to keep it and silence this)`. The exit code stays 0 and the `ok:` line stays first. An explicit `layout: flat` line is the opt-out: migration is opt-in (design.md resolved decision 5), so a repo that chose flat should not be warned forever.
6. Selftest (`selftest()`, line 1732). Add cases on topics fixtures (config `ticket_root: tickets` plus `layout: topics`):
   - `new` writes `tickets/roadmap.md` with `<slug>/handoff.md` links and the `work/` and `notes/` entry files, and `check` passes.
   - `close` with a `note:` follow-up appends to `notes/notes.md`.
   - The close and archive reference scans skip `tickets/roadmap.md`.
   - Negative controls: a stray dir, a root `notes.md`, and a root `.NNNN-x` folder each fail `check` naming the entry; `layout: topics` without `ticket_root` and `layout: nested` each fail; a stale `work/AGENTS.md` fails `check`.
   - A flat fixture's `check` names `migrate-layout`, and one with `layout: flat` does not.

   Update the exact-output asserts near lines 1767, 2015, and 3743 (`out == 'ok: N tickets, roadmap current'`) to the new flat output. They are the only parsers of `check` stdout: `git grep "roadmap current"` finds no reader outside tickets.py.
7. Guidance. Update the module usage docstring (lines 3-140: `--root`, `config`, `roadmap`, `check`, and "the only writer of .sdlc/roadmap.md") and the `ticket_dir` docstring (line 312) to describe the `layout` line and `layout_paths`.

These are left untouched on purpose:
- `messages.py`: its `ENTRY_TEMPLATE` (messages.py:207-212) names only `.sdlc/messages/`, which does not move (design.md:150), and `write_roadmap` keeps calling `messages.write_entries` on `<root>/messages`.
- `check.py`: the /fix lint-target guard (check.py:403-409) tests only the `/step-1/handoff.md` suffix, so a `tickets/` path already passes; `FINISH_DOCS` (check.py:252) needs the literal `notes.md` in tickets.py, which stays.
- `board.py`, `statusline.sh`, `traces/sources/tickets.py:28`, and docs_check.py B-2a: they belong to T-0207, and their flat behavior is unchanged.
- `onboard.py`: step 2.

Depends on: none. Focused checks: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` (about 31 s) and the fixture criteria below. Each fixture keeps its output files outside the ticket root, so they are never counted as strays.
### Acceptance criteria
- `python3 -c 'import sys,pathlib,tempfile; sys.path.insert(0,"plugins/sdlc-lite/scripts"); import tickets as t; d=pathlib.Path(tempfile.mkdtemp()); a=tuple(t.layout_paths(d)); (d/"config").write_text("ticket_root: tickets\nlayout: topics\n"); b=tuple(t.layout_paths(d)); sys.exit(0 if a==("flat",d,d/"roadmap.md",d/"notes.md",d) and b==("topics",d/"tickets",d/"tickets/roadmap.md",d/"notes/notes.md",d/"work") else 1)'`
- `d=$(mktemp -d) && mkdir "$d/a" "$d/b" && printf 'layout: topics\n' > "$d/a/config" && printf 'ticket_root: tickets\nlayout: nested\n' > "$d/b/config" && ! python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/a" check 2>"$d/ea" >/dev/null && grep -qF 'ticket_root: tickets' "$d/ea" && ! python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/b" check 2>"$d/eb" >/dev/null && grep -qF 'layout: nested' "$d/eb"`
- `d=$(mktemp -d) && r="$d/r" && mkdir "$r" && printf 'ticket_root: tickets\nlayout: topics\n' > "$r/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$r" new chore demo "Demo" >/dev/null && mkdir "$r/_templates" && touch "$r/.DS_Store" && test -f "$r/tickets/roadmap.md" && test ! -e "$r/roadmap.md" && grep -qF '](demo/handoff.md)' "$r/tickets/roadmap.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$r" check > "$d/out" && ! grep -qF migrate-layout "$d/out"`
- `d=$(mktemp -d) && r="$d/r" && mkdir "$r" && printf 'ticket_root: tickets\nlayout: topics\n' > "$r/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$r" new chore demo "Demo" >/dev/null && grep -qF 'tickets/roadmap.md' "$r/AGENTS.md" && grep -qF 'notes/notes.md' "$r/AGENTS.md" && for f in work/AGENTS.md work/CLAUDE.md notes/AGENTS.md notes/CLAUDE.md; do test -f "$r/$f" || exit 1; done`
- `d=$(mktemp -d) && r="$d/r" && mkdir "$r" && printf 'ticket_root: tickets\nlayout: topics\n' > "$r/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$r" new chore demo "Demo" >/dev/null && mkdir "$r/junk" && printf 'x\n' > "$r/notes.md" && ! python3 plugins/sdlc-lite/scripts/tickets.py --root "$r" check 2>"$d/err" >/dev/null && grep -qF junk "$d/err" && grep -qF notes.md "$d/err"`
- `python3 -c 'import sys,pathlib,tempfile; sys.path.insert(0,"plugins/sdlc-lite/scripts"); import tickets as t; d=pathlib.Path(tempfile.mkdtemp()); (d/"config").write_text("ticket_root: tickets\nlayout: topics\n"); t.append_notes(d,"T-0001","Demo",[("note","n")]); sys.exit(0 if (d/"notes/notes.md").is_file() and not (d/"notes.md").exists() else 1)'`
- `d=$(mktemp -d) && r="$d/r" && mkdir "$r" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$r" new chore demo "Demo" >/dev/null && python3 plugins/sdlc-lite/scripts/tickets.py --root "$r" check > "$d/out" && grep -qF migrate-layout "$d/out" && printf 'layout: flat\n' >> "$r/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$r" check > "$d/out2" && ! grep -qF migrate-layout "$d/out2"`
- `! grep -nF "roadmap=root / 'roadmap.md'" plugins/sdlc-lite/scripts/tickets.py`
- `sed -n '/^def selftest/,$p' plugins/sdlc-lite/scripts/tickets.py | grep -qF 'layout: topics'`
- (guard) `d=$(mktemp -d) && git archive "$SDLC_BASE_SHA" plugins/sdlc-lite | tar -x -C "$d" && for c in flat nested; do mkdir "$d/$c" && if [ $c = nested ]; then printf 'ticket_root: tickets\n' > "$d/$c/config"; fi && python3 "$d/plugins/sdlc-lite/scripts/tickets.py" --root "$d/$c" new chore demo Demo >/dev/null && python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/$c" check >/dev/null || exit 1; done`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF plugins/sdlc-lite/scripts/tickets.py)"`
