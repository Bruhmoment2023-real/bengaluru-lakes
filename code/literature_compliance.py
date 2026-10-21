"""Table t12: share of literature values failing the CPCB class-C criteria (DO < 4 mg/L, BOD > 3 mg/L, pH outside 6.5-8.5),
all studies and studies with quality score >= 3. Uses single, mean and median values from the published studies and drops
rows marked as secondary duplicates of CPCB NWMP. (The first version of this table was made interactively on 17 Oct 2026;
this script reproduces it exactly from the first-pass data and was added on 22 Oct 2026 to re-run it after the author check.)"""
import pandas as pd
R = r"D:\Research-Publishing\13-bengaluru-lakes"
d = pd.read_csv(R + r"\data\release\lake_measurements_long.csv", low_memory=False)
lit = d[(d.source_type == "literature") & d.statistic.isin(["single", "mean", "median"])
        & (d.analysis_use != "exclude from trend/compliance (secondary duplicate of CPCB NWMP; kept for provenance)")].copy()
lit["v"] = pd.to_numeric(lit.value_std, errors="coerce"); lit = lit[lit.v.notna()]
fail = {"DO": lambda v: v < 4, "BOD": lambda v: v > 3, "pH": lambda v: (v < 6.5) | (v > 8.5)}
rows = []
for sub, x in [("all", lit), ("score>=3", lit[lit.quality_score >= 3])]:
    for p, f in fail.items():
        y = x[x.parameter_std == p]; rows.append(dict(subset=sub, parameter=p, n_values=len(y), share_failing=round(f(y.v).mean(), 3)))
out = pd.DataFrame(rows); out.to_csv(R + r"\results\tables\t12_literature_compliance_sensitivity.csv", index=False); print(out.to_string())
