---
id: T-0077
title: "block-publish.sh matches publish commands inside heredoc and file..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0065
---

## Goal
Inside a role run, `hooks/block-publish.sh` blocks only commands that would actually publish, so a Bash call that merely writes or edits text containing a publish phrase (a heredoc body into a file, a quoted argument to `sed`, `python3 -c`, `printf`, `grep`, a commit message) is no longer blocked, while every real publish, including one fed to a shell, stays blocked.

## Intent
Literal ask: block-publish.sh matches publish commands inside heredoc and file text, not only real commands; a builder's Bash edit containing "git push" was blocked in T-0065.
Deltas:
- Which text is inert: defaulted: heredoc bodies and single- or double-quoted string contents are data, not commands, unless they are handed to a shell or evaluator.
- What stays blocked (hidden scope, safety): defaulted: fail closed. A heredoc or quoted string fed to a shell or evaluator (`bash`, `sh`, `zsh`, `eval`, `bash -c "..."`, `sh -c '...'`, `xargs`, `ssh`, `env`, a pipe into `bash`/`sh`) is still scanned; command substitution `$(...)` and backticks inside double quotes are still scanned; unquoted publish commands anywhere in a pipeline, list, or subshell are still blocked. When the hook cannot tell, it blocks.
- Threat model: defaulted: the hook guards a well-meaning model against accidental publishing, not an adversary; it need not defeat deliberate obfuscation, but must not lose any case it blocks today that is a real publish.
- Done-condition missing: defaulted: selftest cases below.
Do: change `plugins/sdlc-lite/hooks/block-publish.sh` to mask heredoc bodies and quoted string contents before matching, except where they feed a shell or evaluator; add cases to `plugins/sdlc-lite/scripts/hook-selftest.sh` for both directions; update any doc line that describes the hook's matching (CLAUDE.md Layout entry, `.claude/agents/sdlc-lite-author.md` if it describes it).
Non-goals: guarding the user's own session; blocking a custom `--driver` script's direct pushes; changing the list of publish commands.
Done when: `scripts/hook-selftest.sh` and `scripts/check.sh` pass, and the selftest proves: (allowed, exit 0 with SDLC_ROLE set) `cat > f <<'EOF'` with a body line `git push origin main`; `sed -i 's/x/git push/' f`; `python3 -c 'print("gh pr create")'`; `git commit -m "doc: never git push"`; `grep -n "npm publish" f`; (blocked, exit 2) plain `git push origin main`; `cd x && git push`; `bash -c "git push"`; `sh -c 'gh pr create'`; `bash <<EOF` with body `git push`; `echo "$(git push)"`; `eval "git push"`; `gh api -X POST repos/o/r/issues`; `npm publish`.

## Context
Follow-up from T-0065 (fanout-py-s-default-lane/filer-L1.md):

block-publish.sh matches publish commands inside heredoc and file text, not only real commands: a builder's Bash edit whose text contained "git push" was blocked in T-0065, and the builder had to work around it with a temp script.

## Constraints
Every real publish the hook blocks today stays blocked. The hook stays a dependency-light bash script (bash, jq, grep, sed, awk; python3 is allowed if already a plugin dependency). Its exit contract (0 allow, 2 block, stderr message) does not change.
