## Task goal
A harness that reads `.sdlc/*` learns the ticket and message folder systems from the entry files alone, and a fresh Claude role and a fresh Codex role, given only a path to a message file and no skill, ack it and reply correctly.

## Step 2: Router link and roadmap writer in tickets.py
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `.sdlc/AGENTS.md`
### Do
Depends on: step 1 (`messages.write_entries`).

**`plugins/sdlc-lite/scripts/tickets.py`**
- `write_roadmap(root, ts)` (tickets.py:837): after `write_router(root, ts)`, import `messages` inside the function and call `messages.write_entries(os.path.join(root, 'messages'))`.
  - `messages.py` is in the same scripts dir. The import is local so that `board.py`, `fanout.py`, and `traces`, which import `tickets` only to parse, do not load the mailbox module.
  - It always writes, creating the folder when it is missing, so the router's link resolves before any message exists.
- Mailbox path: `<root>/messages`. This is the same mailbox `messages.py --root <root>` uses (T-0177 Mailbox root: `--root DIR` means `DIR/messages`, messages.py:350-353). There is no new resolution rule and no write outside `<root>`.
  - From the main checkout with `--root .sdlc`, this is the shared mailbox.
  - In a linked worktree it is a local folder holding only the entry files. `messages.py` run there resolves the main checkout's mailbox through git, and step 1's `send`/`reply` keep that mailbox's entry files current.
  - With `ticket_root: tickets` the path stays `<root>/messages`, never under `tickets/`.
- Refusals (the router preflight, strays, bad tickets) happen before `write_roadmap`, so a refused command writes no entry files. `--dry-run` writes nothing.
- `check` does not validate the entry files: they are git-ignored local state that a fresh clone lacks. `router_problems` is unchanged.
- The router's mailbox line in `ROUTER_TEMPLATE` (tickets.py:894) becomes exactly:

```
- Mailbox: `messages/` is a git-ignored mailbox, not a record; follow `messages/AGENTS.md` to send, read, reply, ack, or expire a message with `<plugin-root>/scripts/messages.py`.
```

  It keeps `<plugin-root>`: the router is tracked, so it holds no machine path. `TICKETS_TEMPLATE` has no mailbox line and is unchanged.
- Module docstring, Router paragraph, add three facts:
  - `write_roadmap` also writes the mailbox entry files under `<root>/messages/` through `messages.write_entries`, creating the folder. The files are `.gitignore`, `AGENTS.md`, `CLAUDE.md`, and `AGENTS.md` and `CLAUDE.md` in each of `new/`, `read/`, `done/`.
  - The router's Mailbox line links `messages/AGENTS.md`.
  - `check` does not validate the entry files.
- New `selftest()` cases (`expect` labels):
  - `router: roadmap writes the mailbox entry files`
  - `router: roadmap restores an edited mailbox entry file`
  - `router: ticket_root keeps the mailbox at <root>/messages`
  - `router: a refused roadmap writes no mailbox entry files` (the malformed-block fixture)
  - `router: check passes without the mailbox entry files`
  - `router: the router links messages/AGENTS.md`

**`plugins/sdlc-lite/skills/ticket/SKILL.md`** (the consumer contract for this behavior), line 21: after the sentence saying every command that regenerates the roadmap also regenerates the router block, insert this sentence:

```
It also writes the mailbox entry files in `.sdlc/messages/`, whose `AGENTS.md` holds the mailbox procedures that the router's Mailbox line links.
```

This skill is not preloaded into any role (the agents' `skills:` lists name only `decompose`, `level-rubric`, `checks-that-bite`, `checking-rules`), so no Codex agent regeneration is needed.

**This repo's tracked router**: run `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap`.
- `.sdlc/AGENTS.md` is already stale at HEAD (`tickets.py --root .sdlc check` prints `AGENTS.md: router block stale`), so this run both fixes it and adds the link.
- It may rewrite `.sdlc/roadmap.md`, and it writes the git-ignored `.sdlc/messages/` entry files in this worktree.
- `.sdlc/` is outside the scope criterion.

**Contract dependents**
- `tickets.py selftest`: its `snap(root) == before` checks on refusals and dry runs (tickets.py:1875-2850) stay valid, because entry files are written only inside `write_roadmap`. Guarded below.
- `fanout.py`: lanes run `tickets.py close` and roadmap, commit with `git add -A`, and check porcelain. The mailbox's own `.gitignore` (step 1) keeps entry files out. Guarded below.
- `board.py` imports `tickets`. `task_dirs` needs a `handoff.md` (board.py:205-210), so `messages/` never shows as a task. Guarded below.
- `docs/validation/ticket-root-router-live-run.md` lists the files `new` wrote. It is dated evidence and stays untouched on purpose.
- Prose in `skills/handoff-format/SKILL.md` and `docs/maintenance/sdlc-internals.md` is step 4.

No em dashes. Focused checks: `python3 plugins/sdlc-lite/scripts/tickets.py selftest`, `fanout.py selftest`, `board.py selftest`.
### Acceptance criteria
- `R=$PWD && t=$(mktemp -d) && git -C "$t" init -q && cd "$t" && python3 "$R/plugins/sdlc-lite/scripts/tickets.py" --root .sdlc roadmap >/dev/null && grep -qxF "## Handle a message you were given" .sdlc/messages/AGENTS.md && printf '*\n' | cmp -s - .sdlc/messages/.gitignore && for s in . new read done; do printf '@AGENTS.md\n' | cmp -s - ".sdlc/messages/$s/CLAUDE.md" || exit 1; done`
- `R=$PWD && t=$(mktemp -d) && git -C "$t" init -q && cd "$t" && S="$R/plugins/sdlc-lite/scripts" && python3 "$S/tickets.py" --root .sdlc roadmap >/dev/null && test -d .sdlc/messages && mv .sdlc/messages "$t.roadmap" && python3 "$S/messages.py" send --receiver codex --sender claude --topic probe --follow-up false hello >/dev/null && for f in .gitignore AGENTS.md CLAUDE.md new/AGENTS.md new/CLAUDE.md read/AGENTS.md read/CLAUDE.md done/AGENTS.md done/CLAUDE.md; do cmp -s "$t.roadmap/$f" ".sdlc/messages/$f" || exit 1; done`
- `R=$PWD && t=$(mktemp -d) && git -C "$t" init -q && cd "$t" && python3 "$R/plugins/sdlc-lite/scripts/tickets.py" --root .sdlc roadmap >/dev/null && grep -F "Mailbox:" .sdlc/AGENTS.md | grep -qF "messages/AGENTS.md"`
- `R=$PWD && t=$(mktemp -d) && git -C "$t" init -q && cd "$t" && T="$R/plugins/sdlc-lite/scripts/tickets.py" && python3 "$T" --root .sdlc roadmap >/dev/null && test -f .sdlc/messages/new/AGENTS.md && cp .sdlc/messages/new/AGENTS.md "$t.want" && printf 'edited\n' > .sdlc/messages/new/AGENTS.md && rm .sdlc/messages/read/CLAUDE.md && python3 "$T" --root .sdlc roadmap >/dev/null && cmp -s "$t.want" .sdlc/messages/new/AGENTS.md && printf '@AGENTS.md\n' | cmp -s - .sdlc/messages/read/CLAUDE.md`
- `R=$PWD && t=$(mktemp -d) && git -C "$t" init -q && cd "$t" && mkdir .sdlc && printf 'ticket_root: tickets\n' > .sdlc/config && python3 "$R/plugins/sdlc-lite/scripts/tickets.py" --root .sdlc new feature alpha "Alpha" >/dev/null && test -f .sdlc/messages/AGENTS.md && test ! -e .sdlc/tickets/messages`
- `R=$PWD && t=$(mktemp -d) && T="$R/plugins/sdlc-lite/scripts/tickets.py" && mkdir "$t/a" "$t/b" && git -C "$t/a" init -q && git -C "$t/b" init -q && (cd "$t/a" && python3 "$T" --root .sdlc roadmap >/dev/null && test -d .sdlc/messages) && cd "$t/b" && mkdir .sdlc && printf '<!-- sdlc-lite:managed:start v1 sha256:000000000000 -->\nno end\n' > .sdlc/AGENTS.md && ! python3 "$T" --root .sdlc roadmap >/dev/null 2>&1 && test ! -e .sdlc/messages`
- `R=$PWD && t=$(mktemp -d) && git -C "$t" init -q && cd "$t" && T="$R/plugins/sdlc-lite/scripts/tickets.py" && python3 "$T" --root .sdlc new feature alpha "Alpha" >/dev/null && test -d .sdlc/messages && rm -r .sdlc/messages && python3 "$T" --root .sdlc check >/dev/null`
- `python3 -c "import ast; d = ast.get_docstring(ast.parse(open('plugins/sdlc-lite/scripts/tickets.py').read())); assert 'messages/AGENTS.md' in d and 'write_entries' in d"`
- `grep -F "Mailbox:" .sdlc/AGENTS.md | grep -qF "messages/AGENTS.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check >/dev/null`
- `grep -qF "mailbox entry files" plugins/sdlc-lite/skills/ticket/SKILL.md`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `git diff "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/tickets.py plugins/sdlc-lite/skills/ticket/SKILL.md | grep '^+' | { ! grep -qF "$(printf '\342\200\224')"; }`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/(messages|tickets)\.py|plugins/sdlc-lite/skills/ticket/SKILL\.md" | { ! grep -q .; }`
