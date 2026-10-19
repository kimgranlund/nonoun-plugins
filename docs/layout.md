# Layout

Any other folder directly under `docs/` is a topic. It holds the designs, specifications, and decisions for one concept.

## Homes

- `work/`
- `specs/`
- `planning/`
- `decisions/`
- `goals/`
- `kpi/`
- `references/`
- `guides/`
- `reports/`
- `assets/`
- `archive/`
- `other/`

## Kinds

| id | kind | holds | not | why | writer | form | life | entry | read | owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `work/` | work | ticket and task folders, the generated `ROADMAP.md` and `NOTES.md`, and `evals/`, `proposals/`, `archive/` and `fleet.json`; here since `.sdlc/config` set `work_root: docs/work` (T-0636) | designs and plans under review -> `planning/` | work records next to the docs they change | `tickets.py` | `NNNN-slug/handoff.md` | close dot-renames in place | - | running or closing a ticket | `tickets.py` |
| `specs/` | specs | what the system is and must do | plans -> `planning/` | one place to trust | people | kebab-case | supersede to `archive/` | - | defining the system | `docs_check.py` |
| `planning/` | planning | proposals and plans under review | built facts -> `specs/` | decisions need a place | people | `status:` front matter | accept, then `archive/` | - | deciding or scheduling | `docs_check.py` |
| `decisions/` | decisions | one numbered decision per file | narrative -> `specs/` | reasons outlive people | people | `NNNN-slug.md`, `status:` | supersede | - | asking why | `docs_check.py` |
| `goals/` | goals | one intended outcome per file | change plans -> `planning/` | steering needs a record | people | `NNN-slug.md`, `status:` | achieve or drop, then `archive/` | - | steering the work | `docs_check.py` |
| `kpi/` | kpi | one measure per file | values over time -> `reports/` | a number needs a command | people | `NNN-slug.md`, `measure:` | edit in place | - | measuring an outcome | `docs_check.py` |
| `references/` | references | lookup tables and listings | steps -> `guides/` | fast lookup | people | kebab-case | edit in place | - | looking something up | `docs_check.py` |
| `guides/` | guides | procedures a person follows | tables -> `references/` | do, not explain | people | kebab-case | edit in place | - | doing a task | `docs_check.py` |
| `reports/` | reports | dated evidence | steps -> `guides/` | evidence stays fixed | people | `YYYY-MM-DD-slug.md` | immutable | - | checking what was verified | `docs_check.py` |
| `assets/` | assets | non-Markdown files cited by a document | Markdown -> its home | keep prose clean | people | kebab-case | with its citer | - | opening a cited file | `docs_check.py` |
| `archive/` | archive | superseded or retired documents | live documents -> their home | history without noise | people | `status:`, `superseded-by:` | keep | - | researching history | `docs_check.py` |
| `other/` | other | unsorted documents | anything with a home -> that home | a visible backlog | anyone | `owner:`, `review-by:` | review-by date | - | sorting the inbox | `docs_check.py` |

## Decide

1. Is it a ticket or task record, or the generated roadmap or notes file? yes -> `work/`
2. Is it a picture, diagram source or data file? yes -> `assets/`
3. Is it evidence of something that happened on a date? yes -> `reports/`
4. Is it one choice with its reasons and alternatives? yes -> `decisions/`
5. Is it a proposal, roadmap or plan under review? yes -> `planning/`
6. Is it an outcome to steer toward, with an owner and a status? yes -> `goals/`
7. Is it a measure with a command that runs it, a unit and a target? yes -> `kpi/`
8. Is it steps a person follows? yes -> `guides/`
9. Is it a table, listing or glossary you look things up in? yes -> `references/`
10. Does it describe what the system is or must do? yes -> `specs/`
11. Is it retired or superseded? yes -> `archive/`
otherwise -> `other/`

## Frozen paths

- `docs/reports/`
- `plugins/sdlc-lite/bench/results/`
- `plugins/sdlc-lite/adapters/codex/agents/`

## Legacy

- `reports/agent-command-live-run.md`
- `reports/agent-spawn-hook-live-run.md`
- `reports/ask-skill-live-run.md`
- `reports/broken-links-allowlist.md`
- `reports/broken-links-cleanup.md`
- `reports/carry-forward-live-run.md`
- `reports/codex-account-models-2026-09-30.md`
- `reports/codex-conductor-solo-live-run.md`
- `reports/codex-fanout-live-run.md`
- `reports/codex-tier-mirror-2026-09-30.md`
- `reports/defect-fixes-0.20.10.md`
- `reports/defect-fixes-0.20.9.md`
- `reports/docs-schema-design-review.md`
- `reports/dual-host-readiness-recovery.json`
- `reports/entry-files-live-run.md`
- `reports/evals-live-run.md`
- `reports/fanout-solo-live-run.md`
- `reports/fix-batch-0.20.11.md`
- `reports/fleet-retro-2026-10-06.md`
- `reports/haiku-alias-2026-09-30.md`
- `reports/handoff-freeze-live-run.md`
- `reports/hook-perf.md`
- `reports/idle-host-watcher-design-review.md`
- `reports/lane-gate.md`
- `reports/lean-sdlc-cost-control-review.md`
- `reports/lean-sdlc-design-review-2.md`
- `reports/lean-sdlc-design-review.md`
- `reports/messages-idle-host-limit-2026-10-01.md`
- `reports/messages-live-run.md`
- `reports/messages-wait-live-run.md`
- `reports/naming-sdlc-lite.md`
- `reports/native-codex-smoke.json`
- `reports/nested-entry-file-loading.md`
- `reports/onboard-lane-text.md`
- `reports/onboard-live-run.md`
- `reports/parked-tickets-review-2026-10-06.md`
- `reports/plan-reviewer-live-run.md`
- `reports/plan-skills-live-run.d/**`
- `reports/plan-skills-live-run.md`
- `reports/planner-l3-opus-2026-09-30.md`
- `reports/progressive-context-gap-analysis-review.md`
- `reports/proposals-live-run.md`
- `reports/readiness-recovery-validation.md`
- `reports/release-0.19.0.md`
- `reports/release-0.20.0.md`
- `reports/release-0.20.1.md`
- `reports/release-0.20.10.md`
- `reports/release-0.20.11.md`
- `reports/release-0.20.12.md`
- `reports/release-0.20.2.md`
- `reports/release-0.20.3.md`
- `reports/release-0.20.4.md`
- `reports/release-0.20.5.md`
- `reports/release-0.20.6.md`
- `reports/release-0.20.7.md`
- `reports/release-0.20.8.md`
- `reports/release-0.20.9.md`
- `reports/rename-validation-to-reports.md`
- `reports/reorg-inventory-live-run.md`
- `reports/replan-cost-remeasure.md`
- `reports/repo-onboarding-design-review-2.md`
- `reports/repo-onboarding-design-review-3.md`
- `reports/repo-onboarding-design-review.md`
- `reports/role-bodies-subagent.md`
- `reports/role-result-schema-live-run.md`
- `reports/role-routing-probe.md`
- `reports/runner-family-task-dir-live-run.md`
- `reports/solo-budget-gate-live-run.md`
- `reports/solo-close-live-run.md`
- `reports/solo-cost-live-run.md`
- `reports/solo-live-run.md`
- `reports/solo-vs-lean-benchmark-2026-10-04.md`
- `reports/supervisor-live-run.md`
- `reports/ticket-root-router-live-run.md`
- `reports/workflow-stage-pilot/**`
