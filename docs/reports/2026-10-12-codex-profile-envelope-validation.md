# Codex profile envelope validation (T-0506)

Dated evidence for review finding F4 of the [Astra review](2026-10-12-sdlc-lite-astra-review.md#f4--p2-make-the-codex-fingerprint-envelope-compatible-with-role-output). The Astra report is unchanged.

Change: the appended fingerprint section of every generated Codex profile defines the `profile:` line as a host envelope in front of the shared role body. The stored result retains it as line 2 and `results.py` skips one well-formed line. Claude output is unchanged.

Checked (offline, stub transport):
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: all 28 profiles define the envelope with no conflict; the pre-change note is rejected as contradictory and the corrected note passes; a fingerprinted scout report passes `run.sh` subagent exchange and `results.py validate`, and an envelope with a missing or misnamed `## Map` is rejected (exit 3).
- `results.py selftest`: valid envelope plus valid body passes; valid envelope plus missing key section or misordered body fails; a malformed envelope fails.

Unverified: a fresh live Codex named-agent run returning the envelope and complete role sections. No Codex host that can select named roles was available in this lane; it needs a fresh Codex session after `codex_roles.py install`.
