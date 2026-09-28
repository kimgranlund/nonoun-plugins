<!-- role=planner level=L2 model=opus effort=medium -->
I ran the criteria against the current tree and confirmed each is red for the right reason; writing the plan now.

## Goal
Add an opt-in `fanout.py run --rewrite-refs` that passes `--rewrite-refs` through to `tickets.py close`, puts every rewritten file in the `close <id>` commit, and shows the flag in the dry-run plan and in the refusal outcome. /fanout offers the flag at its Confirm step in numbered-mode repos, and the docs describe it.

## Step 1: fanout.py --rewrite-refs passthrough, staging, plan line, refusal hint, selftest
level: L2
### Do
All changes are in `plugins/sdlc-lite/scripts/fanout.py`. `tickets.py` does not change.
- **argparse (`main`)**: add `--rewrite-refs` (store_true). Its help text says it is opt-in, numbered mode only, and rewrites files outside the ticket folder that cite `<rel>/NNNN-<slug>` to `<rel>/.NNNN-<slug>` when the ticket closes. Without the flag, such a close is refused. Add the flag to the usage line in `main` and to the module docstring (the usage line and run step 4).
- **ctx (`preflight`)**: carry `rewrite_refs` and `numbered = tickets.config_numbered(root)`.
- **`print_plan`**: print one `close:` line, choosing from these three:
  - flag given: `close: tickets.py close <slug> --rewrite-refs (files citing a ticket folder are rewritten to its .NNNN-<slug> path)`
  - no flag, numbered mode: `close: tickets.py close <slug> (numbered folders: a file citing a ticket folder refuses the close; --rewrite-refs rewrites them)`
  - no flag, plain mode: `close: tickets.py close <slug>`
- **`run_ticket` close call**:
  - Append `--rewrite-refs` to the `tickets.py close` argv when `ctx['rewrite_refs']` is set.
  - On a refusal, when the flag was not given and the refusal text (stderr or stdout) contains `--rewrite-refs`, append `; fanout.py run --rewrite-refs rewrites them` to the `merged, close refused: <first line>` outcome.
- **`close <id>` commit staging**: stage `rel` plus every path the close itself changed outside `rel`. Snapshot `git status --porcelain` before the close and diff it with the snapshot after; do not parse tickets.py's `rewrote refs in` text. Never run `git add -A` over the whole integration worktree, so leftovers from a gate are never swept into the commit.
- **selftest, new case 4**: build a numbered-mode throwaway repo with `.sdlc/config` = `ticket_folders: numbered`, a `0001-x` ticket, `.worktrees/` in `.gitignore`, and `docs/spec.md` citing `.sdlc/0001-x/handoff.md`. Use a stub driver that writes `filer-L1.md` with Warnings None and makes one change. The case asserts:
  - Without the flag: rc 1, the report row reads `merged, close refused` and names `--rewrite-refs`, the ticket is still `0001-x` with status ready on the integration branch, and the integration worktree is clean.
  - With the flag, on a fresh repo: the row reads `merged`, the tip commit is `close T-0001` and changes `docs/spec.md` to the dot path, `.sdlc/.0001-x/handoff.md` exists on the branch, and the integration worktree is clean.
  - The dry-run plan's `close:` line matches each mode.
- Update the selftest docstring paragraph to match.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/fanout.py run --help | grep -q -- --rewrite-refs`
- With the flag, the ticket closes and the rewrite lands in the `close` commit: `(F="$PWD/plugins/sdlc-lite/scripts/fanout.py" && d=$(mktemp -d) && git init -q -b main "$d/r" && cd "$d/r" && git config user.email t@t && git config user.name t && git config commit.gpgsign false && mkdir -p .sdlc/0001-x docs && printf 'ticket_folders: numbered\n' > .sdlc/config && printf -- '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n' > .sdlc/0001-x/handoff.md && printf 'see .sdlc/0001-x/handoff.md\n' > docs/spec.md && printf '.worktrees/\n' > .gitignore && git add -A && git commit -qm fixture && python3 "$F" run a=T-0001 --integration fanout/t --rewrite-refs --driver 'printf "## Warnings\nNone\n\n## Follow-ups\nNone\n" > "$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"; echo x > x.txt' > "$d/out.txt" 2>&1 && grep -q '| a | T-0001 | merged |' .worktrees/fanout/report.md && git log -1 --format=%s fanout/t | grep -qx 'close T-0001' && git show fanout/t:docs/spec.md | grep -qx 'see .sdlc/.0001-x/handoff.md' && git diff --name-only fanout/t~1 fanout/t | grep -qx docs/spec.md && git cat-file -e fanout/t:.sdlc/.0001-x/handoff.md && test -z "$(git -C .worktrees/fanout/integration status --porcelain)")`
- Without the flag, the close is still refused, the outcome names the flag, and nothing is rewritten: `(F="$PWD/plugins/sdlc-lite/scripts/fanout.py" && d=$(mktemp -d) && git init -q -b main "$d/r" && cd "$d/r" && git config user.email t@t && git config user.name t && git config commit.gpgsign false && mkdir -p .sdlc/0001-x docs && printf 'ticket_folders: numbered\n' > .sdlc/config && printf -- '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n' > .sdlc/0001-x/handoff.md && printf 'see .sdlc/0001-x/handoff.md\n' > docs/spec.md && printf '.worktrees/\n' > .gitignore && git add -A && git commit -qm fixture && { python3 "$F" run a=T-0001 --integration fanout/t --driver 'printf "## Warnings\nNone\n\n## Follow-ups\nNone\n" > "$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"; echo x > x.txt' > "$d/out.txt" 2>&1; test $? -eq 1; } && grep -q '| a | T-0001 | merged, close refused: .*--rewrite-refs' .worktrees/fanout/report.md && git show fanout/t:.sdlc/0001-x/handoff.md | grep -q '^status: ready' && git show fanout/t:docs/spec.md | grep -qx 'see .sdlc/0001-x/handoff.md' && test -z "$(git -C .worktrees/fanout/integration status --porcelain)")`
- The dry-run plan shows the flag: `(F="$PWD/plugins/sdlc-lite/scripts/fanout.py" && d=$(mktemp -d) && git init -q -b main "$d/r" && cd "$d/r" && git config user.email t@t && git config user.name t && git config commit.gpgsign false && mkdir -p .sdlc/0001-x && printf 'ticket_folders: numbered\n' > .sdlc/config && printf -- '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n' > .sdlc/0001-x/handoff.md && printf '.worktrees/\n' > .gitignore && git add -A && git commit -qm fixture && python3 "$F" run a=T-0001 --dry-run --rewrite-refs > "$d/with.txt" && grep -q '^close: tickets.py close <slug> --rewrite-refs' "$d/with.txt" && test ! -e .worktrees)`
- Without the flag in numbered mode, the dry-run plan names the refusal and the flag: `(F="$PWD/plugins/sdlc-lite/scripts/fanout.py" && d=$(mktemp -d) && git init -q -b main "$d/r" && cd "$d/r" && git config user.email t@t && git config user.name t && git config commit.gpgsign false && mkdir -p .sdlc/0001-x && printf 'ticket_folders: numbered\n' > .sdlc/config && printf -- '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n' > .sdlc/0001-x/handoff.md && printf '.worktrees/\n' > .gitignore && git add -A && git commit -qm fixture && python3 "$F" run a=T-0001 --dry-run > "$d/without.txt" && grep -q '^close: tickets.py close <slug> (numbered folders' "$d/without.txt" && test ! -e .worktrees)`
- The selftest holds a numbered-mode case: `grep -q "ticket_folders: numbered" plugins/sdlc-lite/scripts/fanout.py`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/tickets.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Step 2: Document the flag in /fanout, CLAUDE.md, and the author agent
level: L1
### Do
- **`plugins/sdlc-lite/skills/fanout/SKILL.md`**:
  - Add `[--rewrite-refs]` to `argument-hint`.
  - Step 1 (Dry run): the plan's `close:` line shows whether the repo is in numbered mode.
  - Step 2 (Confirm): when the plan's `close:` line says `numbered folders`, add `--rewrite-refs` as a separate AskUserQuestion choice. The choice text says it rewrites files that cite a closed ticket's folder to its `.NNNN-<slug>` path. It is never added without the user picking it (T-0113 decision). Step 3 then runs with the flag only if the user picked it.
  - Mention that a `merged, close refused` outcome naming `--rewrite-refs` means a citing file blocked the close.
- **`CLAUDE.md`**, in the `scripts/fanout.py` Layout bullet:
  - Add `[--rewrite-refs]` to the usage.
  - Add one sentence: `--rewrite-refs` (opt-in, numbered mode) passes the flag to `tickets.py close`, and the `close <id>` commit stages every file the close rewrote. Without it, a citing file gives `merged, close refused: ...` with a hint naming the flag. The dry run's `close:` line shows the mode.
- **`.claude/agents/sdlc-lite-author.md`**: add the same fact on a line that mentions fanout, for example beside the existing "Keep `scripts/fanout.py`, the /fanout skill ... in sync" line.
### Acceptance criteria
- `sed -n '/^## 2. Confirm/,/^## 3/p' plugins/sdlc-lite/skills/fanout/SKILL.md | grep -q -- --rewrite-refs`
- `grep '^argument-hint:' plugins/sdlc-lite/skills/fanout/SKILL.md | grep -q -- --rewrite-refs`
- `grep '^- .scripts/fanout.py.:' CLAUDE.md | grep -q -- --rewrite-refs`
- `grep -n 'fanout' .claude/agents/sdlc-lite-author.md | grep -q -- --rewrite-refs`
- Observable: SKILL.md step 2 presents `--rewrite-refs` as a user-selectable choice, only in numbered mode, and never adds it without the user's pick.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- The step 1 end-to-end criteria run a real `fanout.py run` in a `mktemp -d` repo outside the tree, with a stub driver and no model call. They depend on the user's global git config not breaking `git init -b main` or commits in a fresh repo; `commit.gpgsign` is already forced off.
- The staging snapshot approach can miss a rewritten file that was already dirty before the close. A fresh integration worktree after green gates makes that unlikely, but a gate that modifies a tracked file could cause it.
- `check.py` may guard the fanout docs' wording (the interactive vs headless words). The step 2 edits must keep those words, and the step 2 `check.sh` guard catches it if they don't.
