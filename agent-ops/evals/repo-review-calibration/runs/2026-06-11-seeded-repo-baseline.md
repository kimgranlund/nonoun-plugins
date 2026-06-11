# repo-review calibration — seeded-smell-repo — 2026-06-11 (baseline)

- **What this is:** the first behavioral coverage for agent-ops's `repo-review` skill — the surface the 2026-06-11 real-repo audit flagged as ungated (its own P0-1). The fixture (`build-seeded-repo.py`) is a 4-file synthetic repo with **6 planted architectural smells**; a healthy `repo-review` pass must surface all six in its cascade-ranked backlog. Built on demand (never committed — the catalog ships no intentional-vulnerability files).
- **Instrument:** the real `repo-review` skill, run **cold** (no hint of the planted smells) via a general-purpose agent that loaded the skill + references from disk and ran the full pipeline (Discover → Rubric → Audit → Synthesize → Adversarial → Polish). Model: Claude Fable 5.
- **`check.py` result: 6/6 planted smells caught.** Headline rubric: **~1.5/5 (Broken–Weak)**; 2 P0 / 2 P1 / 4 P2. Trust boundary held (no injection in the fixture; README's false claims treated as data, cited as DX findings).

## Did the review catch the planted smells?

| Planted smell | Caught as |
| --- | --- |
| **S1** god module (parsing+db+http+rendering in one file) | "HTTP/DB/validation all in one file… **Abstraction Layering / DRY** 2/5"; direction: "pull DB access and the HTTP handler apart" |
| **S2** naming drift (camelCase + snake_case) | NAME-1: "**casing convention drifts inside one module**… `getUserData`/`fetchRemote` beside `render_user_page`" (`app.py:5` vs `:9`) |
| **S3** declared-vs-actual (README "stdlib only" vs `import requests`) | DX-1: "**README contradicts the code on every claim**… 'Zero dependencies — stdlib only'… refuted by `app.py:3` (`import requests`)" — P1, "the closest P0/P1 call" |
| **S4** duplicated `_is_valid_email` | DRY-1: "**`_is_valid_email` duplicated verbatim**… `app.py:12` ≡ `validate.py:1`… no single source of truth" |
| **S5** command injection (`os.system` + unsanitized input) | **P0-2 SEC-2: "command injection in the deploy path"** (`deploy.py:6` ← `sys.argv[1]`); before/after → `subprocess.run([...], check=True)` + branch validation |
| **S6** no agent memory / no tests ("well-tested" is false) | TEST-1: "**Zero tests behind a 'well-tested' claim**… no test file anywhere"; the README's "well-tested" cited as a false claim |

## Notable (real review, not answer-key matching)

- **Emergent findings beyond the planted set:** SEC-1 (SQL injection on every HTTP request — promoted to **P0-1**, which the seed didn't explicitly plant but is real in `app.py:6`), SEC-3 (SSRF-able outbound fetch, no timeout), DX-2 (no error handling, raw rows → wire = stored-XSS vector). The auditor found *more* than was planted — evidence it's doing real review.
- **The adversarial wave did real work:** it held P0-2 (command injection) against a "deploy.py may be dead code → demote to P1" challenge — resolved with "absence of a caller is not evidence of safety; if dead, *delete* the RCE sink (still P0), don't tolerate it at P1." And it defended the closest call (DX-1 P1 vs P0) on "the injection is exploitable without a human; the bad README is not."
- **Honest Tier-1 accounting:** the review reported **no Tier-1 patterns above the preservation bar** and argued *why* manufacturing praise here would be a calibration failure — resisting the negative-only-vs-padded trap the skill warns about. A review that correctly declines to find positives is as valid as one that finds them.

## Scorecard

`python3 check.py runs/2026-06-11-seeded-repo-baseline.md` → **6/6**. The `repo-review` surface now has behavioral coverage; CI re-scores this baseline (closing the audit's P0-1 doctrine gap).
