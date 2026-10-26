---
date: 2026-10-16
slug: open-items
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: solo
    agent: sdlc-lite:solo-L2 (fogskill6-solo-L2)
    model: claude-opus-5-5
    did: changed scripts/audit.py, scripts/bundle.py, scripts/reconstruct.py, scripts/coverage_report.py, SKILL.md, references/contract-audit.md, references/diagnostics.md, references/bundles.md; added tests/test_stop_at_cap.py, five tests in tests/test_audit.py, tests/fixtures/contract-audit/tools/tools.json; annotated the Open items of three earlier entries and added the matching exception to updates-log/AGENTS.md; after the adversarial challenge (rebuttal in the agent-ui task records), applied its six keep-with-change points; wrote this entry
  - role: verifier
    agent: sdlc-lite:verifier-L2 (fog-skill-open-items-verifier-L2)
    model: claude-sonnet-5-5
    did: independent verification after the adversarial debate (challenge 0 revert, 6 keep with change; rebuttal conceded all 7), verdict pass
project: the skill itself; Open items of updates-log/20261016-round-7-field-test, 20261016-contract-audit and 20261016-lookup-gaps (agent-ui task .sdlc/work/fog-skill-open-items/handoff.md)
verification: adversarial challenge (Sonnet) plus rebuttal, then independent verifier L2 pass (2026-10-16); skill tests 46 of 46
backup: /private/tmp/claude-501/scratch/cfow-backup-1792169942
---

# 2026-10-16: apply the open items from round 7, the contract audit and the lookup gaps

Ten items: nine applied, item 10 ruled out.

## Added
- `stop-at-cap` bundle detector (item 6): `scripts/bundle.py` maps `outputTokens` and `maxTokens` (integers) and `stopReason` (string) on a record; `scripts/reconstruct.py` emits a candidate for a `model_request` whose `outputTokens` reaches `maxTokens` with no `stopReason`, and abstains without both numbers; a request with a recorded stop reason is listed under `excluded`, and a request without one when others have it, or two records sharing one requestId, is a coverage gap, not a finding; `scripts/coverage_report.py` has its coverage row (`unavailable-telemetry` outside a bundle). Tests: `tests/test_stop_at_cap.py` (5 tests).
- `scripts/audit.py` `scan` adds an `issues` line when a mapping with producer guidance (a `prompt`, `persona`, `skill` or `guide` surface with a matched file) has no repair surface (kind `check` or `repair`) or no tool surface (kind `tool`) with a matched file; a mapping-level `noSurface` (`repair`, `tool`: the reason) silences each, and a catalog-only or corpus-only mapping gets none (item 2). Test: `test_mapping_surface_warning`. The fixture mapping gains a `tools` surface and `tests/fixtures/contract-audit/tools/tools.json`, so the fixture scan prints no issue.
- Each audit inventory entry carries `statementLines`, including a Markdown file's frontmatter lines (audit report version 1.1.0).
- `tests/test_audit.py`: `test_include_exclude_list`, `test_link_scoped_to_statements`, `test_text_summary_limits`, `test_modality_evidence_cap`, `test_mapping_surface_warning`, `test_link_reads_frontmatter`. The first round's eight new tests failed against a copy of the backup with only the new test files dropped in (4 failures, 4 errors). After the challenge, the five new or changed tests (`test_link_reads_frontmatter`, `test_mapping_surface_warning`, `test_modality_evidence_cap`, `test_duplicate_request_id_is_a_gap`, `test_recorded_stop_reason_is_excluded_and_a_missing_one_is_a_gap`) fail against the first-round copy (5 failures). All 46 pass now.

## Changed
- `SKILL.md` checklist step 3 (item 1): unless the question is why the run stopped, blank provider-error turns (usage limit, overload, auth) in a copy before hydrate or ingest, never delete them, so line numbers stay stable (both skip blank lines; `scripts/fog.py` and `scripts/bundle.py`), and cite the original trace path as provenance; step 11 names the blanked lines as a limitation and says a finding passed to `link` quotes the guidance it suspects, and a miss means quote more (item 5).
- `references/bundles.md`: decipher step 1 is the same exclusion; the model_request row lists `outputTokens`, `maxTokens` and `stopReason`; the detector list adds `stop-at-cap`.
- `references/contract-audit.md` (items 2, 3, 5, 7, 8): a Tool definitions surface row; discovery steps 4 and 5 declare repair text as `check` and tool definitions as `tool` and name the new `issues` line; `include` and `exclude` take one regex or a list; the report paragraph names `statementLines` and the `--text` limits; the link section says the phrase match reads only mapped statement lines and that a finding should quote the guidance it suspects; the modality-leak script line says the first 50 naming lines are evidence; `noSurface` is documented.
- `references/diagnostics.md` (items 6, 9): a stop-at-cap bullet (usage equal to `max_tokens` as indirect evidence when no stop reason is recorded), and a lookup-request bullet listing which shell forms count and which do not.

## Fixed
- `audit.py` crashed with `TypeError: unhashable type: 'list'` when a surface's `include` or `exclude` was a list; both now take a string or a list, any match counts (item 3).
- `audit.py link` matched five-word phrases on every line of a surface file; it now reads only the surface's `statementLines`, so lines outside `regions` or `include` (such as `import.meta.glob` calls) no longer match every query. A report without `statementLines` falls back to every line (item 4).
- `audit.py` `--text` summary now prints every `limits` line, the conflict precision line included (item 7).
- The `modality-leak` finding keeps up to 50 naming statement lines as evidence instead of the first 5 (`EVIDENCE_CAP`, also used by `index-only-rule`); `metrics.statements` counts them all, `metrics.evidenceShown` the kept ones, and the observation says "first 50 of M" when it cuts (item 8).
- `updates-log/AGENTS.md`: one exception to never rewriting a past entry, a trailing "Applied in <slug>." sentence on an Open line.

## Open
- Item 9: `git show REV:PATH` is documented as not a lookup; no parser for it was added.
- Item 10, ruled out: session-wide `VAR=` tracking across calls. The trace cannot show that a variable assigned in an earlier call survived to the later one, so tracking it would invent a lookup the run may never have made. Supporting fact: Claude Code's Bash tool starts each call in a fresh shell; Codex was not checked, and a continued Codex tty session can keep shell state. The same-command expansion and the `Lookup target is an unresolved variable` gap stay as they are.
- `references/bundles.md` cites `tests/test_bundle.py`, which is not in `tests/`.
