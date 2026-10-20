import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P378 Raju K, Ravi DR, Hegde R (2022) Water quality inspection and methodical remediation of Andrahalli Lake, Karnataka. IJMRME 8(2):1-6. Seasonal values 2020 (winter, summer, monsoon, post-monsoon), one sampling station.
x = Ex("378"); M = "APHA guidelines (as stated); one sampling station; 2020 seasonal sampling"
SEAS = {"Winter": ("2020-01-01", "2020-02-29"), "Summer": ("2020-03-01", "2020-05-31"), "Monsoon": ("2020-06-01", "2020-09-30"), "Post Monsoon": ("2020-10-01", "2020-12-31")}
T = [("pH", "pH units", {"Winter": (6.95, 167), "Summer": (8.5, 169), "Monsoon": (6.75, 171), "Post Monsoon": (7.2, 173)}),
     ("BOD", "mg/L", {"Winter": (7, 201), "Summer": (18, 203), "Monsoon": (9.66, 205), "Post Monsoon": (7.66, 207)}),
     ("COD", "mg/L", {"Winter": (80.5, 243), "Summer": (204, 245), "Monsoon": (100.66, 246), "Post Monsoon": (81.33, 248)}),
     ("DO", "mg/L", {"Winter": (4.65, 274), "Summer": (4.1, 276), "Monsoon": (3.23, 278), "Post Monsoon": (4.96, 280)}),
     ("total_coliform", "MPN/100mL", {"Winter": (270000, 308), "Summer": (135000, 310), "Monsoon": (184866.66, 311), "Post Monsoon": (178000, 313)})]
for p, u, d in T:
    for s, (v, ln) in d.items():
        ds, de = SEAS[s]
        x.rec("Andrahalli Lake", "sample 1 (single station)", ds, de, "season (months approximate: 'winter, summer, monsoon, post monsoon of 2020' - exact dates not given)", "single", {p: (v, u)}, ln, "Tables 2-6",
              M, "not stated (seasonal value; some are averages e.g. 184866.66)", "season boundaries approximate (assumed Jan-Feb, Mar-May, Jun-Sep, Oct-Dec)", season=s, window=1)
print(x.save())
