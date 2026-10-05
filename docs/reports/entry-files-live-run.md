# Entry files live run

Recorded: 2026-09-29. Live run for ticket T-0162: a role working on a plan step reads the entry files that govern the files it changes. One trial per arm, on Claude Code and on Codex.

## Environment

- Claude Code 2.1.285 (`claude_code_version` in the role logs), default backend of `plugins/sdlc-lite/scripts/run.sh`. Models from the `"model"` fields of the role logs: planner L2 `claude-opus-5-5`, builder L1 `claude-sonnet-5-5`, verifier L1 `claude-opus-5-5`. The verifier moved from Sonnet to Opus under the verifier independence rule; its result header reads `model=opus`.
- Codex CLI 0.154.0, `SDLC_BACKEND=codex`, standalone `codex exec` transport. The Codex event stream does not name the model, so the models come from the runner's records: the result header, `runs.jsonl`, and the attempt record. Planner L3, builder L4, and verifier L3 all ran on `gpt-6-astra`, effort `high`.
- The Codex verifier kept the builder's model, because `verifier_alternates` in `plugins/sdlc-lite/adapters/codex/models.json` is empty (T-0163). `codex_roles.py resolve verifier L3 .sdlc/entry-probe/step-1` printed `gpt-6-astra high shared`. The verifier result header is `<!-- role=verifier level=L3 model=gpt-6-astra effort=high shared_with_builder=yes -->`, and its `runs.jsonl` line holds `"shared_with_builder":true`.
- macOS, Darwin 25.6.0. Throwaway Git projects in a temp folder outside this repository. Transcripts and role logs are not kept in this repository.

## Projects

- Claude Code: `/tmp/entry-probe.bh1AfI/claude`
- Codex: `/tmp/entry-probe.bh1AfI/codex`

Each project was set up the same way and committed once (`ec8e4d9 init`):

- `AGENTS.md`: `# Project guidance` and one line, `A small text fixture. Keep every file plain text with a trailing newline.`
- `CLAUDE.md`: `@AGENTS.md`
- `pkg/AGENTS.md`: `# pkg guidance` and the rule `Every line written to a file in pkg/ must end with the marker token ZEBRA-7 after a single space.`
- `pkg/value.txt`: `value: 1 ZEBRA-7`
- `notes.txt`: `Notes`
- `.sdlc/entry-probe/handoff.md`: goal "Bump the fixture value and record the change in the notes", in two steps. Step 1 changes only `pkg/value.txt`, and step 2 changes only `notes.txt`.

## Method

Every role ran from the project root through a wrapper that unsets the parent run's `SDLC_*` and `CLAUDE_CODE_*` session variables and `CLAUDECODE`, then execs this repository's `plugins/sdlc-lite/scripts/run.sh`. A nested run therefore inherits no base sha, attempt id, or temp-worktree prefix from the run that launched it. `<repo>` below is this repository.

Claude Code:

```sh
<repo>/plugins/sdlc-lite/scripts/run.sh planner L2 .sdlc/entry-probe/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py split .sdlc/entry-probe
<repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/entry-probe/step-1/handoff.md
<repo>/plugins/sdlc-lite/scripts/run.sh verifier L1 .sdlc/entry-probe/step-1/handoff.md
```

Codex:

```sh
python3 <repo>/plugins/sdlc-lite/scripts/codex_roles.py install .
SDLC_BACKEND=codex <repo>/plugins/sdlc-lite/scripts/run.sh planner L3 .sdlc/entry-probe/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py split .sdlc/entry-probe
SDLC_BACKEND=codex <repo>/plugins/sdlc-lite/scripts/run.sh builder L4 .sdlc/entry-probe/step-1/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/codex_roles.py install .
python3 <repo>/plugins/sdlc-lite/scripts/codex_roles.py resolve verifier L3 .sdlc/entry-probe/step-1
SDLC_BACKEND=codex <repo>/plugins/sdlc-lite/scripts/run.sh verifier L3 .sdlc/entry-probe/step-1/handoff.md
```

The second `codex_roles.py install .` refreshed agents that `install --check` reported stale after T-0163. It installed 19 project agents, and a following `install --check` exited 0.

Each arm was read from the handoffs and role logs in the throwaway projects:

- `handoff lists the entry`: `.sdlc/entry-probe/step-1/handoff.md` has `### Read first` with `` - `pkg/AGENTS.md` ``.
- `builder read the entry`: the builder log holds a tool call that reads `pkg/AGENTS.md`, and its result holds the rule text.
- `verifier read the entry`: the same, in the verifier log.
- `root-only step has no Read first`: `grep -c 'Read first' .sdlc/entry-probe/step-2/handoff.md` prints `0`. That step changes only `notes.txt`, whose nearest entry is the root `AGENTS.md`.

## Which runs ran when

The runs came from two attempts of this step. The role bodies they exercise did not change between them: `git diff --quiet f20877a HEAD -- plugins/sdlc-lite/agents plugins/sdlc-lite/scripts/steps.py plugins/sdlc-lite/adapters/codex/instructions.md` exited 0 at `470f645`.

| Host | Run | Attempt | Plugin commit |
| --- | --- | --- | --- |
| Claude Code | project setup, planner, split, builder, verifier | blocked first attempt | `f20877a` |
| Codex | project setup, agent install, planner, split, builder | blocked first attempt | `f20877a` |
| Codex | failed verifier on `gpt-6-sol` (HTTP 400, `verifier-L3.attempt.json` status `failed`) | blocked first attempt | `f20877a` |
| Codex | agent reinstall, resolve, verifier on `gpt-6-astra` (`verifier-L3-2.md`) | this attempt | `470f645` |

The failed `gpt-6-sol` attempt record stays in the Codex step-1 folder. The new run wrote `verifier-L3-2.*` beside it.

## Results

| Host | Arm | Result | Evidence |
| --- | --- | --- | --- |
| Claude Code | handoff lists the entry | yes | step-1 handoff: `### Read first` / `` - `pkg/AGENTS.md` `` |
| Claude Code | builder read the entry | yes | `builder-L1.log`: `{"name": "Read", "input": {"file_path": "/tmp/entry-probe.bh1AfI/claude/pkg/AGENTS.md"}}`, result line 3 `Every line written to a file in pkg/ must end with the marker token ZEBRA-7 after a single space.` |
| Claude Code | verifier read the entry | yes | `verifier-L1.log`: Bash `cd /tmp/entry-probe.bh1AfI/claude; cat pkg/AGENTS.md; od -c pkg/value.txt; ...`, result begins `# pkg guidance\n\nEvery line written to a file in pkg/ must end with the marker token ZEBRA-7 ...` |
| Claude Code | root-only step has no Read first | yes | step-2 handoff (`notes.txt` only): `grep -c 'Read first'` prints `0` |
| Codex | handoff lists the entry | yes | step-1 handoff: `### Read first` / `` - `pkg/AGENTS.md` `` |
| Codex | builder read the entry | yes | `builder-L4.log`: command `/bin/zsh -lc "pwd; cat pkg/AGENTS.md; git status --short; ..."`, output `/tmp/entry-probe.bh1AfI/codex\n# pkg guidance\n\nEvery line written to a file in pkg/ must end with the marker token ZEBRA-7 ...` |
| Codex | verifier read the entry | yes | `verifier-L3-2.log`: command `/bin/zsh -lc 'pwd; cat pkg/AGENTS.md; cat .../skills/sdlc-lite/SKILL.md; ...'`, output `/tmp/entry-probe.bh1AfI/codex\n# pkg guidance\n\nEvery line written to a file in pkg/ must end with the marker token ZEBRA-7 ...` |
| Codex | root-only step has no Read first | yes | step-2 handoff (`notes.txt` only): `grep -c 'Read first'` prints `0` |

Role outcomes: both builders reported Status done and left `pkg/value.txt` as `value: 2 ZEBRA-7`. Both verifiers returned Verdict pass. Neither host's planner put `pkg/AGENTS.md` or the root `AGENTS.md` under `### Read first` in the `notes.txt` step.

## Limits

- One trial ran per arm, on one machine and one account per host.
- The Codex verifier shared the builder's model, `gpt-6-astra`, so that verification was not model-independent. The Claude Code verifier ran on a different model from its builder.
- The planners also carried the `pkg` rule into the step's Do text. The Claude Code planner restated the rule itself. The Codex planner spelled out the target line, `value: 2 ZEBRA-7`, marker included. The evidence for the mechanism is therefore the read in the log, not rule compliance.
- Both Codex reads of `pkg/AGENTS.md` were part of a combined `cat` command, not a lone read.
- The Codex project kept three untracked `sdlc-verifier-l*-alternate.toml` files from the first attempt's install, which the refresh did not remove. The Codex verifier found them, dated them before the build from their timestamps, and did not count them as the builder's changes.
- Codex runs printed `--dangerously-bypass-hook-trust` notices in their event streams.
- The run covers one nested entry one level deep and one root-only step. It does not cover several entry files in one step, deeper nesting, or a conflict between a nested rule and a root rule.
