# Hydrated session contract

`session.schema.json` is the versioned contract between the skill and the shell. The top-level fields are `schemaVersion: 1`, `session`, `coverage`, `sources`, `events`, and `links`. `fog.py validate` checks the schema plus unique identifiers, ordered sequences, ranges, and referential integrity. The browser checks structural validity before replacing a loaded session.

## Source identity and event order

A source has a unique `id`, display `path`, and `inventoried` flag. Repository-relative paths are preferred. External paths are allowed without reading them. Inventory comes from Git tracked/unignored working-tree files, or a bounded directory walk if Git is unavailable. Symlinks are excluded; file contents are not copied. `session.revision` is HEAD provenance only, not proof that the snapshot is clean or historical.

Events follow trace order, not timestamp order. Each has a unique `id`, contiguous zero-based `seq`, `kind`, `label`, `actor`, timestamp (empty when absent), evidence (`traceLine`, `text`), and `exposures`. Evidence contains the original payload, rendered as inert text. Sequence includes pending calls and results separately so future tool output does not leak into an earlier replay position. The timeline itself shows upcoming events as retrospective navigation.

An exposure contains `sourceId`, `state`, and an explicit `basis`. Optional `startLine` and `endLine` are inclusive, one-based, and refer to recorded source output, not JSONL lines. States:

- `discovered`: path or reference encountered.
- `partial`: snippet, bounded read, or truncated return.
- `read`: successful complete single-source return, subject to trace fidelity.
- `edited`: confirmed mutation; separate from exposure of prior contents.

The map shows cumulative historical exposure. A later partial read does not erase an earlier complete read. An edit marks changed content, and a later complete read can establish exposure again. Source history retains all exposures. Compaction never erases history or asserts retention.

## Codex adapter coverage

Accepted records include `session_meta`, `turn_context`, `compacted`, and `response_item` payloads: `message`, `function_call`, `function_call_output`, `custom_tool_call`, and `custom_tool_call_output`. Calls/results match on `call_id`. Event telemetry is counted and omitted to avoid duplicate message representations. Unknown records remain visible. Malformed JSONL lines are counted in warnings; entirely unusable traces fail.

Automatic extraction supports direct `exec_command` / `shell_command` calls with a single `cat PATH`, `sed -n 'START,ENDp' PATH`, `head -n N PATH`, `rg --files`, or numbered `rg` search output. Read exposure requires an explicit zero exit code plus returned content. The output can be a structured JSON object or a Codex text envelope with an exit-code header. Truncated returns are partial with unknown ranges. Missing exit status is conservative: no read exposure is inferred. Apply-patch success results (`Success.` followed by `A/M/D PATH`) record edits.

Sequential wrappers such as `text(await tools.exec_command({cmd: "cat README.md"}));` and `image((await tools.view_image({path: "screen.png"})).image_url);` are statically decoded. Literal object keys, single/double quoted strings, numbers, booleans, nulls, comments, and multiple sequential emitted calls are supported. All statements must fit the grammar. Output blocks must match exactly in number, order, and emission type; otherwise the wrapper remains opaque. No eval, subprocess execution of trace code, or JavaScript runtime is used.

The same direct-tool extractor handles matched wrapped outputs. For literal compound read requests, returned bytes may be matched against files in the supplied repository and explicit `--source-root` directories. A whole-file match establishes returned content; a sufficiently long leading match is partial. Current sources are only witnesses: contents missing from the actual output are never supplied from disk. Changed historical contents may be missed. Files outside allowed roots, binary/large sources, short ambiguous contents, redirections, and heredoc script bodies are excluded from corroboration.

Supported parallel forms are `text(await Promise.all([tools.NAME(LITERAL), ...]));` and the corresponding `allSettled` form. A batch can also be assigned to a const/let variable and immediately emitted with `text(variable);` or `variable.forEach(text);`. Arrays are paired by input index, not completion order. AllSettled fulfillment values and rejection reasons retain their slot. Missing slots, malformed settlement objects, reordered/mapped results, and a rejected Promise.all with no result array remain opaque. Every decoded result includes a tool/output attribution block; exposure bases name the batch and slot.

Pipelines, dynamic arguments, transformed result arrays, general assignments/control flow, asynchronous polling, arbitrary script internals, and subagent threads remain unsupported. Parsed wrapper counts and opaque underlying call counts are distinct. A decoded wrapper does not imply all of its tools yielded attributable file exposure. These limitations are displayed in coverage.

## Skill-assisted hydration

For an unsupported tool, inspect its request and actual output together. Add sources and exposures only when that output identifies the source unambiguously. If a numbered snippet clearly appears in a wrapped tool result, a `partial` exposure is appropriate. If a compound output cannot be attributed to individual files, leave it opaque and explain the limitation. Record line ranges only when known.

To link events, add `{ "from": "e3", "to": "e7", "kind": "recorded", "reason": "..." }` when explicit evidence supports it, or `inferred` with a qualified rationale. The shell shows links only once both events have occurred. Preserve trace-line provenance and add a coverage warning describing manual enrichment. No inferred links are generated automatically.

## Portability and limits

`assets/shell.html` is a complete reusable app with no embedded session. It loads local JSON through a file input. The renderer embeds validated JSON into that same shell, escaping script terminators. Session content is only inserted through `textContent`; it is never interpreted as HTML, code, or navigation.

The v1 shell renders complete lists, and replay recomputes cumulative history. It is intended for small-to-medium traces and repository inventories; large monorepos and multi-hour traces may need filtering, pagination, and indexed state in a later version. Evidence payloads are retained in full, so artifact size grows with trace size. No secret scanning or automatic redaction is claimed.

## Automatic input discovery

`discover.py --repo /project` finds the latest session by recorded start timestamp, filtering the first `session_meta` record by cwd equal to or below the project. It never reads conversation bodies during discovery. Exact current-session selection uses `--session-id` (or `--current` with `CODEX_THREAD_ID`); previous-session selection uses `--exclude-id`. Equal latest timestamps or duplicate exact-ID matches fail with candidate paths rather than guessing. Different checkouts/worktrees are not assumed to be the same project. Set `--sessions` for a nonstandard local archive location.

## v2 decision analysis and publication

Version 2 requires `decisions`, `guidanceEdges`, and `findings`, with exact event citations. Read `decision-analysis.md` before hydrating them. `hydrate` initializes these arrays empty; the skill interprets evidence and fills them. Python and browser validators check citation excerpts and references. V1 data remains compatible.

Finish each report with `library.py publish session.json`. The user library registry records content hash, trace-prefix hash, creation time, schema version, source path, title, project, counts, and relative JSON/HTML paths. The default path is OS-specific application data, separate from skill code. Publication uses a lock, atomic JSON replacement, and atomically installed report directories; an identical report is deduplicated. A stale lock after a process crash is reported explicitly for recovery. The registry is local metadata, not telemetry.

## Expandable tool batches

Events may include `toolCalls` records with position, tool, serialized arguments/output, settlement, and outcome. Call events expose arguments with pending state and no output. Matched result events expose the corresponding results. A rejected Promise is failed; a fulfilled Promise can still contain a failed tool (nonzero exit status or `isError`). Outcomes without explicit success/failure evidence remain unknown. The shell groups parallel input slots into expandable timeline batches and allows jumping between call/result views. Existing reports without this optional field remain readable; rehydrate to add structured batch inspection.

## Automatic diagnostics
Hydration adds optional `diagnostics` (catalog version 1.0.0): detector definitions, exact-citation candidate findings, per-detector assessment counts and coverage limits. See [diagnostics](diagnostics.md). It is separate from reviewed semantic decisions/findings. Validation checks event/source IDs and exact excerpts and original trace lines.


## Frozen-peer attribution corrections

The Codex adapter 1.1.0 statically expands bounded `for (const x of [literal, ...])` loops, with literal string concatenation and simple `${x}` templates. Every body must consist entirely of supported emitted calls. Maximum 128 items per loop, four nested levels, and 1,024 expanded calls. Exact output-block pairing remains mandatory. No JavaScript is executed. Mixed blocks containing store/load, conditional execution, result-dependent variables or transformed output remain wholly opaque; no partial positional assignment is attempted.

A literal `python[3] …/scripts/run.py read SOURCE [--page N]` can establish a paginated return only when its successful output is JSON with matching source and string content. Multi-page returns are partial; page numbers are not source line numbers. Single-page complete returns require explicit page=1, pages=1 and no nextPage. This does not infer internal helper execution from a command name.

Truncation findings retain `metrics.truncationSites`: layer, envelope location, exact marker and reported original token count when present. An unparsed truncation marker at the wrapper output-block level is outer-aggregation; a marker inside a decoded command output envelope is nested-command. Direct/ambiguous envelopes remain command-or-unknown. Locations containing /decoded refer to a decoded JSON string, not a literal original-file JSON pointer. Finding citations still point to the original result event and trace line. Outer aggregation truncation does not permit assigning merged/truncated blocks back to individual requests.

The repository's fixtures/frozen-peer/cases.json preserves twelve selected frozen call/result pairs with original line numbers and hashes. Image data URLs are omitted explicitly; image-return block types remain for pairing tests. Original cohort outcomes and adjudicated image inspection are independent of improved parser coverage. Returned-source counts remain lower bounds, not complete consumed-context inventories. Image returns establish access, not understanding. No direct lexical helper call is not evidence that an invoked review command skipped that helper.


## Recorded store/load image inspection (Codex adapter 1.2.0)

A deliberately narrow producer idiom is supported: a literal `ids` array stored under `ids`, a `paths` map populated from per-ID detail outputs, then `store('details',paths); text(paths);`. The recorded emitted map must have exactly the literal IDs as keys and bounded arrays of absolute path strings. The adapter reconstructs the stored map from that emitted value, not from un-emitted command results or files on disk. A recognized producer must have one complete matching text output. This is not a general JavaScript interpreter.

Consumers can use recorded `load` values, literal slices, dictionary/array lookups, nested bounded loops, property access, shorthand path arguments and the exact literal substring exclusion predicate used in the frozen Seatcraft trace. Image exposure still requires a matching returned image block. Recorded links connect the producer result to consumer calls; exposure bases identify the producer event. Script text is never executed.

A completely known emitted prefix can be paired in order when a later statement is unsupported. It requires the completed wrapper envelope and correctly typed output blocks. The suffix remains opaque and invalidates stored state for subsequent attribution. Unknown producer code invalidates prior snapshots; unknown keys, malformed snapshots, ambiguous outputs, and missing values never get filled from the filesystem. No stored state crosses hydration runs.

The frozen Tidebook producer emits only its first detail object; its remaining store contents are not available, so its store/load loops remain unresolved. The frozen Seatcraft producer emits the complete path map. tests/test_stored.py exercises these exact producer/consumer records, literal exclusion filters, invalidation and partial-prefix handling. Image bytes are omitted from fixtures while original line hashes are preserved. Recovered image access does not establish understanding, completed review or acceptance.

## Adapter options and compound reads

Moved from SKILL.md on 2026-10-16. They apply to `fog.py hydrate`.

Optional `--trace-root /original/repository/path` maps historical absolute paths onto an extracted snapshot. `--title "Session title"` supplies the visible title. Without `--trace-root`, the recorded session cwd is used. Use `--through-line N` for a stable inclusive cutoff; the report records it. Additional `--source-root` paths are optional, repeatable, and used only for bounded returned-byte corroboration, not inventory expansion.

Inspect coverage warnings and representative events. The adapter automatically decodes supported bounded literal for-of loops, sequential and Promise.all/Promise.allSettled wrappers and pairs their outputs by input index. For compound reads, add `--source-root /allowed/context/directory` when that directory is part of the requested context system (for example the installed skills directory). Matching returned bytes can recover reads even when a later command failed. Do not create session-specific exposure scripts for supported calls. Rejected allSettled slots remain attached to their original tool and do not yield read exposures. Explicitly emitted store snapshots can support bounded image-inspection loops; see the hydration contract. Hidden stored values, dynamic JavaScript, transformed/reordered batch results, arbitrary script internals, and ambiguous results remain explicit gaps. Never label temporal adjacency as causal influence.

## Context records

Moved from SKILL.md on 2026-10-16.

Optional `contextRecords` contain sourceId, eventId, status (included/removed), and exact evidence. Populate them only from explicit context-assembly records, never from tool output alone or path mentions. The deterministic adapter recognizes a `context_assembly` payload with `sources: [{"path": "…", "status": "included"}]` (or removed), at top level or in a record payload. Other assembly formats require an evidence-backed adapter; do not infer confirmation. Empty confirmed results are valid.

## Claude compound read corroboration (adapter 1.1.0)

Literal compound Bash readers can reuse the canonical bounded source witness used
by Codex. The adapter parses supported reader operands, optionally with one leading
literal `cd PATH &&`, and attributes a read or partial return only when recorded
output matches a bounded source body or the existing conservative prefix witness.
It never executes a command from a trace. Unknown variables, heredocs, dynamic
scripts, pipelines and multiple directory changes stay outside this attribution.

The exposure basis states that the snapshot revision and the attempted directory
change are unverified. A current source cannot supply missing historical output;
only matching returned text is evidence. The allowed witness remains the supplied
repository/snapshot, with the existing one-megabyte source bound and symlink scope
check. This improves observed lower-bound coverage without proving a complete
consumed-context inventory. Failed or missing native source reads must not be
inferred from a request, source inventory or a later edit.
