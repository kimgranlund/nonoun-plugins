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
