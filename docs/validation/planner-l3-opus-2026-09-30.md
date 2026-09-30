# Planner L3 on Opus xhigh (2026-09-30)

## Decision

On 2026-09-30 the user moved Claude planner L3 (cross-cutting plans and every replan) from Fable xhigh to Opus xhigh, to fit the Claude table to the Max plan. The Codex planner L3 (`gpt-6-astra` high) does not change.

## Basis

Recorded cost from `runs.jsonl` across this repository's `.sdlc/` folders, at list price, with bench runs and lane worktrees excluded:

- About 900 recorded role runs (912 when counted); Fable was about 44 of them (5%).
- Fable was about $164 of $537 (31%) of recorded cost. These totals are approximate: the verifier reproduced them only to within about 1% from a later tree.
- Planner L3 was the largest Fable item: 18 runs, about $103.

## Consequence

The plan-reviewer never runs on the planner's model family. With planner L2 and L3 both on Opus, a review of a plan by planner L2 or L3 now runs on Fable high; only a plan by the Sonnet planner L1 is reviewed on Opus high. Some Fable spend therefore moves from planner to reviewer rather than disappearing.

## Limits

The quality of Opus xhigh plans against Fable plans is not measured.

## Live check after the change

Same day, same machine and login (Claude Code 2.1.285, Max), a throwaway Git project with a one-line `greet.sh` and a one-paragraph goal, through the changed runner:

| Run | Header | Only model in the transcript | Recorded cost |
| --- | --- | --- | --- |
| planner L3 | `model=opus effort=xhigh` | `claude-opus-5-5` | $0.97 |
| plan-reviewer L1 (after that plan) | `model=fable effort=high` | `claude-fable-5-1` | $1.35 |

The reviewer's verdict was `pass`. This is one run on a deliberately tiny task: it shows which model answered and that the family rule moved the review to Fable, not what real planner L3 runs cost or how good Opus xhigh plans are. The earlier planner L3 figures in this note came from real replans of this repository and are not comparable.
