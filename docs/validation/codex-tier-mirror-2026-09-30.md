# Codex tier mirror check

Recorded 2026-09-30 on macOS, Codex CLI 0.159.2, the maintainer's ChatGPT Pro login. Checks the mapping in `plugins/sdlc-lite/adapters/codex/models.json` after the user mirrored the Claude tiers: Opus to `gpt-6.1-sol`, Fable to `gpt-6-astra`, Sonnet to `gpt-6-luna`, Haiku to `gpt-5.6-terra`, with the Claude effort.

## Every model and effort pair

Each distinct pair in the mapping completed a fresh `codex exec --ephemeral --json --sandbox read-only -m <model> -c model_reasoning_effort="<effort>"` turn that answered `OK`: `gpt-6-luna` low, medium, high; `gpt-6.1-sol` low, medium, high, xhigh; `gpt-6-astra` medium, high, xhigh; `gpt-5.6-terra` low. A first attempt at this check returned no answers for every pair because the shell loop passed "model effort" as one argument; the corrected loop is the one recorded here.

## Runner check

In a throwaway Git project with a one-line fixture, `SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=exec run.sh builder L1` and then `run.sh verifier L1` both exited 0.

| Attempt | Recorded model / effort | `shared_with_builder` | Outcome |
| --- | --- | --- | --- |
| builder L1 | `gpt-6-luna` / low | false | done, fixture changed as requested |
| verifier L1 | `gpt-6.1-sol` / medium | false | pass |

The verifier's mapped model is `gpt-6-luna`, the builder's model, so `verifier_alternates` moved it to `gpt-6.1-sol`. That is the Claude rule (a Sonnet build is verified on Opus) expressed on Codex.

## Limits

One account, one machine, one fixture. Short probes establish that each pair is accepted, not that the tiers are equivalent in quality. Native named-agent transport was not exercised.
