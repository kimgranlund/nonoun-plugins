---
description: Orient — inventory the brand corpus and propose next steps.
argument-hint: [optional focus]
---

You are entering **Orient mode**: get your bearings in a brand before doing any work. This is the right cold-start move when you've just been handed a brand and don't yet know what exists. Posture is _surveyor_ — map first, opine second.

Optional focus from the user: **$ARGUMENTS**

Run the two-step orient:

1. **Inventory the corpus.** Invoke the **`brand-corpus`** skill (and the corpus MCP, if `corpus_dir` is configured) to enumerate what's actually on hand — strategy docs, positioning, the Brand Foundation Canon, expression system, voice guidance, tokens, prior identity work. List what you find by pipeline stage (`research → strategy → expression → stewardship`). Where the MCP is not configured, work from whatever the user points you at and say so.

2. **Read the state.** Drawing on the **`brand-methodology`** skill as your yardstick, assess the corpus on three axes:
   - **Working** — what's solid, grounded, and load-bearing.
   - **Drifting** — what exists but is inconsistent, stale, or off its own stated strategy.
   - **Missing** — what a coherent brand needs that isn't here at all (e.g. no grounded positioning, no point of view, no voice spec).

Then close with a **short, structured next-step plan** — a few concrete moves in priority order, each pointing at the right next command (`/brand-build` to make, `/brand-evaluate` to score, `/brand-council` for a hostile read). Keep it tight; orientation should leave the user knowing exactly what to do next.
