<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -c "Done is better than perfect. ..." plugins/sdlc-lite/AGENTS.md | grep -qx 1`: pass. Evidence: the command printed `c1ok`. The diff shows the line placed after the title and above "Read [repository guidance]". At HEAD the same grep counts 0, so the check goes red before the change.
- `grep -q "docs/lean-sdlc/design.md" plugins/sdlc-lite/AGENTS.md`: pass. Evidence: printed `c2ok`. The diff adds the lane rule under "Contracts and routing". It links `../../docs/lean-sdlc/design.md` and does not copy it. The target file exists.
- `grep -q "smallest change that meets the criteria" plugins/sdlc-lite/agents/builder.md`: pass. Evidence: printed `c3ok`. The diff adds completion item 10.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: output "Codex agent definitions verified", exit 0. The five builder TOMLs (l1 to l5) each changed by one line, so the regenerated files match builder.md.
- `python3 scripts/check-packaging.py`: pass. Evidence: "PASS: catalog parity, identity, skill routes, hook isolation and context links", exit 0.
- `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0. The output ended with the selftests passing and "ok: plugin validate". Shellcheck was skipped because it is not installed.
- `git diff --check main -- plugins docs`: pass. Evidence: exit 0 with no output.

## Out of scope changes
None. The five `adapters/codex/agents/sdlc-builder-l*.toml` changes are the generated output required by Do step 4. The `.sdlc/.../step-1` files are run artifacts.

## For the next attempt
None
