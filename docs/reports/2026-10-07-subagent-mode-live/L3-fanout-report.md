# fanout report

- Run: `fanout-1b2834e08e54`
- Integration branch: `fanout/live` at `3475f308c452870c79d547ad53178308ed205d60` (reused)
- Integration worktree: `/private/tmp/sdlcprobe/proj/.worktrees/fanout/integration`
- Lane `agent-acf61a22dc619fd24`: external branch `worktree-agent-acf61a22dc619fd24` at `8fad0bc741475ea3c5c456298d26392860c942b9`
- Lane `agent-ab4b159bcba10b564`: external branch `worktree-agent-ab4b159bcba10b564` at `b2b2c415dd8c9c1cbc91dd72baef410673126eac`
- Gate 1: `python3 -m unittest discover -s tests -t .`
- Logs: `/private/tmp/sdlcprobe/proj/.worktrees/fanout/logs`
- Overlap: none
- Lane for `T-0004`: full
- Lane for `T-0005`: full

| Lane | Ticket | Outcome | Commit |
|---|---|---|---|
| agent-acf61a22dc619fd24 | T-0004 | merged, close refused: 0004-slugify: no filer-L*.md in .sdlc/0004-slugify; run /file on the task first; nothing written | 2d071f4 |
| agent-ab4b159bcba10b564 | T-0005 | merged, close refused: 0005-titlecase: no filer-L*.md in .sdlc/0005-titlecase; run /file on the task first; nothing written | 3475f30 |
