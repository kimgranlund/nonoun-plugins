<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Every sdlc-lite skill that reads `$ARGUMENTS` carries a hint in one grammar, one `## Arguments` table, and one question UI style, and a `check.py` lint (rules H-1 to H-7) keeps hints and real script flags in agreement.

## Step 1: Write the standard and the argument-hint lint, observed red on the current skills
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/specs/doc-standards/AGENTS.md`
### Do
Depends on: none.

Replan state: the first attempt built all four targets below and the work is in the tree, uncommitted. Read `.sdlc/0463-skill-ui-hints/step-1/builder-L3.md` (Changes, Checks, Notes), resume from that work, and do not redo it: run every criterion below and edit only where one is red. That attempt blocked on one criterion, a plan defect this replan fixes. The guard on other FAIL lines matched `^FAIL`, which also catches the summary line `FAIL: <n> role levels, ...` that `check.py` prints whenever it is red. It now matches `^FAIL ` with a trailing space: a finding line starts `FAIL check.py:` and the summary starts `FAIL:`, so only the summary drops out. Do not change the summary `print` line in `check.py` to suit a grep.

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

## Step 2: Standardize every hint, table and question wording, then gates green
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1. This is the gates green step. At its start `check.py`, and so `check.sh`, is red with step 1's `argument hints:` findings only (78 at plan time): that is red an earlier step introduced, which this step fixes (it is not `inherited red`). `check.py` is green at the base commit. Because both are red when this step starts, the `check.py` criterion is tagged `(red)` and the `check.sh` criterion carries no tag: a `(guard)` must pass before the step, and `check.sh` runs every suite before it exits (about 615 s on an earlier recorded run), so run it once, at the end. Read the standard in `docs/specs/doc-standards/prompts.md` (section `## Skill arguments and questions`) first.

Targets: `plugins/sdlc-lite/skills/<name>/SKILL.md` for the 29 non-stub readers (every skill with the `Arguments:` line except the four `plan-*` stubs). Leave the stubs, the four reference skills, and the `sdlc-lite` router unchanged. Change wording, hints and tables only: no step, command, or decision of any skill changes (handoff Constraints).

1. Before editing, write [creates: .sdlc/0463-skill-ui-hints/hints.md] with a table `| Skill | Old hint | New hint |`, one row per reader in the form `| <name> | ... | ... |` (escape each `|` inside a hint as `\|`); the four stubs get a row whose new hint is `unchanged (stub)`. Fill the New column as each hint is settled. Add one line under the table: `report` (T-0460) and the merged `plan` (T-0467, T-0468) are on the tree and standardized here, so there is no follow-up for them.
2. Rewrite each `argument-hint` to the grammar, keeping the value YAML double-quoted. Confirm every flag against the skill body and the script it calls; a flag the script lacks is removed from the hint, never added to the script. Settled hints for the contested cases:
   - `agent`: `<agent> [--level L1|L2|L3] <instructions>`.
   - Levels: `build` `[L1|L2|L3|L4|L5] <handoff.md>`; `research` `[L1|L2|L3] <handoff.md|question>`; `verify` `[L1|L2|L3] <step-handoff.md>`. The allowed set per skill is the role's row count in the level rubric.
   - `ticket`: `new <type> <slug> | close <slug> | roadmap | check | archive | number | migrate-layout [options]` (96 characters); the optional title and every flag go in the table.
   - `fanout`: `<lane>=<ids>... <lane>@<branch>=<ids>... [options]`, every user flag of `fanout.py run` in the table.
   - `report`: `[view...] [--since T=last-report] [--last N=5] [--next N=3] [--format text|md|json] [options]`, the other flags in the table (handoff item 6 draft).
   - `plan`: `[steps|doc|goal|campaign|fanout] [L1|L2|L3] <handoff.md|goal|tickets> | compaction [options]`; keep the string `steps|doc|goal|campaign|fanout` in the file (item 57 pins it).
   - `fleet-retro`: `<repo>... [--since DATE] [--until DATE]` (its line that runs `fleet_collect.py collect` tells the reader to add both).
   - `board`: `[<task>] [--root DIR] [--sort recent|id|name] [--lanes]`; `onboard`: `[setup [--force] | check]`.
   - Free-text hints become named positionals with no spaces, for example `ask` `[<topic|task-dir>]`, `bench` `[<task>]`, `chain` `<handoff.md|goal>`, `plan-loop` `[<task>] [<interval>]`, `plan-verification` `[<goal-id|outcome>]`.
   Every settled hint above parses under the `hint_parses` function step 1 built and is at most 96 characters (plan-time probe).
   An existing `check.py` phrase pin wins over a rewording: `check.py` requires fixed strings in these files, some on the lines this step edits. Keep them in the file: `fanout` `--max-lanes`, `--stagger` and `settle <integration> --forward`; `ticket` `--dry-run`; `plan` `steps|doc|goal|campaign|fanout` and `compaction`; `ask` `## 2. Reason the options`, `If AskUserQuestion is unavailable`, `Write it in chat`; `file` and `review-traces` `at most 4 options per question`; `fleet-status` `If AskUserQuestion is unavailable`; `open-questions` `Nothing open.`; `plan-verification` `Why this plan`; `report` `Exit 2 is a refusal`. A flag that leaves a hint for `[options]` stays in the file through its table row. Run `check.py` after each batch of skills and restore any string a non-`argument hints` FAIL line names.
   H-5 rule, settled: a script flag the skill forwards from the user's arguments goes in the hint or, with `[options]` in the hint, in the table; a flag the skill sets itself or never forwards goes on `HINT_ALLOW` in `check.py` with that reason. Never give a skill a flag it does not forward today. Applied to the 15 flags H-5 reports after step 1 (evidence: each skill's own text at plan time):
   - `ticket` runs `tickets.py --root .sdlc $ARGUMENTS` as written, so every subcommand and flag on the first usage line of `tickets.py` is user-facing. `--keep-refs`, `--apply` and `--scope PATH` each get a table row (H-5 reads the first column only), and the subcommand row names `migrate-size` and `blockers` beside the seven the hint shows; the hint keeps those seven, which is what fits in 100 characters. Remove `--apply` and `--scope` from the `ticket` allowlist entry and correct its comment: only `--light-gate` and `--untracked` are prose in that usage block. `selftest` stays out of the hint and the table.
   - `fanout` passes the arguments to `fanout.py run`: `--root` gets a table row. The skill adds `--dry-run` itself for the preview run: allowlist.
   - `board`: the skill sets `--waiting` itself and passes `--task` from the `<task>` positional, and it never passes `--summary`: allowlist all three.
   - `onboard`: the skill runs `setup --dry-run` itself as the preview: allowlist `--dry-run`.
   - `fleet-retro`: `--since` and `--until` are in the hint above; the skill never passes `--days` or `--du-timeout`: allowlist both.
   - `review-traces`: the skill forwards only `--lanes-dir` and `--max`: allowlist `--out`, `--bench-dir`, `--load-series`, `--rerun-criteria`.
3. Add one `## Arguments` section to each of the 29 skills, directly after the `Arguments:` line's paragraph, with the header row `| Argument | Meaning | Default | Example |` as the next non-blank line after the heading, and one row per positional, subcommand set, and flag. Flags sit in code spans in the first column. Take meanings and defaults from the skill body and the script's usage text, not from memory; `-` for no default.
4. Question UI: 17 of the 29 skills name `AskUserQuestion` at plan time (`grep -l AskUserQuestion plugins/sdlc-lite/skills/*/SKILL.md` also lists the `sdlc-lite` router, which stays unchanged). In each of the 17, edit the question wording to the seven question rules of the standard. Change the wording of a question, never which questions are asked or when. A skill that already conforms stays as is. This is checked by reading, not by a command.
5. Regenerate: `decompose` is preloaded by the architect role (`plugins/sdlc-lite/agents/architect.md` `skills:`) and its body is inlined in `plugins/sdlc-lite/agents/architect-L1.md` and `plugins/sdlc-lite/adapters/codex/agents/sdlc-architect-l1.toml`, so run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` and `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` after editing it.
6. Gates: run `python3 plugins/sdlc-lite/scripts/prompt_lint.py` (P-2 lints the flags the new tables put in code spans), `python3 plugins/sdlc-lite/scripts/check.py`, `python3 scripts/check-packaging.py`, then `bash plugins/sdlc-lite/scripts/check.sh`, and fix any red that step 1 or this step introduced. A gate red for a reason outside both steps, checked in a detached copy of `$SDLC_BASE_SHA`, is reported as `inherited red`.

Validation scope: the 29 skills, the `check.py` allowlist, the generated Claude and Codex agent files, and the dependents named in step 1 (none found). The paths step 1 changed stay in this step's scope criterion because builders do not commit between steps.
### Acceptance criteria
- (red) `python3 plugins/sdlc-lite/scripts/check.py`
- `bash plugins/sdlc-lite/scripts/check.sh`
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
- Step 1's work is in the tree, uncommitted, and its only failing criterion was the guard on other FAIL lines: verified by `.sdlc/0463-skill-ui-hints/step-1/builder-L3.md` and by one probe call that ran every step 1 criterion on this tree (the old guard exits 1, every other span exits 0).
- The rewritten guard `grep '^FAIL '` can pass and can fail: verified by probe. It exits 0 on this tree (78 hint findings plus the summary line). The same command shape exits 1 on a fixture holding a misfired control line (`FAIL check.py: argument hints negative control not flagged for H-1: ...`) and on one holding another check's line (`FAIL check.py: plan stubs: ...`), and exits 0 on a fixture of hint findings plus the summary. At the base `check.py` prints one `ok:` line (builder result, Checks), so no line matches.
- The other step 1 guards are green on this tree with `SDLC_BASE_SHA` set to HEAD, and each shape was seen red: the stub guard on a fixture line for `plan-goal`, the scope guard with `check.py` left out of its allow-list.
- A `(red)` tag on a criterion that is green now stops the rebuild twice: `steps.py split --only` refuses it (`red_first` in `plugins/sdlc-lite/scripts/steps.py`), and the builder's `redck.py record` exits 1, which `plugins/sdlc-lite/agents/builder.md` item 11 turns into Status blocked. So step 1 carries no `(red)` tag; the five controls recorded red before the first edit are in the first attempt's `red-checkpoint.jsonl` (five lines, phase `pre-edit`, exit 1).
- Step 2's `check.py` criterion is red on this tree for the right reason: verified by probe (exit 1, 78 `argument hints:` lines, no other finding line). As a `(guard)` it would make `steps.py split --only 2` refuse (`run_guards` raises `plan defect: step 2 red guard`), which the first plan listed as a risk.
- `check.sh` does not stop at the first failure: verified at `plugins/sdlc-lite/scripts/check.sh` lines 9 to 18 (`set -uo pipefail`, each suite followed by a `fail=1` fallback). It is red while `check.py` is, so it is neither a `(guard)` nor a `(red)` here. Builder and verifier still treat a repo-wide suite as a gate (builder item 8, verifier item 4).
- Step 2's other guards exit 0 and its four other `(red)` spans exit 1 on this tree: verified by the same probe call.
- Every hint settled in step 2 parses and fits: verified by running the built `hint_parses` on each (longest 96 characters), `<repo>... [--since DATE] [--until DATE]` included.
- The H-5 triage in step 2 rests on each skill's text: `skills/ticket/SKILL.md` step 1 (arguments passed as written), `skills/fanout/SKILL.md:35` (arguments passed to `run`, `--dry-run` added by the skill), `skills/board/SKILL.md:13` and `:24`, `skills/onboard/SKILL.md:13`, `skills/fleet-retro/SKILL.md:20`, `skills/review-traces/SKILL.md:14` to `:22`. `--apply`, `--scope` and `--keep-refs` sit on the first usage line of `tickets.py`; `--light-gate` and `--untracked` appear only in its prose (probe over the 182-line block).
- 33 skills read arguments, 4 of them stubs, and 17 of the other 29 name `AskUserQuestion`: verified by a plan-time listing of every `SKILL.md`.
- The plan passes structural validation and a split dry run: verified in a scratch copy of the task folder (see Risks for the path) with `results.py validate`, `steps.py lint`, `specgate.py check`, and `steps.py split` run once with `--only 1` and once with `--only 2`. The two split runs executed both steps' guards and `(red)` spans against this tree, wrote both step handoffs, and rewrote the cited builder result to its superseded folder; the work tree was unchanged afterwards.
- Carried from the first plan (`.sdlc/0463-skill-ui-hints/planner-L2.md`, Assumptions): T-0461, T-0468, T-0460 and T-0467 are merged; the `[options]` pointer and the table reading of H-5 are the plan's reading of the handoff; the old and new hint table lives in `hints.md` in the task folder because a handoff is frozen once a role reads it; both generated architect files inline the `decompose` body.

## Risks
- Step 2 changed in this replan (two criterion tags, the `fleet-retro` hint, the H-5 triage, the `AskUserQuestion` count), so its handoff needs a fresh split too. A full `steps.py split` or `--only 1 --only 2` both work. If only step 1 is split again, step 2 builds from the first plan's text, which still builds but lacks the triage.
- `check.sh` was not run at plan time (rule 1). If it is red at the base for an unrelated reason, step 2 returns `inherited red`.
- Step 2's `(red)` controls will be recorded as `retrospective`, because step 1's uncommitted work makes the tree dirty before step 2's first edit. That writes a process deviation the verifier answers by running each `(red)` check itself. The first plan had the same property.
- The question UI rules are proven by a command only as standard text; each skill's wording is judged by the verifier reading the diff.
- The grammar may reject a hint shape a skill really needs. The step 2 builder then extends the grammar, its must-parse fixtures in `check.py`, and the standard in `prompts.md` (all in step 2's scope), not the hint.
- The phrase-pin list in step 2 comes from the first plan's scan of `check.py` string literals; a pin on another line shows up as a non-`argument hints` FAIL line.
- The `tickets.py` usage block runs 182 lines and feeds prose flags into H-5; the allowlist absorbs them, at the cost of an allowlist edit when that docstring gains a flag.
- Other lanes may add a `check.py` docstring item before this lands; criteria match the `argument hints` label, not the number.
- Scratch files are left in place (rule 15): the plan copy and split dry run under `.worktrees/tmp/0463-planner-L3/`, and one probe output at `$TMPDIR/0463-l3-check.out`, written outside that prefix. No worktree was created.
- Codex display of `argument-hint` is unverified, as the handoff states.
