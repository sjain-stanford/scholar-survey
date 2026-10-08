#!/usr/bin/env python3
"""Build the Pages entry page from the standalone citation map."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'

STYLE = '''
.controls input,.controls select{max-width:100%;min-width:0}
.controls input{flex:1 1 270px}
.controls select{flex:1 1 240px}
.controls #entry{flex:2 1 350px}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #d68620;outline-offset:3px}
@media(max-width:600px){header{padding:20px}header h1{font-size:25px}.controls{padding:15px 20px}main{padding:12px}.notice{padding:15px;margin:0 12px 12px}}
'''


def build():
    survey = json.loads((DOCS / 'Verification.json').read_text())['survey']
    source = (DOCS / 'Comprehensive-Citation-Map.html').read_text()
    assert source.count('</body>') == 1
    source = source.replace('<title>Comprehensive Google Scholar Citation Map</title>',
        '<title>Sambhav R. Jain — scholarly citation map</title>'
        f'<meta name="description" content="A sourced map of {survey["mapped_works"]} citing works across {survey["countries_territories"]} countries and territories, with marked scholarly discussions and citation research.">')
    source = source.replace('</style>', STYLE + '</style>', 1)
    source = source.replace('<input id="q"', '<input id="q" aria-label="Search institution, city, country or paper"')
    source = source.replace('<select id="country"', '<select id="country" aria-label="Filter by country or territory"')
    source = source.replace('<select id="entry"', '<select id="entry" aria-label="Filter by cited publication"')
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
