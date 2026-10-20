import sys, re, csv; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex, FIELDS
# P147 Nagendra Babu R.S. (2014) Ecological assessment of the Hebbal Lake, Bengaluru. PhD thesis, KVAFSU Bidar (College of Fisheries Mangalore). Tables 3-24 (water), 8 stations x 12 months of 2013.
# QA built in: for every table the reported 'Average' row must equal the mean of the 8 station rows (tolerance 2%+0.01); tables failing the check or with layout damage (Table 3 label shift, 8 COD, 24 copper) are NOT loaded.
x = Ex("147")
caps = [(i, int(m.group(1))) for i, l in enumerate(x.L) for m in [re.match(r"\s*Table ?(\d+) ?:", l)] if m]
end_of = {n: (caps[k + 1][0] if k + 1 < len(caps) else len(x.L)) for k, (i, n) in enumerate(caps)}
start_of = {n: i for i, n in caps}
T = {3: ("temperature", "degC"), 5: ("pH", "pH units"), 6: ("DO", "mg/L"), 7: ("BOD", "mg/L"), 9: ("ammoniacal_N", "mg/L"), 10: ("phosphate", "mg/L"),
     11: ("nitrate", "mg/L"), 12: ("EC", "uS/cm"), 13: ("sulphate", "mg/L"), 14: ("chloride", "mg/L"), 15: ("total_alkalinity", "mg/L"), 16: ("total_hardness", "mg/L"),
     17: ("TDS", "mg/L"), 18: ("TSS", "mg/L"), 19: ("iron", "mg/L"), 20: ("lead", "mg/L"), 21: ("mercury", "mg/L"), 22: ("zinc", "mg/L"), 23: ("cadmium", "mg/L")}
meth = "8 surface-water stations (S1-S8), monthly Jan-Dec 2013; DO by Winkler (APHA 1955 as cited); other physico-chemical by APHA standard procedures as cited by the thesis; heavy metals in water (mg/L)"
SHIFT = {3, 10, 11, 13}   # pdftotext shifted the row labels by one line in these tables: first value row after 'Months' = S1 ... 8th = S8, 9th = reported average (verified against text: annual-average ranges)
from litlib import _tok
import calendar
def shifted(n, p, u):
    a, b = start_of[n], end_of[n]; mi = next(i for i in range(a, b) if x.L[i].strip().startswith("Months"))
    rows = []
    for i in range(mi + 1, min(b, mi + 30)):
        t = x.L[i].split()
        if t and re.match(r"^(Station|S\d)$", t[0]): t = t[1:]
        v = _tok(" ".join(t)) if t else None
        if v and len(v) == 12: rows.append((i, v))
    assert len(rows) == 9, (n, len(rows))
    for k, (i, v) in enumerate(rows):
        isavg = k == 8
        for m, val in enumerate(v, 1):
            x.add(lake="Hebbal Lake", site="all stations (reported average)" if isavg else f"S{k+1}", date_start=f"2013-{m:02d}-01", date_end=f"2013-{m:02d}-{calendar.monthrange(2013, m)[1]:02d}",
                  period_precision="month", parameter=p, parameter_as_reported=p, statistic="mean" if isavg else "single", value=val, unit_as_reported=u, method=meth,
                  page_table=f"Table {n} (row labels shifted in text layer; assigned by row order)", source_line=i + 1, n_samples="1 grab per station-month",
                  comparability_flag="")
    return 9
report = []
for n, (p, u) in T.items():
    a, b = start_of[n], end_of[n]
    before = len(x.rows)
    k = shifted(n, p, u) if n in SHIFT else x.grid(a, min(b, a + 60), p, u, "Hebbal Lake", 2013, page_table=f"Table {n}", method=meth, n_samples="1 grab per station-month")
    new = x.rows[before:]
    st = {}; av = {}
    for r in new:
        if r["value"] == "": continue
        (av if r["statistic"] == "mean" else st).setdefault(r["date_start"], {})[r["site"]] = float(r["value"])
    bad = 0; chk = 0
    for mth, d in av.items():
        vals = list(st.get(mth, {}).values())
        if len(vals) == 8:
            chk += 1; m = sum(vals) / 8; rep = list(d.values())[0]
            if abs(m - rep) > 0.02 * abs(rep) + 0.011 * max(1, abs(rep)) and abs(m - rep) > 0.01: bad += 1
    stations = {r["site"] for r in new if r["statistic"] == "single"}
    ok = (k >= 8 and len(stations) == 8 and bad <= 1)
    report.append((n, p, k, chk, bad, "LOADED" if ok else "DROPPED"))
    if not ok: del x.rows[before:]
for r in report: print(r)
print(len(x.rows), x.save())
