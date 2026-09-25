<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0022: tickets.py roadmap honors numbered mode and refuses on the prefix/id rule

## PR body
### Summary
`tickets.py roadmap` used to call `problems(ts)` without numbered mode. With `ticket_folders: numbered` set, it could rebuild `roadmap.md` while `check` failed on the NNNN-/id prefix rule. Now `roadmap` runs the same check as `check`, so the two commands agree on what a valid ticket set is. Follow-up from T-0016.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `cmd_roadmap(root, numbered=False)` uses `numbered or config_numbered(root)` and passes it to `problems`.
  - `run` forwards `kw` to `cmd_roadmap`.
  - The `roadmap` subparser gains `--numbered`.
  - The docstring usage now reads `roadmap [--numbered]`.
  - `selftest` adds four roadmap cases: refusal via the flag, refusal via config, plain `roadmap` still succeeding on the mismatched set, and a matching `0001-alpha` set passing `roadmap --numbered`.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: the argument-hint is now `roadmap [--numbered]`, and the numbered-mode bullet now covers `roadmap`.
- `CLAUDE.md`: in the tickets.py bullet, the flag list now includes `roadmap`, and it notes that `roadmap` refuses on a prefix mismatch in numbered mode.
- Unchanged:
  - Plain-slug mode.
  - The roadmap output format and `write_roadmap`.
  - `.claude/agents/sdlc-lite-author.md`, which has no numbered or roadmap line.

### Verification
Verifier L1 returned pass on every criterion.
- `tickets.py selftest` exits 0.
- Manual temp-root check with `alpha` renamed to `0005-alpha`:
  - `roadmap --numbered` exits 1 with `0005-alpha: folder prefix 0005- does not match id 'T-0001' (want T-0005)` and `roadmap not written`, and the roadmap.md md5 is unchanged.
  - The config line gives the same refusal.
  - With the config line removed, plain `roadmap` exits 0.
- `grep "roadmap \[--numbered\]"` matches `tickets.py:5` and `SKILL.md:4`.
- The diff does not touch `write_roadmap` or the roadmap output text.
- `scripts/check.sh` exits 0 (selftests, shellcheck, plugin validate).
- Negative control (revert to `problems(ts)`):
  - The builder saw both new refusal cases fail.
  - The verifier's rerun from a /tmp copy crashed with FileNotFoundError instead of showing a clean failure, so its confirmation is weak.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: `tickets.py roadmap` now follows numbered mode (`--numbered` or `ticket_folders: numbered` in config). It refuses to write the roadmap on a folder prefix/id mismatch, matching `check`.

## Follow-ups
- tickets.py selftest crashes with FileNotFoundError when run from a copy outside the plugin dir, so negative controls from a temp copy cannot show clean per-case failures
- tickets.py selftest pass output does not list individual expectations, so a verifier cannot confirm which cases ran without reading the diff
