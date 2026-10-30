# Numbered records across worktrees (ADR numbers)

Sibling worktrees each see only their own tree. Two lanes that each take "the next ADR number" from their own folder take the same one, and nothing notices until the merge (one repository's T-0012 and T-0014 both took ADR-0235). `tickets.py new` avoids this for ticket ids; SDLC ships no allocator for ADRs or any other numbered record, because the numbering scheme and its folder belong to the consumer repository. A repository that numbers ADRs owns the rule, and this is the minimum it should state:

- The next number is the highest across every `git worktree list` tree and the integration branch, plus one. A scan of the current tree alone is not enough.
- If the repository has an allocator script, a handoff and a plan call it. If not, the factory picks the number from that tree-wide view before a lane starts and writes it into the ticket's `## Context` as `ADR number: NNNN`; the plan and builder use that number and never pick one.
- A plan step never says "the next ADR number". It names the number, or names the allocator.
- A repository check that fails on a duplicate number in the ADR folder catches a clash that slipped past, the way `tickets.py check` does for ticket ids.
