import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P453 Ravi Kumar K.R. et al. (2025) Assessment of water quality and pollution levels in Dorekere Lake, Bangalore. IJSREM 9(5). Table 1 (PDF p.7), four in-lake sampling locations (E, S, W, N sides); values read from PDF word positions; sampling date not stated.
x = Ex("453"); FL = "sampling date/year not stated: cannot be placed on a timeline"; M = "grab samples at 4 in-lake locations; IS 10500-style reporting; methods not detailed"
SITES = ["Lake water 1 (eastern side)", "Lake water 2 (southern side)", "Lake water 3 (western side)", "Lake water 4 (northern side)"]
D = {"pH": ("pH units", [7.66, 7.8, 8.2, 7.9]), "BOD": ("mg/L (3 days at 27 C)", [5.2, 6.4, 5.7, 6.4]), "nitrate": ("mg/L as NO3", [14, 15.3, 14.8, 17.2]), "sulphate": ("mg/L as SO4", [13.9, 15.6, 15.4, 15.5]),
     "phosphate": ("mg/L as PO4", [0.4, 0.5, 0.4, 0.3]), "fluoride": ("mg/L", [0.48, 0.58, 0.52, 0.48]), "EC": ("uS/cm", [545, 536, 534, 545]), "DO": ("mg/L", [6.4, 6.2, 6.2, 7.8]),
     "total_coliform": ("per 100 mL (method/unit as reported; MPN vs CFU not stated)", [210, 920, 180, 240])}
for p, (u, vs) in D.items():
    for s, v in zip(SITES, vs):
        x.rec_visual("Dorekere Lake", s, "", "", "single survey (year not stated)", "single", {p: (v, u)}, "Table 1, PDF p.7", M, "1", FL, img="word-position read of 453.pdf p.7")
for p, lim, vals in (("free_ammonia_N", 0.05, None), ("boron", 0.1, None), ("lead", 0.01, None), ("copper", 0.02, None), ("cadmium", 0.003, None)):
    for s in SITES:
        x.rec_visual("Dorekere Lake", s, "", "", "single survey (year not stated)", "single", {p: (lim, "mg/L")}, "Table 1, PDF p.7", M, "1", FL + f"; reported '<{lim}' (censored; value = reporting limit)", img="word-position read of 453.pdf p.7")
for s, v in zip(SITES, [None, 0.42, None, 0.07]):
    if v: x.rec_visual("Dorekere Lake", s, "", "", "single survey (year not stated)", "single", {"zinc": (v, "mg/L")}, "Table 1, PDF p.7", M, "1", FL, img="word-position read of 453.pdf p.7")
    else: x.rec_visual("Dorekere Lake", s, "", "", "single survey (year not stated)", "single", {"zinc": (0.05, "mg/L")}, "Table 1, PDF p.7", M, "1", FL + "; reported '<0.05' (censored)", img="word-position read of 453.pdf p.7")
print(x.save())
