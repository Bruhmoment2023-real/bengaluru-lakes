import sys, re; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex, nums
# P234 Arya Alok P., Mohapatra S.S. (2018) Documentation of pollution status, ecological state and fishing activity in the lakes of Bangalore. Int J Fund Appl Sci 7(4):23-34.
x = Ex("234")
NM = {"Chikkavanavara": "Chikkabanavara Lake", "Hoskere nallakarenalli": "Nallakadarenahalli Lake", "Hoskere nallakadarenahalli": "Nallakadarenahalli Lake", "Yellamallappa chetty": "Yellamallappa Chetty Lake", "Madivala": "Madiwala Lake",
      "Jakkur": "Jakkur Lake", "Begur doddakere": "Begur Lake", "Gottegere": "Gottigere Lake", "Hulimavu": "Hulimavu Lake", "Puttenahalli": "Puttenahalli Lake", "Puttenalli": "Puttenahalli Lake", "Sarakki": "Sarakki Lake",
      "Chandrapura": "Chandapura Lake", "Hebbagodi": "Hebbagodi Lake", "Rayasandra": "Rayasandra Lake"}
FL = "single survey; sampling date/year not stated; one grab sample 9-10:30 am; basis/method not detailed"
for i in range(237, 268):
    s = x.L[i].strip(); m = re.match(r"^(\d{1,2})\s+([A-Za-z ]+?)\s{2,}([\d.]+)\s+([\d.]+)\s+([\d.]+)$", s) or re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s{2,}([\d.]+)\s+([\d.]+)\s+([\d.]+)$", s)
    if not m: continue
    nm = NM[m.group(2).strip()]
    t, ph, tu = [float(m.group(k)) for k in (3, 4, 5)]
    for p, u, v in (("temperature", "degC", t), ("pH", "pH units", ph), ("turbidity", "NTU", tu)):
        x.rec(nm, "single sampling point", "", "", "single survey (date not stated)", "single", {p: (v, u)}, i + 1, "Table B, p.27", "single grab sample", "1", FL + ("; pH>10 implausible for lake water? reported as is" if p == "pH" and ph > 10 else ""), window=1)
print(x.save())
