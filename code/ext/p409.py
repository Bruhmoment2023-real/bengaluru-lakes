import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex
# P409 Umadevi K.M. et al. (2024) Assessment of physiochemical, heavy metals and biological characteristic of Bellandur Lake water bodies. (journal vol 6(4):65-69; doi 10.47062/1190.0604.03). Table 1 (PDF p.4), one sample; values read from word positions.
x = Ex("409"); FL = "single sample; sampling date/year not stated; text and table disagree on several values (e.g., lead 0.04-0.08 in text vs 0.12 in table; DO 5.2 vs 4.9); heavy-metal values (Cd 0.4, F 5.2 mg/L) unusually high - verify"
D = {"temperature": ("degC", 24.2), "pH": ("pH units", 7.56), "EC": ("uS/cm (unit not printed)", 1132), "turbidity": ("NTU (unit not printed)", 14.89), "total_hardness": ("mg/L", 235.4), "TDS": ("mg/L", 765), "DO": ("mg/L", 4.9),
     "COD": ("mg/L", 72.56), "BOD": ("mg/L", 25.42), "magnesium": ("mg/L", 29.32), "total_alkalinity": ("mg/L", 457.21), "calcium": ("mg/L", 53.98), "chloride": ("mg/L", 183.4), "sulphate": ("mg/L", 52.43),
     "phosphate": ("mg/L as PO4", 6.7), "nitrate": ("mg/L as NO3", 12.61), "fluoride": ("mg/L", 5.2), "lead": ("mg/L", 0.12), "cadmium": ("mg/L", 0.4), "iron": ("mg/L", 1.5), "copper": ("mg/L", 0.08), "chromium": ("mg/L", 0.03), "nickel": ("mg/L", 0.1)}
for p, (u, v) in D.items():
    x.rec_visual("Bellandur Lake", "single sample", "", "", "single survey (year not stated)", "single", {p: (v, u)}, "Table 1, PDF p.4", "BIS/APHA (as stated)", "1", FL, img="word-position read of 409.pdf p.4")
print(x.save())
