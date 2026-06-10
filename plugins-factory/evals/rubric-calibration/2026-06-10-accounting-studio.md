# Rubric application — accounting-studio (2026-06-10, cold)

**Candidate:** the maintainer's global `accounting-studio` skill (invoicing studio: Toggl pull → HTML invoice; 8 modes, stdlib CLI + lib, schemas, template, evals). **Verdict: BLOCKED** — P1 3 · P2 3 · P3 5 · **P4 2** · P5 3 · P6 4 · P7 4 · P8 3 · **P9 2**. *Sensitive values found in the candidate are redacted here by policy.*

## The findings that set the verdict

- **P9 = 2 — the packaged artifact would ship its author's books.** The would-be package root contains a **live API token** (`.env`), the real client registry (supplier tax/bank identifiers, four real clients' contacts), cached client time data, and issued invoices — protected only by `.gitignore`, which a directory-copy install does not honor. PII survives even perfect data-exclusion: a template build script's docstring and the COMMANDS doc hardcode the author's real name, tax-id-shaped value, phone, and workspace id as "examples." *(Action for the owner, independent of any carve: rotate the token; scrub the docstring examples.)*
- **P4 = 2 — dangling references before any install:** SKILL.md cites `references/schemas/*.json` paths that don't exist (schemas live at `schemas/`); a documented workflow step points at `/tmp/…`; the gate suite depends on library-level scripts (`score-routing.py`, `run-skill-gates.py`) the bundle doesn't contain. Also: commercially-licensed fonts bundled (redistribution not permitted).
- **P2 (AP-P3, the hopeful guarantee, named verbatim):** a 459-line mechanical invoice checker exists and the CHANGELOG claims it converted self-audit items "to actual mechanical gates" — but nothing invokes it (grep-verified). Aspiration, not a gate.
- **P5/P7/P8 — the CREDIT phantom:** `skill.json` declares a CREDIT mode the frontmatter disclaims, the code lacks, and the docs half-removed across three versions; high-form CHANGELOG with verifiably stale claims (the `check-manifest-sync` drift class).
- **Strengths the carve inherits:** P3 = 5 (one domain, explicit deferred/out-of-scope ledger); structural approval gate in code; eval-backed routing corpus with adversarial hand-offs (P7 4); textbook progressive disclosure (P6 4).

## Top 3 carve fixes

1. Tool/data separation: all personal state out of the distributable (runtime data dir); scrub PII examples; replace licensed fonts with the bundled OFL alternative.
2. Kill or ship CREDIT — one synchronized pass over manifest/docs/corpus, then a manifest-sync-class gate so half-applied fixes can't recur.
3. Wire the guarantee (invoke the checker post-render, or ship it as a hook) + fix the three dangling schema refs + declare/vendor the dev-gate dependency.

## Calibration notes (what this taught the rubric)

P4 and P9 discriminated hardest — their mechanical/file-level tests alone separated "excellent skill" from "unshippable plugin." P2's AP-P3 named the exact defect before inspection found it. P8 discriminated in an unanticipated direction: **high-form/low-truth** changelog claims — an anchor gap. P1's "personal one-off vs shareable unit" clause was the right frame for the data entanglement, suggesting an explicit personal-state hard test. P3/P6 near-auto-passed (single well-authored skill).
