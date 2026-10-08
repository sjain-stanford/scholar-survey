"""Ensure coverage checks catch grouped citations and unboxed table values."""
import unittest

import pymupdf

from audit_markings import check_document, covered, occurrences, reference_numbers, reviewed_rectangles
from optimize_markings import STYLES


class CoverageTests(unittest.TestCase):
    def test_reference_ranges_and_grouped_citations(self):
        self.assertEqual(reference_numbers('6, 9, 12–14, 21'), {6, 9, 12, 13, 14, 21})
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((30, 50), 'TQT and Jaint et al. [6, 9, 12,\n14]; another method [13].')
            hits = occurrences(page, 12)
            self.assertEqual([hit[0] for hit in hits], ['TQT', 'Jaint', '[6, 9, 12, 14]'])
            self.assertEqual(len(hits[-1][1]), 4)

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

    def test_selected_pages_require_boxes_and_other_pages_remain_unmarked(self):
        with pymupdf.open() as document:
            for number in range(1, 4):
                page = document.new_page()
                page.insert_text((30, 50), f'| Article 01 | Original p. {number} |')
                if number > 1:
                    page.insert_text((30, 80), 'TQT')
            article = {'article': 1, 'reference_page': 1, 'discussion_pages': [3]}
            result = check_document(document, article)
            self.assertEqual(result['matched'], 2)
            self.assertEqual(result['unboxed'], [{'page': 3, 'term': 'TQT'}])
            article['discussion_pages'].append(2)
            self.assertEqual(check_document(document, article)['unboxed'],
                             [{'page': 2, 'term': 'TQT'}, {'page': 3, 'term': 'TQT'}])
            article['discussion_pages'].remove(2)
            width, color = STYLES[0]
            document[1].draw_rect(pymupdf.Rect(20, 60, 80, 85), color=color, width=width)
            with self.assertRaisesRegex(AssertionError, 'missing from discussion index'):
                check_document(document, article)


if __name__ == '__main__':
    unittest.main()
