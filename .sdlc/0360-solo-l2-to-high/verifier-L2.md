<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- T0360-1: pass. Evidence: `grep '"solo"' plugins/sdlc-lite/adapters/claude/levels.json` prints `"solo": {"L1": ["sonnet", "low"], "L2": ["sonnet", "high"], "L3": ["opus", "xhigh"]}`. `git diff HEAD --stat -- .../levels.json .../codex/models.json` lists only levels.json, 1 insertion and 1 deletion. The diff is the single solo row line, with only L2 `xhigh` changed to `high`. models.json is unchanged.
- T0360-2: pass. Evidence: run in the Tree: `check.py` rc=0 (`ok: 19 role levels, 9 agents, 22 generated definitions checked`), `claude_roles.py generate --check` rc=0 (`verified (22 files)`), `codex_roles.py generate --check` rc=0, `run-selftest.sh` rc=0 (`run selftest: PASS`), `evals.py check` rc=0 (`ok (5 evals, lock cites .sdlc/evals/0004-solo-l2-high.md)`), `tickets.py --root .sdlc check` rc=0 (closed-ticket placeholder and layout warnings only). Changed dependents also pass: `fanout.py selftest` PASS, `solo_run.py selftest` PASS, `evals.py selftest` PASS.
- T0360-3: pass. Evidence:
  - The eval: `.sdlc/evals/0004-solo-l2-high.md` (untracked, new) has the front matter role solo, level L2, model sonnet, effort high, host claude, the exact Intent task_set, pass_rate 13/13, and evidence listing both sweep reports. Its `## Result` begins "High matched xhigh on every verdict (zero disagreements) at 29 to 39 percent of the cost".
  - The lock: the Tree lock is `{"eval": ".sdlc/evals/0004-solo-l2-high.md", "previous_eval": ".sdlc/evals/0002-haiku-5-5.md", "table_sha256": "2dcd093b..."}`, the same sha as HEAD.
  - Written by `evals.py lock`: in a throwaway copy I restored the HEAD lock and ran `evals.py lock --eval .sdlc/evals/0004-solo-l2-high.md`, which printed `locked ... (table sha256 2dcd093b...)`. `cmp` against the Tree lock gave IDENTICAL.
  - The date: the eval is dated 2026-10-08 and the record says that is the UTC date. Confirmed with `date -u`: Thu Oct 8 04:20 UTC, while local time was Oct 7 21:20 PDT.
- T0360-4: pass. Evidence, all in a throwaway rsync copy under the tmp prefix:
  - Lock moved aside: `evals.py check` exits 1 with `.sdlc/evals/table-lock.json: missing; add an eval, then run evals.py lock --eval <file>`. `check.py` exits 1 with `FAIL evals: .sdlc/evals/table-lock.json: missing...`.
  - Lock restored (`cmp` identical): both exit 0.
  - builder L1 set to `["opus","low"]` in a plugin copy: `evals.py --plugin ../pc check` exits 1 with `model table changed: sha256 5b7b5ac1... is not the locked 2dcd093b...`.
  - solo L2 set back to `["sonnet", "xhigh"]`: `evals.py check` stays ok (solo is excluded from the hash), and `check.py` exits 1 with `FAIL solo: adapters/claude/levels.json solo levels are not {... 'L2': ['sonnet', 'high'] ...}`.
- T0360-5: pass. Evidence:
  - First grep: `git grep -n -E "Sonnet xhigh|sonnet xhigh" -- . ':!docs/reports' ':!docs/other' ':!.sdlc'` prints only `docs/README.md:90`, the dated T-0216 live-run line. The same grep at HEAD gives 30 lines, so the check bites.
  - Second grep: `git grep -n -E "'L2': \('sonnet', 'xhigh'" -- plugins` prints nothing (rc=1). It gave 4 lines at HEAD.
  - Each required file says Sonnet high for L2, checked with grep:
    - solo.md:28
    - solo-L1.md:30
    - solo-L2.md:30
    - solo-L3.md:30
    - level-rubric/SKILL.md:29
    - sdlc-internals.md:132
    - solo-lane-contract.md:20
  - `agents/solo-L2.md` front matter has `effort: high`.
  - run.sh has no solo row (`grep -n -i solo run.sh` finds only comments), so it needed no change.
- T0360-6: pass. Evidence:
  - `git diff HEAD --name-only` lists:
    - the handoff
    - table-lock.json
    - three doc files: subagent-mode.md, sdlc-internals.md, solo-lane-contract.md
    - levels.json
    - 8 generated Codex TOMLs
    - solo.md and solo-L1/L2/L3.md
    - check.py, fanout.py, solo_run.py
    - the level rubric

    Plus the untracked eval 0004.
  - Codex TOMLs: a word diff shows each one changes only `xhigh` to `high`, in text that embeds the solo table or the rubric. `codex_roles.py generate --check` passes on them.
  - Dashes: the dash-count command prints 0, and the untracked eval holds 0 dashes. The counter is not vacuous: fed a fixture line `+a—b`, it prints 1.

## Out of scope changes
None. The handoff diff adds only the `## Acceptance criteria` section, which T0360-6 allows. `docs/planning/sdlc-lite/subagent-mode.md` is the third doc line T0360-6 names: its diff changes only the solo L2 effort sentence. The planner and plan-reviewer Codex TOMLs are regenerated output of the rubric change; `codex_roles.py generate --check` passes on them. Steelman of one possible finding: the Result says "29 to 39 percent" while the sweep costs give 28.6 and 30.6 percent. The handoff's Intent dictates that wording, so the builder followed the spec and I dropped the finding.

## For the next attempt
None
