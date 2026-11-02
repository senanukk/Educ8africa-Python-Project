// VoltSafe front-end: theme switching + interactive substation map.
(function () {
  const root = document.documentElement;

  function applyTheme(name) {
    root.setAttribute("data-theme", name);
    document.querySelectorAll(".theme-dot").forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.set === name))
    );
    try { localStorage.setItem("voltsafe-theme", name); } catch (e) { /* storage unavailable */ }
  }
  document.querySelectorAll(".theme-dot").forEach((b) =>
    b.addEventListener("click", () => applyTheme(b.dataset.set))
  );
  applyTheme(root.getAttribute("data-theme") || "midnight");

  // Substation map: clicking a zone reveals its detail / check-in panel.
  const zones = document.querySelectorAll(".site-map .zone");
  function selectZone(code) {
    if (!document.querySelector(".area-panel")) {
      // Map shown without detail panels (home / dashboard): open the full map.
      const map = document.querySelector(".site-map");
      if (map && map.dataset.href) window.location = map.dataset.href + "?area=" + encodeURIComponent(code);
      return;
    }
    zones.forEach((z) => z.classList.toggle("selected", z.dataset.code === code));
    document.querySelectorAll(".area-panel").forEach((p) => (p.hidden = p.dataset.code !== code));
    const panel = document.querySelector(`.area-panel[data-code="${code}"]`);
    if (panel && window.innerWidth < 900) panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  zones.forEach((z) => {
    z.addEventListener("click", () => selectZone(z.dataset.code));
    z.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectZone(z.dataset.code); }
    });
  });
  const initial = document.querySelector(".site-map")?.dataset.initial;
  if (initial) selectZone(initial);
})();
