<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/validation/supervisor-live-run/probe.py`: added the `runs_git_push` shlex classifier, with `PUSH_RE` kept only as its fallback for an unbalanced quote. Added `install_pre_push`, called in `setup()` right after `git remote add`, which writes the hook and sets an absolute `core.hooksPath`. Also added `pre_push_calls`, the new `push_attempt(logs, hook_calls, remote_added, remote)`, `host_final` and `no_push_basis`. The oracle's wake and attached rule now runs on the no-push basis. Added the new evidence lines and facts keys and updated the docstring. The stub's `result` event now carries a `\u2014` escape. The new selftest cases are wired in.
- `docs/validation/supervisor-live-run/AGENTS.md`: added the pre-push hook sentence to the `probe.py` item.
- `docs/ticket-stages/watcher-design.md`: in section 9, added the "records its no-push basis" item right after the `- a message-body arm:` item.

## Checks
- `python3 docs/validation/supervisor-live-run/probe.py selftest`: all 17 labels printed `ok:`, then `probe selftest: PASS` (about 15 s).
- Acceptance criterion 1 (selftest, no stray `.sdlc/supervisor`, all 17 labels): exit 0.
- Acceptance criterion 2 (greps on probe.py, BODY line, no `run.sh`, no em dash): exit 0.
- Acceptance criterion 3 (AGENTS.md `pre-push`, section 9 "records its no-push basis"): exit 0.
- Guard (diff and untracked file allowlist against `$SDLC_BASE_SHA`): exit 0.
- Em dash count in AGENTS.md and watcher-design.md: 0 and 0. `git diff --check`: clean.
- Ad hoc negative controls, run in-process by importing probe and not saved anywhere:
  - The old `PUSH_RE` matches the first run's reply command; `runs_git_push` returns False for it.
  - The unbalanced-quote fallback returns True.
  - With `install_pre_push` stubbed out, `pre_push_calls` is `[]` and the Codex-shaped push log classifies as `absent`, so the hook case depends on the hook.

## Notes
- `claude_push` now reports an attempt when a `permission_denials` Bash entry runs a push, even with no matching tool use. Before, it returned `attempted=False` with `denied=True`, which meant `absent`.
- The command-word skip loops: it repeats over `NAME=value` words, the wrapper words (by basename), and the options after a wrapper, so `env FOO=1 git push` is also caught.
- A `sh -c` recursion past depth 3 returns False.
- The selftest's except list gains `subprocess.SubprocessError`, so a timeout in the hook case reports FAIL instead of a traceback.
- One of my Bash calls was blocked by `block-publish.sh` because a throwaway snippet contained the push phrase. I reran it without the phrase; no file was affected.
