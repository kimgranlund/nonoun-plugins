<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, cases 22 to 24: pass. Evidence: ran it in the worktree, rc=0, last line `fanout selftest: PASS`. Bite proof: a copy of the built fanout.py with two mutations (`'isolation': 'worktree'` to `'none'`; the `land_ticket` rev-list compare `== '0'` to `== '-1'`) gave rc=1 with three red assertions (case 22 dispatch isolation, case 23 `no changes`, case 23 `--ticket` branch). Case 24 stayed green under the land mutation, so it exercises the `run` stub path (`--driver true` gives `| alpha | T-0001 | no changes |`), which is what Done-when bullet 3 asks.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass. Evidence: rc=0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`; the item 24 guard carries the new phrases and negative controls.
- `python3 scripts/check-packaging.py` exits 0: pass. Evidence: rc=0, `PASS: catalog parity, identity, skill routes, hook isolation and context links`.
- `git diff --check` exits 0: pass. Evidence: rc=0, no output.
- `grep -q 'fanout.py land' ... && grep -q 'Tree: <path>' ...` documents the parent-driven full lane: pass. Evidence: rc=0 on the built tree; red at base (rc=1 for both patterns against the base SKILL.md).
- `git check-ignore -q .claude/worktrees/x` exits 0: pass. Evidence: rc=0 on the built tree; red at base (a temp repo holding the base `.gitignore` gives rc=1 for `.claude/worktrees/x` and rc=0 for the `.worktrees/x` control).
- Done when, prep (bullet 1): pass. Case 22 asserts the lane line per ticket with tier, the dispatch JSON (`name T-0001-solo`, `subagent_type sdlc-lite:solo-S`, `model sonnet`, `isolation worktree`, `branch worktree-T-0001-solo`), the brief carrying the commit instruction `T-0001: Ticket t1` and no `Never commit`, a verifier command for tier M only, a land command per ticket, nothing created, and the parity loop (planned-scope overlap, uncommitted handoff, `--max-lanes 1`, one id in two lanes, unknown id: `run` and `prep` both exit 2 with equal stderr).
- Done when, land (bullet 2): pass. Case 23 asserts the merge and `close T-0001` commits on the integration branch, `red: false rc=1` with the tip unchanged and the ticket still ready, `gate vacuous` then `--allow-empty-gate` merges, `no changes`, tier M `no verifier result`, `verifier fail`, then `merged`, and the report `Lane for` and tier lines. The merge reuses `merge_gate_close`; the only edit there is a `ctx.get('land')` guarded `record_solo_lane` call.
- Done when, stub path unchanged (bullet 3): pass. The selftest hunk is pure addition; the shared-path edits are the `resolve_lanes_dir` and `refuse_overlap` extractions and the guarded call. Cases 1 to 21 pass in the same run; case 24 covers the no-commit stub.
- Done when, full-chain docs (bullet 4): pass. SKILL.md `## Sub-agent lanes` step 5 and docs/maintenance/sdlc-internals.md document it; the headless conductor per lane stays the `run` default.
- Constraints: no em dash in any added line (0 found); no branch or worktree added.
- Steelman, dropped: `land` of a `full` branch with no filer file gives `merged, close refused: no filer-L*.md` and no selftest case lands a full branch through close. No criterion names that case, and SKILL.md routes the filer before `land`. Not filed.

## Out of scope changes
- .gitignore: one line, required by the `.claude/worktrees/` criterion.
- plugins/sdlc-lite/AGENTS.md: adds `.claude/worktrees/` to the watcher-exclusion rule the new lane dir needs.
- plugins/sdlc-lite/scripts/solo_run.py: docstring only, replaces `until T-0285`, which this step made stale (`solo_run.py selftest` rc=0).
- plugins/sdlc-lite/scripts/check.py: item 24 guard update for the new entry points with its negative controls.
- .sdlc/0285-fanout-subagent/handoff.md: a new `## Acceptance criteria` block, additions only.
- Untracked runner artifacts in the ticket dir: `base-sha`, `skips.md`, `verifier-L3.attempt.json`, `verifier-L3.dispatch.json`.

## For the next attempt
None
