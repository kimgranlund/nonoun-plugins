<!-- role=builder level=L3 model=opus effort=high -->
## Status
blocked

## Changes
None. Nothing in the repository was changed. The throwaway projects and their role logs are kept outside the repository at `/tmp/entry-probe.bh1AfI/{claude,codex}`. `docs/validation/entry-files-live-run.md` was not written, and the two link lines were not added.

## Checks
- Setup: `git init` in `/tmp/entry-probe.bh1AfI/claude` and `/tmp/entry-probe.bh1AfI/codex`, each with root `AGENTS.md`, a `CLAUDE.md` holding `@AGENTS.md`, `pkg/AGENTS.md` (rule: "Every line written to a file in pkg/ must end with the marker token ZEBRA-7 after a single space."), `pkg/value.txt`, `notes.txt`, `.sdlc/entry-probe/handoff.md`, and one commit. Every role was run through a wrapper that unsets the parent run's `SDLC_*` and `CLAUDE_CODE_*` session variables, then execs this repository's `plugins/sdlc-lite/scripts/run.sh`.
- Claude Code 2.1.285, `run.sh planner L2 .sdlc/entry-probe/handoff.md`: exit 0, model `claude-opus-5-5` (from the init event). The plan's step 1 has `### Read first` / ``- `pkg/AGENTS.md` ``, and step 2 has none.
- Claude Code, `steps.py split .sdlc/entry-probe`: exit 0. The step-1 handoff lists `pkg/AGENTS.md` under `### Read first`, and the step-2 handoff (notes.txt only) has no `### Read first`.
- Claude Code, `run.sh builder L1 .sdlc/entry-probe/step-1/handoff.md`: exit 0, Status done, model `claude-sonnet-5-5`. The log shows `"name":"Read","input":{"file_path":"/tmp/entry-probe.bh1AfI/claude/pkg/AGENTS.md"}`.
- Claude Code, `run.sh verifier L1 .sdlc/entry-probe/step-1/handoff.md`: exit 0, Verdict pass, model `claude-opus-5-5` (moved from sonnet by the independence rule). The log shows the Bash command `cat pkg/AGENTS.md; od -c pkg/value.txt; ...`, and its tool result begins `# pkg guidance\n\nEvery line written to a file in pkg/ must end with the marker token ZEBRA-7 ...`.
- Codex CLI 0.154.0, `codex_roles.py install .`: installed 22 project agents.
- Codex, `SDLC_BACKEND=codex run.sh planner L3 .sdlc/entry-probe/handoff.md`: exit 0, model `gpt-6-astra`. Step 1 has ``### Read first`` / ``- `pkg/AGENTS.md` ``, and step 2 has none.
- Codex, `steps.py split .sdlc/entry-probe`: exit 0. The step-1 handoff lists `pkg/AGENTS.md`, and the step-2 handoff has no `### Read first`.
- Codex, `SDLC_BACKEND=codex run.sh builder L4 .sdlc/entry-probe/step-1/handoff.md`: exit 0, Status done, model `gpt-6-astra` (runs.jsonl). The log shows the command `/bin/zsh -lc "pwd; cat pkg/AGENTS.md; git status --short; ..."` with output `# pkg guidance\n\nEvery line written to a file in pkg/ must end with the marker token ZEBRA-7 ...`.
- Codex, `codex_roles.py resolve verifier L3 .sdlc/entry-probe/step-1`: printed `gpt-6-sol high`.
- Codex, `SDLC_BACKEND=codex run.sh verifier L3 .sdlc/entry-probe/step-1/handoff.md`: exit 1, `verifier exited non-zero`. The log shows `"status":400 ... "The 'gpt-6-sol' model is not supported when using Codex with a ChatGPT account."`, and `verifier-L3.attempt.json` records `"model": "gpt-6-sol", "status": "failed"`.
- No acceptance criterion was run, because the report was not written.

## Notes
plan defect: the Codex levels "builder L4, verifier L3. These levels map to `gpt-6-astra`" are wrong for the verifier. `codex_roles.resolve` switches the verifier away from the builder's model to keep verification independent. After a `gpt-6-astra` build (L4), verifier L3 therefore runs on `gpt-6-sol`, which this account rejects (T-0163). Every Codex builder level maps to Sol or Astra, and every verifier level resolves to Sol or to the opposite of the builder's model. No combination of levels gives both roles `gpt-6-astra` on this account. So the Codex arm `verifier read the entry` cannot be produced, and the criterion requiring `| Codex | verifier read the entry | yes |` cannot pass without one of these:
- the user picks a replacement for `gpt-6-sol` (T-0163);
- the verifier independence rule is relaxed;
- a different account type is used.
Each of these is a user or planner decision, not a builder one.

Results observed so far:

| Host | Arm | Result |
|---|---|---|
| Claude Code | handoff lists the entry | yes |
| Claude Code | builder read the entry | yes |
| Claude Code | verifier read the entry | yes |
| Claude Code | root-only step has no Read first | yes |
| Codex | handoff lists the entry | yes |
| Codex | builder read the entry | yes |
| Codex | verifier read the entry | not run (verifier failed on `gpt-6-sol`, HTTP 400) |
| Codex | root-only step has no Read first | yes |

Other things the replanner should know:
- Both planners also restated the pkg rule in the step's `### Do` text, and the Codex builder read `pkg/AGENTS.md` inside a combined `cat` command.
- Codex exec logs carry `--dangerously-bypass-hook-trust` notices.
- The throwaway projects at `/tmp/entry-probe.bh1AfI` can be reused for the report once the Codex verifier can run; the Codex project's step-1 builder result is already in place.
