#!/usr/bin/env bash
# run.sh — launch the dev-factory dev-server from a persistent, sourced env instead of retyping the inline
# environment on every run. Copy `dev-factory.env.example` to a `dev-factory.env` in YOUR project (instance
# path + run knobs), then `./run.sh`. The .env is *operator config* — keep it in your project, never commit
# it into the plugin (the plugin must not hard-code your instance path or run policy).
#
# Resolution order for the env file: $DEV_FACTORY_ENV → ./dev-factory.env (CWD) → <instance>/run.env.
# Defaults below are the plugin's; your .env overrides them. Vars already exported in your shell win over both.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

set -a   # auto-export everything assigned or sourced below, so uvicorn inherits it

# 1. source the operator env, if present (first match wins)
ENV_FILE="${DEV_FACTORY_ENV:-}"
[ -z "$ENV_FILE" ] && [ -f "$PWD/dev-factory.env" ] && ENV_FILE="$PWD/dev-factory.env"
[ -z "$ENV_FILE" ] && [ -n "${DEV_FACTORY_DIR:-}" ] && [ -f "$DEV_FACTORY_DIR/run.env" ] && ENV_FILE="$DEV_FACTORY_DIR/run.env"
if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then echo "» env: $ENV_FILE"; . "$ENV_FILE"; else echo "» env: none (inline/defaults only)"; fi

# 2. defaults — the plugin supplies these; your .env / shell override them
: "${DEV_KERNEL_BIN:=$HERE/../dev-kernel/bin}"            # the vendored kernel bin, relative to this plugin
: "${HOST:=127.0.0.1}"
: "${PORT:=8731}"
: "${DEV_FACTORY_HEARTBEAT:=0}"                            # Crawl by default; set 1 to auto-dispatch (Walk)
[ "$DEV_FACTORY_HEARTBEAT" = "1" ] && : "${DEV_FACTORY_MAX_DISPATCHES:=6}"   # bound an armed loop (never unbounded)

set +a

# 3. the one thing the plugin can't default — your instance
if [ -z "${DEV_FACTORY_DIR:-}" ]; then
  echo "✗ DEV_FACTORY_DIR is unset — point it at your instance, e.g.:" >&2
  echo "    /path/to/your-project/.agents/dev-factory" >&2
  echo "  Set it in a dev-factory.env (copy dev-factory.env.example) or export it." >&2
  exit 2
fi
if [ ! -d "$DEV_FACTORY_DIR" ]; then
  echo "✗ DEV_FACTORY_DIR=$DEV_FACTORY_DIR does not exist — run /factory-init or 'lattice.py init' there first." >&2
  exit 2
fi

# 4. report the resolved config (the operator should see exactly what posture they're launching), then launch
adapter="${DEV_FACTORY_ADAPTER:-mock}"
hb="OFF (Crawl, human-driven)"
[ "$DEV_FACTORY_HEARTBEAT" = "1" ] && hb="ON (Walk · adapter=$adapter · cap ${DEV_FACTORY_MAX_DISPATCHES:-uncapped} dispatches)"
kit="${DEV_FACTORY_KIT:-}"; [ -z "$kit" ] && kit="none bound — REVIEW spec-quality gate needs a kit"
echo "» dev-factory @ http://$HOST:$PORT"
echo "    instance : $DEV_FACTORY_DIR"
echo "    kit      : $kit"
echo "    heartbeat: $hb"
if [ "$DEV_FACTORY_HEARTBEAT" = "1" ]; then
  if [ "$adapter" = "headless" ]; then
    echo "    ⚠ adapter=headless — the heartbeat dispatches LIVE 'claude' workers (real tokens, writes the worktree)."
  else
    echo "    · adapter=mock — the free deterministic loop (no tokens). Set DEV_FACTORY_ADAPTER=headless for real workers."
  fi
fi
cd "$HERE"
exec python3 -m uvicorn app:app --host "$HOST" --port "$PORT"
