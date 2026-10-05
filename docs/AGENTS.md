# Documentation

Read [the index](README.md) for the full list. Pick the folder for the task; read one file, not the folder.

| Folder or file | Holds | Read it for |
|---|---|---|
| `maintenance/` | Implementation references: [runner and ticket internals](maintenance/sdlc-internals.md), [Claude hooks](maintenance/claude-hooks.md) | Changing runner, ticket, board, fanout, or hook behavior |
| `lean-sdlc/` | The lane, solo, and cost-control designs | Why the default lane is `solo` and how cost is controlled |
| `ticket-stages/` | The `.sdlc` router, ticket root, mailbox, and watcher designs | Changing `.sdlc/` layout, messages, or the supervisor |
| `repo-onboarding/` | Entry-file and docs-layout design for adopting repositories | Changing `onboard.py` or its templates |
| `generative-constructs/` | Progressive Context specifications | Changing the Progressive Context plugin |
| `codex-role-execution.md`, `plugin-compatibility.md`, `readiness-recovery-validation.md` | Host execution, packaging, and recovery references | Codex adapter, marketplace packaging, run recovery |
| `validation/` | Dated live-run, review, and release evidence | Checking what was actually verified; these are history, not instructions |
| `other/` | Source notes and questions | Only when asked |

Rules for documents here:

- Put dated evidence in its own file under `validation/`; do not add it to an entry file.
- Keep one authoritative location per fact and link to it.
- Add a new document to [the index](README.md) in the same change.
