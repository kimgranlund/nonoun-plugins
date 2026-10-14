---
name: grill
description: "Derive the load-bearing design decisions for a greenfield system, component family, or feature whose decision space is mostly unmade, in grounded, cascading AskUserQuestion rounds until it settles, then write the ratified design to the task. Use for \"grill me on the design\", \"nothing is decided yet\", \"what do we need to decide\". NOT for sharpening one given ask (/clarify); NOT for splitting settled work into parts (/decompose)."
argument-hint: "<topic|handoff.md>"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(git log:*), Bash(git show:*), AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

## Arguments

| Argument | Meaning | Default | Example |
|---|---|---|---|
| `<topic\|handoff.md>` | What is being designed, or the task handoff that names it | - | `a plugin settings page` |

/clarify minimizes questions for one ask. /grill derives the questions a mostly-unmade design implies. Same closed-question discipline, opposite posture. Depth: `references/foundations.md`, `references/best-practices.md`; score the result with `references/rubric.md`.

## The two axes
Derive forks from both, every round. One axis alone is self-confirming.
- Structural [S] (whole to part): scope and breadth, the consumer, the element set, composition and nesting, placement and phasing.
- Mechanism [M] (part to whole): load-bearing technical mechanisms, capabilities, semantics, platform primitives, fidelity and density.

## Method
1. Frame: name what is being designed and why it is open. Sketch a few open forks per axis. No questions yet.
2. Rank the forks by leverage (the answer cascades into other decisions) and damage (a wrong default hurts). Round 1 = the top 2 [S] + top 2 [M].
3. Ground every option before asking: read the codebase, catalogs, tokens, and constraints so each option is concrete, with a recommendation and its tradeoff. A user-named exemplar is a hypothesis: read it and classify it as an instance of the pattern or an instance of the gap before building a fork on it.
4. Ask one full AskUserQuestion batch per round: recommendation first, written "(Recommended) X, tradeoff: Y". Then re-derive: each answer closes some forks and opens others. Re-rank and ask the next round. Never drip single questions.
5. Stop at convergence: every remaining fork is defaultable without cascading, or will be settled by /decompose or /plan anyway. Default those (stated) and synthesize. Rounds past convergence waste the user's attention.

## Write it down
Create the task handoff `.sdlc/<slug>/handoff.md` first if none exists. Write `design.md` in the task's records dir (the path `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/order.py records-dir .sdlc/<slug>` prints; git ignores it) and add `Design: <records dir>/design.md` under the handoff's Context, so the handoff stays the one committed record:

```
## Decision space
<what and why it is open>

## Decisions
- [S|M] <fork>: <choice>. Cascade: <what it opened or closed>

## Grounding
- <codebase / catalog / constraint fact the options were built on>

## Deferred
- <fork>: default <X>, left to <decompose | plan>

## Ratified design
Structure: <scope, element set, composition, phasing>
Mechanisms: <primitives, semantics, fidelity>
```

A ratified design is write-once. When a constraint or the scope shifts, re-grill the affected forks into a new design file; never patch the old one.

Done when: decisions exist on both axes, every option was grounded, every deferred fork carries a default, and /decompose could run from design.md without another round.
