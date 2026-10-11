---
name: run-plan
description: "Run an approved plan doc to completion unattended: preflight, then loop plan_done.py, dispatch each open step through fanout.py prep and land, follow steps.py next, and stop with state written when a script says stop. Built for a smaller driver model that follows exit codes and carries no judgment. Use for \"/goal complete build and verify <plan-doc.md>\" or \"run this plan doc\". NOT for writing the plan (plan-doc), a goal with no plan doc (plan-goal), or one ticket (solo)."
argument-hint: "<plan-doc.md>"
allowed-tools: Read, Grep, Glob, Bash, Agent, SendMessage
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. The sub-agent dispatch below (`fanout.py prep`, an `Agent` spawn, `dispatch.py record`) has no Codex counterpart: use the Codex runner line and native exchange there, and say that the plan run on Codex is unverified. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS` (the path of the plan doc).

You are the driver. You route by exit codes and run printed commands; you do not judge, grade or improvise. Read the plan doc, then read [the run rules](references/run-rules.md) in full and follow them step by step. Nothing else is read by default.

1. Print `SDLC_ROLE` and `SDLC_HEADLESS` (`printenv SDLC_ROLE SDLC_HEADLESS`). Unattended means never `AskUserQuestion`. If `SDLC_ROLE` is empty, say once that the publish hook does not guard this session and treat every command outside the plan's Authorization as a stop.
2. Preflight, once per session: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py plan --file <plan-doc.md> --run` must exit 0, then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py --root .sdlc check`, then `dispatch.py recover` and `status` for each step folder that exists (run-rules, Preflight).
3. Loop: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_done.py <plan-doc.md>` and print its output as it is. Exit 0 or 4: stop and report. Exit 2: stop, plan defect. Exit 1: take the first open item and work it with the run rules, then loop.
4. When a script says stop (exit 2, 4 or 5 of `dispatch.py prepare`, a second replan, a spend limit, a merge conflict, inherited red), run `plan_done.py stop <plan-doc.md> --reason "<the script's words>"` and end. Never retry, never guess, never invent a budget ack.

You edit no product file. A verifier is a separate sub-agent started only by the printed dispatch; you never choose its model or level and never grade a step yourself.
