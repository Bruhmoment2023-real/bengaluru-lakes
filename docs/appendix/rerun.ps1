# Rebuilds the Bengaluru lakes results from raw data in order. Usage: powershell -File rerun.ps1 [-Smoke] [-Full]
#  -Smoke (default): rebuilds dataset + analyses from the extracted files already on D: (about 5 minutes).
#  -Full: also re-parses KSPCB/CPCB PDFs (needs E:\Research-Staging\13-bengaluru-lakes\official\...) and re-runs per-paper extractors (needs staged full texts on E:). Searches are cached on E: (code\common.py); delete the cache to refetch.
param([switch]$Full)
$ErrorActionPreference = "Stop"
if (-not (Test-Path "D:\")) { throw "D: is missing - stop" }
$R = "D:\Research-Publishing\13-bengaluru-lakes"; $PY = "D:\Research-Publishing\_tools\biblio-venv\Scripts\python.exe"
function Run($s) { Write-Host "== $s"; & $PY -X utf8 -I "$R\$s"; if ($LASTEXITCODE -ne 0) { throw "failed: $s" } }
if ($Full) {
  Run "code\search.py"; Run "code\screen1.py"; Run "code\screen2.py"
  # fetch_fulltext.py (about 90 min, polite) and triage_fulltext.py are heavy: run them separately if the E: staging folders are empty
  Run "code\extract_kspcb.py"; Run "code\lakes_gazetteer.py"; Run "code\nominatim_fill.py"; Run "code\extract_cpcb.py"
  Get-ChildItem "$R\code\ext\p*.py" | ForEach-Object { Run ("code\ext\" + $_.Name) }
  Run "code\ext_dmg2011.py"; Run "code\ext_bp2017.py"
}
Run "code\build_dataset.py"; Run "code\build_lakes.py"; Run "code\finalize_screening.py"
Run "code\analysis_coverage.py"; Run "code\analysis_compliance_trends.py"; Run "code\literature_compliance.py"
Run "bibliometrics\python\bib_analysis.py"; Run "bibliometrics\python\main_path.py"
Write-Host "done: results in $R\results and $R\data\release"
