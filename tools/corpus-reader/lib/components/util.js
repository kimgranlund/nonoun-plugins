/** Shared helpers for the corpus-reader components — pure, DOM-light. */

export const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

/** Encode a path for use in a `#/…` hash, segment by segment (keeps the slashes). */
export const enc = (p) => String(p).split("/").map(encodeURIComponent).join("/");

/** Resolve `rel` against directory `base` (handles `.` / `..`), returning a repo-root-relative path. */
export function resolvePath(base, rel) {
  if (rel.charAt(0) === "/") return rel.slice(1);
  const parts = base ? base.split("/") : [];
  rel.split("/").forEach((p) => {
    if (p === "..") parts.pop();
    else if (p !== "." && p !== "") parts.push(p);
  });
  return parts.join("/");
}

export function slugify(s) {
  return (
    (s || "")
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .trim()
      .replace(/\s+/g, "-")
      .slice(0, 64) || "section"
  );
}

/** Split a leading `--- … ---` YAML block into flat `key: value` meta + the body. */
export function splitFrontmatter(text) {
  const meta = {};
  const m = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(text);
  if (!m) return { meta, body: text };
  m[1].split(/\r?\n/).forEach((line) => {
    const p = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (p) meta[p[1].trim()] = p[2].trim().replace(/^["']|["']$/g, "");
  });
  return { meta, body: text.slice(m[0].length) };
}

/** Give every heading in `root` a stable unique id (for ToC anchors + scrollspy). */
export function addHeadingIds(root) {
  const seen = {};
  root.querySelectorAll("h1, h2, h3, h4").forEach((h) => {
    if (h.id) return;
    const base = slugify(h.textContent);
    let id = base;
    let i = 2;
    while (seen[id] || document.getElementById(id)) id = base + "-" + i++;
    seen[id] = 1;
    h.id = id;
  });
}

/**
 * Rewrite rendered links/images so they work inside the hash router:
 * intra-corpus `*.md` links → `#/<resolved>`, relative images → resolved src,
 * external links → open in a new tab.
 */
export function rewriteLinks(root, pagePath) {
  const baseDir = pagePath.indexOf("/") >= 0 ? pagePath.replace(/\/[^/]*$/, "") : "";
  root.querySelectorAll("a[href]").forEach((a) => {
    let href = a.getAttribute("href");
    if (!href) return;
    if (/^[a-z][a-z0-9+.-]*:\/\//i.test(href) || /^mailto:/i.test(href)) {
      a.target = "_blank";
      a.rel = "noopener";
      return;
    }
    if (href.charAt(0) === "#") return;
    let frag = "";
    const hi = href.indexOf("#");
    if (hi >= 0) {
      frag = href.slice(hi);
      href = href.slice(0, hi);
    }
    if (/\.md$/i.test(href)) a.setAttribute("href", "#/" + enc(resolvePath(baseDir, href)) + frag);
  });
  root.querySelectorAll("img[src]").forEach((img) => {
    const src = img.getAttribute("src");
    if (!src || /^[a-z][a-z0-9+.-]*:\/\//i.test(src) || /^data:/i.test(src)) return;
    img.setAttribute("src", resolvePath(baseDir, src));
    img.loading = "lazy";
  });
}

const PROV_RE = /\[(KNOWN|INFERRED|OPEN|SEEDED)\]/g;

/**
 * Post-render decoration of corpus prose (operates on the already-sanitized DOM,
 * text nodes only — never re-parses HTML, so it can't reintroduce markup the
 * sanitizer dropped): wrap `[KNOWN]/[INFERRED]/[OPEN]/[SEEDED]` provenance markers
 * in styled spans, and turn inline `code.md` references into in-site xref links.
 * `resolve(basename)` returns the router path for a referenced `*.md`, or null.
 */
export function decorate(root, resolve) {
  const texts = [];
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (n.parentNode && n.parentNode.closest("a, code, pre, .cr-prov")) continue;
    PROV_RE.lastIndex = 0;
    if (PROV_RE.test(n.nodeValue)) texts.push(n);
  }
  texts.forEach((t) => {
    const s = t.nodeValue;
    const frag = document.createDocumentFragment();
    let last = 0, m;
    PROV_RE.lastIndex = 0;
    while ((m = PROV_RE.exec(s))) {
      if (m.index > last) frag.appendChild(document.createTextNode(s.slice(last, m.index)));
      const span = document.createElement("span");
      span.className = "cr-prov cr-prov-" + m[1].toLowerCase();
      span.textContent = m[0];
      frag.appendChild(span);
      last = m.index + m[0].length;
    }
    if (last < s.length) frag.appendChild(document.createTextNode(s.slice(last)));
    t.parentNode.replaceChild(frag, t);
  });

  if (typeof resolve !== "function") return;
  root.querySelectorAll("code").forEach((c) => {
    if (c.closest("pre, a")) return;
    const txt = (c.textContent || "").trim();
    if (!/^[\w./-]+\.md$/i.test(txt)) return;
    const route = resolve(txt.split("/").pop());
    if (!route) return;
    const a = document.createElement("a");
    a.className = "cr-xref";
    a.href = "#/" + enc(route);
    c.replaceWith(a);
    a.appendChild(c);
  });
}
