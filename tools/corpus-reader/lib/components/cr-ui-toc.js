/**
 * <cr-ui-toc> — the per-page table of contents (one grid column).
 *
 * Driven by a `headings` property (array of `{ id, text, level, el }`) supplied
 * by <cr-ui-body> from the page's `cr:page` event. Builds the list, scroll-spies
 * the heading elements with an IntersectionObserver, and scrolls to a heading on
 * click without touching the router hash.
 */
import { UIElement } from "./base.js";
import { esc } from "./util.js";

export class UIToc extends UIElement {
  static properties = {
    headings: { type: Object, default: null },
  };

  static template = () => null;

  #aside = null;
  #observer = null;
  #links = null;

  connected() {
    this.#aside = document.createElement("aside");
    this.#aside.className = "cr-toc";
    this.#aside.setAttribute("aria-label", "On this page");
    this.appendChild(this.#aside);
  }

  disconnected() {
    this.#observer?.disconnect();
    this.#observer = null;
  }

  render() {
    if (!this.#aside) return;
    const heads = Array.isArray(this.headings) ? this.headings : [];
    this.#observer?.disconnect();
    if (!heads.length) {
      this.#aside.innerHTML = "";
      return;
    }

    let html = "<div class='cr-toc-title'>On this page</div><ul>";
    heads.forEach((h) => {
      const l3 = String(h.level || "").toUpperCase() === "H3";
      html +=
        "<li class='cr-toc-item" +
        (l3 ? " cr-l3" : "") +
        "'><a href='#" +
        esc(h.id) +
        "' data-id='" +
        esc(h.id) +
        "'>" +
        esc(h.text) +
        "</a></li>";
    });
    this.#aside.innerHTML = html + "</ul>";

    this.#links = {};
    this.#aside.querySelectorAll("a[data-id]").forEach((a) => {
      const id = a.getAttribute("data-id");
      this.#links[id] = a.parentNode;
      a.addEventListener("click", (e) => {
        // Scroll without changing location.hash (the hash is the router's page path).
        e.preventDefault();
        const found = heads.find((x) => x.id === id);
        const el = (found && found.el) || document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    this.#spy(heads);
  }

  #spy(heads) {
    if (!("IntersectionObserver" in window)) return;
    this.#observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (!en.isIntersecting) return;
          this.#aside
            .querySelectorAll(".cr-active")
            .forEach((n) => n.classList.remove("cr-active"));
          const li = this.#links[en.target.id];
          if (li) li.classList.add("cr-active");
        });
      },
      { rootMargin: "0px 0px -72% 0px", threshold: 0 },
    );
    heads.forEach((h) => {
      if (h.el) this.#observer.observe(h.el);
    });
  }
}

customElements.define("cr-ui-toc", UIToc);
