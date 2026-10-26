# intent — make-figma-agent-connector
status: shipped (2026-09-19), user scope ~/.claude/skills/
species: command
dials: { disable-model-invocation: true, user-invocable: true }
freedom: low
type: encoded-preference

## trigger
should:      ["/make-figma-connector-mcp", "connect Figma to Claude Code", "set up the figma bridge tunnel"]
should_not:  ["review the figma-bridge code", "add a new feature to figma-bridge"]

## delta
Without this skill, a fresh session (no memory of this build) has to re-derive the whole
sequence from tools/figma-bridge/README.md each time and gets Figma's connector-form details
wrong on the first pass — demonstrated live in this session: the MCP server URL was entered
without the required `/mcp` suffix (four requests landed on `/` and 404'd), then the
Authorization header value was entered without the `Bearer ` prefix. With the skill, one command
runs the setup, starts both processes, and prints the exact ready-to-paste values (URL with
`/mcp`, header with `Bearer <token>`) correctly the first time, and arms this session's own
Monitor subscription on `/events` so incoming Figma messages surface live with no extra step.

## fences
- NOT for reviewing or modifying tools/figma-bridge's own source (the code-review skill / a
  dispatched sdlc build-and-review cycle, per this repo's own governance)
- NOT for filing a new capability against figma-bridge (sdlc file-feature + dispatch-build, this
  repo's own ticket-and-worktree flow, e.g. issues #38/#44/#46/#47)

## assertions
1. Running the command starts tools/figma-bridge's server with TLS on (generating mkcert certs
   first if `tools/figma-bridge/certs/` is absent) and captures the printed AUTH TOKEN line.
2. It starts an ngrok tunnel against the local HTTPS server and captures the resulting public
   `https://*.ngrok-free.dev` (or `.app`) tunnel URL from ngrok's own local API.
3. It prints one ready-to-paste block naming exactly: the MCP server URL ending in `/mcp`, and
   the `Authorization` header value in the literal form `Bearer <token>` (no missing prefix, no
   missing path segment — the two failure modes observed live this session).
4. It arms a `Monitor({ws:{url: wss://127.0.0.1:<port>/events, protocols:["bridge-token.<token>"]}})`
   subscription in the CURRENT session (never forked to a subagent, since a fork's Monitor call
   would not persist after the fork ends) and confirms a live connection, not just an attempt.

## gates
P0 route:      PASS — procedure needed on demand (start the local MCP bridge server, start an ngrok tunnel, print the exact values for Figma's custom-connector form), with real side effects (background processes) and no single mechanical pass/fail check; not an always-true project fact; no tool-wall/parallelism/multi-skill-preload need identified yet, so not routed to an agent. Skill.
P1 intent:     PASS — all seven slots filled, user confirmed each (trigger phrasings, delta,
                species/dials, freedom/script, fences, assertions).
P2 evals:      PASS 2026-09-19 — trigger evals skipped (disable-model-invocation: true, user-only);
                5 behavioral assertions in evals/evals.json; 2 baseline outputs in evals/baseline/.
P3 draft:      PASS 2026-09-19 — SKILL.md (command skeleton, both dials explicit, 50 lines) +
                scripts/start-bridge.sh.
P4 language:   PASS 2026-09-19 — body imperative throughout; audit R-rows all PASS, one
                describer (exit-3 log-path claim) rewritten.
P5 validate:   PASS 2026-09-19 — skill_lint clean; fresh-context skill-checker audit PASS
                (evals/audit-report.md, 0 blocking; F2/F3/F4/F8 fixed, F1 fixed, F5-F7 nits
                accepted); assertions demonstrated live: cold start 1s (server detached via
                setsid), reuse path prints "reusing it" twice and starts nothing, URL ends /mcp,
                header value "Bearer <48 hex>", unauthenticated /mcp -> 401, and a message sent
                through /mcp arrived in the calling session via its Monitor /events
                subscription. Fence closure: both NOT-clauses name plugin skills (code-review,
                sdlc file-feature/dispatch-build) whose evals are not editable from user scope;
                this skill is user-only so no routing leak is possible.

## findings accepted with note
- F5-F7 (nits): cosmetic wording; left as is.
- Bug found live during P5: backgrounding server/ngrok with plain `nohup ... &` left them in
  the script's process group, so a harness Bash call waited on them indefinitely (first run
  stalled >2 min after the script itself had finished). Fixed with `detach()` (perl POSIX::setsid).

## rulings
Seed: "make-figma-agent-connector with the system we just built" (tools/figma-bridge/, built across issues #38/#44/#46/#47 this session: MCP server, mkcert HTTPS/WSS, required token auth, ngrok tunnel workflow).

Design ruling (not user-asked, derived from mechanics): this skill must NOT run with
`context: fork`. The whole point of the skill is that the CURRENT interactive session ends up
with a live `Monitor(ws:...)` subscription so future Figma messages surface to the person actually
talking to Claude; a forked subagent's tool calls do not leave a standing subscription behind in
the parent session once the fork ends. So the shell setup (certs/server/tunnel) is bundled as a
script, but the SKILL.md body runs inline and its LAST step is the Monitor call itself, executed
by the main session, not delegated.

ngrok's own one-time account/authtoken step (`ngrok config add-authtoken <token>`) cannot be
scripted around — it requires a human to sign up at ngrok.com themselves (account creation is
outside what Claude may do on a user's behalf). The script checks `ngrok config check` first and
stops with the exact sign-up/authtoken instructions if it's not yet configured, rather than
failing opaquely.
