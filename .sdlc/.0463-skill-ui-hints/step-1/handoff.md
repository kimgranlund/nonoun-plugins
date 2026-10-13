## Task goal
Every user-invocable skill shows a consistent, complete argument hint, documents its arguments in one table, and asks its questions in one UI style, and a lint keeps hints and the real flags in agreement.

## Step 1: Write the standard and the argument-hint lint, observed red on the current skills
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/specs/doc-standards/AGENTS.md`
### Do
Depends on: none.

Replan state: the first attempt built all four targets below and the work is in the tree, uncommitted. Read `.sdlc/0463-skill-ui-hints/step-1.superseded-1/builder-L3.md` (Changes, Checks, Notes), resume from that work, and do not redo it: run every criterion below and edit only where one is red. That attempt blocked on one criterion, a plan defect this replan fixes. The guard on other FAIL lines matched `^FAIL`, which also catches the summary line `FAIL: <n> role levels, ...` that `check.py` prints whenever it is red. It now matches `^FAIL ` with a trailing space: a finding line starts `FAIL check.py:` and the summary starts `FAIL:`, so only the summary drops out. Do not change the summary `print` line in `check.py` to suit a grep.

The first plan tagged five of the criteria below `(red)`: the hint findings, the seven control literals, and the three doc greps. They carry no tag now, because the work is in the tree and a `(red)` command must fail when the builder starts. Each was recorded failing before the first edit: the `red-checkpoint.jsonl` file beside the builder result cited above holds five `pre-edit` controls with exit 1 at the base commit. They still fail in a detached copy of `$SDLC_BASE_SHA`, which holds none of this work.

Two decisions the first attempt made are ratified here. H-6 "followed by" means the next non-blank line after the `## Arguments` heading equals the header row exactly. Every real non-stub reader fails H-6 until step 2, so a control that needs a reader with no other finding mutates a clean reader built in memory from the real `handoff` skill (hint set, table appended), and the `report` controls use a flag no real skill holds.

This step leaves `python3 plugins/sdlc-lite/scripts/check.py` red on purpose: the lint must be seen failing on today's skills before step 2 fixes them (handoff, Done when: "the new rules each observed red before the change"). Edit no file under `plugins/sdlc-lite/skills/` in this step.

Targets.
1. `docs/specs/doc-standards/prompts.md`: add one section `## Skill arguments and questions` holding the hint grammar, the hint rules, the `## Arguments` table shape, and the seven question rules below. Do not add a new card: `docs/specs/doc-standards/AGENTS.md` carries a sha-stamped managed index and registry rule S-7 requires a link per card, so a new card needs a managed-block regeneration this ticket does not own.
2. `docs/specs/doc-standards/README.md`: in the `| Skill |` row only, add `check.py argument hints (H-1 to H-7)` to the Check cell. Keep the header and the Enforcement value `enforced`.
3. `plugins/sdlc-lite/AGENTS.md`: one skill-authoring bullet under `## Contracts and routing` that names `argument-hint`, the `## Arguments` table, the section in `prompts.md`, and the `check.py` item that enforces it.
4. `plugins/sdlc-lite/scripts/check.py`: a new docstring item with the next free number (item 60 in the tree) titled `Argument hints (T-0463)`, and the code before the final `for e in errors` loop, in the file's existing shape: a pure function `hints_bad(skills, usage)` over `{skill name: SKILL.md text}` and `{script path: usage text}`, a call on the real tree, then one mutant per rule (pattern: `plan_stubs_bad` and its controls at the end of the file).

Settled interface decisions.
- Reader predicate: a skill reads arguments when its SKILL.md has a line that starts with `Arguments: ` followed by the code span `$ARGUMENTS`. Evidence: all 33 argument-reading skills use that line (probe at plan time); `skills/sdlc-lite/SKILL.md:44` only defines the term for Codex, so the router is not a reader and gets no hint.
- Stubs: `plan-goal`, `plan-campaign`, `plan-doc`, `plan-fanout` (the existing `PLAN_STUB_KINDS`) are readers but exempt from H-2 to H-6. Item 58 pins each under 15 lines and the handoff says the ticket never touches the stubs.
- Reference skills: `checking-rules`, `checks-that-bite`, `handoff-format`, `level-rubric` carry no `argument-hint` (H-7).
- Finding format, exact: `check.py: argument hints: skills/<name>/SKILL.md: H-<n> <text>`. Control format, exact, one literal `errors.append` line per rule: `check.py: argument hints negative control not flagged for H-<n>: <why>`.
- Rules.
  - H-1: a reader has an `argument-hint` frontmatter line.
  - H-2: the hint parses under the grammar below.
  - H-3: the hint is at most 100 characters (the text inside the YAML quotes).
  - H-4: every `--flag` in the hint appears in the skill text below the frontmatter, and, for a skill in the script map, in that script's usage text.
  - H-5: for a skill in the script map, every `--flag` in the script's usage text is in the hint, or in the first column of the skill's `## Arguments` table when the hint holds the pointer token `[options]`, or in that skill's allowlist. The table reading comes from the handoff's own sentence: "longer flag sets go in the skill's `## Arguments` table with a pointer".
  - H-6: a non-stub reader has exactly one `## Arguments` heading, followed by a table whose header row is exactly `| Argument | Meaning | Default | Example |`.
  - H-7: a reference skill has no `argument-hint`.
  - Every rule runs on every skill it applies to, with no stop at the first finding: `ticket` today breaks H-2 (a double quote) and H-3, `report` breaks H-3 and H-4, and the criteria below expect each finding.
- Grammar (H-2). Tokens are separated by one space.

```
hint       := form (" | " form)*
form       := item (" " item)*
item       := word | level | positional | flag | group | "[options]"
group      := "[" form (" | " form)* "]" ["..."]
word       := lower ("|" lower)* ["..."]        only as the first item of a form
level      := "L" digit ("|" "L" digit)*
positional := "<" name ">" (("=" | "@") "<" name ">")* ["..."]
name       := one or more of a-z 0-9 . - |      no space
flag       := "--" lower [" " value]
value      := one token of A-Z a-z 0-9 _ , . | = -   starting with a letter or digit
lower      := a-z then a-z 0-9 -
```

  Must parse: `<agent> [--level L1|L2|L3] <instructions>`, `[L1|L2|L3|L4|L5] <handoff.md>`, `[view...] [--since T=last-report] [--last N=5] [--format text|md|json] [options]`, `<lane>=<ids>... <lane>@<branch>=<ids>... [options]`, `[setup [--force] | check]`. Must not parse: `{agent-name} [--level L1|L2|L3] {instructions}` (braces), `[L1..L5] <handoff.md>` (two dots), `[topic or task dir]` (free text: a word that is not first in its form), `<handoff.md | goal>` (space inside angle brackets), `[task` (unbalanced), and a hint holding a double quote.
- Script map (H-4, H-5), explicit in `check.py`: `ticket` to `scripts/tickets.py`, `board` to `scripts/board.py`, `report` to `scripts/report.py`, `fleet-status` to `scripts/fleet_status.py`, `fanout` to `scripts/fanout.py`, `onboard` to `scripts/onboard.py`, `review-traces` to `scripts/traces.py`, `fleet-retro` to `scripts/fleet_collect.py`. These are the skills that pass user flags to one script. `decompose` is not mapped: its `--plan` is a skill flag that `coverage_check.py` does not have. Skills that only call `dispatch.py` or `run.sh` have no parity script.
- Usage text of a script: its source lines from the first line that matches the regex `(?i)\busage:\s*($|\S+\.py)` up to, not including, the next blank line; flags are `prompt_lint.FLAG` matches (`check.py` already imports `prompt_lint` for item 53: reuse the regex, write no second one). The plan-time probe found a block in all eight scripts (`report.py` line 1499; `tickets.py` line 6, a 182-line block).
- Allowlist: one dict in `check.py`, skill to a tuple of flags, each skill entry with a one-line reason comment. A flag goes on the allowlist only when the skill does not expose it to the user: the skill sets it itself (`ticket` passes `--root`, `fleet-retro` passes `--gh`), it belongs to a subcommand the skill does not route (`fanout`: `--main`, `--require-covered`, `--ticket`), or it is internal or prose-only (`tickets.py` `--light-gate` and `--untracked`, which appear only in the prose of its usage block; `--driver`, `--no-gate-lock`, `--gate-need`, `--allow-empty-gate`, `--allow-overlap`, `--yes-many`; `fleet_status.py` `--fleet`, `--state-dir`, `--stop-line`, `--active-minutes`, `--no-gh`, `--no-write`; `traces.py` flags of `detect`, `clusters`, `context`). Do not allowlist `fleet-retro` `--since`: the handoff requires it in the hint, and it stays red until step 2. Leave the allowlist as the first attempt wrote it, its `ticket` entry with `--apply` and `--scope` included: step 2 settles every flag H-5 still reports and moves those two to the `ticket` table.
- Standard text (target 1), settled by the handoff's Intent items 1 and 4: syntax `<required>`, `[optional]`, `a|b` choice, `...` repeat, `--flag VALUE`; order subcommand or view first, then positionals, then flags; enums inline; defaults as `[--since T=last]`; at most 100 characters, with `[options]` pointing to the table for the rest; the hint shows shape only and intent stays in `description`; one level notation `[L1|L2|L3]` with the allowed set per skill; no hint on reference skills; the `## Arguments` table columns Argument, Meaning, Default, Example. Question rules for a skill that calls `AskUserQuestion`: header chip at most 12 characters; labels 1 to 5 words; one decision per question; 2 to 4 options, each with a one-line consequence; the recommendation first and marked `(Recommended)` only when evidence supports it; a `preview` when options are code, config or layout; an explicit `Write it in chat` option when prose is needed. State that Codex hint display is unverified.

Controls (one per rule, each mutating a skill text or usage text in memory): H-1 a reader with its hint line removed; H-2 each must-not-parse fixture above, and each must-parse fixture must pass; H-3 a 101-character hint; H-4 a hint flag absent from the body, and a hint flag absent from the mapped script; H-5 a usage text with one extra flag; H-6 a reader without the heading, and one with two headings; H-7 a reference skill with a hint added.

Validation scope: run `python3 plugins/sdlc-lite/scripts/check.py` and read its FAIL lines; run `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`. Dependents search at plan time: `git grep -n 'argument-hint' -- ':!plugins/sdlc-lite/skills' ':!.sdlc'` found none, so no doc, manifest, or fixture mirrors the hints. `check.sh` is not run in this step (it runs `check.py`, which is red here by design); step 2 owns it.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/check.py | grep -qF 'check.py: argument hints: '`
- `out=$(python3 plugins/sdlc-lite/scripts/check.py); for p in 'skills/agent/SKILL.md: H-2' 'skills/build/SKILL.md: H-2' 'skills/ticket/SKILL.md: H-3' 'skills/report/SKILL.md: H-4' 'skills/fleet-retro/SKILL.md: H-5' 'skills/board/SKILL.md: H-6'; do printf '%s\n' "$out" | grep -qF "check.py: argument hints: $p" || exit 1; done`
- (guard) `! python3 plugins/sdlc-lite/scripts/check.py | grep '^FAIL ' | grep -qvF 'check.py: argument hints: '`
- `for r in H-1 H-2 H-3 H-4 H-5 H-6 H-7; do grep -qF "argument hints negative control not flagged for $r" plugins/sdlc-lite/scripts/check.py || exit 1; done`
- (guard) No stub and no reference skill is flagged: `! python3 plugins/sdlc-lite/scripts/check.py | grep -qE 'argument hints: skills/(plan-goal|plan-campaign|plan-doc|plan-fanout|checking-rules|checks-that-bite|handoff-format|level-rubric)/'`
- `grep -qF '## Skill arguments and questions' docs/specs/doc-standards/prompts.md`
- `grep -qF 'argument-hint' plugins/sdlc-lite/AGENTS.md`
- `grep -E '^\| Skill \|' docs/specs/doc-standards/README.md | grep -qF 'check.py'`
- The new `check.py` docstring item names every rule H-1 to H-7 and its negative controls, and each control is a mutant that `hints_bad` runs at module level (observed by reading the diff of `plugins/sdlc-lite/scripts/check.py`).
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE 'plugins/sdlc-lite/scripts/check\.py|plugins/sdlc-lite/AGENTS\.md|docs/specs/doc-standards/(prompts|README)\.md')"`
