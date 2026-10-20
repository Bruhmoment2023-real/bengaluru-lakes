# Captions (notes only)
- fig_annual_production.png: records per publication year (n=332). Data: tables/annual_production.csv. Caution: 2026 is a partial year; duplicates across databases were merged by DOI/title.
- fig_bradford.png: cumulative share of records by venue rank. Data: tables/venues.csv. Caution: 113 records have no venue string, forming the largest "venue".
- fig_term_frequency.png: records whose title/abstract contain the term (word-boundary match). Caution: Crossref records have no abstract, so term counts underestimate.
- fig_topics_by_year_stacked.png: topic families by year (a record can fall in several). Caution: families are hand-defined term sets (see bib_analysis.py).
- fig_term_cooccurrence.png: terms co-occurring in >= 3 records; spring layout seed 7; distances are not metric.
- fig_burst_timeline.png: Kleinberg two-state burst detection (s=2, gamma=1) on yearly term share, 2000-2026. Caution: yearly counts are small (1-34 records); 2026 bursts are partial-year artefacts.
- fig_main_path.png: main path through 92 papers / 144 citations (only records with OpenAlex reference lists). Caution: y-axis jitter is arbitrary; sparse network (5 weak components).
