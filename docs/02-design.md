# 02 - Design and PRISMA-style protocol (written 2026-10-17, BEFORE any search or screening)

Protocol version 1.0. Any later change is logged in the "Amendments" section at the bottom with date and reason. Search counts and screening results were NOT known when this was written.

## 1. Working title
Water quality in Bengaluru lakes: a systematic review and open dataset of published and official measurements.

## 2. Research questions
- RQ1 Coverage: which lakes, years, parameters and study designs does the evidence cover, and where are the gaps?
- RQ2 Comparability: how much reported evidence can be harmonised to common units/methods, and what must be flagged?
- RQ3 Compliance: how do reported values compare with the CPCB Primary Water Quality Criteria for Designated-Best-Use Classes (DO, BOD, total coliform, pH, free ammonia, EC, boron)?
- RQ4 Change over time: where a lake-parameter series is long enough (rule below), is there a monotonic trend, and is there a step change around 2015-2017 (foaming/fire episodes at Bellandur/Varthur, NGT orders)?
- RQ5 Consistency: how much do studies agree for the same lake and period, and does the spread relate to method and reporting quality?

## 3. Hypotheses (directional, written before data)
- H1 Evidence is concentrated on a few large sewage-fed lakes (Bellandur, Varthur) and on DO/BOD/COD/nutrients; coliforms, heavy metals and foaming-specific parameters are sparser.
- H2 Most reported lake-period values for DO and BOD fail Class D/C criteria; sewage-fed lakes fail every class.
- H3 There is no robust pooled improvement after 2017 (series insufficient or inconsistent); apparent trends are dominated by between-study methodological differences.
- H4 Fewer than half of primary studies report sampling dates, replicate numbers and analytical methods adequately.
Tested descriptively; no hypothesis is changed after results.

## 4. Eligibility criteria
Include (all):
- Population: one or more named lakes/tanks/wetlands within the Bengaluru metropolitan area (or explicitly "Bangalore/Bengaluru lake" in Bengaluru Urban/Rural district).
- Outcome: at least one numeric in-situ or laboratory measurement of surface water (or inflow/outflow) quality: DO, BOD, COD, pH, temperature, EC/TDS, turbidity, N species, P species, chlorophyll, coliforms, heavy metals, surfactants/foam-related, alkalinity, hardness, chloride, sulphate, etc.
- Source: peer-reviewed article, thesis (Shodhganga), conference paper, preprint, government/agency report or dataset (KSPCB, CPCB, LDA, BBMP, ENVIS Karnataka, India-WRIS, data.gov.in), NGT/court-filed monitoring reports.
- Any year; English.
Exclude (reason codes logged):
- X1 not Bengaluru; X2 no numeric water-quality value (qualitative, remote-sensing only, modelling without observed values); X3 groundwater/borewell only, or sediment/biota only; X4 duplicate of another record (keep primary, link); X5 review without new numeric values (kept in a "reviews" list); X6 full text not obtainable (logged; listed as "unextractable"); X7 non-English; X8 other (free text).
Satellite-derived proxies are tracked separately and not in the main measurement dataset.

## 5. Information sources (direct fetch; no sign-ups, no logins, no evading blocks)
OpenAlex, Crossref, Semantic Scholar, DOAJ, Shodhganga (INFLIBNET), Google Scholar (attempted; if blocked, reported as blocked and not circumvented). Official: KSPCB, CPCB (NWMP/NWQM reports), Lake Development Authority / BBMP, ENVIS Karnataka, India-WRIS, data.gov.in, NGT. Snowballing: reference lists of included reviews. Access date recorded per source. Exact strings in `data/raw/search-log.csv`.

Search string families (adapted to each database syntax):
- A: (Bengaluru OR Bangalore) AND (lake OR tank OR wetland) AND ("water quality" OR physico-chemical OR pollution OR BOD OR "dissolved oxygen" OR eutrophication)
- B: named lakes (Bellandur, Varthur, Ulsoor, Hebbal, Sankey, Lalbagh, Agara, Madiwala, Jakkur, Yelahanka, Puttenahalli, Kaikondrahalli, Nagawara, Hennur, Kengeri, Hesaraghatta, ...) AND (lake OR tank) AND water
- C: (Bellandur OR Varthur) AND (foam OR froth OR fire OR surfactant OR "heavy metal")
- D (theses): Bangalore lake water quality

## 6. Selection process
- Deduplication by DOI, then normalised title + year.
- Stage 1 title/abstract, Stage 2 full text. Single screener (the agent: rule-based keyword pre-screen then manual reading of borderline records) - a stated limitation. All decisions and reason codes in `data/clean/screening-log.csv`.
- Fixed rule: retain for full-text check if title/abstract mentions a Bengaluru lake (gazetteer in `code/`) or Bengaluru/Bangalore with lakes AND water-quality terms.

## 7. Data items (tidy long format, one row per reported measurement)
record_id, lake (canonical), lake_as_reported, site, sample_date_start, sample_date_end, period_precision, season, parameter (canonical), parameter_as_reported, statistic, value, unit_as_reported, value_std, unit_std, method, n_samples, source_type, source_id, page/table, extraction_mode, comparability_flag, notes.
Harmonisation: DO, BOD, COD, nutrients to mg/L (basis "as N"/"as NO3"/"as PO4" recorded, converted only when stated; otherwise flagged); coliforms to per 100 mL (MPN vs CFU kept distinct); EC to uS/cm; turbidity NTU (JTU/FTU flagged); metals mg/L. Non-comparable values (unknown basis/unit, BOD3@27C vs BOD5@20C, range-only, graph-only) are flagged, retained, never silently converted or dropped. Figure-only values are not digitised.

## 8. Quality scoring (per study, 0-6, fixed now)
1 sampling dates reported; 2 sites/number described; 3 analytical method/standard cited; 4 replicates or n given; 5 QA/QC or detection limits mentioned; 6 raw (not only summary) data available. Sensitivity analysis restricted to score >= 3.

## 9. Analysis plan
- Coverage: counts by lake x year x parameter; heat maps; map of lakes with study counts (coordinates from OpenStreetMap, ODbL, queried slowly with a descriptive User-Agent).
- Compliance vs CPCB Primary Water Quality Criteria for Designated-Best-Use Classes (cpcb.gov.in/water-quality-criteria, page updated 11 Oct 2019, opened 2026-10-17): A DO>=6, BOD<=2, TC<=50 MPN/100mL, pH 6.5-8.5; B DO>=5, BOD<=3, TC<=500, pH 6.5-8.5; C DO>=4, BOD<=3, TC<=5000, pH 6-9; D DO>=4, free NH3-N<=1.2, pH 6.5-8.5; E pH 6-8.5, EC<=2250 umho/cm, B<=2 mg/L (SAR<=26). Ranges classified compliant / non-compliant / straddles.
- Trend: a series qualifies with >= 5 distinct years spanning >= 8 years. Mann-Kendall + Theil-Sen on annual medians; pre/post-2017 comparison only where >= 3 annual values each side; Holm adjustment across series. No pooled meta-regression unless units/methods are comparable; any pooling is exploratory.
- Consistency: between-study coefficient of variation per lake x parameter x 5-year window, versus quality score.
- Publication bias: not applicable to non-effect-size data; stated as limitation.

## 10. Threats to validity (pre-stated)
- Single screener/extractor; no reliability check by a second coder (mitigation: rows carry page/table; scripted 10% re-extraction sample).
- Google Scholar and some publishers cannot be scraped; indexed literature incomplete; grey literature (e.g. IISc EWRG technical reports) poorly indexed.
- Paywalled full texts unread: listed, not extracted (X6).
- Sampling bias (problem lakes oversampled), seasonal confounding, stitched series from different sites/methods, pseudo-replication.
- Official reports: scans, differing stations/methods/detection limits.
- Copyright: numeric facts released with citations; no reproduction of tables; licence recorded per source.

## 11. Licensing plan
Compilation under CC BY 4.0; each row carries source licence field; official data listed with licence found (GODL-India where applicable) or "no licence stated - facts extracted with citation; original file not redistributed".

## Amendments
(none yet)


> Later changes: see 02a-amendments.md (A1-A8), dated 2026-10-17.
