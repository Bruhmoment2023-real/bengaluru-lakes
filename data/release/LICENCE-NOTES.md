> **Note for this repository:** these notes were written for the complete 108,915-row table. In this repository release, the CPCB rows (12,256), the 2011 Mines & Geology CSV rows (1,702) and the IISc rows (16) are **not included**, because no explicit licence permitting redistribution was found. `lake_measurements_long.csv` here has 94,941 rows (KSPCB and the 20 published studies). See the README for how to obtain the CPCB tables.

# Licence and provenance notes (read before depositing)

Checked 2026-10-17. "Opened" = the page or file was fetched and read in this session.

| Source | What was used | Licence / terms found | Handling in the release |
|---|---|---|---|
| KSPCB monthly "Lakes Water Quality Report" (Jul 2023 - Nov 2025), 28 PDFs, via OpenCity dataset `bengaluru-lake-monthly-water-quality-reports` | station values for ~140 lakes | OpenCity dataset page lists licence "Other (Public Domain)" (CKAN API field `license_id: other-pd`, opened). Originator: KSPCB. | values released with citation of KSPCB and OpenCity; original PDFs not redistributed (they are in the OpenCity mirror) |
| CPCB NWMP annual tables "Water quality of lakes, ponds and tanks" 2016-2024 (cpcb.gov.in/wqm/...) and 2013-14 HTML | annual min/max per station | no licence statement on the pages opened; CPCB publications are public documents; OpenCity lists a CPCB NWMP 2021 file as "Other (Public Domain)" | facts (numbers) released with citation; PDFs not redistributed; ask CPCB if a formal licence statement is wanted |
| "Bangalore Lakes Water Quality Results (2011)" CSV via OpenCity (`bengaluru-lakes-water-quality-data`) | 1,702 values | OpenCity licence field "None" (no licence stated); publisher listed as Department of Mines and Geology | numbers released as extracted facts with citation; flag `licence not stated`; consider asking OpenCity/publisher before deposit |
| IISc ENVIS Technical Report 116 (2017), Table 3.1 | 16 range values | report copyright IISc; OpenCity record licence "None" | short factual ranges with citation |
| 20 published studies (see studies.csv) | numerical results transcribed from tables/text | publisher/author copyright in the text and tables; numerical facts are not copyrightable, but the arrangement of a table may be. Open-access licences vary (some CC BY, many "open PDF" without a licence) | only numbers + bibliographic pointer (page/table) are released; no table images or text reproduced; the PDFs are NOT included |
| OpenStreetMap (Overpass, Nominatim) | lake coordinates | ODbL 1.0 | lakes.csv is a derived database: attribution "(c) OpenStreetMap contributors" and share-alike apply to lakes.csv coordinates; kept in a separate file so the measurement table can carry its own licence |
| India-WRIS, data.gov.in | none used | no Bengaluru lake water-quality table found | listed as checked, nothing extracted |
| Lake Development Authority site | none | site did not respond | listed as unreachable |

Proposed licence for the compilation (Sean's decision): CC BY 4.0 for `lake_measurements_long.csv`, `studies.csv`, `screening_log.csv`, derived files and code (MIT); `lakes.csv` under ODbL because of OSM coordinates. Each row's source and the notes above stay with the file.

Not shareable: the PDFs of papers, thesis files, scanned official reports (kept in E:\Research-Staging).
