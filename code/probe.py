import sys; sys.path.insert(0, r"D:\Research-Publishing\13-bengaluru-lakes\code")
from common import get
s,t=get("https://api.openalex.org/works",{"search":"Bellandur lake water quality","per-page":2}); print("openalex",s,t[:300])
s,t=get("https://api.crossref.org/works",{"query.bibliographic":"Bellandur lake water quality","rows":2}); print("crossref",s,t[:200])
s,t=get("https://api.semanticscholar.org/graph/v1/paper/search",{"query":"Bellandur lake water quality","limit":2,"fields":"title,year"}); print("s2",s,t[:300])
s,t=get("https://doaj.org/api/search/articles/Bellandur%20lake",{"pageSize":2}); print("doaj",s,t[:300])
s,t=get("https://shodhganga.inflibnet.ac.in/simple-search",{"query":"Bangalore lake water quality"}); print("shodh",s,len(t),t[:200])
s,t=get("https://scholar.google.com/scholar",{"q":"Bellandur lake water quality"}); print("scholar",s,len(t),t[:200])
