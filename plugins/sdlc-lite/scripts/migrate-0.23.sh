#!/usr/bin/env bash
# Usage: migrate-0.23.sh [--apply | --selftest]; kept for one release, runs migrate-worktrees.sh (T-0563).
exec bash "$(dirname "${BASH_SOURCE[0]}")/migrate-worktrees.sh" "$@"
