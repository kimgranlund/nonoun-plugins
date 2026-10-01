<!-- role=planner level=L3 model=opus effort=xhigh -->
The plan is ready: 8 steps, linted clean by `steps.py lint`, every criterion probed on the current tree. Here is the final plan.

## Goal
`tickets.py` honors an opt-in `ticket_root: tickets` line in `<root>/config` (ticket folders under `<root>/tickets/`, everything else unchanged without the line), and every roadmap regeneration keeps a tested, `check`-enforced router block in `<root>/AGENTS.md` (plus `tickets/AGENTS.md`) that lists stages and carries the create, claim, and close procedures, with board and traces discovery following the same root, docs updated, and a dated live run recorded.

## Step 1: Ticket root resolution for local tickets.py commands
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Change only `plugins/sdlc-lite/scripts/tickets.py`. Depends on: none.
- Add `TICKET_ROOT_RE = re.compile(r'\s*ticket_root\s*:\s*(\S+)\s*(?:#.*)?')` and `ticket_dir(root)`. It reads `<root>/config` the way `config_numbered` and `external_branches` do (tickets.py:215-254: blank and `#` lines ignored, a missing file is no line). No `ticket_root:` line returns `root`. Lines that all name `tickets` return `root / 'tickets'`. Any other value raises `Fail` with a message holding the literal `ticket_root: tickets`, for example `<root>/config: ticket_root: <value> is not supported; the only supported value is ticket_root: tickets; nothing written`. Evidence: the handoff says this build supports the value `tickets`.
- Add `strays(root)`. It returns [] when `ticket_dir(root) == root`. Otherwise it returns one line per dir directly under `root`, other than `tickets`, that `load()`'s folder rule would take (not `_` or `.` prefixed unless `DOT_RE`) and whose `handoff.md` has front matter: `<name>: ticket folder outside the ticket root; <root>/config sets ticket_root: tickets, so move it to tickets/<name>`. A handoff with no front matter (a plain task) is never a stray.
- `load(root)` keeps its signature and meaning: it lists the dir it is given. External callers (`traces/sources/tickets.py`, `fanout.py`) depend on that. Each of `cmd_new`, `cmd_close`, `cmd_roadmap`, `cmd_check`, `cmd_archive`, and `cmd_number` computes `td = ticket_dir(root)` before reading ticket folders or writing anything, so an unsupported value refuses with nothing written. Each calls `load(td)` and adds `strays(root)` to `problems(ts, numbered)` wherever it refuses on problems today.
- Ticket folders, dot folders, follow-up folders, the `stamp()` exists check, and the exists checks in `cmd_new` and `cmd_close` use `td`. `<root>/roadmap.md`, `<root>/config` (`config_numbered`, `ensure_numbered_config`, `external_branches`), `<root>/notes.md` (`append_notes`), and `<root>/_templates` (`template`, `template_types`) keep `root`.
- `render(ts, root)`: the row link becomes `[<slug>](<prefix><slug>/handoff.md)`. The prefix is `''` when `ticket_dir(root) == root`, else `tickets/`. Default-layout output stays byte-identical (the render guard below).
- `outside_refs(root, slug, own=False)` gains a keyword `roadmap=None`: the roadmap path to leave out, which defaults to `root / 'roadmap.md'` (today's rule). close, archive, and number pass the ticket dir as the first argument, so `<rel>` becomes `.sdlc/tickets` and the scan, rewrite, and messages name `.sdlc/tickets/<slug>`. They also pass `roadmap=root / 'roadmap.md'`, because the roadmap link `tickets/<slug>/handoff.md` resolves to the folder and would otherwise count as a cite.
- In this step, `id_floor`, the no-filer hint, and the `close --dry-run` worktree lines keep taking the `.sdlc` root. Step 2 resolves the other trees' ticket dirs.
- Docstring: document `ticket_root: tickets` in the config section and under `--root`. Document the stray rule with the phrase `outside the ticket root`. State that roadmap.md, config, notes.md, and _templates stay at `<root>`. Update the `--root` argparse help to match.
- Selftest: append cases and change no existing case. All of these run with `ticket_root: tickets`:
  - new lands in `tickets/<slug>`, the roadmap links `tickets/<slug>/handoff.md`, and no `tickets/roadmap.md` is written.
  - Plain close works. Numbered close renames to `tickets/.NNNN-<slug>`.
  - A follow-up folder lands in `tickets/`, and notes.md is written at `<root>`.
  - In a git fixture, a cite of `.sdlc/tickets/NNNN-<slug>` refuses close, naming the citing file and never the roadmap, and `--rewrite-refs` rewrites the cite to `.sdlc/tickets/.NNNN-<slug>`.
  - archive and number work under `tickets/`.
  - An unsupported value refuses new with nothing written, and fails check.
  - A stray ticket folder at `<root>` fails check and new.

  Negative control: a root with no `ticket_root` line behaves as today: the folder is `<root>/<slug>`, there is no `tickets/` dir, and the link is `<slug>/handoff.md`.
- Focused check: `python3 plugins/sdlc-lite/scripts/tickets.py selftest`.
### Acceptance criteria
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha "Alpha" && test -f "$t/.sdlc/tickets/alpha/handoff.md" && test ! -e "$t/.sdlc/alpha" && grep -qF '| [alpha](tickets/alpha/handoff.md) |' "$t/.sdlc/roadmap.md" && test ! -e "$t/.sdlc/tickets/roadmap.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" check`
- `t=$(mktemp -d) && git -C "$t" init -q && mkdir -p "$t/.sdlc" && printf 'ticket_root: tickets\nticket_folders: numbered\n' > "$t/.sdlc/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\n- note: Keep this\n' > "$t/.sdlc/tickets/0001-alpha/filer-L1.md" && printf 'see .sdlc/tickets/0001-alpha/handoff.md\n' > "$t/spec.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" close 0001-alpha --rewrite-refs && test -d "$t/.sdlc/tickets/.0001-alpha" && test ! -e "$t/.sdlc/tickets/0001-alpha" && grep -qxF 'see .sdlc/tickets/.0001-alpha/handoff.md' "$t/spec.md" && grep -qF 'note: Keep this' "$t/.sdlc/notes.md" && test ! -e "$t/.sdlc/tickets/notes.md" && grep -qF '(tickets/.0001-alpha/handoff.md)' "$t/.sdlc/roadmap.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" check`
- `t=$(mktemp -d) && git -C "$t" init -q && mkdir -p "$t/.sdlc" && printf 'ticket_root: tickets\nticket_folders: numbered\n' > "$t/.sdlc/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > "$t/.sdlc/tickets/0001-alpha/filer-L1.md" && printf 'see .sdlc/tickets/0001-alpha/handoff.md\n' > "$t/spec.md" && ! python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" close 0001-alpha 2>"$t/err" && grep -qF spec.md "$t/err" && ! grep -qF roadmap.md "$t/err" && test -d "$t/.sdlc/tickets/0001-alpha"`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" close alpha --reason "done elsewhere" >/dev/null && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" number >/dev/null && test -d "$t/.sdlc/tickets/0001-alpha" && test ! -e "$t/.sdlc/0001-alpha" && grep -qx 'ticket_folders: numbered' "$t/.sdlc/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" archive >/dev/null && test -d "$t/.sdlc/tickets/.0001-alpha" && grep -qF '(tickets/.0001-alpha/handoff.md)' "$t/.sdlc/roadmap.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" check`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && printf 'ticket_root: work\n' > "$t/.sdlc/config" && ! python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha 2>"$t/err" && grep -qF 'ticket_root: tickets' "$t/err" && test ! -e "$t/.sdlc/alpha" && test ! -e "$t/.sdlc/work" && test ! -e "$t/.sdlc/roadmap.md" && ! python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" check 2>/dev/null`
- `t=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha >/dev/null && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && ! python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" check 2>"$t/err" && grep -qF 'alpha' "$t/err" && grep -qF 'outside the ticket root' "$t/err" && ! python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature beta 2>/dev/null && test ! -e "$t/.sdlc/tickets"`
- `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import tickets; d = tickets.__doc__; assert 'ticket_root: tickets' in d and 'outside the ticket root' in d, 'docstring'"`
- `t=$(mktemp -d) && for c in a b; do mkdir -p "$t/$c/scripts" "$t/$c/skills/ticket" && cp plugins/sdlc-lite/scripts/*.py "$t/$c/scripts/" && cp -R plugins/sdlc-lite/skills/ticket/templates "$t/$c/skills/ticket/" || exit 1; done && python3 -c "import sys; p = sys.argv[1]; s = open(p).read(); k = 'def ticket_dir(root):\n'; assert s.count(k) == 1, s.count(k); open(p, 'w').write(s.replace(k, k + '    return root\n'))" "$t/b/scripts/tickets.py" && python3 "$t/a/scripts/tickets.py" selftest >/dev/null 2>&1 && ! python3 "$t/b/scripts/tickets.py" selftest >/dev/null 2>&1`
- `t=$(mktemp -d) && for c in a b; do mkdir -p "$t/$c/scripts" "$t/$c/skills/ticket" && cp plugins/sdlc-lite/scripts/*.py "$t/$c/scripts/" && cp -R plugins/sdlc-lite/skills/ticket/templates "$t/$c/skills/ticket/" || exit 1; done && python3 -c "import sys; p = sys.argv[1]; s = open(p).read(); k = 'def strays(root):\n'; assert s.count(k) == 1, s.count(k); open(p, 'w').write(s.replace(k, k + '    return []\n'))" "$t/b/scripts/tickets.py" && python3 "$t/a/scripts/tickets.py" selftest >/dev/null 2>&1 && ! python3 "$t/b/scripts/tickets.py" selftest >/dev/null 2>&1`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `t=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && test -f "$t/.sdlc/alpha/handoff.md" && test ! -e "$t/.sdlc/tickets" && grep -qF '| [alpha](alpha/handoff.md) |' "$t/.sdlc/roadmap.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" check`
- (guard) `t=$(mktemp -d) && git show "$SDLC_BASE_SHA":plugins/sdlc-lite/scripts/tickets.py > "$t/tickets.py" && cp plugins/sdlc-lite/scripts/order.py "$t/" && a=$(python3 -c "import sys, pathlib; sys.path.insert(0, sys.argv[1]); import tickets; r = pathlib.Path('.sdlc'); sys.stdout.write(tickets.render(tickets.load(r), r))" "$t") && b=$(python3 -c "import sys, pathlib; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import tickets; r = pathlib.Path('.sdlc'); sys.stdout.write(tickets.render(tickets.load(r), r))") && test -n "$a" && test "$a" = "$b"`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/tickets.py" | { ! grep -q .; }`

## Step 2: Id floor, worktree hints, and external branches follow each tree's ticket root
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Change only `plugins/sdlc-lite/scripts/tickets.py`. Depends on: step 1 (`ticket_dir`).
- Add `other_ticket_dirs(root)`. It returns `[(worktree dir, ticket dir)]` in `worktree_pairs(root)` order, the same pair shape. Each ticket dir is `ticket_dir(<that tree's root>)`, read from that tree's own `<root>/config`. When that raises `Fail` (an unsupported value there), the pair keeps that tree's root. A tree's problems never fail this one, the rule `id_floor` already follows (tickets.py:493-512). `worktree_pairs` and `worktree_roots` stay unchanged.
- Three callers switch to `other_ticket_dirs(root)`:
  - `id_floor(root)` loads the other ticket dirs instead of `worktree_roots(root)`.
  - The no-filer hint in `cmd_close` globs `<other ticket dir>/<slug>/filer-L*.md`.
  - The `close --dry-run` `open ... (worktree <name>)` lines load the other ticket dirs.

  Callers keep passing the `.sdlc` root to `worktree_pairs`, `other_ticket_dirs`, and `branch_tickets`, never a ticket dir.
- `branch_tickets(root, branch)` first reads the branch's `<rel>/config` blob with `git cat-file -p <branch>:<rel>/config` (`<branch>:config` when rel is `.`). A missing blob means no line. When its lines hold `ticket_root: tickets` (the same regex and rule as `ticket_dir`), it lists `<branch>:<rel>/tickets` and reads `<rel>/tickets/<dir>/handoff.md` blobs. An unsupported value lists `<rel>` as today. Returned names stay folder names.
- Contract dependent: `fanout.py` calls `tickets.branch_tickets(root, ext)` for external lanes (fanout.py:319). A branch without the line is read exactly as today, so this step leaves fanout.py and its selftest untouched; the final step runs them.
- Docstring: the "Ids across git worktrees" paragraph says that each other worktree's and each registered branch's ticket root is resolved by that tree's or branch's own config. Use the phrase `own config`.
- Selftest: append cases. Build the git fixtures in Python, as the existing worktree cases do (tickets.py:2708-2760), because the stray-worktree hook stops role Bash from adding a worktree on a new branch. The fixture is main in the default layout plus a worktree whose `.sdlc/config` says `ticket_root: tickets`, with its tickets under `.sdlc/tickets/`. Cases:
  - new in either tree mints above the other tree's max.
  - `close --dry-run` in main lists an open ticket that exists only in the worktree's `tickets/` as `(worktree <name>)`.
  - The no-filer refusal names `<worktree>/.sdlc/tickets/<slug>` when that folder holds a filer.
  - An external branch whose committed config says `ticket_root: tickets` is counted by new on main.

  Negative control: the same external fixture without the `external_branch:` line mints the colliding id.
- Focused check: `python3 plugins/sdlc-lite/scripts/tickets.py selftest`.
### Acceptance criteria
- `t=$(mktemp -d) && P="$PWD/plugins/sdlc-lite/scripts/tickets.py" && git -C "$t" init -q -b main && python3 "$P" --root "$t/.sdlc" new feature alpha >/dev/null && git -C "$t" add -A && git -C "$t" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit --no-verify -qm a && git -C "$t" checkout -q -b ext && mkdir -p "$t/.sdlc/tickets" && git -C "$t" mv .sdlc/alpha .sdlc/tickets/alpha && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && python3 "$P" --root "$t/.sdlc" new feature beta >/dev/null && grep -qx 'id: T-0002' "$t/.sdlc/tickets/beta/handoff.md" && git -C "$t" add -A && git -C "$t" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit --no-verify -qm b && git -C "$t" checkout -q main && printf 'external_branch: ext\n' > "$t/.sdlc/config" && python3 "$P" --root "$t/.sdlc" new feature gamma >/dev/null && grep -qx 'id: T-0003' "$t/.sdlc/gamma/handoff.md"`
- `t=$(mktemp -d) && for c in a b; do mkdir -p "$t/$c/scripts" "$t/$c/skills/ticket" && cp plugins/sdlc-lite/scripts/*.py "$t/$c/scripts/" && cp -R plugins/sdlc-lite/skills/ticket/templates "$t/$c/skills/ticket/" || exit 1; done && python3 -c "import sys; p = sys.argv[1]; s = open(p).read(); k = 'def other_ticket_dirs(root):\n'; assert s.count(k) == 1, s.count(k); open(p, 'w').write(s.replace(k, k + '    return worktree_pairs(root)\n'))" "$t/b/scripts/tickets.py" && python3 "$t/a/scripts/tickets.py" selftest >/dev/null 2>&1 && ! python3 "$t/b/scripts/tickets.py" selftest >/dev/null 2>&1`
- `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import tickets; d = tickets.__doc__; assert 'own config' in d, 'docstring'"`
- (guard) `t=$(mktemp -d) && P="$PWD/plugins/sdlc-lite/scripts/tickets.py" && git -C "$t" init -q -b main && python3 "$P" --root "$t/.sdlc" new feature alpha >/dev/null && git -C "$t" add -A && git -C "$t" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit --no-verify -qm a && git -C "$t" checkout -q -b ext && python3 "$P" --root "$t/.sdlc" new feature beta >/dev/null && grep -qx 'id: T-0002' "$t/.sdlc/beta/handoff.md" && git -C "$t" add -A && git -C "$t" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit --no-verify -qm b && git -C "$t" checkout -q main && printf 'external_branch: ext\n' > "$t/.sdlc/config" && python3 "$P" --root "$t/.sdlc" new feature gamma >/dev/null && grep -qx 'id: T-0003' "$t/.sdlc/gamma/handoff.md"`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/tickets.py" | { ! grep -q .; }`

## Step 3: Router block, CLAUDE.md import, router line, and check causes
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Change only `plugins/sdlc-lite/scripts/tickets.py`. Depends on: steps 1 and 2.
- Add `import onboard` (same scripts dir; it imports the standard library only). Reuse onboard's managed-block format and helpers rather than inventing a second format, and leave onboard.py unchanged. The helpers, with the evidence for each:
  - `onboard.wrap_block`, which writes the start marker `<!-- sdlc-lite:managed:start v1 sha256:<12 hex> -->`, the block, and the end marker (onboard.py:219-226 and 365-373).
  - `onboard.find_block` and `onboard.digest` (onboard.py:485-533). A file holds at most one block.
  - `onboard.has_import` (onboard.py:200-215).
  - `onboard._replace_region` and `onboard._append_region`, which splice a block in and keep every byte outside the markers (onboard.py:618-631).

  Name this dependency in the docstring.
- Managed files: `<root>/AGENTS.md` (the router) and `<root>/CLAUDE.md`, always. With `ticket_root: tickets`, also `<root>/tickets/AGENTS.md` and `<root>/tickets/CLAUDE.md`.
- `write_router(root, ts)` (ts are the tickets of the ticket dir) is called by `write_roadmap(root, ts)` right after roadmap.md is written. Every command that regenerates the roadmap (new, close, roadmap, archive, number) therefore regenerates the router.
  - Each AGENTS.md: a missing file is created as the wrapped block alone. A file with no block gets the block through `_append_region`. A file with a block gets it through `_replace_region`, whatever the old block held.
  - Each CLAUDE.md: a missing file becomes `@AGENTS.md\n`. A file that fails `onboard.has_import` gets the line `@AGENTS.md` appended, with a newline first when it lacks a trailing one. A file that passes is left untouched.
- Preflight: new, close (`--dry-run` included), roadmap, archive, and number refuse before their first write when a managed AGENTS.md holds a malformed block (`onboard.find_block` status `malformed`). The message is `<label>: router block malformed: <reason>; fix its markers by hand, then rerun; nothing written`, and nothing is written.
- `router_problems(root, ts)` returns [] when ts is empty and `<root>/AGENTS.md` does not exist, the way a missing roadmap with no ticket passes today. Otherwise it returns one line per problem. `<label>` is `AGENTS.md`, `CLAUDE.md`, `tickets/AGENTS.md`, or `tickets/CLAUDE.md`. The lines are:
  - `<label>: router block missing; run tickets.py --root <root> roadmap` when the file or its block is absent.
  - `<label>: router block stale; run tickets.py --root <root> roadmap` when the block text, digest, or version differs from `onboard.wrap_block` of the expected body.
  - `<label>: router block malformed: <reason>; fix its markers by hand, then run tickets.py --root <root> roadmap`.
  - `<label>: no @AGENTS.md import; run tickets.py --root <root> roadmap`.

  `cmd_check` raises these lines after the problems and the stale-roadmap check, so a stale roadmap is still reported alone first. Its success output stays exactly `ok: <n> tickets, roadmap current` plus today's warnings, because the existing selftest compares it exactly (tickets.py:1341 and 1589).
- Paths in the text: `<R>` is the root and `<T>` is the ticket dir, each relative to `file_base(root)` (the git toplevel, else root's parent; tickets.py:681-695), in posix form. For the usual root these are `.sdlc`, and `.sdlc` or `.sdlc/tickets`. No absolute path, plugin path, or ticket id is written, so the text is the same on every machine and in every repo.
- Router body: the `<root>/AGENTS.md` block, exactly. Substitute `<R>`, `<T>`, and the stage lines. Every other `<...>` stays literal, `${CLAUDE_PLUGIN_ROOT}` included. Both templates below are indented four spaces in this plan only, so the plan parser does not read their `##` lines as plan sections; the written blocks have no indent:

    ```
    # Work records

    This folder holds SDLC Lite tickets, task records, `roadmap.md`, `notes.md`, and `config`. `tickets.py roadmap` (also run by `new` and `close`) generates this block: do not edit inside it; change a ticket's `handoff.md` front matter and rerun `roadmap`. `roadmap.md` lists every ticket in dependency order. Closed `.NNNN-*` folders are history: open one only when asked.

    - Ticket folders: next to this file.
    - Mailbox: `messages/` is a git-ignored mailbox, not a record; read it with `<plugin-root>/scripts/messages.py`.
    - `<plugin-root>` is the installed sdlc-lite plugin folder, the one holding `scripts/tickets.py`: `${CLAUDE_PLUGIN_ROOT}` in Claude Code; in Codex, the folder two levels above the `sdlc-lite` skill.

    ## Stages

    <stage lines>

    ## Procedures

    Create a ticket:
    1. Run `python3 <plugin-root>/scripts/tickets.py --root <R> new <feature|bug|chore|spike|idea> <slug> "<title>"`. Never pick an id by hand: `new` stamps the next id above every worktree's.
    2. Fill in the body sections of the new `handoff.md`.

    Claim a ticket:
    1. Open its `handoff.md`. A `claimed_by:` front matter line means another agent holds it: pick another ticket or ask the user.
    2. Add `claimed_by: <claude|codex> <YYYY-MM-DD>` to the front matter, then run `python3 <plugin-root>/scripts/tickets.py --root <R> roadmap`.
    3. Start the work through `run.sh`, which puts it in progress: `<plugin-root>/scripts/run.sh planner <level> <T>/<folder>/handoff.md`, or `/sdlc-lite:chain <T>/<folder>`. `status` stays a person's decision; progress shows on `/board`.

    Close a ticket:
    1. Run the filer (`/file`): `<plugin-root>/scripts/run.sh filer L1 <T>/<folder>/handoff.md`.
    2. Run `python3 <plugin-root>/scripts/tickets.py --root <R> close <folder> --dry-run`. It lists each follow-up as `<i>. <tag>: <title>` and ends with `expect <digest>`.
    3. Run `python3 <plugin-root>/scripts/tickets.py --root <R> close <folder>`. To file the one `decide:` follow-up worth a ticket, add `--ticket <i> --expect <digest>`. `note:` items and the other `decide:` items go to `notes.md`; `fix-now:` items are finished before the close.
    4. Work already done by another ticket: `python3 <plugin-root>/scripts/tickets.py --root <R> close <folder> --reason "<why>"`.
    ```

- Stage lines:
  - One `- <stage>: <count>` line per stage, in the order proposed, ready, blocked, done, dropped (`ENUMS['status']`).
  - Under proposed, ready, and blocked, one `  - <id> <title> (<folder>)` line per ticket, two spaces of indent, in id order. A ticket whose `claimed_by` is a non-empty string gets `, claimed by <value>` appended. done and dropped get the count only.
  - Closed `.NNNN-<slug>` folders count under their status.
  - The folder is the bare folder name, never a path, so close's cite scan never matches a router line.
- With `ticket_root: tickets`, the line `- Ticket folders: next to this file.` becomes ``- Ticket folders: `tickets/`; the same procedures are in `tickets/AGENTS.md`.``
- The `tickets/AGENTS.md` block is the following. The `<plugin-root>` line is the router's line, byte for byte. `## Procedures` is the router's section, byte for byte, and is the last section of both blocks.

    ```
    # Tickets

    One folder per ticket: `<slug>/` or `NNNN-<slug>/` while open, `.NNNN-<slug>/` once closed. Stage counts and the open tickets are in `../AGENTS.md`. `tickets.py roadmap` generates this block: do not edit inside it.

    <the router's `<plugin-root>` line>

    <the router's ## Procedures section>
    ```

- Router line in tickets: `stamp()` inserts `router: <T>/AGENTS.md  # how to claim and close this ticket`, with two spaces before `#`, as the last front matter line, right before the closing `---`. This covers new tickets and close follow-ups. `parse()` reads the value as `<T>/AGENTS.md`, because `parse_value` drops the comment (tickets.py:173-181). `problems()` validates neither `router` nor `claimed_by`, so older tickets without the line stay valid.
- Docstring: the router files, the CLAUDE.md import, `claimed_by`, the `router:` line, and the check causes.
- Selftest: append cases and change no existing case.
  - Regeneration and contents:
    - After new, the proposed count and the ticket line appear. After a status edit and `roadmap`, the line moves to ready. After close, the done count rises and the line is gone. A close follow-up adds a proposed line.
    - Per-stage contents are right with tickets in all five statuses, a closed dot folder included.
    - `claimed_by` shows on an active line.
    - Text outside the block and the existing CLAUDE.md content are kept, with one block and one import after repeated runs.
    - With `ticket_root: tickets`, tickets/AGENTS.md and tickets/CLAUDE.md are written, with identical Procedures and `.sdlc/tickets/<folder>` paths.
    - The router line is present in a new ticket and in a follow-up, in both layouts.
  - Negative controls, one per check cause, each next to a passing clean case:
    - missing block (AGENTS.md deleted)
    - stale count (a count edited by hand)
    - stale ticket line (`claimed_by` added while the roadmap stays current, so check names AGENTS.md and not roadmap.md)
    - missing CLAUDE.md import
    - missing tickets/AGENTS.md
    - malformed block: new, close, and roadmap refuse with nothing written, and check fails.
  - Positive: zero tickets and no AGENTS.md passes check.
- Injected defects: criteria 16 and 17 put defects into a copy of the scripts and require the selftest to fail. Criterion 17 makes `write_router` a no-op once AGENTS.md exists, so the count stays unchanged after a close, which is the example defect the handoff names. The verifier states the defect it injected and that the selftest failed.
- Contract dependents: tickets.py now imports onboard, and every copy of `scripts/*.py` in these criteria includes onboard.py. `write_roadmap` now also writes `.sdlc/AGENTS.md` and `.sdlc/CLAUDE.md` in the fanout, board, and traces selftest fixtures. Fanout stages everything under the root after a close (`git add -A -- <rel>`, fanout.py:752-755), and board and traces skip plain files. This step leaves those selftests untouched; the final step runs them.
- Focused check: `python3 plugins/sdlc-lite/scripts/tickets.py selftest`.
### Acceptance criteria
- `t=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && f="$t/.sdlc/AGENTS.md" && grep -qxF -- '- proposed: 1' "$f" && grep -qxF -- '  - T-0001 Alpha (alpha)' "$f" && grep -qxF -- '- ready: 0' "$f" && grep -qxF -- '- blocked: 0' "$f" && grep -qxF -- '- done: 0' "$f" && grep -qxF -- '- dropped: 0' "$f" && grep -qxF -- '- Ticket folders: next to this file.' "$f" && grep -qx '@AGENTS.md' "$t/.sdlc/CLAUDE.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" check`
- `t=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha >/dev/null && python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import onboard; f = onboard.find_block(open(sys.argv[1]).read()); assert f.status == 'block' and f.block.version == 1 and onboard.digest(f.block.text) == f.block.digest, f" "$t/.sdlc/AGENTS.md"`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && S=plugins/sdlc-lite/scripts/tickets.py && f="$t/.sdlc/AGENTS.md" && python3 $S --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && grep -qxF -- '- proposed: 1' "$f" && grep -qxF -- '  - T-0001 Alpha (alpha)' "$f" && grep -qxF -- '- ready: 0' "$f" && sed -i.bak 's/^status: proposed/status: ready/' "$t/.sdlc/tickets/alpha/handoff.md" && ! python3 $S --root "$t/.sdlc" check 2>/dev/null && python3 $S --root "$t/.sdlc" roadmap >/dev/null && grep -qxF -- '- proposed: 0' "$f" && grep -qxF -- '- ready: 1' "$f" && grep -qxF -- '  - T-0001 Alpha (alpha)' "$f" && python3 $S --root "$t/.sdlc" close alpha --reason "done elsewhere" >/dev/null && grep -qxF -- '- ready: 0' "$f" && grep -qxF -- '- done: 1' "$f" && ! grep -qF 'T-0001' "$f" && python3 $S --root "$t/.sdlc" check >/dev/null`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && printf '# Mine\n\nKeep me.\n' > "$t/.sdlc/AGENTS.md" && printf 'Hello\n' > "$t/.sdlc/CLAUDE.md" && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && python3 $S --root "$t/.sdlc" new feature beta "Beta" >/dev/null && test "$(head -3 "$t/.sdlc/AGENTS.md")" = "$(printf '# Mine\n\nKeep me.')" && test "$(head -1 "$t/.sdlc/CLAUDE.md")" = Hello && test "$(grep -c 'sdlc-lite:managed:start' "$t/.sdlc/AGENTS.md")" -eq 1 && test "$(grep -cx '@AGENTS.md' "$t/.sdlc/CLAUDE.md")" -eq 1 && grep -qxF -- '  - T-0002 Beta (beta)' "$t/.sdlc/AGENTS.md" && python3 $S --root "$t/.sdlc" check >/dev/null`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && python3 -c "import sys; p = sys.argv[1]; s = open(p).read(); open(p, 'w').write(s.replace('created:', 'claimed_by: codex 2026-09-30\ncreated:', 1))" "$t/.sdlc/alpha/handoff.md" && ! python3 $S --root "$t/.sdlc" check 2>"$t/err" && grep -qF AGENTS.md "$t/err" && ! grep -qF roadmap.md "$t/err" && python3 $S --root "$t/.sdlc" roadmap >/dev/null && grep -qxF -- '  - T-0001 Alpha (alpha), claimed by codex 2026-09-30' "$t/.sdlc/AGENTS.md" && python3 $S --root "$t/.sdlc" check >/dev/null`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && sed -i.bak 's/^- proposed: 1$/- proposed: 2/' "$t/.sdlc/AGENTS.md" && grep -qxF -- '- proposed: 2' "$t/.sdlc/AGENTS.md" && ! python3 $S --root "$t/.sdlc" check 2>"$t/err" && grep -qF AGENTS.md "$t/err" && grep -qF stale "$t/err" && ! grep -qF roadmap.md "$t/err"`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && rm "$t/.sdlc/AGENTS.md" && ! python3 $S --root "$t/.sdlc" check 2>"$t/err" && grep -qF AGENTS.md "$t/err" && grep -qF missing "$t/err" && ! grep -qF roadmap.md "$t/err"`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && grep -qx '@AGENTS.md' "$t/.sdlc/CLAUDE.md" && printf 'Other\n' > "$t/.sdlc/CLAUDE.md" && ! python3 $S --root "$t/.sdlc" check 2>"$t/err" && grep -qF CLAUDE.md "$t/err" && ! grep -qF roadmap.md "$t/err"`
- `t=$(mktemp -d) && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/.sdlc" new feature alpha >/dev/null && printf '<!-- sdlc-lite:managed:start v1 sha256:000000000000 -->\nno end\n' > "$t/.sdlc/AGENTS.md" && cp "$t/.sdlc/AGENTS.md" "$t/before" && cp "$t/.sdlc/roadmap.md" "$t/before-rm" && ! python3 $S --root "$t/.sdlc" new feature beta 2>"$t/err" && grep -qF malformed "$t/err" && test ! -e "$t/.sdlc/beta" && ! python3 $S --root "$t/.sdlc" roadmap 2>/dev/null && cmp -s "$t/before" "$t/.sdlc/AGENTS.md" && cmp -s "$t/before-rm" "$t/.sdlc/roadmap.md" && ! python3 $S --root "$t/.sdlc" check 2>/dev/null`
- `t=$(mktemp -d) && git -C "$t" init -q && mkdir -p "$t/.sdlc" && printf 'ticket_root: tickets\nticket_folders: numbered\n' > "$t/.sdlc/config" && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && python3 $S --root "$t/.sdlc" new feature beta "Beta" >/dev/null && grep -qxF -- '  - T-0001 Alpha (0001-alpha)' "$t/.sdlc/AGENTS.md" && printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' > "$t/.sdlc/tickets/0001-alpha/filer-L1.md" && python3 $S --root "$t/.sdlc" close 0001-alpha >/dev/null && test -d "$t/.sdlc/tickets/.0001-alpha" && ! grep -qF 'T-0001' "$t/.sdlc/AGENTS.md" && grep -qxF -- '- done: 1' "$t/.sdlc/AGENTS.md" && python3 $S --root "$t/.sdlc" check >/dev/null`
- ``t=$(mktemp -d) && mkdir -p "$t/.sdlc" && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha "Alpha" >/dev/null && python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import onboard; f = onboard.find_block(open(sys.argv[1]).read()); assert f.status == 'block' and onboard.digest(f.block.text) == f.block.digest, f" "$t/.sdlc/tickets/AGENTS.md" && grep -qx '@AGENTS.md' "$t/.sdlc/tickets/CLAUDE.md" && grep -qF -- '- Ticket folders: `tickets/`' "$t/.sdlc/AGENTS.md" && grep -qF '<plugin-root>/scripts/run.sh filer L1 .sdlc/tickets/<folder>/handoff.md' "$t/.sdlc/tickets/AGENTS.md" && python3 -c "import sys; a, b = (open(p).read() for p in sys.argv[1:3]); s = lambda x: x[x.index('## Procedures'):x.index('sdlc-lite:managed:end')]; assert s(a) == s(b), 'procedures differ'" "$t/.sdlc/AGENTS.md" "$t/.sdlc/tickets/AGENTS.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" check >/dev/null``
- `t=$(mktemp -d) && mkdir -p "$t/a/.sdlc" "$t/b/.sdlc" && printf 'ticket_root: tickets\n' > "$t/b/.sdlc/config" && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/a/.sdlc" new feature alpha >/dev/null && python3 $S --root "$t/b/.sdlc" new feature alpha >/dev/null && grep -qxF 'router: .sdlc/AGENTS.md  # how to claim and close this ticket' "$t/a/.sdlc/alpha/handoff.md" && grep -qxF 'router: .sdlc/tickets/AGENTS.md  # how to claim and close this ticket' "$t/b/.sdlc/tickets/alpha/handoff.md" && python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import tickets; m = tickets.parse(open(sys.argv[1]).read()); assert m.get('router') == '.sdlc/tickets/AGENTS.md', m.get('router')" "$t/b/.sdlc/tickets/alpha/handoff.md"`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/.sdlc" new feature alpha >/dev/null && printf '## Warnings\nNone\n\n## Follow-ups\n- decide: Add retry to fetch\n' > "$t/.sdlc/tickets/alpha/filer-L1.md" && d=$(python3 $S --root "$t/.sdlc" close alpha --dry-run | sed -n 's/^expect //p') && test -n "$d" && python3 $S --root "$t/.sdlc" close alpha --ticket 1 --expect "$d" >/dev/null && grep -qxF 'router: .sdlc/tickets/AGENTS.md  # how to claim and close this ticket' "$t/.sdlc/tickets/add-retry-to-fetch/handoff.md" && grep -qxF -- '  - T-0002 Add retry to fetch (add-retry-to-fetch)' "$t/.sdlc/AGENTS.md"`
- `t=$(mktemp -d) && mkdir -p "$t/.sdlc" && printf 'ticket_root: tickets\n' > "$t/.sdlc/config" && S=plugins/sdlc-lite/scripts/tickets.py && python3 $S --root "$t/.sdlc" new feature alpha >/dev/null && rm "$t/.sdlc/tickets/AGENTS.md" && ! python3 $S --root "$t/.sdlc" check 2>"$t/err" && grep -qF 'tickets/AGENTS.md' "$t/err" && python3 $S --root "$t/.sdlc" roadmap >/dev/null && python3 $S --root "$t/.sdlc" check >/dev/null && printf 'Other\n' > "$t/.sdlc/tickets/CLAUDE.md" && ! python3 $S --root "$t/.sdlc" check 2>"$t/err2" && grep -qF 'tickets/CLAUDE.md' "$t/err2"`
- `t=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/tickets.py --root "$t/.sdlc" new feature alpha >/dev/null && f="$t/.sdlc/AGENTS.md" && grep -qF 'python3 <plugin-root>/scripts/tickets.py --root .sdlc new <feature|bug|chore|spike|idea> <slug> "<title>"' "$f" && grep -qF 'claimed_by: <claude|codex> <YYYY-MM-DD>' "$f" && grep -qF 'python3 <plugin-root>/scripts/tickets.py --root .sdlc roadmap' "$f" && grep -qF '<plugin-root>/scripts/run.sh planner <level> .sdlc/<folder>/handoff.md' "$f" && grep -qF '<plugin-root>/scripts/run.sh filer L1 .sdlc/<folder>/handoff.md' "$f" && grep -qF 'python3 <plugin-root>/scripts/tickets.py --root .sdlc close <folder> --dry-run' "$f" && grep -qF 'close <folder> --reason' "$f" && grep -qF 'git-ignored mailbox' "$f" && grep -qF '<plugin-root>/scripts/messages.py' "$f" && ! grep -qF 'T-0176' "$f"`
- `t=$(mktemp -d) && for c in a b; do mkdir -p "$t/$c/scripts" "$t/$c/skills/ticket" && cp plugins/sdlc-lite/scripts/*.py "$t/$c/scripts/" && cp -R plugins/sdlc-lite/skills/ticket/templates "$t/$c/skills/ticket/" || exit 1; done && python3 -c "import sys; p = sys.argv[1]; s = open(p).read(); k = 'def router_problems(root, ts):\n'; assert s.count(k) == 1, s.count(k); open(p, 'w').write(s.replace(k, k + '    return []\n'))" "$t/b/scripts/tickets.py" && python3 "$t/a/scripts/tickets.py" selftest >/dev/null 2>&1 && ! python3 "$t/b/scripts/tickets.py" selftest >/dev/null 2>&1`
- `t=$(mktemp -d) && for c in a b; do mkdir -p "$t/$c/scripts" "$t/$c/skills/ticket" && cp plugins/sdlc-lite/scripts/*.py "$t/$c/scripts/" && cp -R plugins/sdlc-lite/skills/ticket/templates "$t/$c/skills/ticket/" || exit 1; done && python3 -c "import sys; p = sys.argv[1]; s = open(p).read(); k = 'def write_router(root, ts):\n'; assert s.count(k) == 1, s.count(k); open(p, 'w').write(s.replace(k, k + '    if (root / \'AGENTS.md\').exists():\n        return\n'))" "$t/b/scripts/tickets.py" && python3 "$t/a/scripts/tickets.py" selftest >/dev/null 2>&1 && ! python3 "$t/b/scripts/tickets.py" selftest >/dev/null 2>&1`
- `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import tickets; d = tickets.__doc__; assert all(w in d for w in ('AGENTS.md', 'CLAUDE.md', 'claimed_by', 'router:')), 'docstring'"`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `t=$(mktemp -d) && git show "$SDLC_BASE_SHA":plugins/sdlc-lite/scripts/tickets.py > "$t/tickets.py" && cp plugins/sdlc-lite/scripts/order.py "$t/" && a=$(python3 -c "import sys, pathlib; sys.path.insert(0, sys.argv[1]); import tickets; r = pathlib.Path('.sdlc'); sys.stdout.write(tickets.render(tickets.load(r), r))" "$t") && b=$(python3 -c "import sys, pathlib; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import tickets; r = pathlib.Path('.sdlc'); sys.stdout.write(tickets.render(tickets.load(r), r))") && test -n "$a" && test "$a" = "$b"`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/tickets.py" | { ! grep -q .; }`

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

## Step 6: Reference docs, skills, and design status
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 to 5 (the docs describe built behavior). Files: `docs/maintenance/sdlc-internals.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, `plugins/sdlc-lite/skills/ticket/SKILL.md`, `docs/ticket-stages/design.md`, `docs/ticket-stages/README.md`, `docs/README.md`. Write no em dash. Keep every phrase that `scripts/check.py` requires in these files (`notes.md`, `fix-now:`, `decide:`, `Plan review`, the merge-step block, and the others it lists) byte-identical. Neither skill is preloaded by any agent (`skills:` in `agents/*.md` names only level-rubric, checks-that-bite, checking-rules, and decompose), so no Codex agent regeneration is needed.
- `docs/maintenance/sdlc-internals.md`:
  - The `scripts/tickets.py` entry gains these facts:
    - An opt-in `ticket_root: tickets` line in `<root>/config` puts the ticket folders under `<root>/tickets/`.
    - Ids, closure, the cite scan (it then looks for `<rel>/tickets/<slug>`), the roadmap (it links `tickets/<slug>/handoff.md`), `check`, and the worktree and external-branch id floor all follow that root, each other tree or branch resolved by its own config.
    - roadmap.md, config, notes.md, and `_templates/` stay at `<root>`.
    - Any other value refuses, with nothing written. With the line set, a ticket folder directly under `<root>` fails `check` as outside the ticket root.
    - Every roadmap regeneration writes the router: a managed block in onboard's marker format, in `.sdlc/AGENTS.md` (created if missing, text outside the block untouched). It holds per-stage counts and one `T-NNNN <title> (<folder>)` line per proposed, ready, and blocked ticket, with `, claimed by <value>` when the optional `claimed_by` front matter is set. It also holds the `messages/` mailbox line and the create, claim, and close procedures.
    - It ensures `.sdlc/CLAUDE.md` holds `@AGENTS.md`. With `ticket_root: tickets` it also writes `tickets/AGENTS.md` and `tickets/CLAUDE.md`.
    - `new` stamps `router: <ticket dir>/AGENTS.md` as the last front matter line.
    - `check` fails, naming the file, on a missing, stale, or malformed block or a missing import. A malformed block makes every writing command refuse.
    - After an upgrade, a repo with tickets runs `roadmap` once to add the router.
  - The board paragraph gains: with `ticket_root: tickets` in `.sdlc/config` it also lists the task dirs under `.sdlc/tickets/`.
  - The `scripts/fanout.py` entry gains: regular lanes do not follow `ticket_root` yet. With the line set, preflight finds no ticket under `<root>` for their ids and refuses. This is a follow-up.
  - The `scripts/traces.py` entry gains: ingest also walks `tickets/<name>` task dirs and the ticket reader reads `<root>/tickets` when the config sets `ticket_root: tickets`.
- `skills/handoff-format/SKILL.md`:
  - Add these lines to the Layout code block, after the `.sdlc/_templates/<type>.md` line:
    - `.sdlc/AGENTS.md         router: stage counts, open tickets, and the create, claim, and close procedures; its managed block is regenerated by tickets.py roadmap, new, and close`
    - `.sdlc/CLAUDE.md         @AGENTS.md, so Claude Code loads the router`
    - `.sdlc/config            optional lines: ticket_folders: numbered, external_branch: <branch>, ticket_root: tickets`
    - `.sdlc/tickets/          the ticket folders when config has ticket_root: tickets, with its own AGENTS.md and CLAUDE.md; roadmap.md, notes.md, config, and _templates/ stay in .sdlc/`
  - In the ticket front matter block, after the `provides:` line, add:
    - `claimed_by: <harness> <YYYY-MM-DD>   # optional, who works on it; shown in the router; a second claimant checks it first`
    - `router: .sdlc/AGENTS.md   # stamped by new: the folder rules (.sdlc/tickets/AGENTS.md with ticket_root: tickets)`
- `skills/ticket/SKILL.md`: one new Rules bullet:
  - `ticket_root: tickets` in `.sdlc/config` is opt-in and keeps ticket folders under `.sdlc/tickets/`. roadmap.md, notes.md, config, and `_templates/` stay in `.sdlc/`, and a ticket folder left directly in `.sdlc/` fails `check`.
  - Every command that regenerates the roadmap also regenerates the router block in `.sdlc/AGENTS.md` (and `.sdlc/tickets/AGENTS.md`). The block lists each stage's count and the open tickets, and carries the create, claim, and close procedures.
  - `check` fails when a router block is missing, stale, or malformed, or when a `CLAUDE.md` lacks `@AGENTS.md`. After an upgrade, run `roadmap` once to write the router.
  - An optional `claimed_by: <harness> <YYYY-MM-DD>` front matter line marks a claim and shows in the router.
- `docs/ticket-stages/design.md` line 3 becomes ``Version 0.2, <today's date>. Built: Option A (the router) and the opt-in `tickets/` root. The rest is a proposal.``
- `docs/ticket-stages/README.md` line 3 becomes ``Built: Option A (the router) and the opt-in `tickets/` root. The rest is a proposal, not yet independently reviewed.``
- `docs/README.md`: the Ticket stages line's text after the link becomes ``: the `.sdlc/` router and the opt-in `tickets/` root (built), stage folders and a cross-harness mailbox (proposed).``
- Focused checks: `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`, `python3 scripts/check-packaging.py`, and `git diff --check`.
### Acceptance criteria
- `grep -qF 'ticket_root: tickets' docs/maintenance/sdlc-internals.md && grep -qF '.sdlc/AGENTS.md' docs/maintenance/sdlc-internals.md && grep -qF 'claimed_by' docs/maintenance/sdlc-internals.md && grep -qF 'router:' docs/maintenance/sdlc-internals.md`
- ``grep -qF 'task dirs under `.sdlc/tickets/`' docs/maintenance/sdlc-internals.md``
- ``grep -qF 'do not follow `ticket_root`' docs/maintenance/sdlc-internals.md``
- `grep -qF '.sdlc/AGENTS.md' plugins/sdlc-lite/skills/handoff-format/SKILL.md && grep -qF '.sdlc/CLAUDE.md' plugins/sdlc-lite/skills/handoff-format/SKILL.md && grep -qF '.sdlc/tickets/' plugins/sdlc-lite/skills/handoff-format/SKILL.md && grep -qF 'ticket_root: tickets' plugins/sdlc-lite/skills/handoff-format/SKILL.md && grep -qF 'claimed_by:' plugins/sdlc-lite/skills/handoff-format/SKILL.md && grep -qF 'router:' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'ticket_root: tickets' plugins/sdlc-lite/skills/ticket/SKILL.md && grep -qF '.sdlc/AGENTS.md' plugins/sdlc-lite/skills/ticket/SKILL.md && grep -qF 'claimed_by' plugins/sdlc-lite/skills/ticket/SKILL.md`
- ``grep -qF 'Built: Option A (the router) and the opt-in `tickets/` root' docs/ticket-stages/design.md && grep -qF 'Built: Option A (the router) and the opt-in `tickets/` root' docs/ticket-stages/README.md``
- ``grep -qF 'opt-in `tickets/` root (built)' docs/README.md``
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/tickets.py|plugins/sdlc-lite/scripts/board.py|plugins/sdlc-lite/scripts/traces/ingest.py|plugins/sdlc-lite/scripts/traces/sources/tickets.py|plugins/sdlc-lite/scripts/traces/selftest.py|docs/maintenance/sdlc-internals.md|plugins/sdlc-lite/skills/handoff-format/SKILL.md|plugins/sdlc-lite/skills/ticket/SKILL.md|docs/ticket-stages/design.md|docs/ticket-stages/README.md|docs/README.md" | { ! grep -q .; }`

## Step 7: Live run in throwaway repos and the dated validation record
level: L3
### Do
Depends on: steps 1 to 3 (the code under test) and step 6 (the docs/README.md line this step extends). Files: the new `docs/validation/ticket-root-router-live-run.md` and one new list item in `docs/README.md`, placed after the "Plan reviewer live run" item: ``- [Ticket root and router live run](validation/ticket-root-router-live-run.md): dated live run for T-0175 showing the router block change as a ticket moves proposed to ready to done under `ticket_root: tickets`, and a fresh role claiming and closing a ticket from `tickets/AGENTS.md` alone.`` Run everything in `mktemp -d` projects outside this repository, and keep transcripts and logs out of the repository. Write no em dash. Model the doc on `docs/validation/plan-reviewer-live-run.md`.
- Scripted run: this is deterministic, with no model call.
  1. In a fresh git project, write `.sdlc/config` with `ticket_root: tickets` and `ticket_folders: numbered`.
  2. Run `python3 <repo>/plugins/sdlc-lite/scripts/tickets.py --root .sdlc new feature probe "Probe ticket"`.
  3. Set `status: ready` in `.sdlc/tickets/0001-probe/handoff.md` and run `roadmap`.
  4. Write `.sdlc/tickets/0001-probe/filer-L1.md` holding `## Warnings` None and `## Follow-ups` None.
  5. Run `close 0001-probe`, then `check`.
  6. Copy the Stages section of `.sdlc/AGENTS.md` verbatim, in a fenced block, after each of new, roadmap, and close. The three excerpts hold the lines `- proposed: 1`, `- ready: 1`, and `- done: 1`.
  7. State that the folder ended at `.sdlc/tickets/.0001-probe` and that `check` printed `ok`.
- Fresh role (Claude Code):
  1. Set up a second fresh project the same way, with `new`, the status set to ready, and `roadmap`, then commit it.
  2. From that project root, run `claude -p --model sonnet --effort low --dangerously-skip-permissions --output-format stream-json --verbose -- "<prompt>"`, with no `--plugin-dir` and no `--agent`. Run it through the env wrapper of `plan-reviewer-live-run.md`: unset `CLAUDECODE`, every `CLAUDE_CODE_*` variable, and `SDLC_ROLE SDLC_BASE_SHA SDLC_TMP_WORKTREES SDLC_HEADLESS SDLC_ATTEMPT_ID SDLC_ATTEMPT_NAME SDLC_LIFECYCLE_CHILD SDLC_ROUTING_REASON`. Use the Bash timeout at 600000 or more, in the foreground. Write the log to a file in the temp project, outside this repository.
  3. The prompt is exactly: `Ticket: .sdlc/tickets/0001-probe/handoff.md. Claim this ticket, then close it: its work was already done elsewhere. The sdlc-lite plugin folder is <absolute path of this worktree>/plugins/sdlc-lite.`. It names the plugin folder because the installed plugin caches hold 0.20.1, which has no `ticket_root` (`grep -c ticket_root` of the cached `tickets.py` is 0). It names no skill.
- Record the following from the transcript and the final files:
  - whether the role read `.sdlc/tickets/AGENTS.md` (reached through the handoff's `router:` line);
  - the commands it ran;
  - whether the handoff gained `claimed_by: claude <date>` and the router showed `, claimed by` before the close;
  - whether the ticket ended `status: done` with a `## Closed` section at `.sdlc/tickets/.0001-probe`;
  - whether the router shows `- done: 1`;
  - whether `tickets.py --root .sdlc check` passes;
  - whether any Skill tool call appears.

  Write `Result: verified` when every one holds. Otherwise write `Result: unverified: <what failed>`. When `claude` is missing or not logged in, write `Result: unverified: <the reason>`.
- Doc layout, in this order:
  - `# Ticket root and router live run`
  - a `Recorded: <YYYY-MM-DD>.` line
  - `## Environment`: the Claude Code version, the model from the log's `"model"` field, the plugin commit plus whether the T-0175 changes were uncommitted, and macOS.
  - `## Scripted run`
  - `## Fresh role`: the prompt, the observations, and the `Result:` line.
  - `## Limits`: Claude Code only, Codex not run and not claimed; the prompt named the plugin folder, for the reason above; one trial per arm.
### Acceptance criteria
- `test -f docs/validation/ticket-root-router-live-run.md && grep -qE '^Recorded: [0-9]{4}-[0-9]{2}-[0-9]{2}\.' docs/validation/ticket-root-router-live-run.md`
- `grep -qF '(validation/ticket-root-router-live-run.md)' docs/README.md`
- `grep -qx '## Scripted run' docs/validation/ticket-root-router-live-run.md && grep -qxF -- '- proposed: 1' docs/validation/ticket-root-router-live-run.md && grep -qxF -- '- ready: 1' docs/validation/ticket-root-router-live-run.md && grep -qxF -- '- done: 1' docs/validation/ticket-root-router-live-run.md && grep -qF 'ticket_root: tickets' docs/validation/ticket-root-router-live-run.md`
- `grep -qx '## Fresh role' docs/validation/ticket-root-router-live-run.md && grep -qE '^Result: (verified|unverified: .+)$' docs/validation/ticket-root-router-live-run.md && grep -qx '## Limits' docs/validation/ticket-root-router-live-run.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/tickets.py|plugins/sdlc-lite/scripts/board.py|plugins/sdlc-lite/scripts/traces/ingest.py|plugins/sdlc-lite/scripts/traces/sources/tickets.py|plugins/sdlc-lite/scripts/traces/selftest.py|docs/maintenance/sdlc-internals.md|plugins/sdlc-lite/skills/handoff-format/SKILL.md|plugins/sdlc-lite/skills/ticket/SKILL.md|docs/ticket-stages/design.md|docs/ticket-stages/README.md|docs/README.md|docs/validation/ticket-root-router-live-run.md" | { ! grep -q .; }`

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

## Assumptions
- `load(root)` is the only ticket-folder lister, and outside tickets.py only `traces/sources/tickets.py` and `fanout.py` call it, while board.py uses only `parse`, `GIT_ENV_DROP`, and `ENUMS`: verified by `git grep -n "import tickets\|tickets\.[a-z_]*("` over plugins and scripts.
- Every command that regenerates the roadmap goes through `write_roadmap` (new, close, roadmap, archive, number), so hooking the router there covers each regeneration: verified at tickets.py:819, 1014, 1158, 1181, 1235, 1275.
- The existing selftest compares check's success line exactly (`out == 'ok: 2 tickets, roadmap current'`), so that line must not change: verified at tickets.py:1341 and 1589.
- A router can be stale while the roadmap is current only through `claimed_by` or edits to the managed files, because every other router input (id, title, status, folder) is a roadmap input too. So no existing selftest case reaches the new router failure: verified by reading `render` (tickets.py:708-724) against the router fields. The case fixtures are built through `run(...)` commands, which write the router.
- onboard.py's block format and helpers fit: one managed block per file (find_block marks two blocks malformed), a version and 12-hex sha256 in the start marker, and region splicing that keeps bytes outside the markers. It imports only the standard library, in about 0.09 s: verified at onboard.py:219-226, 365-373, 485-533, 618-631, and by timing `import onboard`.
- onboard does not manage `.sdlc/AGENTS.md`, so no two writers own that file: verified with `grep -n "\.sdlc" plugins/sdlc-lite/scripts/onboard.py` (only template prose).
- Claude Code loads a nested `AGENTS.md` only through a `CLAUDE.md` import and does load a parent folder's `CLAUDE.md`, so both `.sdlc/CLAUDE.md` and `tickets/CLAUDE.md` are needed: verified in docs/validation/nested-entry-file-loading.md (Results for Claude Code).
- The stray-worktree hook blocks role Bash from adding a git worktree on a new branch, so worktree behavior is proven through selftest cases (Python subprocess) and copy-sabotage criteria, and the CLI criteria use an external branch: verified when the hook denied such a command in the interrupted planner attempt and in this run.
- `steps.py` ends a step block at any line starting with `## `, even inside a fence, so step 3's templates are indented: verified at steps.py:277-300.
- The lint's placeholder rule swallows `<!--` up to a later `>`, so no criterion contains `<!--` followed by a later `>`: verified when `steps.py lint` refused that form and accepted the rewrite.
- No agent preloads the handoff-format or ticket skill, so step 6 needs no Codex agent regeneration: verified by reading `skills:` in `plugins/sdlc-lite/agents/*.md`.
- The repo's `.sdlc` check is red at HEAD only because roadmap.md is stale (T-0176's size changed), and `roadmap` fixes it with no ticket problem: verified by running `tickets.py --root .sdlc check` and diffing `render` against roadmap.md.
- The installed plugin caches (`~/.claude/plugins/cache/sdlc-lite/sdlc-lite/0.20.1`, `~/.codex/plugins/cache/sdlc-lite/sdlc-lite/0.20.1`) have no `ticket_root`, so the live-run prompt must name this worktree's plugin folder: verified with `ls -d` and `grep -c ticket_root` (0).
- fanout stages everything under the root after a close (`git add -A -- <rel>`), so the router files ride the `close <id>` commit: verified at fanout.py:752-755.
- Regular fanout lanes build `rel / slug` paths in eight places plus their selftest, which is not a small fix, so they stay a named follow-up. Their preflight already refuses safely under `ticket_root` ("no ticket under <root> has this id"): verified at fanout.py:283-337 and 415-746.
- The router lists only this worktree's tickets, not other worktrees' (design open question 2). The handoff asks for the local stage lists only, and cross-tree lines would make the block differ by machine state.
- At HEAD no em dash appears in any file the plan edits: verified by counting U+2014 in each.
- Every guard was seen red in the same command shape (a sabotaged copy, a fixture, or an older base) and is green now; every new-behavior criterion is red now because the behavior is missing: verified by the probe runs in this planning session.

## Risks
- Router blocks regenerate wherever the roadmap does, so parallel lanes that each run `new` or `close` will conflict on `.sdlc/AGENTS.md` the way they already can on `roadmap.md`. Rerunning `roadmap` after the merge resolves both.
- After upgrading, a consumer repo with tickets fails `check` until it runs `roadmap` once, because the handoff makes a missing router block a failure. Step 6 documents the one-time `roadmap` run.
- Step 8's `tickets.py --root .sdlc check` can turn red again if another lane in this worktree (T-0176) edits ticket front matter after the step's `roadmap` run. Rerun `roadmap`, never a hand edit.
- tickets.py calls onboard's underscore helpers (`_replace_region`, `_append_region`). A later rename in onboard.py breaks the router, but the tickets selftest catches it.
- The step 7 fresh-role run depends on a logged-in `claude` CLI and on model behavior, so it may honestly record `Result: unverified: <reason>`. Codex is not exercised.
- Step 3 is large, with about 20 criteria and many selftest cases. If the builder blocks on size, splitting it at the preflight and `router_problems` boundary is the natural replan.
