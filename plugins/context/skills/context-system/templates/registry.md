# Registry template

Optional local JSON profile. Inline descriptors have the same requirements as the
[descriptor template](descriptor.md); ownership and relationships are optional.

```json
{
  "schemaVersion": 1,
  "entry": "ENTRY.md",
  "artifacts": [{
    "id": "customer-search",
    "location": "domains/customer/search/README.md",
    "kind": "capability",
    "summary": "Search customer records.",
    "revision": "2",
    "sha256": "<SHA256 of referenced file>"
  }],
  "routes": [{"intent": "find-customer", "target": "customer-search"}]
}
```

Resolve every path relative to the corpus root. Prefer generating a registry from
canonical descriptors when scale warrants it. Record generator inputs and their
hashes; never silently update fingerprints to conceal stale generated summaries.
