## Task goal
Plugin maintainers and the author agent default to the cheapest lane that still passes independent verification, and record why a ticket needs more.

## Step 1: Add the philosophy line, the lane rule, and the builder completion line
level: L2

### Read first
- plugins/sdlc-lite/AGENTS.md (the file you edit; read its first 12 lines)
- docs/lean-sdlc/design.md section "1. Lean chain" for the wording to link, not copy

### Do
Make the smallest change that meets the criteria. No refactors, no extra tests, no doc edits outside this step. Report blocked instead of looping.
1. In plugins/sdlc-lite/AGENTS.md, add as the first guidance line, quoted exactly: "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction." (above `Read [repository guidance]`, after the title).
2. In the same file under "Contracts and routing", add one short rule: prefer the lean lane or /fix for plugin work; run the full chain only with a stated reason (an L4 or L5 step, a merge step, cross-cutting scope, a security-sensitive change) and record the reason in the ticket. Link docs/lean-sdlc/design.md, do not copy it.
3. In plugins/sdlc-lite/agents/builder.md, add one completion line: finish the step with the smallest change that meets the criteria; no refactors, extra tests, or doc edits outside the step; report blocked instead of looping.
4. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` so the Codex builder agents match.

### Acceptance criteria
- `grep -c "Done is better than perfect. Trust that modern, advanced models are very capable if given useful context and instruction." plugins/sdlc-lite/AGENTS.md | grep -qx 1`
- `grep -q "docs/lean-sdlc/design.md" plugins/sdlc-lite/AGENTS.md`
- `grep -q "smallest change that meets the criteria" plugins/sdlc-lite/agents/builder.md`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 scripts/check-packaging.py`
- `bash plugins/sdlc-lite/scripts/check.sh`
- `git diff --check main -- plugins docs`
