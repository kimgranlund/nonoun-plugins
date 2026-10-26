---
name: make-figma-agent-connector
description: >-
  Brings up the local figma-bridge (tools/figma-bridge) end to end and hands back the exact
  values for Figma's custom MCP connector form: starts the mkcert-TLS server and an ngrok
  tunnel (reusing either if already live), prints the MCP server URL with its /mcp suffix
  and the Authorization value with its Bearer prefix, then subscribes the current session to
  the bridge's /events feed. Asks for nothing unless ngrok has no account configured.
disable-model-invocation: true
user-invocable: true
argument-hint: "[--domain reserved.ngrok-free.app]"
allowed-tools: Bash(bash *), Bash(curl *), Bash(lsof *), Monitor
---

# /make-figma-agent-connector

Runs the bridge setup script, prints the connector values, and arms this session's own live
subscription. The human chose the timing; proceed without re-asking why. Seed: `$ARGUMENTS`

## Preconditions
- Run from inside a repo that carries `tools/figma-bridge/` (or export `FIGMA_BRIDGE_DIR`).
  Missing → say where the bridge was looked for; stop.
- `$ARGUMENTS` carrying `--domain <name>` → export `FIGMA_BRIDGE_TUNNEL_DOMAIN=<name>` for
  the script call below.

## Workflow
1. Run `bash ${CLAUDE_PLUGIN_ROOT}/skills/make-figma-agent-connector/scripts/start-bridge.sh` inline (a
   Bash call from this session, never delegated to a sub-agent or fork). The script is
   idempotent: a server already bound to the port and a tunnel already forwarding to it are
   reused, never duplicated. Exit codes:
   - `2`: ngrok has no authtoken. Relay the script's sign-up steps verbatim; stop. Account
     creation is the human's own step.
   - `3`/`4`: relay the one-line reason verbatim (a `4` also names a log path); stop.
2. Copy the `=== Figma custom connector ===` block into the reply byte for byte. The two
   values that were entered wrong before this skill existed are the URL's trailing `/mcp`
   and the header value's leading `Bearer `; both come straight from the script, so never
   retype them from memory.
3. Execute the `Monitor({ ws: ... })` line the script printed, in THIS session. A fork's
   subscription ends with the fork, which is the whole reason this step is inline.
4. Confirm the subscription connected (the tool result reports an open connection, not an
   attempt). A TLS or handshake failure → the certs were issued after the server started or
   the token changed; re-run step 1 and retry once.

## Report
Three lines: the connector block (URL, header name, header value), the Monitor status
(connected, plus port), and the two log paths; a fourth relaying the script's unreserved-
hostname note whenever it printed one (a tunnel restart then means recreating the connector). Token and URL are live secrets: they appear
in this reply only, never in a commit, ticket, or shared doc.

Done when Figma's form has been given `<tunnel>/mcp` and `Bearer <token>`, and this session
holds an open `/events` subscription.
