# Role result schema live run

Recorded: 2026-10-01. Live run for ticket T-0184: every role result file is validated against one declared schema before the pipeline advances, and a malformed result is refused so the pipeline does not move. One real Claude Code builder run per arm, plus one rerun of the malformed arm.

## Environment

- Date: 2026-10-01.
- Host OS: macOS 26.6.2 (build 25G83), Darwin 25.6.0.
- `claude --version`: `2.1.286 (Claude Code)`; the role logs record `"claude_code_version":"2.1.286"`. Default Claude backend of `plugins/sdlc-lite/scripts/run.sh`.
- Model: every builder L1 log records `"model":"claude-sonnet-5-5"`; every result header and `runs.jsonl` line records `model=sonnet effort=low`.
- Repo commit: `f45649e` (T-0184 plan review), with the uncommitted T-0184 changes of steps 1 to 5 in the working tree. The scripts that ran, by SHA-256: `run.sh` `b9021f91...b5d8b28`, `results.py` `49c57fff...abf37b`, `steps.py` `0b5aa00b...c735a`.
- Throwaway project: `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/role-result-probe.jIfogzYTz9`, made with `mktemp -d`, outside this repository. One commit (`a4b263f init`) holding `greet.sh` (`echo hello`) and a `.gitignore` of `.sdlc/` and `.worktrees/`. This repository's `.sdlc` was not used. Role logs are not kept in this repository.

## Commands

Every run came from the project root through a wrapper `W` that unsets every `CLAUDE*` variable and `SDLC_ROLE SDLC_BASE_SHA SDLC_TMP_WORKTREES SDLC_HEADLESS SDLC_ATTEMPT_ID SDLC_ATTEMPT_NAME SDLC_LIFECYCLE_CHILD SDLC_ROUTING_REASON`, then runs `exec bash <repo>/plugins/sdlc-lite/scripts/run.sh "$@"`, so the nested run inherits nothing from the builder session that launched it. `W builder L1 <handoff>` is therefore `bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 <handoff>`. `<repo>` is this repository.

Setup:

```sh
P=$(mktemp -d -t role-result-probe)
cd "$P" && git init -q
printf '#!/usr/bin/env bash\necho hello\n' > greet.sh
printf '.sdlc/\n.worktrees/\n' > .gitignore
git add . && git commit -qm init
mkdir -p .sdlc/t/step-1 .sdlc/t2/step-1 .sdlc/t3/step-1
```

Arm 1, malformed (first try, then the stronger rerun in the same step dir):

```sh
# .sdlc/t/step-1/handoff.md: change greet.sh to echo hello world; an "Output format override" asks
# for a final message with only ## Changes and no ## Status
bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/t/step-1/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py next .sdlc/t/step-1
git checkout -q greet.sh
# handoff.md rewritten: the user authorizes the override, the final message must be exactly
# "## Changes" / "greet.sh: echo hello world", and the previous attempt failed by writing ## Status
bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/t/step-1/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py next .sdlc/t/step-1
```

Arm 2, structural (no model call; the copied result is the arm 1 rerun's saved result with its header line removed):

```sh
cp .sdlc/t3/step-1/handoff.md .sdlc/t2/step-1/handoff.md
tail -n +2 .sdlc/t/step-1/builder-L1-2.md > .sdlc/t2/step-1/builder-L1.md
echo '{"role":"builder","level":"L1","file":"builder-L1.md"}' > .sdlc/t2/step-1/runs.jsonl
python3 <repo>/plugins/sdlc-lite/scripts/steps.py next .sdlc/t2/step-1
python3 <repo>/plugins/sdlc-lite/scripts/results.py validate .sdlc/t2/step-1/builder-L1.md --role builder
```

Arm 3, normal (`.sdlc/t3/step-1/handoff.md` asks for the same change and says nothing about the output format):

```sh
git checkout -q greet.sh
bash <repo>/plugins/sdlc-lite/scripts/run.sh builder L1 .sdlc/t3/step-1/handoff.md
python3 <repo>/plugins/sdlc-lite/scripts/steps.py next .sdlc/t3/step-1
```

## Evidence

| Arm | run.sh | stderr | `steps.py next` first line |
| --- | --- | --- | --- |
| 1, first try | exit 0 | none | `verify L1` |
| 1, malformed (rerun) | exit 3 | `run.sh: builder result lacks ## Status (done\|blocked\|inherited red: <tests>); see /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/role-result-probe.jIfogzYTz9/.sdlc/t/step-1/builder-L1-2.md` | `rebuild L1` |
| 2, structural | no run | `steps.py` exit 0; `results.py validate` exit 1 with `results.py: .sdlc/t2/step-1/builder-L1.md: first line is not a <!-- role=<r> level=<L> model=<m> effort=<e> --> header` | `invalid result: .sdlc/t2/step-1/builder-L1.md: first line is not a <!-- role=<r> level=<L> model=<m> effort=<e> --> header` |
| 3, normal | exit 0 | empty | `verify L1` |

Arm 1, first try: the model ignored the malformed instruction. `builder-L1.md` held `## Status` `done`, `## Changes`, `## Checks`, and a `## Notes` saying it did not follow the override because its role instructions fix the final message format. run.sh printed the result path and exited 0, and `steps.py next` printed `verify L1`. Per the step's rule this try was rerun once with a stronger instruction.

Arm 1, malformed rerun: `builder-L1-2.md` is exactly:

```
<!-- role=builder level=L1 model=sonnet effort=low -->
## Changes
greet.sh: echo hello world
```

run.sh exit 3, with the one stderr line in the table and nothing on stdout. The result file and its `runs.jsonl` line (`"file":"builder-L1-2.md"`) were both kept. `steps.py next .sdlc/t/step-1` printed `rebuild L1`, then `reason: builder-L1-2.md has no done/blocked under ## Status; not counted as a fail, rerun the builder at the same level` and `read: .sdlc/t/step-1/builder-L1-2.md`. The pipeline did not advance to verify.

Arm 2, structural: `steps.py next .sdlc/t2/step-1` printed `invalid result: .sdlc/t2/step-1/builder-L1.md: first line is not a <!-- role=<r> level=<L> model=<m> effort=<e> --> header`, then `reason: the newest result does not match its results.py schema; stop and ask the user`. Neither `verify` nor `rebuild` was printed.

Arm 3, normal: `builder-L1.md` held `## Status` `done`, `## Changes`, `## Checks`, and `## Notes` `None`. run.sh exit 0, stdout the result path, stderr empty. `steps.py next .sdlc/t3/step-1` printed `verify L1`, then `reason: no verifier result; build L1 -> verifier L1`. `bash greet.sh` printed `hello world`.

## Limits

- The Codex backend arm is unverified: no `SDLC_BACKEND=codex` run was made, so the result check after a Codex role run is not shown live.
- It is one model at one level: builder L1 on `claude-sonnet-5-5` at effort low, one trial per arm on one machine and one account. No verifier, plan-reviewer, planner, or other role result was checked live.
- The malformed arm needed the stronger instruction; on the first try the model kept `## Status` and the run passed the check, which is the correct outcome for a well-formed result. The malformed result was produced by the model under instruction, not by a natural failure.
- The structural arm is a hand-made copy of a live result with its header line removed; no live run wrote a headerless result, since run.sh always writes the header.
- The live run used the uncommitted T-0184 working tree on top of `f45649e`; the script hashes above bind the evidence to the files that ran.
