# Dashboard UI

## Intent

Help a person answer a consequential question about a system, distinguish signal from uncertainty, and decide whether action is warranted. Begin with decisions and analytical questions, not a gallery of chart types. Monitoring, exploration and reporting have different attention and interaction needs.

| Surface family | User intent and content responsibilities | Candidate next action | Candidate success signal |
| --- | --- | --- | --- |
| Overview | Understand current condition relative to a meaningful baseline | Investigate or continue monitoring | Accurate assessment and detection of important exceptions |
| Monitoring | Recognize changes that merit attention | Acknowledge, investigate or intervene | Appropriate detection and response, with false alarms tracked |
| Exploration | Form and test an explanation through comparisons | Refine, inspect or reject a hypothesis | Correct insights with understandable query/filter context |
| Entity performance | Understand one subject relative to time, peers or targets | Inspect drivers or act on the entity | Correct interpretation and relevant intervention |
| Drill-down | Explain an aggregate with underlying detail | Trace evidence or return to context | Reconciled totals and preserved analytical scope |
| Report / snapshot | Communicate a finding with provenance and caveats | Share, review or decide | Correct recipient interpretation and reproducibility |
| Alerts | Distinguish urgent signals from noise | Investigate, resolve or tune criteria | Useful responses and manageable alert burden |
| Metric definition / data health | Understand calculation, freshness, coverage and uncertainty | Verify, repair or qualify interpretation | Appropriate confidence and fewer invalid conclusions |

## Content strategy

Give each measure its meaning, unit, period, comparison and data status where needed. Make filters, time zones, denominators and aggregation scope inspectable. Distinguish zero, missing, delayed, estimated and suppressed values. Explain whether an apparent change is comparable across periods. A chart title should help identify the question being answered, not merely name the visualization type.

## Decision space

Compare exception-first monitoring, question-led exploration, or narrative summaries with evidence drill-down. A role-focused overview can reduce noise but may obscure relationships across roles. A dense workspace can support expert comparison but increase initial interpretation cost. Choose chart forms after establishing comparison tasks, data shape and uncertainty; do not default to cards because they arrange easily.

## Measures and guardrails

Candidate measures include correct interpretation, useful exception detection, time to supported explanation and appropriate intervention. Pair speed with false positives, missed events, stale-data decisions and unwarranted confidence. Insight counts and dashboard visits are weak proxies unless their relationship to useful decisions is established.

## Review questions

Can a person explain what changed, compared with what, and how certain that conclusion is? Can they trace the evidence and return without losing filters? Are action permissions and consequences clear? Does the narrow layout preserve the comparison task, not just each chart individually?

Prototype scope: sample datasets can demonstrate questions and edge cases; they do not establish real data accuracy, alert performance or causal impact.

Related: [operations](../capabilities.md#operational-and-administrative-systems), [search](../capabilities.md#search-and-discovery), [conditions](../conditions.md).

Use [experience reasoning lenses](../experience-lenses.md) to connect surface choices with task continuity, state, recovery and coherent flow alternatives.
