# Evaluating knowledge-modeling work

Use when designing skill benchmarks, fresh-agent trials or comparative evaluations.
For an ordinary model review or change, check the decision against its sources and
the actual consumer where applicable; this file is not a prerequisite. Do not turn
task verification into an evaluation of the skill itself.

## Evidence levels

1. Structural checks establish format, links, identities and declared constraints.
2. Executable consumer checks establish the tested decisions under selected inputs.
3. Fresh-context agent trials establish observed behavior on the supplied tasks and
   available guidance; explicit skill invocation is distinct from native discovery.
4. Independent domain-expert adjudication can establish a human reference for the
   bounded cases. Agent review does not substitute for this level.

Do not report a level that was not observed. A proposed evaluation is not a result,
and an implemented validator is not evidence that its constraints express the
correct domain policy.

## Discriminating cases

For the changed boundary choose a supported case, a misleading neighbor and, when
relevant, an unknown case. Examples of useful contrasts:

| Boundary | Positive case | Counterexample |
| --- | --- | --- |
| Identity | Scoped synonym resolves to a defined concept | Homonym in a different source is silently merged |
| Relationships | Typed dependency supports its documented query | Composition becomes subclass, equivalence or access permission |
| Mapping | Evidence and context justify the requested operation | Similar labels or values substitute for eligibility evidence |
| Evidence | A derivation preserves inputs and interpretation | Missing value becomes zero, or a claim becomes a measured fact |
| Evolution | Old and new consumers select their intended revisions | A changed definition silently reinterprets retained records |
| Context handoff | Required definitions and policy arrive before use | A summary replaces the contract or all related nodes become mandatory |

Use genuine task criteria, not exact wording or predicates chosen by the implementer.
Allow alternative representations that preserve the required distinctions. A system
that rejects everything must fail supported cases. A schema that accepts everything
must fail malformed/context-incompatible cases.

## Companion-skill trials

When comparing progressive-context alone with the combined skills:

- Preserve baseline skill bytes and raw source revisions. Freeze the task brief and
  independent expected decisions before running either condition. Keep them fixed
  when comparing results; record later repairs as a new revision.
- Use new sessions without prior conclusions or expected answers. Provide the same
  task, source corpus and output requirements; vary only the available guidance.
  Keep answer keys and worked solutions outside the allowed task search scope.
- Record which files/versions were actually read and how those reads were observed.
  Instrumented reads can establish exposed bytes; they cannot establish model
  retention or understanding. Label self-reported reads as such.
- Assess actual artifacts against the frozen oracle, ideally without the grader
  knowing the guidance condition. Preserve failures, retries and alternative paths.
  Do not coach a failed trial and count its continuation as an unchanged fresh run.
- Use multiple domains when claiming portability. A small number of synthetic cases
  can show bounded adequacy; it cannot establish general effectiveness or a reliable
  causal improvement. Report ties and regressions as readily as improvements.

Report separately: **semantic decisions**, **required retrieval/delivery**,
**historical preservation**, and **reading cost** (calls, bytes or measured tokens).
Do not invent token counts from file sizes. Compare efficiency only among runs that
meet correctness criteria, and include skill-reading overhead and recovery reads.

For progressive-context's deterministic tooling, follow its own evaluation contract.
Authored replay, instrumented fresh-context trials and actual host discovery are
different evidence sources. This skill does not ship a general semantic reasoner or
promise automatic selection by a host whose skill catalog has not been observed.
