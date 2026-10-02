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

// Conversion events via Vercel Web Analytics custom events (script tag in <head>). Queues silently
// if analytics isn't enabled on the deployment, and never throws. Events carry no address and no
// e-mail, only which form and whether a suggestion was picked.
function eraTrack(name, data) {
  try {
    window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    window.va("event", data ? Object.assign({ name: name }, data) : { name: name });
  } catch (e) {}
}

// Lead forms: every form.lead posts to /api/lead with its own audience. A page can hold more than
// one (hero and closing section on /ny); each form finds its own confirmation and error elements
// among its siblings, so the forms never touch each other.
//
// A form with data-follow="email" (only /ny) is two steps: the address, then an optional e-mail.
// The address call returns an id; the e-mail call sends it back as leadId, and the server stores the
// e-mail as its own document that points at the first. Nothing already stored is rewritten.
document.querySelectorAll("form.lead").forEach(function (form) {
  var scope = form.parentElement;
  var done = scope.querySelector(".done");
  var err = scope.querySelector(".err");
  var btn = form.querySelector("button[type=submit]");
  var label = btn.textContent;
  var follow = form.dataset.follow === "email";
  var which = (form.id || "").replace("era-lead-", "") || "form";
  var track = function (name, extra) { if (follow) eraTrack(name, Object.assign({ page: "ny", form: which }, extra || {})); };
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
      form.elements.value.focus({ preventScroll: el.tagName !== "A" });
    });
  });
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var value = (form.elements.value.value || "").trim();
    var intent = intentInput ? intentInput.value : undefined;
    var website = (form.elements.website && form.elements.website.value || "").trim();
    err.hidden = true;
    if (value.length < 3) { err.textContent = "Skriv inn litt mer, så finner vi riktig sted."; err.hidden = false; return; }
    // The structured fields of the suggestion the visitor picked, but only while the field still
    // holds exactly that text. Anyone who picked and then edited sends the plain text alone.
    var picked = form.elements.value.__eraPicked;
    var address = follow && picked && picked.full === value ? picked.address : undefined;
    btn.disabled = true; btn.textContent = "Sender…";
    track("find_home_started", { picked: !!address });
    try {
      var r = await fetch("/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ audience: form.dataset.audience, value: value, intent: intent, website: website, page: location.href, address: address }) });
      var j = await r.json().catch(function () { return {}; });
      if (r.ok && j.ok) {
        track("find_home_completed", { picked: !!address });
        if (follow) showFollow(j.id, value, address);
        form.hidden = true; done.hidden = false;
        requestAnimationFrame(function () { requestAnimationFrame(function () { done.classList.add("drawn"); }); });
      }
      else { err.textContent = "Noe gikk galt hos oss. Prøv igjen om et øyeblikk."; err.hidden = false; }
    } catch (x) {
      err.textContent = "Ingen kontakt med serveren. Sjekk nettet og prøv igjen."; err.hidden = false;
    }
    btn.disabled = false; btn.textContent = label;
  });

  // Step two on /ny: say what was found (only what Kartverket actually returned for a picked
  // suggestion), then offer to leave an e-mail. Skipping it costs nothing: the address is stored.
  function showFollow(leadId, value, address) {
    var title = done.querySelector("[data-done-title]");
    var sub = done.querySelector("[data-done-sub]");
    var note = done.querySelector("[data-done-note]");
    var fform = done.querySelector("[data-follow-form]");
    if (!title || !sub || !fform) return;
    if (address) {
      // Kartverket returns municipality names in capitals ("NORDRE FOLLO"); show them as names.
      var place = address.kommunenavn ? String(address.kommunenavn).toLowerCase().replace(/(^|[\s-])(\S)/g, function (m, a, b) { return a + b.toUpperCase(); }) + " kommune" : "";
      var matrikkel = address.gardsnummer !== undefined ? "gnr " + address.gardsnummer + " / bnr " + (address.bruksnummer !== undefined ? address.bruksnummer : "-") : "";
      title.textContent = "Vi fant adressen.";
      sub.textContent = [value, [place, matrikkel].filter(Boolean).join(" · ")].filter(Boolean).join(" · ");
    } else {
      title.textContent = "Takk. Vi har adressen din.";
      sub.textContent = value;
    }
    if (!leadId) { if (note) note.hidden = true; return; }
    fform.hidden = false;
    var fbtn = fform.querySelector("button[type=submit]");
    var ferr = fform.querySelector(".follow-err");
    fform.addEventListener("submit", async function (e) {
      e.preventDefault();
      var email = (fform.elements.email.value || "").trim();
      ferr.hidden = true;
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { ferr.textContent = "Skriv inn en e-postadresse, for eksempel navn@epost.no."; ferr.hidden = false; return; }
      var fl = fbtn.textContent;
      fbtn.disabled = true; fbtn.textContent = "Sender…";
      try {
        var r2 = await fetch("/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ audience: form.dataset.audience, followup: "email", leadId: leadId, value: value, email: email, website: (fform.elements.website && fform.elements.website.value || "").trim(), page: location.href }) });
        var j2 = await r2.json().catch(function () { return {}; });
        if (r2.ok && j2.ok) {
          track("email_submitted");
          title.textContent = "Takk.";
          sub.textContent = "Vi sier fra til " + email + " når ERA åpner for boligen din.";
          if (note) note.hidden = true;
          fform.hidden = true;
          return;
        }
        ferr.textContent = "Noe gikk galt hos oss. Prøv igjen om et øyeblikk."; ferr.hidden = false;
      } catch (x) {
        ferr.textContent = "Ingen kontakt med serveren. Sjekk nettet og prøv igjen."; ferr.hidden = false;
      }
      fbtn.disabled = false; fbtn.textContent = fl;
    });
  }
});

// Address autocomplete: on the owner/board pages, each address field gets a Kartverket
// (Geonorge) suggestion dropdown. Any fetch failure degrades silently to a plain text field.
document.querySelectorAll("form.lead").forEach(function (form) {
  var input = form.elements.value;
  if (!input) return;
  if (form.dataset.audience !== "owner" && form.dataset.audience !== "board") return;
  var box = document.createElement("div");
  box.setAttribute("role", "listbox");
  box.style.cssText = "position:fixed;z-index:9999;display:none;background:#FFFFFF;border-radius:16px;box-shadow:0 20px 50px rgba(15,24,48,0.28);overflow:hidden auto;max-height:280px;font-family:'Schibsted Grotesk',system-ui,sans-serif";
  document.body.appendChild(box);
  var items = [], active = -1, timer = null, ctrl = null;
  var optId = "era-addr-" + (input.id || "x") + "-";
  function close() { box.style.display = "none"; box.innerHTML = ""; items = []; active = -1; input.removeAttribute("aria-expanded"); input.removeAttribute("aria-activedescendant"); }
  function place() { var r = input.getBoundingClientRect(); box.style.left = r.left + "px"; box.style.top = (r.bottom + 8) + "px"; box.style.width = r.width + "px"; }
  function render() {
    if (!items.length) { close(); return; }
    place();
    box.innerHTML = items.map(function (it, i) {
      return '<div role="option" id="' + optId + i + '" data-i="' + i + '" style="padding:11px 16px;cursor:pointer;font-size:14.5px;color:#131E3A;background:' + (i === active ? "#F7F4EE" : "#FFFFFF") + ";border-top:" + (i ? "1px solid #EFEAE0" : "0") + '"><div>' + it.text + '</div><div style="margin-top:2px;font-size:12.5px;color:#8A8579">' + it.sub + "</div></div>";
    }).join("");
    box.style.display = "block";
    input.setAttribute("aria-expanded", "true");
    if (active >= 0) input.setAttribute("aria-activedescendant", optId + active); else input.removeAttribute("aria-activedescendant");
  }
  function select(i) {
    var it = items[i]; if (!it) return;
    input.value = it.full; close();
    input.__eraPicked = { full: it.full, address: it.address };
    if (form.dataset.follow === "email") eraTrack("address_selected", { page: "ny", form: (form.id || "").replace("era-lead-", "") });
    var btn = form.querySelector('button[type="submit"]');
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
          var pt = a.representasjonspunkt || {};
          // What Kartverket returned for this suggestion. Sent along only if the visitor picks it.
          var address = {
            text: a.adressetekst, postnummer: a.postnummer, poststed: a.poststed,
            kommunenummer: a.kommunenummer, kommunenavn: a.kommunenavn,
            gardsnummer: a.gardsnummer, bruksnummer: a.bruksnummer, festenummer: a.festenummer, seksjonsnummer: a.seksjonsnummer,
            lat: pt.lat, lon: pt.lon
          };
          return { text: a.adressetekst || "", sub: sub, full: [a.adressetekst, sub].filter(Boolean).join(", "), address: address };
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
});

// Placeholder typewriter: cycles a few real-looking examples through the address/company
// field until the visitor focuses or types, so the empty field feels alive rather than inert.
document.querySelectorAll("form.lead").forEach(function (form) {
  var input = form.elements.value;
  var span = form.querySelector("#lead-typewriter, .lead-typewriter");
  if (!input || !span) return;
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
});

// /ny: the hero headline has two variants under test. B (the category line) is the default;
// ?hero=a swaps in A for side-by-side review.
(function () {
  if (document.body.getAttribute("data-page") !== "ny") return;
  if (new URLSearchParams(location.search).get("hero") !== "a") return;
  var h1 = document.querySelector("[data-hero-h1]");
  var sub = document.querySelector("[data-hero-sub]");
  if (h1 && h1.getAttribute("data-a")) h1.textContent = h1.getAttribute("data-a");
  if (sub && sub.getAttribute("data-a")) sub.textContent = sub.getAttribute("data-a");
})();

// Five-step story: tabs + prev/next. Only the selected scene is in the DOM flow; arrow keys move
// between steps; earlier steps get a faint state. The panel is sized to the tallest scene once, so
// switching tabs never shifts the page.
(function () {
  var nav = document.querySelector(".stepnav");
  if (!nav) return;
  var tabs = [].slice.call(nav.querySelectorAll('[role="tab"]'));
  var panelBox = document.querySelector(".scene-panel");
  var panels = [].slice.call(panelBox.querySelectorAll(".scene"));
  function equalize() {
    var max = 0;
    panels.forEach(function (p) { var was = p.hidden; p.hidden = false; p.style.visibility = "hidden"; max = Math.max(max, p.offsetHeight); p.style.visibility = ""; p.hidden = was; });
    panelBox.style.minHeight = max ? max + "px" : "";
  }
  function show(i, focusTab) {
    i = Math.max(0, Math.min(tabs.length - 1, i));
    tabs.forEach(function (t, j) { t.setAttribute("aria-selected", j === i ? "true" : "false"); t.tabIndex = j === i ? 0 : -1; t.classList.toggle("is-past", j < i); });
    panels.forEach(function (p, j) { p.hidden = j !== i; p.classList.remove("is-entering"); });
    void panels[i].offsetWidth; panels[i].classList.add("is-entering");
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
  panelBox.querySelectorAll(".scene-nav button").forEach(function (b) {
    b.addEventListener("click", function () {
      var cur = panels.findIndex(function (p) { return !p.hidden; });
      show(cur + Number(b.getAttribute("data-dir")), true);
    });
  });
  var t; window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(equalize, 120); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(equalize); else equalize();
  equalize();
})();

// [data-reveal]: adds .is-in when the element scrolls into view, which starts its CSS transition (the
// documents on /ny that lie scattered and gather). With reduced motion, or without IntersectionObserver,
// it starts in its final state.
(function () {
  var els = [].slice.call(document.querySelectorAll("[data-reveal]"));
  if (!els.length) return;
  var show = function (el) { el.classList.add("is-in"); };
  if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) { els.forEach(show); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { show(e.target); io.unobserve(e.target); } });
  }, { threshold: 0.35 });
  els.forEach(function (el) { io.observe(el); });
})();

// /ny: bevegelse. Regel: bevegelse forklarer hva ERA gjør. Her ligger det som følger scrollen eller
// svarer på et trykk: menyen som følger flaten under seg, reisen som våkner steg for steg, badet som
// går fra behov til dokumentasjon, og huset som går gjennom årstidene. Ingenting looper. Med redusert
// bevegelse står alt i sluttstilling.
(function () {
  var page = document.body.getAttribute("data-page");
  if (page !== "ny" && page !== "om-era-ny") return;
  document.body.classList.add("has-js");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var narrow = window.matchMedia("(max-width: 899px)").matches;
  var run = [];
  var queued = false;
  function frame() { queued = false; run.forEach(function (f) { f(); }); }
  function queue() { if (!queued) { queued = true; requestAnimationFrame(frame); } }
  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", queue);
  // How far through an element the viewport has come: 0 when its top is at `start` of the viewport height,
  // 1 when it has moved `span` of its own height further up.
  function progress(el, start, span) {
    var r = el.getBoundingClientRect();
    var t = (window.innerHeight * start - r.top) / (r.height * span);
    return Math.max(0, Math.min(1, t));
  }
  function stepsFor(t, n) { return t <= 0 ? 0 : Math.max(1, Math.ceil(t * n - 0.001)); }

  // The menu follows the surface under it: dark on cinematic scenes, light on light ones, and a little
  // lower once the page has been scrolled.
  var tones = [].slice.call(document.querySelectorAll("[data-nav]"));
  run.push(function () {
    var tone = "dark";
    for (var i = 0; i < tones.length; i++) {
      var r = tones[i].getBoundingClientRect();
      if (r.top <= 40 && r.bottom > 40) { tone = tones[i].getAttribute("data-nav"); break; }
    }
    document.body.classList.toggle("nav-light", tone === "light");
    document.body.classList.toggle("nav-compact", window.scrollY > 40);
  });

  // Din bolig. Én agent.: the five steps wake in order, and when the last is awake a line is drawn back to
  // the first. On a phone the row is swiped, so every step is awake from the start.
  var flow = document.querySelector(".flow");
  if (flow) {
    var steps = [].slice.call(flow.querySelectorAll(".flow-step"));
    var back = flow.querySelector(".flow-return");
    var awake = 0;
    flow.classList.add("flow-js");
    var wake = function (n) {
      if (n <= awake) return;
      awake = n;
      steps.forEach(function (s, i) { s.classList.toggle("is-active", i < n); });
      if (back && n >= steps.length) back.classList.add("is-drawn");
    };
    if (reduced || narrow) wake(steps.length);
    else run.push(function () { wake(stepsFor(progress(flow, 0.78, 0.7), steps.length)); });
  }

  // Badet: the steps light up in order. The choices are real, and the one people reach for answers with what
  // has already been done for them.
  var list = document.querySelector("#slik .cine-flow");
  if (list) {
    var items = [].slice.call(list.children);
    var lit = 0;
    var note = list.querySelector(".cine-note");
    var chips = [].slice.call(list.querySelectorAll(".cine-chip"));
    list.classList.add("step-js");
    var light = function (n) {
      if (n <= lit) return;
      lit = n;
      items.forEach(function (li, i) { li.classList.toggle("is-active", i < n); });
    };
    if (reduced) light(items.length);
    else run.push(function () { light(stepsFor(progress(list, 0.85, 0.85), items.length)); });
    var say = function (b) { if (note) { note.textContent = b.getAttribute("data-note"); note.classList.add("is-on"); } };
    chips.forEach(function (b) {
      b.addEventListener("click", function () {
        chips.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
        say(b);
      });
      b.addEventListener("mouseenter", function () { say(b); });
    });
  }

  // Boligen husker: the house moves through the seasons with the scroll, not on a timer.
  var host = document.querySelector("#husker");
  var sea = host && host.querySelector(".seasons");
  if (sea && !reduced) {
    var imgs = [].slice.call(sea.querySelectorAll("img"));
    var cur = 0;
    run.push(function () {
      var r = host.getBoundingClientRect();
      var t = (window.innerHeight * 0.85 - r.top) / (r.height + window.innerHeight * 0.3);
      var idx = Math.floor(Math.max(0, Math.min(0.999, t)) * imgs.length);
      if (idx === cur) return;
      cur = idx;
      imgs.forEach(function (im, i) { im.classList.toggle("is-on", i === idx); });
    });
  }

  queue();
})();
