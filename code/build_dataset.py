"""Build the tidy measurement dataset (literature + KSPCB monthly + CPCB NWMP) and the study registry.
Inputs : data/raw/extraction/*.csv (literature), data/clean/official_kspcb_long_clean.csv, data/clean/official_cpcb_nwmp_karnataka_lakes_wide.csv, data/clean/lake_gazetteer_kspcb.csv
Outputs: data/release/lake_measurements_long.csv, data/release/studies.csv, data/release/lakes.csv (+ QA log)
"""
import pandas as pd, numpy as np, re, glob, os, difflib, json, sys
sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
R = r"D:\Research-Publishing\13-bengaluru-lakes"
os.makedirs(R + r"\data\release", exist_ok=True)

# ------------------------------------------------------------------ study registry (19 literature studies fully extracted)
S = [  # id, citation, doi, year, source_type, venue, scores(dates,sites,method,replicates,qaqc,raw), access, note
 ("L047", "Bindiya C., Hanjagi A.D., Nandini N., Jumbe A.S. (2008) Environmental degradation of Mallathalli Lake in Bangalore district, India - a case study", "", 2008, "peer-reviewed", "Nature Environment and Pollution Technology 7(2):189-196", (1, 1, 1, 0, 0, 0), "full text opened (open PDF)", ""),
 ("L063", "Devi Ch.D., Anandhi D.U. (2009) Assessment of water quality for aquaculture - a case study of Madhavara Lake in Bangalore", "", 2009, "peer-reviewed", "Nature Environment and Pollution Technology 8(4):755-760", (1, 0, 1, 0, 0, 1), "full text opened (open PDF)", ""),
 ("L068", "Jumbe A.S., Nandini N. (2009) Impact assessment of heavy metals pollution of Vartur lake, Bangalore", "", 2009, "peer-reviewed", "Journal of Applied and Natural Science 1(1):53-61", (1, 1, 1, 0, 1, 0), "full text opened (open PDF)", "water heavy metals only (Table 1); plant and sediment tables not loaded"),
 ("L112", "Lekhashree S.M. (2013) Application of multivariate statistical techniques for water quality parameters of lakes in Bangalore (MSc thesis, UAS GKVK)", "", 2013, "thesis", "University of Agricultural Sciences, Bangalore (KrishiKosh)", (1, 1, 1, 0, 0, 0), "full text opened (open PDF)", "numbers are KSPCB 2008-2010 data"),
 ("L138", "Ravikumar P., Mehmood M.A., Somashekar R.K. (2013) Water quality index to determine the surface water quality of Sankey tank and Mallathahalli lake, Bangalore urban district, Karnataka, India", "10.1007/s13201-013-0077-2", 2013, "peer-reviewed", "Applied Water Science 3:247-261", (1, 1, 1, 1, 0, 0), "full text opened (open access)", ""),
 ("L147", "Nagendra Babu R.S. (2014) Ecological assessment of the Hebbal Lake, Bengaluru (PhD thesis, KVAFSU Bidar)", "", 2014, "thesis", "Karnataka Veterinary, Animal and Fisheries Sciences University", (1, 1, 1, 0, 0, 1), "full text opened (open PDF)", ""),
 ("L172", "Shekar G., Narayan L., Ramachandra Mohan M. (2015) Impact of urbanization and study of water quality index on Gidadakonenahalli Lake, Bangalore urban district, Karnataka, India", "10.34062/afs.v2i1.1700", 2015, "peer-reviewed", "Advances in Forestry Science 2(1):7-12", (1, 1, 1, 0, 0, 1), "full text opened (open access)", ""),
 ("L175", "Upadhyay A., Chandrakala M. (2015) Pre- and post-monsoon study of physico-chemical parameters of Ulsoor Lake water of Bangalore, Karnataka, India", "10.15680/IJIRSET.2015.0405025", 2015, "peer-reviewed", "Int J Innov Res Sci Eng Technol 4(5)", (0, 1, 1, 0, 0, 1), "full text opened (open PDF)", "year of sampling not stated"),
 ("L207", "Alimuddin (2017) Assessment of physico-chemical parameters of water of Ulsoor Lake in Bangalore, Karnataka", "10.24214/jcbps.D.7.4.80104", 2017, "peer-reviewed", "J Chem Biol Phys Sci Sec D 7(4):801-804", (1, 1, 1, 0, 0, 0), "full text opened (open PDF)", "DO/BOD/COD combination physically unusual"),
 ("L234", "Arya Alok P., Mohapatra S.S. (2018) Documentation of pollution status, ecological state and fishing activity in the lakes of Bangalore", "10.59415/ijfas.v7i4.129", 2018, "peer-reviewed", "Int J Fundamental & Applied Sciences 7(4):23-34", (0, 1, 1, 0, 0, 1), "full text opened (open PDF)", "only Table B (temp, pH, turbidity) loaded; Table A column order unreliable"),
 ("L287", "Naik P.R., Sankalpasri S.S., Bhavya B.S., Reshma T.V. (2019) Water quality assessment of Hebbal Lake in Bangalore city", "10.35940/ijitee.K1274.0981119", 2019, "peer-reviewed", "Int J Innov Technol Exploring Eng 8(11)", (0, 1, 1, 0, 0, 1), "full text opened (open PDF)", "sampling year not stated"),
 ("L291", "Rao S.M., Mogili N.V., Priscilla A., Lydia A. (2020) Aqueous chemistry of anthropogenically contaminated Bengaluru lakes", "10.1186/s42834-020-00049-5", 2020, "peer-reviewed", "Sustainable Environment Research 30:8", (1, 1, 1, 0, 1, 0), "full text opened (open access)", "four lakes pooled in Table 2"),
 ("L378", "Raju K., Ravi D.R., Hegde R.K. (2022) Water quality inspection and methodical remediation of Andrahalli Lake, Karnataka, India", "10.5281/zenodo.6805052", 2022, "peer-reviewed", "Int J Multidisciplinary Research and Modern Education 8(2):1-6", (1, 1, 1, 0, 0, 0), "full text opened (open PDF)", ""),
 ("L409", "Umadevi K.M., Kallimani S., Raikar S.P. (2024) Assessment of physiochemical, heavy metals, and biological characteristic of Bellandur Lake water bodies in Karnataka", "10.47062/1190.0604.03", 2024, "peer-reviewed", "Int J Environment and Health Sciences 6(4):65-69", (0, 0, 0, 0, 0, 1), "full text opened (open PDF)", "single sample, undated; text/table disagree"),
 ("L421", "Shashank A.S., Velayudhannair K. (2024) Comprehensive assessment of heavy metal pollution and ecological risk in lakes of Bangalore, Karnataka, India", "10.60151/envec/ZLAO4807", 2024, "peer-reviewed", "Environment and Ecology 42(2):479-491", (1, 1, 1, 1, 0, 0), "full text opened (open PDF)", "monthly rows partly scrambled in text layer: summary stats + Cd/Cu/Zn monthly only"),
 ("L445", "Venkata Ramaiah G., Ravindra P.K., Kallimani A.K. (2024) Water quality assessment of Byramangala Lake and its proximate ground water", "10.53555/ajbr.v27i4s.7554", 2024, "peer-reviewed", "African J Biomedical Research 27(4s):15074-15078", (0, 1, 0, 0, 0, 1), "full text opened (open PDF)", "peri-urban tank; undated"),
 ("L453", "Ravi Kumar K.R. et al. (2025) Assessment of water quality and pollution levels in Dorekere Lake, Bangalore", "10.55041/ijsrem46810", 2025, "peer-reviewed", "IJSREM 9(5)", (0, 1, 0, 0, 0, 1), "full text opened (open PDF)", "undated"),
 ("L462", "Moramchetty A. (2025) Evaluating the water quality of Ulsoor Lake, Bengaluru, between 2012 and 2023", "10.14445/23942568/IJAES-V12I4P102", 2025, "peer-reviewed", "SSRG Int J Agriculture & Environmental Science 12(4):9-16", (1, 1, 0, 0, 0, 0), "full text opened (open PDF)", "secondary compilation of CPCB NWMP; mixes annual means (2012-14) and min-max midranges (2015+)"),
 ("L492", "Ravi Kumar K.R., Spoorthi S. (2025) Assessment and management of Hebbal Lake, Bangalore: water quality, pollution, and restoration strategies", "10.12944/cwe.20.3.31", 2025, "peer-reviewed", "Current World Environment 20(3):1360-1366", (0, 1, 0, 0, 0, 0), "full text opened (open PDF)", "undated; n=49 summary only"),
 ("L514", "Narayanaswamy S.Y. (2026) Impact of urbanization on the physicochemical parameters of Varthur Lake in Bengaluru City, Karnataka, India", "10.5281/zenodo.18708732", 2026, "peer-reviewed", "Journal of Research and Development 18(2(VI)):182-185", (1, 1, 1, 0, 0, 1), "full text opened (open PDF)", "only rows with unambiguous alignment loaded"),
 ("DMG2011", "Bangalore Lakes Water Quality Results (2011): CSV of inlet/middle/outlet results for 87 lake names (DO, COD, TSS, nitrate, phosphate-P, chloride, hardness, fluoride, pH, metals, coliforms). OpenCity dataset 'Bengaluru Lakes - Water Quality Data' (publisher listed as Department of Mines and Geology)", "", 2011, "official-monitoring", "data.opencity.in (CKAN); licence field 'None'", (0, 1, 0, 0, 0, 1), "CSV opened and parsed", "units/method/month not stated; OCR-type errors possible"),
 ("BP2017", "Ramachandra T.V., Mahapatra D.M., Vinay S., Sincy V., Asulabha K.S., Bhat S., Aithal B.H. (2017) Bellandur and Varthur Lakes Rejuvenation Blueprint. ENVIS Technical Report 116, IISc", "", 2017, "grey-literature", "Energy and Wetlands Research Group, CES, IISc (via OpenCity)", (0, 1, 0, 0, 0, 0), "PDF opened; Table 3.1 only", "ranges synthesised from earlier studies"),
 ("KSPCB", "Karnataka State Pollution Control Board. Lakes Water Quality Report (monthly), July 2023 - November 2025 (28 files; Aug 2023 not parsed). Mirror: OpenCity 'Bengaluru Lake Monthly Water Quality Reports'", "", 2025, "official-monitoring", "KSPCB via data.opencity.in (CKAN) - licence 'Other (Public Domain)' per the dataset page", (1, 1, 0, 0, 0, 1), "28 PDFs opened; 27 parsed", "no methods in files; BOD basis not stated"),
 ("CPCB", "Central Pollution Control Board. National Water Quality Monitoring Programme (NWMP): Water quality of lakes, ponds and tanks, annual tables 2016-2024 (Karnataka section)", "", 2024, "official-monitoring", "cpcb.gov.in/wqm/<year>/Water_pond_tanks_<year>.pdf (2024 file name as listed on cpcb.gov.in)", (1, 1, 0, 0, 0, 1), "9 annual PDFs opened and parsed (pdfplumber); 2015 file not parsed; 2013-14 HTML Ulsoor rows hand-entered", "annual min/max per station; n per year not given in tables"),
]
st = pd.DataFrame([dict(record_id=a, citation=b, doi=c, year=d, source_type=e, venue=f, q_dates=g[0], q_sites=g[1], q_method=g[2], q_replicates=g[3], q_qaqc=g[4], q_raw=g[5], quality_score=sum(g), access=h, notes=i) for a, b, c, d, e, f, g, h, i in S])

# ------------------------------------------------------------------ lake key normalisation
from lakekey import lake_key, ALIAS
sys_path_added = True
# ------------------------------------------------------------------ harmonisation
def harmonise(param, value, unit):
    """returns (param_std, value_std, unit_std, note)"""
    u = str(unit)
    if value is None or (isinstance(value, float) and np.isnan(value)): return param, np.nan, u, ""
    if param in ("nitrate",) and "as NO3" in u: return "nitrate_N", value / 4.4268, "mg N/L", "converted from mg NO3/L (factor 4.4268)"
    if param == "nitrate": return "nitrate_unspecified_basis", value, "mg/L (basis unspecified)", "nitrate basis (as NO3 or as N) not stated: not converted"
    if param == "phosphate" and "as PO4" in u: return "phosphate_P", value * 0.3261, "mg P/L", "converted from mg PO4/L (factor 0.3261)"
    if param in ("phosphate", "orthophosphate"): return param + "_unspecified_basis", value, "mg/L (basis unspecified)", "phosphate basis (as PO4 or as P) not stated: not converted"
    if param == "EC":
        if u.lower().startswith("ms"): return "EC", value * 1000.0, "uS/cm", "mS assumed mS/cm; x1000"
        return "EC", value, "uS/cm", ""
    if param in ("total_coliform", "faecal_coliform"):
        if "CFU" in u.upper(): return param + "_CFU", value, "CFU/100mL", "CFU not comparable with MPN"
        return param + "_MPN", value, "MPN/100mL", ""
    if param == "BOD": return "BOD", value, "mg/L", "BOD incubation basis varies (3 d at 27 C in CPCB/KSPCB convention vs 5 d at 20 C elsewhere); official values assumed 3d/27C, others unspecified"
    return param, value, {"degC": "degC", "pH units": "pH units", "NTU": "NTU", "NTU (unit not printed)": "NTU"}.get(u, u if u.startswith("mg") or u.startswith("uS") else u), ""

FIELDS = ["record_id", "lake_key", "lake_as_reported", "site", "date_start", "date_end", "period_precision", "season", "parameter", "parameter_as_reported", "statistic", "value", "unit_as_reported",
          "parameter_std", "value_std", "unit_std", "harmonisation_note", "method", "n_samples", "page_table", "extraction_mode", "comparability_flag", "notes", "source_type", "analysis_use"]

rows = []
# ------------------------------------------------------------------ literature
for f in sorted(glob.glob(R + r"\data\raw\extraction\*.csv")):
    d = pd.read_csv(f, dtype=str).fillna("")
    for _, r in d.iterrows():
        rid = ("L%03d" % int(r.record_id)) if str(r.record_id).isdigit() else str(r.record_id)
        val = float(r.value) if r.value != "" else np.nan
        rows.append(dict(record_id=rid, lake_as_reported=r.lake, site=r.site, date_start=r.date_start, date_end=r.date_end, period_precision=r.period_precision, season=r.season, parameter=r.parameter,
                         parameter_as_reported=r.parameter_as_reported, statistic=r.statistic, value=val, unit_as_reported=r.unit_as_reported, method=r.method, n_samples=r.n_samples, page_table=r.page_table,
                         extraction_mode=r.extraction_mode, comparability_flag=r.comparability_flag, notes=r.notes, source_type={"DMG2011": "official-monitoring", "BP2017": "grey-literature"}.get(rid, "literature"), _canon=(r.notes.split("lake_key_guess=")[1] if "lake_key_guess=" in r.notes else np.nan)))
# ------------------------------------------------------------------ KSPCB monthly
k = pd.read_csv(R + r"\data\clean\official_kspcb_long_clean.csv")
k = k[k.lake_id.notna() & (k.lake_id != "")]
UK = {"temperature": "degC", "DO": "mg/L", "pH": "pH units", "EC": "uS/cm", "BOD": "mg/L", "nitrate_N": "mg/L as N", "nitrite_N": "mg/L as N", "faecal_coliform": "MPN/100mL", "total_coliform": "MPN/100mL", "turbidity": "NTU"}
for _, r in k.iterrows():
    ds = f"{int(r.year)}-{int(r.month):02d}-01"; de = (pd.Timestamp(ds) + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d")
    fl = []
    if isinstance(r.flag, str) and r.flag: fl.append(r.flag)
    if r.header_mode == "positional": fl.append("columns assigned by position (garbled PDF header)")
    if r.parameter in ("faecal_coliform", "total_coliform") and r.value == r.value and r.value > 1e8: fl.append("implausibly large coliform count as printed: verify")
    if r.water_body_type != "lake/tank": fl.append("river/reservoir station (outside lake scope)")
    rows.append(dict(record_id="KSPCB", lake_as_reported=r.lake_as_reported, site=f"STN {int(r.stn_filled)}", date_start=ds, date_end=de, period_precision="month", season="", parameter=r.parameter,
                     parameter_as_reported=r.header, statistic="single", value=r.value, unit_as_reported=UK.get(r.parameter, r.unit_std), method="KSPCB central laboratory (methods not stated in the monthly tables)", n_samples="1",
                     page_table=f"{r.source_file} p.{int(r.page)}", extraction_mode="table-parsed (pdfplumber)", comparability_flag="; ".join(fl), notes=f"kspcb_class_printed={r.kspcb_use_class}" if isinstance(r.kspcb_use_class, str) else "", source_type="official-monitoring",
                     _stn=int(r.stn_filled), _canon=r.lake_canonical))
# ------------------------------------------------------------------ CPCB NWMP 2016-2024 (wide -> long)
c = pd.read_csv(R + r"\data\clean\official_cpcb_nwmp_karnataka_lakes_wide.csv")
c = c[c.year != 2015].copy(); c["stn"] = pd.to_numeric(c.stn, errors="coerce")
g = pd.read_csv(R + r"\data\clean\lake_gazetteer_kspcb.csv")
kn = dict(zip(g.stn, g.name_kspcb))
qa = []
UC = {"temperature": "degC", "DO": "mg/L", "pH": "pH units", "EC": "uS/cm", "BOD": "mg/L", "nitrate_plus_nitrite_N": "mg/L", "faecal_coliform": "MPN/100mL", "total_coliform": "MPN/100mL"}
for _, r in c[c.stn.isin(g.stn)].iterrows():
    kname = kn[r.stn]; rn = str(r.name_reported) if isinstance(r.name_reported, str) else ""
    ta = set(w for w in lake_key(kname).split() if len(w) >= 5); tb = set(w for w in re.sub(r"[^a-z ]", " ", rn.lower()).split() if len(w) >= 5)
    sim = difflib.SequenceMatcher(None, lake_key(kname), lake_key(rn)).ratio() if rn else np.nan
    mism = bool(rn) and (sim < 0.6 and not (ta & tb) and not any(a[:6] in rn.lower() for a in ta))   # missing name (2020 layout) is not treated as a mismatch
    qa.append((int(r.year), int(r.stn), kname, rn, round(sim, 2) if sim == sim else None))
    for p, u in UC.items():
        for stat in ("min", "max"):
            v = r.get(f"{p}_{stat}")
            if v is None or (isinstance(v, float) and np.isnan(v)): continue
            fl = []
            if mism: fl.append("station name in CPCB row missing or differs from KSPCB name for this station code: check")
            if p in ("faecal_coliform", "total_coliform") and v > 1e8: fl.append("implausibly large coliform count as printed: verify")
            rows.append(dict(record_id="CPCB", lake_as_reported=rn or kname, site=f"STN {int(r.stn)}", date_start=f"{int(r.year)}-01-01", date_end=f"{int(r.year)}-12-31", period_precision="year", season="",
                             parameter=p, parameter_as_reported=p, statistic=stat, value=float(v), unit_as_reported=u, method="CPCB NWMP (state lab); methods not stated in table", n_samples="not stated",
                             page_table=f"{r.source_file} p.{int(r.page)}", extraction_mode="table-parsed (pdfplumber)", comparability_flag="; ".join(fl), notes="annual minimum/maximum over the year's monitoring", source_type="official-monitoring",
                             _stn=int(r.stn), _canon=(rn if (mism and rn) else kname), _mism=mism))
pd.DataFrame(qa, columns=["year", "stn", "name_kspcb", "name_cpcb_row", "similarity"]).to_csv(R + r"\data\release\qa_cpcb_station_name_check.csv", index=False)
# CPCB 2013/2014 (hand-entered from HTML pages, Ulsoor STN 1388 only): min, max, mean per parameter
H = {2013: [("temperature", 25, 32, 29.2), ("DO", 5.7, 8.6, 6.5), ("pH", 7, 10.2, 8.4), ("EC", 277, 1235, 504), ("BOD", 4, 43, 18.9), ("nitrate_plus_nitrite_N", 0.62, 13, 7.6), ("faecal_coliform", 4, 4, 4), ("total_coliform", 920, 1600, 1147)],
     2014: [("temperature", 28.0, 29.0, 28.5), ("DO", 5.7, 8.4, 7.2), ("pH", 7.0, 9.7, 8.4), ("EC", 308, 366, 339), ("BOD", 6.0, 16.0, 10.7), ("nitrate_plus_nitrite_N", 0.3, 7.3, 2.3), ("faecal_coliform", 46, 540, 293), ("total_coliform", 600, 1600, 1320)]}
for yr, L in H.items():
    for p, a, b, m in L:
        for stat, v in (("min", a), ("max", b), ("mean", m)):
            rows.append(dict(record_id="CPCB", lake_as_reported="ULSOOR LAKE TRAINING CENTRE OF FISH BREEDING", site="STN 1388", date_start=f"{yr}-01-01", date_end=f"{yr}-12-31", period_precision="year", season="", parameter=p,
                             parameter_as_reported=p, statistic=stat, value=float(v), unit_as_reported=UC[p], method="CPCB NWMP", n_samples="not stated", page_table=f"cpcb.gov.in/wqm/{yr}/LAKE, POND & TANK DATA {yr}_39.htm",
                             extraction_mode="hand-transcribed from HTML table (verified against paper L462 values)", comparability_flag="", notes="annual min/max/mean over the year", source_type="official-monitoring", _stn=1388, _canon="ulsoor lake temple", _mism=False))

df = pd.DataFrame(rows)
for col in ("_stn", "_canon", "_mism"):
    if col not in df: df[col] = np.nan
df["lake_key"] = np.where(df._canon.notna(), df._canon.map(lambda s: lake_key(s) if isinstance(s, str) else ""), df.lake_as_reported.map(lake_key))
# unify KSPCB canonical names with literature names
df["lake_key"] = df.lake_key.map(lambda s: lake_key(s))
hz = df.apply(lambda r: harmonise(r.parameter, r.value, r.unit_as_reported), axis=1, result_type="expand"); hz.columns = ["parameter_std", "value_std", "unit_std", "harmonisation_note"]
df = pd.concat([df, hz], axis=1)
# analysis use flags
def use(r):
    if r.source_type == "official-monitoring" and isinstance(r.comparability_flag, str) and "river/reservoir" in r.comparability_flag: return "exclude: not a lake"
    if r.record_id == "BP2017": return "exclude from trend/compliance (secondary synthesis; kept for coverage/provenance)"
    if r.record_id == "L462": return "exclude from trend/compliance (secondary duplicate of CPCB NWMP; kept for provenance)"
    if r.record_id == "L112": return "secondary (KSPCB 2008-10 via thesis); usable"
    if r.date_start == "" or pd.isna(r.date_start): return "usable for compliance/coverage; not for trends (undated)"
    return "usable"
df["analysis_use"] = df.apply(use, axis=1)
df["year"] = pd.to_datetime(df.date_start, errors="coerce").dt.year
df = df.merge(st[["record_id", "quality_score"]], on="record_id", how="left")
df = df.merge(st[["record_id"]].assign(_ok=1), on="record_id", how="left")
df = df[[c for c in FIELDS if c in df.columns] + ["year", "quality_score", "_stn"]].rename(columns={"_stn": "station_code"})
df.insert(0, "row_id", np.arange(1, len(df) + 1))
df.to_csv(R + r"\data\release\lake_measurements_long.csv", index=False, encoding="utf-8")
st.to_csv(R + r"\data\release\studies.csv", index=False, encoding="utf-8")
print(len(df), "rows;", df.record_id.nunique(), "sources;", df.lake_key.nunique(), "lake keys")
print(df.groupby("source_type").size())
