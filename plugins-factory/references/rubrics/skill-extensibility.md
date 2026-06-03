---
date: 2026-05-24
status: draft
version: "0.1.0"
---

# Skill Extensibility — Best Practices Rubric

**A skill is a living operating document, not a frozen prompt.** If a skill cannot absorb
new evidence, repeated failures, better tools, new edge cases, and changed project constraints,
it will drift out of alignment with the work it is supposed to govern. If it absorbs everything
without discipline, it becomes a bloated junk drawer that weakens the agent that reads it.

Skill extensibility is the discipline of allowing skills to learn without losing shape.

A good skill evolves in response to observed use. It promotes repeated procedures into mechanisms,
moves cold-start noise into references, turns recurring mistakes into hard rules, adds evals for
new failure modes, and retires instructions that no longer earn their context cost. The skill
gets more capable over time without becoming larger in every invocation.

**Companion docs** (most live in the parent `skills-studio` library; only `skills-authoring.md` and `security-and-scope-containment.md` are bundled here):
- `skills-authoring.md` — the anatomy of a well-formed skill
- `harness-design.md` — what belongs in the harness vs. the skill
- `progressive-context-construction.md` — how context grows only when task state requires it
- `inversion-and-abstraction.md` — when skill prose should become a tool
- `mechanization-best-practices.md` — how repeated deterministic behavior becomes scripts, hooks, validators, gates, and workflows
- `evaluation-workflows.md` — how changes to skills are tested rather than assumed correct
- `observability-and-telemetry.md` — how evidence from use feeds improvement
- `security-and-scope-containment.md` — how extension is bounded by blast radius and authorization

---

## §The Problem

Most skill libraries fail in one of two ways.

**Static decay**: the skill is written once and treated as complete. The environment changes,
tools change, recurring agent failures appear, user expectations shift, but the skill does not
adapt. Agents continue to follow stale instructions because the skill remains authoritative even
after reality has moved on.

**Unbounded accumulation**: every new observation becomes another paragraph in `SKILL.md`.
Every edge case becomes a new warning. Every failure becomes a new rule. Every tool becomes a
new mode. The skill technically learns, but it learns by getting heavier. Eventually the agent
loads too much context, sees too many rules at equal weight, and performs worse despite having
more information.

Skill extensibility solves the tension: skills must be able to change, but every change must
have a destination, a promotion path, and a retirement path.

The extensible skill system answers six questions:

1. **What evidence justifies changing the skill?**
2. **Where should the change land?** (`SKILL.md`, `references/`, `scripts/`, evals, harness, or nowhere)
3. **How does the change affect cold-start context?**
4. **What regression risk does the change introduce?**
5. **How will the change be verified?**
6. **When should the change be pruned, promoted, or mechanized?**

Without those answers, skill evolution becomes indistinguishable from context accumulation.

---

## §First Principles

### 1. Skills learn from observed use, not author intuition

A skill should not grow because an author can imagine a future case. It should grow because the
system has observed a repeated need, a real failure, a recurring ambiguity, or a measurable quality
gap.

The primary inputs to skill evolution are:

- repeated agent mistakes
- repeated user corrections
- repeated manual procedures
- eval failures
- routing ambiguity
- verification gaps
- tool failures
- security or scope violations
- telemetry showing repeated patterns
- changed project constraints

Speculative additions are allowed only when clearly marked as experimental and kept out of
cold-start context until proven useful.

### 2. Extension requires placement discipline

Not every improvement belongs in `SKILL.md`.

The extension target should match the function of the new knowledge:

| New evidence | Proper destination |
|---|---|
| A recurring activation ambiguity | skill description / trigger phrasing / routing eval |
| A recurring hard failure | hard rule or failure-recovery reference |
| A repeated deterministic procedure | script, hook, validator, or workflow |
| A long explanation | reference file |
| A new work type | mode entry |
| A new edge case | eval case first, then reference or rule |
| A cross-cutting invariant | harness rule |
| A task-specific lesson | local memory or project note |
| A stale warning | delete or demote |

The extensible skill does not ask "where can I paste this?" It asks "what is the narrowest durable
home for this evidence?"

### 3. Cold-start context is protected real estate

A skill can become more capable without making every invocation heavier. `SKILL.md` should remain
the routing layer: posture, activation conditions, modes, load conditions, tool citations, and
verification targets. Most new knowledge should land in deferred references, evals, or mechanisms.

Cold-start additions require a higher bar:

- the agent needs it in the first few actions
- bypassing it causes real harm
- it affects mode selection or safety
- it is cross-cutting across most invocations
- it cannot be deferred without degrading behavior

If a new addition does not meet that bar, it should not increase cold-start load.

### 4. Extension should reduce future work, not merely record past work

A skill update earns its keep when it changes future agent behavior.

Bad extension:

> "Remember to be careful with release tags."

Good extension:

> "Before publishing, run `scripts/check-release-tag.mjs --strict --json`; do not continue if it exits non-zero."

The first records a lesson. The second changes behavior. The best extensions either improve
routing, reduce ambiguity, mechanize repeated work, strengthen verification, or prevent a known
failure from recurring.

### 5. Every extension has a regression surface

Changing a skill is changing an operating system for agents. Even a small description edit can
alter routing. A new hard rule can conflict with existing rules. A new mode can steal tasks from
an older mode. A new reference can increase context load. A new script citation can fail in
environments where the script is unavailable.

Skill extension therefore requires regression thinking:

- What behavior should change?
- What behavior must not change?
- Which evals should run?
- Which adjacent skills might be affected?
- What is the rollback path?

No skill extension should be considered complete until its intended behavioral delta is explicit.

### 6. Skills have lifecycle states

A mature skill library distinguishes between:

```txt
experimental → active → senior/load-bearing → deprecated → archived
```

Each state has different extension rules.

Experimental skills can change quickly. Active skills need targeted evals. Senior skills need
regression gates before behavior changes. Deprecated skills should receive only critical fixes.
Archived skills should not receive new behavior.

Without lifecycle states, every skill is treated as equally safe to mutate, which is false.

### 7. Learning loops must close

Skill extensibility is not "add more docs." It is a closed loop:

```txt
observe → classify → place → verify → monitor → prune/promote/mechanize
```

A failure observed but not classified remains anecdote. A classified failure not placed remains
tribal knowledge. A placed update not verified is a hypothesis. A verified update not monitored
may drift. A monitored pattern not pruned or promoted becomes bloat.

---

## §The Rubric

### Dimension 1 — Evidence-driven extension

Does the skill change in response to observed evidence, or in response to speculation?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Every meaningful skill change cites an evidence source: eval failure, repeated invocation pattern, incident, telemetry, user correction, or changed project constraint. Speculative additions are labeled experimental and excluded from cold-start context. |
| **4 — Good** | Most changes are evidence-backed. Some author-judgment additions exist but are low-risk and reviewed later. |
| **3 — Adequate** | Changes are usually sensible but not traceable to evidence. The skill improves, but the reason for each change is often implicit. |
| **2 — Poor** | Skill grows whenever someone imagines a useful rule, example, or mode. No difference between observed need and speculative design. |
| **1 — Failing** | Skill changes are arbitrary. New content accumulates without cause, owner, or measurable effect. |

**Test**: pick the last 10 additions to the skill. For each, identify the evidence that justified it. If more than 3 cannot be tied to observed evidence, extension is speculative.

---

### Dimension 2 — Placement quality

Does new knowledge land in the right layer?

| Score | Evidence |
|---|---|
| **5 — Excellent** | New information is routed to the narrowest correct destination: cold-start only for routing/safety, references for detailed knowledge, scripts/hooks/validators for deterministic procedures, evals for failure cases, harness for cross-cutting invariants. |
| **4 — Good** | Most additions land correctly. Some content lives in `SKILL.md` that could be deferred, but not enough to degrade performance. |
| **3 — Adequate** | Placement is inconsistent. Useful additions exist, but `SKILL.md` mixes routing, procedures, examples, and long explanations. |
| **2 — Poor** | Most additions are appended to `SKILL.md` by default. References and mechanisms are underused. |
| **1 — Failing** | No placement discipline. The skill is a chronological log of lessons, examples, rules, and procedures. |

**Test**: take a recent 20-line addition to `SKILL.md`. Could any part move to a reference, eval, or mechanism without harming first-action behavior? If yes, cold-start is absorbing content that should be deferred.

---

### Dimension 3 — Cold-start stability

Does the skill become more capable without increasing the context loaded on every invocation?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Cold-start surface remains stable over time. New capabilities are exposed through concise mode entries, load conditions, and tool citations. Context growth happens in references and mechanisms, not in the always-loaded surface. |
| **4 — Good** | Cold-start grows slowly and intentionally. Additions are periodically audited and pruned. |
| **3 — Adequate** | Cold-start grows with each release but remains usable. No formal budget, but no immediate bloat crisis. |
| **2 — Poor** | Every extension increases cold-start length. Agents must read more to do the same first action. |
| **1 — Failing** | Cold-start is the full skill archive. The skill gets slower and noisier every time it "learns." |

**Test**: compare current `SKILL.md` token count to 90 days ago. Did capability increase without proportional cold-start growth? If not, extensibility is being paid for with attention debt.

---

### Dimension 4 — Behavioral delta clarity

Does each extension define what behavior should change?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Each extension states the intended behavioral delta: which tasks route differently, which procedure is replaced, which failure is prevented, which verification is added, or which action is now forbidden. |
| **4 — Good** | Major extensions define behavioral deltas. Minor edits do not always document the expected behavior change. |
| **3 — Adequate** | The intended behavior change can be inferred from the edit, but is rarely stated. |
| **2 — Poor** | Edits add content without specifying what future agent behavior should change. |
| **1 — Failing** | Skill changes are content changes only. No one knows whether the agent is supposed to behave differently. |

**Test**: for a recent skill edit, ask: "What should a future agent do differently because this exists?" If the answer is vague, the extension is under-specified.

---

### Dimension 5 — Regression safety

Are skill changes evaluated against old and adjacent behavior?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Skill changes run relevant routing and behavioral evals. Adjacent skills are checked for activation conflicts. Senior skills have regression floors. Rollback path is clear. |
| **4 — Good** | Major changes run evals. Small edits are reviewed manually. Adjacent-skill conflict checks happen when routing language changes. |
| **3 — Adequate** | Some eval coverage exists, but skill changes can still alter behavior without detection. |
| **2 — Poor** | Skill edits are made directly with no regression check. Failures are discovered later in use. |
| **1 — Failing** | No evals, no baselines, no rollback. Skill evolution is untested mutation. |

**Test**: edit one trigger phrase or mode description. Can you identify which evals must run and what score would block the change? If not, regression safety is weak.

---

### Dimension 6 — Mechanization and promotion discipline

Does repeated skill behavior get promoted into mechanisms or higher-level rules when appropriate?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Repeated deterministic procedures are promoted into scripts/hooks/validators/workflows. Repeated cross-cutting failures are promoted to harness rules. Repeated routing failures become eval cases. Promotion thresholds are explicit. |
| **4 — Good** | Common repeated procedures are mechanized. Promotion happens, but thresholds are partly informal. |
| **3 — Adequate** | Some scripts and rules exist, but repeated procedures often remain as prose. |
| **2 — Poor** | Skill prose grows around repeated procedures instead of mechanizing them. |
| **1 — Failing** | No promotion discipline. The agent manually repeats known procedures indefinitely. |

**Test**: find the most repeated 5-step procedure in the skill. Has it been mechanized or explicitly kept as prose because it requires judgment? If neither, the skill is accumulating manual work.

---

### Dimension 7 — Pruning and retirement

Does the skill delete, demote, or archive stale knowledge?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Pruning is part of the lifecycle. Stale rules, dead examples, unused references, unused scripts, and obsolete modes are removed or archived. Deletions are treated as improvements, not loss. |
| **4 — Good** | Periodic cleanup happens. Some stale material remains but does not mislead agents. |
| **3 — Adequate** | Pruning occurs only when bloat becomes obvious. The skill remains mostly usable. |
| **2 — Poor** | New content is added, old content is rarely removed. Contradictions and stale examples accumulate. |
| **1 — Failing** | Nothing is ever deleted. The skill becomes a historical sediment layer rather than an operating document. |

**Test**: identify content that has not affected an invocation in 90 days. Is it deleted, archived, or justified? If not, the skill lacks retirement discipline.

---

### Dimension 8 — Extension governance

Is there an explicit process for proposing, reviewing, landing, and monitoring skill changes?

| Score | Evidence |
|---|---|
| **5 — Excellent** | Skill changes have a lightweight governance flow: proposal, evidence, placement decision, expected behavioral delta, eval/verification, release note, monitoring period. Senior skills require stronger review. |
| **4 — Good** | Review and release notes exist for major skill changes. Minor changes may bypass formal review. |
| **3 — Adequate** | Changes are reviewed by humans but without a consistent template. |
| **2 — Poor** | Anyone can edit skills directly. There is no distinction between typo fixes and behavior changes. |
| **1 — Failing** | No governance. Skill behavior changes silently and unpredictably. |

**Test**: can you reconstruct why a skill changed, who changed it, what behavior it was intended to alter, and whether it worked? If not, extension governance is insufficient.

---

## §Extension Targets

An extensible skill library needs clear destinations for learning. Without destinations, every
lesson lands in the same place.

### 1. `SKILL.md`

Use for content the agent needs at activation or mode selection time:

- purpose
- activation conditions
- when not to use the skill
- mode menu
- load conditions
- hard safety rules specific to the skill
- tool citations
- verification targets
- stop conditions

Do not use for long examples, long procedures, incident history, repeated deterministic steps, or
full domain background.

### 2. `references/`

Use for deferred knowledge:

- detailed explanations
- domain-specific examples
- mode-specific procedures
- long decision guides
- troubleshooting references
- migration notes
- edge-case catalogs

Every reference needs a load condition. A reference without a load condition is an invitation to
preemptive loading.

### 3. `scripts/`, hooks, validators, workflows

Use for deterministic behavior:

- repeated file changes
- scanning and counting
- schema validation
- release checks
- generated output
- dry-run previews
- test orchestration
- scope checks
- formatting and normalization

If the agent does not need judgment to perform the step correctly, consider a mechanism.

### 4. Evals

Use for behavior that must not regress:

- routing cases
- ambiguous activations
- negative cases
- mode selection
- expected context loads
- expected verification targets
- adversarial examples
- prior incidents

Every serious skill failure should create at least one eval case before it creates prose.

### 5. Harness

Use for cross-cutting invariants:

- rules that apply across many skills
- security and scope policies
- verification posture
- tool access posture
- hard operational constraints
- top-level skill surfacing

A skill-specific failure should not become a harness rule unless it generalizes.

### 6. Changelog / release notes

Use for behavioral history:

- what changed
- why it changed
- what evidence motivated it
- what evals ran
- rollback notes
- monitoring notes

The changelog prevents `SKILL.md` from becoming a historical archive.

---

## §Skill Learning Loop

A mature skill learns through a closed loop.

### Step 1 — Observe

Capture evidence from actual use:

- invocation transcript
- tool output
- eval failure
- user correction
- repeated manual step
- security finding
- scope violation
- context bloat trace
- failed verification

Observation should be concrete. "The agent got confused" is not enough. Capture what it saw,
what it did, what it should have done, and what would have prevented the failure.

### Step 2 — Classify

Classify the evidence:

```txt
routing failure
mode-selection failure
context-loading failure
tool-use failure
verification failure
scope failure
security failure
mechanization candidate
output-contract failure
stale-content failure
```

Classification determines destination.

### Step 3 — Place

Choose the narrowest effective destination:

```txt
trigger text → routing problem
reference → detailed knowledge
script/hook/validator → deterministic repeated step
eval → regression case
hard rule → repeated high-impact failure
harness → cross-cutting invariant
delete/demote → stale content
```

### Step 4 — Verify

Run the relevant checks:

- routing eval
- behavioral eval
- mechanism contract test
- context-load test
- security/scope test
- output-contract review
- manual fresh-context review

The verification should test the intended behavioral delta, not just the syntax of the document.

### Step 5 — Monitor

Watch the next few invocations. Did the update actually change behavior? Did it introduce a new
failure? Did it increase context load? Did agents use the new reference or mechanism?

### Step 6 — Prune, promote, or mechanize

After enough use:

- prune if unused
- promote if repeated and high-value
- mechanize if deterministic
- move to harness if cross-cutting
- split if the skill has multiple unrelated responsibilities
- merge if two skills compete for the same task

---

## §Anti-patterns

### AP-01 — Append-only learning

**Symptom**: every lesson becomes another paragraph at the bottom of `SKILL.md`.

**Root cause**: no placement model. Adding text feels safer than deciding where knowledge belongs.

**Correction**: every addition must declare its destination type: routing, rule, reference, mechanism,
eval, harness, or changelog. Append-only is not a valid destination.

---

### AP-02 — Edge-case inflation

**Symptom**: one unusual failure adds a new permanent hard rule.

**Root cause**: treating every observed failure as generalizable.

**Correction**: one-off failures usually become eval cases or reference notes first. Promote to hard
rule only after repetition or high blast radius.

---

### AP-03 — Speculative extension

**Symptom**: the skill gains modes, references, or scripts for tasks that have not occurred.

**Root cause**: authoring from imagined taxonomy rather than observed use.

**Correction**: mark speculative content as experimental and keep it out of cold-start. Promote only
after observed invocation or eval evidence.

---

### AP-04 — Cold-start creep

**Symptom**: each update makes `SKILL.md` longer. Agents read more before doing the same work.

**Root cause**: confusing capability with always-loaded context.

**Correction**: protect cold-start. Add load conditions and deferred references. Promote repeated
deterministic steps into mechanisms instead of prose.

---

### AP-05 — Learning without evals

**Symptom**: a skill is edited to fix a failure, but no regression case is added.

**Root cause**: treating the document edit as the fix.

**Correction**: every serious failure creates an eval case first or alongside the doc change. If the
failure can recur, it must be testable.

---

### AP-06 — Conflicting lessons

**Symptom**: the skill contains two rules from different incidents that contradict each other.

**Root cause**: incident-driven additions without reconciliation.

**Correction**: classify lessons by scope and precedence. If two rules conflict, define when each
applies or delete one.

---

### AP-07 — Mechanization avoidance

**Symptom**: a repeated procedure grows more detailed in prose instead of becoming a script or gate.

**Root cause**: writing instructions is easier than building a mechanism.

**Correction**: apply the mechanization threshold. If the procedure is repeated, testable, and
failure-prone, promote it out of prose.

---

### AP-08 — Silent behavior changes

**Symptom**: a skill description edit changes which tasks activate the skill, but no one notices
until adjacent behavior breaks.

**Root cause**: no routing eval or release note for skill behavior changes.

**Correction**: treat activation language as executable behavior. Run routing evals on trigger,
description, and mode-name changes.

---

### AP-09 — Skill as historical archive

**Symptom**: the skill explains every past decision, every incident, and every migration.

**Root cause**: fear of losing context.

**Correction**: move history to changelog or references. `SKILL.md` is the operating surface, not
the archive.

---

### AP-10 — Unowned extensions

**Symptom**: nobody knows who added a rule, why it exists, or whether it still applies.

**Root cause**: skill changes lack ownership and review.

**Correction**: every non-trivial extension needs a short change record: evidence, destination,
expected behavior, verification, owner.

---

## §Hard Tests

1. **The evidence test**: Pick the last 10 skill changes. For each, identify the evidence that
   justified it. If evidence is missing, classify the change as speculative.

2. **The destination test**: For each new paragraph in `SKILL.md`, ask whether it should instead
   be a reference, mechanism, eval, harness rule, or changelog entry.

3. **The cold-start delta test**: Compare cold-start token count before and after the last 5
   skill releases. Capability should increase faster than cold-start size.

4. **The behavior-delta test**: For each extension, state what a future agent should do differently.
   If there is no behavioral delta, the addition may be documentation noise.

5. **The regression test**: Change a trigger phrase or mode name. Run routing evals. If there is
   no routing eval, activation behavior is unprotected.

6. **The incident-to-eval test**: Pick the last 3 serious skill failures. Does each have a
   corresponding eval case? If not, the skill is learning by memory, not by regression protection.

7. **The mechanization-candidate test**: Identify repeated procedures still described in prose.
   Which meet the mechanization threshold?

8. **The stale-content test**: Find content not used in 90 days. Delete, archive, or justify it.

9. **The conflict test**: Search for rules that use "always" and "never." Do any conflict with
   later exceptions? If yes, rewrite with explicit scope.

10. **The fresh-agent test**: Give the skill to a fresh agent. Does the agent understand activation,
    mode selection, load conditions, and verification without reading the changelog or incident
    history?

11. **The rollback test**: Revert the last extension. What behavior regresses? If the answer is
    unclear, the extension's value was never specified.

12. **The bloat-accounting test**: For every 100 lines added to a skill, how many lines were deleted,
    moved to references, or mechanized? If the answer is zero, the system is append-only.

---

## §Extension Change Template

Use this for non-trivial skill changes.

```md
## Skill Extension Proposal

### Evidence
What observed failure, repeated pattern, eval result, or changed constraint motivates this?

### Classification
Routing / mode selection / context loading / tool use / verification / scope / security /
mechanization / output contract / stale content / other.

### Destination
SKILL.md / reference / script / hook / validator / workflow / eval / harness / changelog / delete.

### Intended behavioral delta
What should a future agent do differently?

### Cold-start impact
Does this change increase always-loaded context? If yes, why is that necessary?

### Regression surface
What existing behavior might be affected?

### Verification
Which evals, hard tests, or manual checks prove this works?

### Rollback
How do we undo this if it causes regression?

### Monitoring
What should we watch in the next 3-5 invocations?
```

---

## §Routing Guidance

Add this to `README.md` or the rubric manifest:

```txt
If you are deciding how a skill should absorb a new lesson, repeated failure, new tool,
new edge case, or changed project constraint → read skill-extensibility.md.
```

Use this document when the question is not "how do I author a skill from scratch?" but
"how should this existing skill change without becoming unstable or bloated?"

---

## §Summary

Skill extensibility is not the ability to append more knowledge. It is the ability to adapt
without degrading the operating surface.

```txt
Observed evidence becomes classified learning.
Classified learning gets the narrowest correct destination.
Repeated deterministic learning becomes mechanism.
Recurring behavioral risk becomes eval.
Cross-cutting invariant becomes harness.
Stale or unused learning gets pruned.
```

The skill improves when future agents behave better with less ambiguity, less repeated work,
and no unnecessary increase in cold-start context.
