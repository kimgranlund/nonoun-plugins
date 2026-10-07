# fanout report

- Run: `fanout-28ed32cb403e`
- Integration branch: `fanout/final` at `a990f1e216abf09a064bc9c69fd847ad96c3114c` (reused)
- Integration worktree: `/private/tmp/sdlcfin3/proj/.worktrees/fanout/integration`
- Lane `agent-a0e93a1c8c3259297`: external branch `worktree-agent-a0e93a1c8c3259297` at `7668c74d16ed9694ce5cfa36e4872eb5c711cfd8`
- Lane `agent-aaf91ebf3f99edab7`: external branch `worktree-agent-aaf91ebf3f99edab7` at `ee16bc9a190e8c521e186974f531f26f2ca569ac`
- Gate 1: `python3 -m unittest discover -s tests -t .`
- Logs: `/private/tmp/sdlcfin3/proj/.worktrees/fanout/logs`
- Overlap: none
- Lane for `T-0001`: solo (tier M: sonnet xhigh)
- Lane for `T-0002`: solo (tier S: sonnet low)

| Lane | Ticket | Outcome | Commit |
|---|---|---|---|
| agent-a0e93a1c8c3259297 | T-0001 | merged | 31f0ded |
| agent-aaf91ebf3f99edab7 | T-0002 | merged | 6151e5e |
