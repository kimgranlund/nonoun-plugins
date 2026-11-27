// The DTCG color token shape (a $type color with colorSpace, components, alpha and, when opaque, hex), shared by
// families.mjs and named.mjs so both write one shape.
export function dtcgColor(colorSpace, components, alpha, hex) {
  const v = { colorSpace, components, alpha };
  if (alpha === 1 && hex) v.hex = hex;
  return { $type: 'color', $value: v };
}
