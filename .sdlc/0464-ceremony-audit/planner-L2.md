<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Write the dated report `docs/reports/2026-10-12-ceremony-audit.md`. It ranks the SDLC Lite ceremony sites by measured cost and by recorded catches, gives a per-site "what did it catch" count, analyses the filer-warning close refusal as the first case, and marks at most 5 changes `[propose a ticket]`.

## Step 1: Ceremony audit report
level: L3
### Read first
- `docs/reports/AGENTS.md`
- `docs/AGENTS.md`
### Do
This is a read-only spike. Its output is one dated report and an optional sibling evidence folder. Depends on: none. Budget cap is $8 (handoff `budget_usd: 8`). If you hit the cap, stop, write what you have, and list the uncounted sites under `## Unverified`.

Targets:
- Create `docs/reports/2026-10-12-ceremony-audit.md`.
- Optionally create the evidence folder `docs/reports/2026-10-12-ceremony-audit/`. It holds any counting script you write plus its captured output, so the verifier can rerun the counts. Precedent: `docs/reports/solo-close-live-run/hidden.py`, and the "small evidence files in a sibling folder" rule in `docs/reports/AGENTS.md`.
- Change nothing else in this repo. Never write to ui-kit-maison (`/Users/kimgranlund/Projects/maison/ui-kit-maison`), agent-ui (`/Users/kimgranlund/Projects/nonoun/agent-ui`) or ultimate-tokens (`/Users/kimgranlund/Projects/nonoun/ultimate-tokens`). You may read them.
- Do not put evidence under `.sdlc/0464-ceremony-audit/`. Close renames that folder to `.0464-...`, so pointers into it would stop resolving.

Settled format decisions:
- The file starts with YAML front matter that contains the line `doc-type: report`. This makes docs_check rule S-6 resolve every relative link and every path code span in the report (`plugins/sdlc-lite/scripts/docs_check.py`, `standards_rules`, the `S-6` branch). That check is what "pointers that resolve" means.
- Write pointers into other repos as absolute paths. S-6 skips spans that start with `/`.
- The `/tmp/fanout-f5N.log` files are absolute paths too. They exist on this host (`/tmp/fanout-f50.log` to `/tmp/fanout-f59.log`) but are untracked. Quote only the numbers you reproduce from them.
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

Content (handoff Intent items 1 to 5):
1. First case. Cover every closed ticket since T-0431: the `.sdlc/.04NN-*` folders in this tree, plus a sample of closed tickets from the three other repos. ui-kit-maison uses `ticket_root: tickets`. For each filer `## Warnings` entry record:
   - its kind (`red-checkpoint: retrospective`, unverified claim, flake, other)
   - whether the close was refused
   - how it was cleared (`--ack-warnings`, `--reason`, `--force`; the flags are in `plugins/sdlc-lite/scripts/tickets.py` usage)
   - whether it led to a fix, a reopened ticket or a later defect
   - the minutes lost

   Confirm or correct the handoff's claims ("9 of 11 filers carry a retrospective red-checkpoint", "about 6 lane stalls"). A probe found 10 filer files containing `red-checkpoint` under `.sdlc/.04*/`. Some closed tickets (solo) have no filer, for example `.sdlc/.0456-cheap-gates-queue-behind-heavy/`.
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
3. Prompt lint. Run `python3 plugins/sdlc-lite/scripts/prompt_lint.py` (it defaults to `agents/*.md`, `skills/*/SKILL.md` and `overlays/*.md`) and count loop, verify and re-run wording. These counts are informational only, compared against `docs/reports/2026-10-11-agent-prompt-lint-baseline.md`.
4. Cost sources:
   - each ticket's `runs.jsonl`
   - `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --since <date>` (method precedent: `docs/reports/2026-10-11-solo-fails-and-blocks.md`, which also notes that minutes and dollars outside sdlc-lite are a floor)
   - `*.attempt.json` records

   Each candidate states its cost, its catches with pointers, the proposed change, the measure that must move, and its quality guard (K-005 first-pass rate, `docs/kpi/005-solo-first-pass-rate.md`, and rework after close). Keep every check that has at least one real catch.
5. Rank the candidates. In `## Already covered`, name each of T-0428, T-0456, T-0459, T-0446, T-0445, T-0457, T-0461 and T-0462 and say what it covers.

Settled evidence:
- `docs_check.py` exits 0 on the current tree with 0 errors and 26 warnings, so the bar is "no finding names the new report".
- I observed an S-6 error on a fixture report with a broken `.sdlc/.0999-nope/...` span, which proves the check bites.

Validation scope: the criteria below, plus `git diff --check`-style hygiene on the new file. This is a docs-only change, so check.sh and the role suites are not in scope (root `AGENTS.md`, validation table). The independent verifier reproduces a sample of the counts. Make each count rerunnable from a command or script named in `## Method`.
### Acceptance criteria
- (red) `test -f docs/reports/2026-10-12-ceremony-audit.md`
- `head -5 docs/reports/2026-10-12-ceremony-audit.md | grep -qx 'doc-type: report'`
- `out=$(python3 plugins/sdlc-lite/scripts/docs_check.py) && ! printf '%s\n' "$out" | grep -qF '2026-10-12-ceremony-audit'`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py >/dev/null`
- `for h in '## Per-site table' '## First case: filer-warning close refusal' '## Prompt lint signals' '## Ranked changes' '## Already covered' '## Unverified'; do grep -qxF "$h" docs/reports/2026-10-12-ceremony-audit.md || exit 1; done`
- `for s in plan-reviewer filer 'second verifier' 'full chain' 'inherited red' gate-lock replan question; do grep -qiF "$s" docs/reports/2026-10-12-ceremony-audit.md || exit 1; done`
- `test -f docs/reports/2026-10-12-ceremony-audit.md && test "$(grep -cF '[propose a ticket]' docs/reports/2026-10-12-ceremony-audit.md)" -le 5`
- `for t in T-0428 T-0456 T-0459 T-0446 T-0445 T-0457 T-0461 T-0462; do grep -qF "$t" docs/reports/2026-10-12-ceremony-audit.md || exit 1; done`
- `grep -qE '\.sdlc/\.04[0-9]{2}-' docs/reports/2026-10-12-ceremony-audit.md`
- `grep -qF '[U]' docs/reports/2026-10-12-ceremony-audit.md`
- `test -f docs/reports/2026-10-12-ceremony-audit.md && ! grep -qF '—' docs/reports/2026-10-12-ceremony-audit.md`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^docs/reports/2026-10-12-ceremony-audit(\.md|/)' )"`

## Assumptions
- The report date is 2026-10-12 (the handoff's `created:` and today). If the build runs on a later day, the file still uses this stem so that the criteria hold. Verified by the handoff front matter.
- `doc-type: report` front matter turns on S-6 path resolution for reports: verified at `plugins/sdlc-lite/scripts/docs_check.py` (`standards_rules`, `on('S-6') and kind == 'reports' and dtype == 'report'`) and by a fixture run that exited 1 with an S-6 error.
- S-6 skips absolute paths, so pointers into the other repos and into `/tmp` do not fail docs_check: verified at the same branch (`span.startswith(('/', '~'))`).
- docs_check is green now (exit 0, 0 errors, 26 warnings, none naming the new report): verified by running it.
- The scope guard goes red when an out-of-scope path changes: verified by running it with `SDLC_BASE_SHA=HEAD~1` (exit 1). It is green at HEAD.
- The three other repos are readable at `/Users/kimgranlund/Projects/maison/ui-kit-maison`, `/Users/kimgranlund/Projects/nonoun/agent-ui` and `/Users/kimgranlund/Projects/nonoun/ultimate-tokens`: verified with `ls`. `/Users/kimgranlund/Projects/_archive/ui-kit-maison` is an archive copy, not the sample source.
- The fanout logs `/tmp/fanout-f50.log` to `/tmp/fanout-f59.log` exist on this host: verified with `ls`.

## Risks
- The criteria check the report's structure, markers and pointer resolution, not whether the counts are right. The independent verifier is the check that reproduces a sample of the counts. Counts that cannot be rerun from `## Method` would leave that check weak.
- Cost data outside sdlc-lite is sparse: the collector records durations for sdlc-lite and ui-kit-maison only and prices only sdlc-lite solo runs (`docs/reports/2026-10-11-solo-fails-and-blocks.md`). Many per-site costs will be floors or `[U]`.
- The $8 cap can force a partial sweep of the item 2 sites. The step handles this by listing uncounted sites under `## Unverified`, but the ranking may be thinner than intended.
- The `[propose a ticket]` ceiling counts the literal anywhere in the file, so a stray mention in prose would count against the 5.
- A probe fixture and `probe.sh` were left under `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout41/w/.worktrees/tmp/0464-planner-L2/` (scratch, removed by run end, not deleted here per the no-delete rule).
