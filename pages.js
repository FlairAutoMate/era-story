// Mobile menu: the pill's button toggles the panel; any link in it closes it.
(function () {
  var btn = document.querySelector("[data-menu-toggle]");
  var panel = document.querySelector(".menu-panel");
  if (!btn || !panel) return;
  var set = function (open) { panel.hidden = !open; btn.textContent = open ? "×" : "☰"; btn.setAttribute("aria-expanded", open ? "true" : "false"); btn.setAttribute("aria-label", open ? "Lukk menyen" : "Åpne menyen"); };
  btn.addEventListener("click", function () { set(panel.hidden); });
  panel.addEventListener("click", function (e) { if (e.target.closest("a")) set(false); });
})();

// Audience pages: the lead form posts to /api/lead with the page's audience.
(function () {
  var form = document.getElementById("era-lead");
  if (!form) return;
  var done = document.querySelector(".done");
  var err = document.querySelector(".err");
  var btn = form.querySelector("button[type=submit]");
  var label = btn.textContent;
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var value = (form.elements.value.value || "").trim();
    var website = (form.elements.website && form.elements.website.value || "").trim();
    err.hidden = true;
    if (value.length < 3) { err.textContent = "Skriv inn litt mer, så finner vi riktig sted."; err.hidden = false; return; }
    btn.disabled = true; btn.textContent = "Sender…";
    try {
      var r = await fetch("/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ audience: form.dataset.audience, value: value, website: website, page: location.href }) });
      var j = await r.json().catch(function () { return {}; });
      if (r.ok && j.ok) { form.hidden = true; done.hidden = false; }
      else { err.textContent = "Noe gikk galt hos oss. Prøv igjen om et øyeblikk."; err.hidden = false; }
    } catch (x) {
      err.textContent = "Ingen kontakt med serveren. Sjekk nettet og prøv igjen."; err.hidden = false;
    }
    btn.disabled = false; btn.textContent = label;
  });
})();

// Address autocomplete: on the owner/board pages, the address field gets a Kartverket
// (Geonorge) suggestion dropdown. Any fetch failure degrades silently to a plain text field.
(function () {
  var form = document.getElementById("era-lead");
  var input = document.getElementById("lead-value");
  if (!form || !input) return;
  if (form.dataset.audience !== "owner" && form.dataset.audience !== "board") return;
  var box = document.createElement("div");
  box.setAttribute("role", "listbox");
  box.style.cssText = "position:fixed;z-index:9999;display:none;background:#FFFFFF;border-radius:16px;box-shadow:0 20px 50px rgba(15,24,48,0.28);overflow:hidden auto;max-height:280px;font-family:'Schibsted Grotesk',system-ui,sans-serif";
  document.body.appendChild(box);
  var items = [], active = -1, timer = null, ctrl = null;
  function close() { box.style.display = "none"; box.innerHTML = ""; items = []; active = -1; input.removeAttribute("aria-expanded"); input.removeAttribute("aria-activedescendant"); }
  function place() { var r = input.getBoundingClientRect(); box.style.left = r.left + "px"; box.style.top = (r.bottom + 8) + "px"; box.style.width = r.width + "px"; }
  function render() {
    if (!items.length) { close(); return; }
    place();
    box.innerHTML = items.map(function (it, i) {
      return '<div role="option" id="era-addr-' + i + '" data-i="' + i + '" style="padding:11px 16px;cursor:pointer;font-size:14.5px;color:#131E3A;background:' + (i === active ? "#F7F4EE" : "#FFFFFF") + ";border-top:" + (i ? "1px solid #EFEAE0" : "0") + '"><div>' + it.text + '</div><div style="margin-top:2px;font-size:12.5px;color:#8A8579">' + it.sub + "</div></div>";
    }).join("");
    box.style.display = "block";
    input.setAttribute("aria-expanded", "true");
    if (active >= 0) input.setAttribute("aria-activedescendant", "era-addr-" + active); else input.removeAttribute("aria-activedescendant");
  }
  function select(i) { var it = items[i]; if (!it) return; input.value = it.full; close(); }
  function search(q) {
    if (ctrl) ctrl.abort();
    ctrl = new AbortController();
    fetch("https://ws.geonorge.no/adresser/v1/sok?sok=" + encodeURIComponent(q) + "&treffPerSide=6&fuzzy=true", { signal: ctrl.signal })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || input.value.trim() !== q) return;
        var list = Array.isArray(data.adresser) ? data.adresser : [];
        items = list.map(function (a) {
          var sub = [a.postnummer, a.poststed].filter(Boolean).join(" ");
          return { text: a.adressetekst || "", sub: sub, full: [a.adressetekst, sub].filter(Boolean).join(", ") };
        });
        active = -1;
        render();
      })
      .catch(function () {});
  }
  input.setAttribute("role", "combobox");
  input.setAttribute("aria-autocomplete", "list");
  input.setAttribute("aria-expanded", "false");
  input.addEventListener("input", function () {
    var q = input.value.trim();
    clearTimeout(timer);
    if (q.length < 3) { close(); return; }
    timer = setTimeout(function () { search(q); }, 250);
  });
  input.addEventListener("keydown", function (e) {
    if (!items.length) return;
    if (e.key === "ArrowDown") { e.preventDefault(); active = Math.min(active + 1, items.length - 1); render(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); active = Math.max(active - 1, 0); render(); }
    else if (e.key === "Enter") { if (active >= 0) { e.preventDefault(); select(active); } }
    else if (e.key === "Escape") { close(); }
  });
  input.addEventListener("blur", function () { setTimeout(close, 150); });
  box.addEventListener("mousedown", function (e) {
    e.preventDefault();
    var row = e.target.closest("[data-i]");
    if (row) select(Number(row.getAttribute("data-i")));
  });
  window.addEventListener("scroll", function () { if (box.style.display === "block") place(); }, { passive: true });
  window.addEventListener("resize", function () { if (box.style.display === "block") place(); });
})();
