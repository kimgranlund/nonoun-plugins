# Apple Smooth motion

Shared state transitions use a CSS linear() sampling of SwiftUI Spring(duration: 0.5, bounce: 0), sampled at 101 equally spaced times through settlingDuration(target: 1, epsilon: 0.001). The final sample is clamped to 1. The generated duration is 800.0ms. The 0.5s parameter is perceptual duration, not the full settling time.

Source: [Apple Smooth](https://developer.apple.com/documentation/swiftui/animation/smooth) and [spring value](https://developer.apple.com/documentation/swiftui/spring/value(target:initialvelocity:time:)). scripts/sample-apple-smooth.swift reproduces samples (run with a compatible macOS SDK). This web sampling reproduces the zero-velocity response, not SwiftUI's velocity-preserving interrupted animation engine. CSS transitions retarget from current presentation values. Reduced motion and forced colors disable transitions.

Segment selection is above hover, both below labels. Idle hover is transparent at selected bounds. On fresh hover, seed those bounds without transition then animate position, size and opacity; leave returns to selection while fading out. Movement between hovered options retargets continuously.

Selected and hover segment backgrounds share the same border protection. Compact (zero container margin) insets both by B per edge: position +B, dimensions −2B, radius max(0, option radius−B). With standard container margins, both use the full option bounds and radius. Per-edge paint inset is max(0, option border width − container padding), so existing margins are not charged twice. Transparent hover starts at the protected selected bounds. This changes paint only, not layout or hit targets.

Opposite foreground/background action pairs swap atomically to avoid a low-contrast interpolated midpoint. Outline, shadow, non-reversing paint and indicator movement retain shared motion. Listbox backgrounds use the same conditional border protection as segments; see [state punch list](interaction-states.md).
