"""Counts-only summary of the CPCB station coverage (no station codes or values, which are not redistributed).

Reads derived_cpcb_annual_wide.csv (rebuilt with extract_cpcb.py / build_dataset.py) and writes
results/cpcb_station_counts.csv: stations and lakes per year, overall totals, and how many
of the 9 years 2016-2024 each station appears in. A station can map to more than one lake key across years.
Usage: python count_cpcb_stations.py [path/to/derived_cpcb_annual_wide.csv]
"""
import os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "release", "derived_cpcb_annual_wide.csv")
out = os.path.join(HERE, "..", "results", "cpcb_station_counts.csv")

d = pd.read_csv(src).dropna(subset=["station_code", "year"])
d["year"] = d["year"].astype(int)
years = sorted(d["year"].unique())

rows = []
for y in years:
    s = d[d["year"] == y]
    rows.append(dict(scope=str(y), stations=s["station_code"].nunique(), lakes=s["lake_key"].nunique(), station_years=len(s)))
rows.append(dict(scope=f"all years {years[0]}-{years[-1]} (distinct)", stations=d["station_code"].nunique(),
                 lakes=d["lake_key"].nunique(), station_years=len(d)))
# The annual PDF series runs 2016-2024; 2013 and 2014 come from a separate one-station HTML table.
m = d[d["year"].between(2016, 2024)]
per_station = m.groupby("station_code")["year"].nunique()
every = per_station[per_station == 9].index
rows.append(dict(scope="present in every year 2016-2024", stations=len(every),
                 lakes=m[m["station_code"].isin(every)]["lake_key"].nunique(), station_years=9 * len(every)))
for k, n in per_station.value_counts().sort_index().items():
    rows.append(dict(scope=f"present in {k} of the 9 years 2016-2024", stations=int(n), lakes="", station_years=int(n) * k))
pd.DataFrame(rows).to_csv(out, index=False)
print(pd.DataFrame(rows).to_string(index=False))
