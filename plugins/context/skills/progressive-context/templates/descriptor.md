# Descriptor template

Optional local JSON profile. Replace paths and hashes with real bytes before use.
Required and optional semantics: [contracts](../references/contracts.md).

```json
{
  "id": "customer-search",
  "location": "domains/customer/search/README.md",
  "kind": "capability",
  "summary": "Search customer records.",
  "revision": "2",
  "sha256": "<SHA256 of referenced file>",
  "owner": "customer-platform",
  "aliases": ["legacy-customer-search"],
  "relationships": {"governed_by": ["privacy-policy"], "depends_on": ["customer-schema"]}
}
```

Keep IDs stable across moves. A standalone check cannot resolve relationship IDs;
validate the registry as well. Do not copy canonical bodies into summaries.
