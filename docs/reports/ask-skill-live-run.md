# Ask skill live run

Recorded: 2026-10-05. Ticket T-0231. Evidence is in [`ask-skill-live-run/`](ask-skill-live-run/). Every claim below names the file that shows it.

## What was run

Claude Code 2.1.289, model `claude-sonnet-5-5` (`*-meta.txt`), with `--plugin-dir` pointing at the `plugins/sdlc-lite` of this branch's worktree. A throwaway project built by [`setup.sh`](ask-skill-live-run/setup.sh) holds a `blocked` ticket with a `## Deferred` note (T-0002), a ticket whose step has a `fail` verifier result with a `## For the next attempt` section (T-0003), and an empty `.sdlc/notes.md`. [`run.sh`](ask-skill-live-run/run.sh) runs two turns in one session. Turn 1 states a weekly rate limit on the upload API and asks a delimiter question in plain text, with no answer given. Turn 2 is `/sdlc-lite:ask`.

The planted conversation items are therefore in a real earlier turn of the same session, not in the turn-2 prompt (`*-turn1-result.txt`).

## First run, before the fix

[`first-run-turn2-tools.txt`](ask-skill-live-run/first-run-turn2-tools.txt) shows one tool call, `ToolSearch` for `AskUserQuestion`. [`first-run-turn2-result.txt`](ask-skill-live-run/first-run-turn2-result.txt) shows two items, both from the conversation. It found neither the blocked ticket nor the failed verifier result, and it ran no search of the repo. It also said `AskUserQuestion` was unavailable and asked in plain text, which the skill did not then cover.

Two defects in the skill, both fixed in the same ticket: the sweep named places to look but no searches, and there was no fallback when `AskUserQuestion` is missing.

## Second run, after the fix

[`second-run-turn2-tools.txt`](ask-skill-live-run/second-run-turn2-tools.txt) shows three `Bash` calls, the first with the sweep searches (`grep -rl '^status: blocked'`, `grep -rl '^## Deferred'`, `grep -rn 'gap:'`, `cat .sdlc/notes.md`), then reads of the T-0002 handoff and of the T-0003 handoff and verifier result. [`second-run-turn2-result.txt`](ask-skill-live-run/second-run-turn2-result.txt) lists four items:

1. the unanswered delimiter question, with two options and a consequence each, and no recommendation;
2. the T-0003 retry-limit scope, cited to the failed verifier result, with two options;
3. the T-0002 column spec, cited to the `## Deferred` note, with the options `Write it in chat now`, create a small file under `docs/` to edit, and leave it blocked;
4. the weekly rate limit, with two options.

No option in that result is marked recommended, and item 1 says why. The result names no other plugin's skill (`grep -c 'harness:'` on the skill file is 0; the guard checks this).

## Limits

- **`AskUserQuestion` was not exercised.** Both runs' `*-meta.txt` show `AskUserQuestion_calls: 0`, because the tool is not available in headless `claude -p` (the first run's `ToolSearch` found nothing). So "one `AskUserQuestion` round of 1 to 4 questions" is unobserved. What was observed is the plain-text fallback, which asked four items in one message and ended its turn. The `AskUserQuestion` path rests on the skill text only.
- **Codex:** not run.
- **Recommendations:** the run does not show a recommendation ranked first where evidence exists, because no item in this fixture had a stated default.
- One session per run, one machine. Spend from the meta files: first run $0.1177 plus $0.2522, second run $0.1134 plus $0.2764.
- The rate-limit item is the model's reading of a statement in turn 1. Nothing checked an actual limit.
