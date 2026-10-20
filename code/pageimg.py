"""pageimg.py ID PAGE [RES] -> renders PDF page to E:\Research-Staging\13-bengaluru-lakes\img\ID_pPAGE.png (for visual verification of tables)"""
import sys, pdfplumber, os
rid, pg = sys.argv[1], int(sys.argv[2]); res = int(sys.argv[3]) if len(sys.argv) > 3 else 100
out = rf"E:\Research-Staging\13-bengaluru-lakes\img\{rid}_p{pg}.png"; os.makedirs(os.path.dirname(out), exist_ok=True)
with pdfplumber.open(rf"E:\Research-Staging\13-bengaluru-lakes\fulltext\{rid}.pdf") as p:
    p.pages[pg - 1].to_image(resolution=res).save(out)
print(out)
