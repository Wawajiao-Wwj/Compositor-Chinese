#!/usr/bin/env python3
"""Validate the static page's local assets, anchors, and publication links."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag in ("a", "link") and "href" in attrs:
            self.links.append(attrs["href"])
        if tag == "img":
            self.images.append(attrs)
            self.links.append(attrs.get("src", ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-placeholder", action="store_true", help="For local preview before a GitHub account is connected")
    args = parser.parse_args()
    failures = []
    html = (DOCS / "index.html").read_text()
    page = PageParser()
    page.feed(html)
    if '<html lang="zh-CN">' not in html:
        failures.append("Missing Chinese document language")
    if "<title>" not in html or 'name="viewport"' not in html:
        failures.append("Missing page title or mobile viewport")
    if len(page.ids) != len(set(page.ids)):
        failures.append("Duplicate page IDs")
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            if url.scheme != "https":
                failures.append("Non-HTTPS external link: " + link)
            continue
        if url.path and not (DOCS / unquote(url.path)).is_file():
            failures.append("Missing local asset: " + link)
        if not url.path and url.fragment and url.fragment not in page.ids:
            failures.append("Missing anchor: " + link)
    for img in page.images:
        if "alt" not in img:
            failures.append("Image missing alternative text: " + img.get("src", ""))
    for svg in (DOCS / "assets").glob("*.svg"):
        ET.parse(svg)
    css = (DOCS / "assets/style.css").read_text()
    if "prefers-reduced-motion" not in css or "focus-visible" not in css:
        failures.append("Missing keyboard focus or reduced-motion styles")
    if not args.allow_placeholder:
        candidates = [ROOT / "README.md", ROOT / "RELEASE_NOTES.md", DOCS / "index.html"]
        for file in candidates:
            if re.search(r"__OWNER__|__REPO__", file.read_text()):
                failures.append("Unresolved publication placeholder: " + str(file.relative_to(ROOT)))
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    qualifier = " (local preview; account links pending)" if args.allow_placeholder else ""
    print(f"Page checks passed: {len(page.links)} links/assets, {len(page.images)} images{qualifier}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
