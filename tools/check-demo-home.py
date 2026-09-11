# -*- coding: utf-8 -*-
"""Guards the one demo home on /boligeier.

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

# Stale values for THIS home. Scoped to /boligeier: the same figures can be legitimate elsewhere —
# /styret prices ventilation for a different building at 80 000-120 000 kr, and /handverker has a
# different customer at another address. A global ban would flag both.
STALE_BOLIGEIER = {
    "1987": "byggear (skal vare 1967)",
    "80 000–120 000": "gammelt kostnadsestimat (skal vare 85 000–140 000 kr)",
    "80 000 – 120 000": "gammelt kostnadsestimat (skal vare 85 000–140 000 kr)",
    "6,8 mill": "gammel verdi (skal vare 6 250 000 kr)",
    "8,9 mill": "gammel verdi (skal vare 6 250 000 kr)",
}

# Always a typo, on any page.
STALE_ANYWHERE = {
    "Myrveien": "feilstavet adresse (skal vare Myrerveien 46A)",
    "Myreveien": "feilstavet adresse (skal vare Myrerveien 46A)",
}

# Must still be present somewhere on /boligeier, so a rewrite cannot quietly drop the facts.
REQUIRED = ["Myrerveien 46A", "1967", "85 000–140 000 kr", "6 250 000 kr", "162 m²"]

PAGES = ["boligeier", "styret", "handverker", "faghandel"]


def main():
    problems = []

    for slug in PAGES:
        path = os.path.join(ROOT, slug, "index.html")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            html = f.read()
        checks = dict(STALE_ANYWHERE)
        if slug == "boligeier":
            checks.update(STALE_BOLIGEIER)
        for bad, why in checks.items():
            if bad in html:
                problems.append("%s/index.html inneholder %r — %s" % (slug, bad, why))

    path = os.path.join(ROOT, "boligeier", "index.html")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            html = f.read()
        for need in REQUIRED:
            if need not in html:
                problems.append("boligeier/index.html mangler %r fra faktaarket" % need)
    else:
        problems.append("boligeier/index.html finnes ikke — kjor tools/build-pages.py forst")

    if problems:
        print("DEMO HOME CHECK: %d problem(er)\n" % len(problems))
        for p in problems:
            print("  FAIL " + p)
        print("\nFaktaarket ligger i DEMO_HOME i tools/build-pages.py.")
        return 1

    print("DEMO HOME CHECK: ok — Myrerveien 46A er konsistent i alle genererte sider")
    return 0


if __name__ == "__main__":
    sys.exit(main())
