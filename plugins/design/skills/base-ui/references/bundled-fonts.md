# Offline font bundle

`getAssetBundle()` embeds licensed font binaries as data-URL @font-face rules in both css and foundationCSS. `build.mjs` includes this bundle in standalone HTML; no network, adjacent files or installed fonts are needed. Do not add Google Fonts imports or duplicate font-face rules. Direct consumers of typography.css alone must use the asset-bundle API to include faces.

Bricolage Grotesque: normal variable weight200–800 (upstream optical-size and width axes retained). IBM Plex Mono: normal and true italic weights100–700. Body/UI remain system-ui. Product headings retain their UI role; content headings use Bricolage. Unsupported glyphs use declared fallback fonts. No claim of all-script coverage.

Authoritative files, exact upstream revision, URLs, hashes and sizes are in assets/fonts/manifest.json. Both unmodified OFL licenses are retained and embedded as CSS comments in generated artifacts. The complete WOFF2 set is embedded instead of TTF, preserving all glyphs, axes, weights and styles. Generation never downloads fonts. Updating binaries is an explicit maintenance operation requiring provenance/hashes, license review, seal/sync and checks.

Verification: await document.fonts.ready after loading and after dynamic font use. A matching font-family declaration or fonts.check alone does not prove glyph rendering. check-bundled-fonts.mjs uses a network-disabled browser, loads every declared face and checks Chromium platform-font records for custom Bricolage/IBM glyphs, plus a missing-face negative control. Nested geometry must be rerun after font loading. Other engines need separate verification.

Maintainers can reproduce the WOFF2 assets with `scripts/compress-fonts.py` using the FontTools and Brotli versions in the manifest; `--check` recompresses and verifies byte parity plus glyph outlines, cmap, metrics and font-table fidelity (head/loca representation and invalidated DSIG signatures excluded). Original pinned TTFs remain as local source inputs; only WOFF2 is embedded in generated HTML. Conversion dependencies are maintenance-only and are not needed by Node generation.

Measured full-face payload: 2,381,884 TTF bytes → 792,880 WOFF2 bytes (66.7% reduction), or approximately 3.18MB → 1.06MB when base64 embedded. No glyph subsetting is used.
