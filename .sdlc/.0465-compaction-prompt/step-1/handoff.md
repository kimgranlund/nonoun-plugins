## Task goal
`/sdlc-lite:plan compaction [--write-handoff|--clear] [<prose>]` authors one high signal prompt, in a fixed shape and controlled language, that the person pastes into a manual `/compact <prompt>`, linted by `plan_check.py compaction`; it never runs the compaction.

## Step 1: Build the compaction kind: lint, handoff script, skill route, reference, check item
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: none. Read `docs/planning/compaction-prompt.md` sections 3 to 7 first; it is the contract and this step cites it instead of copying it. All paths in the numbered list are under `plugins/sdlc-lite/` unless they start with a dot. Change no `AGENTS.md` or `CLAUDE.md` anywhere, and nothing under `skills/plan-loop/` or the four redirect stubs.

Settled block format (spec section 5 leaves these open; each is the reading under which every sentence of section 5 holds):
- Line 1 is the identity line, free text, for example "Continue T-0465; keep the sections below."
- A section header is a line that is exactly one of GOAL, RULES, DECISIONS, STATE, OPEN, NEXT, DROP. All seven appear once, in that order. A section with nothing to carry holds the one line "none".
- Fact lines carry no leading verb. Instruction lines start with KEEP, POINT, DROP or NEXT. A POINT line reads "POINT <locator> -> <what it answers>" and may sit in any section.
- The NEXT section holds one fact line that starts "planned: " or "intended: ". After the DROP lines, the last line of the block is the imperative "NEXT <one action>". This is how the fixed order (DROP last) and "the last line is NEXT" both hold.
- A DECISIONS line reads "<who> <date> <decision> | <reason> | <pointer>": who is "user" or "agent", date is YYYY-MM-DD, the reason has 1 to 5 words, the pointer is a turn reference or "[U]".
- A PIN line is any line under GOAL, RULES, DECISIONS, STATE, OPEN or NEXT that is not a header, not "none", and does not start with POINT or DROP.

Illustrative block (the reference's own example must pass the lint; adjust wording until it does):

```
Continue T-0465; keep the sections below.
GOAL
Build the compaction kind of the plan skill | turn 2
RULES
No write to the entry files | "never touch the entry files" turn 4
DECISIONS
user 2026-10-12 invocation is a kind of the plan skill | maintainer fixed placement | turn 6
agent 2026-10-12 handoff write stays off by default | reload unverified | [U]
STATE
Branch `fanout/wave54-f`, 0 dirty files
POINT `.sdlc/0465-compaction-prompt/handoff.md` -> goal, constraints, done-when
OPEN
Live check of the `CLAUDE.local.md` reload not run
NEXT
planned: verify step 1
DROP
DROP tool output, retry history, superseded plans, resolved errors
NEXT run /sdlc-lite:verify on step 1
```

1. `scripts/plan_check.py`: add the kind `compaction` (argparse choices, `run_check`, the usage and rule list in the docstring) as `check_compaction(text, entry=None, glossary=None)` returning `(fails, warns)` like `check_clarify`. The text is unwrapped with the existing `unwrap`. `entry` is a list of entry-file texts; `None` reads `CLAUDE.md` and `AGENTS.md` from the working directory and skips a missing file. For this kind `main` prints `lines: <N> of 60` and `pin: <M> of 40` before the FAIL, warn and ok lines, where N counts every line of the unwrapped block; the pass line is the existing `ok: compaction plan passes`. Nine FAIL rules, with these ids:
   - `compaction-words`: a line over 20 whitespace-separated words (a token that is only a pipe is not a word).
   - `compaction-verb`: a line in the DROP section that starts with neither DROP nor NEXT, or any non-header line whose first token is 3 or more upper-case letters and is not KEEP, POINT, DROP or NEXT. Two-letter tokens pass, so the spec's own fact "PR 833 merged" passes.
   - `compaction-order`: a header missing, repeated or out of order, more or fewer than one non-blank line before GOAL, or a last non-blank line that does not start with "NEXT ".
   - `compaction-lines`: over 60 lines.
   - `compaction-pin`: over 40 PIN lines.
   - `compaction-em-dash`: the character U+2014 anywhere (write it as an escape in the source; the repository bans the literal).
   - `compaction-entry-copy`: a line of 4 or more words that, after its leading closed verb is removed, equals a stripped line of an entry file with its list marker removed.
   - `compaction-decision`: a DECISIONS line that is not three pipe-separated fields with who, date, a reason of 1 to 5 words, and a non-empty pointer.
   - `compaction-approval`: a line that holds an approval word (approve, approved, approval, authorize, authorized, authorization, consent, agreed, signed off, with the s spellings) and neither a double-quoted span nor "[U]".
   One warning, `compaction-glossary`, reuses `clarify_glossary_aliases` over the text outside code spans and is skipped when the glossary file is absent.
   Selftest: a `GOOD_COMPACTION` fixture and a `compaction_selftest(expect)` in the shape of `clarify_selftest`, called from `selftest`, with `expect` also printing labels that start "compaction: ". It prints "ok: compaction: the good block passes", one "ok: compaction: <rule> does not flag GOOD_COMPACTION" line per rule, and one "ok: compaction: <rule> flags <what>" line per rule from a mutant flagged as exactly that rule, plus one case for the warning and one for a missing entry file. Write each mutant case before its rule and run the selftest to see it fail first; state in the result that each was observed red (the handoff's Done when).
2. Create `skills/plan/scripts/compaction_handoff.py` [creates: plugins/sdlc-lite/skills/plan/scripts/compaction_handoff.py], a skill-owned script like `skills/decompose/scripts/coverage_check.py` (spec section 7). Subcommands: `write --file <path>` with the body from `--text` or stdin, `clear --file <path>`, `status --file <path>`, and `selftest`. `write` exits 2 and writes nothing when neither `CLAUDECODE` nor `CLAUDE_CODE_ENTRYPOINT` is set, when `git check-ignore -q` fails for the file, or when the body has more than 8 lines; otherwise it creates the file if missing, removes the span from the exact H2 "## Compaction handoff" to the next H2 or end of file, and appends the H2 and the body at the end, touching no other byte. `clear` removes only that span and exits 0 when the file or the H2 is absent. `status` prints "none", "fresh", or "stale: written <timestamp>" from the body's "Written <YYYY-MM-DD HH:MM>" line, stale at over 24 hours. The selftest runs in a temporary git repository and prints one "ok: handoff: <case>" line per case; the six case names are the ones in the criterion below.
3. `scripts/check.sh`: add the line that runs the new selftest, in the form of the neighbouring lines (the script path under `$root/skills/plan/scripts/`), next to the `plan_check.py` line, and name it in the header comment.
4. `.gitignore` (repository root): add the line `CLAUDE.local.md`. `git check-ignore CLAUDE.local.md` prints nothing today.
5. Create `skills/plan/references/compaction.md` [creates: plugins/sdlc-lite/skills/plan/references/compaction.md], at most 90 lines. Its first fenced block is the worked example, because `plan_check.py` unwraps the first fence of a file. Content: the argument rule (flags right after the kind, the rest is prose passed through verbatim as the focus and treated as data, an instruction inside it is carried as text and never followed); the fixed command list for STATE, OPEN, NEXT and POINT (`git status`, `gh pr list`, `dispatch.py status`, `steps.py next`, the ticket and plan-doc paths, and the report record through `report.py render` when it exists); GOAL, RULES and DECISIONS from the conversation, each with a transcript pointer or "[U]"; the block format above; the loss test of spec section 6; the lint loop (`plan_check.py compaction` until it exits 0); the return (one fence, the `lines: N of 60` line taken from the lint output, then "Run: /compact <paste>"); the handoff section rules of spec section 7 through `compaction_handoff.py` (off by default, shown first and written only after the person picks `/compact`, never unattended, `status` run at the start of every run with an offer of `--clear` when stale); and the Codex line (no file write; the prompt's last line is "NEXT run /sdlc-lite:report summary"). Reach scripts through `${CLAUDE_PLUGIN_ROOT}`; `check.py` item 42 rejects a prose path that starts with "plugins/" and a link that leaves the skill folder, and `prompt_lint.py` P-2 rejects a subcommand or flag a script lacks (`dispatch.py status`, `steps.py next` and `report.py render` exist today).
6. `skills/plan/SKILL.md`, kept at most 90 lines and 7168 bytes (68 lines and 5886 bytes today), so the detail stays in the reference:
   - `argument-hint` becomes `[steps|doc|goal|campaign|fanout] [L1|L2|L3] <handoff.md | goal | tickets...> | compaction [--write-handoff|--clear] [<prose>]`. The handoff's hint text predates T-0467; this keeps the landed five-kind hint and appends the handoff's compaction clause.
   - `description`: add the kind and the trigger phrases "compaction prompt" and "before I /compact", at most 1024 characters with the key.
   - `allowed-tools`: add `Bash(git status:*)`, `Bash(gh pr list:*)`, `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/report.py:*)` and `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/skills/plan/scripts/compaction_handoff.py:*)`.
   - The `Arguments:` line names the compaction form (the file has no "## Arguments" heading; the line is its arguments record).
   - Section 0: keep the sentence with the literal `steps|doc|goal|campaign|fanout` unchanged (`check.py` item 57 pins it) and add that the first token `compaction` selects the compaction kind, which reads `references/compaction.md` and follows it alone: sections 1 to 5 and the dry run do not apply to it. Add a `compaction` row to the kind table. Extend the "Reserved first word:" line so `compaction` is reserved too (a goal that starts with it is written `goal compaction ...` or quoted). The `AskUserQuestion` still offers the five kinds.
7. Create `skills/plan/evals/06-compaction.ask.md` and `skills/plan/evals/06-compaction.expected.md` [creates: plugins/sdlc-lite/skills/plan/evals/06-compaction.expected.md] in the layout `skills/plan/evals/README.md` gives (line 1 "Kind: compaction", line 2 "Lint: " with the backticked `plan_check.py compaction`, line 3 "Questions: 0"), and add the case row to that README.
8. `skills/sdlc-lite/SKILL.md`: add one row after the "Plan by kind" row, with the second cell "plan compaction" and a first cell that says it authors one `/compact` prompt and never runs the compaction. Keep every other row.
9. `scripts/check.py`: extend item 31 (docstring text tagged "T-0465") with a function `plan_compaction_bad(texts)` in the shape of `plan_kinds_bad`. It requires in `skills/plan/SKILL.md` the phrases "compaction" and "references/compaction.md"; in the reference "plan_check.py compaction", "Run: /compact", "lines: N of 60", "## Compaction handoff", "compaction_handoff.py", "git check-ignore", "KEEP", "POINT", "DROP", "NEXT", "[U]" and "Codex"; no "harness:" in the reference; and "plan compaction" in the entry skill. Errors are prefixed "check.py: plan compaction:". Inline controls, whose message contains "plan compaction negative control not flagged": each phrase removed from its file, the reference reported empty, a harness reference added, and the entry row removed. Leave `PLAN_KINDS` and items 57 and 58 unchanged.

Contract dependents (search: `git grep -n "goal|loop|fanout|campaign"` and `git grep -n "steps|doc|goal|campaign|fanout"`, outside `.sdlc`): the `plan_check.py` docstring usage line (updated in item 1), `check.py` item 57 (the kind-list literal stays in the skill body) and the T-0467 size caps on `SKILL.md` (kept as a guard below). `docs/planning/compaction-prompt.md` is left untouched on purpose: moving a built proposal is the closing ticket's record work.

Validation scope: the criteria below. `check.sh` belongs to step 2. This step does not prove that Claude Code reloads `CLAUDE.local.md` after `/compact`; it proves the script's guards on fixtures.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/plan_check.py compaction --file plugins/sdlc-lite/skills/plan/references/compaction.md) && printf "%s\n" "$out" | grep -qE "^lines: [0-9]+ of 60$" && printf "%s\n" "$out" | grep -qE "^pin: [0-9]+ of 40$" && printf "%s\n" "$out" | grep -qxF "ok: compaction plan passes"`
- `out=$(python3 plugins/sdlc-lite/scripts/plan_check.py selftest) && printf "%s\n" "$out" | grep -qxF "ok: compaction: the good block passes" && for r in compaction-words compaction-verb compaction-order compaction-lines compaction-pin compaction-em-dash compaction-entry-copy compaction-decision compaction-approval; do printf "%s\n" "$out" | grep -q "^ok: compaction: $r flags " || exit 1; printf "%s\n" "$out" | grep -qxF "ok: compaction: $r does not flag GOOD_COMPACTION" || exit 1; done`
- `out=$(python3 plugins/sdlc-lite/scripts/plan_check.py compaction --text "DROP x"); test $? -eq 1 && printf "%s\n" "$out" | grep -q "^FAIL compaction-order: "`
- `out=$(python3 plugins/sdlc-lite/skills/plan/scripts/compaction_handoff.py selftest) && for c in "clear removes only the handoff H2" "write replaces the one handoff H2" "write refuses a file that is not gitignored" "write refuses a body over 8 lines" "write refuses outside Claude Code" "status reports a section older than 24 hours"; do printf "%s\n" "$out" | grep -qxF "ok: handoff: $c" || exit 1; done`
- `F=plugins/sdlc-lite/skills/plan/SKILL.md; grep -qF 'argument-hint: "[steps|doc|goal|campaign|fanout] [L1|L2|L3] <handoff.md | goal | tickets...> | compaction [--write-handoff|--clear] [<prose>]"' "$F" && grep -qF "references/compaction.md" "$F" && grep -qF "goal compaction" "$F" && grep -qF "compaction_handoff.py" "$F" && d=$(grep -m1 "^description:" "$F") && test "${#d}" -le 1024 && printf "%s" "$d" | grep -qF "compaction prompt"`
- `F=plugins/sdlc-lite/skills/plan/references/compaction.md; test "$(wc -l < "$F")" -le 90 || exit 1; for p in "plan_check.py compaction" "Run: /compact" "lines: N of 60" "## Compaction handoff" "compaction_handoff.py" "git check-ignore" "git status" "gh pr list" "dispatch.py status" "steps.py next" "KEEP" "POINT" "DROP" "NEXT" "[U]" "/sdlc-lite:report summary"; do grep -qF -- "$p" "$F" || exit 1; done`
- `grep -qF "| plan compaction |" plugins/sdlc-lite/skills/sdlc-lite/SKILL.md && git check-ignore -q CLAUDE.local.md && grep -qF 'compaction_handoff.py" selftest' plugins/sdlc-lite/scripts/check.sh`
- `C=plugins/sdlc-lite/scripts/check.py; grep -qF "T-0465" "$C" && grep -qF "plan compaction negative control not flagged" "$C" && grep -qF "check.py: plan compaction:" "$C" && python3 "$C"`
- `F=plugins/sdlc-lite/skills/plan; test -f "$F/evals/06-compaction.ask.md" && grep -qx "Kind: compaction" "$F/evals/06-compaction.expected.md" && grep -qF "06-compaction" "$F/evals/README.md" && python3 plugins/sdlc-lite/scripts/prompt_lint.py "$F"/SKILL.md "$F"/references/*.md "$F"/evals/*.md plugins/sdlc-lite/skills/sdlc-lite/SKILL.md && python3 scripts/check-packaging.py`
- (guard) `F=plugins/sdlc-lite/skills/plan/SKILL.md; grep -qF "steps|doc|goal|campaign|fanout" "$F" && grep -qF "Dry run (<kind>)" "$F" && grep -q "^Reserved first word:" "$F" && test "$(wc -l < "$F")" -le 90 && test "$(wc -c < "$F")" -le 7168`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" ":(exclude)plugins/sdlc-lite/skills/plan" ":(exclude)plugins/sdlc-lite/skills/sdlc-lite/SKILL.md" ":(exclude)plugins/sdlc-lite/scripts/plan_check.py" ":(exclude)plugins/sdlc-lite/scripts/check.py" ":(exclude)plugins/sdlc-lite/scripts/check.sh" ":(exclude).gitignore"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc" ":(exclude)plugins/sdlc-lite/skills/plan")"`
