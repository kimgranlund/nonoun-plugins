---
id: T-0549
title: "Role Bash calls avoid bash -c on built strings, so the host stops asking for approval under bypass"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Role sub-agents stop triggering Claude Code's built-in "This shell -c script runs rm and could not be checked" approval, which asks even under bypass permissions.

## Intent
- Do: add one rule to the shared role command guidance (the place every role reads it, e.g. `skills/handoff-format` or the agent contracts `claude_roles.py` generates from): run each check as a plain command, and never pass a built string to `bash -c "$var"`, `sh -c`, or `eval`. A helper like `run(){ bash -c "$2"; }` is exactly the pattern to avoid. When a criterion is itself a shell string, run it as written in its own call.
- Do: a live probe in a throwaway project under a bypassing parent: the old pattern prompts, and the new guidance produces a run with no prompt.
- Non-goals: `bypassPermissions` or `permissionMode` in any shipped agent (the user always runs bypass, and the parent mode already wins); changing a user's settings.
- Done when: the rule is in the role guidance, `claude_roles.py generate --check` and `check.sh` pass, and the live probe shows the prompt before and none after.

## Context
Maintainer report 2026-10-14, with a screenshot from the maison `0535-planner-L3-4` agent. The command defined `run(){ out=$(bash -c "$2" 2>&1); ... }` and passed criteria strings into it, along with `sed -i` and `git worktree add`. The host showed "This shell -c script runs rm and could not be checked. Do you want to proceed?" while the user ran bypass permissions. That text is not from an sdlc-lite hook (grep of `plugins/sdlc-lite/hooks/` finds none), so it is Claude Code's own check on a `bash -c` script whose content it cannot read. Inherited plan mode is ruled out: the user always runs bypass, and under a bypassing parent the sub-agent's mode does not apply (docs/references/claude-hooks.md, probe P1).

## Constraints
Wording only, plus the probe; no hook that rewrites commands.

## Acceptance criteria
- `grep -c 'Run each check as a plain command' plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md plugins/sdlc-lite/agents/solo.md` prints 1 for each file.
- `! grep -n 'one .bash -c. per criterion' plugins/sdlc-lite/agents/*.md plugins/sdlc-lite/adapters/codex/agents/*.toml` exits 0 (the planner no longer tells roles to wrap criteria in `bash -c`).
- `grep -c 'Never wrap a criterion in' plugins/sdlc-lite/agents/planner.md` prints 1.
- `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- No added line in the diff holds an em dash, and no `bypassPermissions` or `permissionMode` appears in any shipped agent file.
- Live probe (manual, recorded in the solo report): a sub-agent under a bypassing headless parent following the new rule runs criteria as plain commands with no approval and no permission denial.

## Outcome

2026-10-14 · lane: solo L2 · verdict: pass · verifier: verifier-L2 (sonnet) · base: ab94588622d9
- Changed: see commits
- Commits: 33a506f T-0549: Role Bash calls avoid bash -c on built strings, so the host stops asking for approval under bypass
- Check: 1 grep -c 'Run each check as a plain command' builder.md verifier.md solo.md prints 1 each: pass
- Check: 2 `! grep -n 'one .bash -c. per criterion' agents/*.md adapters/codex/agents/*.toml` exits 0: pass
- Check: 3 grep -c 'Never wrap a criterion in' planner.md prints 1: pass
- Check: 4 `claude_roles.py generate --check` exits 0: pass
- Check: 5 `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass
- Check: 6 No added em dash; no `bypassPermissions` or `permissionMode` in shipped agent files: pass
- Check: 7 Live probe, new rule, no approval and no denial: pass
- Follow-up: note: The probe cannot go red headlessly -> notes.md
- Follow-up: note: The probe's sub-agent was given the rule in its prompt, not loaded... -> notes.md
- Follow-up: note: check.sh took 42 minutes under host load load average 40 to 55 and... -> notes.md
