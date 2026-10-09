#!/usr/bin/env python3
"""Replace reviewed per-line PDF markings with enclosing group rectangles."""
import argparse
import csv
import hashlib
import re
from pathlib import Path

import pymupdf

from report_collections import PACKET

ROOT = Path(__file__).resolve().parents[1]
STYLES = ((1.4, (.88, .36, .04)), (1.0, (.04, .42, .55)))
NUMBER = rb'[-+]?(?:\d*\.\d+|\d+\.?\d*)'
# The imported markings are flattened square-annotation appearance streams.
# Match the entire stream so publication text and graphics cannot be removed.
LINE_APPEARANCE = re.compile(
    rb'\s*(' + NUMBER + rb')\s+w\s+'
    rb'(' + NUMBER + rb')\s+(' + NUMBER + rb')\s+(' + NUMBER + rb')\s+RG\s+'
    + rb'\s+'.join([NUMBER] * 4) + rb'\s+re\s+S\s*')
GROUP_MARKER = b'% scholar-survey grouped marking\n'
# Widest gap joining boxes: between the lines of a passage or fragments of one line (e.g. a
# reference number and its entry). Passages one line apart, column gutters and side-by-side
# table cells are about 7 pt or more apart once padded.
JOIN_GAP = 6


def style_index(width, color):
    if width is None:
        return None
    for index, (expected_width, expected_color) in enumerate(STYLES):
        if (abs(width - expected_width) < .001 and color is not None
                and len(color) == 3
                and all(abs(a - b) < .001 for a, b in zip(color, expected_color))):
            return index
    return None


def marking_boxes(page):
    """Read page-coordinate rectangles, including flattened Form XObjects."""
    result = [[] for _ in STYLES]
    for drawing in page.get_drawings():
        style = style_index(drawing['width'], drawing['color'])
        if (style is not None and drawing['type'] == 's'
                and len(drawing['items']) == 1 and drawing['items'][0][0] == 're'):
            result[style].append(drawing['rect'])
    return result


def neighboring_lines(a, b):
    """Join adjacent lines or nearby fragments on one line, not other columns."""
    height = min(a.height, b.height)
    x_overlap = min(a.x1, b.x1) - max(a.x0, b.x0)
    y_overlap = min(a.y1, b.y1) - max(a.y0, b.y0)
    return ((x_overlap > 0 and y_overlap >= -min(.5 * height, JOIN_GAP))
            or (y_overlap >= .5 * max(a.height, b.height)
                and x_overlap >= -min(height, JOIN_GAP)))


def enclosing_boxes(line_boxes):
    """Union each connected group of original line boxes, deduplicating repeats.

    Connectivity is tested on the input rectangles, never their enlarged union:
    an enclosing box must not pull unrelated text into its group.
    """
    remaining = [pymupdf.Rect(box) for box in line_boxes]
    groups = []
    while remaining:
        members = [remaining.pop(0)]
        for member in members:
            neighbors = [box for box in remaining if neighboring_lines(member, box)]
            remaining = [box for box in remaining if not neighboring_lines(member, box)]
            members.extend(neighbors)
        bounds = pymupdf.Rect(members[0])
        for member in members[1:]:
            bounds |= member
        groups.append(bounds)
    return groups


def marking_streams(page):
    document = page.parent
    xrefs = set(page.get_contents()) | {obj[0] for obj in page.get_xobjects()}
    result = set()
    for xref in xrefs:
        stream = document.xref_stream(xref)
        match = LINE_APPEARANCE.fullmatch(stream)
        if (stream.startswith(GROUP_MARKER)
                or (match and style_index(float(match[1]),
                                          tuple(float(match[i]) for i in (2, 3, 4)))
                    is not None)):
            result.add(xref)
    return result


def optimize_document(document, check=False):
    jobs = []
    before = after = 0
    for page in document:
        lines = marking_boxes(page)
        groups = [enclosing_boxes(boxes) for boxes in lines]
        before += sum(map(len, lines))
        after += sum(map(len, groups))
        if any(lines):
            jobs.append((page.number, groups, marking_streams(page)))
    if before == after or check:
        return before, after

    # Gather every page before clearing shared appearance streams. A duplicate
    # invocation may refer to the same stream more than once, even across pages.
    originals = {xref: document.xref_stream(xref)
                 for _, _, streams in jobs for xref in streams}
    for xref in originals:
        document.update_stream(xref, b'')
    for number, _, _ in jobs:
        if any(marking_boxes(document[number])):
            for xref, stream in originals.items():
                document.update_stream(xref, stream)
            raise ValueError(f'Page {number + 1}: unrecognized marking stream; left unchanged')
    for number, groups, _ in jobs:
        page = document[number]
        for (width, color), boxes in zip(STYLES, groups):
            for box in boxes:
                page.draw_rect(box, color=color, width=width, overlay=True)
                xref = page.get_contents()[-1]
                document.update_stream(xref, GROUP_MARKER + document.xref_stream(xref))
    return before, after


def refresh_manifests(changed):
    """Refresh only changed outputs; leave captured source hashes untouched."""
    changed = set(changed)
    for path in [ROOT / 'docs/Delivery-Manifest.csv',
                 ROOT / 'provenance/Imported-Package-Manifest.csv',
                 ROOT / 'provenance/Research-Manifest.csv']:
        original = path.read_bytes()
        with path.open(newline='') as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames
            rows = list(reader)
        dirty = False
        for row in rows:
            if (path.name == 'Imported-Package-Manifest.csv'
                    and not (row['path'].startswith('Marked-Articles/')
                             or row['path'] == PACKET)):
                continue
            if row['path'] in changed:
                data = (ROOT / 'docs' / row['path']).read_bytes()
                row.update(bytes=str(len(data)), sha256=hashlib.sha256(data).hexdigest())
                dirty = True
        if dirty:
            with path.open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=fields,
                                        lineterminator='\r\n' if b'\r\n' in original else '\n')
                writer.writeheader()
                writer.writerows(rows)
            if path.parent.name == 'docs':
                changed.add(path.name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check without writing files')
    args = parser.parse_args()
    docs = ROOT / 'docs'
    paths = sorted((docs / 'Marked-Articles').glob('*.pdf'))
    paths.append(docs / PACKET)
    changed = []
    for path in paths:
        with pymupdf.open(path) as document:
            before, after = optimize_document(document, check=args.check)
            if before == after:
                continue
            changed.append(path.relative_to(docs).as_posix())
            if not args.check:
                temporary = path.with_suffix('.tmp.pdf')
                document.save(temporary, garbage=4, deflate=True)
        if not args.check:
            temporary.replace(path)
        print(f'{path.name}: {before} line boxes -> {after} group boxes')
    if args.check and changed:
        raise SystemExit('Marking boxes need consolidation')
    if changed:
        refresh_manifests(changed)
    else:
        print('All marking groups already have one enclosing box')


if __name__ == '__main__':
    main()
