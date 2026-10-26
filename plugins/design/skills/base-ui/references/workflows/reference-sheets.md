# UI sheets

The exported pure renderers under scripts/lib/sheets consume caller-supplied authoritative UI records. The current wireframe-review build-sheets coordinator composes these with its delivery ledger and review history. UI recipes, CSS and contracts belong here; review/gap records do not.

Keep the existing canonical sheets/system-review destination. Do not create new sibling previews or overwrite peer-owned live components.html. Stage publication before integrating changes. Standalone specimens use scripts/build.mjs and do not need the review coordinator.
