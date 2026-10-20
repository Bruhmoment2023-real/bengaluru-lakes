import sys, re; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from litlib import Ex, pdf_lines
# P112 Lekhashree S.M. (2013) MSc thesis, UAS GKVK Bangalore: KSPCB data for 16 lakes 2008-2010; Tables 1-16 on PDF pages 77-92 (read from word positions).
x = Ex("112")
PAR = [("pH", "pH units"), ("DO", "mg/L"), ("BOD", "mg/L"), ("EC", "umho/cm"), ("TDS", "mg/L"), ("TSS", "mg/L"), ("lead", "mg/L"), ("copper", "mg/L"), ("zinc", "mg/L"), ("iron", "mg/L")]
NAMES = {"Sanky tank": "Sankey Tank", "Yadiyur Lake": "Yediyur Lake", "Yalahanka Lake": "Yelahanka Lake", "Yellemallappa Lake": "Yellamallappa Chetty Lake", "Haralakuntte Lake": "Haralakunte Lake"}
tot = 0
for page in range(77, 93):
    L = pdf_lines("112", page)
    title = next(" ".join(t for _, t in r) for _, r in L if "Descriptive statistics for water quality parameters of" in " ".join(t for _, t in r))
    lake = NAMES.get(title.split("parameters of")[-1].strip(), title.split("parameters of")[-1].strip())
    tn = re.search(r"Table\s*(\d+)", title).group(1)
    yl = []
    for top, r in L:
        toks = [t for _, t in r]
        j = next((i for i, t in enumerate(toks) if t in ("2008", "2009", "2010")), None)
        if j is None or j > 4: continue
        nums = [t for t in toks[j + 1:] if re.fullmatch(r"-?\d+(?:\.\d+)?", t)]
        if len(nums) >= 7: yl.append((int(toks[j]), [float(v) for v in nums[:7]], top))
        elif len(toks) - j >= 7: yl.append((int(toks[j]), None, top)); print('  malformed row skipped:', lake, ' '.join(toks))
    assert len(yl) == 30, (lake, len(yl))
    for b in range(10):
        blk = yl[3 * b: 3 * b + 3]; assert [y for y, _, _ in blk] == [2008, 2009, 2010], (lake, b, blk)
        p, u = PAR[b]
        for yr, v, top in blk:
            if v is None: continue
            for stat, val in zip(("mean", "min", "max", "sd"), v[:4]):
                x.add(lake=lake, site="composite of 5 samples (as stated)", date_start=f"{yr}-01-01", date_end=f"{yr}-12-31", period_precision="year", parameter=p, parameter_as_reported=p, statistic=stat, value=val,
                      unit_as_reported=u, method="KSPCB central laboratory, standard methods (as stated)", n_samples="5", page_table=f"Table {tn}, PDF p.{page}", extraction_mode="table-parsed (PDF word positions)",
                      comparability_flag="secondary: KSPCB data as reproduced in an MSc thesis; heavy-metal values of 0.01 mg/L likely at the reporting limit" if p in ("lead", "copper", "zinc", "iron") else "secondary: KSPCB data as reproduced in an MSc thesis")
            tot += 1
print(tot, x.save())
