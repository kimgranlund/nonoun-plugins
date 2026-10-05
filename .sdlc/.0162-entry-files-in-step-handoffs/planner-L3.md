<!-- role=planner level=L3 model=fable effort=xhigh -->
## Goal
A builder or verifier working on a plan step reads the nested `AGENTS.md` files that govern the files the step changes, on both Claude Code and Codex, through a `### Read first` subsection that the planner writes, `steps.py lint` checks, and handwritten step handoffs carry.

## Step 1: steps.py lint refuses a missing `### Read first` path
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first. It is the nearest entry for every file in this step.

In `plugins/sdlc-lite/scripts/steps.py`:
- Add a helper that returns the listed paths of one step block. It reads the lines under a `### Read first` heading, up to the next `## ` or `### ` line, and leaves out fenced lines. It takes each list item that holds a code span, and the path is the text of that span.
- In `lint_steps`, resolve each listed path against the git toplevel of the plan file's folder, using the existing `git_toplevel`. Outside git, resolve it against that folder. A path that does not exist adds this finding: `steps: <plan> step <n>: ### Read first lists a path that does not exist: <path>`.
- `lint_or_fail` then refuses with the usual `plan defect` last line. Because `split` shares `lint_or_fail`, `split` refuses too.
- A step with no subsection stays valid.
- `swap` calls `lint_steps` on a synthetic block that has no subsection, so `swap` is unaffected.
- `split` already copies the subsection verbatim. Do not change that.

Update the module docstring for `lint` and `split`. Name `### Read first`, the one-line item form ``- `<path>` ``, the path base, and the refusal.

Add selftest case (r). It uses a temp git repo so the toplevel base is exercised. Use exactly these check names:
- `(r) lint accepts a ### Read first path that exists`
- `(r) lint refuses a ### Read first path that does not exist`
- `(r) split copies ### Read first into the step handoff`

In `docs/maintenance/sdlc-internals.md`, add the `### Read first` path check to the `scripts/steps.py` entry. That keeps the reference current.
### Acceptance criteria
- ``d=$(mktemp -d) && git -C "$d" init -q && mkdir -p "$d/sub" "$d/.sdlc/t" && touch "$d/sub/AGENTS.md" && printf '## Step 1: x\nlevel: L1\n### Read first\n- `sub/AGENTS.md`\n### Do\nd\n### Acceptance criteria\n- ok\n' > "$d/.sdlc/t/ok.md" && sed "s#sub/AGENTS#gone/AGENTS#" "$d/.sdlc/t/ok.md" > "$d/.sdlc/t/bad.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/.sdlc/t/ok.md" && { python3 plugins/sdlc-lite/scripts/steps.py lint "$d/.sdlc/t/bad.md" > "$d/out" 2>&1; test $? -eq 1; } && grep -qF gone/AGENTS.md "$d/out" && grep -qF "plan defect" "$d/out"``
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -qF 'ok: (r) lint accepts a ### Read first path that exists'`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -qF 'ok: (r) lint refuses a ### Read first path that does not exist'`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -qF 'ok: (r) split copies ### Read first into the step handoff'`
- `grep -qF '### Read first' plugins/sdlc-lite/scripts/steps.py`
- `grep -qF 'Read first' docs/maintenance/sdlc-internals.md`

## Step 2: Planner writes the subsection; builder and verifier read it
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first.

In `plugins/sdlc-lite/agents/planner.md`, add a short `## Entry files` section between the "Criteria that can pass" rules and `## Merge steps`. It states:
- For each file a step changes, find the nearest `AGENTS.md` in that file's folder or a folder above it.
- Leave out the root entry.
- List the rest under a `### Read first` subsection. The subsection sits after the step's `level:` line and before `### Do`.
- Each item is one line, ``- `<path>` ``, with the path relative to the repository root.
- A step whose only entry is the root has no subsection.
- Files the step only reads are not listed.
- `steps.py lint` refuses a listed path that does not exist.

In the planner's final-message template, show the optional subsection between `level: L<n>` and `### Do`, with a one-line note that it appears only when needed. Do not touch the fenced `merge-step` block. check.py requires it to stay identical in the planner and handoff-format.

In `plugins/sdlc-lite/agents/builder.md` and `plugins/sdlc-lite/agents/verifier.md`, add one sentence to the opening paragraph: before starting, read every file listed under the handoff's `### Read first` and follow it for the files it governs. Put it in the opening paragraph, not the numbered list, because `hooks/block-repo-format.sh` cites "builder rule 6" and renumbering would break that reference.

Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` so the Codex agent TOMLs under `plugins/sdlc-lite/adapters/codex/agents/` match.
### Acceptance criteria
- `grep -qF '### Read first' plugins/sdlc-lite/agents/planner.md`
- `grep -qE 'nearest .?AGENTS\.md' plugins/sdlc-lite/agents/planner.md`
- `grep -qF '### Read first' plugins/sdlc-lite/agents/builder.md`
- `grep -qF '### Read first' plugins/sdlc-lite/agents/verifier.md`
- `grep -qF '### Read first' plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l1.toml`
- `grep -qF '### Read first' plugins/sdlc-lite/adapters/codex/agents/sdlc-builder-l1.toml`
- `grep -qF '### Read first' plugins/sdlc-lite/adapters/codex/agents/sdlc-verifier-l1.toml`

## Step 3: Handwritten step handoffs and the step template carry the subsection
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first.

- `plugins/sdlc-lite/skills/fix/SKILL.md` step 2: when the file being fixed has a nearest `AGENTS.md` other than the root, the conductor adds a `### Read first` subsection. It follows the same rule as the planner and sits after `level:` and before `### Do`. Keep the existing lint target `.sdlc/<slug>/step-1/handoff.md` unchanged, because check.py pins it.
- `plugins/sdlc-lite/skills/chain/SKILL.md` section 5 step 3: the `Loose ends` step handoff adds the same subsection for the files its items change.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, step handoff template: add the heading line `### Read first` with an item line ``- `<path>` `` between `level: L<n>` and `### Do`. Add prose that calls the subsection optional, states the nearest-entry rule with the root left out, and notes that `steps.py lint` refuses a missing path. Leave the fenced `merge-step` block unchanged.
### Acceptance criteria
- `grep -qF '### Read first' plugins/sdlc-lite/skills/fix/SKILL.md`
- `grep -qF '### Read first' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF '### Read first' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -A2 -x 'level: L.n.' plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -qxF '### Read first'`
- `grep -F 'Read first' plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -qi optional`

## Step 4: check.py pins the Read first contract
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first.

In `plugins/sdlc-lite/scripts/check.py`, add a contract check that the phrase `Read first` appears in each of these files:
- `agents/planner.md`
- `agents/builder.md`
- `agents/verifier.md`
- `skills/fix/SKILL.md`
- `skills/chain/SKILL.md`
- `skills/handoff-format/SKILL.md`
- `scripts/steps.py`

Each miss is reported as `FAIL <rel>: read-first route missing "Read first"`. Add a negative control in the style of the finish-in-session and builder-scope checks: the check must flag the file when the phrase is removed from its text. Add a numbered item for it to the module docstring.
### Acceptance criteria
- ``d=$(mktemp -d) && cp -R plugins/sdlc-lite "$d/p" && sed -i.bak "s/Read first/Read later/g" "$d/p/agents/builder.md" && { python3 "$d/p/scripts/check.py" "$d/p" > "$d/out" 2>&1; test $? -eq 1; } && grep -F agents/builder.md "$d/out" | grep -qF "Read first"``
- ``d=$(mktemp -d) && cp -R plugins/sdlc-lite "$d/p" && sed -i.bak "s/Read first/Read later/g" "$d/p/skills/fix/SKILL.md" && { python3 "$d/p/scripts/check.py" "$d/p" > "$d/out" 2>&1; test $? -eq 1; } && grep -F skills/fix/SKILL.md "$d/out" | grep -qF "Read first"``

## Step 5: Live run on Claude Code and Codex
level: L3
### Do
Read `AGENTS.md` and `docs/codex-role-execution.md` first. Use `docs/reports/onboard-live-run.md` as the model for the report.

This replaces the blocked first attempt, `.sdlc/0162-entry-files-in-step-handoffs/step-5.superseded-1/builder-L3.md`. That attempt got seven of the eight arms. The Codex verifier failed because it resolved to `gpt-6-sol`. T-0163 has since mapped every Codex level to `gpt-6-astra` in `plugins/sdlc-lite/adapters/codex/models.json` and left `verifier_alternates` empty. The Codex verifier now keeps the builder's model, and `run.sh` records `shared_with_builder=yes` in the verifier result header and `"shared_with_builder": true` in `runs.jsonl`.

Projects:
- Reuse the blocked attempt's throwaway projects, `/tmp/entry-probe.bh1AfI/claude` and `/tmp/entry-probe.bh1AfI/codex`, when they still hold its `.sdlc/entry-probe/` results: the planner result, the `step-1` and `step-2` handoffs, the step-1 builder log, and, in the Claude project, the step-1 verifier log.
- Reuse holds only while the role bodies the arms exercise are unchanged. Run `git diff --quiet "$(cat .sdlc/0162-entry-files-in-step-handoffs/step-5.superseded-1/base-sha)" HEAD -- plugins/sdlc-lite/agents plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/adapters/codex/instructions.md` in this repository. Exit 0 means reuse is allowed. Any other exit means every arm reruns in fresh projects.
- A host whose project or logs are missing gets a fresh throwaway git project in a temp folder outside this repository: a root `AGENTS.md`, a `CLAUDE.md` holding `@AGENTS.md`, `pkg/AGENTS.md` holding one distinctive rule sentence, `pkg/value.txt`, a root `notes.txt`, and a task handoff at `.sdlc/entry-probe/handoff.md` whose goal needs two steps: one that changes `pkg/value.txt` and one that changes only `notes.txt`.

Runs, for each host, from the project root with this repository's `plugins/sdlc-lite/scripts/run.sh`:
1. The planner.
2. `steps.py split` on the task dir.
3. The builder and then the verifier on the `pkg/value.txt` step.

In a reused project, run only the roles that have no result yet. In the reused Codex project, that is only the verifier.

Levels and models:
- Claude Code: the default backend, planner L2, builder L1, verifier L1.
- Codex: `SDLC_BACKEND=codex`, planner L3, builder L4, verifier L3. All three run on `gpt-6-astra`.
- Before any Codex role, run `python3 <this repo>/plugins/sdlc-lite/scripts/codex_roles.py install .` in the Codex project. The agents the blocked attempt installed there are stale, and `install --check` reports them.
- Before the Codex verifier, run `python3 <this repo>/plugins/sdlc-lite/scripts/codex_roles.py resolve verifier L3 .sdlc/entry-probe/step-1` from the project root. It must print `gpt-6-astra high shared`. If it prints anything else, or Codex rejects the model, stop with Status blocked and quote the output.
- The failed `gpt-6-sol` attempt record in the reused step-1 dir stays in place. The rerun writes a new attempt beside it.

Run each role through a wrapper that unsets the parent run's `SDLC_*` and `CLAUDE_CODE_*` session variables, as `/tmp/entry-probe.bh1AfI/run-role` does. That way a nested run never inherits this step's base sha, attempt id, or temp-worktree prefix. Run every role in the foreground with a Bash timeout of 600000 or more.

For each host, confirm the four things below. Check them in the handoffs and role logs themselves, not in the superseded builder report, and quote a short log excerpt as evidence for each:
- The `pkg` step handoff lists `pkg/AGENTS.md` under `### Read first`.
- The builder log shows a read of `pkg/AGENTS.md`.
- The verifier log shows a read of `pkg/AGENTS.md`.
- The `notes.txt` step handoff has no `### Read first`.

Write `docs/reports/entry-files-live-run.md` with:
- the recorded date, 2026-09-29, and ticket T-0162
- the environment: host versions, the models taken from the logs, and the Codex verifier's `shared_with_builder=yes` header
- the method and the exact commands
- the throwaway project paths
- which runs came from the blocked attempt and which ran in this attempt, with the plugin commit each ran at
- a results table with the header `| Host | Arm | Result | Evidence |`
- one row per host and arm. Use the host labels `Claude Code` and `Codex`, the arm labels `handoff lists the entry`, `builder read the entry`, `verifier read the entry`, and `root-only step has no Read first`, and a Result of `yes` or `no`.
- a limits section that states at least these:
  - One trial ran per arm.
  - The Codex verifier shared the builder's model, so that verification was not model-independent.
  - The planners also restated the `pkg` rule in the step's Do text. The evidence for the mechanism is therefore the read in the log, not rule compliance.

Record what actually happened. A `no` stays a `no`. If a host cannot run, Status is blocked with the evidence, and nothing is fabricated.

Add a link line for the report to `docs/README.md`, next to the onboard live run line. Link the report from the "How roles reach an entry" section of `docs/repo-onboarding/design.md`. Transcripts and role logs stay out of the repository.
### Acceptance criteria
- `test -f docs/reports/entry-files-live-run.md`
- `grep -qF 'validation/entry-files-live-run.md' docs/README.md`
- `grep -qF 'entry-files-live-run.md' docs/repo-onboarding/design.md`
- `grep -qF '| Host | Arm | Result | Evidence |' docs/reports/entry-files-live-run.md`
- `for h in "Claude Code" Codex; do for a in "handoff lists the entry" "builder read the entry" "verifier read the entry" "root-only step has no Read first"; do grep -qF "| $h | $a | yes |" docs/reports/entry-files-live-run.md || exit 1; done; done`
- `grep -qF 'gpt-6-astra' docs/reports/entry-files-live-run.md`
- `grep -qF 'shared_with_builder' docs/reports/entry-files-live-run.md`
- `grep -qF 'T-0162' docs/reports/entry-files-live-run.md`
- The report's evidence column or sections quote log excerpts that show a read of pkg/AGENTS.md by the builder and by the verifier on each host.
- The report names the throwaway Codex project path. The Codex verifier result file in that project's .sdlc/entry-probe/step-1 folder has a Verdict section, and its first line is a header holding model=gpt-6-astra and shared_with_builder=yes.

## Step 6: Gates green
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first.

Run every gate below and fix any red that steps 1 to 5 introduced. If a gate was already red at `$SDLC_BASE_SHA`, report Status `inherited red`. If a shared role or skill body changed after step 2, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` again.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `git diff --check`

## Risks
- Only step 5 changed from `planner-L2.md`. Steps 1 to 4 and 6 are byte-identical, and the existing `step-6/handoff.md` already matches, so `steps.py split --only 5` is the only split this replan needs.
- The reused runs span two plugin commits: the blocked attempt's base for seven arms, and the current HEAD for the Codex verifier. On this tree, `git diff --quiet` from that base to HEAD over `agents/`, `steps.py`, and the Codex `instructions.md` exits 0, so reuse holds now. If a main sync changes one of those files before the build, the Do's check sends every arm to a fresh rerun, which means about six live role runs across two hosts.
- If `/tmp/entry-probe.bh1AfI` is cleaned before the build (a reboot, a temp sweep), both hosts rerun in full. That takes longer and costs more, but the steps are the same.
- The Codex verifier now shares the builder's model. That was the user's T-0163 decision. It weakens independence on the Codex arm, so the report must state it as a limit instead of treating it as equivalent to the Claude arm.
- Codex could still reject `gpt-6-astra` or fail for account reasons. The step then blocks with evidence rather than claiming the arm.
- The step 5 verifier cannot cheaply rerun the live runs. The runnable criteria check the report's structure. The last two criteria need the verifier to read the logs in the throwaway projects, which exist only on this host.
- `check.sh` takes about 100 seconds, and the gates step runs it along with the other gates. On this tree all seven gates are green, and each was seen red on a mutated copy.
- Paths in `### Read first` resolve against the git toplevel of the plan file's folder. A plan file outside any git repo falls back to its own folder. That fallback was chosen in step 1, not settled by the ticket.
