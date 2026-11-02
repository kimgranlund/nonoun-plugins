# Growth

Load this before moving a vocabulary to its next stage, when renaming, merging or retiring a concept, or when you suspect an anti-pattern. The stage table with entry criteria is in SKILL.md; this file holds what each stage may produce, the gate to leave it, the change rules, anti-patterns, examples and the Stage 0 to Stage 1 walkthrough. Field semantics are in [model.md](model.md).

## Stage gates

The validator prints the stage the file's structure implies (`inferred stage N`): 1 once any `altLabel`, `hiddenLabel` or deprecated concept exists, 2 once any hierarchy link exists, 3 once two schemes are declared. A stage is reached one entry criterion at a time; evidence for Stage 2 does not let a Stage 0 file skip Stage 1's cleanup.

### Stage 0 (Seed)

- Allowed artifacts: one `vocabulary.yaml` for the whole corpus, copied from `templates/vocabulary.yaml`; one scheme; at most 15 concepts with `id`, `prefLabel`, `definition`, `scheme` and `evidence`. Nothing else.
- Not allowed: synonyms, hierarchy, a second scheme, concepts nobody has used or disputed.
- Gate to leave: the validator exits 0, every concept's `evidence` names two uses or a dispute, and `--corpus` reports no `unreferenced` concept.

### Stage 1 (Synonyms)

- Allowed artifacts: `altLabel` for a form the corpus may keep using, `hiddenLabel` for a form it must stop using, `deprecated` with `replacedBy` for a merged concept, and the rewrite of every affected doc to the `prefLabel` in the same change. A CI step that runs the validator with `--corpus` fits here.
- Gate to leave: `--corpus` reports no `retired-label-used`, and each added label has evidence of where it was seen.

### Stage 2 (Hierarchy)

- Allowed artifacts: `broader` links (or `narrower`) for the one cluster of three or more existing concepts that share an obvious parent. The parent must itself be an evidenced concept. `related` links between distinct concepts that the corpus shows readers confusing or consulting together.
- Not allowed: a parent created to hold a future child, a second level because the first one looks lonely, links for clusters that have not reached three.
- Gate to leave: no `stage-gate` or `broader-cycle` findings.

### Stage 3 (Schemes)

- Allowed artifacts: a second scheme, moving the concepts of each domain into their scheme, and a definition and `scopeNote` for each meaning of the shared label that a reader of one domain can tell apart from the other.
- Not allowed: a scheme per folder, team or document type. One vocabulary per corpus; schemes partition meanings, not files.
- Gate: no `stage-gate` finding, and each doc that uses the shared label resolves to one scheme by its location or context.

## Change rules

- Add a concept only with evidence: two places it is used (`path:line`) or one recorded dispute (a review comment, a question in onboarding, two docs that contradict). Write the evidence into `evidence` in the same change.
- Rename a concept by changing its `prefLabel` and keeping its `id`. The old label moves to `hiddenLabel` (or `altLabel` if it stays acceptable). Rewrite the corpus in the same change.
- Merge two concepts by deprecating one: `deprecated: true`, `replacedBy: <survivor>`. Keep its entry; references to its id still resolve and its labels are flagged in the corpus. Move its evidence to the survivor.
- Split a concept that has drifted into two meanings within one domain by adding a new concept with a new id for the minority meaning, then repointing the docs that use it. The original id keeps the majority meaning.
- Retire, don't delete. A concept leaves the file only if nothing ever referenced its id; a used label leaves only through `hiddenLabel`.
- Demote structure that loses its evidence. When a cluster drops below three children, remove its hierarchy links in the change that removed the child.
- Fix drift in the change that finds it. If a doc and the vocabulary disagree, change the doc or the vocabulary, never neither.
- Add an `excludes` entry only after a confusion is observed (an evaluation run, a review dispute, a misroute), at any stage, and write its statement by hand, never generated. Record the observation in `evidence` in the same change. Shape and rules: [model.md](model.md#exclusions).

## Anti-patterns

| Anti-pattern | Looks like | Caught by | Fix |
|---|---|---|---|
| Speculative taxonomy | A tree of categories drafted before the content exists ("we will need these"). | `stage-gate`, `unreferenced` | Delete the unused branches; let concepts enter one at a time with evidence. |
| Circular or restating definition | "A pager is a pager." "A change request is a request for a change." Two concepts defined by each other. | `circular-definition` (the whole-label case only) | Name the kind of thing and what distinguishes it. |
| Hierarchy deeper than evidence | Three levels where the corpus shows one cluster of three. | `stage-gate` per parent | Keep only the level whose cluster has three evidenced children. |
| Duplicate vocabularies | `docs/glossary.md`, `api/terms.yaml` and a wiki page, each partly right. | Not by the validator; search for other glossaries | Merge into the one `vocabulary.yaml`; leave the others as a link to it. |
| Glossary entries nobody references | Terms added for completeness, defined once, never used. | `unreferenced` | Drop never-used entries; deprecate entries the corpus stopped using. |

## Examples across domains

### Software codebase: Stage 2

`payment method` already has evidence, and the code and docs use `card`, `bank transfer` and `wallet` as kinds of it. Three evidenced concepts share an obvious parent, so the cluster gets `broader` links, and nothing else does.

```yaml
  - id: card
    prefLabel: card
    definition: A payment method charged through a card network at checkout.
    broader: [payment-method]
    scheme: product
    evidence: [api/payments.py:40, docs/payments.md:12]
```

`bank transfer` and `wallet` get the same `broader` line. A fourth kind proposed for next quarter waits until it appears in the corpus.

### Operations or policy corpus: Stage 3

`incident` means an outage in the ops runbooks and a possible data breach in the security policy, with legal reporting duties. Two domains use one label with different meanings, so the vocabulary gets two schemes:

```yaml
schemes:
  - id: ops
    definition: Runbooks for keeping production available.
  - id: security
    definition: Security policy and breach handling.
concepts:
  - id: ops-incident
    prefLabel: incident
    definition: An unplanned loss or degradation of service that on-call must restore.
    scopeNote: Excludes suspected data exposure, which is a security incident.
    scheme: ops
    evidence: [runbooks/incident.md:1, runbooks/escalation.md:4]
  - id: security-incident
    prefLabel: incident
    definition: A suspected or confirmed exposure of protected data that starts the breach-notification clock.
    scheme: security
    evidence: [policies/security.md:30, "audit finding 2026-07: runbook used the ops meaning"]
```

### Research or notes corpus: retiring a label

The ethics board asks the team to stop writing "subject". `subject` moves to `hiddenLabel` on `participant` (see the model example), and the same change rewrites every note that used it. Old field notes that quote the board's letter may keep the word; the warning on that line is the reviewed exception, recorded in `evidence`.

## Walkthrough: empty repo to Stage 1

An operations team keeps runbooks and policies in one repository. Each step shows the files and the validator output; commands run from the repository root with `validate_kos.py` from this skill.

### Step 1: empty repo, no vocabulary

The repository holds no docs yet. Nothing has been used or disputed, so no vocabulary is created. A starter glossary here would be a speculative taxonomy.

### Step 2: two docs and one dispute (Stage 0)

The team adds two docs:

`runbooks/deploy.md`

```markdown
# Deploy
Deploy only inside a maintenance window.
Link the approved change request in the deploy channel.
```

`policies/change-management.md`

```markdown
# Change management
Every production change needs an approved change request.
A maintenance window is booked one week ahead.
```

In review of PR 14 someone asks whether a maintenance window is the same as an outage window. A term was disputed, so the Stage 0 entry criterion holds. Both terms in the dispute's neighborhood are used in two places. Copy the template to `vocabulary.yaml` and replace its placeholder:

```diff
 schemes:
-  - id: main
-    definition: Replace with one sentence naming the corpus this vocabulary covers.
+  - id: ops
+    definition: Runbooks and policies for operating production.

 concepts:
-  - id: example-term
-    prefLabel: example term
-    definition: Replace with what this term means in this corpus, without repeating the label.
-    scheme: main
-    evidence:
-      - Replace with where the term is used or disputed, for example docs/setup.md:12.
+  - id: maintenance-window
+    prefLabel: maintenance window
+    definition: A booked period when production changes may run and users are warned of disruption.
+    scheme: ops
+    evidence:
+      - runbooks/deploy.md:2
+      - policies/change-management.md:3
+      - "review of PR 14: is a maintenance window the same as an outage window?"
+  - id: change-request
+    prefLabel: change request
+    definition: A recorded proposal to alter production that names its risk, owner and rollback, approved before work starts.
+    scheme: ops
+    evidence:
+      - runbooks/deploy.md:3
+      - policies/change-management.md:2
```

(The header comment block copied from the template is unchanged and omitted here.)

```text
$ python3 validate_kos.py vocabulary.yaml --corpus .
vocabulary.yaml: 0 error(s), 0 warning(s), inferred stage 0
```

"Outage window" is not added: it was asked about once and appears in no doc.

### Step 3: drift appears (Stage 1)

A new runbook lands:

`runbooks/db-failover.md`

```markdown
# Database failover
Open a CR before failing over, unless the primary is already down.
Run the failover inside a change window when you can.
```

The validator still passes, because it cannot know an unlisted word is a synonym. A reviewer (or an agent reading the diff with this skill active) sees `change window` used for the maintenance window and `CR` for change request. A drifted term is observed, so the Stage 1 entry criterion holds. The team decides `CR` is an accepted abbreviation and `change window` must go. First the vocabulary:

```diff
   - id: maintenance-window
     prefLabel: maintenance window
+    hiddenLabel: [change window]
     definition: A booked period when production changes may run and users are warned of disruption.
     scheme: ops
     evidence:
       - runbooks/deploy.md:2
       - policies/change-management.md:3
+      - "runbooks/db-failover.md:3 says change window (drift)"
       - "review of PR 14: is a maintenance window the same as an outage window?"
   - id: change-request
     prefLabel: change request
+    altLabel: [CR]
     definition: A recorded proposal to alter production that names its risk, owner and rollback, approved before work starts.
```

The validator now points at the drift:

```text
$ python3 validate_kos.py vocabulary.yaml --corpus .
WARNING retired-label-used maintenance-window hiddenLabel: retired label 'change window' appears at runbooks/db-failover.md:3. Fix: write 'maintenance window' instead.
vocabulary.yaml: 0 error(s), 1 warning(s), inferred stage 1
```

In the same change, rewrite the doc:

```diff
 # Database failover
 Open a CR before failing over, unless the primary is already down.
-Run the failover inside a change window when you can.
+Run the failover inside a maintenance window when you can.
```

```text
$ python3 validate_kos.py vocabulary.yaml --corpus .
vocabulary.yaml: 0 error(s), 0 warning(s), inferred stage 1
```

The change ships as one commit: `vocabulary.yaml` and `runbooks/db-failover.md` together. `CR` stays in the runbook; it is an accepted `altLabel`. Adding `--strict` to CI from here on keeps the corpus at zero retired-label uses.
