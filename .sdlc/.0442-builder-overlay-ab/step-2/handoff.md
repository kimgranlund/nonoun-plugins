## Task goal
A dated report with a keep, extend or drop verdict backed by priced runs.

## Step 2: Run the replay A/B, write the report and the eval, gates green
level: L3
guard timeout: 30
### Read first
- `docs/reports/AGENTS.md`
- `.sdlc/evals/AGENTS.md`
### Do
Depends on: step 1. The design is the Proof paragraph and the drop rules in `.sdlc/.0440-per-tier-agent-prompts/architect-L1.md`. Read it first. This step changes no overlay, agent, adapter or script (non-goal). A `drop` verdict is recorded only: deleting the overlay and regenerating is a follow-up ticket, not this step. Do not change any model or effort.

**1. Arm roots.** Both arms are detached worktrees of this repo at HEAD, under `$SDLC_TMP_WORKTREES`: `armB` and `armA`.
- In `armA`, overwrite `plugins/sdlc-lite/agents/builder-L1.md` and `builder-L5.md` with `git show 00735e20^:<path>`. `00735e20` is the T-0441 overlay commit.
- This is valid because `git diff --stat 00735e20^ HEAD -- plugins/sdlc-lite/agents/builder.md` is empty, and the builder definition preloads no skills (frontmatter has only name, description, model, effort). The two arms therefore differ only by the `## At this level` section.
- Confirm that with `diff` between the two roots' `builder-L1.md`, and the same for `builder-L5.md`.
- Do not use a worktree at `00735e20^` as arm A. That commit also differs in `agents/conductor.md` and in five skills.

**2. Preflight per arm root.** Run one Haiku `claude -p --plugin-dir <root> --model haiku --output-format stream-json --verbose` call with a one-word prompt. Read its init event and confirm that the `sdlc-lite` plugin path it loaded is under `<root>`. If the init event cannot show that, stop with Status blocked: `question: which plugin root does a headless --plugin-dir session load when sdlc-lite is also installed inline?`

**3. Cells.** The tasks are `subagent-tool-names`, `figma-stale-skip-report` and `command-modal-footer`. A cell is (task, level, arm, rep). Run cells in this order:
1. L1, rep 1, all three tasks.
2. L1, rep 2, all three tasks.
3. L5, rep 1, then rep 2, in the order `subagent-tool-names`, `figma-stale-skip-report`, `command-modal-footer`.

Run each (task, level, rep) as an A and B pair, A first on rep 1 and B first on rep 2, so a budget stop never leaves half a pair.

**4. Spend target.** Keep a running Spend: the sum of the priced `cost_usd` of every replay builder and verifier row. Archived costs: builder L1 $0.38 to $0.46, verifier about $0.43 to $0.57 (`bench/results/2026-09-27-*/step-*/runs.jsonl`). Before each pair, estimate its cost as twice the costliest same-level builder plus verifier seen so far, or $8 for the first L5 pair. Start the pair only if Spend plus that estimate stays at or under $10. The other roughly $5 of the $15 ticket budget covers this lane's own planner, builder and verifier. Mark a level with no completed pair `unverified`.

**5. One cell.**
- Create a fresh `git -C <repo> worktree add --detach "$SDLC_TMP_WORKTREES/ab-<task>-<level>-<arm>-<rep>" <base>` and run the task's `setup` there.
- Copy `plugins/sdlc-lite/bench/results/2026-09-27-<task>/step-1/handoff.md` to `<worktree>/.sdlc/ab-<task>/step-1/handoff.md`. `prepare` points the Tree line at the worktree itself, as in the Method of `docs/reports/2026-10-07-verifier-l2-replay.md`.
- Run `python3 <armB>/plugins/sdlc-lite/scripts/dispatch.py prepare builder <L1|L5> <that handoff> --routing-reason "T-0442 overlay A/B arm <A|B>"`.
- Run the dispatch headless from the cell worktree: `SDLC_HEADLESS=1 SDLC_ROLE=builder claude -p --plugin-dir <arm root> --agent sdlc-lite:builder-<level> --model <dispatch model> --effort <dispatch effort> --dangerously-skip-permissions --output-format json "<dispatch prompt>"`. This is the established role pattern, `claude -p --agent sdlc-lite:<role>`, at `plugins/sdlc-lite/scripts/fanout.py:75` and `:462`.
- Price the run with `dispatch.py record <dispatch.json> --transcript <the session jsonl named by the JSON session_id under ~/.claude/projects/> --duration-ms <duration_ms>`. Transcript pricing is described at `dispatch.py:88-90`.
- Then run one verifier the same way: `prepare verifier <L1 for an L1 build, L3 for an L5 build>`, with the `armB` root for both arms (verifier definitions are byte-identical) and the model that `prepare` prints. There is no rebuild, bump or retry for any cell.
- Grade by step 4 of `plugins/sdlc-lite/skills/bench/SKILL.md`: copy `test_paths` from `tests_from`, then run `check`.
  - For `command-modal-footer`, whose archived plan has 4 steps, the step-1 replay cannot pass the full hidden check by construction. Record its `hidden_check` as `n/a`; first-pass there is the verifier verdict alone.
- Measures:
  - `cost_usd`: the builder row; verifier cost goes in its own column.
  - Builder and verifier minutes: each attempt record's `finished_at` minus `started_at`.
  - `blocked`: builder Status blocked.
  - First pass: the hidden check passes (or is `n/a`) and the first verifier passes.
- Leave cell worktrees under the prefix. Never delete them.

**6. Verdict.** Apply the design's drop rules per overlay:
- The L1 overlay is dropped if its blocked rate is not below arm A's, or any task's first-pass rate falls, or cost rises more than 10 percent.
- The L5 overlay is dropped unless its cost per closed step is at least 15 percent under arm A's at equal or better first-pass rate.
- Any hidden-check regression drops that overlay outright.

Derive the overall result as follows:
- `Verdict: extend`: no overlay run is dropped, and every run overlay meets its keep threshold in both reps.
- `Verdict: drop`: every overlay that ran is dropped.
- `Verdict: keep`: any other outcome.

`Null at this sample size: yes` unless every rule outcome is the same in both reps of its level.

**7. Report.** Write `docs/reports/<YYYY-MM-DD>-builder-overlay-ab.md`, named as `docs/reports/AGENTS.md` says. It holds:
- These exact lines: `Verdict: <keep|extend|drop>`, `L1 overlay: <keep|drop|unverified>`, `L5 overlay: <keep|drop|unverified>`, `Null at this sample size: <yes|no>`, `Spend: <n> USD`. Spend is the replay rows only, with two decimals.
- A per-run table with exactly this header: `| task | level | arm | rep | cost_usd | builder_min | blocked | hidden_check | verifier | verifier_cost_usd | verifier_min |`. `blocked` is `yes` or `no`; `hidden_check` is `pass`, `fail` or `n/a`; `verifier` is `pass` or `fail`.
- A Method section with the arm construction, the preflight evidence and the commands.
- A `## Raw rows` fenced jsonl block holding every replay `runs.jsonl` row.
- A not-run section that names `button-geometry-model` and `svelte-icon-component` with the step-1 evidence, plus any cell skipped for budget, all marked unverified.

**8. Eval.** Run `python3 plugins/sdlc-lite/scripts/evals.py add` with:
- role `builder`, level `all`, model `all`, effort `all`, host `claude`
- task_set `bench step-1 replay, 3 of 5 tasks, overlay vs none`
- pass_rate: arm B passes over arm B runs, where a pass is the hidden check (or the verifier for an `n/a` task)
- cost_usd: Spend
- evidence: the report path
- Method and Result text taken from the report

Do not pin the number: `evals.py add` picks the next free one, 0005 at plan time.

**9. Gates.** Run `evals.py check`, `check.py`, `scripts/check-packaging.py` and `git diff --check`, and fix any red this step introduced. This step does not prove that the overlays change behavior beyond the rows it ran.
### Acceptance criteria
- (red) `f=$(ls docs/reports/*-builder-overlay-ab.md) && grep -qE "^Verdict: (keep|extend|drop)$" "$f" && grep -qE "^L1 overlay: (keep|drop|unverified)$" "$f" && grep -qE "^L5 overlay: (keep|drop|unverified)$" "$f" && grep -qE "^Null at this sample size: (yes|no)$" "$f"`
- (red) `f=$(ls docs/reports/*-builder-overlay-ab.md) && grep -qxF "| task | level | arm | rep | cost_usd | builder_min | blocked | hidden_check | verifier | verifier_cost_usd | verifier_min |" "$f"`
- (red) `f=$(ls docs/reports/*-builder-overlay-ab.md) && a=$(grep -cE "^\| [a-z-]+ \| L[15] \| A \| [12] \| [0-9.]+ \|" "$f"); b=$(grep -cE "^\| [a-z-]+ \| L[15] \| B \| [12] \| [0-9.]+ \|" "$f"); test "$a" -ge 1 && test "$a" -eq "$b"`
- (red) `f=$(ls docs/reports/*-builder-overlay-ab.md) && awk -F'|' '/^Spend: [0-9.]+ USD$/{split($0,w," "); s=w[2]} /^\| [a-z-]+ \| L[15] \| [AB] \|/{t+=$6+$11} END{d=s-t; if(d<0)d=-d; exit !(s!="" && s<=15 && d<=0.05)}' "$f"`
- (red) `f=$(ls docs/reports/*-builder-overlay-ab.md) && grep -qF button-geometry-model "$f" && grep -qF svelte-icon-component "$f" && grep -qF "## Raw rows" "$f"`
- (red) `f=$(ls .sdlc/evals/[0-9][0-9][0-9][0-9]-builder-overlays.md) && test "$(printf "%s\n" "$f" | wc -l)" -eq 1 && grep -qx "role: builder" "$f" && grep -qx "host: claude" "$f" && grep -qE "^evidence: .*docs/reports/[0-9]{4}-[0-9]{2}-[0-9]{2}-builder-overlay-ab\.md" "$f"`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/overlays plugins/sdlc-lite/agents plugins/sdlc-lite/adapters plugins/sdlc-lite/scripts && test -z "$(git ls-files --others --exclude-standard -- plugins/sdlc-lite/overlays plugins/sdlc-lite/agents plugins/sdlc-lite/adapters)"`
- (guard) `python3 -c 'import subprocess,sys,re; a=subprocess.run(["git","diff","--name-only",sys.argv[1],"--",".",":(exclude).sdlc"],capture_output=True,text=True).stdout.split(); b=subprocess.run(["git","ls-files","--others","--exclude-standard","--",".",":(exclude).sdlc"],capture_output=True,text=True).stdout.split(); ok=re.compile(r"plugins/sdlc-lite/bench/tasks/(subagent-tool-names|figma-stale-skip-report|command-modal-footer)\.md|docs/reports/\d{4}-\d{2}-\d{2}-builder-overlay-ab\.md"); bad=[p for p in a+b if not ok.fullmatch(p)]; print(bad); sys.exit(1 if bad else 0)' "$SDLC_BASE_SHA"`
- (guard) `python3 plugins/sdlc-lite/scripts/evals.py check`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA"`

### Notes
- This session runs with `SDLC_ROLE=conductor` and no `SDLC_TMP_WORKTREES`, so `hooks/block-stray-worktree.sh` denies every git worktree-add command (the planner and the step-1 verifier both hit it). Build the arm roots and the cell trees as `git clone --shared` copies under your dispatch tmp prefix instead (`git clone --shared <repo> <dir> && git -C <dir> checkout --detach <sha>`); a clone keeps every sha the bench task names. Record this substitution in the report's Method section.
- `prepare` in a cell tree reads that tree's own `.sdlc`; if a gate refuses there (lane, goal, spec), record the refusal text in the report and take the smallest documented override, never a model or effort change.
