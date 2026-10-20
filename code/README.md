# code/ - how the results are built (resumable; HTTP responses cached on E:)

Python: `D:\Research-Publishing\_tools\biblio-venv\Scripts\python.exe -X utf8 -I <script>` (pandas, requests, pdfplumber, matplotlib, scipy, networkx, plotly). No personal identifier is sent in any request (code/common.py uses a descriptive User-Agent only).

Order (also automated in `..\depth\appendix\rerun.ps1`):
1. search.py -> data/raw/records-raw.csv, search-log.csv (6 sources)
2. screen1.py (de-duplicate, rule pre-screen) -> data/clean/records-dedup*.csv, screen-pool.csv; screen2.py (manual decisions for the 547-record pool) -> screening-pool-decisions.csv
3. fetch_fulltext.py (open links only, 3 s per host; ~90 min) -> E:\...\fulltext; triage_fulltext.py -> data/clean/fulltext-triage.csv
4. Official data: extract_kspcb.py (28 PDFs -> official_kspcb_long.csv), lakes_gazetteer.py + nominatim_fill.py (station/lake coordinates), extract_cpcb.py (CPCB NWMP tables), ext_dmg2011.py, ext_bp2017.py
5. Literature extraction: litlib.py (helpers), ext/p<id>.py one script per paper (each writes data/raw/extraction/<id>.csv; hand-typed values are verified against the text layer by `Ex.rec`; table values are parsed by program; PDF word-position readers `pdf_grid/pdf_lines` handle scrambled layouts). Helper CLIs: tabs.py, show.py, pl.py, pageimg.py.
6. build_dataset.py -> data/release/lake_measurements_long.csv + studies.csv; build_lakes.py -> lakes.csv; finalize_screening.py -> screening_log.csv, PRISMA counts and figure
7. analysis_coverage.py, analysis_compliance_trends.py -> results/tables, results/figures
8. ../bibliometrics/python/*.py, ../depth/*.py

Notes: `lakekey.py` normalises lake names. Random seeds: the only random element is the spring layout (seed 7) and the jitter in main_path.py (seeded from node ids). Software versions: see data/release/../../depth/appendix/reproducibility-checklist.md.
