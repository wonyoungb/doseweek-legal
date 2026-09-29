#!/usr/bin/env python3
"""Render sitemap.xml: every route's hash page (x-default) and 17 language pages, each with
the route's hreflang alternates. check_site.py compares it with the generated pages."""

from __future__ import annotations

import argparse

from locale_pages import LOCALES, ROOT, ROUTES, sitemap_xml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "sitemap.xml"
    text = sitemap_xml()
    if args.check:
        assert target.read_text(encoding="utf-8") == text, "sitemap.xml is stale; run scripts/render_sitemap.py"
    else:
        target.write_text(text, encoding="utf-8")
    count = len(ROUTES) * (1 + len(LOCALES))
    print(f"OK: sitemap.xml lists {count} URLs ({len(ROUTES)} routes x hash page + {len(LOCALES)} languages), "
          f"each with {len(LOCALES) + 1} hreflang alternates")


if __name__ == "__main__":
    main()
