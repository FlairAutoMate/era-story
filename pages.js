// Mobile menu: the pill's button toggles the panel; any link in it closes it.
(function () {
  var btn = document.querySelector("[data-menu-toggle]");
  var panel = document.querySelector(".menu-panel");
  if (!btn || !panel) return;
  var set = function (open) { panel.hidden = !open; document.body.classList.toggle("menu-open", open); btn.textContent = open ? "×" : "☰"; btn.setAttribute("aria-expanded", open ? "true" : "false"); btn.setAttribute("aria-label", open ? "Lukk menyen" : "Åpne menyen"); };
  btn.addEventListener("click", function () { set(panel.hidden); });
  panel.addEventListener("click", function (e) { if (e.target.closest("a")) set(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) { set(false); btn.focus(); } });
  document.addEventListener("pointerdown", function (e) { if (!panel.hidden && !e.target.closest("nav")) set(false); });
})();

// Audience pages: the lead form posts to /api/lead with the page's audience.
(function () {
  var form = document.getElementById("era-lead");
  if (!form) return;
  var done = document.querySelector(".done");
  var err = document.querySelector(".err");
  var btn = form.querySelector("button[type=submit]");
  var label = btn.textContent;
  // Intent toggle (e.g. "Meld interesse" / "Be om demo"): a hidden field, the submit label
  // and the confirmation text follow the chosen button. Pages without a toggle skip all of it.
  var intentInput = form.elements.intent;
  var intentTexts = {};
  try { intentTexts = JSON.parse(form.dataset.intents || "{}"); } catch (x) {}
  document.querySelectorAll("[data-intent]").forEach(function (el) {
    el.addEventListener("click", function () {
      if (!intentInput) return;
      var k = el.getAttribute("data-intent");
      intentInput.value = k;
      document.querySelectorAll(".intent [data-intent]").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-intent") === k ? "true" : "false"); });
      label = el.getAttribute("data-label") || label; btn.textContent = label;
      var t = intentTexts[k]; if (t) { done.querySelector("b").textContent = t[0]; done.querySelector("span").textContent = t[1]; }
      if (el.tagName === "A") { form.scrollIntoView({ block: "center" }); }
      document.getElementById("lead-value").focus({ preventScroll: el.tagName !== "A" });
    });
  });
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var value = (form.elements.value.value || "").trim();
    var intent = intentInput ? intentInput.value : undefined;
    var website = (form.elements.website && form.elements.website.value || "").trim();
    err.hidden = true;
    if (value.length < 3) { err.textContent = "Skriv inn litt mer, så finner vi riktig sted."; err.hidden = false; return; }
    btn.disabled = true; btn.textContent = "Sender…";
    try {
      var r = await fetch("/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ audience: form.dataset.audience, value: value, intent: intent, website: website, page: location.href }) });
      var j = await r.json().catch(function () { return {}; });
      if (r.ok && j.ok) {
        form.hidden = true; done.hidden = false;
        requestAnimationFrame(function () { requestAnimationFrame(function () { done.classList.add("drawn"); }); });
      }
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
  function select(i) {
    var it = items[i]; if (!it) return;
    input.value = it.full; close();
    var btn = input.closest("form") && input.closest("form").querySelector('button[type="submit"]');
    if (btn && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      btn.animate([{ boxShadow: "0 0 0 0 rgba(212,177,122,0.6)" }, { boxShadow: "0 0 0 4px rgba(212,177,122,0.35)" }, { boxShadow: "0 0 0 14px rgba(212,177,122,0)" }], { duration: 900, easing: "ease-out", iterations: 2 });
    }
  }
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

// Placeholder typewriter: cycles a few real-looking examples through the address/company
// field until the visitor focuses or types, so the empty field feels alive rather than inert.
(function () {
  var form = document.getElementById("era-lead");
  var input = document.getElementById("lead-value");
  var span = document.getElementById("lead-typewriter");
  if (!form || !input || !span) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var EXAMPLES = {
    owner: ["Storgata 1, Oslo", "Kirkeveien 44, Bergen", "Skogveien 12, Trondheim"],
    board: ["Sameiet Solsiden, Oslo", "Borettslaget Utsikten, Bergen", "Sameiet Fjordblikk, Stavanger"],
    pro: ["Byggmester Hansen AS", "Mester Rørlegger AS", "987 654 321"],
    partner: ["Byggmakker Lillestrøm", "Montér Sandvika", "XL-BYGG Ringerike"]
  };
  var list = EXAMPLES[form.dataset.audience] || EXAMPLES.owner;
  var stopped = false;
  function stop() { stopped = true; span.style.display = "none"; }
  input.addEventListener("focus", stop, { once: true });
  input.addEventListener("pointerdown", stop, { once: true });
  input.addEventListener("input", stop, { once: true });
  var exIdx = 0;
  function after(ms, fn) { if (!stopped) setTimeout(fn, ms); }
  function eraseFrom(text, j) {
    if (j < 0) { exIdx++; after(300, nextWord); return; }
    span.textContent = text.slice(0, j);
    after(25, function () { eraseFrom(text, j - 1); });
  }
  function typeFrom(text, i) {
    if (i > text.length) { after(1300, function () { eraseFrom(text, text.length); }); return; }
    span.textContent = text.slice(0, i);
    after(45, function () { typeFrom(text, i + 1); });
  }
  function nextWord() { typeFrom(list[exIdx % list.length], 0); }
  nextWord();
})();

// Five-step story: tabs + prev/next. Only the selected scene is in the DOM flow; arrow keys move
// between steps; earlier steps get a faint "done" state.
(function () {
  var nav = document.querySelector(".stepnav");
  if (!nav) return;
  var tabs = [].slice.call(nav.querySelectorAll('[role="tab"]'));
  var panels = [].slice.call(document.querySelectorAll(".scene-panel .scene"));
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function show(i, focusTab) {
    i = Math.max(0, Math.min(tabs.length - 1, i));
    tabs.forEach(function (t, j) { t.setAttribute("aria-selected", j === i ? "true" : "false"); t.tabIndex = j === i ? 0 : -1; t.classList.toggle("is-past", j < i); });
    panels.forEach(function (p, j) { p.hidden = j !== i; });
    if (!reduce && panels[i].animate) panels[i].animate([{ opacity: 0.4 }, { opacity: 1 }], { duration: 220, easing: "ease-out" });
    if (focusTab) tabs[i].focus();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { show(i); });
    t.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); show(i + 1, true); }
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp") { e.preventDefault(); show(i - 1, true); }
      else if (e.key === "Home") { e.preventDefault(); show(0, true); }
      else if (e.key === "End") { e.preventDefault(); show(tabs.length - 1, true); }
    });
  });
  document.querySelectorAll(".scene-nav button").forEach(function (b) {
    b.addEventListener("click", function () {
      var cur = panels.findIndex(function (p) { return !p.hidden; });
      show(cur + Number(b.getAttribute("data-dir")), true);
    });
  });
})();
