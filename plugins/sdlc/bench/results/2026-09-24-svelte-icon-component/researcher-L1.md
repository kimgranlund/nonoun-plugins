<!-- role=researcher level=L1 model=sonnet effort=medium -->
## Answer
All six stylesheets exist at `https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/<weight>/style.css`. I fetched each one and computed its sha384 SRI value from the bytes received (values below). The CDN sends `access-control-allow-origin: *`, so `crossorigin="anonymous"` works.

## Findings
Each URL is `https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/<weight>/style.css`. The integrity value is `sha384-` plus the base64 digest, computed with `openssl dgst -sha384 -binary | openssl base64 -A`.

- regular, 78131 bytes: `sha384-6p9AefaqUhEVheRlj1mpAkbngHXy9mbYMrIdcIt4Jlc9lOLIablJq3bBsLOjGwZ7` [source: https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/regular/style.css]
- bold, 85821 bytes: `sha384-nblAP2mo2pVPyMQZDw9Xy9Cwgs9lowushAYep4w5+Q9kF4Ibf3n0B/gCMVdR+Vqy` [source: https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/bold/style.css]
- thin, 85821 bytes: `sha384-ZrguSahlNzFt9jT0cuIhTCpssPYg2cCEoWz7Bpd96tKHthb+kBAIugSMdw0DUcEy` [source: https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/thin/style.css]
- light, 87359 bytes: `sha384-GzhNOdwUkh38xzoNEY1vRdLr+w8q+bXEJsd/km6Ef61w1Kfk+lself6cn14ilrpO` [source: https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/light/style.css]
- fill, 85821 bytes: `sha384-pPVoXE8ft+zxKtxIDDI7SfTK6y95NHm4qa+hKEg/hs8VkjW5IP+9/dGOPCbDpUPl` [source: https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/fill/style.css]
- duotone, 231484 bytes: `sha384-UVFvhZP7fWAENUPOoq61rJg5ef6QZW0k5vpAn71041/QS4STvUcJQCGNhStZLGx9` [source: https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/duotone/style.css]
- A HEAD request to the bold URL returned HTTP 200, `content-type: text/css`, and `access-control-allow-origin: *`. [source: same bold URL]

## Conflicts and gaps
- Bold, thin and fill files are all 85821 bytes, but their hashes differ. This is plausible because the weight name changes inside each file, but I did not diff them.
- I did not cross-check the hashes against jsdelivr's own file-hash API or another mirror.
- I did not check the stylesheets' font file references, or the `ph-<weight>` class names they define.
