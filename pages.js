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
