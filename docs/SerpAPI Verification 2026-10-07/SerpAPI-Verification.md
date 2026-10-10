# SerpAPI verification — October 7, 2026

Authenticated access succeeded: seven requests returned HTTP 200 and SerpAPI search status `Success`. Responses were saved with request parameters and UTC timestamps; API credentials are excluded.

| Item | Google Scholar count retrieved through SerpAPI | Source and exact field |
| --- | ---: | --- |
| Sambhav Jain's profile, all-time citations | 354 | E-0356, [profile.json](profile.json), `data.cited_by.table[0].citations.all` |
| Trained quantization thresholds for accurate and efficient fixed-point inference of deep neural networks | 227 | E-0356, `data.articles[0].cited_by.value`; citing cluster `1211587708316162333` |
| Understanding and Overcoming the Challenges of Efficient Transformer Quantization | 271 | E-0357, [transformer-title-search.json](transformer-title-search.json), `data.organic_results[0].inline_links.cited_by.total`; ACL Anthology link and citing cluster `8710219284475667501` match the intended paper |

The profile response lists 11 entries: the ten publications in the coverage table and the MLSys 2020 slides "TQT: Trained Quantization Thresholds", which had no citations and was later removed from the profile. The Transformer paper's title search also returns a separate bibliographic entry with 11 citations. The report uses the profile-linked Transformer record (271) and retains the separate entry for version reconciliation.

Public source links: [Sambhav Jain's profile](https://scholar.google.com/citations?hl=en&user=1mvzap4AAAAJ), [Transformer paper's citing list](https://scholar.google.com/scholar?cites=8710219284475667501&as_sdt=2005&sciodt=0,5&hl=en), [SerpAPI author API documentation](https://serpapi.com/google-scholar-author-api), [SerpAPI Scholar search documentation](https://serpapi.com/google-scholar-api).

## Citation-list and pagination tests

| Evidence | Saved response | Results returned | `search_information.total_results` |
| --- | --- | ---: | ---: |
| E-0358 | [Transformer citing list, first page](transformer-citing-papers-page1.json) | 20 | 142 |
| E-0359 | [TQT, num=20, start=0](tqt-citing-papers-page1.json) | 20 | 92 |
| E-0360 | [TQT, num=20, start=20](tqt-citing-papers-page2.json) | 20 | 227 |
| E-0361 | [TQT, num=10, start=0, as_sdt=2005](tqt-citing-papers-num10-start0.json) | 10 | 29 |
| E-0362 | [TQT, num=10, start=10, as_sdt=2005](tqt-citing-papers-num10-start10.json) | 10 | 44 |

The two 20-result TQT pages contain 32 distinct result IDs; the two 10-result pages contain 19. The saved responses retain the parameters and retrieval timestamps used for the initial access checks.

## Survey data and source documentation

Article-level cited-by fields and the author-profile citation table supply the dated count statements. The citation survey groups retrieved records across pages and publication versions before counting works. Source PDFs provide the body discussions and publication-time affiliations.

The completed survey records 337 retrieved Scholar records, 323 grouped works and publication-sourced locations for 210 works in 30 countries/territories. Its [research report](../Substantive-Citation-Report.pdf), [citation inventory](../Citation-Inventory.csv) and [coverage table](../Coverage-by-Publication.csv) document these measures.

This supplement preserves the initial authenticated-access snapshots alongside the subsequent source-linked research.

Registered sources: E-0356–E-0362. This note: E-0363. Claims: C-0176–C-0178.
