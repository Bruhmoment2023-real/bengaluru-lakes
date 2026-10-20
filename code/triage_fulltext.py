"""Convert downloaded full texts to text (pdftotext -layout; HTML stripped) in E: staging and score extractability.
Output data/clean/fulltext-triage.csv: id, kind, n_chars, scores for water-quality term counts and number-dense lines."""
import os, re, subprocess, pandas as pd, html
R = r"D:\Research-Publishing\13-bengaluru-lakes"
FT = r"E:\Research-Staging\13-bengaluru-lakes\fulltext"; TX = r"E:\Research-Staging\13-bengaluru-lakes\text"; os.makedirs(TX, exist_ok=True)
dec = pd.read_csv(R + r"\data\clean\screening-pool-decisions.csv").set_index("id")
rows = []
for f in sorted(os.listdir(FT)):
    rid, ext = f.rsplit(".", 1); out = f"{TX}\\{rid}.txt"
    if not os.path.exists(out):
        if ext == "pdf":
            subprocess.run(["pdftotext", "-layout", f"{FT}\\{f}", out], capture_output=True, timeout=120)
        else:
            t = open(f"{FT}\\{f}", encoding="utf-8", errors="replace").read()
            t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t); t = re.sub(r"(?s)<[^>]+>", "\n", t)
            open(out, "w", encoding="utf-8").write(html.unescape(re.sub(r"\n\s*\n+", "\n", t)))
    t = open(out, encoding="utf-8", errors="replace").read()
    nd = sum(1 for l in t.split("\n") if len(re.findall(r"\b\d+\.?\d*\b", l)) >= 4)
    wq = len(re.findall(r"\b(BOD|COD|DO|dissolved oxygen|nitrate|phosphate|pH|conductivity|turbidity|alkalinity|coliform|chloride)\b", t, re.I))
    rows.append(dict(id=int(rid), kind=ext, chars=len(t), numeric_lines=nd, wq_terms=wq, title=str(dec.loc[int(rid), "title"])[:90] if int(rid) in dec.index else ""))
df = pd.DataFrame(rows).sort_values("wq_terms", ascending=False); df.to_csv(R + r"\data\clean\fulltext-triage.csv", index=False)
print(len(df)); print(df.head(40).to_string())
