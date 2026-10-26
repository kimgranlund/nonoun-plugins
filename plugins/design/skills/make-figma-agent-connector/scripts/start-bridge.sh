#!/usr/bin/env bash
# Starts (or reuses) the figma-bridge server and its ngrok tunnel, then prints the exact
# values Figma's custom-connector form needs. Idempotent: a bridge already listening on the
# port and a tunnel already forwarding to it are reused, never duplicated.
#
# Env: FIGMA_BRIDGE_DIR (default <git root>/tools/figma-bridge), FIGMA_BRIDGE_PORT (8934),
#      FIGMA_BRIDGE_TOKEN (pins the token across restarts), FIGMA_BRIDGE_TUNNEL_DOMAIN
#      (a reserved ngrok domain; without it the hostname changes on every tunnel restart).
# Exit: 0 ready; 2 ngrok account/authtoken not configured; 3 bridge dir/tooling missing;
#       4 server or tunnel did not come up within the wait window.
set -euo pipefail

PORT="${FIGMA_BRIDGE_PORT:-8934}"
STATE="${HOME}/.cache/figma-bridge"
mkdir -p "$STATE"
SERVER_LOG="$STATE/server.log"
TUNNEL_LOG="$STATE/tunnel.log"

fail() { echo "start-bridge: $2" >&2; exit "$1"; }
# Run a long-lived process in its own session (setsid), fully detached from this script.
detach() { perl -MPOSIX -e 'POSIX::setsid(); exec @ARGV or die "exec: $!"' -- "$@" & }

# 1. Locate the bridge.
if [ -z "${FIGMA_BRIDGE_DIR:-}" ]; then
  ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  FIGMA_BRIDGE_DIR="${ROOT}/tools/figma-bridge"
fi
[ -f "$FIGMA_BRIDGE_DIR/package.json" ] || fail 3 "no figma-bridge at $FIGMA_BRIDGE_DIR (set FIGMA_BRIDGE_DIR)"
command -v node >/dev/null || fail 3 "node is not on PATH"
command -v ngrok >/dev/null || fail 3 "ngrok is not on PATH (brew install ngrok)"

# 2. ngrok account: a human step, never scripted around.
if ! ngrok config check >/dev/null 2>&1; then
  cat >&2 <<'MSG'
start-bridge: ngrok has no authtoken configured. One-time human step:
  1. Sign up at https://dashboard.ngrok.com/signup (free tier is enough).
  2. Copy the authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
  3. Run: ngrok config add-authtoken <that token>
  Then re-run this script.
MSG
  exit 2
fi

# 3. TLS certs (mkcert) and dependencies.
if [ ! -f "$FIGMA_BRIDGE_DIR/certs/cert.pem" ] || [ ! -f "$FIGMA_BRIDGE_DIR/certs/key.pem" ]; then
  command -v mkcert >/dev/null || fail 3 "mkcert is not on PATH (brew install mkcert), needed to issue certs"
  echo "start-bridge: issuing mkcert certs..."
  (cd "$FIGMA_BRIDGE_DIR" && npm run --silent setup-tls)
fi
[ -d "$FIGMA_BRIDGE_DIR/node_modules" ] || (cd "$FIGMA_BRIDGE_DIR" && npm ci --silent)

# 4. Server: reuse if the port is bound, else start and wait for the AUTH TOKEN line.
TOKEN=""
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "start-bridge: bridge already listening on 127.0.0.1:$PORT, reusing it"
  TOKEN="${FIGMA_BRIDGE_TOKEN:-$(grep -o 'AUTH TOKEN (required on every request): [0-9a-f]*' "$SERVER_LOG" 2>/dev/null | tail -1 | awk '{print $NF}' || true)}"
  [ -n "$TOKEN" ] || fail 4 "server is up but its token is not recoverable from $SERVER_LOG; stop it and re-run, or set FIGMA_BRIDGE_TOKEN"
else
  : > "$SERVER_LOG"
  # detach() puts the child in its own session so a harness waiting on this script's
  # process group (or its stdout pipe) returns as soon as the script itself exits.
  (cd "$FIGMA_BRIDGE_DIR" && detach npm run --silent start <"/dev/null" >"$SERVER_LOG" 2>&1)
  for _ in $(seq 1 40); do
    TOKEN="$(grep -o 'AUTH TOKEN (required on every request): [0-9a-f]*' "$SERVER_LOG" 2>/dev/null | tail -1 | awk '{print $NF}' || true)"
    [ -n "$TOKEN" ] && break
    if grep -q 'HTTPS/WSS is expected' "$SERVER_LOG" 2>/dev/null; then fail 4 "server refused to start (TLS certs), see $SERVER_LOG"; fi
    sleep 0.5
  done
  [ -n "$TOKEN" ] || fail 4 "server printed no AUTH TOKEN within 20s, see $SERVER_LOG"
  echo "start-bridge: server up on https://127.0.0.1:$PORT"
fi

# 5. Tunnel: reuse an ngrok tunnel already forwarding to this port, else start one.
API="http://127.0.0.1:4040/api/tunnels"
# The public_url of the tunnel whose OWN addr is this port (a real JSON parse: a second,
# unrelated ngrok tunnel must never have its URL handed to Figma as this bridge's).
find_url() {
  curl -s --max-time 5 "$API" 2>/dev/null | node -e '
    let d=""; process.stdin.on("data",c=>d+=c).on("end",()=>{
      try { const t=(JSON.parse(d).tunnels||[]).find(t=>t.proto==="https"&&t.config&&t.config.addr==="https://127.0.0.1:"+process.argv[1]);
            if(t) process.stdout.write(t.public_url); } catch(e){} });' "$PORT"
}
addr_ok() { [ -n "$(find_url)" ]; }
URL=""
if addr_ok; then
  URL="$(find_url)"
  echo "start-bridge: ngrok tunnel already forwarding to :$PORT, reusing it"
else
  : > "$TUNNEL_LOG"
  if [ -n "${FIGMA_BRIDGE_TUNNEL_DOMAIN:-}" ]; then
    detach ngrok http --domain="$FIGMA_BRIDGE_TUNNEL_DOMAIN" "https://127.0.0.1:$PORT" --verify-upstream-tls=false --log=stdout <"/dev/null" >"$TUNNEL_LOG" 2>&1
  else
    detach ngrok http "https://127.0.0.1:$PORT" --verify-upstream-tls=false --log=stdout <"/dev/null" >"$TUNNEL_LOG" 2>&1
  fi
  for _ in $(seq 1 40); do
    if addr_ok; then URL="$(find_url)"; [ -n "$URL" ] && break; fi
    sleep 0.5
  done
  [ -n "$URL" ] || fail 4 "ngrok reported no tunnel within 20s, see $TUNNEL_LOG"
fi

# 6. Prove the path: tunnel -> bridge -> auth. Unauthenticated /mcp must be 401.
CODE="$(curl -s --max-time 15 -o /dev/null -w '%{http_code}' -X POST "$URL/mcp" -H 'content-type: application/json' -d '{}' || echo 000)"
[ "$CODE" = "401" ] || fail 4 "expected 401 from $URL/mcp without a token, got $CODE (tunnel not reaching the bridge?)"

cat <<OUT

=== Figma custom connector: paste exactly these ===
MCP server URL:      $URL/mcp
Additional header:   Authorization
Header value:        Bearer $TOKEN

=== This session's live feed (run in the CURRENT session, never a fork) ===
Monitor({ ws: { url: "wss://127.0.0.1:$PORT/events", protocols: ["bridge-token.$TOKEN"] } })

Logs: $SERVER_LOG, $TUNNEL_LOG
$( [ -z "${FIGMA_BRIDGE_TUNNEL_DOMAIN:-}" ] && echo "Note: unreserved ngrok hostname; a tunnel restart changes the URL and Figma's connector must be recreated (set FIGMA_BRIDGE_TUNNEL_DOMAIN to a reserved domain to avoid this)." )
OUT
