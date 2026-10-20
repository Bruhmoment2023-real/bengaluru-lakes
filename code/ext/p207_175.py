import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P207 Alimuddin (2017) J Chem Biol Phys Sci Sec D 7(4):801-804, doi 10.24214/jcbps.D.7.4.80104. Ulsoor Lake, March 2011-Feb 2012, one mid-lake point; Table 1 ranges.
x = Ex("207"); M = "APHA methods; DO Winkler; one sampling point mid-lake, sampled once per sampling day (frequency not stated)"
R = [(79, "temperature", "degC", 18.5, 27.6), (81, "pH", "pH units", 7.12, 9.80), (82, "DO", "mg/L", 10.2, 13.7), (84, "BOD", "mg/L", 19.8, 29.5), (85, "COD", "mg/L", 160.4, 249.2), (86, "EC", "umho/cm", 618, 627),
     (87, "total_alkalinity", "mg/L", 362, 612), (89, "total_hardness", "mg/L", 198, 1900), (90, "TDS", "mg/L", 375, 590), (91, "chloride", "mg/L", 77.4, 81.7), (92, "sulphate", "mg/L", 30.5, 48.3),
     (93, "phosphate", "mg/L", 2.0, 2.5), (94, "nitrate", "mg/L", 0.5, 9.4)]
for ln, p, u, lo, hi in R:
    fl = "range only (no mean); DO 10.2-13.7 mg/L with BOD 19.8-29.5 and COD 160-249 mg/L is physically unusual (possible supersaturation/algal bloom or reporting error): treat with caution" if p in ("DO", "BOD", "COD") else "range only (no mean)"
    for stat, val in (("min", lo), ("max", hi)):
        x.rec("Ulsoor Lake", "mid-lake point", "2011-03-01", "2012-02-29", "period (Mar 2011-Feb 2012)", stat, {p: (val, u)}, ln, "Table 1, p.802", M, "not stated", fl)
print(x.save())
y = Ex("175")
# P175 Upadhyay A., Chandrakala M. (2015) IJIRSET 4(5):2827-2832?, doi 10.15680/IJIRSET.2015.0405025. Ulsoor Lake, S1 pre-monsoon and S2 post-monsoon; year not stated.
RR = [(164, "pH", "pH units", 7.9, 7.6), (166, "EC", "uS/cm", 360, 320), (168, "TDS", "mg/L", 334, 308), (170, "total_hardness", "mg/L", 55, 202), (176, "calcium", "mg/L", 34, 90), (178, "magnesium", "mg/L", 21, 112), (180, "total_alkalinity", "mg/L", 180, 200)]
for ln, p, u, a, b in RR:
    for s, val in (("S1 (pre-monsoon)", a), ("S2 (post-monsoon)", b)):
        y.rec("Ulsoor Lake", s, "", "", "season (year not stated)", "single", {p: (val, u)}, ln, "Table II", "EDTA titration/conductometry/pH meter (Table I of paper); one grab sample per season", "1",
              "sampling year not reported: cannot be placed on a timeline", season="pre-monsoon" if s.startswith("S1") else "post-monsoon", window=1)
print(y.save())
