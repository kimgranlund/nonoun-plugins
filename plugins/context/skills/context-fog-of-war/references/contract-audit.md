# Contract audit: a harness's guidance surfaces, read statically

Use this mode when the input is a codebase or a corpus with no trace, or to tie a trace finding to the contract that caused it. A trace shows what reached the model; this audit shows whether what the project tells the model is coherent before any live spend. In field rounds most failures were (b) conflicting or ambiguous guidance and (d) check, oracle or scenario defects, and both were visible in the files.

The audit is read-only on the audited project. It never runs, imports or fetches what it reads. Script output is a candidate list; the verdict is the agent's semantic review with file:line evidence.

## Guidance and contract surfaces

A surface is any file whose text or structure reaches the model, constrains its output, or judges it.

| Surface | Typical files | What to extract |
|---|---|---|
| Catalog and component schemas | catalog or registry JSON, `*.schema.json`, generated type files | entity names, properties, required fields |
| Component contracts and descriptors | one descriptor per component, docs beside the source | allowed props, usage rules, exemptions |
| Skills and references with their index descriptions | `SKILL.md`, skill registries, frontmatter `description` | the index line versus the body rules |
| Persona and system prompt text | persona presets, system prompts, task framing | what the user needs, and any type it names |
| Shared grammar | the prompt block every agent shares | absolute and emphasised lines |
| Few-shot exemplars and corpus records | examples, JSONL corpora, fixtures | payloads the model imitates |
| Validators and semantic checks with their repair messages | check modules, lints, repair or retry text | what each check matches and what its message asks for |
| Tool definitions | tool names, descriptions and input schemas sent with each request | what each tool says it is for and which fields it requires |
| Routing and selection metadata | selection sidecars, intent lists, `notFor` tables, trigger words | which entity is directed for which situation |
| Scenario oracles and evals | scenarios, eval cases, replays | the entity or string each oracle accepts |
| Generated artifacts and their sources | `*.gen.*`, bundled prompt assets | which source each output embeds |

## Discover them in an unfamiliar repo

1. Start from what the producer loads: the prompt assembly code, the catalog loader, the skill registry. Follow each import to a file; that file is a surface.
2. Read manifests and registries before bodies: they list surfaces and often state load modes (always framed, index-only, triggered).
3. For each generated file, find its generator (a `generate` script, a "do not edit" header, a drift test) and the sources it reads. Declare output and sources together.
4. Find the checks: validators, semantic checks, lints, and the strings they send back as repair text. Each check is a surface and its message is a prompt. Declare the repair text as kind `check` (or `repair`).
5. Find the tool definitions the producer sends (names, descriptions, input schemas) and declare them as kind `tool`. When the mapping has producer guidance (a `prompt`, `persona`, `skill` or `guide` surface with a matched file), `scan` adds an `issues` line for a missing repair surface or tool surface (one with a matched file); set `"noSurface": {"repair": "why", "tool": "why"}` to record a deliberate absence. In the field, `link` named the guidance homes only once both were listed.
6. Find the oracles: scenario files, eval cases, replay fixtures, and the assertion each makes.
7. Load modes come from a trace or the loader code, never from the file name. Without that evidence mark a surface `unknown`, and the index-only detector abstains.

`audit.py scan --root DIR` without a mapping inventories by discovery globs (schemas, catalogs, skills, prompts, agent guides, exemplars, generated files, oracles) and abstains where a detector needs mapping facts. Use that inventory to write the mapping.

## Run the script

```sh
python3 /absolute/skill/scripts/audit.py scan --root /project --mapping /outside/mapping.json \
  --out /outside/audit.json --text /outside/audit.txt
python3 /absolute/skill/scripts/audit.py link --report /outside/audit.json --excerpt "finding title or quoted excerpt"
python3 /absolute/skill/scripts/audit.py link --report /outside/audit.json --finding diag-3 --data /outside/session.json
```

`--out` must sit outside `--root`. Keep the mapping with the run's records and reuse it, as with a bundle mapping.

### Mapping contract

```json
{
  "version": 1,
  "notes": "where each load mode came from",
  "surfaces": [
    {"id": "catalog", "kind": "catalog", "paths": ["src/catalog/*.json"], "load": "full", "authority": true},
    {"id": "skills", "kind": "skill", "paths": ["skills/*.md"], "load": "index-only", "index": {"frontmatter": "description"}},
    {"id": "persona", "kind": "persona", "paths": ["personas/*.md"], "load": "full", "modalityFree": true},
    {"id": "oracles", "kind": "oracle", "paths": ["evals/*.json"], "load": "none"}
  ],
  "entities": {"fromJson": [{"path": "src/catalog/catalog.json", "pointer": "/components", "take": "keys"}],
               "names": [], "ignore": [], "referencePattern": "\\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\\b"},
  "ids": "\\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\\b",
  "topics": ["book", "price"],
  "schemas": [{"id": "Summary", "schema": "schemas/summary.schema.json#/$defs/Summary",
               "instances": [{"paths": ["examples/*.json"], "pointer": "/nodes/*", "where": {"/type": "Summary"}},
                             {"paths": ["checks/*.ts"], "snippets": "objects", "causeClass": "d"}]}],
  "generated": [{"output": "src/assets.gen.ts", "sources": ["prompts/*.md"], "embedded": true, "skipFrontmatter": true, "mtime": false}]
}
```

- `paths` are globs relative to the root (`**/` spans folders). `load` is `full`, `index-only`, `triggered`, `none` or `unknown`. `authority: true` marks the surfaces that define entities. `index` names the index line: a frontmatter key, or `linePattern` for skills embedded in code. For guidance embedded in code, `regions` (a list of `start` and `end` regexes) keeps only the lines from a start match up to the next end match, and `include` and `exclude` (one regex or a list; any match counts) keep or drop single lines (string literals, comments).
- Entities come from `fromJson` (keys or strings at a JSON Pointer, `*` matches every key) and `names`; without either, a PascalCase pattern stands in and the vocabulary-dependent detectors abstain.
- `scope` (a name or a list) says which agent or catalog a surface reaches; two scoped surfaces with no scope in common never pair as a conflict. Unscoped surfaces pair with all.
- `topics`, when set, are the only words that can join two statements into a conflict (one shared topic is enough). Without them a pair needs two shared content words covering at least 0.3 of the shorter statement's words. A ruling-out JSON entry's own negations ("no price") are dropped from its topic words. Declare topics from the situations the scenarios test.
- A schema `instances` entry reads JSON, JSONL, or text snippets (`fenced` json blocks, balanced `objects`, or `both`). `pointer` selects items, `where` filters them by pointer values.
- `generated.embedded` checks that each source line of `minLength` (default 24) or more appears in the output raw, JSON-escaped, template-escaped, or after the output's string escapes are decoded.

The report JSON holds `inventory`, `vocabulary`, an entity and id `index` (for link mode), per-detector `coverage` (assessed with an eligible count, or abstained with `nextEvidence`), `findings` (`status: candidate`, `causeClass`, file:line `evidence` with excerpts), `issues` and `limits`. Each inventory entry carries `statementLines`: the lines the detectors read after `regions`, `include` and `exclude`, plus a Markdown file's frontmatter lines. The `--text` summary prints the issues and the limits, including the conflict precision line.

## Audit rubric

One detector family per defect class. Each states the signal, its evidence rule, what the script covers, its blind spots, the cause class and the harness tag. The evidence rule for all of them is the trace rule: exact file:line excerpts on every side of the defect, quoted as they are in the file. A detector with no evidence abstains; absence is never a finding.

### 1. Cross-surface conflict
- Signal: one entity is directed on one surface and ruled out on another for the same situation, or guidance names an entity the authority surfaces never define.
- Evidence rule: both excerpts, file:line each, plus the shared situation words.
- Script: `cross-surface-conflict` pairs a directing clause (use, must, is one, or any line of an `oracle` surface) with a ruling-out clause (never, not, avoid, instead of, or a `notFor`-style JSON key) on different surfaces that share topic words; `undefined-reference` lists names matching `referencePattern` in directive lines that no authority surface defines.
- Blind spots: two different entities directed for one situation with no negation on either side; a conflict between a surface and the code that builds the prompt; synonyms for the situation; multi-line sentences.
- Precision: a ruling-out entry (a `notFor` reason or similar) that describes an adjacent situation pairs as a conflict by design; in the field run 0 of the 12 reviewed candidates (of 54, no topics) and 0 of 8 (with topics) held on the current tree, while 2 of 9 held on a pre-fix snapshot that had a real conflict, so declared topics cut the count, not the shape, and every pair must be reviewed before one is reported.
- Cause class: (b).
- Applies to: both.

### 2. Index-only rule
- Signal: a rule lives only in a body that reaches the model as its one-line index entry.
- Evidence rule: the body line, the index line, and the load mode's source (a trace showing index-only framing, or the loader).
- Script: `index-only-rule` reports directive body lines of `load: index-only` surfaces whose entities and at least half their topic words appear in no full-load statement and no index line.
- Blind spots: load modes the mapping gets wrong; a rule paraphrased elsewhere; triggered surfaces (neither full nor index-only).
- Cause class: (b). With a trace showing the body was never framed, the failing turn is also (a) exposure.
- Applies to: both.

### 3. Repair or exemplar that fails its own schema
- Signal: an exemplar, corpus record or repair snippet that the schema it teaches rejects, or repair prose asking for a field or shape the schema lacks.
- Evidence rule: the instance file:line, the schema path and pointer, and the validator error.
- Script: `schema-mismatch` validates declared instances with a JSON Schema subset (type, enum, const, required, properties, additionalProperties, items, min and max counts and lengths, pattern, minimum, maximum, local `$ref`, allOf, anyOf, oneOf, not). Other keywords are listed in `issues` and never fail an instance.
- Blind spots: repair prose with no JSON in it (read each repair message against the schema by hand: every field it asks for must exist); schemas in a non-JSON-Schema dialect until converted; instances assembled at run time.
- Cause class: (b) for exemplars and repair text the model reads; (d) for oracle fixtures (`causeClass` per instance).
- Applies to: runtime harness.

### 4. Rule coverage gap
- Signal: a rule enumerates cases and misses one the scenarios or the domain contain (an end-state rule that covers one way a game ends and not another).
- Evidence rule: the rule line, and the file:line of the uncovered case in a scenario, oracle or catalog.
- Script: none. List the cases from scenarios, oracles and domain enums, then grep each rule for each case.
- Blind spots: cases that exist only in live traffic.
- Cause class: (b) when the rule is guidance, (d) when it is a check.
- Applies to: both.

### 5. Check narrower than its rule
- Signal: a check enforces less than the rule it cites (case-sensitive where the rule is not, one spelling of an id, one surface kind).
- Evidence rule: the rule line, the check's matcher line, and one input the rule forbids that the matcher passes.
- Script: none. For each check, write the forbidden input the rule names and run it through the matcher in the project's own test runner.
- Blind spots: rules with no written statement.
- Cause class: (d).
- Applies to: both.

### 6. Oracle too generic
- Signal: an oracle accepts a base type or a substring that many outcomes satisfy, so a wrong answer passes.
- Evidence rule: the oracle line and the more specific entities that satisfy it.
- Script: `generic-oracle` reports an expected entity in an `oracle` surface that two or more declared entities extend by suffix.
- Blind spots: generic string matches, regex oracles, and oracles that check only presence.
- Cause class: (d).
- Applies to: both.

### 7. Literal-reading hazards in shared text
- Signal: a shared line a small model can read literally against its intent: emphasised absolutes, role words in capitals, "final" or "only" without scope.
- Evidence rule: the shared line and the turn or scenario where the literal reading is the wrong move.
- Script: none. Read every absolute and every capitalised word in shared grammar and ask what a literal reader does on each scenario.
- Blind spots: hazards that appear only in combination with persona text.
- Cause class: (b).
- Applies to: both.

### 8. Stale generated artifact
- Signal: a generated file older than, or diverging from, the source it embeds, so the model gets text the source no longer says.
- Evidence rule: the source line absent from the output, or both file times, plus the generator name.
- Script: `stale-generated` compares file times (low confidence: a checkout resets them) and, with `embedded: true`, reports source lines absent from the output.
- Blind spots: generators that transform text rather than embed it; the project's own drift check is the stronger evidence when one exists.
- Cause class: (b).
- Applies to: both.

### 9. Type named in modality-free text
- Signal: persona or task text that must say what the user needs names a catalog type, overriding selection.
- Evidence rule: the text line and the catalog entry it names.
- Script: `modality-leak` reports declared entity names in surfaces marked `modalityFree`, one finding per file with the first 50 naming lines as evidence; `metrics.statements` counts them all.
- Blind spots: paraphrased types ("a little card with a price"); the mapping decides which text is modality-free.
- Cause class: (b).
- Applies to: runtime harness.

## Link a trace finding to its contract

`audit.py link` takes a trace finding (its id in a v2 `session.json`, or an excerpt) and lists the inventoried surfaces whose entities, ids or exact five-word phrases appear in it, with lines, plus the audit findings on those entities or files. The phrase match reads only each surface's mapped statement lines, so code outside its `regions` or `include` never matches. `link` ranks by the finding's own words, so write the finding to quote the guidance it suspects (one line); in the field it reached the guidance homes only once the hypothesis quoted them. A miss means quote more, not that no contract is involved. Put the top surface in the why-and-fix table's file column; when two surfaces match with opposite directives, the row is a cross-surface conflict and the fix is to settle one home ([guidance authoring](learnings/guidance-authoring.md)).

## Reporting

Report per detector: coverage state, eligible count, and findings. Then the semantic review: confirm or dismiss each candidate with the excerpts, apply the rubric-only families by hand, and give each confirmed defect one cause class and the one file to change. A finding without file:line evidence is not reported.
