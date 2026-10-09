#!/usr/bin/env python3
"""Regenerate map data and static geography from the reviewed affiliation ledger."""
import csv,json,math,re
from pathlib import Path
from html import escape
import map_page
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs'
def read(name):return list(csv.DictReader((D/name).open()))
# Headline figures as boxed cards on the right of the header; they wrap below the title on narrow screens.
HEADER_STYLE=('/*header-metrics*/header{display:flex;justify-content:space-between;align-items:center;gap:20px 32px;flex-wrap:wrap}'
 'header .metrics{display:flex;gap:12px;margin:0;flex:0 0 auto}'
 'header .metrics span{display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:120px;padding:10px 18px;'
 'border:1px solid rgba(255,255,255,.4);border-radius:10px;background:rgba(255,255,255,.1);font-size:13px;text-align:center}'
 'header .metrics b{font-size:38px;line-height:1.05;margin:0 0 3px}'
 '@media(max-width:700px){header .metrics{flex:1 1 100%}header .metrics span{flex:1 1 0;min-width:0;padding:8px 6px;font-size:11px}'
 'header .metrics b{font-size:28px}}/*end-header-metrics*/')
def build():
 ledger=read('Map-Affiliation-Ledger.csv');inv={r['work_id']:r for r in read('Citation-Inventory.csv')};v=json.loads((D/'Verification.json').read_text());s=v['survey']
 groups={}
 for r in ledger:
  country_only=r['precision']=='country only';city='Country-level affiliation' if country_only else r['city'];key=(country_only,city,r['country'])
  g=groups.setdefault(key,dict(city=city,country=r['country'],longitude=float(r['longitude']),latitude=float(r['latitude']),country_only=country_only,locations={},work_ids=set()))
  loc=g['locations'].setdefault(r['pin_id'],dict(pin_id=r['pin_id'],institution=r['institution'],precision=r['precision'],papers=[]))
  paper=dict(work_id=r['work_id'],title=r['title'],proof=r['proof_link'],source=r['source_url'],page=r['source_page'],evidence=r['source_evidence'],entries=[int(x) for x in inv[r['work_id']]['cites_profile_entries'].split('; ')])
  if not any(p['work_id']==paper['work_id'] and p['proof']==paper['proof'] for p in loc['papers']):loc['papers'].append(paper)
  g['work_ids'].add(r['work_id'])
 data=sorted(groups.values(),key=lambda g:(g['country'],g['city']))
 for i,g in enumerate(data,1):g['marker']=i;g['locations']=list(g['locations'].values());g['work_ids']=sorted(g['work_ids'])
 assert len({w for g in data for w in g['work_ids']})==s['mapped_works']
 assert sum(len(g['locations']) for g in data)==s['institution_locations']
 text=(D/'Comprehensive-Citation-Map.html').read_text();tail=text.split('const DATA=',1)[1];_,end=json.JSONDecoder().raw_decode(tail)
 text=text.split('const DATA=',1)[0]+'const DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+tail[end:]
 metrics=f'<span><b>{s["countries_territories"]}</b> countries / territories</span><span><b>{s["mapped_works"]}</b> mapped works</span><span><b>{s["institution_locations"]}</b> institution / location entries</span>'
 heading=map_page.heading(s)
 text=re.sub(r'<header>.*?</header>',lambda _:'<header>'+heading+'<div class="metrics">'+metrics+'</div></header>',text,count=1,flags=re.S)
 text=re.sub(r'/\*header-metrics\*/.*?/\*end-header-metrics\*/','',text,flags=re.S).replace('</style>',HEADER_STYLE+'</style>',1)
 notice=f'''<b>Research reach:</b> {s['mapped_works']} Scholar-catalogued works have sourced publication affiliations across {s['countries_territories']} countries/territories. The inventory retains {s['deduplicated_works']} grouped works from 337 archived Scholar records; the saved profile records 354 citations. These are distinct measures, not a complete unique-citation census. Mapping includes coauthor/employer links, thesis previews and source-version discrepancies. Affiliations do not establish adoption or endorsement. City geography uses the publication or reviewed ROR records; hollow pins indicate country-only placement. <a href="Coverage-by-Publication.csv">Coverage</a> · <a href="Map-Affiliation-Ledger.csv">Affiliation sources</a> · <a href="Work-ID-Corrections.csv">ID corrections</a>.'''
 text=re.sub(r'<div class="notice">.*?</div>',lambda _: '<div class="notice">'+notice+'</div>',text,count=1,flags=re.S)
 text=map_page.decorate(text,s)
 (D/'Comprehensive-Citation-Map.html').write_text(text)
 # Reuse the committed map's Natural Earth path geometry, a preserved original asset.
 world=re.search(r'<g class="land">(.*?)</g>',text,re.S)[1]
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1080" viewBox="0 0 1600 1080"><rect width="1600" height="1080" fill="white"/><style>text{font-family:Arial,sans-serif;fill:#193b49}.land path{fill:#e1ebed;stroke:white;stroke-width:.6}.map-heading text{fill:white}</style>']
 def txt(x,y,t,size=18,bold=False):svg.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{700 if bold else 400}">{escape(t)}</text>')
 svg.append('<rect width="1600" height="100" fill="#123d4c"/><g class="map-heading">')
 txt(45,52,'Global reach of research citing Sambhav R. Jain’s work',31,True);txt(45,84,'Most-cited work: Trained Quantization Thresholds (TQT), MLSys 2020 · Google Scholar snapshot · 7 October 2026',18)
 txt(1120,45,f"{s['countries_territories']} countries / territories",24,True);txt(1120,75,f"{s['mapped_works']} works with sourced affiliations",17);svg.append('</g>')
 def panel(name,x,y,w,h,bounds):
  lo,la,hi,ha=bounds; sx=w/((hi-lo)/360*1200);sy=h/((ha-la)/145*485)
  tx=x-((lo+180)/360*1200)*sx;ty=y-((85-ha)/145*485)*sy
  svg.append(f'<defs><clipPath id="{name}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f6f9fa"/><g clip-path="url(#{name})"><g class="land" transform="translate({tx} {ty}) scale({sx} {sy})">{world}</g>')
  for g in data:
   lon,lat=g['longitude'],g['latitude']
   if not lo<=lon<=hi or not la<=lat<=ha:continue
   px=x+(lon-lo)/(hi-lo)*w;py=y+(ha-lat)/(ha-la)*h;r=4.4+min(5,math.log2(len(g['work_ids'])+1))*.75;col='#b16b22' if g['country_only'] else '#0d8091'
   svg.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{r:.2f}" fill="'+('white' if g['country_only'] else col)+f'" stroke="{col}" stroke-width="1.7" opacity=".9"><title>{escape(g["city"]+", "+g["country"])}</title></circle>')
  svg.append('</g>')
 panel('world',45,110,1510,455,(-180,-60,180,85))
 for name,label,x,bounds in [('na','North America',45,(-130,22,-60,57)),('eu','Europe',565,(-12,35,42,65)),('ea','East Asia',1085,(95,18,145,49))]:txt(x,604,label,21,True);panel(name,x,620,470,280,bounds)
 txt(45,940,f"{s['institution_locations']} institution/location entries · {len(data)} display groups · {s['mapped_works']} of {s['deduplicated_works']} retained works mapped",19,True)
 txt(45,972,'Solid: publication or registry city. Hollow: country only. Affiliations do not imply independent adoption or endorsement.',16)
 txt(45,1001,'Includes thesis previews and source-version discrepancies. Archived Scholar records: 337; profile citations: 354.',15)
 txt(45,1030,'Source pages, ID corrections and coverage ledgers accompany the interactive map. Geometry: Natural Earth.',16)
 txt(45,1056,f"The Substantive Citation Report lists {s['selected_articles']} citing articles; marked articles document each selection.",15)
 svg.append('</svg>');(D/'Comprehensive-Citation-Map.svg').write_text(''.join(svg))
 v['survey']['display_groups']=len(data);(D/'Verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 print(f'Rebuilt {len(data)} map groups and static SVG')
if __name__=='__main__':build()
