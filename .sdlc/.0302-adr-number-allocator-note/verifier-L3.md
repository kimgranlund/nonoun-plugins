<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
pass

## Criteria
- `grep -q '^## Numbered records across worktrees (ADR numbers)' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: ran in the built tree, exit=0; heading at plugins/sdlc-lite/skills/handoff-format/SKILL.md:189. Bites: same command in a throwaway worktree at base 7a9633d6, exit=1.
- `awk '/^## Numbered records across worktrees/{f=1;next} /^## /{f=0} f' plugins/sdlc-lite/skills/handoff-format/SKILL.md | grep -q 'git worktree list'`: pass. Evidence: exit=0; the section body line 4 reads "The next number is the highest across every `git worktree list` tree and the integration branch, plus one." Bites: at base the awk body is empty, grep exit=1.
- `! git diff --name-only HEAD | grep -v -E '^(...allowlist...)$' | grep -q .`: pass. Evidence: exit=0; `git diff --name-only HEAD` lists only handoff.md, SKILL.md, and sdlc-planner-l1/l2/l3.toml. Bites: in the throwaway worktree with README.md touched the same command exits 1.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: output "Codex agent definitions verified", exit=0. Bites: at clean base (no edits) it exits 2 with "generated agent drift: .../sdlc-planner-l1.toml", so the gate was red before this build and the regeneration in this tree repaired it.
- `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: "ok: 19 role levels, 9 agents checked", exit=0. Bites: in the throwaway worktree with `guard timeout:` altered in handoff-format SKILL.md it printed "FAIL skills/handoff-format/SKILL.md: spec gate text missing" and exited 1.
- `python3 scripts/check-packaging.py`: pass. Evidence: "PASS: catalog parity, identity, skill routes, hook isolation and context links", exit=0. Bites: in the throwaway worktree with the sdlc-lite entry renamed in .claude-plugin/marketplace.json it printed "FAIL: catalogs must contain both peer plugins" and exited 1 (an added stray key and a version change did not bite; the plugin name is the biting variable).
- `git diff --check`: pass. Evidence: exit=0 with no output. Bites: trailing whitespace appended to README.md in the throwaway worktree gave "README.md:27: trailing whitespace." exit=2.

Builder claims: no builder-*.md exists (solo lane per skips.md), so every claim above is from my own runs. Prose in the new note checked at source: `tickets.py new` stamps above the max across every `git worktree list` tree (plugins/sdlc-lite/scripts/tickets.py:161-162, worktree_pairs at :480-506, :839-856) and `tickets.py check` reports "duplicate id" (:168, :990), so both references the note makes hold. Steelman on the only candidate fail (the planner TOML diff is not the ADR note): the handoff allowlist names those three files, `generate --check` was red at base, and the inserted text is planner.md rule 15 already at HEAD:46, so the regeneration is a correct repair the step allowed; dropped as a fail.

## Out of scope changes
plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l{1,2,3}.toml: the only change is an inserted planner rule 15 ("Never delete anything...") that merge 5dc65fa8 added to agents/planner.md without regenerating; handoff-format is embedded in no TOML (grep for the new heading in adapters/codex/agents/*.toml matches nothing). Within the handoff allowlist and a correct repair of an inherited drift, so not a defect; a sibling lane that also regenerates these TOMLs will merge identically. Untracked .sdlc/0302-adr-number-allocator-note/{base-sha,skips.md,verifier-L3.attempt.json} are runner bookkeeping, not step output.

## For the next attempt
None
