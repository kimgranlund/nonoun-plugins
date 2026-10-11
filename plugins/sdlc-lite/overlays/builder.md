## L1
### Procedure
1. Read the handoff and every file under its Read first.
2. If a criterion is tagged `(red)`, take the rule 11 red checkpoint before the first edit.
3. Change only what the step names (rule 1).
4. Run formatters and generators only on the files you changed (rule 6).
5. Run each check the criteria name, once (rule 2).
6. Before you call a gate red, run the base check of rule 8.
7. Report and stop (rule 10).

### Gap defaults
- A file the Do names does not exist: create it.
- The Do and a criterion disagree on a name: the criterion wins; say so in Notes.
- Two readings both pass the criteria: take the smaller edit and say which.
- No convention for a new test or file: copy the nearest existing one in the same folder.
- Read nothing past Read first and the files the Do names.

Stop only for the gaps rules 3 and 8 route.

## L5
### Goal
A closed step: every criterion met, nothing outside the step touched.

### KPI
The first verifier attempt passes.

### Budget
The Stop rules ceiling above, restated: about 60 tool calls or 25 minutes for the step. This level adds no budget of its own.

### Judgment
- Decide instead of enumerating: when two designs both meet the criteria, take the smaller diff and name the other in one line.
- Investigate only what a failing check points at.
- Trace contract dependents only for the contract the diff changes.
- Before the first edit, read every earlier `builder-*.md` and `verifier-*.md` in the step dir; when there are any, write the root cause of the earlier failure in one Notes line.
