## Task goal
`tickets.py` can use a `tickets/` ticket root under `.sdlc/` when `<root>/config` says `ticket_root: tickets`, and `tickets.py roadmap` keeps a managed router block in `.sdlc/AGENTS.md` current, so an agent reads one short file and opens only the tickets in the stage it needs.

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
