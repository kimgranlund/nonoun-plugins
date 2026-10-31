# Route evaluation

Use when designing or assessing a context-route/delivery experiment, planning a
fresh-agent comparison, or configuring/interpreting the bundled replay. Ordinary
source-backed decisions and local checks do not require this reference. For a route
review, select the evidence levels and practical criteria relevant to its mechanism.
Read the handoff section only for executable contracts, and replay sections only
when using the bundled JSON tools.

Freeze task acceptance independently of the route implementation before changing
metadata. Keep the same suite for before/after comparison. Required sources and
literal clauses are fixture oracles; they are not learned from the route output.
An independent semantic review is still needed for real-world correctness claims.

## Evidence levels

1. Static validation: identity, reachability, hashes and declared conflicts.
2. Authored replay: deterministic selection and required dependency traversal,
   checked against fixed acceptance. No model call, code execution or network.
3. Evaluator-directed runtime: an informed evaluator chooses commands and observes
   actual returns. This verifies delivery, not autonomous discovery.
4. Fresh-agent autonomous runtime: a clean agent starts from the real entry with
   only the task, discovers its own route and is checked by an independent oracle.
   Use the setup and reporting criteria below.

Only observed runtime plus independent outcome checks supports outcome improvement.
Keep these levels separate in reports; report unavailable autonomous evidence as
unknown. A same-session informed probe cannot be relabeled a fresh-agent test.

The supplied replay records available/requested/returned for loaded artifacts;
submitted and retention stay unknown. It does not simulate an assertion of real
submission. Context Fog-of-War can compare observed runtime evidence separately.

## Practical evaluation criteria

Select applicable rows; do not require every mechanism or build a new harness per
case. Add demonstrated counterexamples to maintained tests alongside passing
neighbors. The bundled replay implements its JSON profile only: document parsing,
packaging, browser loading and host discovery need separate fixtures/runtime probes.

| Boundary | Practical probe | Pass criterion |
|---|---|---|
| Task-sensitive entry | Give guidance-only and implementation briefs about the same target; add styling or composition when supported | Each reaches required governing context before action, without unrelated bodies; native host entry/skill discovery works |
| Complete delivery | Return pending documents with a successful exit; exceed default item/batch limits; clip a return | Agent follows continuations and budget overrides, recovers missing coverage and never treats exit status or a summary as completion |
| Reuse and scope | Repeat an unchanged requirement, then add a governing dependency or change a source | No redundant complete read without cause; new or stale requirements are retrieved before dependent action |
| Authority | Present conflicting current clauses and a working generated example | Agent identifies scope/owner, distinguishes behavior from intent and reports the unresolved decision without inventing precedence |
| Document semantics | Exercise inline/reference links and images, autolinks, empty destinations, HTML raw-text elements, namespaces, spaces and Unicode | Supported live references are validated and rewritten correctly; literal examples stay inert; unsupported syntax is explicit, not a silent pass |
| URL/provenance | Vary scheme case, encoding, queries, full fragments and originating directories | Equivalent URLs resolve consistently; fragments are checked whole; relocation retains source meaning and usable media URLs |
| Composition | Reference an undeclared input, invalid fragment or incomplete final object | Reject invalid edges and shapes; valid composed values retain originating link provenance |
| Portable inventory | Install/relocate without personal paths; add nested support files, escaping/cyclic links and permitted aliases | Every shipped file is covered by the same bounded inventory; local aliases work, distribution remains self-contained |
| Evidence and caches | Mutate a scanned dependency, directory membership or loaded/encoded body after capture | Prior evidence becomes stale; hashes describe consumed inputs/bytes and capture preserves loading semantics |

For fresh-agent runs, freeze briefs and independent acceptance before editing. Use
clean sessions with the normal host entry and no injected routes, expected answers
or prior conclusions. Record harness/model and environment differences. Keep
historical evaluation answers out of search scope when feasible; otherwise report
contamination and limit claims. Do not coach a failing run and count it as unchanged.

Report three outcomes separately:

- **Route correctness:** required authority, sequence and complete delivery; accept
  legitimate alternative paths.
- **Answer quality:** factual claims, authored/generated ownership, supported APIs
  and appropriate verification checked against independent evidence.
- **Retrieval overhead:** duplicate reads, irrelevant bodies, calls, bytes and clipping;
  include recovery reads. Compare savings only where correctness remains sufficient.

Use focused probes for a local change. Run broader relocation, packaging or browser
checks at an integration checkpoint or when the affected boundary requires them.
Retain failures and retries; a later pass does not establish an unproven root cause.

## Contract-to-implementation handoff

When a route ends at an implementation contract, verify one minimal consumer made
from that returned contract against the actual implementation. Reachable links,
valid IDs and passing implementation tests can coexist with stale authoring anatomy.
Keep the contract-derived specimen separate from implementation-derived fixtures;
otherwise both the code and its test may omit the same broken handoff.

For each changed route, record the advertised operation, its executable entry,
required inputs and generated output. Exercise the operation from the consumer’s
starting directory. A policy that requires an output format without a usable
producer is a procedure gap, even if its documentation links resolve. If source
ownership moved, check consumers and projections as well as the new owner; do not
repair missing links by inventing an unverified replacement authority.

If delivery is artifact-bound, mutate a transitive dependency in a disposable
fixture and confirm the old acceptance record becomes stale. Record unsupported
asset/dependency types explicitly. A hash of the entry file alone does not certify
its imported implementation. These are evaluator-directed probes, not autonomous discovery evidence.

## Replay suite v1

```json
{
  "version": 1,
  "cases": [{
    "id": "edit-menu",
    "intent": "edit-menu",
    "budget": {"reads": 4, "bytes": 4096},
    "acceptance": {
      "required": {"policy": ["Keep keyboard navigation."], "menu": ["Menu contract"]},
      "forbidden": ["billing"],
      "acceptablePaths": [["policy", "menu"]]
    }
  }]
}
```

`target` may replace `intent` for known-ID/alias entry. Required sources and their
nonempty clause arrays are mandatory. `forbidden` and `acceptablePaths` are optional.
Multiple acceptable paths can include legitimate dependency alternatives; do not
force one exact route merely for cosmetic consistency. Default budgets are eight
reads and 16 KiB; choose task-specific budgets rather than treating them as universal.
The delivery extensions below model full reads, bounded pages and projections.
Incomplete required contracts block; lower byte counts do not imply success.

The tool follows required relationships in declared order, governed_by first. It
records content bytes/read counts, initial validation bytes and subsequent source
verification bytes separately. It neither
estimates tokens nor measures live latency. It keeps acceptance failures, partial
routes and blocked reasons. It refuses to overwrite an output file.

Run using absolute script paths beneath the skill:

```sh
python3 scripts/replay.py --root CORPUS --registry REGISTRY --suite SUITE --out NEW.json
python3 scripts/replay.py compare --before BEFORE.json --after AFTER.json
```

Replay exits 0 when every case passes, 1 for acceptance failures, 2 for invalid
input or IO errors. Comparison rejects changed suite hashes and case sets; exits 1
for a correctness regression. A recovered case may cost more context because it now
loads necessary guidance. Discuss efficiency only where both runs pass.

## Regression cases

Include stale indexes, misleading summaries, duplicate IDs/aliases, missing and
inaccessible dependencies, cycles, conflicting declarations, empty/ambiguous routes,
known-source entry, budget exhaustion and previously passing neighbors. Add seeded
cases where a short route is wrong and a longer route is necessary. Do not change
labels to make a new route pass. Preserve source and registry hashes with results.

The [worked corpus](../examples/worked-corpus/README.md) demonstrates before/after
mechanics with a missing governing edge, a known-ID entry and a stable passing
neighbor. Unit tests mutate copies of these fixtures to exercise failure behavior.

## Delivery and scope extensions (suite v1, replay output v2)

Existing suites remain valid. Output v2 changes partial-delivery accounting;
comparison rejects mixed output versions. Rerun both original inputs with the same
replay version instead of comparing new byte totals to old all-or-nothing totals.

```json
{
  "id": "expanded-task",
  "stages": [{"target": "menu"}, {"target": "status"}],
  "budget": {"reads": 12, "itemBytes": 256, "batchBytes": 1024, "bytes": 2048},
  "deliveries": {"policy": {"mode": "pages", "pageBytes": 32, "maxPages": 8}},
  "acceptance": {"required": {"policy": ["Keep keyboard navigation."], "status": ["Status contract"]}}
}
```

- `stages` replaces the single target/intent and represents ordered task scope
  additions. Each stage is one combined delivery batch (including its required
  relationships and page responses). This is a deterministic batch simulation,
  not concurrent tool execution. Batch bytes reset per stage; reads and context
  bytes do not. Reused complete sources consume no additional delivery budget.
- `itemBytes` caps each response/page; `batchBytes` caps their combined return;
  `bytes` caps cumulative returns. Item and batch defaults equal `bytes` (16 KiB
  by default). Reads default to eight and count every attempted page, including
  empty budget-limited returns. Payload bytes exclude transport/JSON envelopes;
  real adapters must account for envelopes and other prompt content separately.
- `deliveries` is keyed by canonical source ID. `full` is the default. `pages`
  starts at byte zero and returns consecutive `pageBytes` chunks up to `maxPages`.
  Budget clipping stops the required route. Every receipt records source revision
  and hash, returned hash, exact byte range, page, continuation offset, bytes and
  limiting budgets. Complete coverage requires all source bytes. Multibyte splits
  count exact bytes; displayed text uses replacement characters if incomplete.
- `summary` returns only registry summary bytes and is discovery evidence. It
  cannot satisfy full-contract acceptance even if a required phrase appears there.
- `projection` selects JSON object `fields` (names) or array `records` (zero-based
  indices), exactly one. Receipts record the selection. Byte offsets describe the
  serialized projection, not the original source. Projections never claim complete
  source coverage. This conservative profile blocks required projections; an adapter
  for task-sufficient projections needs an independent field-level acceptance oracle.
- `coverage` distinguishes complete, partial, summary and projection. Returned is
  separate from submitted/retained, which remain unknown. Static metadata directives
  are checked only after the complete required source has arrived.
- Later stages traverse governing and dependency edges again and verify source
  hashes before reuse. They cannot mutate the registry mid-run; changed revisions
  need a new frozen replay input. Results list reused identities per stage.

Regression coverage includes aggregate clipping despite individually small items,
first-page-only delivery, complete pagination with unchanged acceptance, summary
impersonation, projected fields/records, added governing dependencies, cumulative
budgets across scope changes, UTF-8 clipping and passing neighboring tasks.

Keep authored, informed and fresh-agent results distinct. The
[discovery evaluation record](../templates/discovery-evaluation.md) is an optional
format when no suitable project record exists.
