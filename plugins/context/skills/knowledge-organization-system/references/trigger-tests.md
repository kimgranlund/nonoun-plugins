# Trigger tests

Load this when you change the skill's `description` or its scope. Run each prompt in a fresh session with the plugin installed and record whether the skill activates. A change to the description passes when every row behaves as expected. Prompts span software, operations or policy, and research or notes corpora.

## Should activate

| # | Prompt | Expected outcome |
|---|---|---|
| A1 | "We call it a workspace in the API and a project in the UI. Which should the docs use?" | Activates. Checks or seeds `vocabulary.yaml`, picks one `prefLabel` with evidence from both files, records the other as `altLabel` or `hiddenLabel`, and rewrites the docs in the same change. |
| A2 | "Set up a glossary for our runbooks." | Activates. Asks for (or finds) terms that were disputed or used in two places; creates a Stage 0 file with at most 15 evidenced concepts, not a speculative list. |
| A3 | "What do we call the thing a customer files when they want their data deleted?" | Activates. Looks the concept up in the vocabulary and answers with its `prefLabel` and definition; if it is absent and disputed, proposes adding it with evidence. |
| A4 | "Half the notes say 'subject' and half say 'participant'. Clean that up." | Activates. Stage 1: keeps one `prefLabel`, moves the retired form to `hiddenLabel`, rewrites the notes, and runs the validator with `--corpus`. |
| A5 | "Add tags to these research notes so we can filter them by method." | Activates. Reuses existing concepts as tags; adds a concept only for a method used in two notes; adds no hierarchy unless three methods share a parent. |
| A6 | "Design the folder structure for our compliance docs." | Activates for the vocabulary part: folder names use `prefLabel`s of evidenced concepts; does not create one vocabulary per folder. |
| A7 | "New hires keep asking what 'SLO' means versus 'SLA'." | Activates. Onboarding confusion is evidence; seeds or updates both concepts with definitions and a `scopeNote` that separates them. |
| A8 | "Our naming conventions doc says 'customer' but the code says 'tenant'. Which is right?" | Activates. Treats it as drift: decides with the owner which label is preferred, fixes the vocabulary or the doc in the same change. |
| A9 | "Build a taxonomy of incident types for the ops wiki." | Activates. Checks the Stage 2 entry criterion first; builds hierarchy only for a cluster of three evidenced concepts and says what evidence is missing for the rest. |
| A10 | "Run the KOS validator and fix what it finds." | Activates. Runs `validate_kos.py`, fixes each error by rule, and reports warnings it left with the reason. |

## Should not activate

| # | Prompt | Expected outcome |
|---|---|---|
| N1 | "Write a friendly paragraph thanking the team for the launch." | Does not activate: casual prose. |
| N2 | "Punch up this landing page headline." | Does not activate: marketing copy. |
| N3 | "Fix the off-by-one error in the pagination loop." | Does not activate: a code change with no naming impact. |
| N4 | "Convert our ontology to OWL and load it into a triple store." | Does not activate: formal ontology and RDF work are out of scope. |
| N5 | "Rewrite this requirement so it is testable: the system should respond quickly." | Does not activate: the problem is how a statement is phrased, which belongs to `controlled-natural-language`. If the requirement uses an undefined term, that term comes back here. |
