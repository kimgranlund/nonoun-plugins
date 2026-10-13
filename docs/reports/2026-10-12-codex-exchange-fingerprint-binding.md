# Codex exchange profile fingerprint binding (T-0507)

Date: 2026-10-12. Host: Claude Code on macOS. Base commit: `07a5c289`. The change is uncommitted in the lane tree at the time of these runs.

## What changed

Each native request file now carries `profile_fingerprint`, the binding captured at dispatch. `codex_exchange.py` refuses a normal report whose first line is not `profile: <that binding>`, and the waiting runner checks a response against the same stored value. `--failed` needs no profile line. The request file and the `runs.jsonl` line record `profile_fingerprint` and `profile_check`.

## Scope of this evidence

Everything below ran offline: a real waiter process (`codex_exchange.wait_for_agent`) and the `codex_exchange.py` command line, with a fixture report in place of a Codex role.

Unverified: the ticket's criterion 7, a fresh callable named-agent Codex run. It cannot run on this Claude host without nesting a CLI. No step in this ticket proves live Codex behavior. The check also reads a fingerprint the role reports about itself, so a passing final report does not prove the role checked before it edited.

## Baseline: the three tests against the unchanged exchange

Run in step 1 with the new tests in place and `codex_exchange.py` still at the base commit: exit 1.

```
FFF
FAIL: test_native_exchange_enforces_the_dispatched_profile_binding (__main__.CodexTests)
    self.assertEqual(done.returncode,2,f'a report with a {label} profile line must be refused: {done.stderr}')
AssertionError: 0 != 2 : a report with a missing profile line must be refused:

FAIL: test_native_exchange_binding_survives_profile_change_after_dispatch (__main__.CodexTests)
    self.assertEqual(done.returncode,2,'the live fingerprint is not the dispatched binding: '+done.stderr)
AssertionError: 0 != 2 : the live fingerprint is not the dispatched binding:

FAIL: test_native_exchange_failed_response_needs_no_profile_line (__main__.CodexTests)
    self.assertEqual(final.get('error'),'native agent reported failure: '+reason)
AssertionError: None != 'native agent reported failure: could not finish: the fixture tool is missing'

Ran 3 tests in 1.548s
FAILED (failures=3)
```

After the change the same three tests pass (step 1: `Ran 3 tests in 2.116s`, `OK`).

## The five cases, run by hand after the change

Setup: a scout L1 waiter started in a temporary directory, as the selftest starts it:

```
python3 -c 'import sys;sys.path.insert(0,sys.argv[1]);import codex_roles,codex_exchange
if sys.argv[4]:codex_roles.fingerprint=lambda agent:sys.argv[4]
sys.exit(codex_exchange.wait_for_agent("scout","L1","Read seed",sys.argv[3],"low",sys.argv[2],60.0))' \
  plugins/sdlc-lite/scripts <tmp>/<name>.request.json <scout L1 model from models.json> "<override>"
```

`<override>` is empty except in the changed-after-dispatch case, where it is `0.0.0+dispatched`: the waiter process then binds that value at dispatch while the responder process computes the live fingerprint. The responder is `python3 plugins/sdlc-lite/scripts/codex_exchange.py <request.json> <report-file> [--failed]`. The report body is a valid scout report. The live fingerprint was `0.22.5+e27be4736593` (`python3 plugins/sdlc-lite/scripts/codex_roles.py fingerprint sdlc-scout-l1`, after the profiles were regenerated in step 2).

| Case | First line of the report | Responder | Request file afterwards |
|---|---|---|---|
| Missing | none | exit 2, no response file | `status: waiting`, binding unchanged |
| Stale | `profile: 0.0.0+stale` | exit 2, no response file | `status: waiting`, binding unchanged |
| Current | `profile: 0.22.5+e27be4736593` | exit 0, waiter exit 0 | `status: received`, `profile_check: ready` |
| Changed after dispatch | `profile: 0.22.5+e27be4736593`, waiter bound to `0.0.0+dispatched` | exit 2 | `status: waiting`, `profile_fingerprint: 0.0.0+dispatched` |
| `--failed` | none | exit 0, waiter exit 1 | `status: failed`, `profile_check: not-checked` |

Refusal messages on stderr:

- Missing: `live freshness unknown: sdlc-scout-l1 stated no loaded profile fingerprint. Handshake required: ask it to reply with the first line `profile: 0.22.5+e27be4736593` before it edits; do not accept edits or claim ready.`
- Stale: `refused: sdlc-scout-l1 loaded profile 0.0.0+stale, the attempt binding is 0.22.5+e27be4736593. Start a fresh Codex session (installing does not change a running session), then rerun preflight and the handshake; accept no edits from this run.`
- Changed after dispatch: `refused: sdlc-scout-l1 loaded profile 0.22.5+e27be4736593, the attempt binding is 0.0.0+dispatched. Start a fresh Codex session (installing does not change a running session), then rerun preflight and the handshake; accept no edits from this run.`

Further results:

- Current: the waiter's result event held `is_error: false`, `profile_fingerprint: 0.22.5+e27be4736593`, `profile_check: ready`.
- Changed after dispatch: the same request then accepted `profile: 0.0.0+dispatched` (exit 0, waiter exit 0, `status: received`, `profile_check: ready`). The request accepts the binding it was dispatched with, not the fingerprint the responder computes.
- `--failed`: the request recorded `error: native agent reported failure: could not finish: the fixture tool is missing`.

## Gates

- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0, `Codex agent definitions verified`.
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: exit 0.
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: exit 0, `Ran 6 tests`, `OK`.
- `python3 scripts/check-packaging.py`: exit 0, `PASS: catalog parity, identity, skill routes, hook isolation and context links`.
- `git diff --check 07a5c289 -- plugins docs`: exit 0.
- `git diff --quiet 07a5c289 -- docs/reports/2026-10-12-sdlc-lite-astra-review docs/reports/2026-10-12-sdlc-lite-astra-review.md`: exit 0.

The full `check.sh` suite was not run here; it belongs to the land gate.
