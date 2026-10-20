"""Citation library: BibTeX + RIS from Crossref transform endpoints for every DOI cited in the folder (studies.csv, evidence table, prior-work list). Entries without a DOI are built from corpus metadata with a note field."""
import pandas as pd, re, sys, os, json
sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from common import get
R = r"D:\Research-Publishing\13-bengaluru-lakes"; D = R + r"\depth\citations"; os.makedirs(D, exist_ok=True)
dois = set()
st = pd.read_csv(R + r"\data\release\studies.csv"); dois |= set(st.doi.dropna().astype(str))
et = pd.read_csv(R + r"\bibliometrics\evidence-table.csv"); dois |= set(et.doi.dropna().astype(str))
dois |= {"10.1016/j.envc.2024.100944", "10.1007/s10661-023-11888-1", "10.1016/j.envpol.2023.122773", "10.3390/rs12223843", "10.1186/s42834-020-00049-5"}
mp = pd.read_csv(R + r"\bibliometrics\tables\main_path_papers.csv"); dois |= set(mp.doi.dropna().astype(str))
dois = sorted(d.lower().strip() for d in dois if re.match(r"^10\.\d{4,9}/\S+$", d.strip()))
bib, ris, bad = [], [], []
for doi in dois:
    s, t = get(f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex")
    s2, t2 = get(f"https://api.crossref.org/works/{doi}/transform/application/x-research-info-systems")
    if s == 200 and t.strip().startswith("@"): bib.append(t.strip())
    else: bad.append((doi, s))
    if s2 == 200 and t2.strip().startswith("TY"): ris.append(t2.strip())
open(D + r"\references.bib", "w", encoding="utf-8").write("\n\n".join(bib) + "\n")
open(D + r"\references.ris", "w", encoding="utf-8").write("\n\n".join(ris) + "\n")
# entries without DOI that are cited in the folder (theses, official files)
extra = [
 "@misc{kspcb_monthly_lakes,\n title={Lakes Water Quality Report (monthly), July 2023 - November 2025},\n author={{Karnataka State Pollution Control Board}},\n year={2025},\n howpublished={Mirrored at data.opencity.in, dataset bengaluru-lake-monthly-water-quality-reports},\n note={No DOI. Metadata from the OpenCity CKAN API, accessed 2026-10-17. Licence field: Other (Public Domain).}\n}",
 "@misc{cpcb_nwmp_lakes,\n title={National Water Quality Monitoring Programme: Water quality of lakes, ponds and tanks (annual tables)},\n author={{Central Pollution Control Board}},\n year={2024},\n howpublished={https://cpcb.gov.in/nwmp-data/},\n note={No DOI. Files cpcb.gov.in/wqm/<year>/Water_pond_tanks_<year>.pdf, accessed 2026-10-17.}\n}",
 "@misc{cpcb_criteria,\n title={Water Quality Criteria: Primary Water Quality Criteria for Designated-Best-Use Classes},\n author={{Central Pollution Control Board}},\n howpublished={https://cpcb.gov.in/water-quality-criteria/},\n note={No DOI. Page updated 11 Oct 2019 per the page; opened 2026-10-17.}\n}",
 "@phdthesis{nagendra2014hebbal,\n title={Ecological assessment of the Hebbal Lake, Bengaluru},\n author={Nagendra Babu, R. S.},\n school={Karnataka Veterinary, Animal and Fisheries Sciences University},\n year={2014},\n note={No DOI. Metadata from the title page of the PDF obtained via OpenAlex/Google Scholar link; accessed 2026-10-17.}\n}",
 "@mastersthesis{lekhashree2013multivariate,\n title={Application of multivariate statistical techniques for water quality parameters of lakes in Bangalore},\n author={Lekhashree, S. M.},\n school={University of Agricultural Sciences, GKVK, Bangalore},\n year={2013},\n note={No DOI. Metadata from the title page of the PDF (KrishiKosh); accessed 2026-10-17.}\n}",
 "@techreport{ramachandra2017blueprint,\n title={Bellandur and Varthur Lakes Rejuvenation Blueprint},\n author={Ramachandra, T. V. and Mahapatra, D. M. and Vinay, S. and Sincy, V. and Asulabha, K. S. and Bhat, S. and Aithal, B. H.},\n institution={Energy and Wetlands Research Group, CES, IISc},\n type={ENVIS Technical Report 116},\n year={2017},\n note={No DOI. From the report footer; via OpenCity; accessed 2026-10-17.}\n}",
 "@article{bindiya2008mallathalli,\n title={Environmental degradation of Mallathalli Lake in Bangalore district, India - a case study},\n author={Bindiya, C. and Hanjagi, A. D. and Nandini, N. and Jumbe, A. S.},\n journal={Nature Environment and Pollution Technology},\n volume={7},\n number={2},\n pages={189--196},\n year={2008},\n note={No DOI found. Journal/page data from the PDF header; author names from the Google Scholar record.}\n}",
 "@article{devi2009madhavara,\n title={Assessment of water quality for aquaculture - a case study of Madhavara Lake in Bangalore},\n author={Devi, Ch. Debala and Anandhi, D. Usha},\n journal={Nature Environment and Pollution Technology},\n volume={8},\n number={4},\n pages={755--760},\n year={2009},\n note={No DOI found. From the PDF first page.}\n}",
 "@article{jumbe2009vartur,\n title={Impact assessment of heavy metals pollution of Vartur lake, Bangalore},\n author={Jumbe, Aboud S. and Nandini, N.},\n journal={Journal of Applied and Natural Science},\n volume={1},\n number={1},\n pages={53--61},\n year={2009},\n note={No DOI found. From the PDF header.}\n}"]
open(D + r"\references.bib", "a", encoding="utf-8").write("\n\n" + "\n\n".join(extra) + "\n")
ris_extra = "\n\n".join([f"TY  - GEN\nTI  - {t}\nPY  - {y}\nN1  - No DOI; see references.bib note\nER  - " for t, y in [("KSPCB Lakes Water Quality Report (monthly) Jul 2023-Nov 2025", 2025), ("CPCB NWMP Water quality of lakes, ponds and tanks (annual tables)", 2024), ("CPCB Primary Water Quality Criteria for Designated-Best-Use Classes", 2019), ("Ecological assessment of the Hebbal Lake, Bengaluru (thesis)", 2014), ("Application of multivariate statistical techniques for water quality parameters of lakes in Bangalore (thesis)", 2013),
                                                                                                              ("Bellandur and Varthur Lakes Rejuvenation Blueprint (ENVIS TR 116)", 2017), ("Environmental degradation of Mallathalli Lake in Bangalore district", 2008), ("Assessment of water quality for aquaculture - Madhavara Lake", 2009), ("Impact assessment of heavy metals pollution of Vartur lake", 2009)]])
open(D + r"\references.ris", "a", encoding="utf-8").write("\n\n" + ris_extra + "\n")
n_bib = len(re.findall(r"^@", open(D + r"\references.bib", encoding="utf-8").read(), re.M))
open(D + r"\README.md", "w", encoding="utf-8").write(f"""# Citation library
- references.bib / references.ris: {len(bib)} entries resolved from DOIs by Crossref content negotiation (api.crossref.org/works/<doi>/transform/...) + {len(extra)} hand-made entries without DOI (each has a note saying where the metadata came from). Total BibTeX entries: {n_bib}.
- DOIs tried: {len(dois)}; not resolved: {len(bad)} {bad[:15]}.
- Import into Zotero: File > Import > choose references.ris (or references.bib), tick "Place imported collections and items into new collection". Then check the entries marked "No DOI" against the source PDFs in E:\\Research-Staging\\13-bengaluru-lakes\\fulltext.
- De-duplicated by lower-cased DOI.
""")
print(len(dois), len(bib), len(ris), bad[:10])
