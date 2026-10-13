<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Every sdlc-lite skill that reads `$ARGUMENTS` carries a hint in one grammar, one `## Arguments` table, and one question UI style, and a `check.py` lint (rules H-1 to H-7) keeps hints and real script flags in agreement.

## Step 1: Write the standard and the argument-hint lint, observed red on the current skills
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/specs/doc-standards/AGENTS.md`
### Do
Depends on: none. This step leaves `python3 plugins/sdlc-lite/scripts/check.py` red on purpose: the lint must be seen failing on today's skills before step 2 fixes them (handoff, Done when: "the new rules each observed red before the change"). Edit no file under `plugins/sdlc-lite/skills/` in this step.

Targets.
1. `docs/specs/doc-standards/prompts.md`: add one section `## Skill arguments and questions` holding the hint grammar, the hint rules, the `## Arguments` table shape, and the seven question rules below. Do not add a new card: `docs/specs/doc-standards/AGENTS.md` carries a sha-stamped managed index and registry rule S-7 requires a link per card, so a new card needs a managed-block regeneration this ticket does not own.
2. `docs/specs/doc-standards/README.md`: in the `| Skill |` row only, add `check.py argument hints (H-1 to H-7)` to the Check cell. Keep the header and the Enforcement value `enforced`.
3. `plugins/sdlc-lite/AGENTS.md`: one skill-authoring bullet under `## Contracts and routing` that names `argument-hint`, the `## Arguments` table, the section in `prompts.md`, and the `check.py` item that enforces it.
4. `plugins/sdlc-lite/scripts/check.py`: a new docstring item with the next free number (60 at plan time; item 59 is the last) titled `Argument hints (T-0463)`, and the code before the final `for e in errors` loop, in the file's existing shape: a pure function `hints_bad(skills, usage)` over `{skill name: SKILL.md text}` and `{script path: usage text}`, a call on the real tree, then one mutant per rule (pattern: `plan_stubs_bad` and its controls at the end of the file).

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
- Usage text of a script: its source lines from the first line that matches the regex `(?i)\busage:\s*($|\S+\.py)` up to, not including, the next blank line; flags are `prompt_lint.FLAG` matches (`check.py` already imports `prompt_lint` for item 53: reuse the regex, write no second one). The plan-time probe found a block in all eight scripts (`report.py` line 1499; `tickets.py` line 6, a 182-line block that also pulls in `--apply`, `--light-gate`, `--scope`, `--untracked` from its prose).
- Allowlist: one dict in `check.py`, skill to a tuple of flags, each skill entry with a one-line reason comment. A flag goes on the allowlist only when the skill does not expose it to the user: the skill sets it itself (`ticket` passes `--root`, `fleet-retro` passes `--gh`), it belongs to a subcommand the skill does not route (`fanout`: `--main`, `--require-covered`, `--ticket`), or it is internal or prose-only (the four `tickets.py` prose flags above; `--driver`, `--no-gate-lock`, `--gate-need`, `--allow-empty-gate`, `--allow-overlap`, `--yes-many`; `fleet_status.py` `--fleet`, `--state-dir`, `--stop-line`, `--active-minutes`, `--no-gh`, `--no-write`; `traces.py` flags of `detect`, `clusters`, `context`). Do not allowlist `fleet-retro` `--since`: the handoff requires it in the hint, and it stays red until step 2.
- Standard text (target 1), settled by the handoff's Intent items 1 and 4: syntax `<required>`, `[optional]`, `a|b` choice, `...` repeat, `--flag VALUE`; order subcommand or view first, then positionals, then flags; enums inline; defaults as `[--since T=last]`; at most 100 characters, with `[options]` pointing to the table for the rest; the hint shows shape only and intent stays in `description`; one level notation `[L1|L2|L3]` with the allowed set per skill; no hint on reference skills; the `## Arguments` table columns Argument, Meaning, Default, Example. Question rules for a skill that calls `AskUserQuestion`: header chip at most 12 characters; labels 1 to 5 words; one decision per question; 2 to 4 options, each with a one-line consequence; the recommendation first and marked `(Recommended)` only when evidence supports it; a `preview` when options are code, config or layout; an explicit `Write it in chat` option when prose is needed. State that Codex hint display is unverified.

Controls (one per rule, each mutating a real skill text or usage text in memory): H-1 a reader with its hint line removed; H-2 each must-not-parse fixture above, and each must-parse fixture must pass; H-3 a 101-character hint; H-4 a hint flag absent from the body, and a hint flag absent from the mapped script; H-5 a usage text with one extra flag; H-6 a reader without the heading, and one with two headings; H-7 a reference skill with a hint added.

Validation scope: run `python3 plugins/sdlc-lite/scripts/check.py` and read its FAIL lines; run `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`. Dependents search at plan time: `git grep -n 'argument-hint' -- ':!plugins/sdlc-lite/skills' ':!.sdlc'` found none, so no doc, manifest, or fixture mirrors the hints. `check.sh` is not run in this step (it runs `check.py`, which is red here by design); step 2 owns it.
### Acceptance criteria
- (red) `python3 plugins/sdlc-lite/scripts/check.py | grep -qF 'check.py: argument hints: '`
- `out=$(python3 plugins/sdlc-lite/scripts/check.py); for p in 'skills/agent/SKILL.md: H-2' 'skills/build/SKILL.md: H-2' 'skills/ticket/SKILL.md: H-3' 'skills/report/SKILL.md: H-4' 'skills/fleet-retro/SKILL.md: H-5' 'skills/board/SKILL.md: H-6'; do printf '%s\n' "$out" | grep -qF "check.py: argument hints: $p" || exit 1; done`
- (guard) `! python3 plugins/sdlc-lite/scripts/check.py | grep '^FAIL' | grep -qvF 'check.py: argument hints: '`
- (red) `for r in H-1 H-2 H-3 H-4 H-5 H-6 H-7; do grep -qF "argument hints negative control not flagged for $r" plugins/sdlc-lite/scripts/check.py || exit 1; done`
- (guard) No stub and no reference skill is flagged: `! python3 plugins/sdlc-lite/scripts/check.py | grep -qE 'argument hints: skills/(plan-goal|plan-campaign|plan-doc|plan-fanout|checking-rules|checks-that-bite|handoff-format|level-rubric)/'`
- (red) `grep -qF '## Skill arguments and questions' docs/specs/doc-standards/prompts.md`
- (red) `grep -qF 'argument-hint' plugins/sdlc-lite/AGENTS.md`
- (red) `grep -E '^\| Skill \|' docs/specs/doc-standards/README.md | grep -qF 'check.py'`
- The new `check.py` docstring item names every rule H-1 to H-7 and its negative controls, and each control is a mutant that `hints_bad` runs at module level (observed by reading the diff of `plugins/sdlc-lite/scripts/check.py`).
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py --root .`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE 'plugins/sdlc-lite/scripts/check\.py|plugins/sdlc-lite/AGENTS\.md|docs/specs/doc-standards/(prompts|README)\.md')"`

## Step 2: Standardize every hint, table and question wording, then gates green
level: L3
guard timeout: 1900
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1. This is the gates green step. At its start `check.py`, and so `check.sh`, is red with step 1's `argument hints:` findings only: that is red an earlier step introduced, which this step fixes (it is not `inherited red`). Both gates are green at the base commit. Read the standard in `docs/specs/doc-standards/prompts.md` (section `## Skill arguments and questions`) first.

Targets: `plugins/sdlc-lite/skills/<name>/SKILL.md` for the 29 non-stub readers (every skill with the `Arguments:` line except the four `plan-*` stubs). Leave the stubs, the four reference skills, and the `sdlc-lite` router unchanged. Change wording, hints and tables only: no step, command, or decision of any skill changes (handoff Constraints).

1. Before editing, write [creates: .sdlc/0463-skill-ui-hints/hints.md] with a table `| Skill | Old hint | New hint |`, one row per reader in the form `| <name> | ... | ... |` (escape each `|` inside a hint as `\|`); the four stubs get a row whose new hint is `unchanged (stub)`. Fill the New column as each hint is settled. Add one line under the table: `report` (T-0460) and the merged `plan` (T-0467, T-0468) are on the tree and standardized here, so there is no follow-up for them.
2. Rewrite each `argument-hint` to the grammar, keeping the value YAML double-quoted. Confirm every flag against the skill body and the script it calls; a flag the script lacks is removed from the hint, never added to the script. Settled hints for the contested cases:
   - `agent`: `<agent> [--level L1|L2|L3] <instructions>`.
   - Levels: `build` `[L1|L2|L3|L4|L5] <handoff.md>`; `research` `[L1|L2|L3] <handoff.md|question>`; `verify` `[L1|L2|L3] <step-handoff.md>`. The allowed set per skill is the role's row count in the level rubric.
   - `ticket`: `new <type> <slug> | close <slug> | roadmap | check | archive | number | migrate-layout [options]` (96 characters); the optional title and every flag go in the table.
   - `fanout`: `<lane>=<ids>... <lane>@<branch>=<ids>... [options]`, every user flag of `fanout.py run` in the table.
   - `report`: `[view...] [--since T=last-report] [--last N=5] [--next N=3] [--format text|md|json] [options]`, the other flags in the table (handoff item 6 draft).
   - `plan`: `[steps|doc|goal|campaign|fanout] [L1|L2|L3] <handoff.md|goal|tickets> | compaction [options]`; keep the string `steps|doc|goal|campaign|fanout` in the file (item 57 pins it).
   - `fleet-retro`: `<repo>... [--since DATE]`.
   - `board`: `[<task>] [--root DIR] [--sort recent|id|name] [--lanes]`; `onboard`: `[setup [--force] | check]`.
   - Free-text hints become named positionals with no spaces, for example `ask` `[<topic|task-dir>]`, `bench` `[<task>]`, `chain` `<handoff.md|goal>`, `plan-loop` `[<task>] [<interval>]`, `plan-verification` `[<goal-id|outcome>]`.
   An existing `check.py` phrase pin wins over a rewording: `check.py` requires fixed strings in these files, some on the lines this step edits. Keep them in the file: `fanout` `--max-lanes`, `--stagger` and `settle <integration> --forward`; `ticket` `--dry-run`; `plan` `steps|doc|goal|campaign|fanout` and `compaction`; `ask` `## 2. Reason the options`, `If AskUserQuestion is unavailable`, `Write it in chat`; `file` and `review-traces` `at most 4 options per question`; `fleet-status` `If AskUserQuestion is unavailable`; `open-questions` `Nothing open.`; `plan-verification` `Why this plan`; `report` `Exit 2 is a refusal`. A flag that leaves a hint for `[options]` stays in the file through its table row. Run `check.py` after each batch of skills and restore any string a non-`argument hints` FAIL line names.
   When H-5 flags a script flag, expose it in the hint or table if a user of the skill can pass it; otherwise add it to the step 1 allowlist in `check.py` with the reason.
3. Add one `## Arguments` section to each of the 29 skills, directly after the `Arguments:` line's paragraph, with the header row `| Argument | Meaning | Default | Example |` and one row per positional, subcommand set, and flag. Flags sit in code spans in the first column. Take meanings and defaults from the skill body and the script's usage text, not from memory; `-` for no default.
4. Question UI: in each skill that names `AskUserQuestion` (18 at plan time, found with `grep -l AskUserQuestion plugins/sdlc-lite/skills/*/SKILL.md`), edit the question wording to the seven question rules of the standard. Change the wording of a question, never which questions are asked or when. A skill that already conforms stays as is. This is checked by reading, not by a command.
5. Regenerate: `decompose` is preloaded by the architect role (`plugins/sdlc-lite/agents/architect.md` `skills:`) and its body is inlined in `plugins/sdlc-lite/agents/architect-L1.md` and `plugins/sdlc-lite/adapters/codex/agents/sdlc-architect-l1.toml`, so run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` after editing it.
6. Gates: run `python3 plugins/sdlc-lite/scripts/prompt_lint.py` (P-2 lints the flags the new tables put in code spans), `python3 plugins/sdlc-lite/scripts/check.py`, `python3 scripts/check-packaging.py`, then `bash plugins/sdlc-lite/scripts/check.sh`, and fix any red that step 1 or this step introduced. `check.sh` took 615 s on record (`.sdlc/plan-reliability-docs/planner-L3.md`, step 8). A gate red for a reason outside both steps is reported as `inherited red`.

Validation scope: the 29 skills, the `check.py` allowlist, the generated Claude and Codex agent files, and the dependents named in step 1 (none found). The paths step 1 changed stay in this step's scope criterion because builders do not commit between steps.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/prompt_lint.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check && python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- (red) `for f in $(grep -l "^Arguments: " plugins/sdlc-lite/skills/*/SKILL.md | grep -vE '/plan-(goal|campaign|doc|fanout)/'); do grep -qxF "| Argument | Meaning | Default | Example |" "$f" || exit 1; done`
- (red) `! grep -lE '^argument-hint:.*(L1\.\.|\{)' plugins/sdlc-lite/skills/*/SKILL.md | grep -q .`
- (red) `grep -qE '^argument-hint:.*--since' plugins/sdlc-lite/skills/fleet-retro/SKILL.md`
- (red) `for f in $(grep -l "^Arguments: " plugins/sdlc-lite/skills/*/SKILL.md); do n=$(basename "$(dirname "$f")"); grep -qE "^\| $n \|" .sdlc/0463-skill-ui-hints/hints.md || exit 1; done`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/skills/plan-goal plugins/sdlc-lite/skills/plan-campaign plugins/sdlc-lite/skills/plan-doc plugins/sdlc-lite/skills/plan-fanout plugins/sdlc-lite/skills/checking-rules plugins/sdlc-lite/skills/checks-that-bite plugins/sdlc-lite/skills/handoff-format plugins/sdlc-lite/skills/level-rubric plugins/sdlc-lite/skills/sdlc-lite`
- In `git diff "$SDLC_BASE_SHA" -- plugins/sdlc-lite/skills`, every changed line is an `argument-hint` line, part of an `## Arguments` section, or question wording that follows the seven question rules; no step, command, or decision of a skill changed (observed by reading the diff).
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE 'plugins/sdlc-lite/skills/[a-z-]+/SKILL\.md|plugins/sdlc-lite/agents/[a-z-]+-L[0-9]\.md|plugins/sdlc-lite/adapters/codex/agents/[a-z0-9-]+\.toml|plugins/sdlc-lite/scripts/check\.py|plugins/sdlc-lite/AGENTS\.md|docs/specs/doc-standards/(prompts|README)\.md')"`

## Assumptions
- T-0461, T-0468, T-0460 and T-0467 are merged, so `report` and one `plan` skill are in scope and no follow-up is needed: verified by `git log --oneline --grep` (e24f0cde close T-0461, 07a5c289 Close T-0468, 5e974e6d Close T-0460, 33d8a945 close T-0467) and the folders `plugins/sdlc-lite/skills/report` and `plugins/sdlc-lite/skills/plan`.
- 33 skills read arguments through one line shape, 4 of them stubs, leaving 29 to standardize; the router does not read arguments: verified by `grep -l '^Arguments: ' plugins/sdlc-lite/skills/*/SKILL.md | wc -l` (33) and `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md:44`.
- The usage-block regex finds a block in all eight mapped scripts: verified by a plan-time Python probe over the map (ticket line 6, board 4, report 1499, fleet-status 6, fanout 7, onboard 4, review-traces 4, fleet-retro 4).
- Each step 1 red criterion is red today and each guard is green at HEAD: verified by one probe call (exit 1 for the seven red spans, exit 0 for `docs_check.py --root .`, `prompt_lint.py`, both `generate --check` commands, `check-packaging.py`, and both scope guards with `SDLC_BASE_SHA` set to HEAD). The step 1 guard on other FAIL lines was seen only in its clean state; its red state is any second kind of FAIL line.
- `check.py` and `check-packaging.py` exit 0 at the base: verified by running both (5.9 s and 0.05 s).
- The plan text passes structural validation: verified by `python3 plugins/sdlc-lite/scripts/steps.py lint` on a scratch copy (`steps lint: ok`).
- The `[options]` pointer token and the table reading of H-5 are this plan's reading of the handoff sentence "longer flag sets go in the skill's `## Arguments` table with a pointer"; the handoff's lint sentence alone says hint or allowlist. With a 100-character cap, `ticket`, `fanout` and `report` cannot satisfy the literal reading.
- The old and new hint table lives in `.sdlc/0463-skill-ui-hints/hints.md`, not in `handoff.md`, because a handoff is frozen once a role reads it (root `AGENTS.md`).
- Both generated architect files inline the `decompose` body: verified by `grep -c coverage_check` on `plugins/sdlc-lite/agents/architect-L1.md` and `plugins/sdlc-lite/adapters/codex/agents/sdlc-architect-l1.toml` (1 each).

## Risks
- `check.sh` was not run at plan time (rule 1); its 615 s figure is from an older record. If it is red at the base for an unrelated reason, step 2 returns `inherited red`.
- Step 1 leaves `check.py` red on purpose, so a `steps.py split --only 2` run after step 1 is built finds step 2's two gate guards red; a full `steps.py split` before any build does not.
- The phrase-pin list in step 2 comes from one plan-time scan of `check.py` string literals against hint and question lines; a pin on another line of a skill shows up as a non-`argument hints` FAIL line in `check.py`.
- The question UI rules are proven by a command only as standard text; each skill's wording is judged by the verifier reading the diff.
- The step 1 grammar may reject a hint shape a skill really needs (a quoted value, a nested repeat). The builder then extends the grammar and its must-parse fixtures in `check.py` and the standard in the same step, not the hint.
- The `tickets.py` usage block runs 182 lines and feeds prose flags into H-5; the allowlist absorbs them, at the cost of an allowlist edit when that docstring gains a flag.
- Other lanes may take docstring item 60 in `check.py` before this lands (handoff: one writer on `check.py` at a time); criteria match the `argument hints` label, not the number.
- Two plan-time probe outputs were written to `/tmp/0463-check.out` and `/tmp/0463-pkg.out`, outside the tmp prefix; they are left in place (rule 15).
- Codex display of `argument-hint` is unverified, as the handoff states.
