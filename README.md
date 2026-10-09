# Scholar survey

[Interactive Citation Map](https://sjain-stanford.github.io/scholar-survey/) · [PDF](docs/Comprehensive-Citation-Map.pdf)

[Substantive Citation Report](docs/Substantive-Citation-Report.html) · [PDF](docs/Substantive-Citation-Report.pdf)

[Marked discussions](docs/Selected-Discussion-Pages.pdf)

A dated survey of research citing Sambhav R. Jain's scholarly work, based on Google Scholar records retrieved through SerpAPI on October 7, 2026. Publication text supplies the substantive discussions and author affiliations.

- **Substantive report:** 22 articles in two groups, with marked discussions in the combined packet. Group A (10 articles) is selected by ICORE2026 A* venue and/or at least 100 Scholar citations; Group B (12 articles) contains articles whose methods rely on or extend TQT.
- **Marked evidence:** 22 complete marked articles and 103 source pages in one combined packet. Article numbers identify the corresponding marked files; numbers 9, 10, 11 and 13 belonged to the withdrawn named report.
- **Map:** 210 grouped citing works, 228 institution/location entries and 30 countries/territories.

The survey includes 323 works from 337 archived Scholar records. Publication affiliations place 210 of those works across 30 countries/territories. Each selected article identifies the specific contribution discussed and links directly to the bibliography page establishing authorship of the cited work. The saved author profile records 354 citations; counts for the selected citing articles are reported separately. The map covers the sourced-affiliation subset, including coauthor- and employer-linked works.

## Files

The complete research package is in [`docs/`](docs/START-HERE.md), including reports, marked articles, CSV inventories, dated source captures, and verification records. Source captures retain the saved evidence; the marked articles and excerpt packet include the reviewed marking regions documented in [`docs/Marking-Review.json`](docs/Marking-Review.json). [`provenance/Research-Manifest.csv`](provenance/Research-Manifest.csv) records current research-file hashes; [`provenance/Imported-Package-Manifest.csv`](provenance/Imported-Package-Manifest.csv) records the preserved source-evidence baseline.

[`docs/index.html`](docs/index.html) is the site entry page, generated from the standalone map with navigation to the evidence. All map data and geometry are embedded; viewing the map requires no API key, server, analytics service or external JavaScript. Links to affiliation proof and report files are relative and work under the `/scholar-survey/` project path.

Publication text documents specific forms of research engagement: methodological adaptation, implementation, experimental comparison, quantizer-design connections, and technical exposition. The entries retain joint attribution and identify the reviewed publication version and exact source page.

## GitHub Pages

Publish **`main` → `/docs`** under [Settings → Pages](https://github.com/sjain-stanford/scholar-survey/settings/pages), using **Deploy from a branch**. The site URL is:

https://sjain-stanford.github.io/scholar-survey/

GitHub Pages serves the committed files directly. `docs/.nojekyll` disables Jekyll processing. PDFs and other source artifacts are ordinary Git files because [GitHub Pages does not support Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage). The validation workflow checks the generated page, imported hashes, research totals, and local links on each push or pull request. GitHub handles deployment from the selected branch and folder.

## Local preview and maintenance

Python 3 is sufficient:

```sh
python3 scripts/build_reports.py
python3 scripts/build_site.py
python3 scripts/validate_site.py
python3 -m http.server 8000 --directory docs
```

Open `http://localhost:8000/`. The original `docs/Comprehensive-Citation-Map.html` also works offline. To check that the committed entry page is current without changing it, use `python3 scripts/build_site.py --check`.

Validation checks the source-evidence baseline, current research and delivery manifests, and consistency of article summaries, evidence types and authorship links across JSON, CSV, HTML and Markdown. [`data/article-discussions.json`](data/article-discussions.json) records the source-based presentation of each selected article. [`data/report-collections.json`](data/report-collections.json) defines report membership and article order, shared by the reports, marked packets and download links. `python3 scripts/build_reports.py --check` verifies generated HTML and Markdown. When revising derived reports, update the current manifests and document the source snapshot together.

To regenerate the report PDF and static map exports, install `scripts/render-requirements.txt` and run `python3 scripts/render_documents.py`; use `--reports-only` when the map has not changed. The Citation Map PDF links to the website at the top under “Interactive Citation Map”. Rendering also requires the platform's Pango and HarfBuzz libraries. Report HTML/Markdown building, site building and validation use only the Python standard library.

After producing reviewed per-line PDF markings, run `python3 scripts/optimize_markings.py` to replace each connected group of line rectangles with one enclosing box in the complete articles and the combined discussion packet. This step uses the existing line geometry, removes the internal borders, and keeps separated passages, columns and marking colors distinct. It also refreshes the PDF hashes in the manifests. Install `scripts/marking-requirements.txt` for this step; `python3 scripts/optimize_markings.py --check` checks the committed PDFs without modifying them, and `python3 -m unittest discover -s scripts -p 'test_*.py'` runs the marking and packet-order regression tests.

Run `python3 scripts/audit_markings.py` to check Jain/TQT markings on the selected discussion and reference pages of all 22 complete papers, including identifying titles and numbered citations, and to compare the combined packet against their source pages. The reviewed supplemental spans in `docs/Marking-Review.json` include complete TQT table rows and a vector-only figure legend; unrelated authors sharing the Jain surname have explicit exclusions. `--apply` adds those reviewed boxes and rebuilds the combined packet and its page index. After changing selection or order, rebuild the packet, reports and site, render the report PDFs, and refresh manifests. Text search cannot inspect labels drawn as graphics, so new source versions also need rendered-page review.

## Attribution

The repository's existing [Apache 2.0 license](LICENSE) applies to original project code. Included scholarly articles, publisher captures, and third-party materials retain their own copyrights and applicable terms; their inclusion does not relicense them. Source URLs and evidence IDs are retained in the research package. Map geometry uses public-domain Natural Earth data.
