#!/usr/bin/env python3
"""Build the citation reports from shared article data and ordered collections."""
import argparse
import csv
import json
from html import escape

import site_nav
from report_collections import DOCS, ROOT, PACKET, article_order, collections, packet_rows


def page(title, content, eyebrow, print_only=False):
    label = 'eyebrow print-only' if print_only else 'eyebrow'
    return (f'<section class="page"><div class="{label}">{escape(eyebrow)}</div>\n'
            f'<h2>{escape(title)}</h2>\n{content}\n</section>')


def page_ranges(numbers):
    groups = []
    for number in numbers:
        if groups and number == groups[-1][-1] + 1:
            groups[-1].append(number)
        else:
            groups.append([number])
    return ', '.join(str(group[0]) if len(group) == 1 else f'{group[0]}–{group[-1]}'
                     for group in groups)


def scrollable_table(table, label):
    return (f'<div class="table-scroll" role="region" aria-label="{escape(label)}" tabindex="0">'
            + table + '</div>')


def citation_count(paper):
    return f'{int(paper["count"]):,}' if int(paper['count']) else 'None shown'


def count_phrase(paper):
    return (f'{int(paper["count"]):,} Google Scholar citations' if int(paper['count'])
            else 'No cited-by count in the saved Google Scholar record')


def selection_bases(paper):
    return paper['venue_basis'].split('; ')


def badges(paper, separator=''):
    return separator.join(f'<span class="badge">{escape(basis)}</span>' for basis in selection_bases(paper))


def marked_article(paper):
    return f'Marked-Articles/{paper["marked_filename"]}'


def article_table(numbers, papers, articles, substantive):
    headings = ('<th>No.</th><th>Article / venue</th><th>Scholar</th><th>Selection basis</th>'
                if substantive else '<th>No.</th><th>Article / venue</th><th>PDF discussion pages</th><th>Scholar</th>'
                ) + '<th>Marked article</th>'
    rows = []
    for number in numbers:
        paper, article = papers[number], articles[number]
        cells = [f'{number:02}',
                 f'<a href="{escape(article["original_url"])}"><b>{escape(paper["title"])}</b></a>'
                 f'<br><span class="small">{escape(paper["venue"])}</span>']
        count = f'<a href="{escape(article["scholar_url"])}">{citation_count(paper)}</a>'
        cells += ([count, badges(paper, '<br>')] if substantive else
                  [page_ranges(json.loads(paper['body_pages'])), count])
        cells.append(f'<a href="{escape(marked_article(paper))}">PDF</a>')
        rows.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>')
    table = (('<table class="articles">' if substantive else '<table>') + '<thead><tr>' + headings
             + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')
    return scrollable_table(table, 'Selected citing articles')


def article_block(number, paper, article, title):
    target = f'Marked-Articles/{paper["marked_filename"]}#page={paper["bibliography_page"]}'
    venue = f' Venue: {escape(article["venue_evidence"])}.' if article['venue_evidence'] else ''
    return f'''<div class="paper" id="article-{number:02}"><div class="kicker print-only">Article {number:02} · {escape(title)}</div><div class="kicker screen-only">Article {number:02}</div>
<h3>{escape(paper['title'])}</h3><div class="meta">{escape(article['authors'])}<br>{escape(paper['venue'])} · {count_phrase(paper)}</div>
{badges(paper)}
<p class="label"><b>Documented contribution:</b> {escape(article['evidence_type'])}</p>
<p>{escape(article['summary'])}</p>
<p class="small"><b>Authorship link:</b> {escape(article['authorship_link'])} <a href="{target}">Bibliography p. {paper['bibliography_page']}</a>.</p>
<p class="small"><b>Reviewed version:</b> {escape(paper['version'])}. <b>Pinpoint:</b> {escape(paper['locator'])}. Source {paper['source_evidence']}; marked copy {paper['marked_evidence']}.<br><b>Count:</b> {paper['count_evidence']}, <span class="mono">{escape(paper['count_pinpoint'])}</span>.{venue}</p>
<p class="small"><a href="{escape(article['original_url'])}">Original article</a> · <a href="{escape(article['scholar_url'])}">Scholar cited-by list</a><br>Marked file: <a class="mono" href="{escape(marked_article(paper))}">{escape(paper['marked_filename'])}</a></p></div>'''


def coverage_page(coverage, survey):
    fields = ['title', 'profile_citations', 'retrieved_scholar_records', 'deduplicated_works', 'mapped_works']
    rows = ''.join('<tr><td>' + f'{int(row["profile_entry"]):02}' + '</td>'
                   + ''.join(f'<td>{escape(row[field])}</td>' for field in fields) + '</tr>' for row in coverage)
    table = ('<table><thead><tr><th>Entry</th><th>Cited work</th><th>Profile citations</th>'
             '<th>Records retrieved</th><th>Grouped works</th><th>Mapped works</th></tr></thead>'
             '<tbody>' + rows + '</tbody></table>')
    return page('Citation coverage across the research portfolio', scrollable_table(table, 'Citation coverage by publication') + f'''
<p class="small">A citing work can appear in several publication rows. Unique survey totals group overlapping records and publication versions.</p>
<p>The saved Scholar profile records {survey['profile_citations']} citations. The inventory retains {survey['deduplicated_works']} works from {survey['scholar_records']} archived Scholar records. Publication affiliations establish locations for {survey['mapped_works']} works; the remaining {survey['deduplicated_works'] - survey['mapped_works']} have their review status recorded in the inventory.</p>
<p class="small">Dated Scholar responses document discovery and article-level counts. Source PDFs establish the selected discussions and affiliation evidence. The coverage table and inventory provide the denominators for each measure.</p>''', 'Survey scope and sources')


def build_reports():
    with (DOCS / 'Selected-Articles.csv').open(newline='') as handle:
        papers = {int(row['n']): row for row in csv.DictReader(handle)}
    articles = {row['n']: row for row in json.loads((ROOT / 'data/article-discussions.json').read_text())['articles']}
    reviews = {row['article']: row for row in json.loads((DOCS / 'Marking-Review.json').read_text())['articles']}
    survey = json.loads((DOCS / 'Verification.json').read_text())['survey']
    with (DOCS / 'Coverage-by-Publication.csv').open(newline='') as handle:
        coverage = list(csv.DictReader(handle))
    index = packet_rows(papers, reviews)
    style = (ROOT / 'scripts/report.css').read_text()
    outputs = {}
    for collection in collections():
        numbers = article_order(collection)
        count = len(numbers)
        selected = [row for row in index if row['report'] == collection['id']]
        start, end = int(selected[0]['packet_start']), int(selected[-1]['packet_end'])
        packet_pages = end - start + 1
        title, report, packet = collection['title'], collection['report'], f'{PACKET}#page={start}'
        pdf_link = f'<a href="{report}.pdf">Report PDF</a> · ' if collection['link_report'] else ''
        html_link = f'<a href="{report}.html">{escape(title)}</a> · ' if collection['link_report'] else ''
        md_link = f'[Report PDF]({report}.pdf) · ' if collection['link_report'] else ''
        substantive = collection['id'] == 'substantive'
        cover = f'''<section class="page"><div class="eyebrow">Sambhav R. Jain · citation research · 7 October 2026</div>
<h1>{escape(title)}</h1><p>{escape(collection['description'])}</p>
<div class="cards"><div class="stat"><b>{count}</b>selected articles</div><div class="stat"><b>{packet_pages}</b>marked discussion pages</div><div class="stat"><b>{survey['countries_territories']}</b>countries / territories in the wider survey</div></div>
<h2>Selection and source documentation</h2><p>{escape(collection['selection'])}</p>
<h2>Authorship links and documented scholarly use</h2><p>Each article identifies the cited work and authors, the specific research connection and the original discussion pages. The bibliography link establishes authorship of the corresponding work by Sambhav R. Jain and coauthors.</p>
<p>Orange rectangles mark selected discussion, citations and TQT results; blue rectangles identify the corresponding bibliography entries. The marked packet follows the article order in this report and retains original page numbers. Article numbers identify the corresponding marked files.</p>
<div class="note"><b>International citation survey.</b> The wider survey maps {survey['mapped_works']} citing works to {survey['institution_locations']} institution/location entries across {survey['countries_territories']} countries/territories. These totals describe the broader citation network, separately from this report’s selection.</div>
<p>{pdf_link}<a href="{packet}">Marked discussions</a> · <a href="index.html">Interactive map</a></p>
<p class="small">Snapshot: October 7, 2026. <a href="https://scholar.google.com/citations?hl=en&amp;user=1mvzap4AAAAJ">Sambhav Jain’s Google Scholar profile</a>. Counts belong to the saved citing-article records or version clusters.</p></section>'''
        sections = [cover]
        if substantive:
            for group in collection['groups']:
                sections.append(page(f'{group["title"]} ({len(group["articles"])})',
                                     article_table(group['articles'], papers, articles, True), title, True))
        else:
            sections.append(page(f'{count} named citing articles',
                                 article_table(numbers, papers, articles, False), title))
        for group in collection['groups']:
            for start in range(0, len(group['articles']), 2):
                blocks = '\n'.join(article_block(n, papers[n], articles[n], title)
                                   for n in group['articles'][start:start + 2])
                # A compact label leaves enough space for two complete article entries; on screen it
                # appears once, before the first pair.
                label = 'eyebrow print-only' if start else 'eyebrow'
                sections.append(f'<section class="page"><div class="{label}">{escape(group["title"])}</div>\n{blocks}\n</section>')
        sections.append(coverage_page(coverage, survey))
        sections.append(page('Publication-sourced affiliations and research connections', f'''
<p>The map presents {survey['institution_locations']} institution/location entries from {survey['mapped_works']} grouped citing works in {survey['countries_territories']} countries/territories. Each pin opens the institutions, citing papers and affiliation-page evidence. Several institutions in one city share a display pin; multi-institution papers contribute several locations.</p>
<p>Affiliations come from the reviewed publication. Explicit campus and city details determine placement; ROR supplies institution-city geography when the publication lists an institution without a city. Hollow markers show country-level affiliations. Coordinates are geographic display anchors.</p>
<p>The map documents the geographic reach of citing authors’ publication affiliations, including coauthor- and employer-linked works. Article passages establish methodological adaptation, implementation, comparison, design connections or technical exposition. Joint attribution is retained where several methods are credited.</p>
<h2>Research files</h2><p><a href="{packet}">Marked discussions</a>: marked source pages in this report’s article order.<br><b>Marked-Articles/:</b> complete articles with original page numbers and source links.<br><b>Selected-Articles.csv:</b> selection membership, counts, evidence types and source pages.<br><b>Discussion-Page-Index.csv:</b> article-to-packet page mapping.<br><b>Sources/:</b> dated Scholar, publication, venue, geography and affiliation captures.</p>
<p>{html_link}<a href="index.html">Interactive map</a></p>
<p class="small">Counts refer to the saved October 7, 2026 snapshot. Hashes and source provenance are recorded in the research manifests.</p>''', 'International research engagement'))
        outputs[report + '.html'] = ('<!doctype html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)}</title><style>{style}{site_nav.CSS}</style></head><body>\n'
            + site_nav.nav('report') + '\n<main class="report">\n' + '\n'.join(sections)
            + '\n</main>\n</body></html>\n')
        md = [f'# {title}', f'Prepared October 7, 2026. {count} selected articles; {packet_pages} marked discussion pages.',
              collection['description'], collection['selection'],
              f'{md_link}[Marked discussions]({packet}) · [Interactive map](index.html)',
              'Article numbers identify the corresponding marked files.']
        for group in collection['groups']:
            md.append(f'## {group["title"]}')
            table = ['| No. | Article / venue | Scholar | Selection basis | Marked article |',
                     '|---:|---|---:|---|---|']
            for n in group['articles']:
                p, a = papers[n], articles[n]
                table.append(f'| {n:02} | [{p["title"]}]({a["original_url"]})<br>{p["venue"]} | [{citation_count(p)}]({a["scholar_url"]}) | {"<br>".join(f"`{basis}`" for basis in selection_bases(p))} | [PDF]({marked_article(p)}) |')
            md.append('\n'.join(table))
        for group in collection['groups']:
            md.append(f'## {group["title"]} — article discussions')
            for n in group['articles']:
                p, a = papers[n], articles[n]
                md += [f'## {n:02}. {p["title"]}', f'{a["authors"]}\n\n{p["venue"]} · {count_phrase(p)}',
                       f'**Documented contribution:** {a["evidence_type"]}', a['summary'],
                       f'**Authorship link:** {a["authorship_link"]} [Bibliography p. {p["bibliography_page"]}](Marked-Articles/{p["marked_filename"]}#page={p["bibliography_page"]}).',
                       f'**Reviewed version:** {p["version"]}. **Source:** {p["source_evidence"]}; {p["locator"]}. Count: {p["count_evidence"]}, {p["count_pinpoint"]}.',
                       f'[Original article]({a["original_url"]}) · [Scholar cited-by list]({a["scholar_url"]})',
                       f'Marked file: [{p["marked_filename"]}]({marked_article(p)})']
        md += ['## International reach and source coverage',
               f'The wider survey maps {survey["mapped_works"]} citing works across {survey["countries_territories"]} countries/territories, with {survey["institution_locations"]} institution/location entries. The inventory retains {survey["deduplicated_works"]} works from {survey["scholar_records"]} archived Scholar records; the saved profile records {survey["profile_citations"]} citations.',
               'Publication affiliations establish geographic reach, including coauthor- and employer-linked works. [Coverage by publication](Coverage-by-Publication.csv) records retrieval and affiliation-review totals. Article-specific passages establish the documented scholarly contribution or connection.']
        outputs[report + '.md'] = '\n\n'.join(md) + '\n'
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, content in build_reports().items():
        path = DOCS / name
        if args.check:
            assert path.read_text() == content, f'{name} needs rebuilding'
        else:
            path.write_text(content)
    print('Report HTML/Markdown files are current' if args.check else 'Built report HTML/Markdown files')


if __name__ == '__main__':
    main()
