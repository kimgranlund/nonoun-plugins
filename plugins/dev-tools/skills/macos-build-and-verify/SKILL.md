---
name: macos-build-and-verify
description: Build, package, and visually verify the native SwiftUI LG Controls Mac app, including its menu-bar interface and local Swift toolchain fallback. Use for this project's macOS builds and UI checks, not unrelated web apps or system-wide toolchain maintenance.
---

# Build and verify LG Controls

Work in `/Users/kimba/Projects/lg-controls`. Read `docs/project-notes.md` and the current `scripts/build-app.sh` before selecting a build path. This is a SwiftUI app with shared controller state across a window and a `MenuBarExtra`, targeting macOS 14 or later.

## Build and package

Use the normal SwiftPM workflow when the toolchain works:

```sh
swift test
bash scripts/build-app.sh
```

This Mac previously had two independent toolchain failures: SwiftPM failed with a `BuildServerProtocol` symbol error, and the default macOS 27 SDK required a newer compiler. The already-installed macOS 26.5 SDK worked with direct `swiftc` compilation:

```sh
LG_SDK_PATH=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk bash scripts/check-core.sh
LG_SDK_PATH=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk bash scripts/build-app.sh --direct
```

Treat that as a local observed fallback, not a universal SDK requirement. Check `swift --version`, `xcrun --show-sdk-path`, and installed SDKs if it fails. Do not change global `xcode-select`, replace toolchain libraries, or install Xcode just to reproduce this workaround unless the user requests system maintenance.

The script produces `dist/LG A:C.app`, with a static core library and ad-hoc signature. It is a local app build, not a notarized distribution. Rebuilding can cause Keychain to ask for access again; preserve the existing service/account identifiers rather than clearing credentials to suppress a prompt.

## Verify behavior and presentation

Use tests appropriate to the changed behavior. The standalone core checks work without SwiftPM/XCTest; report them accurately rather than claiming the XCTest suite ran.

For UI changes, launch the rebuilt bundle and inspect it with available native app tools. Make sure the running process is the new build. Reacquire app state after restart/rebuild before using accessibility element indices.

- Use **Try demo** for interaction testing without changing an appliance. `--demo` is also supported at process launch. The demo's controls and values are illustrative.
- Check the normal window and, when affected, the narrower menu-bar panel. Verify setup, status, disabled controls, and error/notice wrapping as relevant to the edit.
- Inspect the rendered view, not just the accessibility tree. A real regression here was the visible “Display unit” label wrapping vertically beside a 90-point segmented picker. `.labelsHidden()` fixed the visual layout while retaining its accessibility label.
- Preserve shared controller state and serialized commands across views. Avoid duplicate polling from multiple active views and avoid treating a successful HTTP control response as confirmed hardware state.
- If launching a saved account causes a Keychain prompt, leave any unexpected permission decision to the user. Do not expose or clear their token during UI verification.

Finish with the app path, relevant verification results, and any remaining live-device or distribution limitation. Keep verified hardware observations in `docs/project-notes.md`; do not duplicate evolving facts throughout the skill.

## Current project conventions and UI lessons

- Display name: LG A/C. Bundle path: `dist/LG A:C.app`; executable: `lgcontrols`. Preserve bundle identifier and Keychain identity across visual renames. Keep ordinary paths lowercase; conventional README.md, AGENTS.md, CLAUDE.md, and Package.swift may retain casing. Project specs and reference notes belong in `docs/`. The user explicitly exempts the bundle filename: `LG A:C.app` displays as LG A/C in Finder. Quote shell paths containing spaces.
- Typography uses Apple's system SF APIs. Logo/colors come from saved official LG sources; icon generation uses the user-supplied avatar with a Heritage Red background. Reuse `scripts/generate-icon.cjs` (Node + sharp + iconutil) rather than raster-editing the logo. Source icon artwork and size decisions are in `docs/app-icon.md`. The build copies the ICNS and sets CFBundleIconFile before signing.
- Mode and Fan speed are segmented controls derived from profile options. Hide visible captions and built-in labels while retaining accessibility labels. Swing is also segmented: display OFF as Normal and ON as Swing without changing API values. Unknown reported values should not become selectable commands.
- User selected the thermostat dial layout (wireframe 03). `temperaturedial.swift` owns transient preview state; `temperaturedialscale.swift` owns testable angle/value conversion. Verify the lower-gap endpoints, step snapping, unit changes, disabled state, pointer drag release, and accessibility adjustments when editing this interaction. The dial commits once on release; a canceled/disappearing view must discard its preview.
- Verify the actual running build and launch mode. `open` returned success without producing a window on this Mac during prior work; launching the bundled executable directly produced the window. Treat exit status as insufficient evidence of successful launch. Demo tests must show the DEMO label before interacting; never infer it from an earlier process launch.
- Standalone core checks currently include a real sanitized temperature-profile regression and dial geometry. Test counts are historical, not a hardcoded acceptance requirement. Do not report that a complete XCTest suite or menu-bar review passed unless actually run.

- The final main view hides the branding header, routine notices, fetched timestamp, and footer actions. Preserve actionable errors and the DEMO marker. Connection is in the app menu (⌘,); native Quit is ⌘Q. Temperature − | + buttons form a small glass capsule below the room reading.
- See `docs/liquid-glass.md` for native glass APIs, accessibility fallbacks, and local appearance QA flags. Accessibility Reduce Transparency/Motion environment values are read-only; use app-local QA overrides rather than attempting `.environment` writes or changing system preferences.
- Copying the standalone bundle to Applications needs no build tools. Inspect both project and installed copies before launch; builds do not automatically replace an installed copy. A filesystem colon appears as a slash in Finder. Renaming the outer bundle does not change its display identity, executable, or Keychain identifiers.
