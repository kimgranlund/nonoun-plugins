# Package boundary, version 4

local.base-ui 4.0.0 exposes scripts/api.mjs, scripts/build-page.mjs, scripts/build.mjs and scripts/component-context.mjs. build-page.mjs is the default new-page scaffold: it requires a new directory and creates editable modular styles plus offline runtime/fonts. build.mjs remains the explicitly single-file export route. Node 22+ is the stated CLI floor (checks performed on Node 24.9.0); browsers use native platform primitives with the existing component-specific compatibility limits. Public JavaScript/CSS remains vanilla; no external React Base UI dependency exists.

kit.json records owned source hashes and runtimeApiVersion=1. describeKit verifies declared files; this is integrity, not a trust boundary. Only execute a trusted installed or supplied kit. The wireframe consumer locks the exact content identity in ui-kit.lock.json. An update requires explicit seal and sync. Generation never mutates either skill.

Preserve maintained recipe__slot class APIs; current token names and geometry roles come from the component records and [geometry contract](../../../../Projects/ui-kit/docs/system/geometry-contract.md). Runtime mount uses cloneable state, explicit stateKey, reducer/render/bind, and unmount cleanup. Same-key views repaint together; different keys isolate state; readOnly skips binding and dispatch. Host identity, approval policies and review feedback are not base concerns.

Compatibility copies in wireframe-review are generated distribution views, not a second authority. They support legacy source paths and checks during migration. The wireframe shell reads the kit directly. Catalog extraction, pure UI renderers and standalone UI checks are base-owned. The review page shell, overview/gaps assembly, demonstration guidance and review/evidence integration fixtures remain in wireframe-review. Old UI-check commands forward to base-ui. Retiring those compatibility surfaces is a later change, not required for standalone use.

No unchanged component/browser evidence is rerun by extraction. The new ownership/API/runtime seam requires targeted checks. Neither exact bytes nor scoped checks establish all-browser or generation reliability.

## Catalog boundary

`collectCatalog({playwright})` from scripts/api.mjs reads only base-ui sources and resolves tokens, declarations, component fragments and composition coverage with Chromium. It returns source hashes with owner=base-ui; Maps/Sets are retained in the programmatic API. `node scripts/build-catalog.mjs NEW_JSON PLAYWRIGHT` serializes that data and refuses existing output. The caller must provide an installed Playwright module. This entry produces data, not a second review website.

The review sheet coordinator consumes this API and the exported renderComponents/renderTokens/renderColors functions directly. It retains the existing five-page shell, source inspectors, comparison samples, demonstration guide, work register, historical reports and publication policy. Its inventory records sourceRoots by owner and its checker resolves those roots. Generic collector output must not contain a work register or generation history. Neither source extraction nor source hashes certify rendered state coverage.

Geometry vocabulary migration: widget/product/content/brand are the supported tiers; the old micro tier is retired. New CSS uses margin/gutter tokens. Deprecated inset token read aliases retain existing consumer references, but old token overrides are not an authoring API. See [geometry and spacing](geometry-spacing.md).

Version3 replaces the independent Maison sizing profile with a generated projection of mathematical-design-system/scripts/lib/scale.mjs and button.css. Maintainer generation/check commands require that sibling source; runtime consumption does not. Current sizing and curvature follow the [shared geometry contract](../../../../Projects/ui-kit/docs/system/geometry-contract.md), rather than historical fixed dimensions. Geometry changes are intentional and require fresh consumer review.

## Site projection ownership

The ui-kit project owns its UI CSS projection from system/*.css into its local vendor output. scripts/generate-geometry.mjs in this skill only projects numerical geometry tokens from the mathematical skill; it does not read project CSS or update wireframe.css. Updating the reusable UI distribution remains an explicit maintainer operation, separate from site builds.

The current Control slot model has been adopted by UI-KIT as of 2026-10-18. [Integration record](../../mathematical-design-system/references/ui-kit-integration.md) documents typed Select slots, exports, separate build ownership and verification scope. Future changes still require explicit synchronization.
