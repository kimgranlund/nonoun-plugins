# Contract audit

Applies to: both.

Observed in a five-round study of one runtime harness that renders generative UI, not universal law. Format and the other files: [README](README.md). The audit mode itself: contract audit (`references/contract-audit.md`).

30. Audit the guidance and contract surfaces statically before a live round.
    - Observed in the five-round study: most failures were (b) conflicting or ambiguous guidance or (d) check, oracle or scenario defects, and each was visible in the files before any live spend: a skill and the selection metadata directed different card types for one ask, a repair message asked for a field the schema lacks, and an oracle accepted a base type.
    - Check: run `audit.py scan` with a mapping, review every candidate and the rubric-only families, and count how many of the next round's failures trace to a defect the audit listed.
    - Applies to: both.
31. Tie each trace finding to the contract surface it names before choosing a fix layer.
    - Observed in the five-round study: the fix for one cluster had to change the skill, the check and the oracle together, because each named the same type with a different directive.
    - Check: `audit.py link` on the cluster's finding lists every surface that names its types or ids; the fix ticket cites each one or says why it stays.
    - Applies to: both.
