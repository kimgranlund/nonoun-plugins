/**
 * <cr-ui-page> — renders the active route into the content column.
 *
 * route ""        → the home view (hero + section tiles).
 * route "<x>.md"  → fetch + render that markdown (frontmatter meta bar, marked
 *                   body, highlighted code, mermaid → <cr-ui-diagram-viewer>).
 *
 * After a render it emits `cr:page` with the page's headings so <cr-ui-body>
 * can feed <cr-ui-toc>. Fetches are token-guarded against route races.
 */
import { UIElement } from "./base.js";
import {
  esc,
  enc,
  splitFrontmatter,
  rewriteLinks,
  addHeadingIds,
} from "./util.js";

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
      if (
        route === this.#renderedRoute &&
        this.sitemap === this.#renderedSitemap
      )
        return;
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

  #renderHome() {
    const sm = this.sitemap || {};
    let html =
      "<header class='cr-hero'><h1>" + esc(sm.title || "Corpus") + "</h1>";
    if (sm.rootPages && sm.rootPages.length) {
      html +=
        "<p class='cr-hero-links'>" +
        sm.rootPages
          .map(
            (p) =>
              "<a href='#/" + enc(p.path) + "'>" + esc(p.title) + " &rarr;</a>",
          )
          .join("") +
        "</p>";
    }
    html += "</header><div class='cr-tiles'>";
    (sm.sections || []).forEach((s) => {
      const num = (s.id.match(/^\d+/) || [""])[0];
      html += "<section class='cr-tile'><h2>";
      if (num)
        html +=
          "<span class='cr-tile-id'>" +
          esc(String(parseInt(num, 10))) +
          "</span>";
      html += esc(s.title) + "</h2><ul>";
      (s.pages || []).forEach((p) => {
        html += "<li><a href='#/" + enc(p.path) + "'>" + esc(p.title) + "</a>";
        if (p.summary)
          html += "<span class='cr-sum'>" + esc(p.summary) + "</span>";
        html += "</li>";
      });
      html += "</ul></section>";
    });
    html += "</div>";
    this.#article.innerHTML = html;
    this.#emit([]);
    window.scrollTo(0, 0);
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
        const bodyHtml = window.marked
          ? window.marked.parse(fm.body)
          : "<pre>" + esc(fm.body) + "</pre>";
        this.#article.innerHTML =
          this.#meta(route, fm.meta) +
          "<div class='cr-md'>" +
          bodyHtml +
          "</div>";
        const md = this.#article.querySelector(".cr-md");
        rewriteLinks(md, route);
        addHeadingIds(md);
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

  #meta(route, meta) {
    const sm = this.sitemap || {};
    const sec = (sm.sections || []).filter(
      (s) => route.split("/").indexOf(s.id) >= 0,
    )[0];
    let out =
      "<div class='cr-meta'><a href='#/'>" + esc(sm.title || "Home") + "</a>";
    if (sec) out += "<span>/</span>" + esc(sec.title);
    out += "</div>";
    if (meta && (meta.status || meta.version || meta.date)) {
      out += "<div class='cr-tags'>";
      if (meta.status)
        out +=
          "<span class='cr-tag cr-tag-" +
          esc(meta.status.toLowerCase().replace(/[^a-z]+/g, "-")) +
          "'>" +
          esc(meta.status) +
          "</span>";
      if (meta.version)
        out += "<span class='cr-tag'>v" + esc(meta.version) + "</span>";
      if (meta.date)
        out += "<span class='cr-tag'>" + esc(meta.date) + "</span>";
      out += "</div>";
    }
    return out;
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
