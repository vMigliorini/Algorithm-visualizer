"""Grafos: caminhos mínimos, buscas, árvores geradoras e coloração."""
import heapq
import math
import random
from collections import deque

import pygame

from .base import *


def g_bfs(g):
    s, t = g.origem, g.destino
    pai = {s: None}
    fila = deque([s])
    g.cor_no[s] = AMARELO
    yield
    while fila:
        u = fila.popleft()
        g.cor_no[u] = VERMELHO
        yield
        if u == t:
            break
        for v, _ in g.adj[u]:
            if v not in pai:
                pai[v] = u
                fila.append(v)
                g.cor_no[v] = AMARELO
                g.cor_aresta[chave(u, v)] = LARANJA
                yield
        g.cor_no[u] = AZUL
    g.caminho(pai)


def g_dfs(g):
    s, t = g.origem, g.destino
    pai = {}
    pilha = [(s, None)]
    while pilha:
        u, p = pilha.pop()
        if u in pai:
            continue
        pai[u] = p
        g.cor_no[u] = VERMELHO
        if p is not None:
            g.cor_aresta[chave(u, p)] = LARANJA
        yield
        if u == t:
            break
        for v, _ in reversed(g.adj[u]):
            if v not in pai:
                pilha.append((v, u))
                g.cor_no[v] = AMARELO
        yield
        g.cor_no[u] = AZUL
    g.caminho(pai)


def g_dijkstra(g):
    s, t = g.origem, g.destino
    dist = {s: 0}
    pai = {s: None}
    heap = [(0, s)]
    feito = set()
    g.rot[s] = "0"
    g.cor_no[s] = AMARELO
    yield
    while heap:
        d, u = heapq.heappop(heap)
        if u in feito:
            continue
        feito.add(u)
        g.cor_no[u] = VERMELHO
        yield
        if u == t:
            break
        for v, w in g.adj[u]:
            if v in feito:
                continue
            melhora = d + w < dist.get(v, math.inf)
            if melhora:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
                g.rot[v] = str(dist[v])
                g.cor_no[v] = AMARELO
            yield from g.testar_aresta(u, v, melhora, pai)
        g.cor_no[u] = AZUL
    g.caminho(pai, dist.get(t))


def g_astar(g):
    s, t = g.origem, g.destino
    h = lambda v: math.dist(g.pos[v], g.pos[t]) / 10   # admissível (pesos = teto de dist/10)
    dist = {s: 0}
    pai = {s: None}
    heap = [(h(s), s)]
    feito = set()
    g.rot[s] = "0"
    g.cor_no[s] = AMARELO
    yield
    while heap:
        _, u = heapq.heappop(heap)
        if u in feito:
            continue
        feito.add(u)
        g.cor_no[u] = VERMELHO
        yield
        if u == t:
            break
        for v, w in g.adj[u]:
            if v in feito:
                continue
            melhora = dist[u] + w < dist.get(v, math.inf)
            if melhora:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v] + h(v), v))
                g.rot[v] = str(dist[v])
                g.cor_no[v] = AMARELO
            yield from g.testar_aresta(u, v, melhora, pai)
        g.cor_no[u] = AZUL
    g.caminho(pai, dist.get(t))


def g_bellman_ford(g):
    s, t = g.origem, g.destino
    dist = {i: math.inf for i in range(g.n)}
    dist[s] = 0
    pai = {s: None}
    g.rot[s] = "0"
    g.cor_no[s] = AMARELO
    for it in range(g.n - 1):
        mudou = False
        g.info = f"Iteração {it + 1} de {g.n - 1}"
        for u, v, w in g.arestas:
            for a, b in ((u, v), (v, u)):
                melhora = dist[a] + w < dist[b]
                if melhora:
                    dist[b] = dist[a] + w
                    g.rot[b] = str(dist[b])
                    g.cor_no[b] = AMARELO
                    mudou = True
                yield from g.testar_aresta(a, b, melhora, pai)
        if not mudou:
            break
    g.caminho(pai, dist[t] if dist[t] < math.inf else None)


def g_prim(g):
    s = g.origem
    na_arvore = {s}
    heap = [(w, s, v) for v, w in g.adj[s]]
    heapq.heapify(heap)
    total = 0
    g.cor_no[s] = VERDE
    yield
    while heap and len(na_arvore) < g.n:
        w, u, v = heapq.heappop(heap)
        if v in na_arvore:
            continue
        k = chave(u, v)
        g.cor_aresta[k] = LARANJA
        yield
        na_arvore.add(v)
        total += w
        g.cor_no[v] = VERDE
        g.cor_aresta[k] = VERDE
        g.info = f"Peso total da árvore: {total}"
        yield
        for x, wx in g.adj[v]:
            if x not in na_arvore:
                heapq.heappush(heap, (wx, v, x))


def g_kruskal(g):
    pai = list(range(g.n))

    def achar_(x):
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    total = 0
    for u, v, w in sorted(g.arestas, key=lambda e: e[2]):
        k = chave(u, v)
        g.cor_aresta[k] = LARANJA
        g.info = f"Avaliando {g.nome_no(u)}-{g.nome_no(v)} (peso {w})   total: {total}"
        yield
        ru, rv = achar_(u), achar_(v)
        if ru != rv:
            pai[ru] = rv
            total += w
            g.cor_aresta[k] = VERDE
            g.cor_no[u] = g.cor_no[v] = VERDE
        else:
            g.cor_aresta[k] = CINZA_ESC          # formaria ciclo: rejeitada
        g.info = f"Peso total da árvore: {total}"
        yield


def g_coloracao(g):
    cores = {}
    for u in range(g.n):
        g.cor_no[u] = CINZA
        yield
        usadas = {cores[v] for v, _ in g.adj[u] if v in cores}
        c = 0
        while c in usadas:
            c += 1
        cores[u] = c
        g.cor_no[u] = PALETA[c % len(PALETA)]
        g.info = f"Cores usadas: {max(cores.values()) + 1}"
        yield


def g_boruvka(g):
    """Borůvka: a cada fase, cada componente escolhe sua aresta mais barata para o exterior."""
    comp = list(range(g.n))

    def achar_(x):
        while comp[x] != x:
            comp[x] = comp[comp[x]]
            x = comp[x]
        return x

    total, componentes, fase = 0, g.n, 0
    while componentes > 1:
        fase += 1
        melhores = {}
        for u, v, w in g.arestas:
            cu, cv = achar_(u), achar_(v)
            if cu == cv:
                continue
            for c in (cu, cv):
                if c not in melhores or (w, u, v) < melhores[c]:
                    melhores[c] = (w, u, v)
        for c, (w, u, v) in melhores.items():
            g.cor_aresta[chave(u, v)] = LARANJA
            g.info = f"Fase {fase}: cada componente escolhe sua aresta mais barata"
            yield
        for c, (w, u, v) in melhores.items():
            if achar_(u) != achar_(v):
                comp[achar_(u)] = achar_(v)
                total += w
                componentes -= 1
                g.cor_aresta[chave(u, v)] = VERDE
                g.cor_no[u] = g.cor_no[v] = VERDE
        g.info = f"Fase {fase} concluída: peso total {total}, componentes: {componentes}"
        yield
    g.info = f"Peso total da árvore: {total}"


def g_coloracao_bt(g):
    """Coloração ótima por backtracking: tenta k = 1, 2, 3... cores até conseguir."""
    n = g.n
    cores = [None] * n

    def colorir(u, k):
        if u == n:
            return True
        for c in range(k):
            cores[u] = c
            g.cor_no[u] = PALETA[c % len(PALETA)]
            yield
            if all(cores[v] != c for v, _ in g.adj[u]):
                if (yield from colorir(u + 1, k)):
                    return True
        cores[u] = None
        g.cor_no.pop(u, None)
        return False

    for k in range(1, n + 1):
        g.info = f"Tentando com {k} cor(es)..."
        yield
        if (yield from colorir(0, k)):
            g.info = f"Colorível com {k} cores (número cromático)"
            return



class Grafos(Cena):
    titulo = "Grafos"
    N = 12
    vel_inicial = 3
    ajuda = ("Origem: clique esquerdo   Destino: clique direito   N: novo grafo   R: limpar cores",
             "TAB: lista de algoritmos (teclas 1-9 e 0 escolhem direto). Pesos = teto(distância/10).")
    algoritmos = [
        ("BFS (largura)", g_bfs, "O(V + E)"),
        ("DFS (profundidade)", g_dfs, "O(V + E)"),
        ("Dijkstra", g_dijkstra, "O((V+E) log V)"),
        ("A*", g_astar, "depende da heurística"),
        ("Bellman-Ford", g_bellman_ford, "O(V·E)"),
        ("Prim (árvore geradora mínima)", g_prim, "O(E log V)"),
        ("Kruskal (árvore geradora mínima)", g_kruskal, "O(E log E)"),
        ("Borůvka (árvore geradora mínima)", g_boruvka, "O(E log V)"),
        ("Coloração gulosa", g_coloracao, "O(V + E)"),
        ("Coloração ótima por backtracking", g_coloracao_bt, "exponencial"),
    ]

    def nome_no(self, i):
        return chr(65 + i)

    def _gerar(self):
        n = self.N
        pts, sep, tentativas = [], 95, 0
        while len(pts) < n:
            p = (random.randint(50, LARGURA - 50), random.randint(TOPO + 45, ALTURA - 45))
            if all(math.dist(p, q) >= sep for q in pts):
                pts.append(p)
            tentativas += 1
            if tentativas > 5000:
                sep -= 10
                tentativas = 0

        arestas = set()
        for i in range(n):
            viz = sorted((j for j in range(n) if j != i),
                         key=lambda j: math.dist(pts[i], pts[j]))[:3]
            for j in viz:
                arestas.add(chave(i, j))

        pai = list(range(n))

        def achar_(x):
            while pai[x] != x:
                pai[x] = pai[pai[x]]
                x = pai[x]
            return x

        for u, v in arestas:
            pai[achar_(u)] = achar_(v)
        while len({achar_(i) for i in range(n)}) > 1:      # garante grafo conexo
            _, a, b = min((math.dist(pts[a], pts[b]), a, b)
                          for a in range(n) for b in range(a + 1, n) if achar_(a) != achar_(b))
            arestas.add((a, b))
            pai[achar_(a)] = achar_(b)
        return pts, arestas

    @staticmethod
    def _sobrepoe(pts, arestas):
        """True se algum nó fica muito perto de uma aresta que não é dele (evita sobreposição)."""
        for u, v in arestas:
            ax, ay = pts[u]
            dx, dy = pts[v][0] - ax, pts[v][1] - ay
            for i, (px, py) in enumerate(pts):
                if i in (u, v):
                    continue
                t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
                if math.hypot(px - (ax + t * dx), py - (ay + t * dy)) < 30:
                    return True
        return False

    def reiniciar(self):
        for _ in range(300):
            pts, arestas = self._gerar()
            if not self._sobrepoe(pts, arestas):
                break
        n = self.n = self.N
        self.pos = pts
        # peso = teto(distância/10): mantém a heurística do A* admissível
        self.arestas = [(u, v, max(1, math.ceil(math.dist(pts[u], pts[v]) / 10)))
                        for u, v in sorted(arestas)]
        self.adj = {i: [] for i in range(n)}
        for u, v, w in self.arestas:
            self.adj[u].append((v, w))
            self.adj[v].append((u, w))
        self.origem = 0
        self.destino = max(range(n), key=lambda j: math.dist(pts[0], pts[j]))
        self.limpar()

    def limpar(self):
        self.cor_no, self.cor_aresta, self.rot = {}, {}, {}
        self.gerador = None
        self.terminou = False
        self.passos = 0
        self.info = ""
        self.nome = "-" if not hasattr(self, "nome") else self.nome

    def iniciar(self, funcao):
        self.limpar()
        self.comecar(funcao(self))

    # auxiliares usados pelos algoritmos
    def testar_aresta(self, a, b, melhora, pai):
        k = chave(a, b)
        antigo = self.cor_aresta.get(k)
        self.cor_aresta[k] = LARANJA
        if melhora:
            if pai.get(b) is not None:
                self.cor_aresta.pop(chave(b, pai[b]), None)
            pai[b] = a
        yield
        if not melhora:
            if antigo is None:
                self.cor_aresta.pop(k, None)
            else:
                self.cor_aresta[k] = antigo

    def caminho(self, pai, distancia=None):
        t = self.destino
        if t not in pai:
            self.info = "Destino não alcançado"
            return
        rota, v = [], t
        while v is not None:
            rota.append(v)
            self.cor_no[v] = VERDE
            p = pai[v]
            if p is not None:
                self.cor_aresta[chave(v, p)] = VERDE
            v = p
        txt = " > ".join(self.nome_no(x) for x in reversed(rota))
        extra = f"   (distância {distancia})" if distancia is not None else ""
        self.info = f"Caminho: {txt}{extra}"

    def no_em(self, p):
        for i, q in enumerate(self.pos):
            if math.dist(p, q) <= 24:
                return i
        return None

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_n:
                self.reiniciar()
            elif e.key == pygame.K_r:
                self.limpar()
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button in (1, 3):
            i = self.no_em(e.pos)
            if i is not None:
                if e.button == 1 and i != self.destino:
                    self.origem = i
                elif e.button == 3 and i != self.origem:
                    self.destino = i
                self.limpar()

    def desenhar_cena(self, tela):
        for u, v, w in self.arestas:
            k = chave(u, v)
            cor = self.cor_aresta.get(k, (90, 90, 105))
            pygame.draw.line(tela, cor, self.pos[u], self.pos[v], 5 if k in self.cor_aresta else 2)
        for u, v, w in self.arestas:
            mx = (self.pos[u][0] + self.pos[v][0]) // 2
            my = (self.pos[u][1] + self.pos[v][1]) // 2
            r = texto(tela, w, mx, my - 7, "p", CINZA if chave(u, v) not in self.cor_aresta else BRANCO,
                      centro=True)
        for i, (x, y) in enumerate(self.pos):
            if i == self.origem:
                pygame.draw.circle(tela, CIANO, (x, y), 24, 3)
            if i == self.destino:
                pygame.draw.circle(tela, (255, 60, 220), (x, y), 24, 3)
            pygame.draw.circle(tela, self.cor_no.get(i, BRANCO), (x, y), 18)
            texto(tela, self.nome_no(i), x, y - 8, "m", PRETO, centro=True)
            if i in self.rot:
                texto(tela, self.rot[i], x, y - 42, "m", AMARELO, centro=True)
