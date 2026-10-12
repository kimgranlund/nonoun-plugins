## Task goal
A dated report that ranks candidate ceremony cuts by measured cost and by what each step has actually caught, with a "what did it catch" count per step, and at most 5 changes marked "propose a ticket".

## Step 1: Ceremony audit report
level: L3
### Read first
- `docs/reports/AGENTS.md`
### Do
This is a read-only spike. Its output is one dated report and an optional sibling evidence folder. Depends on: none. Budget cap is $8 (handoff `budget_usd: 8`). If you hit the cap, stop, write what you have, and list the uncounted sites under `## Unverified`.

Targets:
- Create `docs/reports/2026-10-12-ceremony-audit.md`.
- Optionally create the evidence folder `docs/reports/2026-10-12-ceremony-audit/`. It holds any counting script you write plus its captured output, so the verifier can rerun the counts. Precedent: `docs/reports/solo-close-live-run/hidden.py`, `.sdlc/.0450-review-traces-solo-fails-and-blocks/sample.py`, and the "small evidence files in a sibling folder" rule in `docs/reports/AGENTS.md`.
- Change nothing else in this repo. Never write to ui-kit-maison (`/Users/kimgranlund/Projects/maison/ui-kit-maison`), agent-ui (`/Users/kimgranlund/Projects/nonoun/agent-ui`) or ultimate-tokens (`/Users/kimgranlund/Projects/nonoun/ultimate-tokens`). You may read them.
- Do not put evidence under this task's own folder in `.sdlc/`. Close renames that folder with a leading dot, so pointers into it would stop resolving.

Settled format decisions:
- The file starts with YAML front matter that contains the line `doc-type: report`. This turns on docs_check rule S-6 for the report, which resolves every relative link and every path code span (`plugins/sdlc-lite/scripts/docs_check.py`, `standards_rules`, the `S-6` branch). That check is what "pointers that resolve" means. No other report uses this front matter yet; it is the opt-in the docs_check module docstring names.
- S-6 checks a code span only when it holds a slash and ends in an extension, and it skips spans that start with `/` or hold `*`, `<`, `$` or `:`. So every repo-relative path span you write with a slash and an extension must exist. Write pointers into other repos and into `/tmp` as absolute paths.
- Cite `.sdlc/` pointers as code spans, never as Markdown links: docs_check rule B-3a warns on a docs link into `.sdlc/`, and that warning names the report, which fails criterion 3.
- Keep the report at 400 lines or fewer: docs_check rule D-11 warns above that, and that warning also names the report. Put long per-ticket tables in the evidence folder as `.md` or `.txt` files and summarize them in the report.
- The `/tmp/fanout-f5N.log` files exist on this host (`/tmp/fanout-f50.log` to `/tmp/fanout-f59.log`) but are untracked. Quote only the numbers you reproduce from them.
- Use these exact headings, one line each, in this order after a one-line result summary and a `## Method` section:
  - `## Per-site table`
  - `## First case: filer-warning close refusal`
  - `## Prompt lint signals`
  - `## Ranked changes`
  - `## Already covered`
  - `## Unverified`
- In `## Ranked changes`, mark each change proposed for a ticket with the literal marker `[propose a ticket]`, at most 5 times in the whole file. Do not use that bracketed literal anywhere else.
- Mark every inference, and every removal with no recorded catch, with `[U]`.
- No em dashes anywhere (user rule).
- `## Method` names the command or script behind every count, so a verifier can rerun it from the repository root.

Content (handoff Intent items 1 to 5):
1. First case. Cover every closed ticket since T-0431: the `.sdlc/.04NN-*` folders in this tree, plus the filers of the three other repos. Their sample is settled as every filer file in them, found with `find <root> -maxdepth 2 -name 'filer-L1*.md'` for the roots `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets` (numbered `.NNNN-*` folders), `/Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc` and `/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc` (slug-named task folders, closed ones dot-prefixed). A planner probe found 20, 12 and 8 such files; record the command and the counts you see in `## Method`. For each filer `## Warnings` entry record:
   - its kind (`red-checkpoint: retrospective`, unverified claim, flake, other)
   - whether the close was refused
   - how it was cleared (`--ack-warnings`, `--reason`, `--force`; the flags are in the `plugins/sdlc-lite/scripts/tickets.py` usage line)
   - whether it led to a fix, a reopened ticket or a later defect
   - the minutes lost

   Confirm or correct the handoff's claims ("9 of 11 filers carry a retrospective red-checkpoint", "about 6 lane stalls"). A planner probe found 11 `filer-L1*.md` files under the closed `.sdlc/.04*` folders, 10 of them containing `red-checkpoint`; that set includes T-0427 (before T-0431) and second filer files (`filer-L1-2.md`), so count per ticket, not per file. Some closed tickets (solo) have no filer, for example `.sdlc/.0456-cheap-gates-queue-behind-heavy/`. T-0428's own record is `.sdlc/.0428-close-first-doctrine/`.
2. Per-site table. One row per site, with columns for cost (minutes and dollars), defects caught (count plus result-file pointers), and manual acks. The sites are:
   - plan-reviewer by level
   - filer on solo and on chain tickets
   - a second verifier round
   - the full chain for L3
   - `inherited red` stops
   - gate-lock timeouts reported as red
   - replans
   - questions that did not change the output
   - any skill or agent rule that tells a role to re-verify or re-run a green result
3. Prompt lint. Run `python3 plugins/sdlc-lite/scripts/prompt_lint.py` (it defaults to `agents/*.md`, `skills/*/SKILL.md` and `overlays/*.md`) and report its P-6 info counts against `docs/reports/2026-10-11-agent-prompt-lint-baseline.md`. prompt_lint has no loop, verify or re-run counter, so count those words with these settled patterns over the same three globs under `plugins/sdlc-lite/`, case-insensitive, one `grep -oiE` per family piped to `wc -l`: loop is `\bloops?\b`, verify is `\bre-?verif[a-z]*`, re-run is `\bre-?run[a-z]*`. A planner probe got 36, 9 and 55 on the current tree. These counts are informational only.
4. Cost sources:
   - each ticket's `runs.jsonl`
   - `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --since <date>` (method precedent: `docs/reports/2026-10-11-solo-fails-and-blocks.md`, which also notes that minutes and dollars outside sdlc-lite are a floor)
   - `*.attempt.json` records
   - prior cost reports named in the handoff Context: `docs/reports/2026-10-11-solo-campaign-baseline.md`, `docs/reports/2026-10-09-l4-full-chain-cost-replay.md`, `docs/reports/2026-10-10-verifier-minutes.md`

   Each candidate states its cost, its catches with pointers, the proposed change, the measure that must move, and its quality guard (K-005 first-pass rate, `docs/kpi/005-solo-first-pass-rate.md`, and rework after close). Keep every check that has at least one real catch.
5. Rank the candidates. In `## Already covered`, name each of T-0428, T-0456, T-0459, T-0446, T-0445, T-0457, T-0461 and T-0462 and say what it covers.

Settled evidence (planner probes on the current tree and on a scratch copy of `docs/`):
- `docs_check.py` exits 0 on the current tree with 0 errors and 26 warnings, none naming the new report, so the bar is "no finding names the new report".
- On a scratch copy, a report with `doc-type: report` front matter and valid spans passed with no finding naming it. The same report got an S-6 error when one path span named a ticket folder that does not exist, a B-3a warning when it linked into `.sdlc/` with a Markdown link, and a D-11 warning at 408 lines. A `.py` and a `.txt` file in the sibling evidence folder drew no finding.

Validation scope: the criteria below, plus trailing-whitespace hygiene on the new files (`git diff --check` does not see untracked files, so check them by eye or with a grep for trailing blanks). This is a docs-only change, so check.sh and the role suites are not in scope (root `AGENTS.md`, validation table); this one step is the gates step, and its gate is docs_check. The independent verifier reproduces a sample of the counts from `## Method`.
### Acceptance criteria
- (red) `test -f docs/reports/2026-10-12-ceremony-audit.md`
- `head -5 docs/reports/2026-10-12-ceremony-audit.md | grep -qx 'doc-type: report'`
- `test -f docs/reports/2026-10-12-ceremony-audit.md && out=$(python3 plugins/sdlc-lite/scripts/docs_check.py) && ! printf '%s\n' "$out" | grep -qF '2026-10-12-ceremony-audit'`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py >/dev/null`
- `for h in '## Per-site table' '## First case: filer-warning close refusal' '## Prompt lint signals' '## Ranked changes' '## Already covered' '## Unverified'; do grep -qxF "$h" docs/reports/2026-10-12-ceremony-audit.md || exit 1; done`
- `for s in plan-reviewer filer 'second verifier' 'full chain' 'inherited red' gate-lock replan question; do grep -qiF "$s" docs/reports/2026-10-12-ceremony-audit.md || exit 1; done`
- `test -f docs/reports/2026-10-12-ceremony-audit.md && test "$(grep -oF '[propose a ticket]' docs/reports/2026-10-12-ceremony-audit.md | wc -l)" -le 5`
- `for t in T-0428 T-0456 T-0459 T-0446 T-0445 T-0457 T-0461 T-0462; do grep -qF "$t" docs/reports/2026-10-12-ceremony-audit.md || exit 1; done`
- `grep -qE '\.sdlc/\.04[0-9]{2}-' docs/reports/2026-10-12-ceremony-audit.md && grep -qF '[U]' docs/reports/2026-10-12-ceremony-audit.md`
- `test -f docs/reports/2026-10-12-ceremony-audit.md && ! grep -qF "$(printf '\342\200\224')" docs/reports/2026-10-12-ceremony-audit.md`
- The verifier reruns three counts named in the report's Method section (one first-case count, one per-site cost or catch count, one prompt lint count) and gets the numbers the report states.
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^docs/reports/2026-10-12-ceremony-audit(\.md|/)' )"`
