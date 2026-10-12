## Task goal
`/sdlc-lite:clarify` turns a fuzzy ask into a plan-ready intent in one pass: a handoff or plan-doc front block that `steps.py lint` and `plan_check.py` accept without a rewrite, with questions asked only when the answer changes the lane, level, cost or an irreversible step.

## Step 1: The `plan_check.py clarify` lint and the eval cases
level: L3
### Do
Depends on: none.

Implementation targets:
- `plugins/sdlc-lite/scripts/plan_check.py`. It gets a new kind `clarify` and a `check_clarify(text)` function. The new kind is added to the argparse `kind` choices and to `run_check`. It also gets its selftest cases and updated module docstring usage and kind lines.
- The new folder `plugins/sdlc-lite/skills/clarify/evals/`.

Settled interface. The evidence is that plan_check.py already lints planned blocks by kind and prints `FAIL <rule>: <why>` and `ok: <kind> plan passes` through `report()` (lines 1-10 and 835-847).
- Usage is `plan_check.py clarify [--text T | --file F]`. The text is not unwrapped, because a clarify block holds backticks. Findings print `FAIL <rule>: <why>` lines and exit 1. Otherwise it prints `ok: clarify plan passes` and exits 0.
- Pass-through: a text with exactly one non-empty line that starts with `already scoped: ` or `follow-up: ` passes with exit 0. Every other text runs the rules below. A single non-empty line that is not a pass-through also runs them, so `--text x` fails `clarify-goal`.
- The block it reads is the clarify output, which is a task handoff:
  - a `## Goal` heading with a non-empty body;
  - a `## Intent` heading whose body holds the lines `Level: L<1-4> ...` and `Non-goals: <text>`;
  - a `Done when:` line in `## Intent`, followed by inline text or by `- ` list items. Inline text counts as one item.
- The literal labels `Done when:` and `(gap: <what>; default: <x>)` stay unchanged. `plugins/sdlc-lite/scripts/specgate.py` (lines 32 and 364) reads `(red)` lines under `Done when`. `plugins/sdlc-lite/skills/open-questions/SKILL.md` line 16 reads the `(gap: ...; default: ...)` lines. Both are dependents left untouched on purpose.
- The rules are exactly these six ids:
  1. `clarify-goal`: `## Goal` is missing or empty.
  2. `clarify-non-goals`: `## Intent` has no `Non-goals:` line with text.
  3. `clarify-level`: `## Intent` has no `Level: L1` to `L4` line.
  4. `clarify-done`: `Done when:` is missing, or an item has neither a backticked command span nor the literal `unverifiable: ` followed by a reason. An item that starts with `[owner: maintainer]` is exempt.
  5. `clarify-done-defect`: an item that does not start with `[owner: maintainer]` and does one of these:
     - reads its own step's verifier result (it matches `verifier-L[0-9]`, `verifier-*`, or `verifier result`);
     - names a fixed sha, meaning a lowercase hex token of 7 to 40 characters with at least one digit and at least one letter a-f (so `$SDLC_BASE_SHA` and ordinary words pass);
     - needs a live run that a verifier cannot do (case-insensitive `live run`, `rehearsal`, or `throwaway project`).

     The evidence is the T-0438 Done when "one more rehearsal plan runs to `plan done` with no hand step" (`.sdlc/.0438-executor-live-run-fixes/handoff.md` line 20). It had to be moved to T-0439. See also `docs/reports/2026-10-11-plan-doc-live-run.md`.
  6. `clarify-pass-through`: the first non-empty line starts with `already scoped: ` or `follow-up: `, but the text has more lines. A pass-through must be one line.
- Selftest cases:
  - a `GOOD_CLARIFY` block that passes;
  - two one-line pass-throughs that pass;
  - one mutant per rule, flagged as exactly that rule and no other. A rule that flags `GOOD_CLARIFY` is a bug, as in `plan_selftest`.
  - one positive and one negative case for the `[owner: maintainer]` exemption.

  Each case label starts with `clarify: <rule-id> `. `expect()` prints `ok: clarify: ...` or `FAIL: clarify: ...` for those labels, the same way it already prints labels that start with `plan: ` (lines 1107-1111). These mutants are the observed-red negative control per rule that the ticket asks for.

Eval cases:
- Eight pairs of files:
  - `evals/<case>.ask.md` holds the ask near-verbatim, taken from this repo's history, plus one line naming its source.
  - `evals/<case>.expected.md` holds the reference clarify output.
- The cases:
  - `01-bare-goal`.
  - `02-wrong-unit`: "build an agent" for what is a deterministic check.
  - `03-conflicting-ask`.
  - `04-unattended-gap`: has a `(gap: ...; default: ...)` delta.
  - `05-multi-step`: the expected output also carries the plan-doc Outcome block lines `Outcome:`, `Measured by:`, `Rubric:` and `Negative control:`.
  - `06-bad-done-when`: the ask's done-condition is a live rehearsal, and the expected output moves it to `[owner: maintainer]`.
  - `07-already-scoped` and `08-follow-up`: the expected output is one line starting `already scoped: ` or `follow-up: `.
- Add `evals/README.md` saying how to replay: run clarify on each `.ask.md`, then run `plan_check.py clarify --file <output>`.
- The eval files sit under `skills/**`, so check.py items 42 and 43 apply to them:
  - item 42: no link that leaves the skill folder and no `plugins/` prose path;
  - item 43: no retired size letters, such as a size word followed by S, M or L.

  Write levels as L1 to L4, and name scripts as `${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py`.

Validation scope: the criteria below and `python3 plugins/sdlc-lite/scripts/plan_check.py selftest`. Contract dependents of plan_check.py, found by `git grep -n plan_check -- plugins scripts docs/specs docs/references`:
- `scripts/check.py` item 49 (`PLAN_DOC_NEEDS`, lines 1003-1010) greps plan_check.py for the plan-doc rule ids. This step keeps them.
- `plan_done.py` imports plan_check for kind `plan`, which stays unchanged.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/plan_check.py selftest 2>&1) && for r in clarify-goal clarify-non-goals clarify-done clarify-done-defect clarify-level clarify-pass-through; do printf "%s\n" "$out" | grep -qF "ok: clarify: $r " || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/plan_check.py clarify --text x); test $? -eq 1 && printf "%s\n" "$out" | grep -qF "FAIL clarify-goal"`
- (red) `for n in 01-bare-goal 02-wrong-unit 03-conflicting-ask 04-unattended-gap 05-multi-step 06-bad-done-when 07-already-scoped 08-follow-up; do test -s plugins/sdlc-lite/skills/clarify/evals/$n.ask.md || exit 1; python3 plugins/sdlc-lite/scripts/plan_check.py clarify --file plugins/sdlc-lite/skills/clarify/evals/$n.expected.md >/dev/null || exit 1; done`
- (red) `E=plugins/sdlc-lite/skills/clarify/evals; test "$(grep -c . $E/07-already-scoped.expected.md)" -eq 1 && grep -q "^already scoped: " $E/07-already-scoped.expected.md && test "$(grep -c . $E/08-follow-up.expected.md)" -eq 1 && grep -q "^follow-up: " $E/08-follow-up.expected.md`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vE "^(plugins/sdlc-lite/(scripts/plan_check\.py|skills/clarify/|skills/handoff-format/SKILL\.md|adapters/codex/agents/)|docs/reports/[0-9-]+-clarify-v2-replay\.md$)" | { ! grep .; }`
