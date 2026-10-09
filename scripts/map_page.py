"""Site presentation of the citation map page: title, navigation, header link and report badges.

rebuild_map.py applies decorate() to the standalone map, which it also reads back, so every step is
idempotent. docs/index.html is a copy of the decorated standalone map.
"""
import csv
import json
import re
from pathlib import Path

import site_nav

DOCS = Path(__file__).resolve().parents[1] / 'docs'
REPORT_LABEL = re.compile(r'Selected substantive review, article (\d+)')
STYLE = '''/*site-chrome*/
.controls input,.controls select{max-width:100%;min-width:0}
.controls input{flex:1 1 270px}
.controls select{flex:1 1 240px}
.controls #entry{flex:2 1 350px}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #d68620;outline-offset:3px}
@media(max-width:600px){header{padding:20px}header h1{font-size:25px}.controls{padding:15px 20px}main{padding:12px}.notice{padding:15px;margin:0 12px 12px}}
header .heading{flex:1 1 520px;min-width:0}header p.cta-row{opacity:1;margin:14px 0 0}
.cta{display:inline-block;padding:8px 15px;border-radius:6px;background:#fff;color:#0c4f5f;font-weight:700;text-decoration:none}
.cta::after{content:" \\2192"}.cta:hover{background:#e7f3f5;text-decoration:underline}
.report-badge{display:inline-block;margin:3px 0 1px;padding:1px 6px;border-radius:3px;background:#e7f3ee;color:#20664d;font-size:11px;font-weight:700;text-decoration:none;white-space:nowrap}
.report-badge:hover{text-decoration:underline}.ids{margin-top:2px;font-size:11px;color:#8197a0}
''' + site_nav.CSS + '/*end-site-chrome*/'
ARIA = [('<input id="q"', ' aria-label="Search institution, city, country or paper"'),
        ('<select id="country"', ' aria-label="Filter by country or territory"'),
        ('<select id="entry"', ' aria-label="Filter by cited publication"')]
DETAIL_HEADING = ("function show(g){let h='<h2>'+esc(g.city)+'</h2><p>'+esc(g.country)+' · '+new Set(g.locations"
                  ".flatMap(l=>l.papers.map(p=>p.work_id))).size+' citing works</p>';")
DETAIL_PAPER = ("for(const p of l.papers)h+='<div class=\"paper\"><b>'+esc(p.title)+'</b><br><a href=\"'+esc(p.proof)+'\" "
                "target=\"_blank\">Affiliation proof, original p. '+p.page+'</a> · <a href=\"'+esc(p.source)+'\" "
                "target=\"_blank\">Original</a><div class=\"small\">'+esc(p.work_id)+' · '+esc(p.evidence)+'</div></div>'")
REPORT_HEADING = ("function show(g){const ids=new Set(g.locations.flatMap(l=>l.papers.map(p=>p.work_id))),"
                  "inReport=[...ids].filter(w=>REPORT[w]).length;let h='<h2>'+esc(g.city)+'</h2><p>'+esc(g.country)+' · '"
                  "+ids.size+' citing works'+(inReport?' · '+inReport+' in the report':'')+'</p>';")
REPORT_PAPER = ("for(const p of l.papers){const n=REPORT[p.work_id]?String(REPORT[p.work_id]).padStart(2,'0'):'';"
                "h+='<div class=\"paper\"><b>'+esc(p.title)+'</b>'+(n?' <a class=\"report-badge\" "
                "href=\"Substantive-Citation-Report.html#article-'+n+'\">Report article '+n+'</a>':'')+'<br><a href=\"'"
                "+esc(p.proof)+'\" target=\"_blank\">Affiliation proof, original p. '+p.page+'</a> · <a href=\"'"
                "+esc(p.source)+'\" target=\"_blank\">Original</a><div class=\"ids\">'+esc(p.work_id)+' · '"
                "+esc(p.evidence)+'</div></div>'}")


def heading(survey):
    return ('<div class="heading"><h1>Global reach of research citing Sambhav\u00a0R.\u00a0Jain’s work</h1>'
            '<p>Most-cited work: Trained Quantization Thresholds (TQT), MLSys 2020 · '
            'Google Scholar snapshot · 7\u00a0October\u00a02026</p>'
            f'<p class="cta-row"><a class="cta" href="Substantive-Citation-Report.html">Read the Substantive Citation '
            f'Report · {survey["selected_articles"]} articles</a></p></div>')


def report_articles():
    """Map each citing work in the substantive report to its article number."""
    with (DOCS / 'Citation-Inventory.csv').open(newline='') as handle:
        return {row['work_id']: int(match[1]) for row in csv.DictReader(handle)
                if (match := REPORT_LABEL.fullmatch(row['discussion_review']))}


def decorate(text, survey):
    title = ('<title>Sambhav R. Jain — scholarly citation map</title>'
             f'<meta name="description" content="A sourced map of {survey["mapped_works"]} citing works across '
             f'{survey["countries_territories"]} countries and territories, with marked scholarly discussions and '
             'citation research.">')
    text = re.sub(r'<title>.*?</title>(<meta name="description"[^>]*>)?', lambda _: title, text, count=1)
    text = re.sub(r'/\*site-chrome\*/.*?/\*end-site-chrome\*/', '', text, flags=re.S)
    text = text.replace('</style>', STYLE + '</style>', 1)
    text = re.sub(r'<nav class="site-nav".*?</nav>', '', text, count=1, flags=re.S)
    assert text.count('<body>') == 1
    text = text.replace('<body>', '<body>' + site_nav.nav('map'))
    for tag, label in ARIA:
        if tag + label not in text:
            assert text.count(tag) == 1, tag
            text = text.replace(tag, tag + label)
    # The pin panel links each work in the substantive report to its article entry.
    articles = json.dumps(report_articles(), sort_keys=True, separators=(',', ':'))
    text = re.sub(r'const REPORT=\{[^}]*\};', '', text, count=1)
    assert text.count("const NS='http://www.w3.org/2000/svg';") == 1
    text = text.replace("const NS='http://www.w3.org/2000/svg';",
                        f"const REPORT={articles};const NS='http://www.w3.org/2000/svg';")
    text = text.replace(DETAIL_HEADING, REPORT_HEADING).replace(DETAIL_PAPER, REPORT_PAPER)
    assert text.count(REPORT_HEADING) == 1 and text.count(REPORT_PAPER) == 1
    return text
