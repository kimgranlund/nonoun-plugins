/**
 * <cr-ui-header> — the sticky top bar: [ brand | Menu ].
 *
 * Properties: `sitemap` (title) and `route` (passed to the nav for the active
 * highlight). Owns the <cr-ui-nav> dropdown and the Menu button that toggles it.
 */
import { UIElement } from "./base.js";

export class UIHeader extends UIElement {
  static properties = {
    sitemap: { type: Object, default: null },
    route: { type: String, default: "" },
  };

  static template = () => null;

  #titleEl = null;
  #btn = null;
  #nav = null;
  #built = false;

  connected() {
    this.#build();
  }

  #build() {
    if (this.#built) return;
    this.#built = true;

    const bar = document.createElement("header");
    bar.className = "cr-nav";

    const brand = document.createElement("a");
    brand.className = "cr-brand";
    brand.href = "#/";
    brand.setAttribute("aria-label", "Home");
    brand.innerHTML =
      "<span class='cr-brand-dot' aria-hidden='true'></span><span class='cr-brand-name'></span>";
    this.#titleEl = brand.querySelector(".cr-brand-name");

    this.#btn = document.createElement("button");
    this.#btn.className = "cr-menu-btn";
    this.#btn.type = "button";
    this.#btn.textContent = "Menu";
    this.#btn.setAttribute("aria-haspopup", "true");
    this.#btn.setAttribute("aria-expanded", "false");

    this.#nav = document.createElement("cr-ui-nav");
    this.#btn.addEventListener("click", () => {
      this.#nav.open = !this.#nav.open;
    });
    this.#nav.addEventListener("cr:open-change", (e) => {
      this.#btn.setAttribute("aria-expanded", String(e.detail.open));
    });

    bar.append(brand, this.#btn);
    this.append(bar, this.#nav);
  }

  render() {
    this.#build();
    if (this.#titleEl)
      this.#titleEl.textContent = this.sitemap?.title || "Corpus";
    if (this.#nav) {
      this.#nav.sitemap = this.sitemap;
      this.#nav.active = this.route;
    }
  }
}

customElements.define("cr-ui-header", UIHeader);
