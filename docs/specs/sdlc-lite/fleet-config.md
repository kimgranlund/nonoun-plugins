# Fleet config

`.sdlc/fleet.json` says which repos and conductors are active, so excluding a repo is a setting. When `.sdlc/config` has a `work_root:` line the file is `fleet.json` in the work root instead (`docs/work/fleet.json` for `work_root: docs/work`); `fleet_config.py` and `fleet_status.py` read that path by default, and `--file` or `--fleet` still names any other. `plugins/sdlc-lite/scripts/fleet_config.py` loads and edits it: `show [--active]`, `add`, `exclude <repo> --reason`, `include <repo>`, `selftest`. It makes no model call and touches only this file.

Schema: an object with `version` and a `repos` list. Each entry:

| Field | Required | Meaning |
|---|---|---|
| `path` | yes | Absolute repo path |
| `name` | yes | Unique short name |
| `conductor` | yes | Conductor session name |
| `gh` | no | `owner/repo` |
| `status` | yes | `active` or `excluded` |
| `reason`, `date` | when excluded | Why and when (YYYY-MM-DD) |

A malformed file exits 1 naming the file and line; an entry is never silently dropped.
