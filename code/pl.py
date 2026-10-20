"""pl.py ID KEYWORD [maxlines] : print word-position-based lines of pages containing KEYWORD (case-insens.); or pl.py ID p:N"""
import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import pdf_lines
import pdfplumber, re
rid, kw = sys.argv[1], sys.argv[2]; mx = int(sys.argv[3]) if len(sys.argv) > 3 else 60
with pdfplumber.open(rf"E:\Research-Staging\13-bengaluru-lakes\fulltext\{rid}.pdf") as p:
    n = len(p.pages)
    pages = [int(kw[2:])] if kw.startswith("p:") else [i + 1 for i, pg in enumerate(p.pages) if kw.lower() in (pg.extract_text() or "").lower()]
print("pages:", pages, "of", n)
for pg in pages[:2]:
    print("=== page", pg)
    for k, (top, r) in enumerate(pdf_lines(rid, pg)):
        if k >= mx: print("..."); break
        print(int(top), " ".join(t for _, t in r)[:170])
