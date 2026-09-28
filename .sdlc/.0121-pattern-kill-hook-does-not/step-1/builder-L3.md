<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-pattern-kill.sh`: added a second `assign` alternative. It matches `NAME=`, an optional `"`, then `$(` or a backtick whose body, up to the closing `)` or backtick, holds `pkill`, `killall`, or `kill` as a whole word. It uses the same boundaries as `word`/`wend`, and the body may start with the kill word. Its matches go through the existing `held_kill` sed extraction and the `$NAME`/`${NAME}` command-position check. The header comment now covers the `$(...)`/backtick substitution form. `strict`, the cheap exit, and `loose` are unchanged.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`:
  - The header clause now reads "a kill word held in a variable, also one assigned through a $(...) or backtick substitution".
  - 6 block fixtures added: `p=$(command -v pkill)`, `k=$(which killall)`, the backtick `command -v`, `echo find`, `compgen | grep | head`, and `k=$(command -v kill); $k $(pgrep ...)`.
  - 3 pass fixtures added: `cmd=$(command -v ls)`, its backtick form, and the single-quoted `echo '...'` mention.
- `CLAUDE.md`: the `hooks/block-pattern-kill.sh` Layout entry now names the `$(...)` or backtick substitution form with an example.
- `.claude/agents/sdlc-lite-author.md`: the kill-pattern hazard line gains "or through a substitution (`p=$(command -v pkill); $p x`)".

## Checks
- I ran all 16 acceptance criteria verbatim, via `eval` in a temporary script that I deleted afterwards. All passed: C1 to C4 (new block cases), C5 to C10 (guards), C11 (`bash plugins/sdlc-lite/scripts/hook-selftest.sh` printed "hook selftest: PASS"), C12 (the fixtures bite against the pre-step hook), and C13 to C16 (the doc greps).
- As a negative control, I ran the edited selftest against the HEAD hook. It fails with `block-pattern-kill blocks 'p=$(echo find pkill); $p x': exit 0, want 2`.
- `shellcheck -S warning` on both scripts: clean.

## Notes
- A substitution body is read only up to its first `)` or backtick. A kill word after a `)` inside a nested substitution is not seen by the new pattern, for example `k=$(basename $(x) kill)`. A nested substitution where the kill word comes before the first `)` is still matched.
- Any assignment through a substitution whose body holds `kill` as a whole word, and whose variable is then run as a command, is now blocked. That includes odd cases such as `r=$(kill 123); $r`.
- `.sdlc/0121-pattern-kill-hook-does-not/handoff.md` was already modified before this step, and I did not touch it.
