---
id: T-0548
title: "A role's Bash call that reads stdin (bare cat > file) hangs the run with no timeout"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A role's Bash call that waits on stdin cannot stall a run for long: the call fails fast, or the run reports the stall, instead of hanging silently.

## Repro
1. In a headless role run (`claude -p`, fanout lane), have the role run `cat > /tmp/x; python3 - <<'EOF' ... EOF`.
2. `cat` reads the inherited stdin, which never closes, so the run waits with no output.

## Expected
The command gets a closed stdin (`< /dev/null`) or a timeout, or a watchdog reports the run stalled.

## Actual
T-0543 step 2 builder (wave 70, 2026-10-14) sat 39 minutes on `cat > /tmp/x` (pid 99957) until the maintainer killed it; the transcript showed no writes from 04:43 to 05:23.

## Context
Builder L4 sub-agent of the conductor in `.worktrees/fanout70/d`. Guess: headless `claude -p` lanes run with an open stdin pipe; a fix might start lane drivers with `stdin=DEVNULL` in `fanout.py`/`solo_run.py`, or add a stall line to the lane monitor.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
- (red) For a role (`SDLC_ROLE=builder`), the new PreToolUse(Bash) hook rewrites a command so a bare `cat` gets end of input while the caller's stdin stays open: `python3 -c "import json,os,subprocess as s;i=json.dumps({'tool_name':'Bash','tool_input':{'command':'cat > /dev/null; echo ok','timeout':600000}});o=json.loads(s.run(['bash','plugins/sdlc-lite/hooks/close-role-stdin.sh'],input=i,capture_output=True,text=True,env=dict(os.environ,SDLC_ROLE='builder')).stdout);u=o['hookSpecificOutput']['updatedInput'];assert u['timeout']==600000;r,w=os.pipe();p=s.Popen(['bash','-c',u['command']],stdin=r,stdout=s.PIPE,text=True);assert p.communicate(timeout=10)[0].strip()=='ok'"` exits 0.
- With no role (`SDLC_ROLE`, `SDLC_HEADLESS` unset, no `agent_type`) the hook prints nothing and exits 0, and `bash plugins/sdlc-lite/scripts/hook-selftest.sh` covers both cases and passes.
- `adapters/claude/hooks.json` registers the hook under the Bash matcher; `python3 scripts/check-packaging.py` passes.
- `docs/references/claude-hooks.md` has a section for the hook stating it is Claude only; `git diff --check` passes.

## Outcome

2026-10-14 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: the claim in the docs section that Claude Code drops its own `< /dev/null` when a command holds a heredoc rests on `docs/reports/2026-10-14-role-bash-stdin-probe.md`, which I did not rerun (no live model call); no criterion names it. | note: no `builder-*.md` exists in the artifacts dir; the verdict rests on the tree, not a builder claim (solo lane).) · verifier: verifier-L2 (sonnet) · base: ab94588622d9
- Changed: see commits
- Commits: b93e735 T-0548: A role's Bash call that reads stdin (bare cat > file) hangs the run with no timeout
- Check: 1 (red) role hook rewrites a bare `cat` onto closed input while the caller's stdin stays open: pass
- Check: 2 no role prints nothing, exit 0, selftest covers both cases and passes: pass
- Check: 3 hooks.json registers the hook under the Bash matcher, check-packaging passes: pass
- Check: 4 claude-hooks.md has a section stating Claude only, `git diff --check` passes: pass
