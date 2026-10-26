# Prompt given: "connect Figma to Claude Code"

The figma-bridge in `tools/figma-bridge/` is already up and connected. I checked port 8934 before doing anything, found it already bound, and did not start a second server or touch the running process.

Current status, read from what's already running (not started by me):

- Server: `node --experimental-strip-types src/server.ts` (PID 97887), listening on `https://127.0.0.1:8934` with TLS on, using the mkcert certs in `tools/figma-bridge/certs/`.
- Tunnel: `ngrok http https://127.0.0.1:8934 --verify-upstream-tls=false` (PID 97967), current public URL `https://<FIGMA_BRIDGE_TUNNEL_URL>` (from ngrok's local API at `127.0.0.1:4040`).
- Auth token, from the server's own startup log at `./figma-bridge-server.log`: `<FIGMA_BRIDGE_TOKEN>`.
- This isn't a fresh setup, it's already been exercised end to end about half an hour ago: `data/inbox.jsonl` has a `"hi"` from the Figma side at 23:53:13 UTC, and `data/replies.jsonl` shows a Claude Code reply, "hi back from Claude Code, the bridge works", at 23:53:18 UTC.

What I just did: subscribed this session to the live event feed at `wss://127.0.0.1:8934/events`, authenticating with the token as the WebSocket subprotocol (`bridge-token.<token>`), same as the README's own worked example. Any new `send_message` call from the Figma Agent will now show up here as a live notification, no polling needed.

If you need the connector details again, for pointing Figma's own custom MCP connector at this bridge, or re-checking it on another machine:

- MCP server URL: `https://<FIGMA_BRIDGE_TUNNEL_URL>/mcp`
- Header: `Authorization: Bearer <FIGMA_BRIDGE_TOKEN>`

To send a reply back to the Figma Agent from here:

```
curl -X POST https://127.0.0.1:8934/reply \
  -H 'content-type: application/json' \
  -H 'Authorization: Bearer <FIGMA_BRIDGE_TOKEN>' \
  -d '{"text":"..."}'
```

Two things worth flagging:

- That ngrok URL and token are live secrets for as long as this process keeps running. Don't paste them anywhere public. A restart with no `FIGMA_BRIDGE_TOKEN` set mints a brand new token and invalidates this one everywhere, including whatever Figma has saved in its connector form.
- I didn't modify any files in the repo and didn't stop or restart the server or tunnel.

I can send a test message through `/reply` to double check the round trip still works, or walk through restarting the bridge fresh if you want a new token or tunnel URL.
