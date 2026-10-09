"""Ensure coverage checks catch grouped citations and unboxed table values."""
import unittest

import pymupdf

from audit_markings import (apply_selections, check_document, covered, marked_pages, occurrences,
                            packet_pages, reference_numbers, reviewed_rectangles)
from optimize_markings import STYLES


def article_pages(document, count):
    for number in range(1, count + 1):
        document.new_page().insert_text((30, 50), f'| Article 01 | Original p. {number} |')


class CoverageTests(unittest.TestCase):
    def test_reference_ranges_and_grouped_citations(self):
        self.assertEqual(reference_numbers('6, 9, 12–14, 21'), {6, 9, 12, 13, 14, 21})
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((30, 50), 'TQT and Jaint et al. [6, 9, 12,\n14]; another method [13].')
            hits = occurrences(page, 12)
            self.assertEqual([hit[0] for hit in hits], ['TQT', 'Jaint', '[6, 9, 12, 14]'])
            self.assertEqual(len(hits[-1][1]), 4)

    def test_plurals_singular_titles_hyphenated_lines_and_bracket_ranges(self):
        with pymupdf.open() as document:
            page = document.new_page()
            # The base-14 test font cannot encode an en dash; the pattern accepts both.
            page.insert_text((30, 50), 'the TQTs method; Trained Quantization Threshold (TQT); Trained\n'
                                       'quantization thresh-\nolds; pre-TQT and TQT-\nbased; literature '
                                       '[24]-[26] and [27]-[29]')
            hits = occurrences(page, 25)
            self.assertEqual([hit[0] for hit in hits],
                             ['TQTs', 'Trained Quantization Threshold', 'TQT', 'Trained quantization thresholds',
                              'TQT', 'TQT', '[24]-[26]'])
            self.assertEqual(len(hits[3][1]), 4)
            self.assertEqual(len(hits[5][1]), 1)
            self.assertEqual([hit[0] for hit in occurrences(page, 28)][-1], '[27]-[29]')
            self.assertNotIn('[24]-[26]', [hit[0] for hit in occurrences(page, 27)])

    def test_full_table_row_is_required(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((30, 50), 'TQT [12]')
            page.insert_text((230, 50), '75.20')
            selection = {'first': '0:0', 'last': '0:1',
                         'start_text': 'TQT [12]', 'end_text': '75.20'}
            rectangles = reviewed_rectangles(page, selection)
            self.assertFalse(covered(rectangles, [rectangles[0]]))
            self.assertTrue(covered(rectangles, [pymupdf.Rect(20, 30, 280, 60)]))

    def test_every_page_requires_boxes_and_unselected_pages_remain_unmarked(self):
        with pymupdf.open() as document:
            article_pages(document, 3)
            for number in (2, 3):
                document[number - 1].insert_text((30, 80), 'TQT')
            article = {'article': 1, 'reference_page': 1, 'discussion_pages': [3]}
            result = check_document(document, article)
            self.assertEqual(result['matched'], 2)
            self.assertEqual(result['unboxed'], [{'page': 2, 'term': 'TQT'}, {'page': 3, 'term': 'TQT'}])
            width, color = STYLES[0]
            document[1].draw_rect(pymupdf.Rect(20, 60, 80, 85), color=color, width=width)
            with self.assertRaisesRegex(AssertionError, 'missing from discussion index'):
                check_document(document, article)
            article['discussion_pages'].append(2)
            self.assertEqual(check_document(document, article)['unboxed'], [{'page': 3, 'term': 'TQT'}])

    def test_reviewed_graphic_regions_are_enforced_and_applied(self):
        with pymupdf.open() as document:
            article_pages(document, 2)
            article = {'article': 1, 'reference_page': 1, 'discussion_pages': [2], 'additional_markings': [
                {'page': 2, 'rect': [20, 60, 80, 85], 'reason': 'TQT label drawn as graphics', 'kind': 'figure_text'}]}
            self.assertEqual(check_document(document, article)['unboxed'],
                             [{'page': 2, 'term': 'TQT label drawn as graphics'}])
            self.assertTrue(apply_selections(document, article))
            self.assertEqual(check_document(document, article)['unboxed'], [])
            self.assertFalse(apply_selections(document, article))

    def test_packet_takes_title_page_and_marked_pages_of_complete_article(self):
        with pymupdf.open() as document:
            for number in range(1, 6):
                page = document.new_page()
                page.insert_text((30, 50), 'TQT')
                if number in (3, 5):
                    page.draw_rect(pymupdf.Rect(20, 30, 80, 60), color=STYLES[number == 5][1],
                                   width=STYLES[number == 5][0])
            self.assertEqual(marked_pages(document), [1, 3, 5])
            self.assertEqual(packet_pages(document, {'article': '1', 'source_pages': '1; 3; 5'}), [1, 3, 5])
            with self.assertRaisesRegex(AssertionError, 'differ from discussion index'):
                packet_pages(document, {'article': '1', 'source_pages': '1; 3'})


if __name__ == '__main__':
    unittest.main()
