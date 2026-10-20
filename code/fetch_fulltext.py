"""Download open-access full texts for records marked 'full-text check'. Polite (per-host throttle), no logins, no paywall evasion:
only the oa_url from OpenAlex / Google Scholar result link, plus citation_pdf_url meta tag on the landing page. Saves to E: staging. Resumable."""
import pandas as pd, os, re, time, requests, csv
from urllib.parse import urlparse, urljoin
R = r"D:\Research-Publishing\13-bengaluru-lakes"
OUT = r"E:\Research-Staging\13-bengaluru-lakes\fulltext"; os.makedirs(OUT, exist_ok=True)
d = pd.read_csv(R + r"\data\clean\screening-pool-decisions.csv"); d = d[d.decision == "full-text check"]
UA = "BengaluruLakesReview/1.0 (open-data systematic review)"
last = {}; log = []
def get(url):
    h = urlparse(url).netloc; w = last.get(h, 0) + 3 - time.time()
    if w > 0: time.sleep(w)
    try: r = requests.get(url, headers={"User-Agent": UA}, timeout=45, allow_redirects=True)
    except Exception as e: last[h] = time.time(); return None, str(e)[:80]
    last[h] = time.time(); return r, ""
done = {f.split(".")[0] for f in os.listdir(OUT)}
for _, r in d.iterrows():
    rid = str(int(r.id))
    if rid in done: continue
    urls = []
    if isinstance(r.oa_url, str) and r.oa_url.startswith("http"): urls.append(r.oa_url)
    status = "no_oa_url"
    for u in urls:
        resp, err = get(u)
        if resp is None: status = "error:" + err; continue
        ct = resp.headers.get("content-type", "")
        if resp.content[:4] == b"%PDF":
            open(f"{OUT}\\{rid}.pdf", "wb").write(resp.content); status = "pdf"; break
        if resp.status_code == 200 and "html" in ct:
            html = resp.text
            m = re.search(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)', html, re.I) or re.search(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', html, re.I)
            if m:
                pu = urljoin(resp.url, m.group(1)); r2, e2 = get(pu)
                if r2 is not None and r2.content[:4] == b"%PDF":
                    open(f"{OUT}\\{rid}.pdf", "wb").write(r2.content); status = "pdf_via_landing"; break
            open(f"{OUT}\\{rid}.html", "w", encoding="utf-8").write(html[:2000000]); status = "html_only"
        else: status = f"http{resp.status_code}"
    log.append((rid, r.title[:80], status, urls[0] if urls else ""))
    print(rid, status, flush=True)
    with open(R + r"\data\raw\fulltext-fetch-log.csv", "a", newline="", encoding="utf-8") as f: csv.writer(f).writerow(log[-1])
