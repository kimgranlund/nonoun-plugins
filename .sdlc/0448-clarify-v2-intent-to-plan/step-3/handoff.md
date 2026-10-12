## Task goal
`/sdlc-lite:clarify` turns a fuzzy ask into a plan-ready intent in one pass: a handoff or plan-doc front block that `steps.py lint` and `plan_check.py` accept without a rewrite, with questions asked only when the answer changes the lane, level, cost or an irreversible step.

## Step 3: Loose ends
level: L1
### Do
- Rewrite the `Level:` line (line 10) of each of the six non-pass-through files `plugins/sdlc-lite/skills/clarify/evals/0[1-6]-*.expected.md` into the shape the rewritten `plugins/sdlc-lite/skills/clarify/SKILL.md` defines: `Level: L<n> (lane: <solo|lean|full>; cost: <one line>; reversible: <yes|no, why>)`. Keep each file's level number and meaning; map the old lane word `chain` to `full`. Change nothing else.
### Acceptance criteria
- (red) `for f in plugins/sdlc-lite/skills/clarify/evals/0[1-6]-*.expected.md; do grep -qE "^Level: L[1-4] \(lane: (solo|lean|full); cost: [^;]+; reversible: (yes|no).*\)$" "$f" || exit 1; python3 plugins/sdlc-lite/scripts/plan_check.py clarify --file "$f" >/dev/null || exit 1; done`
- (guard) `git diff --name-only -- plugins docs scripts | grep -vE "^plugins/sdlc-lite/(scripts/plan_check\.py|skills/clarify/|skills/handoff-format/SKILL\.md)" | { ! grep .; }`
