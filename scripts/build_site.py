#!/usr/bin/env python3
"""Build the Pages entry page from the standalone citation map.

rebuild_map.py writes the complete map page (navigation, header link and report badges come from
map_page.py); the entry page is an identical copy so the offline and published maps stay consistent.
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def build():
    source = (DOCS / 'Comprehensive-Citation-Map.html').read_text()
    assert source.count('</body>') == 1 and 'class="site-nav"' in source, 'Run scripts/rebuild_map.py first'
    return source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Fail if the committed entry page is stale')
    args = parser.parse_args()
    result = build()
    target = DOCS / 'index.html'
    if args.check:
        assert target.read_text() == result, 'docs/index.html is stale; run scripts/build_site.py'
        assert (DOCS / '.nojekyll').is_file(), 'Missing docs/.nojekyll'
        print('Entry page is current')
    else:
        target.write_text(result)
        (DOCS / '.nojekyll').touch()
        print('Built docs/index.html for GitHub Pages')


if __name__ == '__main__':
    main()
