# bibliometrics - literature map for 13-bengaluru-lakes

Corpus: 332 records retained at title/abstract screening (data/corpus.csv); pulled 2026-10-17 from OpenAlex, Crossref, DOAJ, Google Scholar, Semantic Scholar (partial), Shodhganga. See search-protocol.md and scopus-queries.md.

Contents
- data/corpus.csv - corpus with screening status; evidence-table.csv - 60 highest-priority records (20 extracted studies first; each row says "full text read" or "abstract read" or "metadata only"; the one-line finding is the abstract sentence chosen by program).
- python/bib_analysis.py (production, Bradford, Lotka counts, term frequency, topics by year, co-occurrence + VOSviewer files, Kleinberg bursts, evidence table), python/main_path.py (search path count main path). R/ is empty (Bibliometrix not run; reason in search-protocol.md).
- tables/, figures/ (+ figures/captions.md), vosviewer/ (terms_map.txt, terms_network.txt: open in VOSviewer 1.6.20 via "Create a map based on network data" with map + network files; the program is at D:\Research-Publishing\_tools\VOSviewer if unzipped).
- pdfs/ - empty on D: by design; the 165 open-access full texts live on E:\Research-Staging\13-bengaluru-lakes\fulltext (sizes in ../data/raw/fulltext-fetch-log.csv). Several are publisher PDFs without a re-use licence, so they are not copied into the shareable folder.
- gap-analysis.md.

Regenerate: `powershell -File ..\depth\appendix\rerun.ps1`. Limits: metadata-only corpus (113 records without venue), partial year 2026, term matching is substring/word match on title+abstract, authors table contains parsing artefacts, only 253 records have reference lists.
