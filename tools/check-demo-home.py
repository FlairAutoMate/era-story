# -*- coding: utf-8 -*-
"""Guards the one demo home on /boligeier.

Since the positioning change of 3 Oct 2026 the example home is fictitious (Eksempelveien 12): no real street, no value
estimate and no real firm. The ERA Bolig screenshots still carry the old values inside the PNG files until they are
re-exported, see README. History of this guard: 
Every ERA Bolig screenshot on that page shows the same home, Myrerveien 46A. Three different
values for it have already shipped by accident (6,8 mill. / 8,9 mill. / 6 250 000), two different
estimates for the same job (80 000-120 000 / 85 000-140 000), two byggear (1987 / 1967) and two
misspellings of the address. Each one was caught by eye, late.

This fails the moment a stale value reappears in a generated page, and when a value from the fact
sheet in tools/build-pages.py has gone missing from the text.

    python tools/check-demo-home.py

Note: this reads the generated HTML, which is where the alt texts and copy live. It cannot see
inside a PNG. When a screenshot is re-exported, check the image by eye and make the alt text match;
this guard then keeps them from drifting apart afterwards.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Stale values for THIS home. Scoped to /boligeier and the front page / (both show Myrerveien 46A): the same figures can be legitimate elsewhere —
# /styret prices ventilation for a different building at 80 000-120 000 kr, and /handverker has a
# different customer at another address. A global ban would flag both.
STALE_BOLIGEIER = {
    "1987": "byggear (skal vare 1967)",
    "80 000–120 000": "gammelt kostnadsestimat (skal vare 85 000–140 000 kr)",
    "80 000 – 120 000": "gammelt kostnadsestimat (skal vare 85 000–140 000 kr)",
    "6,8 mill": "gammel verdi (skal vare 6 250 000 kr)",
    "8,9 mill": "gammel verdi (skal vare 6 250 000 kr)",
}

# Always wrong, on any page. Borgveien was the old street name and is now Myrerveien everywhere;
# the only place it may still appear is the search string in tools/rebase-deltas.py, which has to
# keep matching the vendor export verbatim, and that file is not scanned here.
STALE_ANYWHERE = {
    "Myrveien": "feilstavet adresse",
    "Myreveien": "feilstavet adresse",
    "Borgveien": "gammelt gatenavn",
}

# The example home is fictitious and shows no value estimate. Checked on the generated pages only; the archived story
# keeps its old figures.
STALE_EXAMPLE = {
    "Myrerveien 46A": "ekte adresse i eksempeldata (skal vare Eksempelveien 12)",
    "Estimert verdi": "ERA viser ikke boligverdi (den hører til Hjemla)",
    "estimert verdi": "ERA viser ikke boligverdi (den hører til Hjemla)",
    "6 250 000": "boligverdi i eksempeldata (ERA viser ikke verdi)",
    "Oslo Fasade": "ekte firmanavn i eksempeldata (skal vare Fasadeeksperten (eksempel))",
}

# Screens whose values are still stale. Empty since 11. sept. 2026: all five ERA Bolig screens now
# carry the fact sheet. Add an entry here only as a deliberate, temporary allowance — a value that
# is on screen and therefore in the alt text, but not yet corrected — and empty it again when the
# screen is re-exported, so the value goes back to being a hard failure.
#
# NB: this guard reads generated HTML and cannot see inside a PNG. Text that appears only in a
# screenshot is not covered. Known open items of that kind are listed in README under
# «Produktflater på /boligeier».
PENDING_REEXPORT = {}

# Must still be present somewhere on /boligeier, so a rewrite cannot quietly drop the facts.
REQUIRED = ["Eksempelveien 12", "1967", "85 000–140 000 kr", "162 m²"]

PAGES = ["boligeier", "styret", "handverker", "faghandel", "", "ny/om-era", "partnere"]

# The street name is checked on the story and partner pages too, not just the audience subpages.
EXTRA_FILES = ["historie/index.html", "om-era/index.html"]


def main():
    problems = []

    warnings = []

    for slug in PAGES:
        path = os.path.join(ROOT, slug, "index.html")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            html = f.read()
        checks = dict(STALE_ANYWHERE)
        checks.update(STALE_EXAMPLE)
        if slug in ("boligeier", ""):
            checks.update(STALE_BOLIGEIER)
        for bad, why in checks.items():
            if bad not in html:
                continue
            if slug in ("boligeier", "") and bad in PENDING_REEXPORT:
                warnings.append("%s/index.html inneholder fortsatt %r — %s"
                                % (slug, bad, PENDING_REEXPORT[bad]))
            else:
                problems.append("%s/index.html inneholder %r — %s" % (slug, bad, why))

    for rel in EXTRA_FILES:
        path = os.path.join(ROOT, *rel.split("/"))
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            html = f.read()
        for bad, why in STALE_ANYWHERE.items():
            if bad in html:
                problems.append("%s inneholder %r — %s" % (rel, bad, why))

    path = os.path.join(ROOT, "boligeier", "index.html")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            html = f.read()
        for need in REQUIRED:
            if need not in html:
                problems.append("boligeier/index.html mangler %r fra faktaarket" % need)
    else:
        problems.append("boligeier/index.html finnes ikke — kjor tools/build-pages.py forst")

    for w in warnings:
        print("  ADVARSEL " + w)
    if warnings:
        print("")

    if problems:
        print("DEMO HOME CHECK: %d problem(er)\n" % len(problems))
        for p in problems:
            print("  FAIL " + p)
        print("\nFaktaarket ligger i DEMO_HOME i tools/build-pages.py.")
        return 1

    print("DEMO HOME CHECK: ok — Eksempelveien 12 er konsistent i alle genererte sider")
    if warnings:
        print("%d skjermbilde-verdi(er) venter pa ny eksport, se PENDING_REEXPORT." % len(warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
