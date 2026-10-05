#!/bin/bash
# Builds the throwaway fixture: a blocked ticket with a Deferred note, a failed verifier result, a notes file.
set -e
D=$(mktemp -d /tmp/ask-live.XXXXXX); cd $D; git init -q proj; cd proj
mkdir -p .sdlc/tickets/0002-csv-export .sdlc/tickets/0003-sync-job/step-1; printf '# Notes\n' > .sdlc/notes.md
cat > .sdlc/tickets/0002-csv-export/handoff.md <<'EOT'
---
id: T-0002
title: "CSV export for the report page"
type: feature
status: blocked
size: S
priority: P2
depends: []
created: 2026-10-05
---

## Goal
Add a CSV export to the report page.

## Deferred
Blocked 2026-10-04: nobody has written the column spec (which fields, which order, header names). The spec is a long document the product owner has to supply.
EOT
cat > .sdlc/tickets/0003-sync-job/handoff.md <<'EOT'
---
id: T-0003
title: "Nightly sync job retries"
type: bug
status: ready
size: S
priority: P2
depends: []
created: 2026-10-05
---

## Goal
The nightly sync job retries a failed upload up to the configured limit.
EOT
cat > .sdlc/tickets/0003-sync-job/step-1/verifier-L1.md <<'EOT'
<!-- role=verifier level=L1 model=sonnet effort=low -->
## Verdict
fail

## Criteria
- 1 retry limit honoured: fail. Evidence: python3 -m unittest tests.test_sync ran 3 tests, 1 failure (test_retry_limit expected 3 attempts, saw 5).

## For the next attempt
The retry counter is never reset between uploads. Decide whether the limit is per upload or per job before fixing: the handoff does not say.
EOT
git add -A; git -c user.name=t -c user.email=t@t commit -q -m fixture
echo $D/proj
