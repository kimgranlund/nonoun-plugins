<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/fanout.py: docstring now says a dirty lane tree is committed as `wip(<id>): <outcome>` on the lane branch only, never merged, with `wip <sha>` in the report's Commit cell, and is WIP-committed before each sync. This replaces "the tree left as is".
- plugins/sdlc-lite/skills/fanout/SKILL.md: added one sentence with the `wip(<id>): <outcome>` commit, and to inspect a stopped lane's `wip(` commit on its lane branch.
- plugins/sdlc-lite/skills/chain/SKILL.md: added a sentence saying a /chain run under fanout leaves its work as a `wip(<id>): <outcome>` commit that fanout.py makes on the lane branch. A plain /chain outside fanout commits nothing and never commits on main.
- CLAUDE.md: the `scripts/fanout.py` bullet under Layout now covers the wip lane commit on a stop and before a dirty sync, never merged, sha in the report.

## Checks
- The four content criteria (docstring, fanout SKILL, chain SKILL, CLAUDE.md) and the no-em-dash diff check passed, chained in one command that printed `ok`.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0.

## Notes
`.claude/agents/sdlc-lite-author.md` only says to keep the docs in sync and does not restate the stop behavior, so I left it alone.
