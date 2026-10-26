# Principles and scope

The irreducible geometry is content + spacing + border. A fixed-size box cannot preserve all three when their sum exceeds its size. The system preserves readable content and alignment slots, consumes available inset first, then permits a containing composite to grow.

Separate four concepts: inset (outer border edge to content slot), internal gap (between siblings), exposed label edge (optical text compensation), and layout gutter (between independent components). CSS margin is one implementation mechanism, not the name for all spacing.

A primitive-to-page progression classifies responsibility: primitive → part → control → composite → collection → card/section → page. It is not a mandatory DOM hierarchy or a single linear spacing scale. Components have a semantic identity, geometry family and parent context independently.

Density is a family-specific lookup, not a global multiplier. Base unit is shared. Font size and label compensation do not change with density. Cards and collections do not overwrite a contained control's density. Prefer logical inline/block properties. A directional layout must preserve start/end meaning under RTL.

Rules marked confirmed express accepted design decisions in this conversation, not a claim of production readiness. Experimental rules require visual evaluation. Deprecated behavior must not be reintroduced merely because old CSS contains it.

The specimen uses explicit px values because the jig varies u in px. A rem-based host can convert resolved values consistently; do not multiply both u and the output again. Browser zoom and text resizing must remain possible.
