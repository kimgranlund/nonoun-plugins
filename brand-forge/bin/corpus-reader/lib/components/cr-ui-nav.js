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
    const meta = p.meta ? Object.values(p.meta).join(" ") : "";
    const search = (p.title + " " + p.path + " " + (p.summary || "") + " " + meta).toLowerCase();
    return (
      "<a class='cr-nav-link" + (extra || "") + "' href='#/" + enc(p.path) +
      "' data-path='" + esc(p.path) +
      "' data-search='" + esc(search) + "'>" +
      esc(p.title) + "</a>"
    );
  }

  /** Wrap each occurrence of `query` in a link's (plain-text) title with <mark>, so the matched
   * phrase is visible in the nav. textContent is always the title (marks don't change it), so it
   * is the stable source on every keystroke. Empty query — or a hit that matched only path /
   * summary / meta, not the title — renders the plain (escaped) title. Substring match, no regex. */
  #highlight(a, query) {
    const title = a.textContent;
    if (!query || title.toLowerCase().indexOf(query) < 0) {
      a.innerHTML = esc(title);
      return;
    }
    let out = "", rest = title, i;
    while ((i = rest.toLowerCase().indexOf(query)) >= 0) {
      out += esc(rest.slice(0, i)) +
        "<mark class='cr-mark'>" + esc(rest.slice(i, i + query.length)) + "</mark>";
      rest = rest.slice(i + query.length);
    }
    a.innerHTML = out + esc(rest);
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
    const query = (q || "").trim().toLowerCase();
    const files = window.CORPUS_FILES || null;
    this.#nav.querySelectorAll(".cr-nav-link").forEach((a) => {
      let hit = !query || (a.dataset.search || "").indexOf(query) >= 0;
      if (!hit && files) {
        const path = a.dataset.path;
        let lc = this.#contentLC.get(path);
        if (lc === undefined) {
          const raw = files[path];
          lc = typeof raw === "string" ? raw.toLowerCase() : null;
          this.#contentLC.set(path, lc);
        }
        hit = lc !== null && lc.indexOf(query) >= 0;
      }
      a.classList.toggle("cr-hide", !hit);
      this.#highlight(a, hit ? query : "");
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
