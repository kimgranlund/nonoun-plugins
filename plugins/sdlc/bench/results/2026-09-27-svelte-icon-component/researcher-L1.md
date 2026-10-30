<!-- role=researcher level=L1 model=sonnet effort=medium -->
## Answer
For `@phosphor-icons/web@2.1.2`, load per-weight CSS from jsdelivr at `https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/<weight>/style.css` (all six weights return HTTP 200: regular, thin, light, bold, fill, duotone — no "sharp" weight exists in this package). Class convention: regular uses `ph ph-<name>` (no `ph-regular`); every other weight uses `ph-<weight> ph-<name>`. Computed sha384 SRI hashes for each weight's `style.css` are listed below (derived by me via curl+openssl against the live CDN response, not published anywhere by Phosphor or jsdelivr).

## Findings
- CDN URL pattern for per-weight stylesheets is `https://cdn.jsdelivr.net/npm/@phosphor-icons/web@<VERSION>/src/<WEIGHT>/style.css`; example given for duotone in the official README. [source: https://github.com/phosphor-icons/web/blob/master/README.md]
- "In order to use a weight, you must include a link to its stylesheet, and use the appropriate weight class on the icon (the regular weight uses `.ph` instead of `.ph-regular`)." Regular weight = `ph ph-<name>`; other weights = `ph-<weight> ph-<name>` (e.g. `ph-bold ph-smiley`). [source: https://github.com/phosphor-icons/web/blob/master/README.md]
- Supported weights for the web package are regular, thin, light, bold, fill, duotone (six total, no "sharp"). [source: https://github.com/phosphor-icons/web (README weight table), cross-checked via web search]
- All six weight CSS files exist at version 2.1.2 on jsdelivr; verified live with `curl -o -w "%{http_code}"` on 2026-09-27, all returned HTTP 200: [source: https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/<weight>/style.css, fetched directly]
  - regular: `sha384-6p9AefaqUhEVheRlj1mpAkbngHXy9mbYMrIdcIt4Jlc9lOLIablJq3bBsLOjGwZ7`
  - bold: `sha384-nblAP2mo2pVPyMQZDw9Xy9Cwgs9lowushAYep4w5+Q9kF4Ibf3n0B/gCMVdR+Vqy`
  - fill: `sha384-pPVoXE8ft+zxKtxIDDI7SfTK6y95NHm4qa+hKEg/hs8VkjW5IP+9/dGOPCbDpUPl`
  - light: `sha384-GzhNOdwUkh38xzoNEY1vRdLr+w8q+bXEJsd/km6Ef61w1Kfk+lself6cn14ilrpO`
  - thin: `sha384-ZrguSahlNzFt9jT0cuIhTCpssPYg2cCEoWz7Bpd96tKHthb+kBAIugSMdw0DUcEy`
  - duotone: `sha384-UVFvhZP7fWAENUPOoq61rJg5ef6QZW0k5vpAn71041/QS4STvUcJQCGNhStZLGx9`
  (Inferred: I computed these with `openssl dgst -sha384 -binary | openssl base64` on the downloaded file bytes myself; the README does not publish SRI hashes, and jsdelivr's general docs page I fetched did not surface a documented hash-lookup endpoint or query param, so I could not corroborate these against a second published source — only against jsdelivr serving the same immutable versioned URL twice.)
- Each `.ph.ph-<icon-name>` rule maps to a `content: "\e..."` glyph via `@font-face` with woff2/woff/ttf/svg sources relative to the CSS file's own directory — confirms the stylesheet is self-contained per weight and matches the "at most one link per weight" injection model in the handoff. [source: https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/regular/style.css, fetched directly]

## Conflicts and gaps
- Could not find an official, documented source (Phosphor README or jsdelivr docs) that publishes SRI hashes for these files — the sha384 values above are self-computed from the live CDN response, not cross-verified against a second independent source. Since jsdelivr serves immutable versioned package URLs, this is very likely stable, but treat it as inferred rather than sourced.
- jsdelivr's general documentation page did not clearly confirm or deny a built-in SRI-hash API/query-param; I did not chase `data.jsdelivr.com` further since the direct curl+hash approach already gives a usable value.
