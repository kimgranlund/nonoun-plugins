/**
 * <cr-ui-page> — renders the active route into the content column.
 *
 * route ""        → the home view (hero + maturity/provenance stats + section cards).
 * route "<x>.md"  → fetch + render that markdown: a kicker (its section), the doc
 *                   title, a badges row (status/version/date/type/path), then the
 *                   prose — highlighted code, mermaid → <cr-ui-diagram-viewer>, and
 *                   provenance tags + `path.md` xrefs via decorate().
 *
 * After a render it emits `cr:page` with the page's headings so <cr-ui-body> can
 * feed <cr-ui-toc>. Fetches are token-guarded against route races.
 */
import { UIElement } from "./base.js";
import {
  esc,
  enc,
  splitFrontmatter,
  rewriteLinks,
  addHeadingIds,
  decorate,
} from "./util.js";

const STAT_CATS = {
  provenance: [["known", "Known"], ["inferred", "Inferred"], ["open", "Open"], ["seeded", "Seeded"]],
  status: [["active", "Active"], ["draft", "Draft"], ["working", "Working"], ["needed", "Needed"]],
};

export class UIPage extends UIElement {
  static properties = {
    route: { type: String, default: "" },
    sitemap: { type: Object, default: null },
  };

  static template = () => null;

  #article = null;
  #renderedRoute = null;
  #renderedSitemap = null;
  #token = 0;

  connected() {
    this.#article = document.createElement("article");
    this.#article.className = "cr-content";
    this.appendChild(this.#article);
  }

  render() {
    if (!this.#article) return;
    const route = this.route || "";
    if (!route) {
      // Home depends on the sitemap, so re-render if either changed.
      if (route === this.#renderedRoute && this.sitemap === this.#renderedSitemap) return;
      this.#renderedRoute = route;
      this.#renderedSitemap = this.sitemap;
      this.#renderHome();
      return;
    }
    if (route === this.#renderedRoute) return;
    this.#renderedRoute = route;
    this.#renderDoc(route);
  }

  #emit(headings) {
    this.dispatchEvent(
      new CustomEvent("cr:page", {
        bubbles: true,
        detail: { headings, route: this.route || "" },
      }),
    );
  }

  /* ---- stats: maturity (frontmatter status) or provenance (corpus tags) ---- */
  #stats() {
    return (this.sitemap && this.sitemap.stats) || { mode: "none" };
  }
  #cats() {
    return STAT_CATS[this.#stats().mode] || [];
  }
  #segs(counts) {
    const cats = this.#cats();
    let tot = 0;
    cats.forEach((c) => (tot += (counts && counts[c[0]]) || 0));
    if (!tot) return "";
    return cats
      .map((c) => {
        const n = (counts && counts[c[0]]) || 0;
        return n
          ? "<i class='cr-seg cr-seg-" + c[0] + "' style='width:" + (100 * n) / tot + "%' title='" + esc(c[1] + " " + n) + "'></i>"
          : "";
      })
      .join("");
  }
  #statBlock() {
    const st = this.#stats();
    if (st.mode === "none") return "";
    const totals = st.mode === "provenance" ? st.provenance : st.status;
    const cats = this.#cats();
    let tot = 0;
    cats.forEach((c) => (tot += (totals && totals[c[0]]) || 0));
    if (!tot) return "";
    const leg = cats
      .map((c) => {
        const n = (totals && totals[c[0]]) || 0;
        return n
          ? "<span class='cr-sl'><i class='cr-dot cr-seg-" + c[0] + "'></i>" + esc(c[1]) + " <b>" + n + "</b></span>"
          : "";
      })
      .join("");
    const label = st.mode === "provenance" ? "Provenance" : "Maturity";
    const suffix = st.mode === "provenance" ? " tagged claims" : " documents";
    return (
      "<div class='cr-stat'><div class='cr-stat-h'><span>" + label + "</span>" +
      "<span class='cr-stat-total'>" + tot + suffix + "</span></div>" +
      "<div class='cr-statbar'>" + this.#segs(totals) + "</div>" +
      "<div class='cr-statleg'>" + leg + "</div></div>"
    );
  }
  #miniBar(sectionId) {
    const st = this.#stats();
    if (st.mode === "none") return "";
    const src = st.mode === "provenance" ? st.secProvenance || {} : st.secStatus || {};
    const segs = this.#segs(src[sectionId] || {});
    return segs ? "<div class='cr-minibar'>" + segs + "</div>" : "";
  }

  #renderHome() {
    const sm = this.sitemap || {};
    const sections = sm.sections || [];
    const docCount =
      sections.reduce((n, s) => n + (s.pages ? s.pages.length : 0), 0) +
      (sm.rootPages ? sm.rootPages.length : 0);

    let html =
      "<header class='cr-hero'><h1>" + esc(sm.title || "Corpus") + "</h1>" +
      "<p class='cr-hero-tag'>" + docCount + " document" + (docCount === 1 ? "" : "s") +
      " across " + sections.length + " section" + (sections.length === 1 ? "" : "s") + ".</p></header>";

    html += this.#statBlock();

    if (sm.rootPages && sm.rootPages.length) {
      html +=
        "<p class='cr-hero-links'>" +
        sm.rootPages
          .map((p) => "<a href='#/" + enc(p.path) + "'>" + esc(p.title) + " &rarr;</a>")
          .join("") +
        "</p>";
    }

    html += "<div class='cr-section-h'>Sections</div><div class='cr-cards'>";
    sections.forEach((s) => {
      const num = (String(s.id).match(/^\d+/) || [""])[0];
      html +=
        "<section class='cr-card'><div class='cr-card-h'>" +
        (num ? "<span class='cr-card-num'>" + esc(String(parseInt(num, 10))) + "</span>" : "") +
        "<h3>" + esc(s.title) + "</h3></div>" +
        this.#miniBar(s.id) +
        (s.desc ? "<div class='cr-card-desc'>" + esc(s.desc) + "</div>" : "") +
        "<div class='cr-card-links'>";
      (s.pages || []).forEach((p) => {
        html += "<a href='#/" + enc(p.path) + "'>" + esc(p.title) + "</a>";
      });
      if (!s.pages || !s.pages.length) html += "<span class='cr-muted-note'>— empty</span>";
      html += "</div></section>";
    });
    html += "</div>";

    this.#article.innerHTML = html;
    this.#emit([]);
    window.scrollTo(0, 0);
  }

  #lookup(route) {
    const sm = this.sitemap || {};
    let section = null;
    let page = null;
    (sm.sections || []).forEach((s) =>
      (s.pages || []).forEach((p) => {
        if (p.path === route) {
          section = s;
          page = p;
        }
      }),
    );
    (sm.rootPages || []).forEach((p) => {
      if (p.path === route) page = p;
    });
    return { section, page };
  }

  /** basename(`foo.md`) → its router path, for inline `code.md` xref linking. */
  #resolver() {
    const sm = this.sitemap || {};
    const byBase = {};
    const add = (p) => {
      byBase[p.path.split("/").pop()] = p.path;
    };
    (sm.sections || []).forEach((s) => (s.pages || []).forEach(add));
    (sm.rootPages || []).forEach(add);
    return (base) => byBase[base] || null;
  }

  #renderDoc(route) {
    const token = ++this.#token;
    this.#article.innerHTML = "<p class='cr-loading'>Loading&hellip;</p>";
    fetch(route)
      .then((r) => {
        if (!r.ok) throw new Error(r.status + " — " + route);
        return r.text();
      })
      .then((text) => {
        if (token !== this.#token) return; // a newer route superseded this load
        const fm = splitFrontmatter(text);
        // Corpus markdown is untrusted and marked does not sanitize → scrub the
        // rendered HTML with DOMPurify. If marked or DOMPurify is unavailable
        // (CDN/SRI failure), never inject raw HTML — degrade to escaped source.
        const bodyHtml =
          window.marked && window.DOMPurify
            ? window.DOMPurify.sanitize(window.marked.parse(fm.body))
            : "<pre>" + esc(fm.body) + "</pre>";
        const info = this.#lookup(route);
        const title = fm.meta.title || (info.page && info.page.title) || route.split("/").pop();
        this.#article.innerHTML =
          this.#head(info, title, fm.meta) + "<div class='cr-md'>" + bodyHtml + "</div>";
        const md = this.#article.querySelector(".cr-md");
        // The big doc title carries the heading; drop a duplicate leading H1 from the prose.
        const h1 = md.querySelector("h1");
        if (h1 && h1 === md.firstElementChild) h1.remove();
        rewriteLinks(md, route);
        addHeadingIds(md);
        decorate(md, this.#resolver());
        this.#highlight(md);
        this.#mermaid(md);
        const heads = [...md.querySelectorAll("h2, h3")].map((h) => ({
          id: h.id,
          text: (h.textContent || "").trim(),
          level: h.tagName,
          el: h,
        }));
        this.#emit(heads);
        window.scrollTo(0, 0);
      })
      .catch((err) => {
        if (token !== this.#token) return;
        this.#article.innerHTML =
          "<div class='cr-error'><h1>Page not found</h1><p>" +
          esc(err.message) +
          "</p><p><a href='#/'>&larr; Back to index</a></p></div>";
        this.#emit([]);
      });
  }

  #head(info, title, meta) {
    let out = "";
    if (info.section) {
      const num = (String(info.section.id).match(/^\d+/) || [""])[0];
      out +=
        "<div class='cr-kicker'>" +
        (num ? esc(String(parseInt(num, 10))) + " · " : "") +
        esc(info.section.title) +
        "</div>";
    }
    out += "<h1 class='cr-doc-title'>" + esc(title) + "</h1>";
    out += this.#badges(info, meta);
    return out;
  }

  #badges(info, meta) {
    const m = meta || {};
    const b = [];
    if (m.status)
      b.push(
        "<span class='cr-badge cr-badge-" +
          esc(m.status.toLowerCase().replace(/[^a-z]+/g, "-")) +
          "'>" + esc(m.status) + "</span>",
      );
    if (m.version) b.push("<span class='cr-badge'>v<b>" + esc(m.version) + "</b></span>");
    if (m.date) b.push("<span class='cr-badge'>" + esc(m.date) + "</span>");
    if (m.type) b.push("<span class='cr-badge'>" + esc(m.type) + "</span>");
    if (info.page)
      b.push("<span class='cr-badge'><b>" + esc(info.page.path.replace(/^(\.\.\/)+/, "")) + "</b></span>");
    return b.length ? "<div class='cr-badges'>" + b.join("") + "</div>" : "";
  }

  #highlight(md) {
    if (!window.hljs) return;
    md.querySelectorAll("pre code").forEach((c) => {
      if (/\blanguage-mermaid\b/.test(c.className)) return;
      try {
        window.hljs.highlightElement(c);
      } catch (e) {
        /* ignore */
      }
    });
  }

  #mermaid(md) {
    md.querySelectorAll("code.language-mermaid").forEach((c) => {
      const viewer = document.createElement("cr-ui-diagram-viewer");
      viewer.code = c.textContent;
      const pre = c.closest("pre") || c.parentNode;
      pre.replaceWith(viewer);
    });
  }
}

customElements.define("cr-ui-page", UIPage);
