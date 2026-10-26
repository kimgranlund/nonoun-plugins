# Pointer-focus border replacement

Date: 2026-10-10

Root cause: preview CSS used :focus to hide component borders while displaying replacement rings only for :focus-visible. Review-shell CSS had the same global rule plus an older button/input/select/textarea :focus rule. Pointer-focused unchecked choices could lose their visible outline without a replacement ring.

All three rules now use :focus-visible. Explicit input-group focus-within remains because it paints a ring; switch-track and disclosure ownership remain intact. Border width is retained. Contracts, product/shell context, recipe source and checkbox demonstration guidance distinguish ring replacement from ordinary pointer focus. The bounded choices-context lookup delivers the corrected shared rule. Token index and demonstration dependency identities refreshed.

Focused verification:54 authored control contexts in Playwright Chromium,Firefox,WebKit at Light/Dark, spanning preview checkbox,button,input,select,textarea and shell button,input,select,textarea. Keyboard ring/border replacement, stable dimensions, invalid semantic attribute, restored blur paint, input-group/switch/disclosure owners and unaffected ancestor boundary passed. The old-pointer rule failure control was rejected in Chromium/Firefox (four contexts). WebKit does not focus the tested checkbox on pointer activation: that negative-control state is not applicable, not a pass. Missing keyboard-ring controls were rejected in all six engine/scheme contexts. Accepted installed-Safari/AT/device/environment limitations are unchanged.

The check-development failures are retained: blur was sampled during the existing state transition; another old shell rule was discovered; the negative control was corrected to reproduce original transition ownership. No prior evaluation or full component suite was rerun. This is authored focused verification, not full-generation efficacy or complete accessibility coverage.

Canonical source-derived sheets and ZIP are refreshed by the publication receipt. Prior canonical and package are retained. Existing reports, sealed holdout, register dispositions and peer-owned live components.html are preserved. The round2 candidate remains rejected; this CSS correction does not rewrite its scores.
