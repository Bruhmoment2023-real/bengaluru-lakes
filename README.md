# Water quality in Bengaluru's lakes: a systematic search and open dataset of published and official measurements

Archived on Zenodo: https://doi.org/10.5281/zenodo.23537686 (this DOI always points to the latest version).

Sean Solano Paul, Independent researcher, Bengaluru, India. Funding: none. Competing interests: none.

## Summary

Bengaluru's lakes became known for foaming and fires, yet their water-quality measurements are scattered across papers, theses, reports and monthly PDF bulletins. This repository holds the code, screening record, extracted data and results behind a systematic search of six databases and the official sources (3,541 unique records screened), from which every reported measurement was extracted from 20 published studies and from the Karnataka State Pollution Control Board (KSPCB) monthly lake reports and Central Pollution Control Board (CPCB) annual tables, each row carrying provenance and comparability flags. Analyses cover coverage by lake and year, compliance with CPCB designated-use classes, and trend tests.

## Repository layout

```
code/            extraction, build and analysis scripts (code/README.md gives the order); ext/ has one extractor per paper
data/release/    released tables: lake_measurements_long.csv, studies.csv, lakes.csv, screening_log.csv, search_log.csv,
                 derived_kspcb_monthly_class.csv, DATA-DICTIONARY.md, LICENCE-NOTES.md
data/clean/      intermediate tables (KSPCB long table, gazetteer, screening decisions, full-text triage)
data/raw/        search-log.csv and extraction/ (one CSV of values transcribed from each published study)
results/         tables (t01-t12), figures (PRISMA flow, coverage, compliance, trends, map), RESULTS-SUMMARY.md
bibliometrics/   literature map: scripts, tables, figures, VOSviewer files, gap analysis, search protocol
docs/            prior-work review, design, amendments, appendix (rerun script, data dictionary), citations (.bib/.ris)
```

## How to reproduce

- Python 3.12; `pip install -r requirements.txt`. Scripts are run with `python -X utf8 -I <script>`.
- Run order is in `code/README.md` and `docs/appendix/rerun.ps1`: `build_dataset.py`, `build_lakes.py`, `finalize_screening.py`, `analysis_coverage.py`, `analysis_compliance_trends.py`, then `bibliometrics/python/bib_analysis.py` and `main_path.py`.
- The scripts were written against a working tree rooted at `D:\Research-Publishing\13-bengaluru-lakes` (see `R = ...` near the top of each script and `code/common.py`); edit that root path to your checkout.
- `build_dataset.py` also reads CPCB and 2011 inputs that are not redistributed here (see below). To rebuild the full 108,915-row table, obtain those sources and re-create the inputs with `extract_cpcb.py` and `ext_dmg2011.py` / `ext_bp2017.py`. Otherwise use the released subset in `data/release/`.
- Searches (`search.py`) and full-text fetching (`fetch_fulltext.py`) call public APIs and are slow and rate-limited; no personal identifier is sent.

## Data sources and licences

| Source | Used for | Terms |
|---|---|---|
| KSPCB monthly "Lakes Water Quality Report", Jul 2023 - Nov 2025, via OpenCity | station values (~140 lakes) | OpenCity lists "Other (Public Domain)"; included, cite KSPCB and OpenCity |
| 20 published studies (list in `data/release/studies.csv`) | numerical values transcribed with page/table pointers | publisher/author copyright in the text; only numbers and pointers released, no text or table images |
| OpenStreetMap (Overpass, Nominatim) | lake coordinates in `lakes.csv` and the gazetteer | ODbL 1.0: (c) OpenStreetMap contributors; share-alike applies to those coordinates |
| Bibliographic APIs (OpenAlex, Crossref, DOAJ, Semantic Scholar, Shodhganga, Google Scholar) | search and screening records | metadata only; abstracts removed from the released corpus |
| CPCB NWMP annual lake tables 2013-2024 | analysis | no licence statement found: raw/wide tables NOT redistributed (code and source URLs provided) |
| "Bangalore Lakes Water Quality Results (2011)" (Department of Mines and Geology, via OpenCity) | analysis | no licence stated: NOT redistributed |
| IISc ENVIS Technical Report 116 (2017), Table 3.1 | 16 range values | report copyright IISc: NOT redistributed |

### CPCB source files (not redistributed)
Central Pollution Control Board, National Water Quality Monitoring Programme, "Water quality of lakes, ponds and tanks" (cpcb.gov.in, Water Quality Monitoring pages). Files used, by year:
- 2013 and 2014: HTML station tables (yearly pages)
- 2015: `NWMP_2015.pdf`
- 2016 to 2024: `Water_pond_tanks_<year>.pdf` (one file per year)
- 2024 also: `LPT-PhysicoChemical.pdf`, `LPT-Nitorgen_Indicator.pdf`, `LPT-Bectological.pdf` (CPCB's own file names)
Download them and run `code/extract_cpcb.py` to rebuild the 12,256 CPCB rows.

Full provenance notes: `data/release/LICENCE-NOTES.md` (written for the complete table; the rows it lists for CPCB, the 2011 CSV and IISc are the ones omitted here).

## Not included and why

- `data/release/lake_measurements_long.csv` is a subset: the 12,256 CPCB rows, 1,702 rows of the 2011 results CSV and 16 IISc rows (licence not stated or restricted) are removed, leaving 94,941 rows (KSPCB and the 20 published studies). `derived_cpcb_annual_wide.csv`, the CPCB wide table and the CPCB station-name QA file are likewise omitted; CPCB-based result tables and figures derived by the author are kept. Obtain the CPCB tables from cpcb.gov.in (NWMP, "Water quality of lakes, ponds and tanks") and run `code/extract_cpcb.py`. So that the station counts in the paper (122 distinct stations; 41 in every year 2016-2024; 44 in 2016, 121 in 2023, 122 in 2024) can be checked without the CPCB rows, `results/cpcb_station_counts.csv` gives counts only (stations and lakes per year, and how many of the nine years each station appears in), made by `code/count_cpcb_stations.py`.
- Full-text PDFs and text of papers, theses and scanned official reports (copyright); the KSPCB/CPCB bulletin PDFs (fetch from the OpenCity mirror and cpcb.gov.in).
- Raw API responses, logs and caches (`data/raw/records-raw.csv`, HTTP logs): regenerate with `code/search.py`.
- Large intermediate record tables (`candidates.csv`, `records-dedup*.csv`, `screen-pool.csv`, the 15 MB `official_kspcb_long.csv`): regenerate with `screen1.py` and `extract_kspcb.py`.
- Abstract and full-text columns of the bibliographic corpus, and per-paper reading notes (they contain quotations).
- Contact details found in scraped source text were redacted.

## Citation

Solano Paul, S. (2026). Water quality in Bengaluru's lakes: a systematic search and open dataset of published and official measurements. Code and data repository. See `CITATION.cff`. A Zenodo DOI will be added when the repository is made public.

## Licences

Code: MIT (`LICENSE`). Author-derived data, results and figures: CC BY 4.0 (`LICENSE-DATA.md`). Third-party source data keep their own terms.
