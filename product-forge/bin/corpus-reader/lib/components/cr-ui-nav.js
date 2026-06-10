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
    return (
      "<a class='cr-nav-link" + (extra || "") + "' href='#/" + enc(p.path) +
      "' data-search='" + esc((p.title + " " + p.path + " " + (p.summary || "")).toLowerCase()) + "'>" +
      esc(p.title) + "</a>"
    );
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

  /** Live-filter links by a query against each link's `data-search`; hide empty groups. */
  filter(q) {
    if (!this.#nav) return;
    const query = (q || "").trim().toLowerCase();
    this.#nav.querySelectorAll(".cr-nav-link").forEach((a) => {
      const hit = !query || (a.dataset.search || "").indexOf(query) >= 0;
      a.classList.toggle("cr-hide", !hit);
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
