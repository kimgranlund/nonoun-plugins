<!-- role=builder level=L2 model=opus effort=low -->
## Status
blocked

## Changes
- `docs/validation/runner-family-task-dir-live-run/fam/` (new): the rsync copy of the throwaway task dir, with handoffs, the builder and verifier results, `runs.jsonl` and attempt records.
- `docs/validation/runner-family-task-dir-live-run/dry-run-base.txt` (new, written by redirection). It is not a real negative control (see Notes).
- `docs/validation/runner-family-task-dir-live-run/dry-run-fixed.txt` (new, written by redirection).
- Not written: the report `docs/validation/runner-family-task-dir-live-run.md` and the `docs/README.md` line.

## Checks
- `claude --version`: 2.1.286. `git rev-parse --short HEAD`: aa59ebc. `git hash-object plugins/sdlc-lite/scripts/run.sh`: e5308edf87a23bd02eb179eab631250a1bf24819. `git status --porcelain -- plugins/`: empty, because steps 1 and 2 are already committed in d87cc4b and aa59ebc.
- Live builder (`W bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/fam/step-1/handoff.md`): exit 0. Header `<!-- role=builder level=L1 model=sonnet effort=low -->`. Log model `claude-sonnet-5-5`.
- Base dry run from `git archive "$SDLC_BASE_SHA"` with `SDLC_BASE_SHA=aa59ebc`: exit 0, but it printed `--model opus --effort medium` where `sonnet` was expected.
- Fixed dry run: exit 0, `--model opus --effort medium`.
- Live verifier (`W bash <repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/fam/handoff.md`): exit 0. Header `<!-- role=verifier level=L1 model=opus effort=medium -->`. The `runs.jsonl` line has role verifier, model opus, effort medium, backend claude. Log model `claude-opus-5-5`.
- I did not run the acceptance criteria as a set. The dry-run-base criterion fails as built, and the report and README criteria have nothing to check yet.

## Notes
plan defect: item 5 and the dry-run criterion `grep -qF -- '--agent sdlc-lite:verifier --model sonnet ...' dry-run-base.txt` cannot hold, because `$SDLC_BASE_SHA` (aa59ebc) is the step-2 checkpoint commit and already contains the step 1 and 2 fix. The base run.sh therefore picks Opus too, so the negative control does not discriminate. The real pre-fix commit is 171e13b (`T-0195 plan split`, parent of the step-1 commit d87cc4b).

To fix it, the replan should name `git archive 171e13b` and rerun only the two dry runs into the same files, with no model call. The throwaway project can be rebuilt from `fam/handoff.md` and `fam/step-1/`, which were copied. After that, write the report (Result: pass) and add the README line.

- The live proof passed: the builder ran on Sonnet and the verifier on Opus. Do not rerun the live roles; the evidence is already in `fam/`.
- The Environment section must say that steps 1 and 2 are committed, not uncommitted as the handoff assumed.
- Cleaning up the temp dir `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.PDQbvWuqBm` (the project plus the base extract) was denied by permissions, so it still exists. It is outside the repo.
