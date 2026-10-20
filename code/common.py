"""HTTP helper: on-disk cache in data/raw/cache, per-host throttle, descriptive UA, no personal identifiers."""
import hashlib, json, os, time, requests
ROOT = r"D:\Research-Publishing\13-bengaluru-lakes"
CACHE = "E:/Research-Staging/13-bengaluru-lakes/cache"
os.makedirs(CACHE, exist_ok=True)
UA = "BengaluruLakesReview/1.0 (open-data systematic review; contact via project folder)"
INTERVAL = {"api.openalex.org": 1.0, "api.crossref.org": 0.5, "api.semanticscholar.org": 3.0,
            "doaj.org": 1.0, "shodhganga.inflibnet.ac.in": 3.0, "scholar.google.com": 10.0}
_last = {}
LOG = os.path.join(ROOT, "data", "raw", "http-log.csv")

def get(url, params=None, binary=False, tries=3, timeout=60, headers=None):
    from urllib.parse import urlparse, urlencode
    full = url + (("?" + urlencode(params)) if params else "")
    key = hashlib.sha1(full.encode()).hexdigest()
    path = os.path.join(CACHE, key + (".bin" if binary else ".txt"))
    if os.path.exists(path):
        with open(path, "rb") as f:
            b = f.read()
        return 200, (b if binary else b.decode("utf-8", "replace"))
    host = urlparse(url).netloc
    for t in range(tries):
        w = _last.get(host, 0) + INTERVAL.get(host, 1.0) - time.time()
        if w > 0: time.sleep(w)
        try:
            h = {"User-Agent": UA}; h.update(headers or {})
            r = requests.get(full, headers=h, timeout=timeout)
        except Exception as e:
            _last[host] = time.time(); status, body = -1, str(e).encode()
            time.sleep(2 * (t + 1)); continue
        _last[host] = time.time()
        status, body = r.status_code, r.content
        if status in (429, 503):
            time.sleep(15 * (t + 1)); continue
        break
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')},{status},\"{full[:300]}\"\n")
    if status == 200:
        with open(path, "wb") as f: f.write(body)
    return status, (body if binary else body.decode("utf-8", "replace"))
