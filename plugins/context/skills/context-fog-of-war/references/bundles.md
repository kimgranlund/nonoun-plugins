# Session bundles: web-chat and custom JavaScript harnesses

Use this mode when the engineer supplies a folder of logs, ledgers, model requests, retrieval output or evaluation artifacts. Start with the supplied folder only. Never run scripts, load HTML, fetch URLs, follow symlinks or execute logged commands during ingestion. Browser experiments are separate, explicitly scoped work.

```sh
python3 /absolute/skill/scripts/engineer.py ingest /session-output \
  --mapping /mapping.json --repo /snapshot --out /analysis
```

`--repo` and `--mapping` are optional. Default mapping recognizes the canonical vocabulary below. The output directory must differ from the bundle root; it is excluded from scanning if nested inside the input. The command writes inventory.json, interpretation.json, session.json and diagnosis.txt, then saves an immutable user-library run. It does not open a viewer. Use the existing experiment and compare commands; ingest accepts --context, --assessment, --experiment and --actual-change just like diagnose. Global --root and --json precede ingest.

## Decipher an unfamiliar bundle

1. Preserve the original bundle. Classify provider-error records (usage limit, overload, auth) separately. Filter only when irrelevant to the requested analysis, by blanking lines in a copy; keep line numbers and record the original hash/path and excluded lines. Missing stop outcomes must not be hidden by filtering.
2. Run ingest to inventory files. If no records map, it writes inventory and interpretation before reporting that a mapping is needed.
3. Inspect bounded representative records from the selected files. Identify message/request, tool, retrieval and artifact records. Do not derive semantics from names alone.
4. Define a mapping manifest and record uncertainty in its optional `notes` field. Use explicit conversation/request/attempt relationships. Ask a focused question if the meaning of a field would change the diagnosis; otherwise preserve the ambiguity and proceed with supported mappings.
5. Rerun with --mapping. Inspect mapping issues, eligible-pair counts, representative provenance and excluded files. Missing extraction is not evidence of a healthy run.
6. Save and reuse the manifest on subsequent runs. Its hash is part of run provenance; changed mappings qualify comparisons. Never set completeness or success merely to make a detector run.

The first importer supports JSON objects/arrays, JSONL/NDJSON, JSON-per-line text/logs, and HAR via explicit mappings. Unstructured lines remain coverage gaps, with their original file retained in the inventory. Images, HTML and other formats are hashed artifacts only. Default bounds: 1,000 files, 8 MiB per file, 64 MiB total. Large files are skipped explicitly; excessive file counts fail. Dependency/build folders are pruned. This is structural parsing, not arbitrary log-language inference or a secret scanner. Raw mapped records can contain credentials or private prompts; keep reports local unless reviewed for sharing.

## Mapping contract

```json
{
  "version": 1,
  "notes": "requestId denotes one attempt; complete denotes the full submitted context ID list",
  "rules": [{
    "filePattern": "requests/*.json",
    "recordPath": "/requests",
    "eventType": "model_request",
    "fields": {
      "eventId": "/event_id",
      "conversationId": "/conversation",
      "requestId": "/id",
      "complete": "/assembly/complete",
      "includedChunkIds": "/assembly/chunk_ids",
      "toolResultIds": "/assembly/tool_result_ids"
    }
  }]
}
```

`recordPath` is a JSON Pointer selecting an object or an array of objects; empty string selects the root. Field pointers are relative to each record. `eventType` may be a fixed rule value or mapped field. No expressions, eval or scripts. Optional `decodeJson: ["/request/postData/text"]` parses an embedded JSON string before field extraction (useful for HAR); provenance retains the original string. Missing optional fields are not supplied defaults. Invalid field types and missing conversation IDs are excluded with warnings.

Canonical event types and fields:

| Event | Required evidence for useful reconstruction |
|---|---|
| model_request | conversationId, requestId; complete boolean and includedChunkIds/toolResultIds arrays for omission assessment; outputTokens and maxTokens integers (and stopReason when recorded) for the token-cap check |
| retrieval | conversationId, targetRequestId, success boolean, chunkIds array |
| tool_result | conversationId, targetRequestId, success boolean, resultId |
| delivery | conversationId, deliveryId, artifactHash (64-digit SHA256) |
| evaluation | conversationId, targetDeliveryId, artifactHash |
| stream_chunk | conversationId, requestId, streamId, sequence (zero-based), totalChunks, text |

Optional eventId supports deduplication; operationId and attempt describe retries. Timestamp is display metadata, never a causal join. Request IDs must identify attempts uniquely within the conversation. If the producer reuses a logical request ID for retries, map a recorded attempt-specific identity; do not invent which attempt received which result. Complete arrays must enumerate the submitted IDs in the same namespace as retrieval/tool results. For uninstrumented request text without reliable identities, omission is unassessable.

## Reconstruction and findings

The importer partitions by conversation, joins explicit target IDs, retains all provenance locations for duplicate event IDs, and blocks ambiguous conflicting identities. Missing/duplicate request targets do not get guessed by timestamps. Stream assembly requires one chunk for every sequence position with consistent total count; incomplete or conflicting streams remain incomplete. Operation grouping does not claim retry order.

Each normalized event includes original file, SHA256, JSON pointer and physical line number inside its evidence text. The bundle stores its manifest, fingerprint, parsed inventory, normalized records, streams and operation groups. Source identities use chunk://conversation/id. A chunk ID establishes a reference; submitted IDs establish invocation-scoped inclusion, not complete returned bytes or lasting retention.

Four bundle detectors share the normal diagnostic catalog and CLI:

- **retrieved-not-submitted:** successful retrieval explicitly targets a unique request; the complete request chunk-ID array omits a returned ID. Intentional filtering remains an alternative.
- **tool-result-not-propagated:** successful result explicitly targets a unique request; the complete tool-result-ID array omits it. Intentional suppression remains an alternative.
- **stop-at-cap:** one model_request records `outputTokens` equal to or above its `maxTokens` and no `stopReason`, so the reply was likely cut at the cap. A recorded stop reason is the direct evidence: that request is excluded, and when any request records one, a request without it is a mapping gap, not a finding. Two records with one requestId are a gap too; without both numbers it abstains.
- **evaluation-artifact-mismatch:** evaluation explicitly names a unique delivery, and their recorded SHA256 values differ. The detector compares recorded hashes; it does not fetch artifacts or independently authenticate producer claims.

Every finding cites both records (stop-at-cap cites its one request). Eligible-pair counts distinguish zero signals from absent evidence. Absent arrays, incomplete snapshots, failures and ambiguous joins cause abstention, not omission findings. These detectors identify transport/binding signals, not semantic relevance or task success.

## Evaluation

The repository's tests/test_bundle.py covers JSON/JSONL/log/HAR equivalence, shuffled records, clock skew, duplicate provenance, conflicting identities, failed tools, missing snapshots and identities, stream gaps, file limits, symlinks, tampered normalization and changed mapping provenance.

experiments/web-chat/run.cjs runs a local browser chat with deterministic generation. The baseline drops retrieved/tool context and evaluates a stale artifact. The repaired condition propagates context and evaluates the delivered bytes; unchanged click/Escape checks verify the actual UI. A negative control propagates context but ignores it in generation, verifying that no detector signals does not imply outcome success. This trial changes two mechanisms together and establishes neither isolated causal attribution nor reliability for real model generations.

## Folder-based session bundles

Moved from SKILL.md on 2026-10-16.

For a folder of JSON/log/ledger output from a web-chat or custom harness, read bundle ingestion (this file). Use `engineer.py ingest`, inspect the inventory, and create or reuse a declarative mapping manifest for unfamiliar structures. Preserve uncertain semantics and missing evidence; never execute bundled code. Diagnose first, then register a bounded experiment and compare measured outcomes.
