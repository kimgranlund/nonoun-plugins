<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Add support for a `layout: topics|flat` line in `.sdlc/config` and one `tickets.py` resolver for the ticket dir, roadmap, notes, and work paths, and route every roadmap and notes caller, the router text, `check`'s stray rule and flat warning, and onboard's managed block through it, with every flat repo's generated text byte-identical.

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

   Evidence: design.md:141-155 (target layout); docs/docs-schema/design.md:194 (`.sdlc/layout.md`) and :334 with docs_check.py:45-46, where `board.md` is a known loose record, so flagging it would fail `check` in every topics repo that has one.
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

## Step 2: onboard topics variant, then gates green
level: L2
guard timeout: 1300
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Edits in `plugins/sdlc-lite/scripts/onboard.py` (line numbers at HEAD 264be0cb):

1. `Model` (line 478) gains a trailing field `roadmap` whose default is `'.sdlc/roadmap.md'`. Extend the namedtuple `defaults` so every existing `Model(...)` call and selftest fixture keeps working.
2. `build_model` (lines 622-648) sets `roadmap` to `tickets.layout_paths(pathlib.Path(root, '.sdlc')).roadmap` made relative to `root`, in posix form: `.sdlc/roadmap.md` for a flat repo, `.sdlc/tickets/roadmap.md` for topics.
   - `tickets` is imported locally inside the helper body, as tickets.py:929 does for `messages`. tickets.py imports onboard at module level (tickets.py:189), so a top-level import back would be circular.
   - A `tickets.Fail` from a bad `.sdlc/config` is re-raised as `SetupError(str(e))`. `_plan_or_report` (lines 931-938) then prints `onboard.py: <reason>` to stderr, and `setup` and `check` exit 1 with nothing written.
3. `render_templates` (line 530) replaces the literal `.sdlc/roadmap.md` in the root block with `model.roadmap`. For a flat repo the replacement is the identity, so the block text, its digest, and `TEMPLATE_VERSION = 1` (line 307) stay unchanged and every existing block stays `current`. A bump would mark every block stale (design.md:169).
4. Selftest. Add gate `layout-variant` to `GATES` (line 1563), after `lane-text`.
   - Positive, flat: in a `_fixture` with no `.sdlc`, `run_setup` writes a root block whose text equals the unsubstituted template block (`_split_template(ROOT_AGENTS_TEMPLATE).block` with `<N>` set to the version), and `run_check` labels `AGENTS.md` current.
   - Positive, topics: in a fixture whose `.sdlc/config` holds `ticket_root: tickets` and `layout: topics`, the written block names `.sdlc/tickets/roadmap.md` and not `.sdlc/roadmap.md`, its version is `TEMPLATE_VERSION`, and `run_check` labels it current.
   - Negative variants, each of which must be rejected: `('renders the topics text for a flat repo', REAL._replace(render=_render_topics_always))` and `('renders the flat text for a topics repo', REAL._replace(render=_render_flat_always))`.
   - The existing `_selftest` loop prints `gate layout-variant: positive ok, negative ok`.
5. The module docstring says that the root block names the resolved roadmap path. Its "Standard library only" sentence (line 8) also says that the layout is read through a function-local import of the sibling `tickets.py`.

Then run every gate below and fix any red that step 1 or this step introduced, inside the four owning files (`tickets.py`, `onboard.py`, `check.py`, `messages.py`). `check.sh` runs the selftests of every script that imports `tickets` (board, budget, fanout, steps, solo_run, traces), so an exact-output dependent that the grep missed shows up here. A gate already red at the build-start HEAD comes back as Status `inherited red`. At plan time all four were green: `check.sh` rc 0 in 431 s, `check-packaging.py`, `codex_roles.py generate --check`, and `tickets.py --root .sdlc check` rc 0. `onboard.py check` is rc 1 on this repo before any change (missing `docs/layout.md` and topic entries), so it is not a gate.

Depends on: step 1.
### Acceptance criteria
- `d=$(mktemp -d) && s="$PWD/plugins/sdlc-lite/scripts/onboard.py" && git -C "$d" init -q && mkdir "$d/.sdlc" && printf 'ticket_root: tickets\nlayout: topics\n' > "$d/.sdlc/config" && (cd "$d" && python3 "$s" setup >/dev/null 2>&1) && grep -qF '.sdlc/tickets/roadmap.md' "$d/AGENTS.md" && ! grep -qF '.sdlc/roadmap.md' "$d/AGENTS.md" && (cd "$d" && python3 "$s" check 2>/dev/null) | grep -qx 'current AGENTS.md'`
- `d=$(mktemp -d) && e=$(mktemp -d) && s="$PWD/plugins/sdlc-lite/scripts/onboard.py" && git -C "$d" init -q && mkdir "$d/.sdlc" && printf 'ticket_root: tickets\nlayout: nested\n' > "$d/.sdlc/config" && (cd "$d" && ! python3 "$s" setup 2>"$e/err" >/dev/null) && grep -qF 'layout: nested' "$e/err" && test ! -e "$d/AGENTS.md"`
- `python3 plugins/sdlc-lite/scripts/onboard.py selftest | grep -qx 'gate layout-variant: positive ok, negative ok'`
- (guard) `d=$(mktemp -d) && s="$PWD/plugins/sdlc-lite/scripts/onboard.py" && git archive "$SDLC_BASE_SHA" plugins/sdlc-lite/scripts/onboard.py | tar -x -C "$d" && for c in none nested; do r="$d/$c" && mkdir "$r" && git -C "$r" init -q && if [ $c = nested ]; then mkdir "$r/.sdlc" && printf 'ticket_root: tickets\n' > "$r/.sdlc/config"; fi && (cd "$r" && python3 "$d/plugins/sdlc-lite/scripts/onboard.py" setup >/dev/null 2>&1) && (cd "$r" && python3 "$s" check 2>/dev/null) | grep -qx 'current AGENTS.md' || exit 1; done`
- (guard) `grep -qx 'TEMPLATE_VERSION = 1' plugins/sdlc-lite/scripts/onboard.py`
- (guard) `python3 plugins/sdlc-lite/scripts/onboard.py selftest`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxE 'plugins/sdlc-lite/scripts/(tickets|onboard|check|messages)\.py')"`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`

## Assumptions
- T-0204 (the fanout resolver this ticket depends on) is closed: verified by `ls -d .sdlc/.0204-fanout-resolver`.
- Cited line numbers hold at HEAD 264be0cb: verified by reading tickets.py:200-345, 505-560, 900-1135, 1312-1324, 1585-1625, 1708-1730 and onboard.py:300-350, 478, 525-600, 618-690, 931-985, 1524-1660.
- The router text and the onboard block are the only generated texts that name the root `roadmap.md` or `notes.md`. The `messages/AGENTS.md` text does not: verified by `grep -n "roadmap\|notes\.md" plugins/sdlc-lite/scripts/messages.py` (docstring mentions only) and messages.py:207-212.
- `tickets.py check` stdout is parsed exactly only in tickets.py's own selftest: verified by `git grep -nF "roadmap current" -- plugins scripts` (tickets.py:1613, 1767, 2015, 3615, 3743).
- `onboard` is imported only by tickets.py and docs_check.py, and neither uses `Model`, `build_model`, or `render_templates`: verified by `git grep` over plugins and scripts.
- The cross-version guards are green at base and go red on a changed block: verified by running them at plan time. A base-created flat fixture and a `ticket_root: tickets` fixture both check clean under the current tickets.py and onboard.py. The same fixture with one word edited in the router or onboard block fails (`AGENTS.md: router block stale`, `edited AGENTS.md`).
- "New repos get `layout: topics`" (handoff Constraints, design.md:169) is not part of this ticket's build: verified by the handoff's Do, whose onboard item covers rendering only, and design.md:242 (row L13: "`onboard.py` variants without a bump for flat repos"). Nothing here writes `.sdlc/config` for a new repo, and `tickets.py new` on a missing root stays flat, which many selftest fixtures rely on. T-0206's Do covers only migrating an existing tree, so the default flip needs its own follow-up, recorded by the filer as `decide:`.
- `check.sh` takes about 431 s on this host: verified by timing it once at plan time (rc 0). The `guard timeout: 1300` on step 2 gives about three times that.

## Risks
- Until T-0206 lands, the flat warning names `tickets.py migrate-layout`, a command that does not exist yet. T-0206 depends on this ticket and is planned as the next unit.
- In a migrated repo, docs_check.py B-2a will warn on `.sdlc/work/` and `.sdlc/notes/` (`SDLC_RECORD_DIRS`, docs_check.py:45). board.py, statusline.sh, and traces/sources/tickets.py:28 still read the root `roadmap.md` and `notes.md`. No repo is on topics until T-0206, and T-0207 owns these readers, so nothing breaks now.
- `check.sh` may run slower under host load than the 431 s measured. It can also surface an exact-output dependent in a file outside the step 2 allow-list; that comes back as a scope decision rather than a fix.
- tickets.py is also written by T-0206 and T-0207; per the handoff, they must never run in parallel lanes with this ticket.
