<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Write `docs/reports/<date>-solo-fails-and-blocks.md`, a dated report that sorts the solo first-round verifier non-passes and the builder blocked notes since 2026-10-08 (ui-kit-maison, agent-ui, ultimate-tokens, sdlc-lite) by root cause and ranks the agent file changes that would have prevented them, each with evidence pointers that resolve. Nothing outside this repo is written.

## Step 1: Classify solo non-passes and builder blocks, and write the ranked report
level: L3
### Read first
- `docs/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
This is a spike that produces one report. No agent file, script, or ticket changes. Every repo it inspects is read-only. Depends on: none. This is also the gates green step: the only gate that applies is `docs_check.py` (handoff Done when, and the root `AGENTS.md` validation table row for documentation-only edits).

1. Ingest and detect, with no model call (review-traces stage 1, `plugins/sdlc-lite/skills/review-traces/SKILL.md`). For each repo `~/Projects/maison/ui-kit-maison`, `~/Projects/nonoun/agent-ui`, `~/Projects/nonoun/ultimate-tokens`, and `~/Projects/nonoun/sdlc-lite` (the main checkout, not this lane), run `python3 plugins/sdlc-lite/scripts/traces.py ingest <repo>`, then `traces.py detect --repo <repo>`, then `traces.py clusters --max 5 --repo <repo>`, all from this tree. The default out dir is `.sdlc/runtime/traces/<repo-key>` under the current directory (`plugins/sdlc-lite/scripts/traces/store.py` `out_dir`). That dir is gitignored (`.gitignore:12`), so nothing is written into the inspected repos. Never pass `--rerun-criteria`, because it reruns criteria inside the inspected repo. Use the clusters only to cross-check your classification.
2. Cost and minutes: run `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --since 2026-10-08` per repo (the same command form as `docs/reports/2026-10-10-verifier-minutes.md`). Rank causes by count, then by minutes. Use dollars only where a repo is priced (the baseline says only sdlc-lite is metered; K-001).
3. Sample, drawn by a script you write at `.sdlc/0450-review-traces-solo-fails-and-blocks/sample.py` so the verifier can rerun it. Follow the baseline report's method (`docs/reports/2026-10-11-solo-campaign-baseline.md`): solo tickets have a `solo` row in `runs.jsonl` dated 2026-10-08 or later, hidden closed `.NNNN-*` folders are included, and worktree copies are excluded. Verifier rounds are ordered by round number (`verifier-L2.md`, then `-2`, `-3`), not by name.
   - First-round non-passes: take all of them, every first verifier result whose verdict is not `pass` on a ticket that later passed or closed. The baseline counted 34. If your count differs, report both numbers and the reason.
   - Builder blocked notes: classify all `builder-*.md` files with Status blocked in the window mechanically, by their tagged lines (`plan defect:`, `stale lane:`, `inherited red`, other). Read only a stratified sample of at most 30 in full: per repo, in sorted path order, every k-th file. State k and the per-repo counts. The handoff counted 173 notes, 55 naming a plan defect.
4. Classify each sampled non-pass into exactly one of the handoff's categories:
   - criterion defect (unsatisfiable, vacuous, fixed sha, circular, needs a live run)
   - builder gap (no default for a gap, scope widened, claimed without running)
   - environment (timeout, load, stale base)
   - verifier over-reach
   - other

   Classify each read blocked note as plan defect, environment, or other.
5. For each top cause, name the agent file and the rule it would change (`plugins/sdlc-lite/agents/builder.md`, `verifier.md`, `planner.md`, `solo.md`, or an overlay), the smallest wording change, and an observable measure (a detect rule, or a K-005 movement against the baseline of 89 of 123 first-pass, 72 percent). Read only the agent files your top causes name. Compare each cause with what has already shipped (T-0412, T-0413, T-0438, T-0439, overlays T-0441, T-0448 clarify v2) and say what is already covered. Find each of those tickets via `.sdlc/roadmap.md`, reading its handoff only. Mark at most 3 changes with the exact phrase `propose a ticket`, and do not use that phrase anywhere else in the report. File nothing.
6. Write the report at `docs/reports/YYYY-MM-DD-solo-fails-and-blocks.md`, using the date you write it. Use these exact `##` headings: `## Sample`, `## Classified counts`, `## Ranked changes`, `## Already covered`, `## Unverified`. Under `## Sample`, give the sample size, how it was drawn, and the commands run.
7. Evidence pointer format, settled here so the check can resolve it: write each pointer as a backticked path of the form `~/Projects/<...>/.sdlc/<...>.md`, pointing at the verifier or builder result file itself. Include at least 10 `verifier-L*` pointers and at least 5 `builder-L*` pointers.
8. Report rules:
   - Mark every claim you did not check `[U]`.
   - K-005 has no file yet (T-0449 is proposed, not built), so cite K-005 with the baseline report as its source.
   - No em dashes, no trailing whitespace, and keep the report under 400 lines (docs_check D-11 soft limit).

Diagnose, verify, and propose (review-traces stages 2 to 4) run inside this builder rather than as separate archaeologist, verifier, or planner dispatches. That keeps the ticket within its $10 budget, and the ticket's one independent verifier samples the pointers. Say so in `## Unverified`. Stop at $10 and report whatever you have.

Validation scope: the criteria below, plus `python3 plugins/sdlc-lite/scripts/docs_check.py`. No role, hook, or check.sh suite applies to a docs-only change.
### Acceptance criteria
- (red) `test "$(ls docs/reports/ | grep -c -- "-solo-fails-and-blocks\.md$")" -eq 1`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && for h in "## Sample" "## Classified counts" "## Ranked changes" "## Already covered" "## Unverified"; do grep -qxF "$h" "$f" || exit 1; done`
- `python3 -c "import re,os,glob; f=glob.glob('docs/reports/*-solo-fails-and-blocks.md'); assert len(f)==1, f; t=open(f[0]).read(); p=re.findall(r'\x60(~/Projects/[^\x60\s]*/\.sdlc/[^\x60\s]*\.md)\x60',t); v=[x for x in p if '/verifier-L' in x]; b=[x for x in p if '/builder-L' in x]; assert len(v)>=10 and len(b)>=5, (len(v),len(b)); bad=[x for x in p if not os.path.exists(os.path.expanduser(x))]; assert not bad, bad[:5]"`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && test "$(grep -c "propose a ticket" "$f")" -le 3`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && for t in T-0412 T-0413 T-0438 T-0439 T-0441 T-0448; do grep -qF "$t" "$f" || exit 1; done`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && grep -qF "K-005" "$f" && grep -qF "89 of 123" "$f"`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && for c in "criterion defect" "builder gap" "environment" "verifier over-reach" "plan defect"; do grep -qiF "$c" "$f" || exit 1; done`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && grep -qE "agents/(builder|verifier|planner|solo)\.md" "$f"`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && ! grep -nE "[[:space:]]$" "$f"`
- The verifier opens at least 5 evidence pointers from `## Ranked changes` and confirms each file shows the cause the report assigns it. The verifier also runs `.sdlc/0450-review-traces-solo-fails-and-blocks/sample.py` and confirms it reproduces the sample size stated under `## Sample`.
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py >/dev/null`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -v -- "-solo-fails-and-blocks\.md$")"`

## Assumptions
- docs_check.py exits nonzero on errors and passes on the current tree: verified. At HEAD it printed "0 errors, 24 warnings" with exit 0. On a fixture copy of `docs/` with `docs/reports/Bad Name.md` added, it exited 1 (D-12, D-3).
- The scope guard goes red when any file outside the report changes: verified on a scratch git repo with a stray file, which exited 1. At base it exits 0.
- The traces default out dir is inside this tree and gitignored, so ingest writes nothing into the inspected repos: verified by `plugins/sdlc-lite/scripts/traces/store.py` `out_dir` and `git check-ignore` (`.gitignore:12 .sdlc/runtime/`).
- The repo paths are `~/Projects/maison/ui-kit-maison` and `~/Projects/nonoun/{agent-ui,ultimate-tokens,sdlc-lite}`: verified by `ls` of each `.sdlc` dir and by the commands in `docs/reports/2026-10-10-verifier-minutes.md`.
- K-005 has no file in `docs/kpi/` yet (T-0449 is proposed in `.sdlc/roadmap.md:449`), so the report cites the baseline report for the 89 of 123 figure: verified by `ls docs/kpi`.
- Running stages 2 to 4 in the builder instead of as separate role dispatches is settled by the $10 ticket budget, by the review-traces rule that a headless session files nothing, and by the handoff's single independent verifier.

## Risks
- The first-round non-pass count may not reproduce 34. The baseline came from an unchecked one-off script, and T-0449's committed version is not built. The report states both numbers, and the criteria do not pin the count.
- `traces.py ingest` on four repos may be slow or produce clusters that do not match the handoff's categories. The clusters are a cross-check only.
- Evidence pointers into live repos can stop resolving if a closed folder is moved later. The criterion checks existence at verify time only.
- The 400-line soft limit is a warning, not an error, so a long report passes docs_check. The Do asks for less than 400 lines, but no criterion enforces it.
- The planner could not create a probe worktree here because `SDLC_TMP_WORKTREES` was unset in this session and the hook blocked it. Instead, the guard red views ran on scratch fixtures under the tmp prefix.
