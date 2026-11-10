"""Grafos avançados: Floyd-Warshall, ordenação topológica, SCC (Tarjan/Kosaraju),
pontes e articulações, ciclo euleriano, fluxo máximo e emparelhamento bipartido.

Cada algoritmo pede um tipo de grafo diferente (DAG, dígrafo, rede de fluxo...), então
o grafo é gerado de novo quando você escolhe o algoritmo (N gera outro do mesmo tipo)."""
import math
import random
from collections import deque

import pygame

from .base import *
from .grafos import Grafos


def _pontos(n, x0, x1, y0, y1, sep=90):
    pts, tent = [], 0
    while len(pts) < n:
        p = (random.randint(x0, x1), random.randint(y0, y1))
        if all(math.dist(p, q) >= sep for q in pts):
            pts.append(p)
        tent += 1
        if tent > 5000:
            sep -= 10
            tent = 0
    return pts


def _knn_conexo(pts, k=2):
    n = len(pts)
    arestas = set()
    for i in range(n):
        viz = sorted((j for j in range(n) if j != i), key=lambda j: math.dist(pts[i], pts[j]))[:k]
        for j in viz:
            arestas.add(chave(i, j))
    pai = list(range(n))

    def achar(x):
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    for u, v in arestas:
        pai[achar(u)] = achar(v)
    while len({achar(i) for i in range(n)}) > 1:
        _, a, b = min((math.dist(pts[a], pts[b]), a, b)
                      for a in range(n) for b in range(a + 1, n) if achar(a) != achar(b))
        arestas.add((a, b))
        pai[achar(a)] = achar(b)
    return arestas


# =====================================================================
#  ALGORITMOS (recebem a cena `g`)
# =====================================================================

def floyd_warshall(g):
    n = g.n
    D = [[math.inf] * n for _ in range(n)]
    for i in range(n):
        D[i][i] = 0
    for u, v, w in g.arestas:
        D[u][v] = D[v][u] = w
    g.matriz = D
    g.info = "D[i][j] = min(D[i][j], D[i][k] + D[k][j])  (k = amarelo)"
    yield
    for k in range(n):
        g.cor_no = {k: AMARELO}
        for i in range(n):
            for j in range(n):
                if i == j or i == k or j == k:
                    continue
                nova = D[i][k] + D[k][j]
                melhora = nova < D[i][j]
                if melhora:
                    D[i][j] = nova
                g.mat_dest = (k, i, j, melhora)
                yield
    g.cor_no, g.mat_dest = {}, None
    g.info = "Matriz final: menor distância entre todos os pares"


floyd_warshall.tipo = "matriz"


def topo_kahn(g):
    n = g.n
    grau = [0] * n
    for u, v, _ in g.arestas:
        grau[v] += 1
    fila = deque(i for i in range(n) if grau[i] == 0)
    for i in fila:
        g.cor_no[i] = AMARELO
    g.rot = {i: f"in={grau[i]}" for i in range(n)}
    g.info = "Remove repetidamente nós sem arestas de entrada"
    yield
    while fila:
        u = fila.popleft()
        g.cor_no[u] = VERDE
        g.lista.append(u)
        yield
        for v, _ in g.adj[u]:
            g.cor_aresta[(u, v)] = CINZA_ESC
            grau[v] -= 1
            g.rot[v] = f"in={grau[v]}"
            if grau[v] == 0:
                fila.append(v)
                g.cor_no[v] = AMARELO
            yield


topo_kahn.tipo = "dag"


def topo_dfs(g):
    estado = {}

    def dfs(u):
        estado[u] = 1
        g.cor_no[u] = AMARELO
        yield
        for v, _ in g.adj[u]:
            if v not in estado:
                g.cor_aresta[(u, v)] = LARANJA
                yield from dfs(v)
        estado[u] = 2
        g.cor_no[u] = VERDE
        g.lista.insert(0, u)                 # pós-ordem invertida
        yield

    g.info = "DFS: ao terminar um nó, ele entra no INÍCIO da lista"
    for u in range(g.n):
        if u not in estado:
            yield from dfs(u)


topo_dfs.tipo = "dag"


def scc_tarjan(g):
    idx, low, pilha, na_pilha = {}, {}, [], set()
    cont, ncomp = [0], [0]
    g.comp = {}

    def dfs(u):
        idx[u] = low[u] = cont[0]
        cont[0] += 1
        pilha.append(u)
        na_pilha.add(u)
        g.cor_no[u] = AMARELO
        g.rot[u] = f"{idx[u]}/{low[u]}"
        yield
        for v, _ in g.adj[u]:
            if v not in idx:
                g.cor_aresta[(u, v)] = LARANJA
                yield from dfs(v)
                low[u] = min(low[u], low[v])
            elif v in na_pilha:
                low[u] = min(low[u], idx[v])
                g.cor_aresta[(u, v)] = ROXO
            g.rot[u] = f"{idx[u]}/{low[u]}"
            yield
        if low[u] == idx[u]:
            cor = PALETA[ncomp[0] % len(PALETA)]
            while True:
                w = pilha.pop()
                na_pilha.discard(w)
                g.cor_no[w] = cor
                g.comp[w] = ncomp[0]
                if w == u:
                    break
            ncomp[0] += 1
            yield

    g.info = "Rótulo = índice/low-link. Um nó com low = índice é raiz de uma componente."
    for u in range(g.n):
        if u not in idx:
            yield from dfs(u)
    g.info = f"{ncomp[0]} componentes fortemente conexas"


scc_tarjan.tipo = "digrafo"


def scc_kosaraju(g):
    visto, ordem = set(), []
    g.comp = {}

    def dfs1(u):
        visto.add(u)
        g.cor_no[u] = AMARELO
        yield
        for v, _ in g.adj[u]:
            if v not in visto:
                g.cor_aresta[(u, v)] = LARANJA
                yield from dfs1(v)
        ordem.append(u)
        g.cor_no[u] = AZUL
        g.rot[u] = str(len(ordem))
        yield

    g.info = "Passo 1: DFS no grafo original, numerando a ordem de término"
    for u in range(g.n):
        if u not in visto:
            yield from dfs1(u)
    radj = {i: [] for i in range(g.n)}
    for u, v, _ in g.arestas:
        radj[v].append(u)
    g.cor_aresta = {}
    g.cor_no = {}
    g.info = "Passo 2: DFS no grafo TRANSPOSTO, na ordem inversa de término"
    yield
    visto2, ncomp = set(), [0]

    def dfs2(u, cor):
        visto2.add(u)
        g.cor_no[u] = cor
        g.comp[u] = ncomp[0]
        yield
        for v in radj[u]:
            if v not in visto2:
                g.cor_aresta[(v, u)] = cor
                yield from dfs2(v, cor)

    for u in reversed(ordem):
        if u not in visto2:
            yield from dfs2(u, PALETA[ncomp[0] % len(PALETA)])
            ncomp[0] += 1
    g.info = f"{ncomp[0]} componentes fortemente conexas"


scc_kosaraju.tipo = "digrafo"


def pontes_articulacoes(g):
    disc, low = {}, {}
    tempo = [0]
    pontes, arts = [], set()

    def dfs(u, pai):
        disc[u] = low[u] = tempo[0]
        tempo[0] += 1
        filhos = 0
        g.cor_no[u] = AMARELO
        g.rot[u] = f"{disc[u]}/{low[u]}"
        yield
        for v, _ in g.adj[u]:
            if v == pai:
                continue
            if v in disc:
                low[u] = min(low[u], disc[v])
            else:
                filhos += 1
                g.cor_aresta[chave(u, v)] = LARANJA
                yield from dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    pontes.append(chave(u, v))
                    g.cor_aresta[chave(u, v)] = VERMELHO
                else:
                    g.cor_aresta[chave(u, v)] = VERDE
                if pai is not None and low[v] >= disc[u]:
                    arts.add(u)
            g.rot[u] = f"{disc[u]}/{low[u]}"
            yield
        if pai is None and filhos > 1:
            arts.add(u)
        g.cor_no[u] = ROXO if u in arts else AZUL
        yield

    g.info = "Rótulo = descoberta/low. Ponte: low[filho] > descoberta[pai]."
    yield from dfs(0, None)
    g.pontes, g.arts = pontes, arts
    nome = g.nome_no
    g.resultado = ("Pontes (vermelhas): " + (", ".join(f"{nome(a)}-{nome(b)}" for a, b in pontes) or "nenhuma")
                   + "   |   Articulações (roxas): " + (", ".join(nome(a) for a in sorted(arts)) or "nenhuma"))


pontes_articulacoes.tipo = "pontes"


def euler_hierholzer(g):
    rest = {u: [v for v, _ in g.adj[u]] for u in range(g.n)}
    pilha, circuito = [0], []
    g.cor_no[0] = AMARELO
    g.info = "Hierholzer: segue arestas não usadas; ao travar, recua e emite o nó"
    yield
    while pilha:
        u = pilha[-1]
        if rest[u]:
            v = rest[u].pop()
            rest[v].remove(u)
            g.cor_aresta[chave(u, v)] = LARANJA
            pilha.append(v)
            g.cor_no[v] = AMARELO
        else:
            circuito.append(pilha.pop())
            g.cor_no[u] = VERDE
        yield
    g.circuito = circuito
    g.cor_aresta = {}
    for a, b in zip(circuito, circuito[1:]):
        g.cor_aresta[chave(a, b)] = VERDE
        yield
    g.resultado = "Ciclo euleriano: " + " > ".join(g.nome_no(x) for x in circuito)
    g.info = f"Usou as {len(g.arestas)} arestas exatamente uma vez"


euler_hierholzer.tipo = "euler"


def _colorir_fluxo(g, cap):
    g.cor_aresta = {}
    for u, v, w in g.arestas:
        f = w - cap[(u, v)]
        g.rot_aresta[(u, v)] = f"{f}/{w}"
        if f == w:
            g.cor_aresta[(u, v)] = VERMELHO
        elif f > 0:
            g.cor_aresta[(u, v)] = AZUL


def _fluxo(g, modo):
    s, t, n = g.origem, g.destino, g.n
    cap, viz = {}, {i: set() for i in range(n)}
    for u, v, w in g.arestas:
        cap[(u, v)] = w
        cap.setdefault((v, u), 0)
        viz[u].add(v)
        viz[v].add(u)
    fluxo = 0
    _colorir_fluxo(g, cap)
    g.info = "Procura caminhos aumentantes no grafo residual. Azul = com fluxo, vermelho = saturada."
    yield
    while True:
        pai = {s: None}
        g.cor_no = {s: AMARELO}
        if modo == "bfs":
            fila = deque([s])
            while fila and t not in pai:
                u = fila.popleft()
                for v in sorted(viz[u]):
                    if v not in pai and cap[(u, v)] > 0:
                        pai[v] = u
                        fila.append(v)
                        g.cor_no[v] = AMARELO
                        yield
        else:
            def dfs(u):
                if u == t:
                    return True
                for v in sorted(viz[u]):
                    if v not in pai and cap[(u, v)] > 0:
                        pai[v] = u
                        g.cor_no[v] = AMARELO
                        yield
                        if (yield from dfs(v)):
                            return True
                return False
            yield from dfs(s)
        if t not in pai:
            break
        gargalo, v = math.inf, t
        while v != s:
            gargalo = min(gargalo, cap[(pai[v], v)])
            v = pai[v]
        v = t
        rota = []
        while v != s:
            u = pai[v]
            cap[(u, v)] -= gargalo
            cap[(v, u)] += gargalo
            rota.append((u, v))
            v = u
        fluxo += gargalo
        _colorir_fluxo(g, cap)
        for u, v in rota:
            if (u, v) in g.rot_aresta:
                g.cor_aresta[(u, v)] = VERDE
        g.info = f"Caminho aumentante com gargalo {gargalo}: fluxo total = {fluxo}"
        yield
    g.cor_no = {}
    _colorir_fluxo(g, cap)
    g.fluxo = fluxo
    g.info = f"Fluxo máximo = {fluxo} (nenhum caminho aumentante restante)"


def fluxo_edmonds_karp(g):
    return _fluxo(g, "bfs")


def fluxo_ford_fulkerson(g):
    return _fluxo(g, "dfs")


fluxo_edmonds_karp.tipo = "fluxo"
fluxo_ford_fulkerson.tipo = "fluxo"


def kuhn(g):
    par = {}

    def tentar(u, vis):
        for v, _ in g.adj[u]:
            if v in vis:
                continue
            vis.add(v)
            k = chave(u, v)
            antes = g.cor_aresta.get(k)
            g.cor_aresta[k] = LARANJA
            g.cor_no[v] = AMARELO
            yield
            if v not in par or (yield from tentar(par[v], vis)):
                if v in par:
                    g.cor_aresta.pop(chave(par[v], v), None)
                par[v] = u
                g.cor_aresta[k] = VERDE
                yield
                return True
            if antes is None:
                g.cor_aresta.pop(k, None)
            else:
                g.cor_aresta[k] = antes
        return False

    g.info = "Cada nó da esquerda tenta um par; se o par já está ocupado, tenta realocar o ocupante"
    for u in g.esq:
        g.cor_no[u] = AMARELO
        yield
        ok = yield from tentar(u, set())
        for r in g.dir:
            g.cor_no.pop(r, None)
        for r in par:
            g.cor_no[r] = VERDE
        g.cor_no[u] = VERDE if ok else VERMELHO
        yield
    g.par = dict(par)
    g.info = f"Emparelhamento máximo: {len(par)} pares"


kuhn.tipo = "bipartido"


# =====================================================================
#  CENA
# =====================================================================

class GrafosAvancados(Grafos):
    titulo = "Grafos avançados"
    ajuda = ("N: gerar outro grafo do mesmo tipo   R: limpar cores   TAB: escolher o algoritmo",
             "O tipo de grafo muda conforme o algoritmo (DAG, dígrafo, rede de fluxo, bipartido...).")
    algoritmos = [
        ("Floyd-Warshall (todos os pares)", floyd_warshall, "O(V³)"),
        ("Ordenação topológica: Kahn", topo_kahn, "O(V + E)"),
        ("Ordenação topológica: DFS", topo_dfs, "O(V + E)"),
        ("Componentes fortemente conexas: Tarjan", scc_tarjan, "O(V + E)"),
        ("Componentes fortemente conexas: Kosaraju", scc_kosaraju, "O(V + E)"),
        ("Pontes e pontos de articulação", pontes_articulacoes, "O(V + E)"),
        ("Ciclo euleriano (Hierholzer)", euler_hierholzer, "O(E)"),
        ("Fluxo máximo: Edmonds-Karp (BFS)", fluxo_edmonds_karp, "O(V·E²)"),
        ("Fluxo máximo: Ford-Fulkerson (DFS)", fluxo_ford_fulkerson, "O(E · fluxo)"),
        ("Emparelhamento bipartido (Kuhn)", kuhn, "O(V·E)"),
    ]

    def reiniciar(self):
        self.gerar("matriz")
        self.alg_idx = 0
        self.nome, _, self.complexidade = self.algoritmos[0]

    # ---------- geração dos grafos ----------
    def gerar(self, tipo):
        self.tipo = tipo
        for _ in range(200):
            pts, arestas, dirigido = getattr(self, "_gerar_" + tipo)()
            if tipo in ("fluxo", "bipartido") or not Grafos._sobrepoe(pts, [(u, v) for u, v, _ in arestas]):
                break
        self.pos, self.arestas, self.dirigido = pts, arestas, dirigido
        self.n = len(pts)
        self.adj = {i: [] for i in range(self.n)}
        for u, v, w in arestas:
            self.adj[u].append((v, w))
            if not dirigido:
                self.adj[v].append((u, w))
        self.limpar()
        if tipo == "fluxo":
            self.rot_aresta = {(u, v): str(w) for u, v, w in arestas}

    def _gerar_matriz(self):
        pts = _pontos(7, 50, 610, TOPO + 50, ALTURA - 50)
        ar = _knn_conexo(pts, 2)
        return pts, [(u, v, max(1, math.ceil(math.dist(pts[u], pts[v]) / 10))) for u, v in sorted(ar)], False

    def _gerar_dag(self):
        n = 8
        pts = _pontos(n, 50, LARGURA - 50, TOPO + 50, ALTURA - 60)
        ordem = random.sample(range(n), n)
        ar = set()
        for i in range(n - 1):                       # garante que quase todos tenham ligação
            if random.random() < 0.6:
                ar.add((ordem[i], ordem[i + 1]))
        for i in range(n):
            for j in range(i + 2, n):
                if random.random() < 0.22:
                    ar.add((ordem[i], ordem[j]))
        return pts, [(u, v, 1) for u, v in sorted(ar)], True

    def _gerar_digrafo(self):
        tamanhos = random.choice([[3, 3, 3, 1], [4, 3, 3], [5, 4, 1], [4, 4, 1, 1]])
        n = sum(tamanhos)
        pts = _pontos(n, 50, LARGURA - 50, TOPO + 50, ALTURA - 60, sep=80)
        nos = random.sample(range(n), n)
        grupos, k = [], 0
        for t in tamanhos:
            grupos.append(nos[k:k + t])
            k += t
        ar = set()
        for gr in grupos:
            if len(gr) >= 3:
                for a, b in zip(gr, gr[1:] + gr[:1]):
                    ar.add((a, b))
        for _ in range(len(grupos) + 2):
            i, j = sorted(random.sample(range(len(grupos)), 2))
            ar.add((random.choice(grupos[i]), random.choice(grupos[j])))
        return pts, [(u, v, 1) for u, v in sorted(ar)], True

    def _gerar_pontes(self):
        n = 9
        pts = _pontos(n, 50, LARGURA - 50, TOPO + 50, ALTURA - 60)
        ar = set()
        for i in range(1, n):
            ar.add(chave(i, random.randrange(i)))
        for _ in range(2):
            a, b = random.sample(range(n), 2)
            ar.add(chave(a, b))
        return pts, [(u, v, 1) for u, v in sorted(ar)], False

    def _gerar_euler(self):
        n = 7
        pts = _pontos(n, 80, LARGURA - 80, TOPO + 60, ALTURA - 60, sep=110)
        ciclo = random.sample(range(n), n)
        ar = {chave(a, b) for a, b in zip(ciclo, ciclo[1:] + ciclo[:1])}
        for _ in range(200):
            tri = random.sample(range(n), 3)
            novas = {chave(tri[0], tri[1]), chave(tri[1], tri[2]), chave(tri[0], tri[2])}
            if not (novas & ar):
                ar |= novas
                break
        return pts, [(u, v, 1) for u, v in sorted(ar)], False

    def _gerar_fluxo(self):
        camadas = [[0], [1, 2, 3], [4, 5, 6], [7]]
        xs = [90, 340, 620, 900]
        pts = [None] * 8
        for x, cam in zip(xs, camadas):
            for i, no in enumerate(cam):
                y = TOPO + 60 + (i + 0.5) * (ALTURA - TOPO - 120) / len(cam) + random.randint(-14, 14)
                pts[no] = (x + random.randint(-12, 12), int(y))
        ar = {(0, v) for v in camadas[1]} | {(v, 7) for v in camadas[2]}
        for u in camadas[1]:
            for v in random.sample(camadas[2], 2):
                ar.add((u, v))
        for v in camadas[2]:
            if not any(b == v for _, b in ar if _ in camadas[1]):
                ar.add((random.choice(camadas[1]), v))
        self.origem, self.destino = 0, 7
        return pts, [(u, v, random.randint(4, 14)) for u, v in sorted(ar)], True

    def _gerar_bipartido(self):
        esq, dir_ = list(range(5)), list(range(5, 10))
        pts = [None] * 10
        for i in range(5):
            pts[i] = (330, int(TOPO + 60 + (i + 0.5) * (ALTURA - TOPO - 120) / 5))
            pts[5 + i] = (670, int(TOPO + 60 + (i + 0.5) * (ALTURA - TOPO - 120) / 5))
        ar = set()
        for u in esq:
            for v in random.sample(dir_, random.choice([1, 2, 2, 3])):
                ar.add((u, v))
        self.esq, self.dir = esq, dir_
        return pts, [(u, v, 1) for u, v in sorted(ar)], False

    # ---------- estado ----------
    def k(self, u, v):
        return (u, v) if self.dirigido else chave(u, v)

    def limpar(self):
        self.cor_no, self.cor_aresta, self.rot = {}, {}, {}
        self.rot_aresta = getattr(self, "rot_aresta", {}) if self.tipo == "fluxo" else {}
        if self.tipo == "fluxo":
            self.rot_aresta = {(u, v): str(w) for u, v, w in self.arestas}
        self.lista, self.resultado, self.matriz, self.mat_dest = [], "", None, None
        self.gerador = None
        self.terminou = False
        self.passos = 0
        self.info = ""

    def iniciar(self, funcao):
        self.gerar(funcao.tipo)                   # sempre um grafo novo do tipo que o algoritmo pede
        self.comecar(funcao(self))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_n and self.alg_idx >= 0:
                self.selecionar_sem_rodar()
            elif e.key == pygame.K_r:
                self.limpar()

    def selecionar_sem_rodar(self):
        self.gerar(self.algoritmos[self.alg_idx][1].tipo)

    # ---------- desenho ----------
    def desenhar_cena(self, tela):
        mostra_peso = self.tipo == "matriz"
        for u, v, w in self.arestas:
            k = self.k(u, v)
            cor = self.cor_aresta.get(k, (95, 95, 110))
            larg = 5 if k in self.cor_aresta else 2
            if self.dirigido:
                seta(tela, self.pos[u], self.pos[v], cor, larg, recuo=19, ponta=11)
            else:
                pygame.draw.line(tela, cor, self.pos[u], self.pos[v], larg)
        for u, v, w in self.arestas:
            k = self.k(u, v)
            rot = self.rot_aresta.get(k) if self.tipo == "fluxo" else (str(w) if mostra_peso else None)
            if rot:
                mx = (self.pos[u][0] + self.pos[v][0]) // 2
                my = (self.pos[u][1] + self.pos[v][1]) // 2
                r = texto(tela, rot, mx, my - 7, "p", BRANCO, centro=True)
                pygame.draw.rect(tela, (12, 12, 20), r.inflate(4, 0))
                texto(tela, rot, mx, my - 7, "p", AMARELO if k in self.cor_aresta else CINZA, centro=True)
        for i, (x, y) in enumerate(self.pos):
            anel = None
            if self.tipo == "fluxo" and i == self.origem:
                anel = CIANO
            elif self.tipo == "fluxo" and i == self.destino:
                anel = (255, 60, 220)
            if anel:
                pygame.draw.circle(tela, anel, (x, y), 24, 3)
            pygame.draw.circle(tela, self.cor_no.get(i, BRANCO), (x, y), 18)
            texto(tela, self.nome_no(i), x, y - 8, "m", PRETO, centro=True)
            if i in self.rot:
                texto(tela, self.rot[i], x, y - 42, "p", AMARELO, centro=True)
        if self.matriz is not None:
            self._desenhar_matriz(tela)
        if self.tipo in ("dag",) and self.lista:
            texto(tela, "Ordem topológica: " + " > ".join(self.nome_no(x) for x in self.lista),
                  10, ALTURA - 28, "m", CIANO)
        elif self.tipo == "digrafo" and getattr(self, "comp", None) and self.terminou:
            grupos = {}
            for no, c in self.comp.items():
                grupos.setdefault(c, []).append(self.nome_no(no))
            texto(tela, "Componentes: " + "   ".join("{" + ",".join(sorted(v)) + "}" for v in grupos.values()),
                  10, ALTURA - 28, "m", CIANO)
        elif self.resultado:
            texto(tela, self.resultado, 10, ALTURA - 28, "m", CIANO)

    def _desenhar_matriz(self, tela):
        n, lado_x, lado_y = self.n, 46, 34
        x0, y0 = 640, TOPO + 50
        texto(tela, "Matriz de distâncias D", x0, y0 - 28, "m", CIANO)
        for i in range(n):
            texto(tela, self.nome_no(i), x0 + (i + 1) * lado_x + lado_x // 2, y0 + 8, "m", CINZA, centro=True)
            texto(tela, self.nome_no(i), x0 + lado_x // 2, y0 + (i + 1) * lado_y + 8, "m", CINZA, centro=True)
        for i in range(n):
            for j in range(n):
                r = pygame.Rect(x0 + (j + 1) * lado_x, y0 + (i + 1) * lado_y, lado_x - 2, lado_y - 2)
                fundo = (28, 28, 40)
                if self.mat_dest:
                    k, a, b, melhorou = self.mat_dest
                    if (i, j) == (a, b):
                        fundo = VERDE if melhorou else AMARELO
                    elif (i, j) in ((a, k), (k, b)):
                        fundo = (60, 80, 120)
                pygame.draw.rect(tela, fundo, r, border_radius=4)
                v = self.matriz[i][j]
                cor = PRETO if fundo in (VERDE, AMARELO) else BRANCO
                texto(tela, "-" if v == math.inf else v, r.centerx, r.y + 8, "p", cor, centro=True)
