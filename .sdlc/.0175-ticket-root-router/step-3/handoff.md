## Task goal
`tickets.py` can use a `tickets/` ticket root under `.sdlc/` when `<root>/config` says `ticket_root: tickets`, and `tickets.py roadmap` keeps a managed router block in `.sdlc/AGENTS.md` current, so an agent reads one short file and opens only the tickets in the stage it needs.

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
