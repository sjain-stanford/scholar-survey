"""Combined packet indexes and bookmarks preserve report and article order."""
import unittest
from unittest.mock import patch

from report_collections import packet_rows, packet_toc


class PacketIndexTests(unittest.TestCase):
    def test_offsets_continue_across_reports_and_bookmarks_use_combined_pages(self):
        papers = {n: {'title': f'Paper {n}', 'source_evidence': f'E-{n}'} for n in [1, 2, 3]}
        reviews = {1: {'reference_page': 9, 'discussion_pages': [1, 4]},
                   2: {'reference_page': 8, 'discussion_pages': [3]},
                   3: {'reference_page': 7, 'discussion_pages': [2, 5]}}
        reports = [{'id': 'first', 'title': 'First report', 'groups': [{'articles': [1, 3]}]},
                   {'id': 'second', 'title': 'Second report', 'groups': [{'articles': [2]}]}]
        with patch('report_collections.collections', return_value=reports):
            rows = packet_rows(papers, reviews)
            toc = packet_toc(rows)
        self.assertEqual([row['article'] for row in rows], ['1', '3', '2'])
        self.assertEqual([(row['packet_start'], row['packet_end']) for row in rows],
                         [('1', '3'), ('4', '7'), ('8', '10')])
        self.assertEqual(rows[0]['source_pages'], '1; 4; 9')
        self.assertEqual(toc, [[1, 'First report', 1], [2, '01. Paper 1', 1],
                               [2, '03. Paper 3', 4], [1, 'Second report', 8],
                               [2, '02. Paper 2', 8]])


if __name__ == '__main__':
    unittest.main()
