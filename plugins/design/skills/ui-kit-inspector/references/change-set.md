# The change set

The change set is what a jig hands back. It is one JSON object, format `jig.changeset/1`, that says what moved, from what, against which base, in what context, with which check results, and why. The schema is [../schema/changeset.schema.json](../schema/changeset.schema.json), and a complete one is [../examples/minimal-system-jig/changeset.json](../examples/minimal-system-jig/changeset.json).

## Fields

Every field is required unless marked optional. No other key is allowed anywhere, except inside `context` and `extensions`.

| Field | Shape | Meaning |
|---|---|---|
| `$schema` | The constant `jig.changeset/1` | The format name. An importer keys on it. |
| `kind` | `system`, `component`, `layout` or `theme` | What the jig tunes |
| `base` | Object | What the change set was made against |
| `createdAt` | `YYYY-MM-DDThh:mm:ss`, an optional fraction, then `Z` or an offset | When it was exported |
| `context` | Object of strings, numbers, booleans or null | The viewpoint the person had. It changes nothing. |
| `changes` | Array | Constants that moved |
| `overrides` | Array | Derived values pinned off their formula |
| `checks` | Object with `contract` and `proposed` | What the rules said at export |
| `effects` | Array | Derived values that moved as a result |
| `note` | String, may be empty | The human reason |
| `extensions` | Object, optional | Free space for one tool's own data |

### base

| Key | Meaning |
|---|---|
| `system` | The name of the system, required |
| `source` | The file the constants live in, relative to the project root, or a package name. Required. |
| `sha256` | 64 lowercase hex characters: the hash of the bytes of `source` |
| `version` | A version string |
| `revision` | Optional, for example a commit |

At least one of `sha256` and `version` is present. Prefer `sha256` when the constants live in one file, because it changes whenever the file does. Base identity sits inside the change set because a pasted change set arrives with nothing else around it.

### changes

One entry per constant that moved.

| Key | Meaning |
|---|---|
| `path` | Starts with `/`. The same string as the control's `data-jig-constant`. Unique within the change set. |
| `from` | The value it replaced: a string, a number or a boolean |
| `to` | The new value. It differs from `from`. |
| `home` | Where the constant is written today, as a non-empty string, or null |
| `label` | Optional. The plain name shown to people. |
| `hint` | Optional. A suggestion for the receiver to confirm. |

How to fill `home`: record the place in the host's source where you found the literal, in words a person can follow to it, for example `host/tokens.css :root --unit`. Where the host uses DTCG token files, use the token's path. A constant you did not find in the source gets `home: null`. The jig lists it as a proposal, and the receiver decides where it should live.

### overrides

One entry per derived value a person pinned. An override is a request ("I want this result here"), never a new constant.

| Key | Meaning |
|---|---|
| `target` | The derived value, for example `--card-padding` |
| `from`, `to` | The value the formula gave, and the value wanted. They differ. |
| `at` | Optional. Where the pin applies, for example `width 360` or a variant name. |
| `formula` | Optional. The formula it was pinned off, in the host's own terms. |
| `reason` | Optional. Why this one spot should differ. |

### checks

`contract` holds the result of the host system's own rules. It is null when the host states none. `proposed` holds the checks the jig adds. Each is an object:

| Key | Meaning |
|---|---|
| `passed` | True exactly when `failures` is empty |
| `failures` | One non-empty string per failure, naming the rule and where it broke |
| `notes` | Optional. Findings that break no rule. |

A change set with failures can still be exported. The panel marks it as failing, and the receiver sees the failures.

### effects

One entry per derived value that moved because of the changes: `target`, `from`, `to`, and an optional `at`. The receiver uses it to confirm the result after applying, and does not edit from it.

### note and extensions

`note` is the person's reason in a sentence or two. It is the first thing a receiving agent reads. The panel asks for it every time, and an empty note is allowed.

`extensions` follows the precedent of `$extensions` in the DTCG format: a tool keeps its own data there under a key that names the tool, and other tools keep it and ignore it.

## Refusal rules

The validator, `node scripts/validate-changeset.mjs <file.json>`, refuses a change set that breaks the schema or one of three rules a schema cannot say:

| Rule | Refuses |
|---|---|
| R1 | A change or an override whose `from` equals its `to` |
| R2 | Two changes with the same `path` |
| R3 | A check whose `passed` is true while `failures` is not empty, or false while it is empty |

Each error is one line, `invalid <json pointer>: <message>`. The pointer names the object that holds the problem: `/changes/0`, `/base`, `/kind`, `/checks/proposed`, or `/` for the root.

The jig's own `importSet(text)` refuses more, because it knows the base:

1. `$schema` is not `jig.changeset/1`.
2. No base identity matches. Compare `sha256` with `sha256` and `version` with `version`, for each one present on both sides. If none is equal, refuse.
3. A change names a `path` this jig does not have.
4. A change's `from` differs from the base value here.

A refusal applies nothing and returns the reasons as an array of strings. An accepted set is applied onto the base, not onto the edits in progress, and returns an empty array.

## Three ways out, one way in

- Copy JSON: the change set alone.
- Copy as prompt: the instructions below, then the change set in a fenced `json` block.
- Selectable text: show the current change set in the panel, so it can be copied by hand where the clipboard is not available.
- Import: a text area that takes either form and passes it to `importSet`. Show the refusal reasons beside it.

## What the prompt export tells the receiver

The prompt is written for an agent that has never seen the jig. It carries five instructions, in this order, and then the change set.

1. Refuse a stale base. Compare `base` with the current `source`. If the identity does not match, or the value at any change's `home` is not its `from`, stop and say the base moved. Apply nothing.
2. Apply `changes` by path. Edit each constant at its `home` from `from` to `to`. A change with `home: null` has no place today: propose where the constant should live, and say that you did.
3. Run the contract. Run the host's own rules after applying, and report every failure. A failing contract needs a decision before the change lands.
4. Treat `overrides` as requests. For each one, propose the constant change that achieves it, or list it as a named exception. Keep the formula for everything else.
5. Confirm the effects. Check that the derived values now equal the `to` of each entry in `effects`, in the stated `context`.

A prompt of this shape works as a starting text. Replace the first line with the host's own names.

```
Apply this jig change set to the project.

1. base.source is the file the constants live in. Check base.sha256 or base.version against it. If it does not match, stop and say the base moved.
2. For each entry in changes, edit the place named in home from the value in from to the value in to. If the value there is not from, stop. If home is null, propose where the constant should live and say that you did.
3. Run the project's own rules and report every failure. checks.contract holds what the jig saw; checks.proposed holds the jig's own suggestions.
4. Each entry in overrides is a request for one derived value at one spot. Propose the constant change that achieves it, or list it as a named exception. Do not hard-code it.
5. Confirm your result reproduces effects in the stated context. context is only the viewpoint. note is the reason.
```

## Presets are saved change sets

A preset is a named change set against a base, not a bare snapshot of values. Saving a preset stores what `changeSet()` returns. Loading one calls `importSet`, so a preset made against an older base is refused the same way a pasted one is. Beside presets, always offer a reset to the base.

Presets kept in the browser stay in that browser. Every preset can also be copied out as JSON, so nothing a person tuned lives only in local storage.

## How the format sits beside existing ones

No existing format the research read carries from, to, base and reason in one object. That is why the change set is its own envelope. It borrows from each.

| Format | What it describes | What it lacks for this job | What the change set borrows |
|---|---|---|---|
| DTCG Format Module 2025.10 | Token state: a token is an object with `$value`, and optional `$type`, `$description` and `$deprecated` | No diff, no old value, no base version or hash, no intent field, no formulas | Token paths and `{group.token}` aliases as `home`; the `$extensions` idea |
| JSON Patch, RFC 6902 | An ordered list of operations on a JSON document | `replace` carries only the new value; no base identity and no reason field; the RFC's base check is the HTTP `If-Match` header, outside the patch | The `test` idea: assert the old value, and apply nothing on a mismatch |
| JSON Merge Patch, RFC 7396 | A partial document that mirrors the target | New values only: no old value, no base identity, no intent | Nothing. It is named so nobody mistakes it for enough. |

Sources: DTCG format (https://www.designtokens.org/tr/2025.10/format/), JSON Patch (https://www.rfc-editor.org/rfc/rfc6902), JSON Merge Patch (https://www.rfc-editor.org/rfc/rfc7396).

Working with DTCG hosts:

- Cite the stable 2025.10 module. It is a file format for token state, so do not present it as a change format.
- If the jig ever writes into a token file, keep jig-only data under a reverse-domain key in `$extensions`. Tools that read the file must preserve data they do not understand.
- DTCG has no formulas or computed values. A jig over a derived system finds its formulas in the host's code, and an override stays a request.
- The DTCG Resolver Module 2025.10 (https://www.designtokens.org/tr/2025.10/resolver/) handles contexts such as light and dark with sets, modifiers and a `resolutionOrder`. Its `version` field names the format version, not a token base, so it is not a base identity.

Working with JSON Patch hosts: when the constants live in one JSON document and each change's `path` is a JSON Pointer into it, the changes can be exported as `test` then `replace` pairs. A failed `test` leaves the document unchanged, which is the same refusal the change set makes on a wrong `from`.

```json
[
  { "op": "test", "path": "/unit", "value": 4 },
  { "op": "replace", "path": "/unit", "value": 5 }
]
```

This export is lossy. It drops `base`, `context`, `overrides`, `checks`, `effects` and `note`, and JSON Patch gives no place to put them, since members it does not define are ignored. Offer it as an extra beside the change set, never in place of it.
