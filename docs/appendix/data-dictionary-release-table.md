# Data dictionary - Bengaluru lake water-quality measurements (candidate data paper)

Version 0.1, built 2026-10-17. All files UTF-8 CSV. Row = one reported value (or one reported summary statistic) for one lake, site, period and parameter.

## lake_measurements_long.csv  (main table)
| column | meaning |
|---|---|
| row_id | integer key |
| record_id | source: `KSPCB` (monthly lake reports), `CPCB` (NWMP annual tables), `DMG2011` (2011 results CSV), `BP2017` (IISc blueprint Table 3.1), `Lnnn` = published study (nnn = pool id; see studies.csv) |
| lake_key | normalised lake name used to join sources (lower case, "lake/tank/kere" removed, spelling variants merged by `code/lakekey.py`). Two lakes named Puttenahalli share one key (flagged in lakes.csv). |
| lake_as_reported | lake name exactly as printed in the source |
| site | station/site label as printed or assigned (KSPCB/CPCB: `STN <code>`) |
| date_start, date_end | ISO dates of the sampling period. Empty when the source does not state the year |
| period_precision | `month`, `year`, `season`, `period (...)`, or a note that the year/month is not stated |
| season | season label when reported |
| parameter | parameter name as normalised during extraction (before harmonisation) |
| parameter_as_reported | label in the source |
| statistic | `single` (one value), `mean`, `sd`, `min`, `max`, `median`, `all_below_limit` |
| value, unit_as_reported | value and unit exactly as printed (blank value = reported below detection/"Absent" with no number; see flag) |
| parameter_std, value_std, unit_std, harmonisation_note | harmonised parameter and value. Rules: nitrate "as NO3" -> mg N/L (/4.4268); phosphate "as PO4" -> mg P/L (x0.3261); conductivity mS -> uS/cm (x1000); coliforms split by basis (`_MPN` vs `_CFU`, never merged); nitrate/phosphate with unspecified basis kept separate (`*_unspecified_basis`); BOD flagged because incubation basis differs (CPCB/KSPCB convention 3 d at 27 C versus 5 d at 20 C) |
| method | analytical method as stated (often only "APHA" or none) |
| n_samples | sample count if stated |
| page_table | table/page in the source (official files: file name and PDF page) |
| extraction_mode | `table-parsed` (program read the table), `hand-transcribed` (typed, with an automatic check that the number occurs near the cited source line), `hand-transcribed from rendered page image`, `CSV parsed` |
| comparability_flag | semicolon-separated cautions (undated, below detection limit, positional column assignment, internal inconsistency, secondary duplicate, etc.). A row with a flag is kept, never silently altered |
| notes | free text |
| source_type | `literature`, `official-monitoring`, `grey-literature` |
| analysis_use | how the row was used in the paper's analyses (see 02-design/02a-amendments) |
| year | year of date_start (blank if undated) |
| quality_score | study quality 0-6 (studies.csv); blank for official series |
| station_code | KSPCB/CPCB station code (official rows only) |

## studies.csv
One row per source: citation, doi, year, source_type, venue, six quality items (q_dates, q_sites, q_method, q_replicates, q_qaqc, q_raw; 1 = yes), quality_score (sum), access (what was opened), notes.

## lakes.csv
One row per lake_key: display name, lat/lon (OpenStreetMap via Overpass or Nominatim, ODbL), coord_source, osm_name, osm_id, coord_confidence (read this; 80 of 202 keys have no coordinates), counts of extracted sources, KSPCB months, CPCB years, number of candidate papers whose title/abstract mention the lake.

## screening_log.csv
Every de-duplicated record (3,541) with stage-1 decision and reason code (X1 not Bengaluru, X2 no numeric values, X3 groundwater/biota/soil only, X5 review, X6 full text not obtained, X8 other/quality), stage-2 status.

## search_log.csv, http-log
Queries, databases, dates, record counts.

## derived_*.csv
`derived_kspcb_monthly_class.csv` (best CPCB designated-use class met per lake-month, computed), `derived_cpcb_annual_wide.csv` (annual min/max per station with status), `qa_cpcb_station_name_check.csv` (CPCB station name versus KSPCB name per station code).

## Known problems
- KSPCB Aug 2023 file not parsed; six 2023-24 files had garbled headers (core columns only, by position; flagged).
- KSPCB/CPCB values printed as "<x(BDL)": value = the printed limit with flag; 4,381 rows had "BDL" without a number (blank value, flagged).
- Coliform counts above 1e8 MPN/100 mL are printed in the sources and flagged as implausible.
- CPCB 2015 file not parsed; 2012 not found; CPCB 2013-14 only Ulsoor (hand-entered).
- CPCB and KSPCB are not independent sources (CPCB 2023-24 ranges contain 99.5-100 percent of KSPCB monthly values at the same stations).
- DMG 2011 CSV: units, months and method are not printed; OCR-type artefacts (decimal points lost) were repaired by rule and flagged.
- Literature: 7 of 20 extracted studies give no sampling year (all their rows have blank dates); L462 and L112 are secondary compilations of CPCB and KSPCB data (L462 is excluded from analyses as a duplicate of CPCB).
