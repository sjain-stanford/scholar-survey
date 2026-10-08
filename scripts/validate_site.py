#!/usr/bin/env python3
"""Validate source hashes, research artifacts, article consistency, and map coverage."""
import csv
import hashlib
import json
import re
import unicodedata
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build_site import DOCS, ROOT, build
from report_collections import PACKET, article_order, collections, packet_rows


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ['href', 'src'] and value:
                self.paths.append(value)


def validate_path(href, directory=DOCS):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        assert parsed.scheme != 'file', f'Nonportable file URL: {href}'
        return
    assert not parsed.path.startswith('/'), f'Root-relative link breaks project Pages path: {href}'
    path = (directory / unquote(parsed.path)).resolve()
    assert path.is_relative_to(DOCS.resolve()), f'Link escapes published folder: {href}'
    assert path.is_file(), f'Missing linked artifact: {href}'


def main():
    verification = json.loads((DOCS / 'Verification.json').read_text())
    survey = verification['survey']
    index = (DOCS / 'index.html').read_text()
    assert index == build(), 'Entry page needs rebuilding'
    assert (DOCS / '.nojekyll').is_file()
    assert not any(path.is_symlink() for path in DOCS.rglob('*')), 'Pages snapshot must contain regular files'
    manifest = list(csv.DictReader((ROOT / 'provenance/Research-Manifest.csv').open()))
    for row in manifest:
        path = DOCS / row['path']
        data = path.read_bytes()
        assert len(data) == int(row['bytes']), row['path']
        assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
        assert not data.startswith(b'version https://git-lfs.github.com/spec/v1'), f'LFS pointer cannot be served: {path}'
    initial = list(csv.DictReader((ROOT / 'provenance/Imported-Package-Manifest.csv').open()))
    for row in initial:
        path = Path(row['path'])
        if path.parts[0] in ['Sources', 'Marked-Articles'] or path.name == PACKET or ('SerpAPI Verification' in row['path'] and path.suffix == '.json'):
            assert hashlib.sha256((DOCS/path).read_bytes()).hexdigest() == row['sha256'], row['path']
    for row in csv.DictReader((DOCS / 'Delivery-Manifest.csv').open()):
        data = (DOCS / row['path']).read_bytes()
        assert len(data) == int(row['bytes']), row['path']
        assert hashlib.sha256(data).hexdigest() == row['sha256'], row['path']
    source_ledger = {row['evidence_id']: row for row in csv.DictReader((DOCS / 'Source-Ledger.csv').open())}
    for row in source_ledger.values():
        assert hashlib.sha256((DOCS / row['file']).read_bytes()).hexdigest() == row['sha256'], row['file']
    for filename in ['index.html', 'Comprehensive-Citation-Map.html'] + [c['report'] + '.html' for c in collections()]:
        parser = Links()
        parser.feed((DOCS / filename).read_text())
        for href in parser.paths:
            validate_path(href)
    # Proof links are generated from embedded JSON, not static HTML anchors.
    markers, _ = json.JSONDecoder().raw_decode(index.split('const DATA=', 1)[1])
    assert len(markers) == 123
    assert len({m['country'] for m in markers}) == survey['countries_territories']
    mapped_works = {w for m in markers for w in m['work_ids']}
    assert len(mapped_works) == survey['mapped_works']
    assert sum(len(m['locations']) for m in markers) == survey['institution_locations']
    inventory = list(csv.DictReader((DOCS / 'Citation-Inventory.csv').open()))
    assert len(inventory) == survey['deduplicated_works']
    assert mapped_works <= {row['work_id'] for row in inventory}
    reports = {c['id']: (DOCS / (c['report'] + '.html')).read_text() for c in collections()}
    coverage = list(csv.DictReader((DOCS / 'Coverage-by-Publication.csv').open()))
    for row in coverage:
        entry = row['profile_entry']
        works = {work['work_id'] for work in inventory
                 if entry in [value.strip() for value in work['cites_profile_entries'].split(';')]}
        assert len(works) == int(row['deduplicated_works']), entry
        mapped = {paper['work_id'] for marker in markers for location in marker['locations']
                  for paper in location['papers'] if int(entry) in paper['entries']}
        assert len(mapped) == int(row['mapped_works']), entry
        values = [f'{int(entry):02}'] + [row[field] for field in
                  ['title', 'profile_citations', 'retrieved_scholar_records', 'deduplicated_works', 'mapped_works']]
        for report in reports.values():
            assert '<tr>' + ''.join(f'<td>{escape(value)}</td>' for value in values) + '</tr>' in report, entry
    proofs = set()
    for marker in markers:
        assert set(marker['work_ids']) == {paper['work_id'] for location in marker['locations']
                                          for paper in location['papers']}
        for location in marker['locations']:
            for paper in location['papers']:
                validate_path(paper['proof'])
                proofs.add(paper['proof'])
    selections = list(csv.DictReader((DOCS / 'Selected-Articles.csv').open()))
    assert (len(selections), sum(p['a'] == 'True' for p in selections),
            sum(p['named'] == 'True' for p in selections)) == (
                survey['selected_articles'], survey['shortlist'], survey['named'])
    assert all((p['a'] == 'True') != (p['named'] == 'True') for p in selections), \
        'Each selected article must belong to exactly one report'
    expected_numbers = list(range(1, len(selections) + 1))
    selected_titles = {int(paper['n']): paper['title'] for paper in selections}
    selected_collections = {int(paper['n']): 'substantive' if paper['a'] == 'True' else 'named'
                            for paper in selections}
    normalize_title = lambda title: re.sub(r'\W+', '', unicodedata.normalize('NFKC', title).casefold())
    inventory_selections = []
    for work in inventory:
        match = re.fullmatch(r'Selected (substantive|named) review, article (\d+)', work['discussion_review'])
        if match:
            number = int(match[2])
            assert number in selected_titles, work['work_id']
            assert match[1] == selected_collections[number], work['work_id']
            assert normalize_title(work['title']) == normalize_title(selected_titles[number]), work['work_id']
            inventory_selections.append(number)
    assert sorted(inventory_selections) == expected_numbers
    assert {path.name for path in (DOCS / 'Marked-Articles').glob('*.pdf')} == {
        paper['marked_filename'] for paper in selections}
    articles = json.loads((ROOT / 'data/article-discussions.json').read_text())['articles']
    assert [article['n'] for article in articles] == expected_numbers
    assert [int(paper['n']) for paper in selections] == expected_numbers
    papers = {int(paper['n']): paper for paper in selections}
    article_data = {article['n']: article for article in articles}
    for paper, article in zip(selections, articles):
        count_source = source_ledger[paper['count_evidence']]
        count = json.loads((DOCS / count_source['file']).read_text())
        for key in re.findall(r'\w+', paper['count_pinpoint']):
            count = count[int(key)] if key.isdigit() else count[key]
        assert count == int(paper['count']), (paper['n'], 'Saved Scholar citation count')
        validate_path('Marked-Articles/' + paper['marked_filename'])
        assert paper['marked_filename'].startswith(f'{int(paper["n"]):02}-'), paper['n']
        for field in ['summary', 'research_connection', 'evidence_type', 'authorship_link']:
            assert article[field] and paper[field] == article[field], (paper['n'], field)
        assert int(paper['bibliography_page']) == article['bibliography_page'] > 0
    for collection in collections():
        order = article_order(collection)
        assert len(order) == len(set(order))
        assert set(order) == {int(paper['n']) for paper in selections
                              if paper[collection['selection_field']] == 'True'}
        report = reports[collection['id']]
        markdown = (DOCS / (collection['report'] + '.md')).read_text()
        html_articles = re.findall(r'<div class="paper">.*?</p></div>', report, re.S)
        md_articles = re.split(r'\n## \d+\.', markdown)[1:]
        assert len(html_articles) == len(md_articles) == len(order)
        assert [int(n) for n in re.findall(r'Article (\d+) ·', report)] == order
        assert [int(n) for n in re.findall(r'^## (\d+)\.', markdown, re.M)] == order
        for number, html_article, md_article in zip(order, html_articles, md_articles):
            paper, article = papers[number], article_data[number]
            for field in ['summary', 'research_connection', 'evidence_type', 'authorship_link']:
                assert escape(article[field]) in html_article, (number, field, 'HTML')
                assert article[field] in md_article, (number, field, 'Markdown')
            target = f'Marked-Articles/{paper["marked_filename"]}#page={article["bibliography_page"]}'
            assert f'href="{target}"' in html_article, number
            assert f']({target})' in md_article, number
            assert f'href="{escape(article["original_url"])}"' in html_article, number
        for target in [collection['report'] + '.html', collection['report'] + '.pdf']:
            assert (f'href="{target}"' in index) == collection['link_report'], target
            validate_path(target)
    assert f'href="{PACKET}"' in index, PACKET
    validate_path(PACKET)
    index_rows = list(csv.DictReader((DOCS / 'Discussion-Page-Index.csv').open()))
    marking = json.loads((DOCS / 'Marking-Review.json').read_text())
    assert len(marking['articles']) == len(selections)
    reviews = {review['article']: review for review in marking['articles']}
    assert index_rows == packet_rows(papers, reviews)
    unique_pages = set()
    for row in index_rows:
        number = int(row['article'])
        assert json.loads(papers[number]['body_pages']) == reviews[number]['discussion_pages']
        unique_pages.update((number, int(page)) for page in row['source_pages'].split(';'))
    assert len(unique_pages) == survey['selected_unique_pages']
    for collection in collections():
        rows = [row for row in index_rows if row['report'] == collection['id']]
        current = verification['collections'][collection['id']]
        assert current['articles'] == article_order(collection)
        start, end = int(rows[0]['packet_start']), int(rows[-1]['packet_end'])
        assert current['packet_pages'] == end - start + 1
        assert current['packet_start'] == start and current['packet_end'] == end
        target = f'{PACKET}#page={start}'
        assert f'href="{target}"' in reports[collection['id']]
    assert verification['discussion_packet']['file'] == PACKET
    assert verification['discussion_packet']['pages'] == int(index_rows[-1]['packet_end'])
    print(f'Validated {len(manifest)} research files, preserved source evidence, {len(markers)} map markers, '
          f'{len(proofs)} proof links, {len(selections)} synchronized article/authorship entries, '
          f'and {survey["named"]} named discussions')


if __name__ == '__main__':
    main()
