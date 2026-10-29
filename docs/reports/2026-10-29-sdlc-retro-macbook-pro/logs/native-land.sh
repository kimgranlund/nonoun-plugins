#!/bin/bash
# usage: native-land.sh lane:ticket:lanekind ...   sync then land, one at a time (native sdlc-lite 0.33.0)
set -u
R=/Users/kimba/Projects/ultimate-tokens-color-science; F=$R.worktrees/fanout; I=fanout/2026-10-21
S=/Users/kimba/.claude/plugins/cache/sdlc-lite/sdlc-lite/0.37.0/scripts; V=$R/tmp/skillvenv/bin/python
REGEN="npm run -s build:ui-tokens && npm run -s build:ui-components && npm run -s build:ui-catalog && node scripts/build-export-identity.ts"
G1="{ [ \"\$(shasum package-lock.json)\" = \"\$(cat node_modules/.lock.sha 2>/dev/null)\" ] || { npm ci --no-audit --no-fund && shasum package-lock.json > node_modules/.lock.sha; }; } && SKILL_VALIDATION_PYTHON=$V nice -n 10 npm run check"
G2="nice -n 10 node --test --test-concurrency=4 resources/corpus/computation/test/*.test.js && NODE_OPTIONS=--max-old-space-size=4096 nice -n 10 npx vitest run --maxWorkers=4"
for spec in "$@"; do
  IFS=: read -r lane ticket kind <<<"$spec"
  cd $F/$lane || { echo "NOLANE $lane"; continue; }
  git checkout -q -- .claude/settings.local.json 2>/dev/null
  if [ -n "$(git status --porcelain -- . ':!.claude/settings.local.json')" ]; then git add -A -- . ':!.claude/settings.local.json'; git commit -q -m "$ticket: lane build" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"; echo "COMMITTED $lane"; fi
  base=$(python3 -c "import json;print(json.load(open('.lane.json'))['base'])")
  echo "== sync $lane"; python3 $S/fanout.py sync $F/$lane --lanes-dir $F --regen "$REGEN" 2>&1 | tail -4
  rc=${PIPESTATUS[0]}; if [ $rc -ne 0 ]; then echo "SYNC-STOP $lane rc=$rc"; cd $R; continue; fi
  node scripts/build-export-identity.ts >/dev/null 2>&1; git add src/application/export-implementation.js; git diff --cached --quiet || git commit -q -m "$ticket: regenerate export identity after sync"
  # sdlc-lite #59: drop open folders of tickets already closed on integration
  for d in $(git ls-tree -d --name-only HEAD docs/tickets/ | grep -E '^docs/tickets/[0-9]'); do b=${d#docs/tickets/}; git cat-file -e "$I:docs/tickets/.$b" 2>/dev/null && git rm -rq "$d" && echo "STALE removed $d"; done
  git diff --cached --quiet || git commit -q -m "$ticket: drop open folders of tickets closed on integration"
  cd $R
  echo "== land $lane"; python3 $S/fanout.py land fanout/2026-10-21-$lane --ticket $ticket --lane $kind --integration $I --lanes-dir $F --base $base --gate "$G1" --gate "$G2" 2>&1 | tail -4
  echo "LAND-RC $lane ${PIPESTATUS[0]}"
  git -C $R status --short
done
