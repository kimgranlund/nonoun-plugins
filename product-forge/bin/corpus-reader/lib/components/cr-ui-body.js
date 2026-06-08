/**
 * <cr-ui-body> — the main column: a sticky topbar (breadcrumb) over the
 * `content | toc` grid.
 *
 * Holds <cr-ui-page> (column 1) and <cr-ui-toc> (column 2, right rail), forwards
 * `sitemap`/`route` to the page, toggles `.cr-home` (single column) when there is
 * no route, renders the topbar breadcrumb from the sitemap, and pipes the page's
 * `cr:page` headings into the toc.
 */
import { UIElement } from "./base.js";
import { esc } from "./util.js";

export class UIBody extends UIElement {
  static properties = {
    sitemap: { type: Object, default: null },
    route: { type: String, default: "" },
  };

  static template = () => null;

  #col = null;
  #topbar = null;
  #crumb = null;
  #grid = null;
  #toc = null;
  #page = null;
  #built = false;

  connected() {
    this.#build();
  }

  #build() {
    if (this.#built) return;
    this.#built = true;

    this.#col = document.createElement("div");
    this.#col.className = "cr-main";

    this.#topbar = document.createElement("header");
    this.#topbar.className = "cr-topbar";
    this.#crumb = document.createElement("nav");
    this.#crumb.className = "cr-crumb";
    this.#crumb.setAttribute("aria-label", "Breadcrumb");
    this.#topbar.append(this.#crumb);

    this.#grid = document.createElement("main");
    this.#grid.className = "cr-body";
    this.#page = document.createElement("cr-ui-page");
    this.#toc = document.createElement("cr-ui-toc");
    this.#grid.append(this.#page, this.#toc); // content first, toc = right rail

    this.#col.append(this.#topbar, this.#grid);
    this.appendChild(this.#col);

    this.#page.addEventListener("cr:page", (e) => {
      if (this.#toc) this.#toc.headings = e.detail.headings;
    });
  }

  render() {
    this.#build();
    this.#grid.classList.toggle("cr-home", !this.route);
    if (this.#page) {
      this.#page.sitemap = this.sitemap;
      this.#page.route = this.route || "";
    }
    this.#renderCrumb();
  }

  #renderCrumb() {
    const sm = this.sitemap || {};
    const route = this.route || "";
    const home = esc(sm.title || "Corpus");
    if (!route) {
      this.#crumb.innerHTML = "<b>" + home + "</b>";
      return;
    }
    let sec = null;
    let page = null;
    (sm.sections || []).forEach((s) => {
      (s.pages || []).forEach((p) => {
        if (p.path === route) {
          sec = s;
          page = p;
        }
      });
    });
    (sm.rootPages || []).forEach((p) => {
      if (p.path === route) page = p;
    });
    let out = "<a href='#/'>" + home + "</a>";
    if (sec) out += "<span>/</span>" + esc(sec.title);
    if (page) out += "<span>/</span><b>" + esc(page.title) + "</b>";
    this.#crumb.innerHTML = out;
  }
}

customElements.define("cr-ui-body", UIBody);
