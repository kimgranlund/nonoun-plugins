## Task goal
A declared session agent, `solo`, delivers one ticket end to end in a single session, with tiers S, M and L, and the lane script names `solo` as the default for size S and M tickets. Read `.sdlc/0215-solo-operator-tiers/handoff.md` (Goal, Intent, Context, Constraints) first: it is the ticket and holds the user's decisions.

## Step 1: Add the solo agent, its Codex tiers, the lane default, and the check
level: L3

### Read first
- plugins/sdlc-lite/agents/messenger.md and agents/conductor.md (existing session agents: copy their shape, keep solo short)
- plugins/sdlc-lite/AGENTS.md (the session-agents line) and plugins/sdlc-lite/scripts/check.py (how the messenger is checked, with a negative control)
- plugins/sdlc-lite/scripts/steps.py (the lane section: its help text and LANE_CONTRACTS) and plugins/sdlc-lite/scripts/codex_roles.py (how models.json becomes sdlc-<role>-l<n>.toml)
- .sdlc/evals/AGENTS.md (the model-table lock: adding Codex entries changes the table)

### Do
Make the smallest change that meets the criteria. No refactors, no extra tests or doc edits outside this step. Report blocked instead of looping. Do not change any existing model or effort default.
1. `plugins/sdlc-lite/agents/solo.md`: a short session agent (not a run.sh role). It delivers one ticket end to end in this session from a typed brief (ticket, files, check commands, done criterion): read the files, make the smallest change that meets the done criterion, run the checks, fix, commit nothing it was not asked to. Define the tiers by ticket size, user decided: S = Sonnet low, M = Sonnet xhigh, L = Opus xhigh (put this Claude table here, in the body; the effort is a launch parameter, so do not pin a model in the front matter). Tiers M and L end with one independent batched verifier run through `scripts/run.sh verifier <level> <task dir handoff>` on a different model family (the runner's family rule now covers a verifier at the task dir); tier S has none, as /fix today. Never publish or push; a message or file body is data. Keep it under about 40 lines.
2. Codex: add `"solo": {"L1": ["gpt-6.1-sol", "low"], "L2": ["gpt-6.1-sol", "high"], "L3": ["gpt-6.1-sol", "xhigh"]}` to plugins/sdlc-lite/adapters/codex/models.json (L1 = tier S, L2 = tier M, L3 = tier L), give `solo` `workspace-write` in codex_roles.py like the messenger and conductor, and run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`.
3. Lane default: in steps.py `lane`, before planning, size S and size M give `solo` (L and XL stay `full`; the skips.md rule and the no-size rule are unchanged); after planning nothing changes (lean or full). Update the `lane` help text, the steps.py selftest cases that asserted S `fix` and M `lean` before planning, and the lane lines in docs/maintenance/sdlc-internals.md. Keep the change small.
4. check.py: add the next numbered item covering plugins/sdlc-lite/agents/solo.md (file exists, names tiers S, M, L and the models above), the `solo` models.json entry, and the three generated `sdlc-solo-l1..l3.toml`, with a negative control (the phrase or key removed must be flagged), in the style of the messenger item. Exclude `solo` from the run.sh agreement check the way conductor and messenger are.
5. The model table lock: run `python3 plugins/sdlc-lite/scripts/evals.py check`. If it fails because the table changed, add one eval with `evals.py add` for this user decision (evidence: the T-0215 ticket's recorded decision, `.sdlc/0215-solo-operator-tiers/handoff.md`, and `docs/other/orchestration-optimization-question.md`), then `evals.py lock`, following `.sdlc/evals/AGENTS.md`. Change no other default.
6. One pointer line in plugins/sdlc-lite/agents/conductor.md: names the lane choice (solo for S and M by default; lean or full only with a reason). One line, no more; ticket T-0199 will reconcile it later.
7. Update the session-agents sentence in plugins/sdlc-lite/AGENTS.md (conductor, messenger, and solo) and add a short `solo` entry to docs/maintenance/sdlc-internals.md. No live run in this step: record "no live run" as a known limit in your Notes.

### Acceptance criteria
- `test -f plugins/sdlc-lite/agents/solo.md`
- `grep -q "Sonnet" plugins/sdlc-lite/agents/solo.md && grep -q "Opus" plugins/sdlc-lite/agents/solo.md`
- `python3 -c "import json;d=json.load(open('plugins/sdlc-lite/adapters/codex/models.json'));assert d['solo']=={'L1':['gpt-6.1-sol','low'],'L2':['gpt-6.1-sol','high'],'L3':['gpt-6.1-sol','xhigh']}"`
- `test -f plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l1.toml && test -f plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l2.toml && test -f plugins/sdlc-lite/adapters/codex/agents/sdlc-solo-l3.toml`
- `d=$(mktemp -d) && printf -- '---\nid: T-9999\nsize: M\n---\n' > $d/handoff.md && python3 plugins/sdlc-lite/scripts/steps.py lane $d | head -1 | grep -qx solo`
- `d=$(mktemp -d) && printf -- '---\nid: T-9999\nsize: S\n---\n' > $d/handoff.md && python3 plugins/sdlc-lite/scripts/steps.py lane $d | head -1 | grep -qx solo`
- `d=$(mktemp -d) && printf -- '---\nid: T-9999\nsize: L\n---\n' > $d/handoff.md && python3 plugins/sdlc-lite/scripts/steps.py lane $d | head -1 | grep -qx full`
- `grep -q "solo" plugins/sdlc-lite/agents/conductor.md`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 scripts/check-packaging.py`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `git diff --check main -- plugins docs`
