Manifest: .sdlc/0182-idle-host-watcher-design/review/decompose/manifest-v1.json (technical-architecture · default) · coverage_check: clean
Quadrant: load-bearing structurally; three needs are hosted in name only (a10, a15, a16)
Outside-in: the design's ten sections are the nodes. s2 lacks sleep and permission columns; s8 repeats s4's wrong Codex flag.
Inside-out: 16 needs derived from the ticket Context and the mechanics, not from the section list. a10 (judge a wake by mailbox progress), a15 (wake the host the user left), a16 (worktree roots for mailbox, lock, sandbox) have a section to live in but no text that satisfies them. a2 and a5 rest on a flag `codex exec resume` rejects and on an env var that arms no publish hook.
Hand-off: review report (architect-L1.md); no /plan

Note: the handoff Context line `Decomposition: decompose/report.md` was not added because this role is read-only outside decompose/.
