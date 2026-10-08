#!/usr/bin/env python3
"""Render the report HTML and map SVG into their downloadable formats."""
from pathlib import Path
import argparse

import pymupdf
from weasyprint import HTML

from report_collections import collections

DOCS = Path(__file__).resolve().parents[1] / 'docs'
PUBLIC_BASE = 'https://sjain-stanford.github.io/scholar-survey/'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reports-only', action='store_true', help='Render reports without changing map exports')
    args = parser.parse_args()
    # A public base keeps PDF links portable instead of embedding local paths.
    for collection in collections():
        report = HTML(string=(DOCS / (collection['report'] + '.html')).read_text(), base_url=PUBLIC_BASE)
        report.write_pdf(DOCS / (collection['report'] + '.pdf'))
    if args.reports_only:
        print('Rendered both report PDFs; refresh manifests after review')
        return
    svg = (DOCS / 'Comprehensive-Citation-Map.svg').read_text()
    map_html = ('''<!doctype html><html><head><meta charset="utf-8">
<title>Citation Map PDF</title><style>
@page{size:1600px 1140px;margin:0}body{margin:0}svg{display:block}
a{color:#096b83;text-decoration:underline}
.site-url{padding:16px 45px 12px;font:18px/1.4 Arial,sans-serif;color:#173441}
</style></head><body>'''
        + f'<header class="site-url"><b>Interactive Citation Map:</b> <a href="{PUBLIC_BASE}">'
        'sjain-stanford.github.io/scholar-survey/</a></header>'
        + svg + '</body></html>')
    HTML(string=map_html, base_url=PUBLIC_BASE).write_pdf(
        DOCS / 'Comprehensive-Citation-Map.pdf')
    with pymupdf.open(DOCS / 'Comprehensive-Citation-Map.pdf') as document:
        assert len(document) == 1, 'Map must fit on one page'
        page = document[0]
        scale = 2240 / page.rect.width
        page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False).save(
            DOCS / 'Comprehensive-Citation-Map.png')
    print('Rendered both report PDFs and map PDF/PNG; refresh research and delivery manifests after review')


if __name__ == '__main__':
    main()
