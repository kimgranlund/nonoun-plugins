# Live probe, T-0368 (2026-10-08, maintainer session)

Throwaway repo, scripts from this lane. Steps and observed output:

1. `dispatch.py prepare scout L1 .sdlc/probe/handoff.md --routing-reason "prune live probe"` printed name `probe-scout-L1`, prompt first line `probe | scout L1` (T-0363 style), and `"prune": true`.
2. `Agent` spawn with exactly that JSON (haiku). The spawn gate accepted the title-first prompt. The agent finished and showed `idle` in ListAgents.
3. `dispatch.py record ... --transcript <agent transcript>` printed `prune: probe-scout-L1`.
4. `dispatch.py prune` printed `TaskStop task_id=probe-scout-L1    # scout L1, recorded 2026-10-08T17:44:37.714525+00:00; then: dispatch.py prune --done probe-scout-L1`.
5. `TaskStop task_id=probe-scout-L1` returned "Successfully stopped task".
6. ListAgents afterwards no longer listed probe-scout-L1.
7. `dispatch.py prune --done probe-scout-L1` emptied the queue (`dispatch.py prune` printed nothing).

Note: the scout did not write its result file; `record --transcript` took the report from the transcript, which is the 0.21.2 fix working. Not observed: a hook stopping agents on its own (not claimed).
