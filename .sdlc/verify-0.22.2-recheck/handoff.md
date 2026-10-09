## Task goal
Recheck the three criteria of .sdlc/verify-0.22.2-batch/verifier-L3.md that failed: T-0404 (its red control was misstated), and the Status line of the two design docs. Judge the current HEAD in a `git archive HEAD` copy. Read-only: run checks, change nothing in the repo.

## Step 1: Recheck the failed criteria
level: L2

### Acceptance criteria
- T-0404 placeholder fix bites: in a `git archive HEAD` copy, `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, and after replacing the line starting `PLACEHOLDER_RE = ` in plugins/sdlc-lite/scripts/steps.py with `PLACEHOLDER_RE = re.compile(r'<[^<>\s][^<>]*>')` (the v0.22.1 regex), the same selftest exits 1 and its output names `(n) an unquoted i<t ... >= is not skipped`. Report both exit codes.
- `grep -c '^Status' docs/specs/sdlc-lite/plan-verification.md` prints 1 or more in the copy, and `python3 -c "import sys;t=open('docs/specs/sdlc-lite/plan-verification.md').read();sys.exit(1 if ('—' in t or '–' in t) else 0)"` exits 0 in the copy.
- `grep -c '^Status' docs/specs/sdlc-lite/verifier-held-criteria.md` prints 1 or more in the copy, and the same dash check on that file exits 0.
