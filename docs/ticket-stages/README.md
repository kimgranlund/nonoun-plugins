# Ticket stages and message bus

Built: Option A (the router), the opt-in `tickets/` root, and the message bus with its `messenger` agent (T-0175, T-0177, T-0178, T-0179). Stage folders remain a proposal.

- [Design](design.md): stage folders, the `.sdlc/AGENTS.md` router, claim and close procedures, and a cross-harness message bus.
- [Idle-host watcher design](watcher-design.md): proposed external process that resumes an idle host when a message arrives, with its safety limits and validation plan.
