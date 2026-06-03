# CHANGELOG — adia-ui-gen-review

## [2.9.0] — ported into adia-ui-forge

Faithful port from the @adia-ai monorepo's maintainer skill, de-repo'd and made self-contained. The closed-loop quality system (derive ideal spec → decompose actual → score → root-cause → corpus fix) is preserved unchanged. De-repo changes:

- Phase-1 spec sub-skill is now **adia-ui-authoring** (the in-plugin authority on AdiaUI primitives + composition contracts), replacing the monorepo's `adia-ui-kit`. The broad-sweep peer is **adia-ui-dogfood**, replacing `dogfood-sweep`.
- The four companion QA scripts (`gen-review-decompose.mjs`, `gen-review-coverage-audit.mjs`, `validate-cycle-scores.mjs`, `gen-review-status.mjs`) are now **skill-owned** under `scripts/` (they previously lived in the repo's `scripts/qa/`). They resolve monorepo paths from the working directory (run from the monorepo root) and the schema from `${CLAUDE_PLUGIN_ROOT}`. The absolute `js-yaml` import in the coverage audit is now a bare specifier.
- All in-plugin references use `${CLAUDE_PLUGIN_ROOT}/...`; the trust boundary and PEV rationale point at the shared-infra docs (`references/shared/content-trust.md`, `references/shared/pev-rationale.md`).
- Monorepo conventions (`apps/genui`, `packages/a2ui/`, `@adia-ai/*` scope, `npm run harvest:chunks` / `gallery:generate` repo-local steps) are kept by design. Instance data (cycle ledgers, scratch paths, scores history, commit hashes, dated narration) is dropped; durable knowledge + the rubric/schema is retained.

The version history below records the rubric/schema/protocol evolution from the source skill.

---

## [2.9.0]

Canonical card-ui slot grammar finalized in §CorpusHTMLPatterns. Earlier `row-ui`/`col-ui` header-wrapper workarounds are retired now that the transpiler preserves `slot=` universally and leaf-type element children survive transpilation.

- `loop-protocol.md` §CorpusHTMLPatterns rewritten to reflect the post-fix canonical patterns; the wrapper antipattern is explicitly marked "do not reintroduce".
- New §SectionBleedDecisionRule: when to use `<section bleed>` (media/tables) vs plain `<section>` (lists/forms).
- For trailing button carets: `button-ui[icon-trailing]` (parallel to leading `icon=`).

## [2.8.0]

Substrate Phase-5 fix arc. Traced header/bleed bugs to two gaps in the A2UI transpilation pipeline:

1. `extractProps()` dropped all `slot=` attributes (HTML-standard, not a yaml-declared prop). Fixed with a universal `slot=` preserve at the top of `extractProps()`.
2. `card.css` heading rule didn't match transpiled `<text-ui variant="…">` variants (`HTML_TAG_MAP` converts `<h1>`–`<h6>` and `<p>`). Fixed by extending the heading + description + unslotted-children selectors to match the corresponding text-ui variants.

`loop-protocol.md` §CorpusHTMLPatterns updated: the canonical slot grammar now works identically in corpus HTML and hand-authored full-page HTML.

## [2.7.0]

Comprehensive §CorpusHTMLPatterns expansion (validated FAILS/WORKS pairs): header controls, `section bleed` for list/table content, `style=` survival on A2UI custom elements vs native HTML, `card-ui raw` anti-pattern, multiple `<section>` per card, `chart-ui type="sparkline"` as image placeholder, `chat-input-ui` self-containment, `nav-group-ui open`, `accordion-item-ui text=` (not `label=`), `col-def key=` (not `field=`), `integration-card-ui` for integration grids. Design rules: check-ui over icon-ui for permission matrices, colored badge-ui role columns, progress-row-ui for usage meters, every card-ui needs `<header>`.

## [2.6.2]

Human-QA findings absorbed. Added `rubric-score.md` §DomainMismatchCheck (pre-scoring gate comparing chunk domain to gallery prompt group) and two §KnownGaps (viewport clipping; RETRIEVAL_SCORE failures). New §CorpusHTMLPatterns: alert-ui content slot, table-ui `col-def`/`data`, `size="sm"` ban inside card-ui body.

## [2.6.0]

Added `loop-protocol.md` §CorpusHTMLPatterns (FAILS/WORKS for card header title+subtitle and chart-ui inline data) and `rubric-score.md` §KnownGaps (layout-axis collapse; empty chart). §Teach routing table extended with two rows. §SourceOfTruth cross-references §CorpusHTMLPatterns and §KnownGaps.

## [2.5.0]

- **§SourceOfTruth** doctrine added to SKILL.md and loop-protocol.md: HTML pages are the source of truth; chunks are derived/aligned from HTML, not the reverse. Phase 5 fix plans require a SoT HTML lookup (domain → canonical HTML path table) before writing any corpus fix.
- **Overflow / clip detection in Phase 2** (`gen-review-decompose.mjs`): every text-bearing element is checked for layout overflow via `scrollWidth > clientWidth` / `scrollHeight > clientHeight` against computed `overflow: hidden`. Results land in the decomposed file as `overflowElements`.
- **§VisualGate in rubric-score.md**: non-empty `overflowElements` auto-promotes each entry to a P1 cosmetic finding. A structural score of 92+ cannot achieve PASSING if overflow is detected — visual and structural lanes are independent.
- **§ExitCondition** condition 2: `overflowElements.length = 0` for all prompts is now an explicit exit gate.

## [2.4.0]

- **`validate-cycle-scores.mjs`**: mechanized schema gate for `review/cycle-N/scores.json`. `--strict` exits 1 on any error.
- **`gen-review-status.mjs`**: ledger consumer — pass/fail counts, mean score, delta, failing prompts, exit-condition check. `--check-exit` exits 1 if the loop is not done.
- **§ManualHandoff** in loop-protocol.md: documents the human-executed steps between agent phases (Playwright requires a running dev server) and why the loop is intentionally semi-manual.
- **§SelfAudit checks 6+7** in SKILL.md: after any review cycle, run the schema gate and the exit-condition status check.

## [2.3.0]

- **Excellence threshold raised 80 → 92** (operator calibration). Acceptable band 70–91; Failing 0–69.
- **scores.schema.json bumped to 2.0.1**: fixed stale `rubricScore.score` maximum (110 → 105, aligning with the v2.0.0 D6 mechanical change).

## [2.2.0]

- **`references/teach-protocol.md`**: 8-branch decision tree for §Teach invocations, mapping evidence type to the exact file + edit required. Includes §VerifyAfterAnyBranch and §AntiPatterns.
- **Mode 5 — Teach** in §ColdStartTriage.
- **§SelfAudit check 5 mechanized**: `gen-review-coverage-audit.mjs --strict` is the mechanical gate for TAG_TO_COMPONENT coverage.
- **§Teach invocation surface** registered in skill.json `description:`.

## [2.1.0]

- **`gen-review-decompose.mjs`**: Playwright script mechanizing Phase 2 — navigates the gallery, screenshots the canvas, walks the DOM, writes screenshots/raw-dom/decomposed per prompt. Flags: `--cycle N`, `--group`, `--prompt`, `--port`, `--dry-run`, `--settle`.
- **`gen-review-coverage-audit.mjs`**: SelfAudit check 5 mechanized — reads component yamls, extracts `-ui` tags, reports any missing from `TAG_TO_COMPONENT`. Flags: `--strict`, `--json`.
- **§Teach routing table** in SKILL.md; anti-patterns block.
- **`TAG_TO_COMPONENT`**: covers all AdiaUI primitives plus `Native*` entries for quality-signal tracking of raw HTML elements in canvas output.

### Fixed

- Shell-skip recursion bug: `canvas-ui` and `a2ui-root` now skip-but-descend (previously returning null stopped all recursion).
- §Setup no longer incorrectly validates `gallery-latest.json` against `scores.schema.json` (that is the output schema, not the input schema).

## [2.0.0]

### Breaking changes

- **Deleted `rubric-spec.md`** (Phase 1 scoring removed): scoring the spec was circular self-assessment. Phase 1 now produces A-data only (binary success check).
- **D6 replaced with a mechanical check**: the subjective intent-satisfaction modifier (±10) became a mechanical root-component match (0 or +5). Max score 110 → 105; excellence threshold adjusted.
- **Phase 5 now conditional**: only runs for FAILING prompts.

### Added

- **`references/scores.schema.json`**: formal JSON schema for `review/cycle-N/scores.json`.
- **§TrustBoundary** in loop-protocol.md: Phase 2 and Phase 5 structurally separated via the decomposed file; DOM attribute allowlist (strips `data-*`, `aria-*` values).
- **`cycle-{N}.lock` sentinel** in §Setup: prevents N=2 ledger collision under concurrent invocations.
- **Human QA gate** in §Cycle Close: mandatory 5-prompt operator review before a cycle is COMPLETE.
- **Regression block**: cycles with `rubricScore.delta < -10` are blocked from proceeding to cycle close.
- **RENDER_FAILURE handling** in §Phase 2: prompts with <50px canvas height skip Phases 3/4/5.
- **Phase 2 primitive lookup table**: tag → component name mapping replaces agent interpretation.
- **File allowlist** for fix-plan `file:` entries in Phase 5.

## [1.0.0]

- Initial skill with four rubrics (spec, decompose, score, cosmetic).
- loop-protocol.md — six-phase closed-loop orchestration across all gallery prompts.
- rubric-spec.md, rubric-decompose.md, rubric-score.md, rubric-cosmetic.md.
- SKILL.md — §ExitCondition, §DataModel, cycle-ledger schema.
- skill.json — standalone skill manifest.
