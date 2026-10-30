# Evidence-backed diagnostics v1

`scripts/diagnostics.py` owns a versioned, deterministic catalog and runs during hydration. It can also enrich an existing validated report:

```
python3 scripts/diagnostics.py --data session.json --out session.json
python3 scripts/fog.py validate session.json
```

The optional `diagnostics` object contains the catalog, coverage counts, limits and candidate findings. Existing `decisions` and manually reviewed `findings` remain separate. Running diagnostics replaces only its own object and is deterministic. Every candidate includes exact event excerpts, trace lines, event/source IDs, a signal-confidence label, observation, qualified hypothesis, alternative explanations, proposed guidance and a validation experiment. No recommendation is applied automatically.

## Detectors and exclusions

- **Failed discovery:** require a matched call/result, a lookup request, a concrete lookup-error signal and an explicit failed outcome. Ordinary grep no-match exit 1 alone is not a failure finding. A failure can be an intentional probe. Wrapped compound commands may leave the specific failing subcommand ambiguous.
- **Repeated retrieval:** use recorded full returns or overlapping explicit line ranges. Deduplicate exposure records within one event. Suppress across known edits and compaction. Unknown partial ranges are insufficient. Repeated returned images may be legitimate visual verification; unrecorded edits and hidden context eviction remain alternatives. This does not establish wasted tokens or useless context.
- **Truncation:** require an explicit marker in a returned output. A partial exposure alone is insufficient. Command text, user messages and hypothetical examples in requests are not inspected as result evidence. A tool printing a marker can still be a false positive; inspect the original output before judging impact.
- **Stop at the token cap (`stop-at-cap`, bundles):** a model reply cut at `max_tokens` carries no output marker. When the trace records no stop reason, `outputTokens` equal to (or above) the request's `max_tokens` is the evidence to map: put both on one `model_request` record (`outputTokens`, `maxTokens`, and `stopReason` when recorded; [bundles](bundles.md)). The detector abstains without both numbers, excludes a request with a recorded stop reason, and records a gap, not a finding, for a request without one when others have it, or for two records sharing one requestId. Equal usage is indirect; a recorded stop reason settles it.
- **Lookup request (failed discovery and broken reference):** `shell_lookup` reads one shell command. These count as a lookup: the readers `cat`, `head`, `tail`, `sed` (any script, but not `sed -i`), `nl`, `wc`, `less` and `more`, plus `rg`, `grep`, `find` and `ls` targets; a read inside a pipe; a read with a stderr redirect (`2>/dev/null`, `2>&1`, `2>>log`); a read after `cd`, `pushd` or `popd` in the same command (the target stays relative, as the error line prints it); a `$VAR` target assigned earlier in the same command (`NAME=value` or `export NAME=value`). These do not: a segment with a stdout redirect (`>`, `>>`, `1>`, `>|`, `&>`, `>&`), any heredoc, `git show REV:PATH` (no reader parses it), and a `$VAR` assigned in an earlier call: the trace cannot show that the value survived to the later call, so tracking it would invent a lookup the run may never have made (Claude Code's Bash tool, for one, starts each call in a fresh shell). An unresolved variable target is recorded as a coverage gap, never matched bare.
- **Broken reference:** a literal failed-lookup target must appear in previously returned named guidance. The path may be an example, a working-directory mismatch, or unrelated to the failing subcommand. Treat as low-confidence provenance-based candidate, not causal attribution.
- **Late guidance:** compare first observed returns of AGENTS.md/SKILL.md with earlier edits under their directory. Scope proximity is only a hypothesis. Root/ambiguous paths are excluded; task applicability, inherited/injected instructions, hidden delivery and prior retention cannot be established by this heuristic. Require review before proposing earlier mandatory loading.

Coverage `assessed` counts eligible observations or literal targets considered, not complete semantic coverage or unique tasks. Zero findings is not proof of a healthy context system. Opaque wrappers, incomplete read extraction, unrecorded changes and absent scope metadata reduce coverage.

## Investigation workflow

1. Start from the engineer's question or a candidate detector signal.
2. Open **Investigate**, filter a detector, and inspect its observation and supporting records.
3. Use **Show evidence path** to focus the relevant events on the unified canvas. This deliberately switches to a focused route and, only when necessary, advances the replay cutoff to make cited events visible. Sequence and highlighted ancestry are not causal proof.
4. Confirm or reject alternatives, including deliberate probing, verification, different snapshots, context compaction and hidden instruction delivery.
5. Propose a specific change to a named entry point, instruction or retrieval operation. If scope/target is unknown, report the missing evidence instead of inventing an edit.
6. Validate on comparable tasks, preserving outcome quality. Compare failure/retrieval/truncation counts, discovery latency and recorded token usage only where the instrumentation supports them.

The first release does **not** automatically run A/B experiments, measure correctness, identify every conflicting instruction, infer exact retained context, or compute causal savings. Recommendations are experiment proposals. A counterfactual improvement requires additional runs and a task-success rubric.

## Evaluation

`tests/test_diagnostics.py` covers positive and negative cases: known overlap vs disjoint/unknown ranges, edit/compaction invalidation, direct and wrapped failure signals, no-match exclusions, output vs request truncation, reference provenance, heuristic scope, deterministic reruns and invalid citations. These synthetic checks establish implementation behavior, not production precision or recall. Calibrate on labeled real sessions before assigning defect probabilities.

## Canvas investigation

Badges anchor each candidate once, at its final supporting event; collapsed episodes aggregate those anchors. This is a navigation convention, not proof that a defect originated there. Earlier supporting events remain exact linked citations. Clicking a badge opens the scoped Findings panel and preserves the camera, replay and layout. Trace evidence on canvas explicitly focuses the supporting path. Findings disclose observations, suggestions and validation separately from hypotheses and alternative explanations.

Diagnostic focus is independent of exposure filtering and explicit Focused route layout. All findings or one candidate expands supporting-event episodes and dims unrelated context. The map retains original edges, with their original meanings; it does not invent causal connections between citations. Earlier replay positions only show evidence already reached. The normal manual expansion state is retained underneath this temporary expansion. Filter selection persists per report. “Focus this finding on canvas” pans to the first visible citation without zooming; “Trace evidence on canvas” remains the explicit compressed-route action.


Truncation findings now distinguish outer wrapper aggregation from nested command output and retain envelope locations/token counts in metrics. The frozen base-ui cohort regression cases assert Tidebook e18 outer, e29 nested; Cueforge e27/e40/e50/e57 nested. Seatcraft has no detected marker in the frozen window, not confirmed full retention. Rehydration comparisons measure extraction coverage on identical traces and must not be presented as author-run improvements.

## Coverage explanations and blind spots

Each detector coverage row retains its legacy `assessed` scan count and adds `explanation`. Scan counts are not eligible comparisons, defect counts, context tokens or a denominator for precision/recall.

`explanation.status` distinguishes:
- `assessed-no-signal`: eligible inputs were checked with no candidate finding.
- `findings-observed`: eligible inputs produced candidates, not proven defects.
- `partial`: some candidates were assessable and others stopped at missing prerequisites.
- `insufficient-evidence`: observed candidates could not pass a required evidence gate.
- `no-eligible-candidates`: no applicable trigger was recorded, or explicit unsuccessful results were excluded from a success-only detector.
- `unavailable-telemetry`: the report lacks the explicit bundle request-assembly or evaluation/delivery projection required by that detector.

Rows include eligible counts and units, excluded cases, grouped blocked candidates with event excerpts, and `nextEvidence`. Requests stop at the first missing prerequisite for each candidate: fix a missing target link before asking for a complete identity list; request a complete list before interpreting omission. `count: null` denotes absence of telemetry, not a measured number of missing events. An absent trigger does not automatically require more logging; `investigationEvidence` describes what would be needed only if that question is relevant.

Repeated retrieval counts comparable consecutive source-return pairs separately from observed returns. A first return, an intervening edit, or compaction starts a new comparison window. Two partial returns without ranges cannot establish overlap. Broken-reference attribution needs earlier returned guidance; the current repository cannot replace missing historical content. Native Codex/Claude reports do not establish complete request assembly merely because their tool outputs are visible.

`blindSpots` preserves semantic limits even when eligible checks pass. Unsupported-wrapper warnings are attached separately; they do not create invented missing calls or findings. For affected wrappers, emit an ordered tool/argument/status/result ledger, plus a stored path snapshot only when required for attribution. No hidden values are reconstructed from today's files. No amount of scan coverage proves understanding, retention, causation, relevance or acceptance.

CLI `diagnose` prints these explanations and minimal evidence requests. Full grouped gaps and exact citations are saved in the immutable run. Existing historical reports can be diagnosed again without rehydration; new coverage explanations do not alter their workflow outcomes. Newly generated reports inherit the same additive fields. Existing viewers may still display the legacy summary counts; the detailed coverage interface in this version is the CLI/JSON record.


## Signal triage

All signals remain in the report. Each has a versioned `triage` record: `needs-review` or `likely-benign`, a reason, supporting citations and the smallest next evidence request. Triage does not change exposure, detector eligibility, or historical outcomes.

The initial conservative rule qualifies truncation only when its own single returned result explicitly says required answer/evidence was returned and optional material was omitted. Contradictory missing-required/error statements prevent qualification; multi-tool batches abstain because a sibling's qualification cannot explain another output. This is a reported assertion, not verified acceptance. Other wording may remain needs-review. No benchmark case ID, rationale, expected label, or action rating is used by the classifier.

The CLI retains likely-benign groups for inspection but does not propose corrective work from them alone. Mixed groups retain each occurrence's triage and still require review. For repeated reads, request intent linked to the later call; for omitted context, request the item-specific inclusion requirement or exclusion reason. Absent intent is not evidence of waste or harmlessness. The detailed triage interface is currently CLI/JSON; the viewer retains all candidate signals.


Legacy plain command strings and nested `arguments` envelopes use the same lookup parser. A generic missing-file result can establish failed discovery for one plain single-file reader. Compound commands, redirects, pipelines, multiple operands and unresolved variables still require explicit attribution; a sibling failure never establishes that a read failed.

## Explicit source delivery contracts

Four additive checks use `deliveryContract`: `required-source-before-write`,
`incomplete-source-delivery`, `unfinished-continuation`, and `excluded-source-read`.
They never derive a required selection from the full manifest, infer an unseen
ledger read, or equate returned bytes with understanding. Existing detector IDs,
findings, triage and scan counts remain available.

Supply the contract on an existing hydrated report, or as a separate CLI input:

```sh
python3 scripts/diagnostics.py --data session.json --delivery-contract contract.json --out diagnosed.json
python3 scripts/engineer.py diagnose --data session.json --delivery-contract contract.json
```

The engineering run saves the supplied contract in its input snapshot. Hydrate
native traces first with the existing host adapter. Neither command executes a
command found in a trace or reads a source path named by the contract.

```json
{
  "mode": "authored-replay",
  "intent": "fresh-builder",
  "requiredSources": [{
    "path": "packages/kit/docs/api.md",
    "contentHash": "optional SHA256 of the complete required resolved body",
    "evidence": {"eventId": "e1", "traceLine": 1, "excerpt": "Exact instruction declaring the required body."}
  }],
  "applicationPaths": ["apps/example/"],
  "excludedPaths": ["history/"],
  "sanctionedPaths": ["history/sanctioned-example/"],
  "evidence": {"eventId": "e1", "traceLine": 1, "excerpt": "Exact applicable policy text."},
  "observationWindow": {
    "throughEventId": "e20",
    "sourceReturnsComplete": true,
    "evidence": {"eventId": "e2", "traceLine": 2, "excerpt": "Exact assertion of the bounded returned-read observation coverage."}
  }
}
```

The example contains placeholders, not usable citations. Every citation must name
an existing event, its original trace line, and an exact nonempty excerpt. Invalid
citations prevent the relevant finding and produce a coverage gap. Citation checks
verify provenance, not the truth of an analyst's interpretation. In particular,
pointing at an unrelated event does not establish an observation window or an
exclusion policy. Review these semantics independently before supplying a contract.

`mode` records interpretation provenance: `analyst-supplied` (default), `observed`,
`authored-replay`, or `retrospective-policy`. These are supplied labels, never an
automatic authenticity determination. Historical traces must not gain fabricated
policy or completeness events. A retrospective exclusion is a replay of an explicit
policy against observed reads, not proof of contemporaneous disobedience. The
finding metrics and `diagnostics.delivery` retain the mode and qualification.

`observationWindow.sourceReturnsComplete` means that relevant returned-read evidence
through the cited cutoff was captured and reviewed. It does not mean the model's
complete context, hidden helper execution, retained memory, or understanding was
observed. Missing or uncited coverage, hidden relevant calls, or an opaque recovery
must remain unknown. Do not manufacture a completeness assertion to force a finding.
Without this assertion, missing required returns and unresolved recovery generate
coverage gaps. A first write requires an attributed mutation result within an
explicit `applicationPaths` prefix. A call alone is not a successful write. Reads
must precede that first observed write; later recovery does not erase the earlier
gap. Without a write, continuation analysis may use the inclusive window cutoff,
while before-write coverage remains unassessable.

Paths use report-relative identities. Optional `sourceBase` supplies a base only
when a returned page has no `pathBase`; explicit page bases take precedence.
Directory comparisons use path boundaries, so `history-extra` does not match
`history`. An exact file exclusion also covers its fragments. Maintenance intent
never inherits fresh-builder exclusions, and sanctioned examples suppress only the
excluded-read signal. Source requests, inventory entries and edits are not reads.
`diagnostics.delivery.sources` distinguishes inventory availability, observed
requests, returned evidence, complete matching bodies and unknown coverage.

### Returned page and packet support

Source pages carry `source` (or legacy recipe `id`), optional `renderer`, `sha256`
delivery identity, `offset`, `end`, `total`, string `content`, `complete` and `next`.
`contentSha256`, when present, is the complete resolved body's hash, not a page
hash. Matching contiguous ranges must have consistent identity, totals and content;
conflicting overlaps, missing prefixes, changed hashes, or a terminal page alone
cannot establish a complete body. Offsets use Unicode code points. A complete
native read can establish a body without a requested content hash, unless recorded
clipping or command bounds contradict completeness.

Metadata and search pages can finish their own continuations without establishing
referenced source bodies. Complete `task-packet-page` chains are reconstructed as
recorded JSON, then each complete inner `kind: body` is credited only after its
content hash verifies. Direct complete `task-packet` results use the same check.
References never count as bodies; selected JSON records do not substitute for an
entire source file. An output-file receipt establishes that bytes were written,
not that the file's body was returned. This parser does not open receipt paths.

Only returned nonempty executable `next.args` lists are continuation candidates.
Legacy offset-only descriptors produce an explicit eligibility gap. Following the
request without its matching complete return does not resolve the signal. Tool
clipping remains the existing `truncation` detector. Intentional `head`, `cut`,
`tail` and bounded `sed` requests are separately recorded as command bounds in
`incomplete-source-delivery`; they do not become tool-output truncation.

Synthetic and producer-integration checks establish these mechanics, not autonomous
routing efficacy, production precision, reduced cost or improved generation quality.
