#!/bin/bash
# hidden check: run from the repo root of the worktree
set -e
grep -Eq 'scout:L1\)[[:space:]]+model=claude-haiku-4-5;[[:space:]]+effort=low' plugins/sdlc-lite/scripts/run.sh
grep -Fq '| scout | L1 | Haiku 4.5 low |' plugins/sdlc-lite/skills/level-rubric/SKILL.md
python3 plugins/sdlc-lite/scripts/check.py >/dev/null
python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check >/dev/null
echo PASS
