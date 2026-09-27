<!-- role=filer level=L1 model=sonnet effort=medium -->
All steps: single step, builder done, verifier pass, gates green. No warnings.

## Warnings
None

## PR title
T-0120: block-publish.sh scans raw command when an interpreter's inline-code flag follows a value-taking option

## PR body
### Summary
`hooks/block-publish.sh` masked away publish calls hidden inside interpreter inline code (`python3 -c`, `node -e`, etc.) whenever the inline-code flag was preceded by an option that takes its own separate value word, such as `python3 -X dev -c` or `node --require x -e`. The masker's option-run regex only accepted dash-prefixed words before the flag, so the separate value word (`dev`, `x`) broke the match and the command fell back to the masked scan, letting a publish call slip through inside a role run.

### Changes
- `plugins/sdlc-lite/hooks/block-publish.sh`: replaced the single `OPTS` regex with a per-interpreter `VALOPTS` list (python: `-X`, `-W`, `--check-hash-based-pycs`; node: `-r`/`--require`, `--import`, `--loader`/`--experimental-loader`, `-C`/`--conditions`, `--input-type`, `--title`, and other `--flag value` options; perl: `-I`, `-M`, `-m`, `-x`; ruby: `-I`, `-r`, `-C`, `-E`, `-x`, `-W`) and an `opts(name)` builder, so an interpreter's inline-code flag is matched even when preceded by one of these options and its value word. A non-option word (a script path) still ends the option run, keeping `python3 scripts/check.py -c "..."` on the masked scan. Attached forms (`-Xdev`, `--require=x`), short-option clusters, path-qualified interpreters, and quoted interpreter mentions are unchanged. Header comment updated to describe the rule, citing `python3 -X dev -c`.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: added 5 blocked fixtures (`python3 -X dev -c`, `python3 -W ignore -c`, `node --require x -e`, `perl -I lib -e`, `ruby -I lib -e`) and 2 allowed guard fixtures (`python3 -X dev scripts/check.py`, `python3 scripts/check.py -c`).
- `CLAUDE.md`: extended the `hooks/block-publish.sh` bullet to note that value-taking options before the inline-code flag still count, citing `python3 -X dev -c`.

### Verification
- Builder (L2, opus) ran all 5 blocked-case criteria (exit 2 each), both allowed guard criteria (exit 0 each), extra probes (`-Xdev`, `--require=x`, `ruby -E`), all 4 grep criteria, and the full `hook-selftest.sh` and `check.sh` gates: all green.
- Verifier (L1, sonnet) independently reran every criterion in the built tree (all pass) and confirmed check-bites: in a throwaway worktree at the pre-build commit, the same blocked-exit and grep criteria went red (old code let the command through / new fixtures/text absent), proving the criteria actually discriminate the change. Verdict: pass.
- Out-of-scope check: only the three named files were touched; unrelated untracked SDLC process artifacts were confirmed as normal trail, not scope creep.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `block-publish.sh` now scans the raw command for interpreter inline code even when a value-taking option (`python3 -X dev -c`, `node --require x -e`, `perl -I lib -e`, `ruby -I lib -e`, etc.) comes before the inline-code flag, closing a gap where a publish call could hide there.

## Follow-ups
- The node, perl, and ruby value-option lists are best-effort (the builder did not cross-check against `node --help` or the perl/ruby docs) and python/node option sets can change across versions; an unlisted value-taking option before the inline-code flag still falls back to the masked scan and could let a publish call through.
