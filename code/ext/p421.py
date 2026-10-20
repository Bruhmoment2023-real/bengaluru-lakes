import sys, re; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex, nums
# P421 Shashank A.S., Velayudhannair K. (2024) Environment and Ecology 42(2):479-491, doi 10.60151/envec/ZLAO4807. Ulsoor and Agara lakes, Aug 2021-Jul 2022, 5 stations per lake.
x = Ex("421"); M = "AAS (Shimadzu AA6880) after mixed-acid digestion, APHA protocols (as stated); 5 stations per lake; +-values are SD"
for lake, k in (("Ulsoor Lake", 0), ("Agara Lake", 1)):
    for stat, ln in (("mean", 225), ("sd", 227)):
        v = nums(x.L[ln - 1])
        assert len(v) == 8, v
        P = [("temperature", "degC", v[0 + k]), ("turbidity", "NTU", v[2 + k]), ("EC", "uS/cm", v[4 + k]), ("pH", "pH units", v[6 + k])]
        for p, u, val in P: x.rec(lake, "5 stations pooled", "2021-08-01", "2022-07-31", "year", stat, {p: (val, u)}, ln, "Table 1, p.483", M, "5 stations x 12 months")
    rng = re.findall(r"\d+(?:\.\d+)?-\d+(?:\.\d+)?", x.L[228])   # line 229 (range)
    for (p, u), r in zip([("temperature", "degC"), ("temperature", "degC"), ("turbidity", "NTU"), ("turbidity", "NTU"), ("EC", "uS/cm"), ("EC", "uS/cm"), ("pH", "pH units"), ("pH", "pH units")], rng):
        pass
# range strings: Ulsoor/Agara order alternates; handled explicitly below
rng = re.findall(r"\d+(?:\.\d+)?-\d+(?:\.\d+)?", x.L[228]); assert len(rng) == 8, rng
names = [("temperature", "degC"), ("turbidity", "NTU"), ("EC", "uS/cm"), ("pH", "pH units")]
for j, (p, u) in enumerate(names):
    for k, lake in enumerate(("Ulsoor Lake", "Agara Lake")):
        lo, hi = map(float, rng[2 * j + k].split("-"))
        x.rec(lake, "5 stations pooled", "2021-08-01", "2022-07-31", "year", "min", {p: (lo, u)}, 229, "Table 1, p.483", M, "5 stations x 12 months")
        x.rec(lake, "5 stations pooled", "2021-08-01", "2022-07-31", "year", "max", {p: (hi, u)}, 229, "Table 1, p.483", M, "5 stations x 12 months")
# Table 1 continued: TDS and alkalinity means/ranges (rows 263,267); order TDS U, TDS A, [hardness blank], alk U, alk A
m = nums(x.L[262]); assert len(m) == 4, m
for lake, tds, alk in (("Ulsoor Lake", m[0], m[2]), ("Agara Lake", m[1], m[3])):
    x.rec(lake, "5 stations pooled", "2021-08-01", "2022-07-31", "year", "mean", {"TDS": (tds, "mg/L")}, 263, "Table 1 (continued), p.483-484", M, "5 stations x 12 months")
    x.rec(lake, "5 stations pooled", "2021-08-01", "2022-07-31", "year", "mean", {"total_alkalinity": (alk, "mg/L")}, 263, "Table 1 (continued), p.483-484", M, "5 stations x 12 months")
# Table 3 monthly Cd, Cu, Zn in water (mg/L), rows Aug-21..July-22 (lines 339-350)
mm = {"Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12, "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7}
import calendar
for i in range(338, 350):
    s = x.L[i]; lab = s.split()[0]; mon = mm[lab[:3]]; yr = 2021 if mon >= 8 else 2022
    toks = re.findall(r"BDL|\d+(?:\.\d+)?\ufffd\d+(?:\.\d+)?", s[len(lab):]); assert len(toks) == 6, (s, toks)
    for (metal, lake), t in zip([("cadmium", "Ulsoor Lake"), ("cadmium", "Agara Lake"), ("copper", "Ulsoor Lake"), ("copper", "Agara Lake"), ("zinc", "Ulsoor Lake"), ("zinc", "Agara Lake")], toks):
        ds, de = f"{yr}-{mon:02d}-01", f"{yr}-{mon:02d}-{calendar.monthrange(yr, mon)[1]}"
        if t == "BDL":
            x.add(lake=lake, site="5 stations pooled", date_start=ds, date_end=de, period_precision="month", parameter=metal, parameter_as_reported=metal, statistic="single", value="", unit_as_reported="mg/L",
                  method=M, page_table="Table 3, p.485", source_line=i + 1, comparability_flag="below_detection_limit (detection limit not stated)", n_samples="5 stations")
        else:
            v, sd = map(float, t.split("\ufffd"))
            x.rec(lake, "5 stations pooled", ds, de, "month", "mean", {metal: (v, "mg/L")}, i + 1, "Table 3, p.485", M, "5 stations")
            x.rec(lake, "5 stations pooled", ds, de, "month", "sd", {metal: (sd, "mg/L")}, i + 1, "Table 3, p.485", M, "5 stations")
print(x.save())
