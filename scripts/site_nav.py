"""Shared top navigation for the map entry page and the report HTML."""
from html import escape

ITEMS = [('map', 'index.html', 'Citation map'),
         ('report', 'Substantive-Citation-Report.html', 'Substantive report'),
         ('packet', 'Selected-Discussion-Pages.pdf', 'Marked discussions')]
DATA = [('Substantive-Citation-Report.pdf', 'Report PDF'),
        ('Comprehensive-Citation-Map.pdf', 'Citation map PDF'),
        ('Selected-Articles.csv', 'Selected articles (CSV)'),
        ('Citation-Inventory.csv', 'Citation inventory (CSV)'),
        ('Coverage-by-Publication.csv', 'Survey coverage (CSV)'),
        ('Map-Affiliation-Ledger.csv', 'Affiliation sources (CSV)')]
# The report stylesheet is also used for PDF rendering, so the bar is hidden in print.
CSS = ('.site-nav{display:flex;align-items:center;flex-wrap:wrap;gap:4px 18px;padding:9px 32px;background:#0c2c38;'
       'font:14px/1.4 Arial,sans-serif}.site-nav a,.site-nav summary{color:#d7e8ec;text-decoration:none;cursor:pointer}'
       '.site-nav a:hover,.site-nav summary:hover{color:#fff;text-decoration:underline}'
       '.site-nav a[aria-current]{color:#fff;font-weight:700}.site-nav .brand{color:#fff;font-weight:700;margin-right:10px}'
       '.site-nav details{position:relative}.site-nav summary{list-style:none}.site-nav summary::-webkit-details-marker{display:none}'
       '.site-nav summary::after{content:" \\25BE"}.site-nav details ul{position:absolute;z-index:10;left:0;top:calc(100% + 8px);'
       'min-width:230px;margin:0;padding:6px 0;list-style:none;background:#fff;border:1px solid #c9dbe0;border-radius:6px;'
       'box-shadow:0 6px 18px rgba(12,44,56,.18)}.site-nav details li a{display:block;padding:6px 14px;color:#0b5f70}'
       '.site-nav details li a:hover{background:#eef5f7;color:#0b5f70}'
       '.site-nav a:focus-visible,.site-nav summary:focus-visible{outline:3px solid #d68620;outline-offset:3px}'
       '@media(max-width:600px){.site-nav{padding:9px 16px}.site-nav .brand{display:none}}'
       '@media print{.site-nav{display:none}}')


def nav(current):
    links = ''.join(f'<a href="{href}"' + (' aria-current="page"' if key == current else '') + f'>{escape(label)}</a>'
                    for key, href, label in ITEMS)
    downloads = ''.join(f'<li><a href="{href}">{escape(label)}</a></li>' for href, label in DATA)
    return (f'<nav class="site-nav" aria-label="Site"><span class="brand">Sambhav R. Jain · Citation research</span>'
            f'{links}<details><summary>Data</summary><ul>{downloads}</ul></details></nav>')
