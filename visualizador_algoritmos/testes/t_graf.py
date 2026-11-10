from tu import *
import heapq, math, itertools
from visualizador import grafos as G
random.seed(3)
def dref(c, s):
    d = {s: 0}; h = [(0, s)]
    while h:
        x, u = heapq.heappop(h)
        if x > d[u]: continue
        for v, w in c.adj[u]:
            if x + w < d.get(v, 1e9): d[v] = x + w; heapq.heappush(h, (x + w, v))
    return d
c = G.Grafos(app)
ok = True
for t in range(25):
    c.reiniciar()
    ref = dref(c, c.origem)[c.destino]
    res = []
    for nome in ("Dijkstra", "A*", "Bellman-Ford"):
        i = [a[0] for a in c.algoritmos].index(nome); c.selecionar(i); rodar(c); res.append(c.info)
    ok = ok and all(f"distância {ref})" in r for r in res)
checar("Dijkstra / A* / Bellman-Ford = referência (25 grafos)", ok)
ok = True
for t in range(15):
    c.reiniciar(); pesos = []
    for nome in ("Prim", "Kruskal", "Borůvka"):
        i = [k for k, a in enumerate(c.algoritmos) if a[0].startswith(nome)][0]; c.selecionar(i); rodar(c)
        import re; pesos.append(int(re.findall(r"\d+", c.info)[-1]))
        n_verdes = sum(1 for v in c.cor_aresta.values() if v == base.VERDE)
        ok = ok and n_verdes == c.n - 1
    ok = ok and len(set(pesos)) == 1
checar("Prim = Kruskal = Borůvka, e n-1 arestas (15 grafos)", ok, pesos)
for nome in ("BFS", "DFS"):
    i = [k for k, a in enumerate(c.algoritmos) if a[0].startswith(nome)][0]; c.selecionar(i); checar(f"{nome}: " + c.info if rodar(c) else nome, "Caminho" in c.info)
ok = True
for t in range(10):
    c.reiniciar()
    gul = [k for k, a in enumerate(c.algoritmos) if a[0] == "Coloração gulosa"][0]; c.selecionar(gul); rodar(c)
    ok = ok and all(c.cor_no[u] != c.cor_no[v] for u, v, _ in c.arestas)
    ng = len(set(c.cor_no.values()))
    bt = [k for k, a in enumerate(c.algoritmos) if a[0].startswith("Coloração ótima")][0]; c.selecionar(bt); rodar(c)
    nb = len(set(c.cor_no.values()))
    ok = ok and all(c.cor_no[u] != c.cor_no[v] for u, v, _ in c.arestas) and nb <= ng
    # minimalidade: nenhuma coloração com nb-1 cores (força bruta)
    if nb > 1 and c.n <= 12:
        poss = False
        for cor in itertools.product(range(nb - 1), repeat=c.n):
            if all(cor[u] != cor[v] for u, v, _ in c.arestas): poss = True; break
        ok = ok and not poss
checar("Coloração: gulosa válida; backtracking válida e ótima (10 grafos)", ok)
c.reiniciar(); c.selecionar(2); c.vel = 4
for _ in range(80): c.atualizar()
c.desenhar(tela); foto("s_grafo")
fim()
