# Model registry — mode 4

The shared model catalog and provider detection. Source: `packages/llm/src/models.ts` (the `MODELS` catalog + `DEFAULT_MODEL`) and the `detectProvider()` function in `packages/llm/src/adapters/index.ts`.

---

## What the registry is for

`models.ts` is the one source for the model list three surfaces previously duplicated. It is exported as a subpath (`@adia-ai/llm/models`) and as a top-level re-export from `index.ts`. Its consumer is the `<chat-input-ui>` web-module's `models` setter — a grouped-options structure rendered by an internal `<select-ui>` with `<optgroup>`s.

## The `MODELS` shape — do not deviate

`models.ts` exports:

```text
ModelOption = { value: string; label: string }
ModelGroup  = { label: string; options: ModelOption[] }
MODELS: ModelGroup[]
DEFAULT_MODEL: string
```

`MODELS` is a 2-D grouped array: an outer list of provider groups, each with a `label` (the provider name shown as the `<optgroup>` label) and an `options[]` of `{ value, label }` pairs (the `value` is the model id sent to the API; the `label` is the human display name).

**This exact shape is a contract.** The `<chat-input-ui>.models` setter expects `[{ label, options: [{ value, label }] }]`. Flattening it, renaming the keys, or nesting differently breaks the chat input. The current groups (as authored in `models.ts`) are `Anthropic`, `OpenAI`, `Google` — adding a group is additive; restructuring is breaking.

## `DEFAULT_MODEL` — keep it cheap and present

`DEFAULT_MODEL` is the value `<chat-input-ui>` selects on load. Two rules:

- **It must be a `value` that exists somewhere in `MODELS`.** A `DEFAULT_MODEL` that no group lists leaves the select with nothing selected.
- **Default to the cheapest/fastest option, not a flagship.** Most consumers want fast/cheap by default; a flagship default is a cost surprise. The current default in `models.ts` is the Haiku-tier Anthropic id.

## Model ids must be resolvable by `detectProvider()`

When a `chat()` / `streamChat()` call omits an explicit `provider`, the facade infers it from the model id via `detectProvider(model)` in `index.ts`. The current rules (case-insensitive on the id):

| Returns | Matches when the id… |
| --- | --- |
| `anthropic` | includes `claude` OR starts with `anthropic/` |
| `openai` | includes `gpt` / `o1` / `o3` / `o4` OR starts with `openai/` |
| `gemini` | includes `gemini` OR starts with `google/` |
| `null` | none of the above → the facade throws "Cannot detect provider…; set provider explicitly" |

**So a new model id in `MODELS` must either match an existing `detectProvider` branch or ship with a new branch** — otherwise every consumer that relies on auto-detection breaks for that model. When you add a provider, add both the `MODELS` group AND the `detectProvider` branch (see `add-a-provider.md`).

Note the two id-naming conventions both flow through detection: a substring convention (`claude…`, `gpt…`, `gemini…`) and a `provider/model` prefix convention (`anthropic/…`, `openai/…`, `google/…`). A new provider should support both for forward-compatibility.

## The bridge's `DEFAULT_MODELS` is a separate map — keep it in sync

`llm-bridge.ts` carries its own `DEFAULT_MODELS` (per-provider fallback used by `createAdapter()` when no model is supplied — e.g. `anthropic → claude-sonnet-4-…`, `openai → gpt-4o`, `google → gemini-2.0-flash`). This is **distinct** from `models.ts`'s `DEFAULT_MODEL` (the chat-input default). They serve different surfaces:

- `models.ts:DEFAULT_MODEL` — what the chat-input UI pre-selects (cheap/fast).
- `llm-bridge.ts:DEFAULT_MODELS[provider]` — what `createAdapter()` falls back to per provider when the caller passes none.

When you add a provider, add an entry to the bridge's `DEFAULT_MODELS` too (see `bridge-facade.md`). When you retire a model id, check both maps.

## Worked example — adding a model to an existing provider

Add a new Anthropic model to the chat-input dropdown.

1. Plan: verify target is `npm run build` (the package compiles) plus a `chat()` with the new id resolving to the `anthropic` provider and returning text.
2. Execute: add `{ value: '<new-claude-id>', label: '<display name>' }` to the `Anthropic` group's `options[]` in `models.ts`. No `detectProvider` change needed — the id includes `claude`, so the existing branch matches.
3. Verify: `npm run build` passes; the `MODELS` shape is unchanged structurally; a `chat({ model: '<new-claude-id>', … })` with no explicit provider resolves Anthropic and returns non-empty `text`. If `DEFAULT_MODEL` should point at the new id, confirm it's a value that now exists.

## Pitfalls

- **A model id that `detectProvider` can't classify.** Adding `{ value: 'mystery-1' }` with no matching branch makes auto-detection throw for that model. Either name it to match a branch or add a branch.
- **Reordering groups for "cleanliness".** The order is the dropdown order; reordering is a visible UI change, not a no-op.
- **Treating `DEFAULT_MODEL` and the bridge `DEFAULT_MODELS` as the same thing.** They're two maps for two surfaces; a "default model" change usually means deciding which one you mean.

## Cross-references

- [bridge-facade.md](bridge-facade.md) — `createAdapter()` and its per-provider `DEFAULT_MODELS`
- [add-a-provider.md](add-a-provider.md) — the recipe that adds a `MODELS` group + a `detectProvider` branch together
- Source: `packages/llm/src/models.ts`, `detectProvider()` in `packages/llm/src/adapters/index.ts`, `DEFAULT_MODELS` in `packages/llm/src/llm-bridge.ts`
