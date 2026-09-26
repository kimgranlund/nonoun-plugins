## Task goal
A stopped chain never blocks the next sync.

## Step 2: Document where stopped work lands
level: L1
### Do
Update the docs to match Step 1, with no em dashes:
- `plugins/sdlc-lite/scripts/fanout.py` module docstring, the `run` section: on step 2 (driver non-zero exit) and on any outcome other than `merged`, a dirty lane tree is committed as `wip(<id>): <outcome>` on the lane branch only. It is never merged, and the report's Commit cell shows `wip <sha>`. Before each sync, a dirty lane tree is WIP-committed first. Replace "the tree left as is".
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: one sentence near the top saying the same, with the literal `wip(<id>): <outcome>`. Also say to inspect a stopped lane's `wip(` commit on its lane branch.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: one sentence saying a /chain run under fanout that stops mid-step leaves its work as a `wip(<id>): <outcome>` commit that fanout.py makes on the lane branch. A plain /chain outside fanout commits nothing and never commits on main.
- `CLAUDE.md`, the `scripts/fanout.py` bullet under Layout: add the `wip(<id>): <outcome>` lane commit on a stop and before a dirty sync, never merged, sha in the report. `.claude/agents/sdlc-lite-author.md` does not restate the stop behavior (it only says to keep them in sync), so leave it unless the builder finds a restatement.

`check.sh` takes about 11 minutes, longer than the 300s guard timeout, so it is a plain final criterion here, not a `(guard)`.
### Acceptance criteria
- `python3 -c 'import ast,sys; d=ast.get_docstring(ast.parse(open("plugins/sdlc-lite/scripts/fanout.py").read())); sys.exit(0 if "wip(<id>): <outcome>" in d else 1)'`
- `grep -qF 'wip(<id>): <outcome>' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `grep -qF 'wip(<id>)' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF 'wip(<id>): <outcome>' CLAUDE.md`
- `! git diff HEAD -- CLAUDE.md plugins/sdlc-lite/skills/fanout/SKILL.md plugins/sdlc-lite/skills/chain/SKILL.md plugins/sdlc-lite/scripts/fanout.py | grep -q '^+.*—'`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- `plugins/sdlc-lite/scripts/check.sh` exits 0.
