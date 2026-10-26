# Diagnosis Reference

Detail for SKILL.md sections 6, 7 and 13: the diagnosis sequence, the two root-cause steps that come first, the taxonomy, cause classes for model-driven systems, and clustering.

## Diagnosis sequence

Use this sequence:

```text
FAIL
  → classify
  → localize
  → generate hypotheses
  → rank by evidence and cost to test
  → run discriminating test
  → confirm/refute
  → repair confirmed cause
```

Avoid symptom patching unless the episode explicitly permits a temporary containment fix.

## Rule out lost context first

Before any hypothesis about the system's behavior, prove that its inputs arrived. Check, per failing case:

- every item a retrieval or routing step selected was actually submitted to the system under test (retrieved equals submitted);
- every tool or step result reached the next request that depends on it;
- no input was truncated, and no output stopped at a token, size or time cap (read a recorded stop reason when one exists; otherwise compare output size with the request's cap);
- the guidance meant to apply was loaded in full, not only listed by name in an index.

A failure on any of these is a transport or context defect: rewriting guidance or swapping models cannot fix it, and a fix aimed there will appear to fail. Record "lost context ruled out" with the counts checked (pairs, envelopes, lines) before classifying further. When the instrumentation cannot answer one of these questions, say so; an unassessed check is not a clean one.

## Uniform errors point at your own pipeline

When failures are uniform (every run, every model, every case, or every attempt fails with the same code, stop reason, or shape), the likeliest shared cause is something all of them pass through: your harness, runner, checks, scenario script, credentials, quota, network, or a parser on your side. Treat the system under test as innocent until a discriminating test says otherwise:

1. Find one case that should pass under every hypothesis (a known-good input, a replay of a past pass, a smaller or stronger model) and run it through the same pipeline.
2. If it fails the same way, the cause is in the pipeline; open the episode there.
3. If it passes, compare its path with a failing one step by step until they diverge.

This is a root-cause step inside diagnosis, not a repair. Do not patch the symptom (retry until it passes, loosen the check) before the shared cause is named.

## Universal root-cause taxonomy

Use this taxonomy as a starting point; extend it when the domain requires more precision:

- **Intent:** objective or requirement was missing, contradictory, or misread.
- **Context:** relevant information was absent, stale, excessive, or incorrectly scoped.
- **Knowledge:** the agent/system lacked correct domain knowledge or discoverability.
- **Planning:** decomposition, ordering, dependency, or strategy was wrong.
- **Contract:** schema, interface, invariant, policy, or expectation was violated or underspecified.
- **Selection:** wrong tool, component, model, resource, pattern, or strategy was chosen.
- **Generation / Transformation:** produced representation was incorrect.
- **Implementation:** local logic or construction was wrong.
- **Integration:** individually valid parts interacted incorrectly.
- **Runtime / Environment:** execution conditions differed from assumptions.
- **Interaction / Workflow:** sequence or state transition failed under use.
- **Evaluation:** verifier, test, oracle, benchmark, or acceptance logic was wrong or incomplete.
- **Observability:** evidence was insufficient or misleading.
- **Process:** ownership, checkpointing, permissions, or operational flow caused failure.

Distinguish **discovery failure** from **knowledge failure**, **selection failure**, **contract failure**, and **implementation failure** whenever possible. They require different interventions.

### Evaluation failure modes

- **Check narrower than its rule.** The rule says "a priced list of services is shown as cards"; the check only fires when the priced list arrives as a table, so the same list as a key-value block passes. Symptom: an unexpected pass that a stronger model answers differently. Fix the trigger to the rule's whole condition, and keep a negative case that must stay clean.
- **Oracle too generic.** The scenario's expected outcome admits several correct answers ("book a massage" when two massages match, "summarize the report" when two reports are open), or a scripted next step assumes a path the system may legally not take (a scripted click after a move that can end the scenario). Symptom: a correct, defensible result scored as a failure, often with the system asking a clarifying question. Fix the scenario so exactly one answer is right, and have a second reviewer agree it is the only one.

Both are class (d) below. Check them on every unexpected pass and every unexpected fail before blaming the system under test.

## Cause classes for model-driven systems

When an AI model or agent is the system under test, give every failure cluster one primary class, and name the evidence that excludes the others:

- **(a) Exposure:** the guidance never reached the model (an index-only entry, nothing relevant retrieved). Lost context is not a class: it is ruled out before classification.
- **(b) Conflicting or ambiguous guidance:** two rules the model saw disagree, or one reads two ways; the model's own reasoning often names the conflict.
- **(c) Model ignored clear guidance:** only when the guidance was framed in full and a stronger model passed on identical framing. When the system under test is already the strongest model available, N samples on the same framing, or a second model family, stand in.
- **(d) Check, oracle or scenario defect:** the evaluation was wrong, including the two failure modes above.

Read the mix before repairing. In a nine-cycle study of one generative UI runtime, most failures in most cycles were (b) or (d), so the fix belonged in guidance or checks; a cycle whose failures read as all (c) usually has an unexamined (a), (b) or (d). Fix (a) and (b) in what the model reads, (d) in the check or the scenario, and record (c) as a model note, never as a reason to rewrite shared guidance. Small models read guidance literally; a fix for one agent belongs in that agent's own text before shared text.

The cause classes, their checks and the field evidence: context-fog-of-war triage lessons (`context:context-fog-of-war` `references/learnings/triage.md`) and guidance authoring lessons (`context:context-fog-of-war` `references/learnings/guidance-authoring.md`).

## Failure clustering

Before creating episodes:

1. deduplicate identical failure signatures;
2. group failures sharing a probable causal boundary;
3. separate independent symptoms that only appear related;
4. prefer the smallest cluster that can be causally reasoned about;
5. order clusters by dependency and expected downstream impact.

When one upstream cause plausibly explains many downstream failures, test that hypothesis before opening many separate repair windows.

Assign a failed case to every cluster it fails in and report two counts per cluster: cases that fail in it at all ("any") and cases that fail only in it ("only"). Single assignment hides overlap, and a fix for one cluster will not turn a multi-cluster case green.
