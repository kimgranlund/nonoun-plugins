<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Write the T-0458 retest report, `docs/reports/2026-10-12-builder-overlay-retest.md`, from the replay evidence already on disk: three priced cells, the replay stopped at the $20 ticket cap, the T-0442 rules applied as written, and every pair that did not run marked unverified.
guard timeout: 30

## Step 1: Write the retest report from the recorded cells, gates green
level: L1
### Read first
- `docs/reports/AGENTS.md`
### Do
Depends on: none. This is a replan of step 1 after the builder blocked on budget (`.sdlc/0458-builder-overlay-retest/step-1.superseded-2/builder-L3.md`, Notes). Conductor direction from the handoff's `## Plan review`: run no further cells; write the report from what exists. Every value below is settled here. Copy it; do not re-derive or soften it.

Hard limits:
- No model spend. Do not run a cell, `claude -p`, `dispatch.py`, a preflight or `cell.py`.
- Do not edit `.sdlc/0458-builder-overlay-retest/run-log.md` or anything under `docs/reports/2026-10-12-builder-overlay-retest/`. Read them only.
- Do not edit any overlay, agent, adapter, skill, script, or `docs/reports/2026-10-11-builder-overlay-ab.md`. Reports are immutable, and the scope guard (criterion 8) refuses any path outside the report stem.

Inputs (read only):
- Per-run values: `.sdlc/0458-builder-overlay-retest/run-log.md`, one line per cell. Columns after the timestamp are task, source, level, arm, rep, cost_usd, builder_min, blocked, block_tag, hidden_check, verifier, verifier_cost_usd, verifier_min, then the notes.
- Evidence folder `docs/reports/2026-10-12-builder-overlay-retest/`: `budget.txt`, `preflight.txt`, `cell.py`, and the cell dirs `rt-rts-step10-L1-A-1/`, `rt-rts-step10-L1-B-1/` and `rt-ndc-step2-L5-A-1/`. Each cell dir holds `builder.md`, `rows.jsonl`, `log.txt`, and `verifier.md` when a verifier ran.
- Method facts and findings: the Checks and Notes of `.sdlc/0458-builder-overlay-retest/step-1.superseded-2/builder-L3.md`.
- Layout to follow: `docs/reports/2026-10-11-builder-overlay-ab.md`. The rules come from `.sdlc/.0442-builder-overlay-ab/planner-L2.md`, step 2 item 6.

Write `docs/reports/2026-10-12-builder-overlay-retest.md` [creates: docs/reports/2026-10-12-builder-overlay-retest.md]. Use this stem, not today's date, because the evidence folder already has it (`docs/reports/AGENTS.md`). Write the sections below in this order.

1. Title `# Builder overlay retest on blocking tasks (T-0458)`, then one line stating the ticket question. Then these lines, each exactly as written, on its own line:
   - `Verdict: drop`
   - `L1 overlay: drop`
   - `L5 overlay: unverified`
   - `Null at this sample size: yes`
   - `Spend: 10.04 USD`
   - `Ticket spend: <n.nn> USD (planners, the blocked L3 builder and the replay, before this report's builder, verifier and filer), under the 20 USD cap`. Here `<n.nn>` is the second number criterion 4 prints, to two decimals.
   - `Outcome metric: builder blocked rate, arm A versus arm B: L1 0 of 1 versus 0 of 1, L5 1 of 1 versus not run (before: 0 of 5 versus 0 of 5 on the first A/B tasks)`

   Then one paragraph that says:
   - The drop comes from the T-0442 blocked-rate rule, the same rule that dropped L1 in the first A/B. It could not bite here either.
   - So the retest adds no evidence beyond the first A/B's outcome, which the maintainer saw and overruled on 2026-10-11.
   - The only L1 task that ran replayed the fixed handoff, sha256 `8974d49f`. The blocked version, `fceea3cc`, was never committed in agent-ui and is gone. So no L1 run tested blocking, and the retest did not reach the ticket's question.
   - The L5 pair is half run.
   - The replay stopped at the cap.
2. `## Per-run results`. One sentence on cost provenance: `dispatch.py record --transcript`, `cost_estimated`, basis `usage fields x rates`. Then the table with exactly this header line:
   `| task | source | level | arm | rep | cost_usd | builder_min | blocked | block_tag | hidden_check | verifier | verifier_cost_usd | verifier_min |`
   Add a `|---|` separator line, then one row per run-log line in run order. Each row is that line's 13 columns after the timestamp, copied character for character (criterion 2 compares them). `hidden_check` is `n/a` on all three, because both tasks are `blocked note` tasks (the plan's rule: a step with a real plan defect has no correct build to grade).
3. `## Rule outcomes`.
   - A per-arm table with columns `| measure | arm A (no overlay) | arm B (overlay) | change |` and these rows:
     - L1 builder cost, `rts-step10` rep 1: 0.34, 0.28, -17.5 percent.
     - L1 verifier cost: 0.51, 0.37, -27.3 percent.
     - L1 builder minutes: 1.2, 1.2, none.
     - L1 verifier minutes: 1.5, 1.1, -0.4 min.
     - L1 blocked: 0 of 1, 0 of 1, none.
     - L1 first pass, `rts-step10`: 1 of 1, 1 of 1, none.
     - L5 builder cost, `ndc-step2` rep 1: 8.54, not run, n/a.
     - L5 blocked: 1 of 1, not run, n/a.
     - Blocks that name the same defect as the original note: 1 of 1 (L5), 0 runs, n/a.
   - Then an L1 rule table `| rule | rep 1 | rep 2 |` with these rows; every rep 2 cell is `not run`:
     - blocked rate below arm A's: no (0/1 vs 0/1), drop.
     - any task's first-pass rate falls: no.
     - cost rises more than 10 percent: no (-17.5).
     - hidden-check regression: none (n/a in both arms).
     - measured-block: arm B blocked rate above arm A's: no (0/1 vs 0/1).
     - measured-block: lower on the blocked-note tasks: no (0 vs 0 on `rts-step10`; `ndc-step2` L1 not run).
   - Then these prose lines:
     - Null: only rep 1 ran, so no rule outcome was shown in both reps, and the null line is `yes`.
     - The measured-block rule (the ticket's added rule) is not raised, and lowering could not be measured.
     - L5 rules: not applied, because arm B never ran, so `L5 overlay: unverified`.
     - Same defect: the L5 arm A block names the original note's defect. The scope guard omits `scripts/bundle.mjs`, which the mandated chart imports require. That makes 1 of 1 arm A blocks the same defect, with no arm B run. The original L3 builder cost $3.41 to block on it. The L5 builder cost $8.54.
     - Overall: the only overlay that ran is dropped, so `Verdict: drop` (T-0442 derivation). This records the verdict only. Deleting or keeping the overlay is the maintainer's call, and T-0443 stays gated on it.
4. `## Stop at the cap`. Quote the three lines of `budget.txt`. Then state the arithmetic:
   - Replay Spend was 10.04 after half the L5 pair.
   - Arm B at the arm A cost would have made it 18.58, against the 14.00 replay target.
   - The planners ($3.85) plus the blocked L3 builder ($2.14) put the ticket at about $16.03.
   - So no further cell ran, per the conductor's direction and the ticket Constraint "stop at it and report what was run".
5. `## Method`. Take each bullet from builder-L3.md:
   - Arms: `git clone --shared` copies under the tmp prefix. armB is this repo at `ebac4973`. armA is the same with `builder-L1.md` and `builder-L5.md` from `00735e20^`. `diff -rq` of the two plugin folders lists only those two files, with one hunk each (`34a35,55` for L1, `34a35,52` for L5), and each hunk starts `## At this level`.
   - Preflight: the Haiku `--plugin-dir` init events in `preflight.txt` show exactly one `sdlc-lite` plugin, at the arm root, in agent-ui@0e18b708, ultimate-tokens@7f05eb50 and sdlc-lite@6a14c165 cells, for both arms.
   - Hash checks: the `rts-step10` cell handoff is `8974d49f6a3f`, the done row, not the blocked row `fceea3cca477` (mismatch). The `ndc-step2` handoff is `6c2cd3e60200`, which matches the blocked row.
   - The t0378 hidden check is red at base `b599114e` and green at `a8b39893` and `e1fa6e04`. The earlier plan's claim "red at wip a8b39893" was false. t0378 did not run.
   - Base trees were checked with `git ls-tree`; no task was dropped.
   - Each cell was priced with `dispatch.py record --transcript`. `steps.py lint` was ok and `prepare` passed every time.
   - The driver is `cell.py` in the evidence folder.
   - Repository paths outside this repo are written as absolute paths or plain words, never as bare repo-relative `.sdlc/` paths.
6. `## Not run`. One bullet each, verbatim:
   - `ndc-step2` L5 arm B rep 1: unverified, skipped for budget.
   - L1 rep 1 pairs `ndc-step2`, `t0368`, `t0373`, `t0378`: unverified, skipped for budget.
   - L1 rep 2 pairs for `rts-step10`, `ndc-step2`, `t0368`, `t0373`, `t0378`: unverified, skipped for budget (no rep 2 ran).
   - `match-peer-lightness`: unverified, its L5 original cost $39.24 and fits no budget.
   - `button-geometry-model`, `svelte-icon-component`: unverified, their repos and base shas are missing on this machine.
   - 0356, 0398: unverified, T-0450 criterion defects that can never pass.
   - 0372, 0426: unverified, no separable hidden check.
7. `## First A/B verifier miss`. `figma-stale-skip-report` failed its hidden check `staleskipnotice` in all four first A/B runs, while both verifier levels passed it each time. It is a verifier miss, the same in both arms. It is recorded for the verifier prompt work and not fixed here.
8. `## Raw rows` as the last section. A fenced `jsonl` block holding the output of `cat docs/reports/2026-10-12-builder-overlay-retest/rt-*/rows.jsonl`, unchanged (5 rows).

Style: no em dash and no trailing whitespace. Any relative Markdown link must resolve from `docs/reports/`; plain backticked paths are safer (criterion 6).

Validation scope: criteria 1 to 7 check the report against the run log and the `rows.jsonl` files at run time. Criterion 8 is the scope guard. Criterion 9 is the repo check (`check.py` reads tracked files only, so the untracked report is checked by criteria 1 to 7). No other contract consumes this report: it is a new dated file that nothing names.
### Acceptance criteria
- (red) `test -f docs/reports/2026-10-12-builder-overlay-retest.md && f=docs/reports/2026-10-12-builder-overlay-retest.md && grep -qxF "Verdict: drop" "$f" && grep -qxF "L1 overlay: drop" "$f" && grep -qxF "L5 overlay: unverified" "$f" && grep -qxF "Null at this sample size: yes" "$f" && grep -qE "^Outcome metric: " "$f" && grep -qxF "| task | source | level | arm | rep | cost_usd | builder_min | blocked | block_tag | hidden_check | verifier | verifier_cost_usd | verifier_min |" "$f"`
- (red) `python3 -c 'import os,sys; f="docs/reports/2026-10-12-builder-overlay-retest.md"; L=[l[2:].rstrip("\n").split(" | ",14) for l in open(".sdlc/0458-builder-overlay-retest/run-log.md") if l.startswith("- ")]; want=sorted(tuple(p[1:14]) for p in L if len(p)==15); s=open(f).read() if os.path.isfile(f) else ""; r=[tuple(c.strip() for c in l.split("|")[1:-1]) for l in s.splitlines() if l.startswith("| ") and len(l.split("|"))==15]; got=sorted(x for x in r if x[2] in ("L1","L5") and x[3] in ("A","B")); print(len(want),len(got)); sys.exit(0 if want and got==want else 1)'`
- (red) `python3 -c 'import glob,json,os,re,sys; f="docs/reports/2026-10-12-builder-overlay-retest.md"; s=open(f).read() if os.path.isfile(f) else ""; m=re.search(r"^Spend: ([0-9]+\.[0-9]{2}) USD$",s,re.M); e=sum(json.loads(l)["cost_usd"] for p in glob.glob("docs/reports/2026-10-12-builder-overlay-retest/rt-*/rows.jsonl") for l in open(p) if l.strip()); r=[[c.strip() for c in l.split("|")[1:-1]] for l in s.splitlines() if l.startswith("| ") and len(l.split("|"))==15]; t=sum(float(x[5])+float(x[11]) for x in r if x[2] in ("L1","L5") and x[3] in ("A","B")); print(m and m.group(1), round(e,2), round(t,2)); sys.exit(0 if m and e>0 and abs(float(m.group(1))-e)<=0.01 and abs(t-e)<=0.05 and e<=20 else 1)'`
- (red) `python3 -c 'import glob,json,os,re,sys; f="docs/reports/2026-10-12-builder-overlay-retest.md"; s=open(f).read() if os.path.isfile(f) else ""; m=re.search(r"^Ticket spend: ([0-9]+\.[0-9]{2}) USD",s,re.M); d=".sdlc/0458-builder-overlay-retest"; ps=[d+"/runs.jsonl"]+glob.glob(d+"/step-*.superseded-*/runs.jsonl")+glob.glob("docs/reports/2026-10-12-builder-overlay-retest/rt-*/rows.jsonl"); e=sum(json.loads(l).get("cost_usd") or 0 for p in ps if os.path.isfile(p) for l in open(p) if l.strip()); print(m and m.group(1), round(e,2)); sys.exit(0 if m and float(m.group(1))>=e-0.05 and float(m.group(1))<=20 else 1)'`
- (red) `python3 -c 'import os,re,sys; f="docs/reports/2026-10-12-builder-overlay-retest.md"; s=open(f).read() if os.path.isfile(f) else ""; m=re.search(r"^## Not run.*?(?=^## |\Z)",s,re.M|re.S); t=m.group(0) if m else ""; need=["ndc-step2","rts-step10","t0368","t0373","t0378","arm B","rep 2","budget","unverified","match-peer-lightness","button-geometry-model","svelte-icon-component","0356","0398","0372","0426"]; miss=[w for w in need if w not in t]; print(miss); sys.exit(0 if m and not miss else 1)'`
- (red) `python3 -c 'import os,re,sys; f="docs/reports/2026-10-12-builder-overlay-retest.md"; s=open(f).read() if os.path.isfile(f) else ""; need=["figma-stale-skip-report","staleskipnotice","measured-block","same defect","8974d49f","fceea3cc","scripts/bundle.mjs","b599114e","e1fa6e04","## Method","## Raw rows"]; miss=[w for w in need if w not in s]; bad=[n for n,l in enumerate(s.splitlines(),1) if chr(8212) in l or l!=l.rstrip()]; links=[t for t in re.findall(r"\]\(([^)\s]+)\)",s) if not re.match(r"[A-Za-z][A-Za-z0-9+.-]*:|#",t) and not os.path.exists(os.path.join("docs/reports",t.split("#")[0]))]; print(miss,bad[:5],links); sys.exit(0 if s and not miss and not bad and not links else 1)'`
- (red) `python3 -c 'import glob,json,os,sys; f="docs/reports/2026-10-12-builder-overlay-retest.md"; s=open(f).read() if os.path.isfile(f) else ""; t=s.split("\n## Raw rows\n",1)[1] if "\n## Raw rows\n" in s else ""; got=sorted(json.loads(l)["attempt_id"] for l in t.splitlines() if l.startswith("{")); want=sorted(json.loads(l)["attempt_id"] for p in glob.glob("docs/reports/2026-10-12-builder-overlay-retest/rt-*/rows.jsonl") for l in open(p) if l.strip()); print(len(got),len(want)); sys.exit(0 if want and got==want else 1)'`
- (guard) `python3 -c 'import subprocess,sys,re; a=subprocess.run(["git","diff","--name-only",sys.argv[1],"--",".",":(exclude).sdlc"],capture_output=True,text=True,check=True).stdout.split(); b=subprocess.run(["git","ls-files","--others","--exclude-standard","--",".",":(exclude).sdlc"],capture_output=True,text=True,check=True).stdout.split(); ok=re.compile(r"docs/reports/2026-10-12-builder-overlay-retest(\.md|/.+)"); bad=[p for p in a+b if not ok.fullmatch(p)]; print(bad); sys.exit(1 if bad else 0)' "$SDLC_BASE_SHA"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`

## Assumptions
- Settled scope: no new cells, three report rows. Verified by the handoff's second `plan review:` line, which gives the conductor's direction under the cap, and by `.sdlc/0458-builder-overlay-retest/run-log.md`, which holds exactly three lines: `rts-step10` L1 A and B rep 1, and `ndc-step2` L5 A rep 1.
- Verdict values, derived from `.sdlc/.0442-builder-overlay-ab/planner-L2.md` lines 65 to 75 applied to the three rows:
  - L1: arm B blocked 0 of 1 is not below arm A's 0 of 1, so rule 1 drops it.
  - L5: arm B never ran, so unverified.
  - Overall: the only overlay that ran is dropped, so `Verdict: drop`.
  - Null: only rep 1 ran, so `yes`.
  - The previous plan said to apply the rules as written (`.sdlc/0458-builder-overlay-retest/planner-L3.md` item 8). This replan keeps that, and the report must state that the rule could not bite. The result matches the T-0442 precedent: drop, with L5 unverified.
- Spend: the five `rows.jsonl` rows sum to 10.0434, which matches `budget.txt` ("spend 10.04") and the run-log columns (0.34 + 0.51 + 0.28 + 0.37 + 8.54 + 0.00).
- Ticket spend before this replan was 16.03: planners 2.34 + 1.51, blocked builder L3 2.14, replay 10.04. Criterion 4 printed `16.03` on a fixture copy of the three sources. This replan's own row lands in the task `runs.jsonl` before the builder starts, so the builder reads the higher total from criterion 4.
- Budget: $16.03 plus this replan, plus builder L1, verifier and filer, must stay under $20. That is why the step is L1 with every value pinned. Builder L1 is Sonnet low. Its verifier is L1, which dispatch moves to Opus medium after a Sonnet build; the replay's L1 verifiers on that seat cost $0.37 and $0.51.
- No level bump: the earlier block was tagged `plan defect:`, and a superseded step dir does not count (level rubric).
- Criteria probes, run once in one call:
  - On the current tree with `SDLC_BASE_SHA=ebac4973`, all seven `(red)` exit nonzero because the report is missing. Criterion 1 exits 1 at its `test -f`. The rest exit 1 and print empty or missing results.
  - Criterion 1 starts with `test -f` so `steps.py` reads it as a command. Its earlier bare `f=...` assignment head was skipped by `specgate.py red`, which counted 6 spans before the fix and 7 after.
  - Both guards are green.
  - On a fixture copy (evidence folder, run-log and both `runs.jsonl` copied under the tmp prefix, plus a fixture report) all seven pass.
  - A fixture with one wrong cost cell and Spend off by 0.60 turns criteria 2 and 3 red.
  - A fixture with an em dash and a ticket spend of 21.00 turns criteria 6 and 4 red.
  - A scratch copy of this plan passed `results.py validate --role planner`, `steps.py lint`, `steps.py split`, `steps.py lint` of the split handoff, `specgate.py check`, and `specgate.py red` (7 of 7 red now). `steps.py review` says no plan review is required.
- Guards:
  - The scope guard is green at `ebac4973` with the untracked evidence folder present. It goes red with `SDLC_BASE_SHA=00735e20^`, listing tracked paths outside the stem; with `HEAD~3` it stays green, because those commits touch only `.sdlc`.
  - `check.py` ran in 5 seconds, so the guard timeout is 30, kept from the previous plan for margin under concurrent-lane load. Its red state was not observed here; it carries its own negative controls.

## Risks
- The `drop` verdict rests, again, on a rule that could not bite: zero blocks in both arms on a task whose blocking handoff no longer exists. A reader could argue that `L1 overlay: unverified` is more honest. This plan keeps the T-0442 derivation as written, as the previous plan settled. The report must say that the drop does not answer the ticket's question, so the maintainer can overrule it.
- Budget: if this replan costs more than about $1.5, the builder, verifier and filer have under $2.50 together. A verifier fail and rebuild could cross $20, which the conductor must stop on.
- Criterion 4 counts every row in the task-level `runs.jsonl`. If the conductor records another task-level row between builder and verifier, such as a plan-reviewer, which this L1 plan does not need, the reported ticket spend would fall short and criterion 4 goes red. The fix is a one-line value update.
- Criterion 5 checks token presence in the `## Not run` section, not one token per bullet. A bullet dropped while its task name stays elsewhere in the section passes.
- Builder L1 must copy the run-log cells character for character; the `ndc-step2` row's `0.00` and `0` are the likely slip. Criterion 2 catches it before the verifier does.
- `check.py` reads tracked files only, so it cannot see the untracked report until the lane lands it. Criteria 1 to 7 cover the report instead.
- The planner hook refused `git worktree add` for this session (`SDLC_TMP_WORKTREES` unset). So the probe fixtures are plain directory copies under `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout40/v/.worktrees/tmp/0458-planner-L3-2/`, and they stay in place (rule 15):
  - `fx`, `fx2` and `fx3`
  - `task`, `task2`, `task3`, `task4` and `task5`
  - `broken.md`, `crit.txt`, `critC.txt`, `critC1.txt`, `critC6.txt`, `critG1.txt` and `run.sh`
