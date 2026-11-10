from tu import *
import heapq, math, itertools
from collections import deque
from visualizador import grafos_avancados as GA
from visualizador.base import chave
random.seed(11)
c = GA.GrafosAvancados(app)
nomes = [a[0] for a in c.algoritmos]
def sel(prefixo): 
    i = [k for k, n in enumerate(nomes) if n.startswith(prefixo)][0]; c.selecionar(i); return rodar(c)
def reach(n, adj):
    R = []
    for s in range(n):
        vis = {s}; q = deque([s])
        while q:
            u = q.popleft()
            for v, _ in adj[u]:
                if v not in vis: vis.add(v); q.append(v)
        R.append(vis)
    return R
def comps(n, edges, remover_v=None, remover_e=None):
    adj = {i: [] for i in range(n)}
    for u, v, _ in edges:
        if remover_e and chave(u, v) == remover_e: continue
        if remover_v is not None and remover_v in (u, v): continue
        adj[u].append((v, 1)); adj[v].append((u, 1))
    vis = set(); k = 0
    for s in range(n):
        if s == remover_v or s in vis: continue
        k += 1; q = deque([s]); vis.add(s)
        while q:
            u = q.popleft()
            for v, _ in adj[u]:
                if v not in vis: vis.add(v); q.append(v)
    return k

# Floyd-Warshall
ok = True
for _ in range(15):
    sel("Floyd")
    ref = []
    for s in range(c.n):
        d = {s: 0}; h = [(0, s)]
        while h:
            x, u = heapq.heappop(h)
            if x > d[u]: continue
            for v, w in c.adj[u]:
                if x + w < d.get(v, 1e9): d[v] = x + w; heapq.heappush(h, (x + w, v))
        ref.append([d[j] for j in range(c.n)])
    ok = ok and c.matriz == ref
checar("Floyd-Warshall = Dijkstra de cada nó (15 grafos)", ok)
foto("s_floyd")

# Topológica
for nome in ("Ordenação topológica: Kahn", "Ordenação topológica: DFS"):
    ok = True
    for _ in range(20):
        sel(nome); pos_ = {u: i for i, u in enumerate(c.lista)}
        ok = ok and len(c.lista) == c.n and all(pos_[u] < pos_[v] for u, v, _ in c.arestas)
    checar(f"{nome}: ordem respeita todas as arestas (20 DAGs)", ok)
foto("s_topo")

# SCC
for nome in ("Componentes fortemente conexas: Tarjan", "Componentes fortemente conexas: Kosaraju"):
    ok = True
    for _ in range(20):
        sel(nome); R = reach(c.n, c.adj)
        ref = {frozenset(j for j in range(c.n) if i in R[j] and j in R[i]) for i in range(c.n)}
        got = {}
        for no, k in c.comp.items(): got.setdefault(k, set()).add(no)
        ok = ok and ref == {frozenset(v) for v in got.values()} and len(c.comp) == c.n
    checar(f"{nome}: partição = alcançabilidade mútua (20 dígrafos)", ok)
foto("s_scc")

# Pontes / articulações
ok = True; tot = 0
for _ in range(25):
    sel("Pontes"); base_k = comps(c.n, c.arestas)
    pontes_ref = {chave(u, v) for u, v, _ in c.arestas if comps(c.n, c.arestas, remover_e=chave(u, v)) > base_k}
    arts_ref = {v for v in range(c.n) if comps(c.n, c.arestas, remover_v=v) > base_k}
    ok = ok and set(c.pontes) == pontes_ref and c.arts == arts_ref; tot += len(pontes_ref)
checar("Pontes e articulações = remoção por força bruta (25 grafos)", ok, f"{tot} pontes no total")
foto("s_pontes")

# Euler
ok = True
for _ in range(20):
    sel("Ciclo euleriano"); cir = c.circuito
    usadas = sorted(chave(a, b) for a, b in zip(cir, cir[1:]))
    ok = ok and usadas == sorted(chave(u, v) for u, v, _ in c.arestas) and cir[0] == cir[-1] == 0
checar("Euler: ciclo usa cada aresta exatamente uma vez (20 grafos)", ok)

# Fluxo máximo
def mincut(g):
    n, s, t = g.n, g.origem, g.destino; melhor = math.inf
    outros = [i for i in range(n) if i not in (s, t)]
    for r in range(len(outros) + 1):
        for S in itertools.combinations(outros, r):
            S = set(S) | {s}
            melhor = min(melhor, sum(w for u, v, w in g.arestas if u in S and v not in S))
    return melhor
for nome in ("Fluxo máximo: Edmonds-Karp (BFS)", "Fluxo máximo: Ford-Fulkerson (DFS)"):
    ok = True
    for _ in range(20):
        sel(nome); ok = ok and c.fluxo == mincut(c)
    checar(f"{nome}: fluxo = corte mínimo (20 redes)", ok, c.info)
foto("s_fluxo")

# Emparelhamento
def maxmatch(g):
    best = 0
    for r in range(len(g.esq) + 1):
        for sub in itertools.combinations(g.arestas, r):
            L = [u for u, v, _ in sub]; R_ = [v for u, v, _ in sub]
            if len(set(L)) == r and len(set(R_)) == r: best = max(best, r)
    return best
ok = True
for _ in range(20):
    sel("Emparelhamento"); verdes = sum(1 for v in c.cor_aresta.values() if v == base.VERDE)
    ok = ok and len(c.par) == maxmatch(c) == verdes
checar("Emparelhamento (Kuhn) = máximo por força bruta (20 grafos)", ok)
foto("s_kuhn")
# N gera outro grafo
c.selecionar(0); tecla(c, pygame.K_n); c.desenhar(tela)
fim()
