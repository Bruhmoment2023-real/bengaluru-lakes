"""Print a condensed view of a staged full text: first lines, sampling sentences, 'Table' captions and numeric table-like lines. Usage: tabs.py ID [maxlines]"""
import sys, re
rid = sys.argv[1]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 220
t = open(rf"E:\Research-Staging\13-bengaluru-lakes\text\{rid}.txt", encoding="utf-8", errors="replace").read().replace("\x0c", "\n")
L = [l.rstrip() for l in t.split("\n")]
print("== chars", len(t), "lines", len(L))
head = [l for l in L if l.strip()][:14]
print("\n".join(x[:170] for x in head)); print("-- sampling/method sentences")
n = 0
for i, l in enumerate(L):
    if re.search(r"(sampl|collected|monthly|fortnight|season|during the period|from .* (to|and) .*(19|20)\d\d)", l, re.I) and re.search(r"(19|20)\d\d|month|season|station|site", l, re.I):
        print("  ", l.strip()[:170]); n += 1
        if n >= 14: break
print("-- tables / numeric lines")
n = 0
for i, l in enumerate(L):
    if re.match(r"\s*(table|tab\.)\s*\.?\s*\d", l, re.I) or len(re.findall(r"(?<![A-Za-z])\d+\.?\d*(?![A-Za-z])", l)) >= 4:
        print(f"{i:5d} {l.strip()[:200]}"); n += 1
        if n >= mx: print("   ...truncated"); break
