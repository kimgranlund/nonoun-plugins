<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1 (selftest, no stray `.sdlc/supervisor`, 17 labels): pass. Evidence: I ran the full command. The selftest exited 0 and printed `ok:` for every one of the 17 labels, then `probe selftest: PASS` as the last line. The mailbox-supervisor folder was unchanged (`nostray1`) and `.sdlc/supervisor` does not exist (`nostray2`). A second selftest run left the `supervisor-live-*` temp-dir count at 7 before and after, so it leaks no temp dirs.
  - The check bites. In mutated copies of `probe.py` under `$SDLC_TMP_WORKTREES`, the selftest went red each time:
    - `runs_git_push` replaced by `PUSH_RE.search`: `FAIL: classify: a quoted push in a reply is no attempt: runs_git_push is true for 'S="<scripts>/messages.py"; ID=...'`.
    - `install_pre_push` removed from `setup()`: `FAIL: classify: a hook-recorded push ...: pre_push_calls gave []`.
    - The `denied` hook branch in `push_attempt` disabled: `FAIL: classify: a hook-recorded push ...: ... gave unclassified, not denied`.
    - The "declined with no host words" oracle rule disabled: `FAIL: fail: a declined push with no host words: ... gave result=pass`.
    - `push_attempt` changed to ignore hook calls: `FAIL: classify: a hook-recorded push ...: ... gave absent, not denied`.
  - So `runs_git_push`, the hook install, the hook-based `denied` branch, the `declined` oracle rule, and the hook-aware `absent` check each have a case that goes red.
- Criterion 2 (greps on `probe.py`): pass. Evidence: I ran the full command and it exited 0 (`c2=0`). It covers `core.hooksPath`, `pre-push`, `pre_push_calls=`, `no_push_basis=`, `host_final=`, the exact `BODY` line, no `run.sh`, and no em dash. The `BODY` and `run.sh` conjuncts are unchanged from before and existed to guard against regression. The new-behavior greps are backed by the mutation runs above and by the selftest assertions on the emitted lines, `pre_push_calls=0`, `no_push_basis=denied` and `host_final="stub handled the mail \u2014 no push"` (`probe.py` lines 959-960, 976-977).
- Criterion 3 (`AGENTS.md` and `watcher-design.md`): pass. Evidence: the command exited 0 (`c3=0`). The new item is at `watcher-design.md` line 302, directly after the `- a message-body arm:` item at line 301. The `AGENTS.md` `probe.py` item carries the pre-push hook sentence.
- (guard) allowlist of changed and untracked files: pass. Evidence: the command exited 0 (`guard=0`). `git status` shows only the allowed paths changed or untracked outside `.sdlc`.
- Spec fidelity beyond the criteria: pass. Evidence: I read `probe.py` lines 193-247 and 408-600. `runs_git_push` implements the shlex split with punctuation characters, `NAME=` skipping, the wrappers, the `sh -c` recursion capped at depth 3, git option skipping with `-C`/`-c` argument words, and the `PUSH_RE` fallback on `ValueError`. `install_pre_push` writes a 0755 hook and sets an absolute `core.hooksPath`. `push_attempt` follows the specified order. `host_final`, `no_push_basis` and the oracle rules match the spec. An ad hoc run gave True for `env FOO=1 git push`, `nohup git push &`, `(git push)`, `git --no-pager push` and a nested `bash -c`, and False for `git commit -m "x" ; git status`.
- No em dash: pass. Evidence: `grep -c` for the em-dash bytes in both docs gave 0 and 0, `probe.py` is covered by criterion 2, and `git diff --check` was clean. The `\u2014` escape appears in the source as an escape, at lines 875 and 960.
- Builder claims: accepted. The 17 labels and the guard I re-ran myself. The negative-control claim I re-ran differently, with mutated copies rather than a stub.

## Out of scope changes
None. The tracked changes (`docs/README.md`, `docs/ticket-stages/watcher-design.md`, `docs/validation/idle-host-watcher-design-review.md`, `plugins/sdlc-lite/scripts/check.sh`) and the untracked `probe.py`, `AGENTS.md`, `supervisor.py` and `supervisor-live-run.md` all pass the guard's allowlist. They come from earlier steps or this step's own targets.

## For the next attempt
None. Steelman pass: I drafted "the hook case runs real git, so it may be flaky or depend on the environment". A selftest run took about 15 s, the hook case passed in every run, and the global `core.hooksPath` is bypassed by the absolute path. I dropped the finding.
