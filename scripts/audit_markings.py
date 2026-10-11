#!/usr/bin/env python3
"""Check every page of the complete papers for unboxed mentions; apply reviewed additional ranges."""
import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

import pymupdf

from optimize_markings import GROUP_MARKER, STYLES, marking_boxes, optimize_document
from report_collections import PACKET, packet_rows, packet_toc

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
DIRECT = re.compile(r'\bJaint?\b|\bTQTs?\b|trained\s+(?:uniform\s+quantization|quantization\s+thresholds?)'
                    r'|1903\.08066|1706\.08948', re.I)
NUMERIC = re.compile(r'\[([\d\s,–—-]+)\]')
# IEEE style writes a citation range as separate brackets: "[24]–[26]" cites [25].
NUMERIC_RANGE = re.compile(r'\[(\d+)\]\s*[–—-]\s*\[(\d+)\]')


def text_lines(page):
    return [(f'{b}:{n}', ''.join(span['text'] for span in line['spans']),
             pymupdf.Rect(line['bbox']))
            for b, block in enumerate(page.get_text('dict')['blocks'])
            for n, line in enumerate(block.get('lines', []))]


def reviewed_rectangles(page, selection):
    if 'rect' in selection:
        return [pymupdf.Rect(selection['rect'])]
    lines = text_lines(page)
    ids = [line[0] for line in lines]
    first, last = ids.index(selection['first']), ids.index(selection['last'])
    assert first <= last, selection
    assert lines[first][1] == selection['start_text'], selection
    assert lines[last][1] == selection['end_text'], selection
    return [rect + (-2, -2, 2, 2) for _, _, rect in lines[first:last + 1]]


def bounds(rectangles):
    result = pymupdf.Rect(rectangles[0])
    for rect in rectangles[1:]:
        result |= rect
    return result


def reference_numbers(citation):
    result = set()
    for part in citation.split(','):
        values = [int(number) for number in re.findall(r'\d+', part)]
        if len(values) == 1:
            result.add(values[0])
        elif len(values) == 2:
            result.update(range(values[0], values[1] + 1))
    return result


def occurrences(page, reference_number=None):
    """Match words across PDF line breaks, including hyphenated words and grouped/ranged citations."""
    words = page.get_text('words')
    text, positions = '', []
    for index, word in enumerate(words):
        normalized = unicodedata.normalize('NFKC', word[4])
        following = words[index + 1] if index + 1 < len(words) else None
        # A line-final hyphen continues the word on the next line; it is dropped only between
        # lowercase letters ("thresh-" "olds"), so "TQT-" "based" stays hyphenated.
        joined = (normalized.endswith('-') and len(normalized) > 1 and following is not None
                  and tuple(following[5:7]) != tuple(word[5:7]))
        start = len(text)
        if joined and normalized[-2].islower() and following[4][:1].islower():
            text += normalized[:-1]
        else:
            text += normalized if joined else normalized + ' '
        positions.append((start, len(text) - (0 if joined else 1), pymupdf.Rect(word[:4])))
    matches = list(DIRECT.finditer(text))
    if reference_number is not None:
        matches.extend(match for match in NUMERIC.finditer(text)
                       if reference_number in reference_numbers(match[1]))
        matches.extend(match for match in NUMERIC_RANGE.finditer(text)
                       if int(match[1]) < reference_number < int(match[2]))
    return [(match[0], [rect for start, end, rect in positions
                       if start < match.end() and end > match.start()])
            for match in sorted(matches, key=lambda match: match.start())]


def covered(rectangles, boxes):
    # Text glyph boxes and drawn strokes differ slightly after PDF rounding. Some fonts report
    # glyph boxes reaching into the adjacent lines, so a box need only enclose the full width
    # and the middle third of each rectangle's height.
    return all(any((box + (-.5, -.5, .5, .5)).contains(rect + (0, rect.height / 3, 0, -rect.height / 3))
                   for box in boxes)
               for rect in rectangles)


def check_document(document, article):
    selected_pages = {article['reference_page'], *article['discussion_pages']}
    exclusions = {}
    for selection in article.get('excluded_occurrences', []):
        page = document[selection['page'] - 1]
        exclusions.setdefault(page.number, []).extend(reviewed_rectangles(page, selection))
    counts = {'matched': 0, 'excluded': 0, 'unboxed': []}
    for page in document:
        footer = f'| Article {article["article"]:02} | Original p. {page.number + 1} |'
        assert footer in page.get_text(), ('Incorrect provenance footer', article['article'], page.number + 1)
        boxes = [box for group in marking_boxes(page) for box in group]
        matches = occurrences(page, article.get('reference_number'))
        if page.number + 1 not in selected_pages:
            assert not boxes, ('Marked page missing from discussion index', article['article'], page.number + 1)
        for term, rectangles in matches:
            if covered(rectangles, exclusions.get(page.number, [])):
                counts['excluded'] += 1
            else:
                counts['matched'] += 1
                if not covered(rectangles, boxes):
                    counts['unboxed'].append({'page': page.number + 1, 'term': term})
    for selection in article.get('additional_markings', []):
        page = document[selection['page'] - 1]
        if not covered(reviewed_rectangles(page, selection), marking_boxes(page)[0]):
            counts['unboxed'].append({'page': page.number + 1, 'term': selection['reason']})
    return counts


def apply_selections(document, article):
    added = 0
    for selection in article.get('additional_markings', []):
        page = document[selection['page'] - 1]
        # Establish the reviewed line rectangles first; one enclosing box then
        # covers the whole logical group, including all cells of a table row.
        rectangles = reviewed_rectangles(page, selection)
        if covered(rectangles, marking_boxes(page)[0]):
            continue
        rect = bounds(rectangles)
        width, color = STYLES[0]
        page.draw_rect(rect, color=color, width=width, overlay=True)
        xref = page.get_contents()[-1]
        document.update_stream(xref, GROUP_MARKER + document.xref_stream(xref))
        added += 1
    if added:
        optimize_document(document)
    toc = document.get_toc()
    destinations = {item[2] for item in toc}
    updated = sorted(toc + [[1, f'Body discussion, original p. {page}', page]
                            for page in article['discussion_pages'] if page not in destinations],
                     key=lambda item: item[2])
    if updated != toc:
        document.set_toc(updated)
        added += 1
    return added


def marked_pages(document):
    """The title page and every page carrying a marking box."""
    return [page.number + 1 for page in document if page.number == 0 or any(marking_boxes(page))]


def packet_pages(source, row):
    """Pages of a complete marked article that enter the packet; they must match the page index."""
    pages = marked_pages(source)
    indexed = list(map(int, row['source_pages'].split(';')))
    assert pages == indexed, ('Marked pages differ from discussion index', row['article'], pages, indexed)
    return pages


def check_packet(papers, reviews):
    with (DOCS / 'Discussion-Page-Index.csv').open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    assert rows == packet_rows(papers, reviews)
    with pymupdf.open(DOCS / PACKET) as packet:
        offset = 0
        for row in rows:
            number = int(row['article'])
            with pymupdf.open(DOCS / 'Marked-Articles' / papers[number]['marked_filename']) as source:
                for page_number in packet_pages(source, row):
                    original, excerpt = source[page_number - 1], packet[offset]
                    assert original.rect == excerpt.rect, (number, page_number)
                    assert original.get_text() == excerpt.get_text(), (number, page_number)
                    assert marking_boxes(original) == marking_boxes(excerpt), (number, page_number)
                    offset += 1
        assert offset == len(packet)
        assert packet.get_toc() == packet_toc(rows)
    return offset


def rebuild_packet(papers, reviews):
    rows = packet_rows(papers, reviews)
    try:
        check_packet(papers, reviews)
        return
    except (AssertionError, IndexError, FileNotFoundError):
        pass
    packet_path = DOCS / PACKET
    with pymupdf.open() as packet:
        for row in rows:
            number = int(row['article'])
            with pymupdf.open(DOCS / 'Marked-Articles' / papers[number]['marked_filename']) as source:
                for page in packet_pages(source, row):
                    packet.insert_pdf(source, from_page=page - 1, to_page=page - 1)
        packet.set_toc(packet_toc(rows))
        packet.set_metadata({'title': 'Marked discussions'})
        temporary = packet_path.with_suffix('.tmp.pdf')
        packet.save(temporary, garbage=4, deflate=True)
    temporary.replace(packet_path)
    with (DOCS / 'Discussion-Page-Index.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Add reviewed boxes and rebuild the combined packet')
    args = parser.parse_args()
    reviews = json.loads((DOCS / 'Marking-Review.json').read_text())['articles']
    with (DOCS / 'Selected-Articles.csv').open(newline='') as handle:
        papers = {int(row['n']): row for row in csv.DictReader(handle)}
    failed = False
    for article in reviews:
        path = DOCS / 'Marked-Articles' / papers[article['article']]['marked_filename']
        with pymupdf.open(path) as document:
            added = apply_selections(document, article) if args.apply else 0
            result = check_document(document, article)
            print(f'{path.name}: {result}')
            failed |= bool(result['unboxed'])
            if added and not result['unboxed']:
                document.save(path.with_suffix('.tmp.pdf'), garbage=4, deflate=True)
        if added and not result['unboxed']:
            path.with_suffix('.tmp.pdf').replace(path)
    if failed:
        raise SystemExit('Unboxed occurrences remain')
    if args.apply:
        rebuild_packet(papers, {article['article']: article for article in reviews})
        print('Rebuilt packet and index; refresh report page lists and manifests after review')
    print(f'Verified {check_packet(papers, {article["article"]: article for article in reviews})} '
          'packet pages against their complete articles')


if __name__ == '__main__':
    main()
