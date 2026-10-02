# -*- coding: utf-8 -*-
"""Fails when sites/investor/ has drifted from the files it was copied from.

The investor page deploys from its own folder (its own Vercel project), so it carries copies of
pages.css, partner.css, fonts.css, the scripts, the fonts and the images it uses. Change one of the
originals and the copy goes stale without anything noticing. This compares every copied file with its
original and tells you to regenerate.

    python tools/check-investor-sync.py

Regenerate with: python tools/build-partner-story.py (then commit sites/investor/).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "sites", "investor")


def main():
    problems = []
    checked = 0
    for dirpath, _dirs, files in os.walk(SITE):
        for name in files:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, SITE).replace(os.sep, "/")
            if rel in ("index.html", "vercel.json"):
                continue  # generated, not copied
            original = os.path.join(ROOT, *rel.split("/"))
            checked += 1
            if not os.path.isfile(original):
                problems.append("%s finnes ikke lenger i roten" % rel)
                continue
            with open(full, "rb") as a, open(original, "rb") as b:
                if a.read() != b.read():
                    problems.append("%s er ulik originalen" % rel)
    if problems:
        print("INVESTOR SYNC CHECK: %d avvik\n" % len(problems))
        for p in problems:
            print("  FAIL " + p)
        print("\nKjor: python tools/build-partner-story.py  (og commit sites/investor/)")
        return 1
    print("INVESTOR SYNC CHECK: ok - %d kopierte filer er like originalene" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
