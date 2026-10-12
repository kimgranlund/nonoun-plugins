## Task goal
A dated report with a keep, extend or drop verdict for the builder overlays from a replay on tasks that make builders block, and at least one priced L5 pair.

## Step 1: Run the overlay retest replay, write the report, gates green
level: L3
### Read first
- `docs/reports/AGENTS.md`
- `.sdlc/AGENTS.md`
### Do
Depends on: none. This step is a near copy of step 2 of `.sdlc/.0442-builder-overlay-ab/planner-L2.md` (items 1 to 7: arm roots, preflight, cells, spend, one cell, verdict, report). Read that step and the Method section of `docs/reports/2026-10-11-builder-overlay-ab.md` first and follow them, except for what this Do changes below. Non-goals: no edit to any overlay, agent, adapter, skill or script; no model or effort change; no eval entry. A `drop` verdict is recorded only.

Path forms in this Do: a file in another repository is written as an absolute path. A file that exists only at a base commit is written in git object form, `<sha>:<path>`, read with `git -C <repo> show <sha>:<path>`, and appears in the cell at that relative path after the checkout. A path inside a cell is written as `<cell>/<path>`. None of these resolve against this tree, so the `links` gate of `prepare` does not read them as citations of this repository.

**1. Arm roots: unchanged from T-0442.** Use `git clone --shared` copies under `$SDLC_TMP_WORKTREES`, as T-0442's Method did (its hook denial of the worktree form is recorded there).
- `armB` is this repo at HEAD.
- `armA` is the same, with `plugins/sdlc-lite/agents/builder-L1.md` and `builder-L5.md` overwritten from `git show 00735e20^:<path>`.
- This is still valid. `git diff --stat 00735e20^ HEAD -- plugins/sdlc-lite/agents/builder.md` is empty (planner probe), and `git log` shows `00735e20` as the last commit to touch `builder-L1.md` and `overlays/builder.md`.
- Confirm that `diff` of each file between the roots shows exactly one hunk, and that the hunk is the `## At this level` section (lines 35 to 55 in L1, 35 to 52 in L5).

**2. Preflight.** Run T-0442's Haiku `--plugin-dir` preflight for each arm root from inside one cell of each repo: agent-ui, ultimate-tokens, and an sdlc-lite clone. An sdlc-lite cell carries its own old `plugins/sdlc-lite` and `.claude/` settings, which T-0442 never tested. If the init event shows more than one `sdlc-lite` plugin, or a path outside the arm root, stop with Status blocked: `question: which plugin root does a headless --plugin-dir session load inside a cell that is itself an sdlc-lite checkout?`

**3. Tasks (settled here).** Each task has a repo, a base sha and a source handoff, all present on this machine (planner probe: `git cat-file -t <base>` printed `commit` for each, and `git cat-file -t` printed `blob` for each git object handoff below):
- `rts-step10`, source `blocked note`.
  - Repo `/Users/kimgranlund/Projects/nonoun/agent-ui`, base `0e18b7086906ff7359698a043cbe486c0c980495`, setup `npm ci`.
  - Handoff: copy `/Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/response-type-selection/step-10/handoff.md` to the same relative path in the cell. It is not tracked at base.
  - Original: builder L2 blocked, `plan defect:` a `(red)` criterion already green at base.
- `ndc-step2`, source `blocked note`.
  - Repo `/Users/kimgranlund/Projects/nonoun/ultimate-tokens`, base `7f05eb50d6d33dec5de2557d91c8fcd107e7a2e4`, setup `npm ci`.
  - Handoff: the git object `7f05eb50d6d33dec5de2557d91c8fcd107e7a2e4:.sdlc/native-dom-charts/step-2/handoff.md` in that repo (its working copy is `/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc/native-dom-charts/step-2/handoff.md`). It is tracked at base together with the task's architect and planner files, so the checkout puts it in the cell and the cell's `links` gate resolves its cited paths there.
  - Original: builder L3 blocked ($3.41), `plan defect:` the scope guard excludes `scripts/bundle.mjs`.
- `t0368`, source `non-pass`.
  - Repo `/Users/kimgranlund/Projects/nonoun/sdlc-lite` (main checkout), base `6a14c1658afa9715ad2695c6c35b2cda44be5bfc`, handoff the git object `6a14c1658afa9715ad2695c6c35b2cda44be5bfc:.sdlc/0368-prune-flag/handoff.md` (tracked at base, so the checkout puts it in the cell).
  - Hidden check: `grep -q "dispatch.py prune" plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -q "dispatch.py prune" plugins/sdlc-lite/skills/fanout/SKILL.md`. Planner probe: 0 matches in each file at base, 1 each at merge `bc5d3871`.
- `t0373`, source `non-pass`.
  - Same repo, base `687d169e100f5a28cf9e3e6ca5b63cdc22b30b4b`, handoff the git object `687d169e100f5a28cf9e3e6ca5b63cdc22b30b4b:.sdlc/0373-codex-role-preflight/handoff.md`.
  - Hidden check: `grep -qi "readiness and resume" plugins/sdlc-lite/agents/solo.md && grep -qi "readiness and resume" plugins/sdlc-lite/skills/agent/SKILL.md`. Planner probe: 0 matches at base, 1 each at merge `c25ad66a`.
- `t0378`, source `non-pass`.
  - Same repo, base `b599114e2746e41bc227910242d988ef64cbdfe0`, handoff the git object `b599114e2746e41bc227910242d988ef64cbdfe0:.sdlc/0378-red-checkpoint-builder/handoff.md`.
  - Hidden check: the criterion span the first verifier failed. `python3 plugins/sdlc-lite/scripts/redck.py selftest` must print both `ok: a handoff changed after the original checkpoint` and `ok: an unbound control` (`.sdlc/.0378-red-checkpoint-builder/verifier-L2.md` in the main checkout).
  - Before any cell, show in a scratch clone that this check is red at the wip commit `a8b39893` and green at merge `e1fa6e04`.

Per-task preflight, before the task's first cell:
- For `rts-step10` and `ndc-step2`, compare the `sha256` of the cell handoff with `handoff_sha256` of the blocked builder row in the source step's `runs.jsonl`. A mismatch is noted in the run log and the report; it does not stop the task.
- If a cell step dir already holds a builder or verifier result at base, or a gate in `prepare` refuses with anything other than the lane gate below, drop that task. Replace it with the fallback `gci-step4`: ultimate-tokens base `40bcf50b364e6834d80e049638111a1b7a367bd7`, with `/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc/geometry-compound-insets/step-4.superseded-1/handoff.md` (on disk only, not tracked at base) copied into the cell as `<cell>/.sdlc/geometry-compound-insets/step-4/handoff.md`, `blocked note` (stale red criterion). Record the reason under Not run.

Hidden check for the two `blocked note` tasks, and for any run that blocked: `n/a`. A step whose plan carries a real defect has no correct build to grade. For those tasks, record instead whether the block names the same defect as the original note.

**4. Gates that T-0442 never hit.**
- The three sdlc-lite handoffs are L2 solo-lane tickets. `prepare builder` on them refuses with exit 5 at the lane gate (`plugins/sdlc-lite/scripts/dispatch.py:703-711`). Run `prepare` for those cells with `SDLC_LANE_OVERRIDE="T-0458 overlay retest: replay a solo ticket as one builder step"`.
- The `links` gate (`dispatch.py:696-700`) runs `steps.py lint` only on `step-<n>` dirs. Run `python3 <armB>/plugins/sdlc-lite/scripts/steps.py lint <cell step dir>` before `prepare`, and if it refuses, record the refusal as the drop reason.

**5. Order and spend.** The replay target is $14 of the $20 cap. The rest is for this lane's planner, this builder session and its verifier. Run pairs in this order, A first on rep 1 and B first on rep 2:
1. L1 rep 1 `rts-step10`. It is the cheapest and proves the machinery.
2. L5 rep 1 `ndc-step2`. It is the costliest original builder among the chosen tasks; the `match-peer-lightness` L5 original cost $39.24 and fits no budget.
3. L1 rep 1 `ndc-step2`, `t0368`, `t0373`, `t0378`.
4. L1 rep 2 in the same task order.

There is no L5 rep 2. Before each pair, estimate its cost as twice the costliest same-level builder plus verifier seen so far, or $2.00 for the first L1 pair and $8.00 for the L5 pair. Start a pair only when Spend plus the estimate is at or under $14.

**6. One cell: as T-0442, with these changes.**
- Make the cell with `git clone --shared <repo> "$SDLC_TMP_WORKTREES/rt-<task>-<level>-<arm>-<rep>"`, then `git -C <cell> checkout --detach <base>`, then the setup.
- An L1 build gets verifier L1, an L5 build gets verifier L3, both through `prepare` with the `armB` root.
- A blocked builder gets no verifier: verifier `n/a`, verifier cost and minutes `0`.
- Price every row with `dispatch.py record --transcript`.
- `block_tag` is `plan defect`, `stale lane`, `inherited red`, `other`, or `none`, taken from the builder's Notes the same way as the T-0450 mechanical tag.
- First pass means: not blocked, hidden check `pass` or `n/a`, and verifier `pass`.

**7. Run log.** Append one line per cell to `.sdlc/0458-builder-overlay-retest/run-log.md` [creates: .sdlc/0458-builder-overlay-retest/run-log.md]. Write it right after grading and before `record`, because `record` removes the tmp prefix and the first A/B lost its grade and minutes evidence that way (handoff Constraints). Each line holds every per-run column below plus the block Notes line.

**8. Rules and verdict.** Apply T-0442's drop rules from step 2 item 6 of its plan, per rep and pooled. Add the measured-block rule from the handoff: the L1 overlay is dropped if arm B's blocked rate over all its L1 runs is above arm A's. It should also be lower on the two `blocked note` tasks.
- The same rules apply to L5 with the L5 thresholds.
- Count the blocks that name the same defect as the original note, per arm.
- Every block on these tasks is a real plan defect: T-0450 calls the block the designed exit. So a lower blocked rate made of correct blocks lost (a build pushed through the defect) is a quality regression, not a win. Say so in the verdict text when it happens. The rule outcome is still applied as written.
- Derive `Verdict`, `L1 overlay`, `L5 overlay` and `Null at this sample size` exactly as in T-0442.

**9. Report.** Write `docs/reports/<YYYY-MM-DD>-builder-overlay-retest.md`. Small evidence files may go in a sibling folder of the same stem (`docs/reports/AGENTS.md`). The report holds:
- The lines `Verdict: <keep|extend|drop>`, `L1 overlay: <keep|drop|unverified>`, `L5 overlay: <keep|drop|unverified>`, `Null at this sample size: <yes|no>`, and `Spend: <n.nn> USD`. Spend is the sum of every replay builder and verifier row; also state the ticket total, if known, against the $20 cap.
- A per-run table with exactly this header: `| task | source | level | arm | rep | cost_usd | builder_min | blocked | block_tag | hidden_check | verifier | verifier_cost_usd | verifier_min |`.
- The per-arm totals table and the rule outcomes, including a line on the measured-block rule and a line counting blocks that name the same defect as the original note.
- A Method section with the arm diff, the preflights, the hash checks and the commands. Write any handoff from another repository or a base commit in the path forms above, never as a bare repo-relative path.
- A `## Not run` section. It lists `match-peer-lightness` (cost), `button-geometry-model` and `svelte-icon-component` (repos still missing), and 0356 and 0398 (T-0450 criterion defects that can never pass). It also lists 0372 and 0426 (no separable hidden check), any dropped task, and every pair skipped for budget, each marked unverified.
- A note that `figma-stale-skip-report` failed its hidden check `staleskipnotice` in all four first A/B runs while both verifier levels passed it, a verifier miss that is the same in both arms. It is recorded for the verifier prompt work, not fixed here.
- `## Raw rows`: a fenced jsonl block of every replay `runs.jsonl` row.

**10. Gates.** Run the guards below and fix any red this step introduced. This step does not prove an overlay effect beyond the rows it ran.
### Acceptance criteria
- (red) `f=$(ls docs/reports/*-builder-overlay-retest.md) && grep -qE "^Verdict: (keep|extend|drop)$" "$f" && grep -qE "^L1 overlay: (keep|drop|unverified)$" "$f" && grep -qE "^L5 overlay: (keep|drop|unverified)$" "$f" && grep -qE "^Null at this sample size: (yes|no)$" "$f"`
- (red) `f=$(ls docs/reports/*-builder-overlay-retest.md) && grep -qxF "| task | source | level | arm | rep | cost_usd | builder_min | blocked | block_tag | hidden_check | verifier | verifier_cost_usd | verifier_min |" "$f"`
- (red) `python3 -c 'import glob,sys; f=glob.glob("docs/reports/*-builder-overlay-retest.md"); r=[[c.strip() for c in l.split("|")[1:-1]] for l in open(f[0]) if l.startswith("| ") and len(l.split("|"))==15] if len(f)==1 else []; r=[x for x in r if x[2] in ("L1","L5") and x[3] in ("A","B")]; a1={x[0] for x in r if x[2]=="L1" and x[3]=="A" and x[4]=="1"}; b1={x[0] for x in r if x[2]=="L1" and x[3]=="B" and x[4]=="1"}; n5={a:sum(x[2]=="L5" and x[3]==a for x in r) for a in "AB"}; ok=len(a1)>=4 and a1==b1 and n5["A"]>=1 and n5["A"]==n5["B"] and sum(x[3]=="A" for x in r)==sum(x[3]=="B" for x in r); print(len(r),sorted(a1),n5); sys.exit(0 if ok else 1)'`
- (red) `python3 -c 'import glob,re,sys; f=glob.glob("docs/reports/*-builder-overlay-retest.md"); s=open(f[0]).read() if len(f)==1 else ""; m=re.search(r"^Spend: ([0-9]+\.[0-9]{2}) USD$",s,re.M); r=[[c.strip() for c in l.split("|")[1:-1]] for l in s.splitlines() if l.startswith("| ") and len(l.split("|"))==15]; r=[x for x in r if x[2] in ("L1","L5") and x[3] in ("A","B")]; t=sum(float(x[5])+float(x[11]) for x in r); print(m and m.group(1), round(t,2)); sys.exit(0 if m and r and abs(float(m.group(1))-t)<=0.05 and float(m.group(1))<=20 else 1)'`
- (red) `f=$(ls docs/reports/*-builder-overlay-retest.md) && grep -qF figma-stale-skip-report "$f" && grep -qF staleskipnotice "$f" && grep -qiF "measured-block" "$f" && grep -qiF "same defect" "$f" && grep -qE "^## Not run" "$f" && grep -qxF "## Raw rows" "$f"`
- (red) `test -s .sdlc/0458-builder-overlay-retest/run-log.md`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins docs/specs scripts && test -z "$(git ls-files --others --exclude-standard -- plugins docs/specs scripts)"`
- (guard) `python3 -c 'import subprocess,sys,re; a=subprocess.run(["git","diff","--name-only",sys.argv[1],"--",".",":(exclude).sdlc"],capture_output=True,text=True).stdout.split(); b=subprocess.run(["git","ls-files","--others","--exclude-standard","--",".",":(exclude).sdlc"],capture_output=True,text=True).stdout.split(); ok=re.compile(r"docs/reports/\d{4}-\d{2}-\d{2}-builder-overlay-retest(\.md|/.+)"); bad=[p for p in a+b if not ok.fullmatch(p)]; print(bad); sys.exit(1 if bad else 0)' "$SDLC_BASE_SHA"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA"`
