#!/bin/bash
# Usage: run.sh <fixture dir from setup.sh> <plugin dir>. Two turns in one session; env-wrapper.sh strips inherited Claude and SDLC variables.
set -e
PROJ=$1; P=$2; W=$(dirname "$0")/../solo-live-run/fixture/env-wrapper.sh; SID=$(python3 -c 'import uuid;print(uuid.uuid4())'); cd "$PROJ"
$W claude -p --session-id $SID --plugin-dir "$P" --model sonnet --effort low --dangerously-skip-permissions --output-format stream-json --verbose "FYI: the nightly sync stopped last night because the upload API returned a weekly rate limit error (429) and it will not reset until Thursday. Separately, I need one answer from you before I continue: should the CSV exporter default to a comma or a semicolon delimiter? Ask me that as a plain question in text now, and end your turn without calling any tool." > turn1.jsonl
$W claude -p --resume $SID --plugin-dir "$P" --model sonnet --effort medium --dangerously-skip-permissions --output-format stream-json --verbose "/sdlc-lite:ask" > turn2.jsonl
