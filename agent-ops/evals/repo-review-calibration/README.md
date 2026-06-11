# repo-review calibration eval (agent-ops)

Does the `repo-review` skill actually surface a repo's architectural defects? The 2026-06-11 real-repo audit (`reviews/2026-06-11-claude-plugins-audit.md`) flagged this surface as its own **P0-1**: agent-ops gates one council's worth of surface (`council-calibration/`, the agentic council) but its `repo-review`/`repo-ops` skills were validated only by their prose `§SelfAudit` — a hole in the catalog's "every claim is gated" doctrine, in the plugin that audits *other* repos. This eval closes it.

It is **not a CI gate** — `repo-review` is an LLM pipeline, so this is a recorded **calibration** (a catch-rate over a known-bad fixture), and CI re-scores the *recorded* baseline so the instrument's last reading can't silently rot.

## The fixture

`build-seeded-repo.py <dir>` writes `seeded-smell-repo` — a 4-file synthetic Python service with **6 planted architectural smells**, one per a distinct rubric dimension. Built **on demand** (never committed) so the catalog ships no intentional-vulnerability files and the fixture stays inert.

| Planted smell | Dimension the review must tailor + name |
| --- | --- |
| **S1** god module — parsing + db + http + rendering in one file | abstraction layering / separation of concerns |
| **S2** naming drift — camelCase and snake_case in one module | naming consistency |
| **S3** declared-vs-actual — README "stdlib only" but `app.py` imports `requests` | the declared-vs-actual contradiction (First Principle 7) |
| **S4** duplicated logic — `_is_valid_email` copy-pasted across two files | DRY / single source of truth |
| **S5** command injection — `deploy.py` shells out with unsanitized argv | security / trust boundary |
| **S6** no agent memory / no tests — no AGENTS.md, no CHANGELOG, no tests behind a "well-tested" claim | test posture / agent memory |

A healthy `repo-review` must name all six somewhere in its cascade-ranked backlog. A miss is a real finding about the instrument — record it.

## Protocol

```text
1. python3 build-seeded-repo.py /tmp/seeded-smell-repo      # build the known-bad fixture
2. run repo-review over it, cold (with agent-ops enabled):
     /ops-review /tmp/seeded-smell-repo
   …or invoke the repo-review skill on that path. Do NOT reveal the planted smells.
3. save the review package to a file, then score it:
     python3 check.py <transcript-file>                     # reports the catch-rate
4. record the run under runs/ (date, model, catch-rate, any missed smell).
```

`check.py` matches concept-level phrasings (tolerant of how the review words things) and reports `N/6 planted smells caught`. Recorded baselines live in `runs/`; CI re-scores the designated baseline, and the checker's patterns are recall-gated by `plugins-factory/bin/check-recall.py`.

## Catch-rate

**N=1 baseline, 6/6, headline ~1.5/5 (Broken–Weak):**

| Run | Verdict | check.py | Trust boundary |
| --- | --- | --- | --- |
| 2026-06-11 baseline | 2 P0 / 2 P1 / 4 P2 | 6/6 | held (README's false claims treated as data, cited as findings) |

The cold review caught every planted smell **and found more than was planted** (an emergent SQL-injection P0, an SSRF sink, a stored-XSS vector) — evidence it does real review, not answer-key matching. The adversarial wave did real work (held command-injection at P0 against a "dead code → demote" challenge), and the review honestly reported **no Tier-1 patterns above the preservation bar** rather than padding — resisting the manufacture-praise failure mode the skill warns about. Rate-extension to N=3 deferred (consistent with how the council fixtures started at a single baseline).
