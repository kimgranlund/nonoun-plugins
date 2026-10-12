## Task goal
A dated report with a keep, extend or drop verdict for the builder overlays from a replay on tasks that make builders block, and at least one priced L5 pair.

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
