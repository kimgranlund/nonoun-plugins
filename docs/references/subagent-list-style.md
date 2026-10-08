# Sub-agent list style guide

Read when changing what `dispatch.py prepare`, `solo_run.py` or `fanout.py` print for an Agent spawn. It decides what a person sees in the host's background agent list, so a row can be told apart at a glance. Status: implemented by T-0363 in `dispatch.py` (`agent_name`, `list_title`, `list_description`), `solo_run.py` and `fanout.py`. The fanout lane name stays `T-NNNN-solo` because the host's worktree branch is `worktree-<name>`.

## What the list shows

Observed in a maison session on 2026-10-08 (Claude Code 2.1.294, terminal):

| Column | Source | Behavior |
|---|---|---|
| Left | the spawn `name` | cut at about 24 characters with an ellipsis |
| Middle | the first line of the spawn `prompt` | cut at about 50 characters; the `description` did not appear |
| Right | the host | `idle`, or elapsed time and tokens; not ours to change |

Finished agents collapse into one `N idle agents` row. Why the middle column shows the prompt and not the `description` is not established; the guide works from what was seen.

## Rules

1. The first 24 characters of `name` carry what differs between rows. Put the ticket number first, then the role and level, then the attempt: `0153-builder-L3`, `0153-builder-L3-2`, `0227-verifier-L2`. Long slugs go last, where cutting them costs nothing.
2. The first line of the prompt is a title, not a path: `T-0153 harness coverage | builder L3 | try 2`. At most 50 characters, ticket id first, no leading `Handoff:`.
3. The `Handoff: <path>` line stays in the prompt as its own line. `hooks/block-role-spawn.sh` accepts it on any line, so it moves to line 2.
4. The `description` repeats the title in 3 to 5 words. The host may show it somewhere other than this list.
5. A name is stable for one attempt. A retry adds `-2`, `-3` at the end so it survives the cut; it never renames the first attempt.
6. No dates, shas or absolute paths in the name or the first prompt line.

## Examples

| Today | Target |
|---|---|
| `builder-L3-0153-harness-cov…` | `0153-builder-L3` |
| `builder-L4-0153-harness-cov…` | `0153-builder-L4` |
| `Handoff: /Users/kimgranlund/Projects/maison/ui-kit…` | `T-0153 harness coverage \| builder L3 \| try 2` |
| `verifier-L3-verify-fix0213` | `verify-fix0213-verifier-L3` |

## Not ours to change

The right column, the `N idle agents` grouping, and the cut widths. Another host version may cut differently, so the rules above keep the useful part in front rather than depending on an exact width.

## Check for the implementing ticket

- A selftest that prints the name and the prompt's first line for two attempts of two tickets and asserts the first 24 characters of each name differ and each first line is at most 50 characters (observed failing first).
- `dispatch.py resume` finds an agent by its new name, and the spawn gate still accepts the prompt (`hook-selftest.sh`).
