from tu import *
import heapq, math
from collections import deque
from visualizador import grade as GR
random.seed(21)
c = GR.Grade(app)
nomes = [a[0] for a in c.algoritmos]
def sel(prefixo):
    i = [k for k, n in enumerate(nomes) if n.startswith(prefixo)][0]; c.selecionar(i); return rodar(c)
def livres(c): return {(r, k) for r in range(c.LINS) for k in range(c.COLS) if c.grade[r][k] == 0}
def componente(c, s):
    vis = {s}; q = deque([s])
    while q:
        u = q.popleft()
        for v in c.vizinhos(u):
            if v not in vis: vis.add(v); q.append(v)
    return vis
# ---- labirintos
for nome, perfeito in (("Labirinto: DFS", True), ("Labirinto: Prim", True), ("Labirinto: Kruskal", True),
                       ("Labirinto: Wilson", True), ("Labirinto: divisão", False)):
    sel(nome)
    L = livres(c); comp = componente(c, (1, 1))
    ok = comp == L and c.fim in comp
    if perfeito: ok = ok and len(L) == 312 + 311
    checar(f"{nome}: conexo{' e perfeito (árvore)' if perfeito else ''}", ok, f"{len(L)} células livres")
    foto("s_lab_" + nome.split()[-1])
# ---- pathfinding em grades aleatórias
def ref_dijkstra(c, oito=False, lama=True):
    s, t = c.inicio, c.fim; d = {s: 0}; h = [(0, s)]
    while h:
        x, u = heapq.heappop(h)
        if x > d[u] + 1e-12: continue
        if oito:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (dr or dc) and c.livre(u[0] + dr, u[1] + dc):
                        v = (u[0] + dr, u[1] + dc); w = math.sqrt(2) if dr and dc else 1
                        if x + w < d.get(v, 1e18): d[v] = x + w; heapq.heappush(h, (x + w, v))
        else:
            for v in c.vizinhos(u):
                w = c.custo(v) if lama else 1
                if x + w < d.get(v, 1e18): d[v] = x + w; heapq.heappush(h, (x + w, v))
    return d.get(t)
def bfs_len(c):
    s, t = c.inicio, c.fim; d = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for v in c.vizinhos(u):
            if v not in d: d[v] = d[u] + 1; q.append(v)
    return d.get(t)
def caminho_valido(c):
    verdes = {k for k, v in c.cor.items() if v == base.VERDE} | {c.inicio, c.fim}
    return c.inicio in verdes
res = {n: True for n in ("BFS", "DFS", "Dijkstra", "A*", "gulosa", "bidirecional", "Lee", "flood BFS", "flood DFS", "JPS", "lama Dij=A*=ref")}
tent = 0; jps_testes = 0
for tr in range(40):
    p = random.choice([0.1, 0.2, 0.3, 0.38])
    c.reiniciar(); c.grade = [[1 if random.random() < p else 0 for _ in range(c.COLS)] for _ in range(c.LINS)]
    c.grade[1][1] = c.grade[c.LINS - 2][c.COLS - 2] = 0
    ref = bfs_len(c)
    if ref is None: continue
    tent += 1
    sel("BFS"); res["BFS"] &= c.caminho_len == ref
    sel("DFS"); res["DFS"] &= "Caminho" in c.info
    sel("Dijkstra"); res["Dijkstra"] &= c.caminho_len == ref
    sel("A*"); res["A*"] &= c.caminho_len == ref
    sel("Busca gulosa"); res["gulosa"] &= "Caminho" in c.info and c.caminho_len >= ref
    sel("BFS bidirecional"); res["bidirecional"] &= c.caminho_len == ref
    sel("Algoritmo de Lee"); res["Lee"] &= c.caminho_len == ref
    sel("Flood fill: BFS"); res["flood BFS"] &= c.preenchidas == len(componente(c, c.inicio))
    sel("Flood fill: DFS"); res["flood DFS"] &= c.preenchidas == len(componente(c, c.inicio))
    sel("Jump Point"); r8 = ref_dijkstra(c, oito=True)
    res["JPS"] &= abs(c.custo_jps - r8) < 1e-9; jps_testes += 1
    if tr % 4 == 0:
        c.espalhar_lama(); c.lama.discard(c.fim); c.lama.discard(c.inicio)
        rl = ref_dijkstra(c)
        sel("Dijkstra"); a = c.custo_total
        sel("A*"); b = c.custo_total
        res["lama Dij=A*=ref"] &= (a == b == rl)
        c.lama.clear()
for k, v in res.items(): checar(f"Grade {k} ({tent} grades aleatórias)", v)
# JPS em grade vazia e em labirinto
c.reiniciar(); c.grade = [[0] * c.COLS for _ in range(c.LINS)]
sel("Jump Point"); checar("JPS grade vazia: custo = diagonal + reta", abs(c.custo_jps - ref_dijkstra(c, oito=True)) < 1e-9, c.info)
sel("Labirinto: Prim"); sel("Jump Point"); checar("JPS em labirinto", abs(c.custo_jps - ref_dijkstra(c, oito=True)) < 1e-9)
foto("s_jps")
sel("Algoritmo de Lee"); foto("s_lee")
sel("A*"); foto("s_astar")
fim()
