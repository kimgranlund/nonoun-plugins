"""Detectors: deterministic checks over the persisted rows (events.jsonl) and aux.json.

Each family module exposes detect(rows, aux, thresholds) and builds its findings with
findings.make. thresholds.THRESHOLDS holds every number a detector uses; a caller may pass a
partial dict that overrides it (see thresholds.merged).

Families: escalation (replans, recurring findings, bumps, refusals, resume order, run records),
plan (criteria that never went red, contract dependents, scope widened in prose),
hygiene (stray worktrees, tracked runtime files, integration resets, stale or overwritten fanout
logs, ticket id collisions, unregistered external branches),
cost (cost over the bench baseline, many builder attempts, polling loops, background denials, rate
limits). cost.detect returns (findings, notes); the others return findings alone.
"""
