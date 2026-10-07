---
name: clarify
description: "Sharpen a vague or overloaded ask into an executable one (root goal, deltas, scoped do with a done-condition) and write it into the task handoff. An ask that already states its scope and done-condition passes through in one line. Use for \"what are they actually asking for\", \"is this ask scoped\", or before /plan on a fuzzy request. NOT for a greenfield design with most decisions unmade (/grill); NOT for splitting scoped work into parts (/decompose)."
argument-hint: "<ask | handoff.md>"
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

Minimize questions: resolve what defaults settle, ask only what changes the output.

## 0. Gate
- No ask → ask "what's the request?" and stop.
- The ask already states its scope and a done-condition → reply `already scoped: <ask>, done = <condition>` and stop. That is the ideal outcome, not a skipped step.

## 1. Extract
1. Literal ask, near-verbatim.
2. Root goal in one sentence: the outcome that counts as success, and for whom.
3. Deltas between ask and goal: wrong unit for the goal, ambiguity, conflict, unstated assumption, missing done-condition, hidden scope. Name each.
4. Sort each delta:
   - Resolve: a convention, the codebase, or this conversation settles it. State the assumption so it can be corrected.
   - Ask: it changes the output and cannot be defaulted.

## 2. Resolve the Ask items
- A person is present: one AskUserQuestion round, 1 to 4 questions, 2 to 4 concrete options each, recommendation first. Never drip questions across turns.
- Unattended (headless, /chain in a script): never block. Record each as `(gap: <what is missing>; default: <what was assumed>)` and proceed on the default.

## 3. Write it down
Put the result in the task handoff (create `.sdlc/<slug>/handoff.md` per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md` if none exists):

```
## Goal
<root goal>

## Intent
Literal ask: <near-verbatim>
Deltas:
- <delta>: <defaulted: assumption | answered: choice | gap: what is missing; default: X>
Do: <what to actually do, scoped>
Non-goals: <what is out>
Done when: <checkable condition>
```

Reply with the handoff path and the Do / Done when lines.

Done when: executing Do exactly would produce Goal, every delta is defaulted, answered, or a named gap, and (interactive) the user has seen the read-back.
