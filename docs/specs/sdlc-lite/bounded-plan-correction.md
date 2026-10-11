# Bounded plan correction: a two-line fix after design and criteria are accepted

Status: design, proposed. Ticket T-0421 (design only, nothing built). Needs the maintainer's go before a build ticket is filed.

## 1. Answer in one paragraph

No, a two-line plan correction does not need a fresh planner L3 run. When the newest plan review says `replan` only because the plan names a symbol or path that does not exist, and the reviewer has found the one existing name, a script (`steps.py correct`) writes the corrected plan as a new immutable `planner-L<n>-<k>.md`. It swaps the named tokens in `### Do` text and nothing else, and refuses unless a diff check proves that. The corrected plan then takes the route a replan already takes: a plan review only when a step is at builder L4 or L5, and that review is the existing resume review (re-check the earlier findings and what changed). A correction that fails the check, or that touches anything but `### Do` and `### Read first` prose, goes the normal route unchanged: planner L3, then the review, with the two-replan cap intact. The new part is one reviewer finding tag, one `steps.py` verb, one `review` action, and a cap rule.

## 2. Sources

- Evidence: maison ticket T-0365 (`.sdlc/tickets/0365-bounded-plan-correction-route/handoff.md` in the maison ui-kit repository, read as data). UI Kit T0351 needed a full fresh planner L3 and plan-reviewer L1 because `Do` named `buildPrompt` where the export is `assemblePrompt`. The author's second report changed exactly two occurrences and kept every criterion. The reported durations include useful schema review, so none of the reported cost is claimed as saved here. Model dollar cost is unknown and the observed host was Codex native transport; Claude overhead is not inferred.
- This repo: [steps.py](../../../plugins/sdlc-lite/scripts/steps.py) (`next_action`'s review branch near line 2640, `review_notes`, `review_overrides`, `plan_facts`), [order.py](../../../plugins/sdlc-lite/scripts/order.py), [planner.md](../../../plugins/sdlc-lite/agents/planner.md), [plan-reviewer.md](../../../plugins/sdlc-lite/agents/plan-reviewer.md), [chain skill](../../../plugins/sdlc-lite/skills/chain/SKILL.md) section 3, [specgate.py](../../../plugins/sdlc-lite/scripts/specgate.py).

## 3. What exists today, and the gap

- A `notes-fix` finding (T-0364) already lets a review with only Notes-level gaps read as `pass`; `split` appends the line to the step's `### Notes`. It cannot repair a plan: the reviewer rule says "a wrong interface is a real defect, not a notes-fix", and a Notes line leaves the wrong name in `### Do` and, worse, in any criterion command that greps for it.
- A `replan` verdict sends the whole plan back to planner L3 (chain section 3). The plan reviewer must not write replacement text (reviewer rule 3).
- A replan is itself reviewed only when it holds an L4 or L5 step (`review_required`). The cap: a second plan review with Verdict `replan` in the task dir stops and asks the user (`next_action`, `len(replans) >= 2`).
- `order.py` ranks a result file by its `runs.jsonl` record, and an unrecorded file sorts before every recorded one. A plan written by a script therefore needs a `runs.jsonl` row, or it would sort as older than the plan it corrects. This is the one non-obvious build constraint.

The gap is a reviewer finding that is both a real defect (so not `notes-fix`) and fully mechanical (so not worth a model run).

## 4. What counts as a bounded correction

All of these hold, or the route is refused:

1. The newest plan-reviewer result has Verdict `replan` and every `## Findings` item is a `token-fix` line: `- step <n>: token-fix: \`<old>\` -> \`<new>\`. Evidence: <path:line where <new> is defined; command showing <old> is absent>`. Any other finding kind in the same review (a criterion, scope, ordering, level, or `plan:` finding) means the review is not bounded.
2. At most 2 distinct pairs and at most 6 changed lines in total. More is a design problem, not a typo.
3. `<old>` has no match anywhere in the tracked tree outside `.sdlc/` (`git grep -w -F`), so the plan named something that does not exist. A name that exists but is the wrong one is a semantic choice, not a rename: normal route.
4. `<new>` matches (`git grep -w -F`) in the file the Evidence cites. Name matching alone never proves behavioral equivalence, so the reviewer's tag asserts that it read the definition and that the `Do` line's use fits it; section 6 keeps the independent check on that assertion.
5. Occurrences of `<old>` in the plan sit only in `### Do` and `### Read first` text of steps the finding names. An occurrence inside `### Acceptance criteria`, or in any scope allow-list, is a criterion or scope change and refuses the route (the ticket's "no criterion or scope change").

## 5. The boundedness check is a command

`steps.py correct <task dir>` does the whole route; `steps.py correct <task dir> --check <old plan> <new plan>` runs only the proof, for a human or a verifier to rerun.

Apply (default mode):

1. Read the newest plan-reviewer result and the newest `planner-*.md` (by `order.py`). Refuse with the usual `invalid result:` text if either fails `results.structure_error`.
2. Parse the `token-fix` findings. Run rule 3 and rule 4 of section 4.
3. Build the corrected plan in a temp file beside the task dir and run the check below on the pair. On any refusal print `plan defect: correction refused: <why>; replan this step (/chain 3)`, exit 1, and leave the task dir untouched.
4. On success move it in as the next free `planner-L<n>-<k>.md` (the old plan stays byte-identical). Its first lines are the result header plus `Corrects: <old plan name> sha256=<old digest>; <new> sha256=<new digest>; review <review name>; pairs: <old>-><new> x<count>`.
5. Append a `runs.jsonl` row (`role planner`, `file`, `route correction`, `corrects`, the two digests, pairs, changed line count) so the new file ranks as newest. No model ran: the row carries no cost, and it is not a second replan of the planner.

Check (the proof of "bounded"), all exact, all must hold:

- Same step count, titles, and levels, in the same order.
- Every region outside `### Do` and `### Read first` is byte-identical: `## Goal`, every `### Acceptance criteria` block, `## Assumptions`, `## Risks`. The digest of the concatenation of those regions matches between the two files.
- The line diff (`difflib`, zero context) holds only changed lines in the allowed regions. For each changed line, `new_line == old_line.replace(old, new)` for a declared pair, with the count of replacements equal to the count of occurrences in the old line. No added or deleted lines.
- `steps.py lint` accepts the new plan, and `specgate.py check` accepts it, with the old plan's refusals not newly worse (the existing pre-review gates still run on the corrected plan).

Exit 0 prints `correct: <new plan name>`, then `reason:` and one `read:` line per file consulted, the form the other `steps.py` verbs use.

## 6. Review the correction gets

- `steps.py review` gains one action line, `correct`, printed when the newest review is a bounded `replan` (section 4 rule 1) and no correction has been recorded for it yet. The conductor runs `steps.py correct`, then `steps.py review` again.
- After the corrected plan exists, no plan-reviewer result counts after it, so today's rule applies unchanged: a plan with no L4 or L5 step is a routine plan and goes to `split`; a plan with an L4 or L5 step gets `review L1`. That review is the delta review. The plan-reviewer already re-checks "only its findings and what the plan changed since" on resume; the build adds one sentence to the reviewer's brief naming the `Corrects:` line, so the reviewer starts from the diff the script already proved.
- The independent check on the tag's equivalence claim is the corrected symbol still failing review if absent (the reviewer rereads the cited definition) and, for every ticket, the step's verifier running the unchanged criteria on the built result. A wrong equivalent breaks a criterion; it cannot pass quietly because no criterion was weakened.

## 7. What forces the normal route

Each of these refuses the correction and falls through to planner L3 with the review counted as a replan, as today:

- A finding that is not a `token-fix` line, or a mixed review.
- More than 2 pairs or 6 changed lines.
- `<old>` still exists in the tree, or `<new>` is absent from the cited file (dynamic or ambiguous equivalence).
- `<old>` appears in a criterion, a scope allow-list, `## Goal`, `## Assumptions`, or `## Risks`.
- Any step count, title, level, or order change, or any added or removed line.
- A review that is `blocked` (never bounded).
- A second correction in the same task dir (section 8).

## 8. Interaction with the replan cap

- A review consumed by a successful correction does not count toward the two-`replan`-reviews cap: it is counted out in `next_action` the way `notes-fix` reviews are (it carries a `corrects` row in `runs.jsonl` naming it). A refused correction leaves the review counted, so the user-ask rule is not weakened.
- One correction per task dir. A second `token-fix` review after a correction means the plan keeps naming things wrongly; `steps.py review` then prints `replan` and the normal route runs. This bounds the loop at one script step.
- The planner's own one-replan budget is untouched: a script run is not a planner run, and the normal replan after a refused or second correction is that budget's first use.
- Worst case total: one bounded correction, then up to two normal `replan` reviews, then the stop. No new path reaches a builder without a review that counts, and no cap is raised.

## 9. Negative control

A throwaway task dir holds a plan with a rename pair and a seeded second defect, run through `steps.py correct`:

1. Positive: a plan whose `Do` names `buildPrompt` twice, the repo defines only `assemblePrompt`, and the review has one `token-fix` finding. `correct` exits 0, the new file differs from the old on exactly the 2 lines, the old file is byte-identical, `steps.py review` then prints `split` (no L4/L5) or `review L1` (L4/L5), and `steps.py next` ranks the new file newest.
2. Negative, criterion weakened: the same review, but the plan author's file also has `buildPrompt` in an acceptance criterion. `correct` exits 1 with `correction refused` naming the criterion region, writes no file and no `runs.jsonl` row.
3. Negative, extra line: a hand-edited corrected plan with one extra edited line, run through `--check`. Exit 1, naming the line.
4. Negative, equivalence: `<old>` still defined in the tree, or `<new>` absent in the cited file. Exit 1.
5. Negative, cap: two reviews that each carry a `token-fix` finding; the second `correct` is refused and `review` prints `replan`.
6. Each negative asserts the specific refusal text and that the task dir listing and `runs.jsonl` are unchanged, so a refusal is the check's and not an argument error. Disabling the region comparison in a copy of the script must make negatives 2 and 3 pass wrongly, which shows the comparison is what refuses them.

## 10. Files a build would change

A build is one ticket of level L2, planned later; nothing here is built.

- `plugins/sdlc-lite/scripts/steps.py`: `correct` verb (apply and `--check`), the `correct` action in `review` and `next_action`, the cap exclusion, the usage text, and its selftest cases for section 9.
- `plugins/sdlc-lite/scripts/order.py`: none expected (the row uses the existing `file` field); selftest gains a script-written file ranking case.
- `plugins/sdlc-lite/agents/plan-reviewer.md`: the `token-fix` finding form beside `notes-fix`, with its Evidence rule and a line that a `Corrects:` plan is reviewed as a delta.
- `plugins/sdlc-lite/agents/planner.md`: one line that a `Corrects:` plan is script-written and is never edited by hand.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: section 3 gains the `correct` action.
- `plugins/sdlc-lite/scripts/results.py`: the `planner` schema accepts the `Corrects:` header line; `Verdict` and findings stay as they are.
- `plugins/sdlc-lite/scripts/check.py` and `docs/specs/sdlc-lite/README.md`: register the spec and run the selftest.
- Contract files other roles parse (`agents/`, `steps.py`, `results.py`) make this a non-lean ticket for any lane-script decision, so plan it as its own ticket.

## 11. Rejected alternatives

- A model author revision (maison's proposal as written): the original planner writes the immutable revision under an allowlisted diff. It keeps the cost this ticket removes (a full planner run, 6m42 reported) to apply a token swap that a script does exactly. The boundedness check in section 5 is the same check maison asks for, so the script is strictly cheaper with equal proof. It stays the fallback if a future correction class needs judgment.
- Widen `notes-fix` to wrong names: the wrong name stays in `Do` and in criteria, and the builder meets a Do that names a missing symbol. It also drops the reviewer's rule that a wrong interface is a real defect.
- Let the reviewer write the corrected plan: breaks reviewer rule 3 (never writes replacement text) and removes the independence between finding and fix.
- Auto-correct without a review of the diff when a step is L4 or L5: those steps already require a plan review for any replan; a correction does not lower that bar.
- `split --override-review` on the replan: only the user can lift a `replan`, it ignores the bad name, and it records no corrected plan.
- Count a correction as a replan for the cap: the cap exists to stop a plan that keeps failing review. A proven token swap is not that signal, and counting it would make the user-ask fire on a typo.

## 12. Acceptance criteria for the design

1. The design names the files a build changes (section 10), the boundedness check (section 5), and the rejected alternatives (section 11).
2. It states what counts as bounded (section 4), the review (section 6), what forces the normal route (section 7), the replan-cap interaction (section 8), and a negative control (section 9).
3. `python3 plugins/sdlc-lite/scripts/docs_check.py` and `python3 plugins/sdlc-lite/scripts/check.py` pass.

## 13. Open questions

- Does maison's Codex native transport apply the same `order.py` ranking, so that a script-written row sorts correctly there? The build must test it on Codex.
- Is the pair limit of 2 and the 6-line cap right? The only measured case is 2 occurrences. Raise them only on a second case.
