# Growth

Load this before moving a rule set to its next stage, when adding, promoting or retiring a pattern, or when you suspect an anti-pattern. The stage table with entry criteria is in SKILL.md; this file holds what each stage may produce, the gate to leave it, the change rules, anti-patterns, examples from three domains and the Stage 0 to Stage 1 walkthrough. The file shape and linter rules are in [patterns.md](patterns.md).

## Stage gates

Each governed doc type moves through the stages on its own. A corpus can have one doc type at Stage 2 and a second at Stage 0.

### Stage 0 (Seed)

- Entry evidence: a named failure in one doc type: a defect, a review dispute, a misread instruction, two readers acting differently on one sentence. Record it (ticket, review link, `path:line`).
- Allowed artifacts: one `rules.yaml` copied from `templates/rules.yaml`, with one doc type, 3 to 5 patterns whose shapes appear in that doc type's sentences, each with its source sentences, and a short banned-word list (the words that caused or nearly caused the failure, plus the template's). The vocabulary terms the slots need exist in `vocabulary.yaml` first.
- Not allowed: a second doc type, patterns for shapes nobody has written yet, a banned word nobody misread.
- Gate to leave: `lint_cnl.py rules.yaml vocabulary.yaml` (no docs) reports no `schema`, `unknown-concept` or `no-source` finding.

### Stage 1 (Enforce)

- Allowed artifacts: linter runs on the doc type's docs, rewrites of the violating sentences, pattern refinements driven by a real failure (a tighter slot limit, a banned word that caused a misreading, a pattern split in two), and a CI step that runs the linter on that doc type.
- Every refinement records its failure in the pattern's `sources` or in the commit message.
- Gate to leave: the doc type passes the linter with zero errors, and every remaining warning has a recorded reason.

### Stage 2 (Extend patterns)

- Entry evidence: one sentence shape the patterns reject appears 3 or more times in governed docs, and the sentences are correct statements, not violations to rewrite.
- Allowed artifacts: one new pattern per observed shape, with all observed sentences recorded in `sources`.
- Not allowed: a pattern for a shape seen once or twice, a pattern loose enough to accept the violations Stage 1 rewrote.
- Gate: the docs that motivated the pattern pass, and no earlier rewrite would now pass in its original wording unless that was the point of the change.

### Stage 3 (Extend doc types)

- Entry evidence: the current doc type passes the linter cleanly, and a second doc type shows its own Stage 0 failure.
- Allowed artifacts: a second entry under `docTypes`, starting at Stage 0 for it, with its own patterns. Shared banned words may move to the top-level `bannedWords`.
- Not allowed: governing a doc type because the first one went well, or copying one doc type's patterns to another without that type's own source sentences.

## Change rules

- **Add** a pattern only with source sentences from the governed docs (`path:line` and the sentence). A pattern written from imagination is the "patterns before examples" anti-pattern.
- **Promote** a recurring shape (Stage 2) by adding a pattern, never by widening a slot until the shape fits; a wider slot also accepts the sentences the old limit caught.
- **Retire, don't delete.** A pattern that should no longer be written gets `deprecated: true` and `replacedBy: <pattern id>`. The linter warns on each sentence that still uses it. Delete the retired pattern in the change that rewrites the last such sentence.
- **Rename** a pattern by retiring it and adding the new id; ids are never reused.
- **Terms go to the vocabulary.** A slot value that fails to resolve is a vocabulary question. Add the term there (with evidence, through `knowledge-organization-system`) or use an existing label. Never add a term, synonym or definition to `rules.yaml`.
- **Drift is a defect.** When a governed doc and the rules disagree, the change that finds it fixes the doc or the rules, never neither.

## Anti-patterns

| Anti-pattern | Looks like | Caught by | Fix |
|---|---|---|---|
| Rules that redefine terms | A banned word whose fix is a definition, a slot comment that explains a term, a doc type description that is a glossary. | Review; `unknown-concept` and `unresolved-slot` when the term is missing from the vocabulary | Move the term to `vocabulary.yaml`; make the rule point at it. |
| Patterns before examples | A full EARS set for a doc type whose docs use two shapes. | `no-source` | Delete patterns with no source sentence; add them back at Stage 2. |
| Governing every doc type at once | `docTypes` lists requirements, runbooks, ADRs and policies on day one. | Review: count doc types against recorded Stage 0 failures | Keep the one with the failure; drop the rest until each has its own. |
| Catch-all patterns | `"{anything}."`, or a text slot with no limit that covers most of the sentence. | Review: a pattern whose template has fewer literal words than slots | Split it into the specific shapes the sources show, each with literal words. |
| Style preferences disguised as rules | Banning "utilize", serial commas, sentence-case headings. | Review: ask which failure the rule prevents | Remove it. A rule must prevent a misreading or make a statement checkable. |

## Examples across domains

### Software codebase: Stage 2

Requirements for an import job use the five EARS forms. Three sentences in `requirements/import.md` (lines 4, 9, 15) read "The import job shall finish within N minutes", and reviewers keep asking whether "finish" includes retries. The shape recurs 3 times, so Stage 2 allows one pattern: `ears-latency` from [patterns.md](patterns.md), with the three sentences in `sources`. The response slot's `maxWords: 12` and the `limit` regex make "within" mean a number with a unit. A shape seen once ("Import jobs are resumed after a crash") gets no pattern; it is rewritten to the ubiquitous form.

### Operations or policy corpus: retiring a pattern

The runbooks used "Contact the {role}." for escalation. An incident review found "contact" let responders send an email to a paging rotation. The team adds `If {condition}, page the {role}.` and retires the old pattern:

```yaml
  - id: step-contact
    docType: runbook
    template: "Contact the {role}."
    slots:
      role: {type: concept, scheme: ops}
    sources: ["runbooks/db-failover.md:9: Contact the database on-call."]
    deprecated: true
    replacedBy: step-conditional
```

The linter now warns `deprecated-pattern` on each remaining "Contact the ..." step. The pattern entry is deleted in the change that rewrites the last one.

### Research or notes corpus: Stage 3

The team's findings doc passes cleanly. Their methods doc then gets a review comment: two coders read "We coded the transcripts" as "every transcript" and "a sample", and coded different sets. That is a Stage 0 failure in a second doc type, so `docTypes` gains `methods` with the one pattern its sentences show (`method` in [patterns.md](patterns.md)) and the source sentence from the review. The findings doc type's patterns are not copied over.

## Walkthrough: ungoverned doc type to Stage 1

A team keeps product requirements in `requirements/` and a vocabulary at the repository root. Commands run from the root with `lint_cnl.py` from this skill.

### Step 1: ungoverned, with a failure

`vocabulary.yaml` (maintained with `knowledge-organization-system`) already defines `auth service` (with `login service` as its `hiddenLabel`) and `account`.

`requirements/sign-in.md`:

```markdown
# Sign-in
The auth service should lock an account after repeated failures.
When a sign-in fails, the login service shall record the attempt.
If the identity provider is down, then the auth service shall show a maintenance page.
The auth service shall respond quickly.
Accounts are unlocked by support.
```

QA tested a lock after 3 failures, the build locked after 5, and the release slipped (bug 212). One doc type caused a defect, so the Stage 0 entry criterion holds. Nothing else in the repository is governed.

### Step 2: seed the rules (Stage 0)

Copy `templates/rules.yaml` to `rules.yaml`. The requirements show three shapes: ubiquitous (line 5), event-driven (line 3) and unwanted behavior (line 4). Keep those three patterns with their source sentences; drop state-driven and optional-feature, which no sentence uses. A source records the shape, so line 5 counts even though its wording will be rewritten.

```diff
 docTypes:
   - id: requirement
-    description: Replace with the doc type that caused errors or ambiguity, and who reads it.
+    description: Product requirements for the account service; read by engineers and QA.
     paths: ["requirements/**/*.md"]
@@
       system: {type: concept}
       response: {type: text, maxWords: 20}
     sources:
-      - Replace with the real sentence this pattern came from and where, for example requirements/login.md:4.
+      - "requirements/sign-in.md:5: The auth service shall respond quickly."

   - id: ears-event
@@
     sources:
-      - Replace with the real sentence this pattern came from and where.
+      - "requirements/sign-in.md:3: When a sign-in fails, the login service shall record the attempt."

-  - id: ears-state
-    docType: requirement
-    template: "While {state}, the {system} shall {response}."
-    slots:
-      state: {type: text, maxWords: 12}
-      system: {type: concept}
-      response: {type: text, maxWords: 20}
-    sources:
-      - Replace with the real sentence this pattern came from and where.
-
   - id: ears-unwanted
@@
     sources:
-      - Replace with the real sentence this pattern came from and where.
-
-  - id: ears-optional
-    docType: requirement
-    template: "Where {feature}, the {system} shall {response}."
-    slots:
-      feature: {type: text, maxWords: 12}
-      system: {type: concept}
-      response: {type: text, maxWords: 20}
-    sources:
-      - Replace with the real sentence this pattern came from and where.
+      - "requirements/sign-in.md:4: If the identity provider is down, then the auth service shall show a maintenance page."
```

(The header comment block and banned-word list copied from the template are unchanged and omitted.) The rules alone pass:

```text
$ python3 lint_cnl.py rules.yaml vocabulary.yaml
rules.yaml: 0 error(s), 0 warning(s), 0 governed doc(s), 0 ungoverned file(s)
```

### Step 3: enforce (Stage 1)

```text
$ python3 lint_cnl.py rules.yaml vocabulary.yaml requirements
ERROR banned-word requirements/sign-in.md:2: banned word 'should'. Fix: Write "shall" for a requirement; move a wish or rationale out of the requirement.
ERROR no-pattern requirements/sign-in.md:2: sentence matches no pattern: "The auth service should lock an account after repeated failures." Fix: rewrite it to one of "The {system} shall {response}." | "When {trigger}, the {system} shall {response}." | "If {condition}, then the {system} shall {response}.", or add a pattern once this shape recurs 3 times (Stage 2).
ERROR hidden-label requirements/sign-in.md:3: 'login service' is a retired label of concept 'auth-service'. Fix: write 'auth service'.
ERROR banned-word requirements/sign-in.md:5: banned word 'quickly'. Fix: State a measurable limit, for example "within 2 seconds".
ERROR no-pattern requirements/sign-in.md:6: sentence matches no pattern: "Accounts are unlocked by support." Fix: rewrite it to one of "The {system} shall {response}." | "When {trigger}, the {system} shall {response}." | "If {condition}, then the {system} shall {response}.", or add a pattern once this shape recurs 3 times (Stage 2).
rules.yaml: 5 error(s), 0 warning(s), 1 governed doc(s), 0 ungoverned file(s)
```

Line 2 is the sentence behind bug 212. `should` was only half of it: QA and the developer also read "repeated" as different counts. That is a real failure, so Stage 1 refines the rules with it:

```diff
       - word: user-friendly
         fix: State the observable behavior a reader can test.
+      - word: repeated
+        fix: State the count and the period, for example "5 times in 10 minutes".
```

Then rewrite the doc in the same change. The product owner confirms the count (5) and who unlocks an account:

```diff
 # Sign-in
-The auth service should lock an account after repeated failures.
-When a sign-in fails, the login service shall record the attempt.
+When a sign-in fails 5 times in 10 minutes, the auth service shall lock the account for 15 minutes.
+When a sign-in fails, the auth service shall record the attempt.
 If the identity provider is down, then the auth service shall show a maintenance page.
-The auth service shall respond quickly.
-Accounts are unlocked by support.
+The auth service shall return the sign-in result within 2 seconds.
+When support approves an unlock request, the auth service shall unlock the account.
```

```text
$ python3 lint_cnl.py rules.yaml vocabulary.yaml requirements
rules.yaml: 0 error(s), 0 warning(s), 1 governed doc(s), 0 ungoverned file(s)
```

The change ships as one commit: `rules.yaml` and `requirements/sign-in.md` together, with bug 212 in the message. A CI step running the linter on `requirements/` keeps the doc type at Stage 1. "Accounts are unlocked by support" was rewritten, not given a passive-voice pattern: it was seen once, and Stage 2 needs three.
