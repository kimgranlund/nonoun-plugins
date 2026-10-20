# Lean chain

Detail for the chain skill's `## Lean chain` section.

Lean conditions (all hold): a ticket of level L1 or L2; planner L1 or L2; at most two steps, each at builder L1 to L3; no merge step; no replan; and the change stays within one nearest `AGENTS.md` owner, or one script and its tests, with no change to a contract other roles parse (role output sections, level tables, `steps.py`, `tickets.py` invariants, hooks).

The full chain is mandatory when any of these holds: any step at L4 or L5; an `unresolved:` assumption; the ticket changes role behavior, a runner invariant, a hook, or a check (its focused live run is still required); or a step touches shared generated state (roadmap, router, generated Codex agents) alongside other tickets in flight. A lean task that meets any of these is on the full chain from that point. Work already done stays valid.

What lean means: the planner follows the Coarse steps rule in `${CLAUDE_PLUGIN_ROOT}/agents/planner.md`. Plan review is for plans with an L4 or L5 step only (`steps.py review`); a lean plan has none, so the planner's open readiness concerns go to the builder as `## Notes`. Each step gets one verifier, and lean never skips a role that `steps.py review` or `steps.py next` asks for.

What the code computes: `steps.py lane <task dir>` prints `solo`, `lean`, or `full` from these conditions, one `reason:` line per deciding fact, and appends each result to the task's `skips.md`; `steps.py lint` warns on step and criterion counts.
