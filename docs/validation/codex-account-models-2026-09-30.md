# Codex account discovery and independent verifier

Recorded 2026-09-30 on macOS with the existing ChatGPT Pro login. Maintenance base: `0ff454e`, branch `codex-scout-astra`.

CLI 0.159.2 lists and successfully runs `gpt-6.1-sol`, `gpt-6-sol`, and `gpt-6-luna`. The final mapping preserves every existing Astra role default and pairs `gpt-6-astra` builders with `gpt-6.1-sol` verifiers. The local config's original `gpt-6.1-sol` default now completes a turn without a model override.

## Discovery and exact available IDs

Started `codex app-server --listen stdio://`, initialized its RPC protocol, read `account/read`, and queried `model/list` with `includeHidden: true, limit: 100`. The account was `chatgpt`, plan `pro`; the updated catalog returned ten models with no pagination cursor. The matching model cache was fetched at `2026-09-30T13:35:38.174615Z` for CLI 0.159.2.

A catalog alone does not prove access: [OpenAI's model discovery guidance](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference) distinguishes listing from completed inference. Every exact ID below then completed a fresh `codex exec` turn, exit 0, with exactly `MODEL_PROBE_OK`. The [catalog](codex-account-models-2026-09-30/cli-0.159.2/catalog.json) and [probe summaries](codex-account-models-2026-09-30/cli-0.159.2/probes.json) retain evidence without credentials or account identifiers.

| Exact ID | Visibility | Advertised reasoning efforts | Live probe |
| --- | --- | --- | --- |
| `gpt-6.1-sol` | visible, catalog default | low, medium, high, xhigh, max, ultra | completed |
| `gpt-6-astra` | visible | low, medium, high, xhigh, max, ultra | completed |
| `gpt-6-sol` | visible | low, medium, high, xhigh, max, ultra | completed |
| `gpt-6-luna` | visible | low, medium, high, xhigh, max | completed |
| `gpt-5.6-sol` | visible | low, medium, high, xhigh, max, ultra | completed |
| `gpt-5.6-terra` | visible | low, medium, high, xhigh, max, ultra | completed |
| `gpt-5.6-luna` | visible | low, medium, high, xhigh, max | completed |
| `gpt-5.5` | visible | low, medium, high, xhigh | completed |
| `gpt-reserve` | hidden | low, medium, high, xhigh, max | completed |
| `codex-auto-review` | hidden, automatic approval review | low, medium, high, xhigh, max | completed |

Hidden entries were not selected as pipeline defaults. Successful short probes establish access for those requests, not suitability for ordinary roles. The catalog says `gpt-5.5` retires October 14, 2026 and points to `gpt-5.6-sol`.

For every listed ID, matching catalog metadata advertises a 272,000-token context window, 95% effective context (258,400 tokens), text/image inputs, and a 10,000-token tool-output truncation policy. That truncation value is not a generated-output cap. No per-model RPM, TPM, message allowance, or maximum generated-output limit was exposed. Priority/fast service tiers are advertised but were not exercised. The availability probes used effort low; the config-default probe used high, and the verifier trial below uses medium.

`account/rateLimits/read` on 0.159.2 returned one shared `codex` bucket: ordinary usage allowed, 82% used in a 10,080-minute (seven-day) window, resetting October 5, 2026 at 3:33:27 p.m. America/Los_Angeles. No secondary window, individual limit, or model-specific bucket was returned. Credits were present and not unlimited. This is an observed usage snapshot, not a guaranteed future allowance or per-model quota.

The availability command, run for each exact catalog ID, was:

```sh
codex exec --ephemeral --json --color never --sandbox read-only \
  -C /tmp/sdlc-codex-account-20260930/cli-0.159.2/project -m '<exact-id>' \
  -c 'model_reasoning_effort="low"' -c 'approval_policy="never"' \
  -c 'agents.enabled=false' \
  -c 'developer_instructions="Model availability probe. Reply with exactly MODEL_PROBE_OK. Do not call tools."' \
  'Reply with exactly MODEL_PROBE_OK. Do not call tools.'
```

These are model-access probes, not replacements for pipeline roles.

## Why the earlier results differed

Before the user updated the CLI during this session, 0.154.0 returned only seven entries: the five older visible models and two hidden entries. All seven completed turns; it was already incorrect to conclude that only Astra worked. Exact `gpt-5.6-sol`/`gpt-5.6-luna` IDs differ from several spellings in the earlier supplied probes.

On 0.154.0, fresh probes of `gpt-6.1-sol`, `gpt-6-sol`, and `gpt-6-luna` all failed with HTTP 400, "not supported when using Codex with a ChatGPT account." After the update, `codex --version` reported 0.159.2, all three appeared in the new catalog, and all three completed live turns. This is a before/after observation; it does not isolate client-version gating from a simultaneous server-side rollout.

The [earlier catalog](codex-account-models-2026-09-30/cli-0.154.0/catalog.json), [probes](codex-account-models-2026-09-30/cli-0.154.0/probes.json), and first role trial are retained separately. That trial selected Astra low for builder L1 and 5.6 Sol medium for verifier L1; both attempts completed, the builder reported done, and the verifier passed. The verifier had already finished when cancellation was considered, so no signal was sent and no interruption was fabricated. Its review binds to the interim 5.6 Sol alternate, not the final 6.1 Sol mapping.

## Final maintenance and local config

- `plugins/sdlc-lite/adapters/codex/models.json` now maps `gpt-6-astra` to `gpt-6.1-sol` in `verifier_alternates`. Every existing role model/effort remains unchanged, including scout L1 Astra high. The final role mapping uses 6.0/6.1 throughout.
- Regenerated the three alternate verifier profiles: L1 medium, L2/L3 high. There are 22 generated profiles in total; base profiles and shared role contracts remain unchanged.
- Isolated the empty-alternate fixture from shipped defaults. The runner regression tests both empty and configured alternate maps, actual CLI selection, result headers and `runs.jsonl` sharing/model fields.
- Updated the current execution guide's agent count, scout row and alternate explanation. Historical dated observations remain historical.
- `scripts/run.sh`, Claude models, and Claude efforts are unchanged.

The original `~/.codex/config.toml` named `gpt-6.1-sol` at high effort. It failed on 0.154.0, was temporarily changed to the proven Astra ID, then restored to `gpt-6.1-sol` after the CLI update. A fresh 0.159.2 turn without `-m` completed on the restored default; its [retained completion summary](codex-account-models-2026-09-30/cli-0.159.2/config-default.json) records the absence of model/effort overrides. Each model edit preserved all other then-current TOML settings; the concurrently changed `projects` table was preserved. There is no remaining default-model change to this file and no machine-local config in the Git commit. The original backup is `/tmp/sdlc-codex-account-20260930/config.toml.before`, mode 0600.

## Final live role trial

The final throwaway project is `/tmp/sdlc-codex-account-20260930/cli-0.159.2/project`: an initial Git commit, a small `AGENTS.md`, ignored `.sdlc/`/`.worktrees/`, and `value.txt` initially containing `value: 1` with a newline. The handoff requests exactly `value: 2` with a newline and independent semantic review of the final external maintenance diff. Both roles use fresh CLI contexts through the actual runner.

The unrestricted outer launcher explicitly uses standalone exec transport. The builder and verifier retain the generated workspace-write/read-only sandboxes and approval policy never. Native named-agent exchange was not used or tested. From the throwaway project:

```sh
SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=exec SDLC_CODEX_TIMEOUT_SECONDS=600 \
  SDLC_ROUTING_REASON='User-requested proof on updated CLI 0.159.2; L1 one-file fixture, preserve Astra 6.0 builder default' \
  /Users/kimgranlund/Projects/nonoun/sdlc-lite/plugins/sdlc-lite/scripts/run.sh \
  builder L1 .sdlc/model-pair/step-1/handoff.md

SDLC_BACKEND=codex SDLC_CODEX_TRANSPORT=exec SDLC_CODEX_TIMEOUT_SECONDS=600 \
  SDLC_ROUTING_REASON='User-requested final independent verifier on CLI 0.159.2; prefer working 6.1 Sol paired with Astra 6.0 builder' \
  /Users/kimgranlund/Projects/nonoun/sdlc-lite/plugins/sdlc-lite/scripts/run.sh \
  verifier L1 .sdlc/model-pair/step-1/handoff.md
```

The first 6.1 Sol verifier accepted the fixture, mapping, generated profiles, model evidence, test coverage, and unchanged runner, but returned Verdict fail for one stale sentence in the execution guide: “the defaults configure none.” That sentence was corrected to distinguish the earlier native smoke test from the current configured alternate. The first report and its completed attempt remain retained; a completed runtime attempt is not a passed verification. A fresh verifier rerun passed after independently assessing the correction and the full maintenance scope.

| Attempt | Attempt ID | Recorded model / effort | Runtime / role outcome |
| --- | --- | --- | --- |
| [builder-L1](codex-account-models-2026-09-30/cli-0.159.2/builder-L1.attempt.json) | `796caccdd3464e869ee59677e80f6274` | `gpt-6-astra` / low | completed / done |
| [verifier-L1](codex-account-models-2026-09-30/cli-0.159.2/verifier-L1.attempt.json) | `2bc313dbe8ed4cffba8612f95c1c3779` | `gpt-6.1-sol` / medium | completed / fail |
| [verifier-L1-2](codex-account-models-2026-09-30/cli-0.159.2/verifier-L1-2.attempt.json) | `d970b7aaf4d44a088b14d455a9e9d182` | `gpt-6.1-sol` / medium | completed / pass |

All three final-trial attempts used backend `codex`, transport `exec`, and exit 0. Both verifier run records have `shared_with_builder: false`; the first verifier’s fail is an accepted report, not a transport failure. See the [run records](codex-account-models-2026-09-30/cli-0.159.2/runs.jsonl), [builder report](codex-account-models-2026-09-30/cli-0.159.2/builder-L1.md), [final verifier report](codex-account-models-2026-09-30/cli-0.159.2/verifier-L1-2.md), and [handoff](codex-account-models-2026-09-30/cli-0.159.2/handoff.md). The [material hashes after correction](codex-account-models-2026-09-30/cli-0.159.2/reviewed-material-after-correction.json) were checked unchanged after the review. The final reports do not claim model-quality equivalence.

## Verification and boundaries

The first selftest run failed two assumptions that the shipped alternate map must be empty. After fixture isolation, all 20 tests passed, and they passed again after switching the alternate to 6.1 Sol. In an owned temporary plugin copy, deliberately disabling alternate selection made the runner regression fail: expected `model=fixture-alt`, observed `model=gpt-6-astra`, exit 1. The positive case and observed negative control are distinct from live inference evidence.

Also passed locally: `codex_roles.py generate --check`, `scripts/check-packaging.py`, `plugins/sdlc-lite/scripts/check.py` (18 role levels, eight agents), exec readiness, and `git diff --check`. No CI-authoritative gate result was observed or claimed.

Not established: API-key account access, other accounts/hosts, native named-agent transport, maximum context/output capacity, every advertised effort/service tier, or comparative verifier quality. Runner records establish requested model IDs and accepted reports; raw completion events do not independently expose server model identity. This is one account and one machine, not broad model qualification.

## Handoff

Commit on `codex-scout-astra` with Codex attribution; no push or PR. Durable catalog/probe/role evidence is retained beside this report. The two task-owned temporary projects and raw transcripts are under `/tmp/sdlc-codex-account-20260930`; all required runs have finished and no role remains active. Future model changes should repeat account discovery and completed inference, preserve the user's 6.1/6.0 preference, and retain a different verifier model from the builder.
