## Task goal
A dated report that turns the 34 first-round verifier non-passes on solo tickets and the 173 builder blocked notes into a ranked list of specific agent file changes, each with the evidence rows behind it.

## Step 1: Classify solo non-passes and builder blocks, and write the ranked report
level: L3
### Read first
- `docs/AGENTS.md`
- `docs/reports/AGENTS.md`
- `.sdlc/AGENTS.md`
### Do
This spike produces one report. It changes no agent file, script, or ticket, and every repo it inspects is read-only. Depends on: none. This is also the gates green step. The only gate that applies is `docs_check.py` (the handoff's Done when, and the root `AGENTS.md` validation table row for documentation-only edits).

1. Ingest and detect, with no model call (review-traces stage 1, `plugins/sdlc-lite/skills/review-traces/SKILL.md`). Run every command from this tree. For each repo, run `python3 plugins/sdlc-lite/scripts/traces.py ingest <repo>`, then `traces.py detect --repo <repo>`, then `traces.py clusters --max 5 --repo <repo>`. The repos are:
   - `~/Projects/maison/ui-kit-maison`
   - `~/Projects/nonoun/agent-ui`
   - `~/Projects/nonoun/ultimate-tokens`
   - `~/Projects/nonoun/sdlc-lite` (the main checkout, not this lane)

   The default out dir is `.sdlc/runtime/traces/<repo-key>` under the current directory (`plugins/sdlc-lite/scripts/traces/store.py` `out_dir`). It is gitignored (`.gitignore:12`), so nothing is written into the inspected repos. Never pass `--rerun-criteria`, because it reruns criteria inside the inspected repo. Use the clusters only to cross-check your classification.
2. Cost and minutes: run `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --since 2026-10-08` for each repo. This is the command form `docs/reports/2026-10-10-verifier-minutes.md` uses; it prints to stdout and writes no file. Rank causes by count, then by minutes. Use dollars only where a repo is priced: the baseline says only sdlc-lite is metered (K-001).
3. Draw the sample with a script you write at `.sdlc/0450-review-traces-solo-fails-and-blocks/sample.py`, so the verifier can rerun it. Follow the method of the baseline report (`docs/reports/2026-10-11-solo-campaign-baseline.md`):
   - A solo ticket has a `solo` row in `runs.jsonl` dated 2026-10-08 or later.
   - Include the hidden closed `.NNNN-*` folders. ui-kit-maison keeps its tickets in a tickets subfolder of its own .sdlc folder.
   - Exclude worktree copies.
   - Order verifier rounds by round number (`verifier-L2.md`, then `-2`, then `-3`), not by name.

   What to sample:
   - First-round non-passes: take all of them. That is every first verifier result whose verdict is not `pass`, on a ticket that later passed or closed. The baseline counted 34. If your count differs, report both numbers and the reason.
   - Builder blocked notes: classify every `builder-*.md` in the window with Status blocked mechanically, by its tagged lines (`plan defect:`, `stale lane:`, `inherited red`, other). Read in full only a stratified sample of at most 30: per repo, in sorted path order, every k-th file. State k and the per-repo counts. The handoff counted 173 notes, 55 of them naming a plan defect.
4. Classify each sampled non-pass into exactly one of the handoff's categories:
   - criterion defect (unsatisfiable, vacuous, fixed sha, circular, needs a live run)
   - builder gap (no default for a gap, scope widened, claimed without running)
   - environment (timeout, load, stale base)
   - verifier over-reach
   - other

   Classify each blocked note you read as plan defect, environment, or other.
5. For each top cause, give:
   - the agent file and the rule it would change (`plugins/sdlc-lite/agents/builder.md`, `verifier.md`, `planner.md`, `solo.md`, or an overlay)
   - the smallest wording change
   - an observable measure: a detect rule, or a K-005 movement against the baseline of 89 of 123 first-pass (72 percent)

   Read only the agent files your top causes name. Compare each cause with what has already shipped (T-0412, T-0413, T-0438, T-0439, the overlays in T-0441, T-0448 clarify v2) and say what is already covered. Find each of those tickets through `.sdlc/roadmap.md` and read only its handoff. Mark at most 3 changes with the exact phrase `propose a ticket`. Do not use that phrase anywhere else in the report, not even in prose about the cap. File nothing.
6. Write the report at `docs/reports/YYYY-MM-DD-solo-fails-and-blocks.md`, using the date you write it. Use these exact `##` headings: `## Sample`, `## Classified counts`, `## Ranked changes`, `## Already covered`, `## Unverified`. Under `## Sample`, give the sample size, how it was drawn, and the commands run. Do not create a sibling evidence folder under `docs/reports/`. Keep `sample.py`, any sample list it prints, and any stage 2 to 4 scratch in `.sdlc/0450-review-traces-solo-fails-and-blocks/`, because the scope guard below allows no file outside `.sdlc` except the report.
7. Evidence pointer format, fixed here so the check can resolve it: write each pointer as a backticked path of the form `~/Projects/<...>/.sdlc/<...>.md` that points at the verifier or builder result file itself. Include at least 10 `verifier-L*` pointers and at least 5 `builder-L*` pointers.
8. Report rules:
   - Mark every claim you did not check `[U]`.
   - K-005 has no file yet: `docs/kpi/` holds 001 to 004, and T-0449 is proposed, not built. Cite K-005 with the baseline report as its source.
   - No em dashes, no trailing whitespace, and keep the report under 400 lines (the docs_check D-11 soft limit).

Run diagnose, verify, and propose (review-traces stages 2 to 4) inside this builder, not as separate archaeologist, verifier, or planner dispatches. That keeps the ticket within its $10 budget, and the ticket's one independent verifier samples the pointers. Say so under `## Unverified`. Stop at $10 and report whatever you have.

Validation scope: the criteria below, plus `python3 plugins/sdlc-lite/scripts/docs_check.py`. No role, hook, or check.sh suite applies to a docs-only change.

Why the cap criterion changed: `steps.py split` refused the planner-L2 form as a count over a changing set. That form ran `grep -c` on a file found with `ls` and a glob, and compared the result with 3. The count is over this step's own report, so the cap is now one `python3 -c` that finds the single report and counts occurrences of the phrase, not lines. On a fixture report with four occurrences it exits 1.
### Acceptance criteria
- (red) `test "$(ls docs/reports/ | grep -c -- "-solo-fails-and-blocks\.md$")" -eq 1`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && for h in "## Sample" "## Classified counts" "## Ranked changes" "## Already covered" "## Unverified"; do grep -qxF "$h" "$f" || exit 1; done`
- `python3 -c "import re,os,glob; f=glob.glob('docs/reports/*-solo-fails-and-blocks.md'); assert len(f)==1, f; t=open(f[0]).read(); p=re.findall(r'\x60(~/Projects/[^\x60\s]*/\.sdlc/[^\x60\s]*\.md)\x60',t); v=[x for x in p if '/verifier-L' in x]; b=[x for x in p if '/builder-L' in x]; assert len(v)>=10 and len(b)>=5, (len(v),len(b)); bad=[x for x in p if not os.path.exists(os.path.expanduser(x))]; assert not bad, bad[:5]"`
- `python3 -c "import glob; f=glob.glob('docs/reports/*-solo-fails-and-blocks.md'); assert len(f)==1, f; n=open(f[0]).read().count('propose a ticket'); assert n <= 3, n"`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && for t in T-0412 T-0413 T-0438 T-0439 T-0441 T-0448; do grep -qF "$t" "$f" || exit 1; done`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && grep -qF "K-005" "$f" && grep -qF "89 of 123" "$f"`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && for c in "criterion defect" "builder gap" "environment" "verifier over-reach" "plan defect"; do grep -qiF "$c" "$f" || exit 1; done`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && grep -qE "agents/(builder|verifier|planner|solo)\.md" "$f"`
- `f=$(ls docs/reports/*-solo-fails-and-blocks.md) && ! grep -nE "[[:space:]]$" "$f"`
- The verifier opens at least 5 evidence pointers from `## Ranked changes` and confirms that each file shows the cause the report assigns to it. The verifier also runs `.sdlc/0450-review-traces-solo-fails-and-blocks/sample.py` and confirms that it reproduces the sample size stated under `## Sample`.
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py >/dev/null`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -v -- "-solo-fails-and-blocks\.md$")"`
