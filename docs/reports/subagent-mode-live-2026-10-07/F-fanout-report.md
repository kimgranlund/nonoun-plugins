# fanout report

- Run: `fanout-4fa4437d1b89`
- Integration branch: `fanout/final` at `fad24e8b9074c025281ec370917ea8ab4ac51bc6` (reused)
- Integration worktree: `/private/tmp/sdlcfin2/proj/.worktrees/fanout/integration`
- Lane `agent-a2a547eb68291d1b8`: external branch `worktree-agent-a2a547eb68291d1b8` at `e7815af4f5dd9490a76234d765a99f19d5ccd6a9`
- Lane `agent-a2ee016865091989b`: external branch `worktree-agent-a2ee016865091989b` at `6d3dd8f13f38eb35af2f87a73abaf45cf1a95e3f`
- Gate 1: `python3 -m unittest discover -s tests -t .`
- Logs: `/private/tmp/sdlcfin2/proj/.worktrees/fanout/logs`
- Overlap: none
- Lane for `T-0001`: solo (tier M: sonnet xhigh)
- Lane for `T-0002`: solo (tier S: sonnet low)

| Lane | Ticket | Outcome | Commit |
|---|---|---|---|
| agent-a2a547eb68291d1b8 | T-0001 | merged | ab26077 |
| agent-a2ee016865091989b | T-0002 | merged | 90bcb87 |
