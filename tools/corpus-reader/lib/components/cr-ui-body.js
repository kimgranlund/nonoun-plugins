/**
 * <cr-ui-body> — the main column: a sticky topbar (menu button + breadcrumb) over
 * the `content | toc` grid, plus the mobile-drawer scrim.
 *
 * Holds <cr-ui-page> (column 1) and <cr-ui-toc> (column 2, right rail), forwards
 * `sitemap`/`route` to the page, toggles `.cr-home` (single column) when there is
 * no route, renders the breadcrumb, pipes the page's `cr:page` headings into the
 * toc, and drives the mobile drawer (a `.cr-drawer-open` class on <html>).
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
  #scrim = null;
  #onKey = null;
  #built = false;

  connected() {
    this.#build();
  }

  disconnected() {
    if (this.#onKey) document.removeEventListener("keydown", this.#onKey);
  }

  #build() {
    if (this.#built) return;
    this.#built = true;

    this.#col = document.createElement("div");
    this.#col.className = "cr-main";

    this.#topbar = document.createElement("header");
    this.#topbar.className = "cr-topbar";

    const menu = document.createElement("button");
    menu.type = "button";
    menu.className = "cr-menu-btn";
    menu.setAttribute("aria-label", "Open navigation");
    menu.innerHTML =
      "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' " +
      "stroke-linecap='round' aria-hidden='true'><line x1='3' y1='6' x2='21' y2='6'/>" +
      "<line x1='3' y1='12' x2='21' y2='12'/><line x1='3' y1='18' x2='21' y2='18'/></svg>";
    menu.addEventListener("click", () => this.#drawer());

    this.#crumb = document.createElement("nav");
    this.#crumb.className = "cr-crumb";
    this.#crumb.setAttribute("aria-label", "Breadcrumb");
    this.#topbar.append(menu, this.#crumb);

    this.#scrim = document.createElement("div");
    this.#scrim.className = "cr-scrim";
    this.#scrim.addEventListener("click", () => this.#drawer(false));

    this.#grid = document.createElement("main");
    this.#grid.className = "cr-body";
    this.#page = document.createElement("cr-ui-page");
    this.#toc = document.createElement("cr-ui-toc");
    this.#grid.append(this.#page, this.#toc); // content first, toc = right rail

    this.#col.append(this.#topbar, this.#grid);
    this.append(this.#scrim, this.#col);

    this.#page.addEventListener("cr:page", (e) => {
      if (this.#toc) this.#toc.headings = e.detail.headings;
    });
    this.#onKey = (e) => {
      if (e.key === "Escape") this.#drawer(false);
    };
    document.addEventListener("keydown", this.#onKey);
  }

  /** Toggle (or set, when `open` is passed) the mobile drawer via a class on <html>. */
  #drawer(open) {
    const cl = document.documentElement.classList;
    if (open === undefined) cl.toggle("cr-drawer-open");
    else cl.toggle("cr-drawer-open", open);
  }

  render() {
    this.#build();
    this.#drawer(false); // navigation closes the mobile drawer
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
    (sm.sections || []).forEach((s) =>
      (s.pages || []).forEach((p) => {
        if (p.path === route) {
          sec = s;
          page = p;
        }
      }),
    );
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
