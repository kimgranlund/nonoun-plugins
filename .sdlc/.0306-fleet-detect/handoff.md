---
id: T-0306
title: "fleet_detect.py: waste and stall detect rules"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0305]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Mechanical rules that flag waste and stalls in a collector fingerprint, each with the evidence field that triggered it.

## Intent
- Do: Add plugins/sdlc-lite/scripts/fleet_detect.py with `detect <fingerprint.json>... ` printing findings as JSON lines (rule id, repo, evidence path, measured value, threshold), plus `selftest`. Rules at minimum: planner results per ticket over 5; plan-review plus planning share of spend over 40 percent; size M ticket with more than 20 criteria; any hook process over 50 percent CPU for over 20 seconds; Chromium over 30 processes or 6 GB; interrupted or limit-marker attempts over 3; a session whose plugin version is older than the installed one; a CI workflow with more than 25 push runs in 7 days duplicating its pull_request runs.
- Non-goals: Fixing any finding; model judgment.
- Done when:
  - Each rule has a fixture that triggers it and one that does not (a positive and a negative per rule, observed).
  - Running detect on the fingerprints of the three repos reproduces these known findings: agent-ui plan-review share over 40 percent, maison a size M ticket over 20 criteria is not required, maison and gen-ui-kit Chromium over the threshold.
  - Thresholds live in one table at the top of the file and are documented.
  - `check.py` and `tickets.py check` pass.

## Context
Decided by the user on 2026-10-06 after three repo root-cause reports (maison, agent-ui, gen-ui-kit, each at root-cause-2026-10-06.md in its repo). Design: a thin skill `/sdlc-lite:fleet-retro` on top of the existing `review-traces` skill: a deterministic collector, mechanical detect rules, a 5-question conductor interview, one cross-repo ranked report, a sampled verifier, then filing through review-traces. Existing pieces to reuse: runs.jsonl dedupe by attempt_id (agent-ui's method), scripts/budget.py cost sums, skills/review-traces/SKILL.md, scripts/footprint.py. Build after the 0.20.11 batch ships; target release 0.21.1.

## Constraints
No model call inside collect or detect. Read-only on every repo it inspects. No em dashes. No change to any model or effort value. No push, tag or publish.

## Acceptance criteria
Run from the repository root. fleet_detect reads only fingerprints, so the collector gains the keys the rules need (`runs.by_ticket`, `tickets`, per-process `items` and `rss_mb`, CI `by_event` and the 7-day push counts), additive only. A repo that sets `ticket_root: tickets` (maison) keeps its tickets in `.sdlc/tickets/<folder>`, and a lane worktree may lack the untracked `.sdlc/config`, so the collector keys a ticket by its folder under that root. Chromium and hook CPU are live machine state: they are reproduced from fixtures that encode the 2026-10-06 reports' numbers, not from a live run. The agent-ui plan-review share is also checked live at the report's cutoff.
- `out=$(python3 plugins/sdlc-lite/scripts/fleet_detect.py selftest) && printf '%s\n' "$out" | grep -qx 'fleet_detect selftest: ok'`
- `out=$(python3 plugins/sdlc-lite/scripts/fleet_detect.py selftest) && for r in planner_results_per_ticket plan_review_share size_m_criteria hook_cpu chromium_load stall_attempts plugin_version_stale ci_push_duplicates; do printf '%s\n' "$out" | grep -q "^ok: positive: $r (" && printf '%s\n' "$out" | grep -q "^ok: negative: $r" || { echo "no observed positive and negative for $r"; exit 1; }; done`
- `out=$(python3 plugins/sdlc-lite/scripts/fleet_detect.py selftest) && printf '%s\n' "$out" | grep -q '^ok: negative control: raising stall_attempts in the table silences stall_attempts'`
- `out=$(python3 plugins/sdlc-lite/scripts/fleet_detect.py selftest) && printf '%s\n' "$out" | grep -q '^ok: known finding: agent-ui plan-review share is over 40 percent' && printf '%s\n' "$out" | grep -q '^ok: known finding: maison Chromium is over' && printf '%s\n' "$out" | grep -q '^ok: known finding: gen-ui-kit Chromium is over'`
- `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect /Users/kimgranlund/Projects/nonoun/agent-ui --until 2026-10-06T14:06:53Z --du-timeout 5 2>/dev/null | python3 plugins/sdlc-lite/scripts/fleet_detect.py detect - 2>/dev/null | python3 -c "import json,sys; f=[json.loads(l) for l in sys.stdin]; sys.exit(0 if any(x['rule']=='plan_review_share' and x['value']>0.40 for x in f) else 1)"`
- `echo '{"repo":"/x","runs":"none","ci":"skipped","plan_review_share":null}' | python3 plugins/sdlc-lite/scripts/fleet_detect.py detect - 2>/dev/null | wc -c | grep -qx ' *0'`
- `awk '/^THRESHOLDS/{t=NR} /^def rule_/{if(!r)r=NR} END{exit !(t && t<r)}' plugins/sdlc-lite/scripts/fleet_detect.py && test "$(sed -n '/^THRESHOLDS/,/^\])/p' plugins/sdlc-lite/scripts/fleet_detect.py | grep -c "^    ('")" = 9`
- `python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest | grep -qx 'fleet_collect selftest: ok'`
- `out=$(python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest) && printf '%s\n' "$out" | grep -q '^ok: ticket_root: tickets keys each ticket folder' && printf '%s\n' "$out" | grep -q '^ok: ticket_root control: the flat layout keys the same folders by name'`
- `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect /Users/kimgranlund/Projects/maison/ui-kit-maison --du-timeout 5 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); b=d['runs']['by_ticket']; sys.exit(0 if 'tickets' not in b and any(k.startswith('tickets/') for k in b) and d['tickets']['count'] > 20 else 1)"`
- `! grep -n "$(printf '\342\200\224')" plugins/sdlc-lite/scripts/fleet_detect.py plugins/sdlc-lite/scripts/fleet_collect.py docs/maintenance/sdlc-internals.md .sdlc/0306-fleet-detect/handoff.md && git diff --check`
- `grep -q 'fleet_detect.py" selftest' plugins/sdlc-lite/scripts/check.sh && grep -q '^## `scripts/fleet_detect.py`' docs/maintenance/sdlc-internals.md`
- `python3 plugins/sdlc-lite/scripts/check.py`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
