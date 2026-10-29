#!/bin/bash
set -u
R=/Users/kimba/Projects/ultimate-tokens-color-science; F=$R.worktrees/fanout; I=$F/integration
S=/Users/kimba/.claude/plugins/cache/sdlc-lite/sdlc-lite/0.37.0/scripts
LOCK=/private/tmp/claude-501/-Users-kimba-Projects-ultimate-tokens-color-science/de5167ec-ebf4-4d6e-8a3c-797bfa42b23e/scratchpad/land.lock
mkdir -p "$(dirname $LOCK)"; until mkdir $LOCK 2>/dev/null; do sleep 15; done
trap 'rmdir $LOCK 2>/dev/null' EXIT
while pgrep -f "[f]anout.py land" >/dev/null; do sleep 15; done
PORT=$(python3 -c 'import socket;s=socket.socket();s.bind(("",0));print(s.getsockname()[1])')
echo "== app dev check on $(git -C $I rev-parse --short HEAD) port $PORT"
( cd $I && nice -n 10 node packages/ui/testing/app-shell-dev-check.ts --port $PORT ) || { echo "DEVCHECK FAILED"; exit 3; }
G1='{ [ "$(shasum package-lock.json)" = "$(cat node_modules/.lock.sha 2>/dev/null)" ] || { npm ci --no-audit --no-fund && shasum package-lock.json > node_modules/.lock.sha; }; } && SKILL_VALIDATION_PYTHON='$R'/tmp/skillvenv/bin/python nice -n 10 npm run check'
G2='nice -n 10 node --test --test-concurrency=4 resources/corpus/computation/test/*.test.js && VITEST_BROWSERS=chromium,webkit NODE_OPTIONS=--max-old-space-size=4096 nice -n 10 npx vitest run --maxWorkers=4'
cd $R
echo "== settle"
python3 $S/fanout.py settle fanout/2026-10-21 --forward --force --lanes-dir $F --gate "$G1" --gate "$G2"
rc=$?; echo "SETTLE rc=$rc main=$(git rev-parse --short main)"; exit $rc
