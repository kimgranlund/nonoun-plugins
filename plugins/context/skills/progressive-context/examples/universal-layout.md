# Universal Layout Example

Illustrative, not prescriptive.

```text
knowledge-system/
├── ENTRY.md
├── registry/
│   ├── artifacts.yaml
│   ├── procedures.yaml
│   └── domains.yaml
├── schemas/
├── procedures/
│   └── <procedure>/
│       ├── ENTRY.md
│       └── references/
├── domains/
│   └── <domain>/
│       ├── ENTRY.md
│       ├── descriptors/
│       ├── references/
│       └── subdomains/
└── adapters/
    ├── harness-a/
    └── harness-b/
```

Possible mappings:

```text
ENTRY.md      → AGENTS.md / README.md / CONTEXT.md / index record
registry/     → JSON / YAML / SQLite / API
procedures/   → skills / workflows / runbooks
domains/      → folders / collections / wiki spaces
adapters/     → provider-specific integration
```

The architecture is defined by responsibilities, not filenames.
