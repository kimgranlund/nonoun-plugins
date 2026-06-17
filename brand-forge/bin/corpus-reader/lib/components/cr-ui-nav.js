/**
 * <cr-ui-nav> — the persistent sidebar nav (sections → pages).
 *
 * Properties: `sitemap` (rendered into links) and `active` (current path, for the
 * highlight). Renders an always-visible <nav class="cr-side-nav"> list inside the
 * sidebar rail — no dropdown, no toggle. Navigation flows through `#/…` hash links.
 */
import { UIElement } from "./base.js";
import { esc, enc } from "./util.js";

export class UINav extends UIElement {
  static properties = {
    sitemap: { type: Object, default: null },
    active: { type: String, default: "" },
  };

  static template = () => null;

  #nav = null;
  #renderedSitemap = null;

  connected() {
    this.#nav = document.createElement("nav");
    this.#nav.className = "cr-side-nav";
    this.#nav.setAttribute("aria-label", "All pages");
    this.appendChild(this.#nav);
  }

  render() {
    if (!this.#nav) return;
    if (this.sitemap && this.sitemap !== this.#renderedSitemap) {
      this.#renderedSitemap = this.sitemap;
      this.#renderLinks();
    }
    this.#markActive();
  }

  #link(p, extra) {
    // Search index: title + path + summary + every frontmatter value (p.meta), so a query
    // matches on tags / type / version / owner / status, not just the title and path.
    const metaVals = p.meta ? Object.values(p.meta).join(" ") : "";
    const search = (p.title + " " + p.path + " " + (p.summary || "") + " " + metaVals).toLowerCase();
    // The frontmatter itself powers field-scoped queries (`type:guide`, `status:active`) and the
    // "Meta: …" hint line. JSON in a single-quoted attr, esc-safe; parsed back in #fm().
    const fm = p.meta ? esc(JSON.stringify(p.meta)) : "";
    return (
      "<a class='cr-nav-link" + (extra || "") + "' href='#/" + enc(p.path) +
      "' data-path='" + esc(p.path) +
      "' data-search='" + esc(search) +
      "' data-fm='" + fm + "'>" +
      "<span class='cr-nav-title'>" + esc(p.title) + "</span></a>"
    );
  }

  /** Parse a query into plain terms + field-scoped tokens. `field:value` (e.g. `type:guide`,
   * `status:active`) scopes the match to a frontmatter field; a bare token matches the plain
   * index. A leading `/` is stripped, so `/tag:active` works like `tag:active`. Tokens AND. */
  #parseQuery(raw) {
    const q = String(raw || "").trim().replace(/^\/+/, "").trim().toLowerCase();
    const terms = [], fields = [];
    if (q) {
      q.split(/\s+/).forEach((tok) => {
        const m = /^([a-z0-9_-]+):(.*)$/.exec(tok);
        if (m) fields.push({ field: m[1], value: m[2] });
        else terms.push(tok);
      });
    }
    return { terms, fields, empty: !terms.length && !fields.length };
  }

  /** The page's frontmatter, parsed from data-fm (esc-decoded by the browser → valid JSON). */
  #fm(a) {
    try {
      return a.dataset.fm ? JSON.parse(a.dataset.fm) : {};
    } catch (e) {
      return {};
    }
  }

  /** A field token matches if some frontmatter key STARTS WITH `field` (so `tag`→`tags`) and its
   * value contains `value` (an empty value means the key need only exist). Returns [key,value]|null. */
  #matchField(fm, tok) {
    for (const k of Object.keys(fm)) {
      if (k.toLowerCase().indexOf(tok.field) === 0) {
        const v = String(fm[k]);
        if (tok.value === "" || v.toLowerCase().indexOf(tok.value) >= 0) return [k, v];
      }
    }
    return null;
  }

  /** Wrap every occurrence of any term (lowercased substrings) in `text` with <mark>. esc-safe. */
  #mark(text, terms) {
    const lc = text.toLowerCase();
    let out = "", pos = 0;
    for (;;) {
      let at = -1, len = 0;
      for (const t of terms) {
        if (!t) continue;
        const i = lc.indexOf(t, pos);
        if (i >= 0 && (at < 0 || i < at)) { at = i; len = t.length; }
      }
      if (at < 0) { out += esc(text.slice(pos)); break; }
      out += esc(text.slice(pos, at)) +
        "<mark class='cr-mark'>" + esc(text.slice(at, at + len)) + "</mark>";
      pos = at + len;
    }
    return out;
  }

  /** Baked-build full-text fallback: does the page's inlined markdown contain `term`? */
  #contentHit(a, term, files) {
    if (!files) return false;
    const path = a.dataset.path;
    let lc = this.#contentLC.get(path);
    if (lc === undefined) {
      const raw = files[path];
      lc = typeof raw === "string" ? raw.toLowerCase() : null;
      this.#contentLC.set(path, lc);
    }
    return lc !== null && lc.indexOf(term) >= 0;
  }

  /** Highlight plain terms in the title; empty list → plain (escaped) title. textContent is the
   * stable title source (marks don't change it), so this re-runs cleanly on every keystroke. */
  #highlight(a, terms) {
    const span = a.querySelector(".cr-nav-title");
    if (!span) return;
    const title = span.textContent;
    span.innerHTML = terms && terms.length ? this.#mark(title, terms) : esc(title);
  }

  /** The small mono "Meta: …" hint under a link. Shows matched field tokens as `key: value` (value
   * <mark>ed), else a windowed fragment for a plain term that hit the frontmatter but NOT the title.
   * Removed when there's nothing meta-side to reveal. Lives inside the <a>, so it stays clickable. */
  #metaLine(a, info, radius = 48) {
    let line = a.querySelector(".cr-nav-meta");
    const drop = () => { if (line) line.remove(); };
    if (!info) return drop();
    const { terms, fieldMatches } = info;
    // Readable context: the frontmatter minus `title` (already the visible label), "k: v · k: v".
    const md = Object.entries(this.#fm(a))
      .filter(([k]) => k.toLowerCase() !== "title")
      .map(([k, v]) => k + ": " + v)
      .join("  ·  ");
    if (!md) return drop();
    const mdLC = md.toLowerCase();
    const titleLC = (a.querySelector(".cr-nav-title")?.textContent || "").toLowerCase();
    // Phrases to highlight: matched field values (or the key for an empty-value token) + plain
    // terms that hit the frontmatter but NOT the title (a title hit is already shown up top).
    const phrases = [];
    (fieldMatches || []).forEach(([k, , val]) => {
      if (k.toLowerCase() !== "title") phrases.push(val || k.toLowerCase());
    });
    (terms || []).forEach((t) => {
      if (mdLC.indexOf(t) >= 0 && titleLC.indexOf(t) < 0) phrases.push(t);
    });
    // Anchor on the earliest phrase; symmetric window — `radius` chars on EACH side of the matched
    // region, so there's as much context after the highlight as before. Two lines via CSS clamp.
    let at = -1, len = 0;
    for (const p of phrases) {
      const i = mdLC.indexOf(p);
      if (i >= 0 && (at < 0 || i < at)) { at = i; len = p.length; }
    }
    if (at < 0) return drop();
    const start = Math.max(0, at - radius);
    const end = Math.min(md.length, at + len + radius);
    const html = (start > 0 ? "…" : "") +
      this.#mark(md.slice(start, end), phrases) +
      (end < md.length ? "…" : "");
    if (!line) {
      line = document.createElement("span");
      line.className = "cr-nav-meta";
      a.appendChild(line);
    }
    line.innerHTML = html;
  }

  #renderLinks() {
    const sm = this.sitemap || {};
    let html = "";
    (sm.rootPages || []).forEach((p) => {
      html += this.#link(p, " cr-nav-root");
    });
    (sm.sections || []).forEach((s) => {
      const num = (String(s.id).match(/^\d+/) || [""])[0];
      html +=
        "<div class='cr-nav-group'><div class='cr-nav-group-title'>" +
        (num ? "<span class='cr-nav-ln'>" + esc(String(parseInt(num, 10))) + "</span>" : "") +
        "<span>" + esc(s.title) + "</span></div>";
      (s.pages || []).forEach((p) => {
        html += this.#link(p);
      });
      html += "</div>";
    });
    this.#nav.innerHTML = html;
  }

  #contentLC = new Map(); // lazy lowercased page text, by path (baked builds only)

  /** Live-filter links by a query against each link's `data-search` — and, in a baked
   * single-file build, against the page's full inlined markdown (window.CORPUS_FILES),
   * so search covers content, not just title/path/summary. Served layouts keep the
   * metadata-only filter (content isn't local there). Hide empty groups. */
  filter(q) {
    if (!this.#nav) return;
    const { terms, fields, empty } = this.#parseQuery(q);
    const files = window.CORPUS_FILES || null;
    this.#nav.querySelectorAll(".cr-nav-link").forEach((a) => {
      const search = a.dataset.search || "";
      let hit = empty;
      const fieldMatches = [];
      if (!empty) {
        // plain terms: each matches the metadata index, or (baked) the full inlined markdown
        const plainHit = terms.every(
          (t) => search.indexOf(t) >= 0 || this.#contentHit(a, t, files),
        );
        // field tokens: each scopes to a frontmatter field
        let fieldHit = true;
        if (fields.length) {
          const fm = this.#fm(a);
          for (const f of fields) {
            const m = this.#matchField(fm, f);
            if (!m) { fieldHit = false; break; }
            fieldMatches.push([m[0], m[1], f.value]);
          }
        }
        hit = plainHit && fieldHit;
      }
      a.classList.toggle("cr-hide", !hit);
      this.#highlight(a, hit ? terms : []);
      this.#metaLine(a, hit && !empty ? { terms, fieldMatches } : null);
    });
    this.#nav.querySelectorAll(".cr-nav-group").forEach((g) => {
      const any = [...g.querySelectorAll(".cr-nav-link")].some(
        (a) => !a.classList.contains("cr-hide"),
      );
      g.classList.toggle("cr-hide", !any);
    });
  }

  #markActive() {
    const want = this.active ? "#/" + enc(this.active) : null;
    this.#nav.querySelectorAll(".cr-nav-link").forEach((a) => {
      a.classList.toggle(
        "cr-active",
        Boolean(want) && a.getAttribute("href") === want,
      );
    });
  }
}

customElements.define("cr-ui-nav", UINav);
