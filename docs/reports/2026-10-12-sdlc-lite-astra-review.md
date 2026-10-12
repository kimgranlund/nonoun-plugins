---
doc-type: report
date: 2026-10-12
scope: SDLC Lite 0.22.5
---
# SDLC Lite independent Astra review

SDLC Lite has coherent shared role contracts, explicit host adapters, and substantial offline coverage, but its current tree has defects at the interfaces between those parts. The highest-priority author task is to repair invalid Claude agent frontmatter and verify actual discovery. Two Claude hook integrations fail in reproducible local fixtures. Codex profile freshness has contradictory output instructions and can be bypassed by the normal exchange API when its separate manual check is omitted. The review found no reason to change the user's model or effort choices.

This is a source and focused integration review, not live certification of either host. **[V]** means checked against the reviewed source or an observed fixture. **[U]** marks an unverified runtime consequence or limitation. Priorities below express recommended repair order: P1 warrants immediate host verification; P2 affects a supported workflow; P3 is guidance maintenance.

## Findings and bounded repairs

### F1 — P1: Repair invalid YAML in Claude agent definitions

**Scope:** Claude discovery and generated declarations. **Confirmed:** invalid YAML. **Unverified:** how Claude 2.1.296 handles these particular files at runtime.

**[V] Evidence.** The generator retains the source description's surrounding quotes at [claude_roles.py:104](../../plugins/sdlc-lite/scripts/claude_roles.py#L104), then appends a level suffix outside that scalar at [claude_roles.py:180](../../plugins/sdlc-lite/scripts/claude_roles.py#L180). For example, [builder-L2.md:3](../../plugins/sdlc-lite/agents/builder-L2.md#L3) ends its quoted description before `Level L2: opus low.`. All **22 generated Claude definitions** fail a standard YAML parse. The parser reports `expected <block end>, but found '<scalar>'` at the appended `Level` text. The shared [conductor.md:3](../../plugins/sdlc-lite/agents/conductor.md#L3) also fails: its unquoted description contains the colon-space sequence in `"agent": "sdlc-lite:conductor"`, producing `mapping values are not allowed here`. In total, **23 of 34 agent frontmatter blocks fail**, while all 38 skill frontmatter blocks parse.

**Impact and steelman.** Claude documents these files as YAML frontmatter. A loader that follows that contract cannot parse these definitions normally, putting the plugin's primary launch routes at risk. However, `claude plugin validate plugins/sdlc-lite` succeeds, and this review did not execute live agent discovery. A permissive host parser could recover some fields. Therefore this finding does **not** claim that 23 agents were observed unavailable. Generated parity also passes because checked-in files reproduce the same invalid output; parity does not establish syntax validity.

**Fix.** Parse the source description as a scalar and serialize the entire augmented description once; quote the conductor description. Regenerate through the generator. Preserve all model and effort values. Add one actual frontmatter parse to generation validation rather than another byte-comparison assertion.

**Validate.** Parse all 34 agent files; retain the current malformed description as a rejecting fixture and a quoted whole-description positive case. Then use a fresh Claude session to discover the plugin agents and perform one prepared scout dispatch. The in-memory quoted-description positive control already parses in this review. [Probe transcript](2026-10-12-sdlc-lite-astra-review/probes.txt).

### F2 — P2: Preserve spaces in prepared Claude handoff paths

**Scope:** Claude prepared role spawning.

**[V] Evidence.** [dispatch.py:778](../../plugins/sdlc-lite/scripts/dispatch.py#L778) emits an absolute `Handoff:` path. [block-role-spawn.sh:86](../../plugins/sdlc-lite/hooks/block-role-spawn.sh#L86) truncates it at the first whitespace before locating the dispatch record. A real `dispatch.py prepare scout L1` in a disposable repository named `plain` yields a payload accepted by the hook, exit 0. The same operation under `with spaces`, passing the printed fields unchanged, is rejected with exit 2: `no dispatch record ... beside .../with`.

**Impact and steelman.** A valid repository path can prevent every prepared role from starting. Ignoring trailing explanatory text was an intentional compatibility choice, also documented in [conductor.md:41](../../plugins/sdlc-lite/agents/conductor.md#L41); it nevertheless conflicts with the prepare command's own path output. This is not a fixture inventing an invalid dispatch.

**Fix.** Give the handoff locator an unambiguous encoding and parse it as a whole path. Keep any optional explanation outside that field. Also quote the `cd` path in the generated execution-tree instruction at [dispatch.py:780](../../plugins/sdlc-lite/scripts/dispatch.py#L780).

**Validate.** Prepare and pass the exact spawn payload through the hook for plain paths, spaces in both project and task paths, and any supported explanatory suffix. Assert that a truly missing dispatch still fails. One fresh-Claude smoke run under a path with spaces should complete before claiming host validation.

### F3 — P2: Connect Claude handoff freezing to prepared attempts

**Scope:** Claude default subagent transport; the legacy shell runner has a different marker lifecycle.

**[V] Evidence.** [warn-handoff-edit.sh:14](../../plugins/sdlc-lite/hooks/warn-handoff-edit.sh#L14) recognizes only sibling `*.running` files. The current prepared transport writes running attempt and dispatch JSON at [dispatch.py:815](../../plugins/sdlc-lite/scripts/dispatch.py#L815) through line 822, but no such marker. In both disposable prepared scout cases, the attempt is `running`, there are zero running markers, and an Edit of its handoff passes silently even with `SDLC_HANDOFF_EDIT_MODE=deny`. Adding the expected marker makes the same hook reject the same edit, exit 2.

**Impact and steelman.** The default transport bypasses the advertised warning and deny modes while a role reads the handoff. The hook itself works on its older marker input; the integration is missing. Completion-time handoff hashing still provides a `stale_input` signal, so this is not a claim that all stale-input detection disappeared. Nor does it demand implementing the separately deferred stale-result routing policy.

**Fix.** Prefer one authoritative lifecycle source: have the hook recognize live prepared attempts, or make prepare/record/recover consistently own the existing marker. Avoid leaving two independent definitions of a live run.

**Validate.** Exercise prepare → handoff edit → record and prepare → recovery. A live attempt must warn or deny according to configuration; a completed or recovered attempt must stop doing so. Test the actual prepare output, not only a hand-created marker.

### F4 — P2: Make the Codex fingerprint envelope compatible with role output

**Scope:** Generated Codex profiles and shared output contracts.

**[V] Evidence.** [codex_roles.py:104](../../plugins/sdlc-lite/scripts/codex_roles.py#L104) requires `profile: <fingerprint>` to be the first line of both the first message and final report. **23 of 28 generated profiles** also include the literal instruction `nothing before the first heading`; for example the shared [scout.md:16](../../plugins/sdlc-lite/agents/scout.md#L16). Both requirements cannot hold for the same final message.

**Impact and steelman.** A role has to violate one output instruction. A capable model may prioritize the appended fingerprint, and the result-section validator can still accept useful content. No live bad report was observed. The contradiction nevertheless makes a deliberately strict report contract ambiguous at exactly the point where freshness is checked.

**Fix.** Define a small host envelope plus role body, or explicitly exempt the Codex fingerprint line from the shared first-heading rule during generation. Keep Claude output unchanged. State whether stored result artifacts retain or remove that envelope.

**Validate.** Check every generated profile for a consistent output contract; pass a fingerprinted report through the actual exchange and result parser. Retain one missing-envelope and one malformed-body rejecting case.

### F5 — P2: Bind Codex freshness checks to the native exchange

**Scope:** Codex native pipeline exchange; this is a workflow integrity gap, not host attestation or an adversarial security claim.

**[V] Evidence.** The helper at [codex_roles.py:117](../../plugins/sdlc-lite/scripts/codex_roles.py#L117) correctly classifies a missing fingerprint as `unknown`, a stale one as `refused`, and the current one as `ready`. But the request at [codex_exchange.py:53](../../plugins/sdlc-lite/scripts/codex_exchange.py#L53) carries no expected fingerprint, and [codex_exchange.py:89](../../plugins/sdlc-lite/scripts/codex_exchange.py#L89) checks ownership, response destination, and nonempty text without invoking that helper. Using a real waiting exchange in a subprocess, all three reports—missing, stale, current—were accepted with respond exit 0, exchange exit 0, `is_error: false`, and request status `received`.

**Impact and steelman.** The adapter separately instructs the conductor to perform a handshake. A fully compliant conductor can enforce that manual step, so the fixture does not prove every current run is unsafe or that an old profile executed. It proves the exchange accepts an otherwise ordinary report without the required check. The documented attempt binding is also not materialized in the request; checking against regenerated files later can confuse a mid-run plugin update with the revision actually dispatched. A final-report check alone cannot establish that checking occurred before edits.

**Fix.** Store the expected profile fingerprint with the request/attempt and require the same binding when accepting a normal response. Treat missing or stale fingerprints as explicit incomplete/refused outcomes. If a pre-edit handshake is an intended enforceable guarantee, make the initial acknowledgement a distinct exchange state; otherwise accurately describe it as a conductor instruction. A self-reported fingerprint remains self-reported even after this fix.

**Validate.** Reuse the saved three-case fixture: current succeeds; missing and stale cannot produce an accepted normal result. Add one case where generated files change after dispatch but the attempt's binding remains stable. No broad permission changes are needed.

### F6 — P2: Make the open-question sweep honor the ticket layout

**Scope:** Shared `/ask` workflow on Claude and Codex.

**[V] Evidence.** [ask/SKILL.md:24](../../plugins/sdlc-lite/skills/ask/SKILL.md#L24) searches blocked and deferred tickets only under `.sdlc/tickets`, although [ticket/SKILL.md:23](../../plugins/sdlc-lite/skills/ticket/SKILL.md#L23) makes that root opt-in and explicitly supports flat layout. A disposable flat blocked ticket is missed with exit 2 (`No such file or directory`); the otherwise identical search from the actual root finds it with exit 0. A blocked ticket with no result or gap lines is not rescued by the following verdict/gap searches.

**Impact and steelman.** Following the supplied commands can miss a real blocker and lead toward `Nothing open.`. The prose says to inspect tickets, and an attentive conductor may recover by noticing the missing directory. That recovery is not encoded in the workflow. The searches are also described as runnable from a supplied task directory even though their paths are repository-relative.

**Fix.** Resolve the configured ticket root from the repository root using existing ticket layout logic, then search it. Keep the task filter separate. Follow the existing closed-ticket exclusion conventions.

**Validate.** Flat and topics fixtures with the same blocked/deferred items should produce the same open-question inventory. Include a supplied-task-directory case and an already-resolved item that must be excluded.

### F7 — P3: Align current operator guidance with implemented lifecycle and inventory

**Scope:** Shared conductor instructions and Codex reference documentation.

**[V] Evidence.** [conductor.md:37](../../plugins/sdlc-lite/agents/conductor.md#L37) says recording with no result closes the attempt as failed and prevents another record. [dispatch.py:1128](../../plugins/sdlc-lite/scripts/dispatch.py#L1128) instead returns exit 2 and leaves it running, unless explicit failure closure is requested. This implementation deliberately permits recording again. Separately, [codex-role-execution.md:25](../references/codex-role-execution.md#L25) says 25 definitions / 21 base and omits the three solo profiles; the current generator produces 28 / 24.

**Impact and steelman.** The script's diagnostic gives the correct recovery, so a conductor reading stderr can recover. The authoritative role prose nevertheless describes the opposite state transition and can encourage unnecessary reruns or misreported state. The profile count is a smaller discovery/documentation defect. Dated compatibility evidence was not treated as a promise to describe today's inventory.

**Fix and validate.** Update only the current conductor recovery paragraph and current Codex inventory reference. Derive the counts from generator output. Include the existing no-result retry behavior in the targeted documentation check; do not change lifecycle behavior to match stale prose.

## Author action list

These can be separate maintenance tickets, each with a narrow done condition:

1. **Claude frontmatter:** repair generator serialization and conductor description; parse every definition; verify discovery in a fresh host.
2. **Claude dispatch paths:** pass prepared paths with spaces through the actual spawn hook and a smoke role.
3. **Claude handoff freeze:** share the prepared attempt lifecycle with the edit hook and verify completion/recovery cleanup.
4. **Codex report envelope:** resolve the contradictory first-line contract across all profiles.
5. **Codex exchange freshness:** persist the dispatch binding and reject missing/stale normal responses.
6. **Layout-aware `/ask`:** use the supported ticket-root resolver and cover both layouts.
7. **Operator guidance:** correct no-result recovery and the current Codex role inventory.

For the Claude-based author, items 1–3 are directly reproducible without Codex. Items 4–5 need a callable named-role Codex session for live sign-off after the offline fixtures pass. No finding requires changing the approved role/model tables, increasing levels, introducing another verifier, or rewriting the workflow architecture.

## Complete skill and command coverage

**[V] Inventory:** 38 skill entry files were read. Their frontmatter all parses as YAML. Two explicitly set `user-invocable: false`: `handoff-format` and `level-rubric`. The other 36 are discovery surfaces. There is no separate plugin commands directory; Claude command discovery is through these skills, while Codex exposes skills and uses the adapter's tool/path translations. “Reviewed” here means instructions and routing inspected, not that the model-executed workflow was run.

| Skill / command surface | Review coverage and conclusion |
|---|---|
| [agent](../../plugins/sdlc-lite/skills/agent/SKILL.md) | Name routing, solo versus question roles, deferral to owning skills; generated-agent finding F1 applies. |
| [architect](../../plugins/sdlc-lite/skills/architect/SKILL.md) | Handoff and design-role dispatch; host translation and source-role contract read. |
| [ask](../../plugins/sdlc-lite/skills/ask/SKILL.md) | Sweep, question batching, unattended behavior; layout failure F6. |
| [bench](../../plugins/sdlc-lite/skills/bench/SKILL.md) | Throwaway task flow, hidden-test grading, cost/attempt semantics; no benchmark executed. |
| [board](../../plugins/sdlc-lite/skills/board/SKILL.md) | Script-rendered status and artifact ownership; board selftest passes. |
| [build](../../plugins/sdlc-lite/skills/build/SKILL.md) | Level selection, prepared dispatch, result/escalation handoff. |
| [chain](../../plugins/sdlc-lite/skills/chain/SKILL.md) | Lane choice, review/split, retry/bump/replan, loose ends and closure; steps selftest passes. |
| [checking-rules](../../plugins/sdlc-lite/skills/checking-rules/SKILL.md) | Symmetric evidence, independent checking and steelmanning; applied in this review. |
| [checks-that-bite](../../plugins/sdlc-lite/skills/checks-that-bite/SKILL.md) | Discriminating checks and observed negative controls; applied in focused probes. |
| [clarify](../../plugins/sdlc-lite/skills/clarify/SKILL.md) | Goal/delta/done-condition refinement, ambiguity and unattended gaps; saved evals inventoried, not model-graded. |
| [decompose](../../plugins/sdlc-lite/skills/decompose/SKILL.md) | Structure/behavior coverage, conditional domain references; coverage-check selftest passes. |
| [dig](../../plugins/sdlc-lite/skills/dig/SKILL.md) | Archaeologist routing, history evidence, read-only intent. |
| [fanout](../../plugins/sdlc-lite/skills/fanout/SKILL.md) | Lane isolation, prep/land, integration gates, host driver split; broad fanout selftest did not finish in this review. |
| [file](../../plugins/sdlc-lite/skills/file/SKILL.md) | Draft records, publish authorization, follow-up classifications and closure. |
| [fix](../../plugins/sdlc-lite/skills/fix/SKILL.md) | Explicit fast-lane trigger, builder/verifier separation, inline ticket close. |
| [fleet-retro](../../plugins/sdlc-lite/skills/fleet-retro/SKILL.md) | Collection, evidence labels, sampled verification and approved filing; no fleet run. |
| [fleet-status](../../plugins/sdlc-lite/skills/fleet-status/SKILL.md) | Fixed rendered order, needs-user collection, machine/release state; schema inventoried. |
| [grill](../../plugins/sdlc-lite/skills/grill/SKILL.md) | Cascading design decisions and ratification; no live interview. |
| [handoff](../../plugins/sdlc-lite/skills/handoff/SKILL.md) | Context capture, self-contained task boundary and artifacts. |
| [handoff-format](../../plugins/sdlc-lite/skills/handoff-format/SKILL.md) | Reference-only; ticket/task/step/result shapes and shared run operations. |
| [level-rubric](../../plugins/sdlc-lite/skills/level-rubric/SKILL.md) | Reference-only; role/level selection and host-owned model tables; values preserved. |
| [onboard](../../plugins/sdlc-lite/skills/onboard/SKILL.md) | Entry-file setup, managed blocks, preserving repository instructions; no user config changed. |
| [open-questions](../../plugins/sdlc-lite/skills/open-questions/SKILL.md) | Task-local close-out and unresolved defaults; distinct from broader ask sweep. |
| [plan](../../plugins/sdlc-lite/skills/plan/SKILL.md) | Planner dispatch, ordered steps, readiness and review routing. |
| [plan-campaign](../../plugins/sdlc-lite/skills/plan-campaign/SKILL.md) | Wave planning, lane partition and outcome constraints; planning-only scope. |
| [plan-doc](../../plugins/sdlc-lite/skills/plan-doc/SKILL.md) | Executable plan structure, authorization and lint routing. |
| [plan-fanout](../../plugins/sdlc-lite/skills/plan-fanout/SKILL.md) | Nonoverlap, lane caps, gate/budget command construction and dry run. |
| [plan-goal](../../plugins/sdlc-lite/skills/plan-goal/SKILL.md) | Done condition, numeric stops, authority and goal-block generation. |
| [plan-loop](../../plugins/sdlc-lite/skills/plan-loop/SKILL.md) | Idempotence, cadence and stop condition; host loop syntax remains a live-check limitation. |
| [plan-verification](../../plugins/sdlc-lite/skills/plan-verification/SKILL.md) | Outcome, measure/baseline, rubric and negative control; distinct from step verifier. |
| [report](../../plugins/sdlc-lite/skills/report/SKILL.md) | Thread views, structured record/output, evidence and context reporting. |
| [research](../../plugins/sdlc-lite/skills/research/SKILL.md) | Outside-world citations, researcher levels and handoff. |
| [review-traces](../../plugins/sdlc-lite/skills/review-traces/SKILL.md) | Mechanical ingest/detect, diagnosis, verification and approved filing; no historical traces ingested. |
| [run-plan](../../plugins/sdlc-lite/skills/run-plan/SKILL.md) | Preflight, deterministic completion/stop loop, dispatch and recovery; run-rules reference read. |
| [scout](../../plugins/sdlc-lite/skills/scout/SKILL.md) | Map-only handoff and dispatch; actual prepare used by focused hook fixtures. |
| [sdlc-lite](../../plugins/sdlc-lite/skills/sdlc-lite/SKILL.md) | Codex adapter, install/preflight/native exchange/exec split and limitations; F4–F5. |
| [ticket](../../plugins/sdlc-lite/skills/ticket/SKILL.md) | Typed creation, numbering, layouts, close/follow-up consent and roadmap; tickets selftest passes. |
| [verify](../../plugins/sdlc-lite/skills/verify/SKILL.md) | Independent role dispatch, result acceptance and next-step routing. |

### Shared and generated agents

All 12 shared role bodies were read. Generated declarations were covered through both generators, complete generated parity checks, full YAML/TOML inventories, and the source bodies/overlays from which they are built. Repeated generated prose was not treated as 50 independent designs.

| Shared contract | Claude generated levels | Codex base levels | Contract focus |
|---|---|---|---|
| [conductor](../../plugins/sdlc-lite/agents/conductor.md) | Shared session agent | L1 | Routing, host dispatch, recovery, pruning, escalation and closure; F1/F7. |
| [messenger](../../plugins/sdlc-lite/agents/messenger.md) | Shared session agent | L1 | Mailbox ownership, delivery and active-parent lifetime. |
| [solo](../../plugins/sdlc-lite/agents/solo.md) | L1–L3 | L1–L3 | Small-ticket end-to-end work, independent verification and cost recording. |
| [scout](../../plugins/sdlc-lite/agents/scout.md) | L1 | L1 | Code map and bounded read-only search. |
| [researcher](../../plugins/sdlc-lite/agents/researcher.md) | L1–L3 | L1–L3 | Outside evidence, citations and uncertainty. |
| [architect](../../plugins/sdlc-lite/agents/architect.md) | L1 | L1 | Design fit, alternatives and assessment artifacts. |
| [archaeologist](../../plugins/sdlc-lite/agents/archaeologist.md) | L1 | L1 | Git history, decisions and landmines. |
| [planner](../../plugins/sdlc-lite/agents/planner.md) | L1–L3 | L1–L3 | Buildable steps, acceptance criteria and readiness. |
| [plan-reviewer](../../plugins/sdlc-lite/agents/plan-reviewer.md) | L1 | L1 | Independent plan critique and decision gaps. |
| [builder](../../plugins/sdlc-lite/agents/builder.md) | L1–L5 | L1–L5 | Scoped implementation, evidence and blocked/plan-defect reports; level overlay read. |
| [verifier](../../plugins/sdlc-lite/agents/verifier.md) | L1–L3 | L1–L3 | Independent acceptance checking, negative controls and actionable verdicts. |
| [filer](../../plugins/sdlc-lite/agents/filer.md) | L1 | L1 | Draft records, warnings and classified follow-ups. |

**[V] Totals:** 22 generated Claude rows, all represented among Codex's 24 base profiles; Codex additionally has conductor and messenger. Four Codex alternates cover verifier L1–L3 and plan-reviewer L1, for 28 TOML files. Claude's 34 Markdown files consist of the 12 shared contracts plus 22 generated rows. Fixed host model/effort declarations were compared with the authoritative tables; no values were changed.

### Script, hook and packaging coverage

The script inventory contains **58 top-level script files** plus the decomposition coverage script. All are accounted for below. Source review was concentrated on runtime boundaries and the findings; this is not a claim to have read every line of every test fixture or helper.

| Surface | Files / behavior covered |
|---|---|
| Execution and declarations | `run.sh`, `dispatch.py`, `solo_run.py`, `run_lifecycle.py`, `readiness.py`, `claude_roles.py`, `codex_roles.py`, `codex_exec.py`, `codex_exchange.py`: host split, model routing, attempts, records, locks, cancellation, install ownership, fingerprint and recovery. |
| Work state and integration | `tickets.py`, `steps.py`, `order.py`, `results.py`, `fanout.py`, `lanes.py`, `gate_lock.py`, `verify_scope.py`, `specgate.py`, `redck.py`: workflow contracts and selected runtime paths; completed suites listed below. |
| Planning and authoring | `plan_check.py`, `plan_doc.py`, `plan_done.py`, `prompt_lint.py`, `reply_lint.py`, `cite_check.py`, `onboard.py`, `docs_check.py`, `reorg.py`, `rename_refs.py`, `promote.py`, `inventory.py`: entry routes and validation ownership inventoried; later suites were not reached. |
| Reporting, cost and fleet | `board.py`, `report.py`, `budget.py`, `cost_estimate.py`, `solo_stats.py`, `statusline.sh`, `messages.py`, `supervisor.py`, `fleet_collect.py`, `fleet_detect.py`, `fleet_config.py`, `fleet_status.py`, `footprint.py`, `traces.py`, `evals.py`, `proposals.py`: state/cost/evidence boundaries and public workflow consumers inspected. |
| Benchmark and maintenance launchers | `bench.sh`, `bench-dir.sh`, `bench-summary.sh`, `reap-tmp-worktrees.sh`: launcher ownership and cleanup scope inventoried; no benchmarks or cleanup jobs run. |
| Check entry points | `check.sh`, `check.py`, `codex-selftest.py`, `lifecycle-selftest.py`, `run-selftest.sh`, `hook-selftest.sh`, `hook-live-probe.sh`, and decomposition's `coverage_check.py`: offline versus live distinction and execution order inspected. |

**[V] Claude hook registration:** [adapters/claude/hooks.json](../../plugins/sdlc-lite/adapters/claude/hooks.json) registers nine guards: background, publish, pattern-kill, stray-worktree, repository-format, disk-scan, role-spawn, role-write, and handoff-edit. The shared `_role.sh` resolver, registration, role guards and handoff hook were inspected; F2–F3 have executable probes. The other hook implementations were not independently exhaustively audited in this review, and the later general hook selftest was not reached.

**[V] Packaging:** Claude and Codex manifests both identify version 0.22.5; Claude points to its host hook registration, and Codex points to the skills directory. Marketplace parity, package identity, skill routes, hook isolation and context links pass the repository packaging check. Installing the plugin alone does not install project Codex roles; the explicit managed install route and refusal to overwrite user edits are documented. No project configuration was installed for this review.

## Checks actually run

| Check | Observed result |
|---|---|
| `python3 scripts/check-packaging.py` | PASS. |
| `claude plugin validate plugins/sdlc-lite` | Exit 0. Warning that root CLAUDE.md is not loaded as consumer project context; consistent with maintenance guidance, not counted as a defect. |
| Both generated-agent parity checks | PASS in the broad suite; generated syntax defect F1 survives parity. |
| `claude_roles.py selftest` | PASS. |
| `dispatch.py selftest` | PASS. |
| `codex-selftest.py` | 37 tests, OK. |
| `lifecycle-selftest.py` | 6 tests, OK. |
| `check.py` | FAIL on the pre-existing unrelated Progressive Context link to its untracked performance contract; not attributed to SDLC Lite. |
| Decomposition coverage, tickets, board, results, evals, proposals, steps, order selftests | Each completed with PASS. |
| `bash plugins/sdlc-lite/scripts/check.sh` as a whole | **INCOMPLETE**. Stopped by this reviewer during fanout selftests after the preceding checks. Owned shell exited 143. Later checks, shellcheck and the suite's final validator were not reached. This is neither a full pass nor a diagnosed fanout failure. |
| [Focused probes](2026-10-12-sdlc-lite-astra-review/probes.py) | Exit 0; full [observed output](2026-10-12-sdlc-lite-astra-review/probes.txt) retains positive controls and defect cases for F1–F6. Temporary Git projects and exchange subprocesses only; no model calls. Requires Python, PyYAML, Git, Bash and jq. |
| Report links and whitespace | Checked after authoring; recorded in the accompanying check summary. |

The broad suite's completed output and stop condition are summarized in [checks.txt](2026-10-12-sdlc-lite-astra-review/checks.txt). Other Claude fanout/check processes were running concurrently in other worktrees. Only this review's exact suite process tree was stopped. No slowdown or resource-contention outcome is filed as a plugin defect.

## Host interfaces, limits and omitted validation

**[V] Installed tools:** Claude Code 2.1.296 and Codex CLI 0.162.1. Official [Claude subagent documentation](https://code.claude.com/docs/en/sub-agents) establishes the YAML frontmatter contract and current model/effort configuration. Its current per-invocation effort support also means blanket historical claims that Agent cannot select effort should be qualified by host version; fixed generated profiles remain a valid product choice. Official [Claude hook documentation](https://code.claude.com/docs/en/hooks) describes event/agent fields, not an equivalent Codex enforcement mechanism.

**[V] Codex capability boundary:** Official [Codex subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) supports project agent TOML definitions. This does not prove every Codex client exposes a named-role selector. This review session's collaboration tool schema provides model/effort but no custom named-agent selector, and this checkout has no installed project Codex configuration. The adapter correctly requires a callable-role preflight. **[U]** A live pipeline with these custom roles on CLI 0.162.1 remains unverified here; a restart alone is not evidence of callability. No nested model process was launched to conceal this limitation.

**[V] Documented limitations, not new defects:** Codex read-only checking roles can be unable to execute write-requiring test setup; the adapter requires reporting that limitation rather than weakening the sandbox or declaring a pass. Codex dollar spend is unknown, so cost/budget claims cannot be inferred from Claude estimates. Claude write hooks govern particular tools and role resolution; they are not a general shell sandbox. An inherited `SDLC_ROLE` can take precedence in role resolution, as the hook guide documents. These distinctions should remain explicit in consumer guidance.

**[U] Not live-tested:** Claude agent loading, actual role tool permissions, background completion/pruning/resumption, full solo/chain/fanout, benchmark grading, fleet operations, publishing flows, the Codex native exchange with a real named agent, and host goal/loop scheduling. The messenger's persistent Claude behavior and Codex report/respawn fallback are documented separately; no idle-parent wake capability was assumed. Approval and external-write policies were read as contracts, not exercised against external services.

Every skill entry and shared role body is covered, but conditional reference resources were inventoried and read selectively, and underlying scripts received targeted review rather than an exhaustive line audit. Saved clarification evaluations, benchmark task corpora and historical run evidence were not model-executed. Closed ticket folders, historical reports and unrelated documents were not used as evidence. The review did not change runtime scripts, generated definitions, models, user settings, tickets or branches, and did not commit.

## Evidence binding and reviewer configuration

**[V] Reviewed baseline:** HEAD `a3e2cd9b273ade52a66978f8e1938ad8e7fae948`, SDLC Lite 0.22.5. The [source snapshot](2026-10-12-sdlc-lite-astra-review/source-snapshot.json) contains SHA-256 hashes for all 472 tracked SDLC Lite files. Its aggregate hash over the sorted file/hash mapping is `d05af6caa41b3ec8d9db732dcb14e502111dcdd56f733e476f69e9f7556d78d5`. The unrelated Progressive Context skill edit and untracked performance contract were present before this review and preserved. A final hash comparison checks that the reviewed plugin source remained unchanged while the report was written.

**Review configuration:** independent sub-agent requested and dispatched as **gpt-6-astra with xhigh reasoning effort (Astra extra-high)**. The review received a bounded task description, inspected repository sources and produced its own probes; it did not delegate further. This is configuration provenance, not a measured claim about Astra's speed, cost, or superiority. The report and its small evidence directory are the only authored deliverables.
