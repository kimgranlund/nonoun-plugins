# Research corpus: one word, different populations

This is an authored illustration with synthetic reports and figures. The numbers
are example inputs, not empirical observations or demonstrated research outcomes.

## Request and source material

“Summarize retention evidence across two research teams and update the glossary
when the service team changes its reporting definition.”

| Source record | Native assertion |
| --- | --- |
| `report:service-a/r1` | “Retention”: proportion of 100 activated accounts returning within 30 days; reported value 60%. |
| `report:service-b/r1` | “Retention”: proportion of the same stated cohort returning within 30 days; reported value 58%. No reconciliation with service-a is supplied. |
| `report:archive/r1` | “Retention”: proportion of 200 stored objects retained after a 90-day lifecycle; reported value 95%. |
| `glossary:service/r2` | Future service reporting will use paid accounts returning within 30 days; the old activated-account definition is retained as deprecated. |

## A sufficient model

| Identity | Meaning and scope |
| --- | --- |
| `service:activated-account-return-30d` | Return proportion for activated accounts; source label “retention” scoped to the old service glossary |
| `archive:object-retention-90d` | Retained-object proportion after the archive lifecycle; source label “retention” scoped to the archive glossary |
| `service:paid-account-return-30d` | Return proportion for paid accounts; distinct concept introduced by service glossary r2 |
| `claim:service-a/r1` | A source assertion of 60%, about the old service concept and its specified cohort |
| `claim:service-b/r1` | A separate assertion of 58%, with its own source attribution |

Keep each claim's reported value, denominator description, period and source
revision. `asserts_about` relates a claim to its concept; `reported_in` relates it
to its report. `supersedes_for_future_reporting` relates the new service definition
to the old one without claiming equivalence or rewriting earlier assertions.

The authored glossary owns definitions; each report owns its assertion. An authored
reconciliation note can record disagreement. Search indexes and summary tables are
generated views whose rows retain those source identities and definitions.

## Decisions and neighboring failures

| Decision | Outcome and evidence |
| --- | --- |
| Retrieve all three reports for the ambiguous word “retention” | Useful discovery, provided results retain their separate scopes |
| Compare service-a and service-b as disagreeing reports | Supported by their stated matching definition and cohort; preserve both claims |
| Publish 59% as the reconciled service result | Unsupported: averaging is neither a reported fact nor a justified reconciliation method |
| Rank the archive's 95% against the service's 60% | Unsupported: populations, periods and properties differ despite the common label and percentage unit |
| Link the paid-account definition as the future service measure | Supported by glossary r2; it does not establish equivalence with the old definition |

For a historical summary, resolve each report using the definition it actually
used. For a current summary, expose the definition change and report old evidence
under its old concept. Recalculation for paid accounts is unknown without underlying
cohort data; neither a renamed glossary entry nor a schema migration supplies it.

Validation can require a report revision and concept reference. Establishing which
service figure is correct requires additional evidence; passing those structural
checks cannot settle the disagreement.

Use [identity](../references/identity.md), [evidence](../references/evidence.md),
[mappings](../references/mappings.md), and [evolution](../references/evolution.md) for the reusable method.
