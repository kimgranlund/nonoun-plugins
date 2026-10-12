---
name: clarify
description: "Sharpen a vague or overloaded ask into an executable one (root goal, deltas, scoped do with a done-condition) and write it into the task handoff. An ask that already states its scope and done-condition passes through in one line. Use for \"what are they actually asking for\", \"is this ask scoped\", or before /plan on a fuzzy request. NOT for a greenfield design with most decisions unmade (/grill); NOT for splitting scoped work into parts (/decompose)."
argument-hint: "<ask | handoff.md>"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

The output is a plan-ready intent: a task handoff that `/plan`, `steps.py`, and `plan_check.py` accept without a rewrite. Ask a question only when its answer changes the lane, the level, the cost, or an irreversible action. Default everything else and state the default.

## 0. Gate
- No ask: ask "what's the request?" and stop.
- A follow-up that points at session state ("any updates", "do that", "go on"): reply with one line, `follow-up: <what it points at>`, answer it from the board and run records, and run no extraction.
- The ask already states its scope and a done-condition: reply with one line, `already scoped: <ask>, done = <condition>`, and stop. That is the ideal outcome, not a skipped step.

A changed ask means a re-run of clarify on the new ask, not a patch of the old block.

## 1. Extract
1. Literal ask, near-verbatim.
2. Root goal in one sentence: the outcome that counts as success, and for whom.
3. Deltas between ask and goal: wrong unit for the goal, ambiguity, conflict with a repo rule, unstated assumption, missing done-condition, hidden scope. Name each.
4. Sort each delta:
   - Resolve: a convention, the codebase, or this conversation settles it. State the assumption so it can be corrected.
   - Ask: the answer changes the lane, the level, the cost, or an irreversible action, and no default is safe.

## 2. Size and lane
Estimate the level, L1 to L4, from the one level scale in `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`: the lowest row that fits every signal. L1 and L2 take the solo lane, L3 and L4 the full chain. Cost is that row's ticket budget ($5, $30, $60, or "ask the user" at L4). Reversible is yes unless the work deletes data, rewrites history, publishes, or changes a shared contract that others already read.

Once the ticket handoff exists, its front matter `size:` holds the same level. Confirm the lane with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lane <task dir>`, which reads that `size:`. When it prints another lane (`lean`, or `full` for a sticky skip), write the lane it printed.

## 3. Resolve the Ask items
- A person is present: one AskUserQuestion round, 1 to 4 questions, 2 to 4 concrete options each, recommendation first. Never drip questions across turns.
- Unattended (headless, /chain in a script): never block. Record each as `(gap: <what is missing>; default: <what was assumed>)` and proceed on the default.

## 4. Tracker
Before any lane, branch, or worktree, the work has a ticket: no ticket, no lane; no merge, no close.
- Use the tracker the repo already has: local `.sdlc` tickets, GitHub Issues (a GitHub remote), or Linear (a Linear config). Never create a second tracker. With none, use local `.sdlc` tickets.
- Claim the existing ticket for this ask, or create one when none exists. A local claim sets `status: claimed` and `claimed_by: <who> <date>` in the front matter (create with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc new <type> <slug> "<title>"`). On GitHub or Linear the claim is the assignee, set through the repo's own CLI or tool; when none is present, say `ticket not updated: <why>`.
- One lane per ticket. A new idea found here becomes a new ticket, not a larger one.
- A ticket closes only after its work is merged, with a one-line result and a link to the commit or PR.

## 5. Write it down
Put the result in the task handoff (create `.sdlc/<slug>/handoff.md` per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md` if none exists):

```
## Goal
<root goal, one or two sentences>

## Intent
Literal ask: <near-verbatim>
Level: L<n> (lane: <solo|lean|full>; cost: <one line>; reversible: <yes|no, why>)
Deltas:
- <delta>: <defaulted: assumption | answered: choice | (gap: what is missing; default: X)>
Do: <what to actually do, scoped>
Non-goals: <what is out of scope>
Done when:
- `<runnable command>` exits 0
- unverifiable: <why no command can decide it>
- [owner: maintainer] <a check only the maintainer can run>
Verify: `<the one command that best proves Done when>`

## Context
<pointers: paths, tickets, decisions a clean-context agent needs>

## Constraints
<what must not change, limits; "None" if none>
```

Done when is the definition of done:
- Every item is a backticked runnable command or the literal `unverifiable: <why>`.
- Move an item to `[owner: maintainer]` when it reads its own step's verifier result, pins a fixed sha (use `$SDLC_BASE_SHA` instead), or needs a live run that a verifier cannot do.

Multi-step work (more than one ticket, or a plan doc) also gets a `## Outcome` section after `## Intent`, with the four parts `Outcome:`, `Measured by:`, `Rubric:`, and `Negative control:` as defined in `${CLAUDE_PLUGIN_ROOT}/skills/plan-verification/references/outcome-block.md`. For a plan doc, the front block follows `${CLAUDE_PLUGIN_ROOT}/skills/plan-doc/references/plan-doc-format.md`.

Then lint the block with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py clarify --file <handoff>`, fix each FAIL, and run it again until it exits 0.

Reply with the handoff path and the Level, Do, and Done when lines.

## Low tier
For a low-effort model (Sonnet low, Haiku), follow these three steps in order and nothing else:
1. Extract. Copy the ask into `Literal ask:`. Write the Goal as the outcome in one sentence. List each delta from section 1.
2. Default. Give every delta a default instead of a question:
   - no done-condition: the selftest or check script of the file the Do changes;
   - no level signal: L2, solo lane;
   - an item needing a live run: `[owner: maintainer]`;
   - two readings: the smaller change, the other one in Non-goals;
   - anything else unsettled: `(gap: <what>; default: <the smallest safe choice>)`.
   Ask a question only when no default is safe for an irreversible action.
3. Write. Fill the section 5 template, run the `plan_check.py clarify` lint, and fix each FAIL.

## Eval cases
`evals/README.md` lists eight asks from this repo's history with the output each should produce, and how to replay them.

Done when: executing Do exactly would produce Goal, every delta is defaulted, answered, or a named gap, the `plan_check.py clarify` lint exits 0, and (interactive) the user has seen the read-back.
