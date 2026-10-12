<!-- role=architect level=L1 model=fable effort=high -->
## Approach

Result in one line: the published record supports execution feedback from reliable tests and an independent judge on a different model family with repo access; it does not support generator-critic loops without an external signal, role-based multi-agent teams on coding (3x to 15x tokens, no equal-compute win), or spec-first tooling (Kiro, Spec Kit, Tessl: launch posts and one hooks ablation, no outcome data); merge-queue gains (GitHub 33 percent wait cut, Uber 53 percent CI cost) are batching under contention at hundreds of engineers and do not transfer to a one-maintainer repo, where the measured merge cost is hand-resolved generated files (5 of 8 wave merges). The three things our system does that no surveyed pattern does (cross-family verifier, observed negative controls, per-ticket budget stop) each have a published mechanism behind them (self-preference bias in LLM judges; test strength moving scores 10 to 25 points; cost-controlled comparisons changing rankings) and local evidence for keeping them (0 verifier over-reach in 34 non-passes, verifiers 7.5 percent of spend against planning 55 percent).

Report: `/Users/kimgranlund/Projects/nonoun/sdlc-lite/docs/reports/2026-10-12-industry-alternatives-review.md` (sections: patterns with sources and tiers, local comparison, the three unique mechanisms, one verdict per open ticket, ranked changes, unverified).

Ranked changes to the queue (cost is this repo's measured solo run, about $3 and 20 minutes, scaled by level: an estimate):
1. Move T-0485 (solo result file, L1) to the top. About $3 plus one verifier round. Quality pillar: prerequisite for testing the one open claim, that a verified solo pass met intent. Worsens nothing.
2. Order the merge cluster T-0489 first, T-0491 beside it, T-0492 after, defer T-0490. T-0489 about $5 to $15, T-0491 about $3. Performance (one hand merge per wave removed) and cost (no 1800 s waits on cheap gates). Resilience worsens only if `settle --forward` regenerates over a real conflict; its exit 2 control guards that.
3. Reshape T-0486 into a 10 minute rerun on main first (T-0473 moved the red-checkpoint phase read to the working tree); close if green, else fold into the finding 6 resume-semantics ticket. Under $1. Cost pillar.
4. Defer T-0443 to the maintainer's call on T-0458 (retest verdict drop, question never reached); close as dropped on a drop. Saves about $10. Cost pillar.
5. Plan-skill cluster order stands (T-0467, T-0468, then T-0469 and T-0463 in parallel, T-0465 after A); the one change is T-0465 recording its before baseline before building. Under $3. Cost pillar.

No new ticket for an LLM diff reviewer, a critic loop, a role team, spec-first tooling or a queue daemon: the evidence rejects each beyond what the independent verifier already is.

## Interfaces

- New file, untracked, maintainer commits: `/Users/kimgranlund/Projects/nonoun/sdlc-lite/docs/reports/2026-10-12-industry-alternatives-review.md`. No code, ticket or spec changed.

## Constraints and assumptions

- 15 proposed tickets, 0 ready: verified by the `.sdlc/AGENTS.md` Stages block (roadmap, 2026-10-12).
- T-0481 (light merge lane) is built: verified by `docs/planning/light-merge-lane.md` front matter `status: built`.
- T-0473 moved the red-checkpoint phase read to the working tree at HEAD: verified by the `plugins/sdlc-lite/scripts/redck.py` docstring; whether T-0486's codex case still reproduces: unverified.
- T-0458's retest verdict is drop and never reached the ticket's question: verified by `docs/reports/2026-10-12-builder-overlay-retest.md` lines 5, 13, 53.
- 5 of 8 wave merges hand-resolved, 4 on generated files: from `docs/planning/merge-ops-and-queue.md` line 16, not re-run here | unverified.
- Research rows come from four researcher L1 sub-agents' output; this pass re-fetched no page | unverified.
- Local cost figures are floors: 113 of 192 baseline runs unmetered (K-001, `docs/kpi/005-solo-first-pass-rate.md` line 23): verified by reading.
- `dispatch.py prepare` enforces the verifier family rule: verified by `plugins/sdlc-lite/agents/solo.md` line 51 and `skills/level-rubric/SKILL.md` line 56.

## Rejected alternatives

- A new ticket for an LLM diff reviewer or a second critic pass: Kapoor et al. 2024 (critic loops at up to 50x cost, no gain) and Huang et al. 2023 (self-correction without external feedback hurts); our verifier already is the reviewer-with-repo-access form the one positive result describes.
- A role-based multi-agent build (MetaGPT, ChatDev shape): 3x to 15x tokens in every source, no coding benchmark win at equal compute; our measured chain overhead sits in planning, not role count.
- Spec-first tooling adoption (Kiro, Spec Kit) or a heavier planner: no published outcome data a year after launch; planning is already 29 to 55 percent of local spend.
- A plugin-owned serial merge queue daemon: the published queue gains are batching under contention; a serial queue is a documented bottleneck; the local cost is conflict resolution, which T-0489 addresses.
- Dropping the L1 and docs-only verifier skips now: no local record shows what they miss; T-0485 is the measurement step that comes first.

## Risks

- The done-when says every pattern has a dated source; it holds at the family level, but the Cursor, Claude Code plan mode and sub-agent, Zuul and GitLab rows are undated docs or snippets with no outcome data, and no Cursor default-loop documentation was found.
- No independent check of the research rows was run; several headline numbers (SWE-Review, Devin 67 percent, DORA, the Agentless version split) rest on secondary summaries and are marked so.
- T-0486's rerun was not performed; change 3 assumes T-0473's rule could cover the codex case.
- The T-0489 cost is a level-scaled estimate from the benchmark's lean-arm range, not a measured L3 solo run.
- The verdict on the verifier rests on over-reach and first-pass data; nothing local tests whether a verified pass met intent, so section 3.1 could be wrong in the direction the benchmark names.

## Carry forward

- Report: `/Users/kimgranlund/Projects/nonoun/sdlc-lite/docs/reports/2026-10-12-industry-alternatives-review.md` (verdict table section 4, ranked changes section 5).
- Solo quality claim untested: `docs/reports/solo-vs-lean-benchmark-2026-10-04.md` line 38; `docs/kpi/005-solo-first-pass-rate.md` line 22.
- 0 verifier over-reach in 34 first-round non-passes: `docs/reports/2026-10-11-solo-fails-and-blocks.md` lines 5, 52 to 57.
- Planning plus plan review 55.5 percent of agent-ui spend, verifiers 7.5 percent: `docs/reports/fleet-retro-2026-10-06.md` line 16; `docs/specs/sdlc-lite/pillars.md` line 35.
- Red-checkpoint phase read against the working tree at HEAD (T-0473): `plugins/sdlc-lite/scripts/redck.py` docstring; finding 6 at `docs/reports/2026-10-12-maison-wave-7b-mechanics.md` line 16.
- T-0458 retest verdict drop: `docs/reports/2026-10-12-builder-overlay-retest.md` lines 5, 13, 53.
- Wave merge conflicts 5 of 8, generated files: `docs/planning/merge-ops-and-queue.md` lines 16, 18.
- Agentless reproduction-test ablation 77 to 96 fixes: https://arxiv.org/pdf/2407.01489 (2024-07).
- Critic loops at up to 50x cost, no gain: https://arxiv.org/abs/2407.01502 (2024-07-01).
- LLM judge self-preference bias: https://arxiv.org/abs/2404.13076 (2024-04).
- Multi-agent token multiples (4x, 15x) and the coding caveat: https://www.anthropic.com/engineering/multi-agent-research-system (2025-06-13, vendor claim).
- GitHub merge queue 33 percent wait cut: https://github.blog/engineering/engineering-principles/how-github-uses-merge-queue-to-ship-hundreds-of-changes-every-day (2024-03-06); Uber 53 percent CI cost: https://arxiv.org/html/2501.03440v2 (2025).
- Spec-driven tools have no outcome data: https://arxiv.org/abs/2605.01160 (2026-05-01), https://arxiv.org/abs/2604.05278 (2026-04-07).
