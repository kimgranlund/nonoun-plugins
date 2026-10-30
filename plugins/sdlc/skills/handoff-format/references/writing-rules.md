# Writing rules for work records

A ticket's committed record is its task `handoff.md`: the brief a role reads, and the `## Outcome` that `tickets.py close` appends. Everything else a run writes stays local in the records dir. These rules keep that one file short, exact, and readable by a model with no other context.

## Controlled language

- One fact per line. Present tense for what holds, past tense only in the Outcome.
- Name things exactly: a path, a command, a ticket id (`T-0540`), a section heading. Never "the script" or "the earlier ticket".
- Use the plugin's words: ticket level (`size:` L1 to L5), lane (`solo`, `lean`, `full`, `fix`), role level, verifier verdict (`pass`, `fail`, `inherited red`). No synonyms.
- No hedging words (should, probably, ideally) in a criterion or a decision. State the rule or mark it as an open question.
- No em dashes and no bold inline labels that restate the sentence after them.
- Replace every template prompt line. `tickets.py close` refuses a handoff that still holds one, unless `--reason` is given.

## Patterns

| Pattern | Form | Where |
|---|---|---|
| Checklist | `- [ ] <one verifiable item>` | `## Acceptance criteria` |
| Criterion | `- [ ] \`<command>\` exits 0` or `<command> prints <text>`: runnable as written, from the repository root | `## Acceptance criteria`, Done-when |
| Dependency | `depends: [T-NNNN, file:<path>, cap:<name>]` in front matter; never prose like "after the other ticket" | front matter |
| Decision | `- Decided (<who>, <YYYY-MM-DD>): <decision>` | `## Context` |
| Status line | the front matter `status:`, plus `paused_reason:` or `claimed_by:` when the status needs one; never a status sentence in the body | front matter |
| Open question | `- Open: <question>? Default: <what happens without an answer>` | `## Context` |
| UI review criterion | ``grep -A1 '^## Verdict' <review result>`` prints `pass` or `pass-with-notes`: name the ui-designer `## Verdict` field, never "a review passes" | `## Acceptance criteria`, Done-when |
| Lane | recorded by `steps.py lane` in `skips.md` and on the Outcome header; never hand-written in the handoff | `skips.md`, `## Outcome` |

## Outcome

- `tickets.py close` writes it from the newest verifier result, the `T-NNNN:` commit subjects, the red-checkpoint audit and the close flags. Do not edit it by hand.
- `--changed "<one line>"` is the only free text: one sentence on what changed for a user of the work, not how.
- A deviation (a skipped verifier, an acknowledged warning, a kept stale reference) is a `- Deviation:` line, never a side file.

## Other records

- `notes.md` never states a ticket's status: it cites the ticket id, and the ticket's front matter holds the status.
- A ticket writes no dated `docs/reports/` file. Releases and retros write reports; a role result worth keeping is promoted to `docs/` before the close.
