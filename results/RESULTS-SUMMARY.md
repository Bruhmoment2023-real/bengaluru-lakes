# RESULTS-SUMMARY (bullets; numbers come from results/tables/*.csv produced by code/*.py on 2026-10-17)

## Evidence base
- Search: 6,402 records from 6 databases (OpenAlex 819, Crossref 4,600, DOAJ 225, Google Scholar 240, Semantic Scholar 200, Shodhganga 318) -> 3,541 after de-duplication -> 332 retained at title/abstract. Full text obtained for 165; 20 published studies extracted, 4 excluded at full text, 30 eligible queued, 111 triage-negative (not read by eye), 167 not obtainable (X6). See fig01 and data/release/screening_log.csv.
- Dataset (data/release/lake_measurements_long.csv): 108,915 rows (104,283 with a numeric value), 24 sources, 202 lake keys plus one key for a group of four lakes that one study reported together (39 rows; not counted as a lake, so 203 keys in the file). Sources: KSPCB monthly reports 88,935 rows (27 of 28 files parsed; Jul 2023 - Nov 2025), CPCB NWMP annual min/max 12,256 rows (2013-14 Ulsoor, 2016-2024), DMG 2011 CSV 1,702, IISc blueprint 16, 20 published studies 6,006.
- Parameter coverage (t03/t03b): DO, BOD, pH, EC, coliforms and temperature are covered mainly by the official series; nutrients are N species in KSPCB (nitrate-N, nitrite-N, ammoniacal-N; phosphate in part of the months) and nitrate/phosphate in 12 studies; heavy metals: 3,011 KSPCB values (2024-25 months), 510 DMG 2011 values, and 7 studies (L068 Varthur, L112 16 lakes, L138, L147 Hebbal, L409 Bellandur, L421 Ulsoor/Agara, L445/L453/L492 in part). Foaming: no measurement dataset; 19 candidate papers mention foam/froth/surfactant/fire in title/abstract (t09).
- Lakes: only Bellandur (66 candidate papers), Varthur (41), Hebbal (38), Ulsoor (22) exceed 20 candidate mentions; 122 of 202 lake keys have coordinates; most KSPCB-monitored lakes have no published study (fig05, fig02).
- Time: published extracted studies cover 2005-2025 sparsely (single lake-years); no lake has a continuous published series. The only multi-year series are official: CPCB 2013-2024 for Ulsoor (2015 missing), CPCB 2016-2024 for ~44 stations, KSPCB monthly 27 months. 7 of 20 studies state no sampling year.

## Compliance (RQ3; t04*, t05; fig06)
- KSPCB lake-months classified (n = 3,051): best class met D 61.0 percent, E 34.9 percent, below E 3.4 percent, unclassified 0.8 percent; class A, B, C: none. Exceedance shares: DO < 4 mg/L 34 percent; DO < 5 mg/L 55 percent; BOD > 3 mg/L 99.9 percent; total coliform > 5,000 MPN/100 mL 51 percent; ammoniacal-N > 1.2 mg/L 27 percent (proxy); pH outside 6.5-8.5 2.2 percent.
- By lake (t04): months with DO < 4: Rayasandra 100 percent, Vengaiyyanakere (KR Puram) 95, Chandapura 89, Yellamallappa Chetty 85, Varthur 50, Bellandur 35, Hebbal 16, Ulsoor 15. BOD > 3 in at least 98 percent of months for all four of Bellandur, Varthur, Hebbal, Ulsoor.
- CPCB annual tables: in 2023, 121 of 121 stations never met BOD < 3 and 100 of 121 never met total coliform < 5,000; in 2024, 121 of 122 never met BOD < 3 (t05).
- Literature values (undated or old) are consistent in direction (Bellandur/Varthur DO < 5, BOD tens of mg/L) but cannot be tested statistically (see consistency).

## Trends (RQ4; t06-t08; fig07)
- Eligibility (amended, 02a A4): no published-literature lake-parameter series met the pre-set rule. CPCB annual series (>= 7 years over >= 8 years) exist for 42-43 stations; KSPCB monthly (27 months) for 113 station-parameter series (exploratory).
- CPCB annual extremes 2016-2024: Mann-Kendall significant before correction for 6 of 43 stations (max BOD), 12 of 42 (min DO), 16 of 43 (max faecal coliform), 14 of 43 (max total coliform); after Holm correction 1, 0, 1, 1. Median tau: BOD +0.20 (worsening), DO -0.38 (worsening), faecal coliform -0.48 and total coliform -0.39 (falling extremes). Direction is mixed: lower coliform maxima with lower DO minima.
- Balanced panel (41 stations in every year 2016-2024, fig07): median of annual max BOD 19 -> 30 mg/L; median annual min DO 2.5 -> 0.7 mg/L; median annual max faecal coliform 7.0e6 -> 1.4e4 MPN/100 mL. DO 0.3 mg/L entries are detection-limit values.
- KSPCB monthly 2023-25: raw significant slopes for 10 of 113 BOD series and 15 of 113 DO series, 2 and 1 after Holm correction; median tau about 0 (-0.02 BOD, +0.07 DO): no consistent short-window trend.
- Step change around 2015-17: testable only for Ulsoor (CPCB station 1388; 3 annual values <= 2016 vs 7 values >= 2018): min DO 5.7 -> 2.0 mg/L (Mann-Whitney p = 0.021, n = 3 vs 7, uncorrected, exploratory), max BOD 16.0 vs 17.4 (p = 0.73), max faecal coliform 540 vs 94,000 MPN (p = 0.38). Bellandur/Varthur: only 2016-17 before the orders, so not testable (hypothesis H3 not rejected, not confirmed).

## Consistency (RQ5; t10, t11; fig08)
- CPCB 2023-24 annual min-max contain 99.5-100 percent of the KSPCB monthly values at the same station codes (t10): the two official series are one data stream, not two independent sources (changes the trend rule, 02a A4).
- Between independent sources for the same lake the spread is large and partly methodological. Examples (t11): Hebbal BOD median 6.0 (L147, 2013, 108 values), 22.9 (L287, undated, 38 values), 3.1 (L492, undated, 3 values), 7.0 (KSPCB 2023-25); Varthur BOD 58.5 (L514, 2025) vs 14.0 (KSPCB/CPCB medians) vs 6.4 (L112, KSPCB 2008-10 means); Ulsoor DO 12 (L207, 2011-12) vs 5.3-5.7 (KSPCB/CPCB).
- Quality score (0-6) of the 20 studies: median 3 (range 1-4), 15 of 20 score >= 3. Sensitivity (t12): literature values failing DO >= 4: 27.4 percent (all, n = 241) vs 28.1 percent (score >= 3, n = 235); BOD > 3: 95.1 vs 94.9 percent; pH outside 6.5-8.5: 23.6 vs 24.6 percent. Restricting to higher-scored studies changes nothing material.
- Data-quality exclusions: two papers with physically implausible tables; several others kept with flags (DO 41.2 mg/L for Ulsoor in the DMG 2011 CSV; DO 10-14 with BOD 20-30 in L207).

## Limits
- Single screener/extractor; 20 of ~165 retrieved studies read; 167 candidates without open full text; Google Scholar/Semantic Scholar partial.
- BOD basis (3 d at 27 C vs 5 d at 20 C), nitrate/phosphate basis and coliform method (MPN vs CFU) differ or are unstated; values are flagged, not converted unless the basis is stated.
- KSPCB/CPCB use annual extremes or single monthly grabs; neither gives sampling dates inside the month.
