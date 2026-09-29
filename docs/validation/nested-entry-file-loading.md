# Nested entry file loading

Recorded: 2026-09-29. Live probe for the [repository onboarding design](../repo-onboarding/design.md). One trial per arm.

## Environment

- Claude Code 2.1.284, headless `claude -p`, model `claude-fable-5-1`, tools limited to Read, user settings and plugins at their defaults.
- Codex CLI 0.154.0, headless `codex exec`, read-only sandbox, model `gpt-6-astra`. The default model `gpt-6-sol` and `gpt-6-luna` were rejected, see Limits.
- macOS, Darwin 25.6.0. Throwaway Git repositories in the session scratchpad. They are not kept in this repository.

## Method

Each file carried a unique canary string. The prompt told the model to read a fixed list of files and then report every canary present in its context. The transcript was checked to confirm that the model made only the listed Read calls, so any other canary reached it through host loading.

Controls:

- Positive: the canary in the root `CLAUDE.md` and the canaries in the files read had to be reported.
- Negative: a canary in `docs/topic-a/unread.md`, which was never read and is not an entry file, had to be absent.

Arms:

| Arm | Layout | Files read |
| --- | --- | --- |
| nested | Root `CLAUDE.md` with `@AGENTS.md`. `docs/` has `CLAUDE.md` with `@AGENTS.md`. `docs/topic-a/` and `.sdlc/` have `AGENTS.md` only. `docs/topic-b/` has `AGENTS.md` and a `CLAUDE.md` whose import sits between HTML comment markers. | One note in each topic folder and one handoff under `.sdlc/` |
| control | Root files only | Same |
| markers | Root files only, root import between HTML comment markers | Same |
| bridge | `docs/CLAUDE.md` holds `@../AGENTS.md`, `@topic-a/AGENTS.md`, and a backticked `@topic-b/AGENTS.md`. No topic folder has a `CLAUDE.md`. | `docs/index.md` only |

Every nested `AGENTS.md` was 25 lines and about 1,650 bytes.

## Results for Claude Code

| Question | Observed |
| --- | --- |
| Is a nested `CLAUDE.md` loaded when a file in its folder is read? | Yes, for `docs/` and `docs/topic-b/`. |
| Is a parent folder's `CLAUDE.md` loaded when a file in a child folder is read? | Yes. Reading a note in a topic folder loaded `docs/CLAUDE.md`. |
| Is a nested `AGENTS.md` loaded without a `CLAUDE.md` beside it? | No, for `docs/topic-a/` and `.sdlc/`. |
| Does `@AGENTS.md` work in a nested `CLAUDE.md`? | Yes. |
| Does the import work between HTML comment markers? | Yes, at the root and nested. |
| Is an import of a child folder's file deferred until that folder is touched? | No. `@topic-a/AGENTS.md` in `docs/CLAUDE.md` was loaded when only `docs/index.md` was read. |
| Is a backticked import evaluated? | No. |
| Negative control | The unread canary was absent in every arm. |

## Results for Codex

The nested and control layouts were reused. Codex read the files with `cat`.

| Arm | Working directory | Entry files loaded |
| --- | --- | --- |
| nested | Repository root | Root `AGENTS.md` only |
| nested | `docs/topic-a/` | Root, `docs/`, and `docs/topic-a/` `AGENTS.md` |
| control | Repository root | Root `AGENTS.md` only |

| Question | Observed |
| --- | --- |
| Is a nested `AGENTS.md` loaded when a file in its folder is read? | No. From the root, reading files in nested folders loaded no nested entry. |
| Are entries between the root and the working directory loaded? | Yes. |
| Is a sibling folder's entry loaded? | No. `docs/topic-b/` was absent when working in `docs/topic-a/`. |
| Is `CLAUDE.md` read? | No. Its canaries were absent in every arm. |
| Negative control | The unread canary was absent in every arm. |

## HTML comments

Added 2026-09-29, after the third design review. One project held a root `CLAUDE.md` and a root `AGENTS.md`, each with one canary inside an HTML comment and one in visible text. The `CLAUDE.md` imported the `AGENTS.md`. The session had no tools on Claude Code and ran no command on Codex.

| Host | Canary in a comment | Canary in visible text |
| --- | --- | --- |
| Claude Code, `CLAUDE.md` | Absent | Present |
| Claude Code, imported `AGENTS.md` | Absent | Present |
| Codex, `AGENTS.md` | Present | Present |

## Token cost

Claude Code:

| Arm | Turns | Total input tokens | Output tokens |
| --- | --- | --- | --- |
| nested | 4 | 90,699 | 1,167 |
| control | 4 | 89,115 | 607 |

Total input is the sum of uncached input, cache creation, and cache read over the run. The nested arm loaded four extra files (two `AGENTS.md`, two `CLAUDE.md`) and used 1,584 more input tokens. The arms also differed in output, and earlier output is sent back as input on later turns, so the difference is not purely the entry files. By size alone the four files are about 870 tokens at four bytes per token.

For Codex, the run started in `docs/topic-a/` used 43,356 input tokens and the run started at the root used 41,559. The difference of 1,797 covers two nested `AGENTS.md` files. Each run made one command call.

## Limits

- One trial per arm. No repeat runs, so variance is unknown.
- Results rely on the model reporting canaries. The negative control and the transcript check support the reports but the injected context was not inspected directly.
- A real role run uses `--agent`, a plugin directory, and more turns. Those were not part of this probe.
- `codex exec` rejected two models with status 400, for example: "The 'gpt-6-sol' model is not supported when using Codex with a ChatGPT account." `gpt-6-luna` failed the same way. `gpt-6-sol` is this machine's default and appears in SDLC Lite's Codex defaults. The probe used `gpt-6-astra`.
- How either host settles a conflict between a nested rule and a root rule was not tested.
