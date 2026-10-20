"""Main-path analysis (search path count, global main path by dynamic programming) on direct citations among corpus records that carry OpenAlex reference lists."""
import pandas as pd, numpy as np, networkx as nx, re, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = r"D:\Research-Publishing\13-bengaluru-lakes"; B = R + r"\bibliometrics"
raw = pd.read_csv(R + r"\data\raw\records-raw.csv", usecols=["id", "title", "year", "refs", "doi", "authors"]); raw = raw[raw.id.notna()].drop_duplicates("id")
c = pd.read_csv(B + r"\data\corpus.csv"); raw = raw[raw.title.str.lower().isin(set(c.title.str.lower()))].copy(); raw["year"] = pd.to_numeric(raw.year, errors="coerce")
info = raw.set_index("id")
G = nx.DiGraph()
for _, r in raw.iterrows():
    for ref in str(r.refs).split("|"):
        if ref in info.index and ref != r.id and info.loc[ref, "year"] <= r.year: G.add_edge(ref, r.id)   # knowledge flows cited -> citing
G.remove_nodes_from([n for n in list(G) if G.degree(n) == 0])
# break any residual cycles
while not nx.is_directed_acyclic_graph(G):
    cyc = nx.find_cycle(G); G.remove_edge(*cyc[-1])
order = list(nx.topological_sort(G)); src = [n for n in G if G.in_degree(n) == 0]; snk = [n for n in G if G.out_degree(n) == 0]
f = {n: 1 if n in src else 0 for n in order}
for n in order:
    if n not in src: f[n] = sum(f[p] for p in G.predecessors(n))
b = {n: 1 if n in snk else 0 for n in reversed(order)}
for n in reversed(order):
    if n not in snk: b[n] = sum(b[s] for s in G.successors(n))
for u, v in G.edges: G[u][v]["spc"] = f[u] * b[v]
best = {n: (0, None) for n in order}
for n in order:
    for p in G.predecessors(n):
        w = best[p][0] + G[p][n]["spc"]
        if w > best[n][0] or best[n][1] is None: best[n] = (w, p)
end = max(order, key=lambda n: best[n][0]); path = [end]
while best[path[-1]][1] is not None: path.append(best[path[-1]][1])
path = path[::-1]
rows = [dict(order=i + 1, year=int(info.loc[n, "year"]) if info.loc[n, "year"] == info.loc[n, "year"] else None, title=info.loc[n, "title"], doi=info.loc[n, "doi"], openalex_id=n) for i, n in enumerate(path)]
pd.DataFrame(rows).to_csv(B + r"\tables\main_path_papers.csv", index=False)
pd.DataFrame([dict(nodes=G.number_of_nodes(), edges=G.number_of_edges(), sources=len(src), sinks=len(snk), main_path_length=len(path), total_spc_on_path=best[end][0])]).to_csv(B + r"\tables\main_path_summary.csv", index=False)
fig, ax = plt.subplots(figsize=(9, 6)); ys = {n: info.loc[n, "year"] for n in G}; pos = {n: (ys[n] + np.random.RandomState(abs(hash(n)) % 2**31).uniform(-0.3, 0.3), np.random.RandomState(abs(hash(n[::-1])) % 2**31).uniform(0, 1)) for n in G}
nx.draw_networkx_edges(G, pos, alpha=0.15, arrows=False, ax=ax); nx.draw_networkx_nodes(G, pos, node_size=14, node_color="#bdbdbd", ax=ax)
pe = list(zip(path[:-1], path[1:])); nx.draw_networkx_edges(G, pos, edgelist=pe, edge_color="#e6550d", width=2, ax=ax, arrows=True, arrowsize=8); nx.draw_networkx_nodes(G, pos, nodelist=path, node_size=40, node_color="#e6550d", ax=ax)
ax.set_xlabel("Publication year"); ax.set_yticks([]); ax.spines[["left", "top", "right"]].set_visible(False); ax.set_title(f"Main path through the direct-citation network ({G.number_of_nodes()} papers, {G.number_of_edges()} citations; y jitter is arbitrary)")
fig.tight_layout(); fig.savefig(B + r"\figures\fig_main_path.png", dpi=220); plt.close(fig)
print(G.number_of_nodes(), G.number_of_edges(), len(path))
print(pd.DataFrame(rows)[["year", "title"]].to_string())
