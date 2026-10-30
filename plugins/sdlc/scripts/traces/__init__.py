"""traces: read sdlc run traces (attempt records, runs.jsonl, result files) into rows.

Modules: table (row schema and join), sources (per-source readers), store (out dir, events,
aux, cursor), ingest (the walk), findings (finding records, findings.jsonl, clusters), selftest
(named case registry), cli (subcommands).
Sibling scripts (order, steps, tickets) are imported from the scripts/ dir, never re-implemented.
"""
