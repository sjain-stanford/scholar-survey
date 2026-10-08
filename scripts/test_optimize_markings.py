"""Regression checks for line grouping and removal of flattened PDF borders."""
import unittest

import pymupdf

from optimize_markings import enclosing_boxes, marking_boxes, optimize_document, STYLES


class MarkingTests(unittest.TestCase):
    def test_partial_lines_and_duplicates(self):
        lines = [pymupdf.Rect(*coords) for coords in
                 [(90, 20, 120, 34), (10, 32, 120, 46), (10, 44, 50, 58),
                  (10, 32, 120, 46)]]
        self.assertEqual(enclosing_boxes(lines), [pymupdf.Rect(10, 20, 120, 58)])
        self.assertEqual(enclosing_boxes([]), [])
        self.assertEqual(enclosing_boxes(lines[:1]), lines[:1])

    def test_separate_passages_columns_and_reference_number(self):
        lines = [pymupdf.Rect(*coords) for coords in
                 [(10, 20, 20, 34), (26, 20, 120, 34), (26, 32, 120, 46),
                  (10, 200, 120, 214), (150, 20, 260, 34), (150, 32, 260, 46)]]
        self.assertEqual(enclosing_boxes(lines),
                         [pymupdf.Rect(10, 20, 120, 46),
                          pymupdf.Rect(10, 200, 120, 214),
                          pymupdf.Rect(150, 20, 260, 46)])

    def test_enlarged_bounds_do_not_connect_unrelated_lines(self):
        lines = [pymupdf.Rect(*coords) for coords in
                 [(90, 20, 120, 34), (10, 32, 120, 46), (10, 10, 40, 24)]]
        self.assertEqual(len(enclosing_boxes(lines)), 2)

    def test_flattened_markings_removed_and_text_preserved(self):
        with pymupdf.open() as source, pymupdf.open() as document:
            page = source.new_page()
            page.insert_text((30, 50), 'The original publication text')
            page.draw_rect((300, 200, 350, 250), color=(.2, .3, .4))
            for width, color in STYLES:
                offset = 0 if width == 1.4 else 100
                for rect in [(30, 40 + offset, 130, 54 + offset),
                             (30, 52 + offset, 110, 66 + offset)]:
                    annot = page.add_rect_annot(rect)
                    annot.set_colors(stroke=color)
                    annot.set_border(width=width)
                    annot.update()
            source.bake()
            # Two pages share the imported form and its marking appearances.
            for _ in range(2):
                target = document.new_page()
                target.show_pdf_page(target.rect, source, 0)
            original_text = [page.get_text() for page in document]
            original_drawings = [page.get_drawings() for page in document]
            self.assertEqual(optimize_document(document, check=True), (8, 4))
            self.assertEqual([page.get_drawings() for page in document], original_drawings)
            self.assertEqual(optimize_document(document), (8, 4))
            self.assertEqual([page.get_text() for page in document], original_text)
            for page in document:
                self.assertEqual([len(boxes) for boxes in marking_boxes(page)], [1, 1])
                self.assertEqual(len(page.get_drawings()), 3)
            before = document.tobytes(no_new_id=True)
            self.assertEqual(optimize_document(document), (4, 4))
            self.assertEqual(document.tobytes(no_new_id=True), before)

    def test_unknown_stream_is_not_removed(self):
        with pymupdf.open() as document:
            page = document.new_page()
            # A source drawing with the same style is not a known annotation.
            for rect in [(20, 20, 80, 34), (20, 32, 80, 46)]:
                page.draw_rect(rect, color=STYLES[0][1], width=STYLES[0][0])
            before = page.get_drawings()
            with self.assertRaisesRegex(ValueError, 'unrecognized marking stream'):
                optimize_document(document)
            self.assertEqual(page.get_drawings(), before)


if __name__ == '__main__':
    unittest.main()
