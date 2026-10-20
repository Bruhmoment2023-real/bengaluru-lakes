# Search protocol (as run) - 2026-10-17

Written before screening in `02-design.md` (section 5-6); deviations in `02a-amendments.md`.

## Databases and strings
| database | access | strings (families defined in 02-design.md) | pages/rows | notes |
|---|---|---|---|---|
| OpenAlex | REST, keyless, `filter=title_and_abstract.search:` | A, B1, C, A2 (exact boolean strings in data/raw/search-log.csv) | up to 8 x 100 per family | cursor paging refused without key, so page paging; 819 records |
| Crossref | REST, keyless | 23 phrase queries ("Bangalore lake water quality", "Bellandur lake", "Varthur lake", lake names + water ...) | 2 x 100 each | relevance ranked, no abstracts: 4,600 records, screened on title |
| Semantic Scholar | Graph API, keyless | 6 phrase queries | 100 each | HTTP 429 for 4 of 6 queries; 200 records |
| DOAJ | article search API | 8 phrase queries | 2 x 100 | 225 records |
| Shodhganga | simple-search HTML | 11 phrase queries | 3 x 10 | 318 records (thesis metadata) |
| Google Scholar | plain fetch, 10 s spacing | 12 phrase queries | 2 x 10 | 240 records; no block encountered; stopped-on-block rule not triggered |
| Official: KSPCB (OpenCity mirror), CPCB NWMP, DMG 2011 CSV, IISc blueprint, NEERI 2020 (not extracted), India-WRIS, data.gov.in, LDA | direct fetch | - | - | see LICENCE-NOTES.md and 02a A3 |

## Counts (PRISMA-style; see results/figures/fig01_prisma_flow.png)
| step | n |
|---|---|
| records identified | 6,402 |
| duplicates removed | 2,861 |
| screened title/abstract | 3,541 |
| excluded: rule pre-screen / manual title-abstract | 2,994 / 215 |
| retained for full-text check | 332 |
| full text retrieved | 165 |
| not obtained (X6) | 167 |
| excluded at full text | 4 |
| extracted into dataset | 20 studies (+ DMG 2011, IISc blueprint, KSPCB, CPCB) |
| eligible, extraction queued | 30 |
| retrieved, triage-negative (unverified) | 111 |

## Inclusion/exclusion rules
As 02-design.md section 4. Corpus for bibliometrics = the 332 records retained at title/abstract stage (data/corpus.csv).

## Scopus / Web of Science
Not used (no login). Paste-ready strings are in `scopus-queries.md`. `scopus-drop\` is empty (created, no exports present).

## Why Bibliometrix was not run
Bibliometrix needs Scopus/WoS-style fields (affiliations, cited references, author keywords). The corpus comes from OpenAlex/Crossref/Scholar/Shodhganga metadata: only 253 OpenAlex records carry reference lists, 113 of 332 records carry no venue, and most have no affiliations or keywords. Python equivalents of the meaningful outputs were produced instead (annual production, Bradford, Lotka counts, term frequency, co-occurrence network + VOSviewer files, Kleinberg bursts, main path). Co-citation, bibliographic coupling, historiograph, thematic map and three-field plots were not produced: they would be uninformative on this metadata.
