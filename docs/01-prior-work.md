# 01 - Prior work and novelty verdict (searches run 2026-10-17)

Labels: [full text] = opened in full; [abstract] = abstract/metadata text read; [metadata] = title/metadata only.

## Novelty verdict
**Go, with a precise claim.** I found no systematic review (PRISMA-type) of Bengaluru lake water-quality measurements and no open, tidy measurement dataset for these lakes. What exists: (a) scattered primary studies (332 candidate records, 3,541 after de-duplication from six databases), (b) narrative or governance reviews, (c) monthly KSPCB PDFs and CPCB annual PDFs that are public but not tidy. Not claimed as "first": synthesis tables inside reports (IISc EWRG ENVIS TR 116, Table 3.1 for Bellandur/Varthur; Das/Ramachandra group reviews) and one review-like paper compiling 2000-2022 values (Gnanapragasam 2025, [full text], narrative). The claim that survives: first open, row-level, harmonised compilation across lakes and sources, with flags, and the first audit showing that the two official streams are not independent.

Searches behind the verdict (all in data/raw/search-log.csv and data/clean/prior_work_review_like_hits.csv):
- Title/abstract screen of 3,541 de-duplicated records for review/synthesis/compilation/dataset terms with Bengaluru/lake terms: 36 review-like hits, none a systematic review of water-quality data (the hits are narrative reviews, governance papers, a fish-mortality review, theses, and unrelated records picked up by the term "review").
- DataCite API and Zenodo API queries ("Bengaluru lakes water quality", "Bangalore lakes water quality", "Bellandur lake"): no dataset of lake water-quality measurements; datasets found are unrelated (dairy cattle health, ACT lakes in Australia, Chennai) or figshare/Zenodo copies of single papers (e.g. figshare 10.6084/m9.figshare.1101538 is a paper copy on Bellandur).
- OpenCity catalogue (CKAN) holds the KSPCB monthly reports (PDF), a 2011 results CSV, NGT/BBMP/High Court reports: raw material, not a harmonised dataset.
- Caveat: Google Scholar and Semantic Scholar searches were partial; Scopus/WoS not searched (no login). IISc EWRG technical reports are poorly indexed (flagged in the track file): the ENVIS TR 116 blueprint was found through OpenCity, others may exist.

## Closest works
| work | what it is | status | verdict |
|---|---|---|---|
| Sourav S.K., Clements L., Nguyen T.T. et al. (2024) Urbanization and seasonal effects on the lake ecosystem dynamics from 2002 to 2022 in Bengaluru. Environ Challenges. https://doi.org/10.1016/j.envc.2024.100944 | satellite-based lake dynamics | [metadata] (from track-E file; not opened) | not a synthesis of in-situ measurements |
| Jamwal P., Carvalho L., Bhattacharyya S. et al. (2023) The benefits of restoring urban lakes in the tropics. Environ Monit Assess. https://doi.org/10.1007/s10661-023-11888-1 | restoration outcomes | [metadata] | not a systematic dataset |
| Das R., Hoysall C., Rao L. (2023) Surfactants in sewage-fed foaming Bellandur Lake. Environ Pollut. https://doi.org/10.1016/j.envpol.2023.122773 | foam chemistry, one lake | [metadata] | primary study; foam parameters could enter the dataset when extracted |
| Rao S.M., Mogili N.V., Priscilla A., Lydia A. (2020) Aqueous chemistry of anthropogenically contaminated Bengaluru lakes. Sustain Environ Res 30:8. https://doi.org/10.1186/s42834-020-00049-5 | ion chemistry of four lakes, 2018-19 | [full text] | primary study (extracted, pooled table) |
| Ramachandra T.V. et al. (2017) Bellandur and Varthur Lakes Rejuvenation Blueprint, ENVIS TR 116 | report with Table 3.1 ranges "over past several years" | [full text of the table section] | synthesis for two lakes only; ranges used as secondary rows |
| Nagendra Babu R.S. (2014) Ecological assessment of the Hebbal Lake (PhD) | monthly 8-station data 2013 | [full text] | primary; richest single source in the dataset |
| Lekhashree S.M. (2013) MSc thesis: KSPCB 2008-2010 data of 16 lakes | statistics of KSPCB data | [full text] | secondary compilation; the only 2008-10 official-data trace found |
| Moramchetty A. (2025) Ulsoor Lake 2012-2023, IJAES 12(4):9-16 | CPCB NWMP annual values for one lake | [full text] | secondary; mixes means (2012-14) and min-max midranges (2015+): shown by comparison with the CPCB tables |
| Gnanapragasam R.S.K. (2025) Quality of lake water in Bangalore and subterrain aquifers recharge. Curr World Environ 20(3):1027-1035 | narrative review compiling 2000-2022 studies | [full text] | review without new data; excluded X5, useful reading |
| Bareuther M., Klinge M., Buerkert A. (2020) Remote Sensing 12:3843. https://doi.org/10.3390/rs12223843 | weed cover time series | [metadata] | relevant to idea D4, not this paper |
| Ramachandra and group papers 2008-2015 (Bellandur, Varthur, 25-lake series) | primary studies | [metadata]/[abstract] for most; full text not retrieved | candidates (X6 or queued) |

## Annotated bibliography of extracted sources
See `data/release/studies.csv` (citation, quality items, access) and `depth/reading-notes/` (one note each, with verbatim quotes and page numbers). Full citation library: `depth/citations/references.bib` (62 entries).

## Method precedents (for Sean to read)
- PRISMA 2020 statement (Page et al., BMJ 2021) for flow and checklist; PRISMA-P for the protocol. (Not re-fetched in this pass: read from the BMJ site before citing.)
- CPCB "Primary Water Quality Criteria for Designated-Best-Use Classes" (cpcb.gov.in/water-quality-criteria, opened).
