# Prompt given: "set up the figma bridge tunnel"

The figma-bridge server and its ngrok tunnel are both already running, so I didn't start new ones (starting another server would just fail on the bound port, and starting a second ngrok tunnel would leave you with two live URLs and no way to tell Figma which one is real). Here's what's actually live:

**Server** (`tools/figma-bridge`): `https://127.0.0.1:8934`, TLS on, PID 97887
**Tunnel** (ngrok): `https://<FIGMA_BRIDGE_TUNNEL_URL>` -> `https://127.0.0.1:8934`, PID 97967

I confirmed this isn't just two idle processes sitting around — I hit the tunnel's `/mcp` endpoint without a token and got `401` (proves ngrok is actually forwarding to the bridge and the auth middleware is enforcing), then hit it again with the token and got past auth (`400` on a bare `ping`, since that's not a real MCP handshake, but no longer a `401`). So the full path Figma -> ngrok -> bridge -> auth is live right now.

To wire this into Figma's custom connector form:

- **MCP server URL**: `https://<FIGMA_BRIDGE_TUNNEL_URL>/mcp`
- **Additional header**: `Authorization` / `Bearer <FIGMA_BRIDGE_TOKEN>`

That token was printed to the server's own console at startup; I recovered it from this machine's existing log of that startup rather than restarting the server to mint a new one (a restart with no `FIGMA_BRIDGE_TOKEN` pinned would have generated a fresh token and broken anything already configured against the old one). Treat it as a live secret — once tunneled, it's the only thing standing between the public internet and this bridge, so don't paste it anywhere public.

Two things worth flagging:

1. ngrok's free tier mints a new random subdomain every time the tunnel process restarts. If this ngrok instance ever gets killed and restarted, the URL above goes stale and Figma's connector config needs updating to match.
2. Same logic for the token: if the bridge server itself restarts without `FIGMA_BRIDGE_TOKEN` set in the environment, it mints a brand-new token and the one above stops working.

If you also want this session subscribed to live messages from the Figma agent, I can attach with:

```
Monitor({ ws: { url: "wss://127.0.0.1:8934/events", protocols: ["bridge-token.<FIGMA_BRIDGE_TOKEN>"] } })
```

Just say the word.
