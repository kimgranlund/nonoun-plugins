---
date: 2026-10-16
slug: contract-audit
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: solo
    agent: sdlc-lite:solo-L3 (fogskill5-solo-L3)
    model: claude-opus-5-5
    did: added scripts/audit.py, tests/test_audit.py, tests/fixtures/contract-audit/, references/contract-audit.md, references/learnings/contract-audit.md; edited SKILL.md, AGENTS.md, references/learnings/README.md; wrote this entry
  - role: verifier
    agent: sdlc-lite:verifier-L3 (fog-skill-contract-audit-verifier-L3, try 2)
    model: fable
    did: independent verification; try 1 failed on the missing conflict precision limit, try 2 pass
project: agent-ui (nonoun), task .sdlc/work/fog-skill-contract-audit/handoff.md
verification: independent verifier L3, try 1 fail (precision limit), try 2 pass (2026-10-16); skill tests 35 of 35
backup: /private/tmp/claude-501/scratch/cfow-backup-1792162475
---

# 2026-10-16: contract audit mode (static review of guidance and contract surfaces)

## Added
- `scripts/audit.py` (stdlib only, read-only): `scan` inventories surfaces from a mapping (or discovery globs), extracts entities, ids and directive statements per surface, and runs seven mechanical detectors: `cross-surface-conflict`, `undefined-reference`, `schema-mismatch` (a JSON Schema subset; unsupported keywords abstain), `stale-generated` (file times, and embedded source lines), `index-only-rule`, `modality-leak`, `generic-oracle`. Output: JSON report with per-detector coverage and `status: candidate` findings with file:line excerpts, plus a text summary. `link` lists the surfaces a trace finding (an excerpt, or a finding id in a v2 `session.json`) touches by entity, id or exact five-word phrase.
- `references/contract-audit.md`: surface kinds, discovery in an unfamiliar repo, the mapping contract (including `regions`, `include`, `exclude` and `scope` for guidance embedded in code), and the nine-family rubric, each with signal, evidence rule, script coverage, blind spots, cause class and harness tag.
- The conflict detector's precision limit (adjacent-situation `notFor` entries pair by design; field run 0 of 12 and 0 of 8 held on the current tree, 2 of 9 on a pre-fix snapshot) in `references/contract-audit.md` section 1 and in the report `limits` from `scripts/audit.py`.
- `references/learnings/contract-audit.md`: lessons 30 and 31, Applies to: both; indexed in `references/learnings/README.md`.
- `tests/test_audit.py` (11 tests; `test_link` also covers `link --finding ID --data session.json`) with `tests/fixtures/contract-audit/` (synthetic, no project names). Each detector test fails with its detector stubbed to return no findings.

## Changed
- `SKILL.md`: routing row "Codebase or corpus (no trace)"; the checklist intro routes a no-trace input to the contract audit; step 11 cites the contract file `audit.py link` names; the frontmatter description names the static audit.
- `AGENTS.md`: layout lines for the new reference, script and fixtures.

## Fixed
- None.

## Open
- From the try 2 verifier: the `--text` summary never prints the report's `limits` (the conflict precision limit lives only in the JSON), and the modality-leak finding keeps only the first 5 statement lines as evidence while its title counts every type. Applied in 20261016-open-items.
1. Conflict precision on a large guidance set is low: in the agent-ui field run 0 of 12 reviewed candidates held without topics, and a selection `notFor` reason reads as a conflict by design. Topics declared from the scenarios narrow it (54 to 8 on HEAD) but did not remove the adjacency false positives.
2. Rule coverage gaps, checks narrower than their rule, literal-reading hazards and prose repair text are rubric-only; the field run's script caught 3 of 8 field cases, partly 1, and the rubric all 8.
3. `modality-leak` matches a capitalised English word that is also a type name (one field false positive).
4. Triggered surfaces count as neither framed nor index-only, so a rule mirrored only in a triggered skill is still reported as index-only.
