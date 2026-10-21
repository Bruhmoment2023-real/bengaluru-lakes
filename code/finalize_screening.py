"""Assemble the full screening log (all de-duplicated records) and PRISMA counts + flow diagram."""
import pandas as pd, numpy as np, os, re
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = r"D:\Research-Publishing\13-bengaluru-lakes"
raw = pd.read_csv(R + r"\data\raw\records-raw.csv")
dd = pd.read_csv(R + r"\data\clean\records-dedup-flagged.csv")
pool = pd.read_csv(R + r"\data\clean\screen-pool.csv")[["id", "key"]]
dec = pd.read_csv(R + r"\data\clean\screening-pool-decisions-final.csv")  # first pass: screening-pool-decisions.csv; corrections from the check in data/checks/check-changelog.csv
tri = pd.read_csv(R + r"\data\clean\fulltext-triage.csv")
fl = pd.read_csv(R + r"\data\raw\fulltext-fetch-log.csv", header=None, names=["id", "title", "status", "url"], on_bad_lines="skip")
fl = fl[pd.to_numeric(fl.id, errors="coerce").notna()].copy(); fl["id"] = fl.id.astype(int)
EXTRACTED = {68: "L068", 47: "L047", 63: "L063", 112: "L112", 138: "L138", 147: "L147", 172: "L172", 175: "L175", 207: "L207", 234: "L234", 287: "L287", 291: "L291", 378: "L378", 409: "L409", 421: "L421", 445: "L445", 453: "L453", 462: "L462", 492: "L492", 514: "L514"}
EXC_FT = {403: "X1 not Bengaluru (Hebbal Lake at Krishnarajanagara, Mysuru district)",
          524: "X5 narrative review compiling values from other studies; no new measurements",
          290: "X8 data-quality exclusion: implausible repeated-digit values (e.g. DO 21.21 and 36.36 mg/L; Sn 24 ppm) in all three lakes",
          441: "X8 data-quality exclusion: pH reported as 16.00 +/- 27.71, 'humidity' listed as a water parameter, summer water temperature 42 C"}
LOWPRI = {350: "sampling year not stated (journal received the paper in March 2014); six-month summary table only, and the table rows are misaligned in the text layer, so it needs reading from the page image", 241: "alkali/alkaline-earth metals only in tables, time given as days after idol immersion, year not stated; heavy metals only in figures", 288: "same design as 241 (Yelahanka and Yediyur lakes)"}
# merge
m = dd.merge(pool, on="key", how="left").merge(dec[["id", "decision", "reason"]], on="id", how="left")
m["stage1_decision"] = np.where(m.decision == "full-text check", "retain for full-text check", "exclude")
m["stage1_reason"] = np.where(m.id.isna(), "pre-screen rule: no Bengaluru/lake name with water-quality terms in title/abstract/venue (X1/X2; metadata-only records judged by title)", m.reason.fillna(""))
m.loc[m.id.notna() & (m.decision == "full-text check"), "stage1_reason"] = ""
st = fl.set_index("id").status.to_dict(); tri_ids = set(tri.id)
tq = tri.set_index("id")
def stage2(r):
    if r.stage1_decision != "retain for full-text check": return "", ""
    i = int(r.id)
    if i in EXTRACTED: return "included - extracted to dataset", f"study {EXTRACTED[i]}"
    if i in EXC_FT: return "excluded at full text", EXC_FT[i]
    if i in LOWPRI: return "eligible - extraction queued (low priority)", LOWPRI[i]
    if i in tri_ids:
        t = tq.loc[i]
        if t.wq_terms >= 15 and t.numeric_lines >= 10: return "eligible - full text retrieved, extraction queued", f"triage positive (wq terms {int(t.wq_terms)}, numeric lines {int(t.numeric_lines)})"
        return "full text retrieved - no extractable numeric table found by automated triage", f"unverified by eye (wq terms {int(t.wq_terms)}, numeric lines {int(t.numeric_lines)}); may be figures-only, scan or landing page"
    s = st.get(i, "not attempted")
    return "X6 full text not obtained", f"fetch status: {s}"
m[["stage2_status", "stage2_reason"]] = m.apply(lambda r: pd.Series(stage2(r)), axis=1)
out = m[["key", "title", "year", "doi", "venue", "sources", "n_hits", "id", "stage1_decision", "stage1_reason", "stage2_status", "stage2_reason"]].rename(columns={"id": "pool_id"})
out.to_csv(R + r"\data\release\screening_log.csv", index=False, encoding="utf-8")
# counts
by_db = raw.groupby("source_db").size().to_dict()
C = {"records_identified_total": len(raw), "duplicates_removed": len(raw) - len(dd), "records_screened_title_abstract": len(dd),
     "excluded_prescreen_rule": int((m.id.isna()).sum()), "excluded_manual_title_abstract": int(((m.id.notna()) & (m.stage1_decision == "exclude")).sum()), "full_text_candidates": int((m.stage1_decision != "exclude").sum())}
s2 = m[m.stage1_decision == "retain for full-text check"].stage2_status.value_counts().to_dict()
C.update({"s2_" + k: v for k, v in s2.items()})
for k, v in by_db.items(): C["identified_" + k] = v
pd.Series(C).to_csv(R + r"\results\tables\prisma_counts.csv", header=["n"])
print(pd.Series(C).to_string())
# reasons x-codes at stage 1
r1 = m[(m.stage1_decision == "exclude")].stage1_reason.str.extract(r"^(X\d)")[0].fillna("pre-screen").value_counts()
r1.to_csv(R + r"\results\tables\prisma_stage1_reason_counts.csv", header=["n"]); print(r1)
# flow diagram
fig, ax = plt.subplots(figsize=(10, 9)); ax.axis("off")
def box(x, y, w, h, txt, fc="#eef3f8"):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec="#33475b", lw=1.2)); ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=9)
def arrow(x1, y1, x2, y2): ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color="#33475b"))
db = ", ".join(f"{k} {v}" for k, v in sorted(by_db.items()))
box(0.05, 0.86, 0.9, 0.11, f"Identification: {C['records_identified_total']} records from 6 databases\n({db})\n+ official monitoring series added separately (KSPCB monthly, CPCB NWMP)")
box(0.05, 0.70, 0.42, 0.10, f"After de-duplication (DOI, then title+year):\n{C['records_screened_title_abstract']} records screened")
box(0.55, 0.70, 0.40, 0.10, f"Duplicates removed: {C['duplicates_removed']}", "#f6f6f6")
box(0.05, 0.53, 0.42, 0.11, f"Stage 1 (title/abstract) retained: {C['full_text_candidates']}")
box(0.55, 0.53, 0.40, 0.11, f"Excluded at stage 1: {C['excluded_prescreen_rule'] + C['excluded_manual_title_abstract']}\n(rule pre-screen {C['excluded_prescreen_rule']}; manual {C['excluded_manual_title_abstract']})", "#f6f6f6")
got = sum(v for k, v in s2.items() if not k.startswith("X6"))
box(0.05, 0.36, 0.42, 0.11, f"Full text retrieved: {got}\nnot retrieved (X6): {s2.get('X6 full text not obtained', 0)}")
box(0.55, 0.36, 0.40, 0.11, f"Not obtained (X6): {s2.get('X6 full text not obtained', 0)}\n(paywall, dead repository, no open copy)", "#f6f6f6")
box(0.05, 0.10, 0.28, 0.20, f"Included, extracted:\n{s2.get('included - extracted to dataset', 0)} studies\n+ 2 official series", "#e3f2e1")
box(0.36, 0.10, 0.28, 0.20, f"Eligible, extraction queued:\n{s2.get('eligible - full text retrieved, extraction queued', 0) + s2.get('eligible - extraction queued (low priority)', 0)}\nTriage-negative (unverified): {s2.get('full text retrieved - no extractable numeric table found by automated triage', 0)}", "#fff6dc")
box(0.67, 0.10, 0.28, 0.20, f"Excluded at full text:\n{s2.get('excluded at full text', 0)} (X1, X5, 2x X8)", "#f6f6f6")
for a in ((0.5, 0.86, 0.26, 0.80), (0.26, 0.70, 0.26, 0.64), (0.47, 0.75, 0.55, 0.75), (0.47, 0.585, 0.55, 0.585), (0.26, 0.53, 0.26, 0.47), (0.47, 0.415, 0.55, 0.415), (0.26, 0.36, 0.19, 0.30), (0.26, 0.36, 0.50, 0.30), (0.26, 0.36, 0.80, 0.30)): arrow(*a)
ax.set_title("PRISMA-style flow (extraction not yet complete for the queued records)", fontsize=11)
os.makedirs(R + r"\results\figures", exist_ok=True)
fig.savefig(R + r"\results\figures\fig01_prisma_flow.png", dpi=200, bbox_inches="tight"); fig.savefig(R + r"\results\figures\fig01_prisma_flow.svg", bbox_inches="tight")
