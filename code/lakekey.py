"""Lake-name normalisation shared by the build scripts."""
import re
ALIAS = {"madivala": "madiwala", "madavara": "madavara", "madhavara": "madavara", "malathalli": "mallathahalli", "mallathalli": "mallathahalli", "malathahalli": "mallathahalli", "mallathahalli": "mallathahalli",
         "gottegere": "gottigere", "yelhanka": "yelahanka", "yadiyur": "yediyur", "sanky": "sankey", "bellaur": "bellandur", "tubrahalli": "thubarahalli", "tubarahalli": "thubarahalli", "yelemallappa shetty": "yellamallappa chetty",
         "yellemallappa": "yellamallappa chetty", "yellamallappa chetty": "yellamallappa chetty", "yellamallappa": "yellamallappa chetty", "elemallappa shetty": "yellamallappa chetty", "agaram": "agara", "chandapura": "chandapura",
         "chikkavanavara": "chikkabanavara", "kaikondanahalli": "kaikondrahalli", "kaikoanahalli": "kaikondrahalli", "doddanekkundi": "doddanekundi", "dhorekere": "dorekere", "dore": "dorekere", "haralakuntte": "haralakunte",
         "andhrahalli": "andrahalli", "andrahalli": "andrahalli", "nagavara": "nagawara", "nagawara": "nagawara", "begur": "begur", "hosakerehalli": "hosakerehalli", "karihobanahalli": "karihobanahalli", "hesaraghatta": "hesaraghatta"}
def lake_key(name):
    s = str(name).lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z ]", " ", s)
    s = re.sub(r"\b(lake|tank|kere|kunte|cheruvu|reservoir|pond|bengaluru|bangalore|bengalore)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    for k in ("ulsoor", "halasuru"):
        if s.startswith(k): return "ulsoor"
    for k in sorted(ALIAS, key=len, reverse=True):
        if s == k or s.startswith(k + " "): return ALIAS[k]
    return s

