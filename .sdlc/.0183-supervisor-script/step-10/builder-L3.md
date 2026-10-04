<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/supervisor.py`: `wake_prompt` gains one sentence. It names `<scripts_dir()>/messages.py` as the only script, says not to search for it, and lists `count`, `list`, `read`, `reply`, `ack` as `python3 <path> <command> ...`. Both hosts get the same prompt.
  - Updated the module docstring (D4) and the woken-host bullet in the init AGENTS.md text to match.
  - Selftest: `st_prompt` is now `st_prompt(h, receiver, n)` and writes the path out itself; a new helper `st_script(h)`; all five callers updated.
  - Selftest: new failure constant `NO_SCRIPT_PATH`, new patch `CTL_PATHLESS_PROMPT`, and a new case `codex prompt names the absolute script path and no message text` with its negative control run inside the case via `st_control`.
- `docs/validation/supervisor-live-run.md`: new section `## Codex wake arm after the prompt fix` placed before Limits. Small edits to the intro sentence and two Limits bullets, which had said no arm was rerun and `supervisor.py` was not changed.
- `docs/validation/supervisor-live-run/AGENTS.md`: one new bullet listing `codex-rerun-<N>.txt`.
- `docs/README.md`: the T-0183 line now ends "...and three Codex wake reruns after a prompt fix; Claude Code pass, Codex pass. Codex wake arm after the fix: 3 of 3 passed."
- `docs/validation/supervisor-live-run/codex-rerun-1.txt`, `codex-rerun-2.txt`, `codex-rerun-3.txt`: new evidence, written only by `tee`.

## Checks
- `command -v codex && codex login status`: `Logged in using ChatGPT`, exit 0 (pre-flight, not an arm).
- `python3 plugins/sdlc-lite/scripts/supervisor.py selftest`: every case `ok`, including `ok: codex prompt names the absolute script path and no message text`; prints `supervisor selftest: PASS`.
- `python3 docs/validation/supervisor-live-run/probe.py selftest`: `probe selftest: PASS`.
- Rerun 1, `set -o pipefail; python3 docs/validation/supervisor-live-run/probe.py codex | tee docs/validation/supervisor-live-run/codex-rerun-1.txt`: `result=pass`, exit 0.
- Rerun 2, same command with `codex-rerun-2.txt`: `result=pass`, exit 0.
- Rerun 3, same command with `codex-rerun-3.txt`: `result=pass`, exit 0. k=3. No fourth run.
- Acceptance criteria, each run exactly as written in the handoff:
  - AC1 (selftest grep): PASS
  - AC2 (`wake_prompt` path and commands): PASS
  - Rerun 1, 2 and 3 last-line checks: PASS
  - k sentence in the record and the README (k=3): PASS
  - Known-limit conditional: PASS (it does not apply, since all three passed)
  - No-`Codex pass` conditional: PASS (it does not apply)
- Guards:
  - supervisor selftest: `supervisor selftest: PASS`
  - probe selftest: `probe selftest: PASS`
  - Em dash grep over the three files: PASS. `docs/validation/supervisor-live-run/AGENTS.md` also has 0.
  - Scope guard with `SDLC_BASE_SHA=3ac65cd`: no stray files; the changed set is exactly the 7 allowed paths.
- `git diff --check`: clean.

## Notes
- The other six arms (dry-run, claude, claude-attached, claude-push, codex-attached, codex-push) were not rerun on the fixed prompt, though Claude Code wakes now get the new sentence too.
  - The README's `Claude Code pass` and the codex-attached and codex-push parts of `Codex pass` follow the handoff's formula, using those arms' results from the old prompt.
  - The record's Limits section says this.
- All three reruns used the absolute path from the prompt, and every `messages.py` call exited 0. Each wake also ran `--help` for `list`, `reply` and `ack`. Rerun 1 also ran one `rg --files .sdlc/messages -g AGENTS.md` first.
- No `Known limit` line was written because k=3. A Limits bullet says three passes on one machine do not rule out the earlier variation.
- The record describes the pre-fix run as "its stream shows no command" instead of the handoff's "never ran a command". That matches the existing `### codex` section, which says the log cannot show whether any command ran.
- The probe kept its three throwaway repos and their wake logs under the system temp dir (`supervisor-live-1e4vpigz`, `-5fftr43f`, `-o5ffchzb`), as the probe is designed to. No git worktree was created.
