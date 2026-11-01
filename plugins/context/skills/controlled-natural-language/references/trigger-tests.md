# Trigger tests

Load this when you change the skill's `description` or its scope. Run each prompt in a fresh session with the plugin installed and record whether the skill activates. A change to the description passes when every row behaves as expected. Prompts span software, operations or policy, and research or notes corpora.

## Should activate

| # | Prompt | Expected outcome |
|---|---|---|
| A1 | "Review these requirements before QA starts on them." | Activates. Checks for a `rules.yaml`; if the requirements doc type is governed, runs `lint_cnl.py` and rewrites each violation to a pattern; if not, reports the ambiguous sentences and asks for the failure that would justify Stage 0. |
| A2 | "Make this acceptance criterion testable: the page should load fast." | Activates. Rewrites to a pattern with a measurable slot ("The search page shall render within 2 seconds."), names the banned words it removed, and resolves "search page" against the vocabulary. |
| A3 | "Write an ADR for moving sessions to Redis." | Activates for the decision statement only: the decision log line follows the governed pattern if one exists; the ADR's context and consequences stay narrative. |
| A4 | "Turn this incident write-up into runbook steps." | Activates. One instruction per sentence, conditions first, roles resolved against the vocabulary; proposes Stage 0 for runbooks only if a recorded failure exists. |
| A5 | "Our privacy policy says requests are handled promptly. Tighten the compliance language." | Activates. Rewrites to an obligation pattern with an actor and a period; a role the vocabulary lacks goes to `knowledge-organization-system` first. |
| A6 | "Edit this system prompt so the model can't read the instructions two ways." | Activates. Applies one-reading rules (one instruction per sentence, no hedges, vocabulary labels); does not create a rule set for prompts without a recorded failure. |
| A7 | "Write a style guide for how we phrase findings in our research notes." | Activates. Proposes patterns only from sentences the notes already contain, each with sources, and a short banned-word list; refuses to write rules for shapes nobody has written. |
| A8 | "Set up CNL for our specs." | Activates. Asks which spec doc type has caused errors; seeds `rules.yaml` from the template for that one type with 3 to 5 patterns from real sentences. |
| A9 | "This SOP says 'contact the on-call as appropriate'. Half the team emails, half pages. Fix the wording." | Activates. Treats it as a Stage 1 refinement: bans "as appropriate", rewrites the step, and retires the old step pattern with `replacedBy` if one exists. |
| A10 | "Run the CNL linter on docs/requirements and fix what it finds." | Activates. Runs `lint_cnl.py`, fixes each error by rule, hands unresolved terms to the vocabulary, and reports warnings it left with the reason. |

## Should not activate

| # | Prompt | Expected outcome |
|---|---|---|
| N1 | "Write a quick reply thanking Sam for the review." | Does not activate: casual prose and one-off chat. |
| N2 | "Make our product launch blog post more exciting." | Does not activate: marketing or narrative copy. |
| N3 | "Add a comment explaining this regex." | Does not activate: code comments. |
| N4 | "Should we call it a tenant or a workspace?" | Does not activate: a naming question, which belongs to `knowledge-organization-system`. |
| N5 | "Translate the runbook into German." | Does not activate: machine translation is out of scope. |
