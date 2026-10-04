
**User Question**

- In Claude Code: what is the only orchestration-model approach that will beat regular single-session mode in economy, speed, and quality of task completion?

**Fable Response**

The premise is wrong as stated: nothing beats single-session mode on all three axes unconditionally. Any orchestration layer adds tokens (the orchestrator's context plus every worker's context plus the handoff text), so on economy it starts behind and has to earn its way back. The one pattern that can come out ahead on economy, speed, *and* quality is narrow and conditional, so it's worth being precise about what it is and why.

The rate-limiting factor in a single long session is context: as the window fills with file dumps, tool output, and dead ends, every subsequent token costs more (prompt cache misses, re-reads, larger prefixes) and quality degrades (attention diluted across stale material, the model forgetting earlier decisions). Orchestration wins only when it attacks that factor directly.

The pattern that does: a thin orchestrator that holds the task spec and the decisions, and delegates *context-heavy, independent* work to short-lived subagents that return conclusions rather than raw material. Concretely, the orchestrator never reads twenty files to find something; it sends an Explore-style read-only agent that reads them and returns three lines. It never runs a long build-and-fix loop in its own context; it sends a worker with a tight contract (files to touch, test command, done criterion) and gets back a diff plus a pass/fail. Independent pieces go out in parallel in one message.

Why that can beat single-session on all three:

- Economy: the orchestrator's prompt stays small and stable, so cache hit rate stays high across its whole run, and the expensive reading happens once in a disposable context instead of persisting in a growing one. Workers can also run on a cheaper model when the subtask is mechanical.
- Speed: parallelism across independent subtasks, plus no slowdown from a bloated context.
- Quality: the decision-maker always sees the spec and the summaries, never a window of debris; each worker starts fresh with exactly the context its task needs.

The conditions that make this hold, and where it flips negative: subtasks must be independent enough to parallelize or at least isolate; the handoff contract must be typed and explicit (fuzzy delegation is where most of the economy evaporates, because workers wander and the orchestrator has to re-litigate); and the task must be big enough that context bloat would have bitten. For a focused change in two files, single-session wins on all three axes and orchestration is pure overhead.

What's known vs inferred here: the context-cost mechanics (cache behavior, attention degradation with length) are well established. That this specific thin-orchestrator/fat-worker shape is the one that can win on all three is an inference from those mechanics plus how Claude Code's Agent tool is structured; I'm not aware of a published benchmark from Anthropic that ranks orchestration modes on these three axes, so treat "only" as my claim, not a documented one.