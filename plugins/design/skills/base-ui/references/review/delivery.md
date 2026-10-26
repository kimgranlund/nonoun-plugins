# Draft → review → delivery

`build.mjs` produces a runnable **draft** plus `.review-status.json` marked pending-review. Building must precede browser inspection; it is not a release. The kit's delivery gate requires a completed review and consumer measurements to copy that draft into a release. Manual filesystem copies remain outside this boundary.

For UI, prefer the [executable review session](session.md): it initializes the bound record while capturing the app-state matrix, then links your explicit judgments to evidence and lists outstanding work. This avoids separate manual evidence/state bookkeeping. The session separates the full machine matrix from a generated risk-based visual sample; the gate validates both independently. All machine rows and failures remain checked, while manual conclusions explicitly cover only the sampled images. For manual or image reviews, initialize a bound record before inspection:

```sh
python3 scripts/run.py review-delivery.mjs begin /absolute/app.html /absolute/evidence/review.json
```

This creates every rubric item as unreviewed and records the artifact's exact SHA256. Fill task, reviewer, states and checks through the [review workflow](index.md). Keep the binding and scope.artifact unchanged. If the app changes, preserve this review and begin a new one against the changed artifact; rerun affected checks and inspect neighboring relationships. Do not simply replace the hash to carry stale evidence forward.

Evidence references resolve relative to the review JSON, or may be absolute local paths. Preserve screenshots for every declared state and reference them in the applicable items, with state IDs and observations. Source refs may use `:line` or `#anchor`. URLs and missing/empty files cannot substantiate the offline delivery record. File existence does not establish that a screenshot was inspected or that it depicts the artifact.

For UI reviews, include `kind: "measurement"` evidence pointing to the actual JSON returned by [consumer contrast and task-access checks](measurements.md). Arbitrary filenames and nested wrappers are supported. Both measurement kinds are required; all recognized nested measurements must pass for acceptance. A wrapper's `passed: true` cannot conceal a failed inner measurement. Other measurement JSON (for example geometry) remains preserved evidence; files without recognized consumer results are explicitly `unreviewed` by this measurement evaluator and do not substitute for either required kind. Their meaning remains the reviewer’s responsibility.

Check intermediate progress, then finish:

```sh
python3 scripts/run.py review-delivery.mjs check /absolute/evidence/review.json
python3 scripts/run.py review-delivery.mjs finish /absolute/evidence/review.json /absolute/evidence/completion.json /absolute/released.html
```

The optional final HTML path is created only for **accepted** records; it is an exact copy of reviewed bytes. Existing receipts/releases are never overwritten. The receipt hashes the review, artifact and preserved evidence. It records these separate outcomes:

- `incomplete`: missing/invalid binding or evidence, blocked/unreviewed items, or missing measurement coverage.
- `complete-with-findings`: every review item addressed, but a rubric failure or nonpassing measurement remains.
- `accepted`: every item addressed, no recorded failure, both consumer measurement kinds passing, unchanged artifact and resolvable evidence.

To preserve an unfinished or completed-with-findings outcome, omit the HTML path. This writes an honest receipt and exits nonzero. Report that outcome and remaining work; never describe it as acceptance. An accepted receipt means accepted **in the recorded scope**, not all possible states. The gate cannot authenticate visual judgment, prevent fabricated observations, or certify arbitrary host actions. Independent visual and trace review remain necessary.

Historical schema-v1 checklist records remain readable by `review-checklist.mjs check`. They cannot be released through this gate without a new artifact-bound review.

CLI `check` and `finish` return bounded summaries with counts and a durable `report` path. The report preserves every measurement, evidence record and error; open only the needed records. The programmatic verification API still returns the full result. Compact stdout does not weaken the gate.

For a page with local external stylesheets or scripts, the binding also records each asset hash, recursively including CSS imports, local font/image URLs and static ES module imports/re-exports (including inline module entries). Module syntax is parsed without execution. Bare module specifiers/import maps fail explicitly. Runtime-created URLs, dynamic imports and remote assets are outside this binding; do not claim their integrity from this receipt. The gate rejects asset changes and copies dependencies with the release. A shared filename does not imply shared review validity. Remote assets remain outside this guarantee.
