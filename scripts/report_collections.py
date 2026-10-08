"""Shared report membership, ordering and packet page index."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
PACKET = 'Selected-Discussion-Pages.pdf'


def collections():
    return json.loads((ROOT / 'data/report-collections.json').read_text())['collections']


def article_order(collection):
    return [number for group in collection['groups'] for number in group['articles']]


def packet_rows(papers, reviews):
    rows = []
    offset = 0
    for collection in collections():
        for number in article_order(collection):
            review, paper = reviews[number], papers[number]
            pages = sorted({1, review['reference_page'], *review['discussion_pages']})
            rows.append({'report': collection['id'], 'article': str(number),
                         'title': paper['title'], 'packet_start': str(offset + 1),
                         'packet_end': str(offset + len(pages)),
                         'source_pages': '; '.join(map(str, pages)),
                         'source_evidence': paper['source_evidence']})
            offset += len(pages)
    return rows


def packet_toc(rows):
    toc = []
    for collection in collections():
        selected = [row for row in rows if row['report'] == collection['id']]
        toc.append([1, collection['title'], int(selected[0]['packet_start'])])
        toc.extend([2, f'{int(row["article"]):02}. {row["title"]}', int(row['packet_start'])]
                   for row in selected)
    return toc
