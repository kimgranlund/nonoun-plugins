// Canonical class normalization only. No aliases or CSS selector rewriting.
export function normalizeClassNames(value) {
  return [...new Set(value.split(/\s+/).filter(Boolean))].join(' ');
}
