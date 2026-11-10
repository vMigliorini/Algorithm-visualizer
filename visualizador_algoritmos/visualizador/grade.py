"""Pathfinding em grade, flood fill e geradores de labirinto."""
import heapq
import math
import random
from collections import deque

import pygame

from .base import *


def grade_bfs(g):
    s, t = g.inicio, g.fim
    pai = {s: None}
    fila = deque([s])
    while fila:
        u = fila.popleft()
        if u == t:
            break
        for v in g.vizinhos(u):
            if v not in pai:
                pai[v] = u
                fila.append(v)
                g.cor[v] = AMARELO
        g.cor[u] = AZUL
        yield
    g.caminho(pai)


def grade_dfs(g):
    s, t = g.inicio, g.fim
    pai = {}
    pilha = [(s, None)]
    while pilha:
        u, p = pilha.pop()
        if u in pai:
            continue
        pai[u] = p
        if u == t:
            break
        g.cor[u] = AZUL
        for v in g.vizinhos(u):
            if v not in pai:
                pilha.append((v, u))
                g.cor[v] = AMARELO
        yield
    g.caminho(pai)


def _a_estrela(g, guloso):
    s, t = g.inicio, g.fim
    h = lambda c: abs(c[0] - t[0]) + abs(c[1] - t[1])
    custo = {s: 0}
    pai = {s: None}
    heap = [(h(s), 0, s)]
    fechado = set()
    while heap:
        _, gc, u = heapq.heappop(heap)
        if u in fechado:
            continue
        fechado.add(u)
        if u == t:
            break
        for v in g.vizinhos(u):
            novo = gc + g.custo(v)
            if v not in custo or novo < custo[v]:
                custo[v] = novo
                pai[v] = u
                prioridade = h(v) if guloso else novo + h(v)
                heapq.heappush(heap, (prioridade, novo, v))
                g.cor[v] = AMARELO
        g.cor[u] = AZUL
        yield
    g.caminho(pai)


def grade_astar(g):
    return _a_estrela(g, guloso=False)


def grade_gulosa(g):
    return _a_estrela(g, guloso=True)


def grade_labirinto(g):
    """Gera um labirinto perfeito com DFS recursivo (backtracker)."""
    g.grade = [[1] * g.COLS for _ in range(g.LINS)]
    g.cor.clear()
    g.grade[1][1] = 0
    pilha = [(1, 1)]
    while pilha:
        r, c = pilha[-1]
        opcoes = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + 2 * dr, c + 2 * dc
            if 0 < nr < g.LINS - 1 and 0 < nc < g.COLS - 1 and g.grade[nr][nc] == 1:
                opcoes.append((nr, nc, dr, dc))
        if opcoes:
            nr, nc, dr, dc = random.choice(opcoes)
            g.grade[r + dr][c + dc] = 0
            g.grade[nr][nc] = 0
            pilha.append((nr, nc))
            g.cor[(nr, nc)] = AMARELO
            yield
        else:
            g.cor.pop(pilha.pop(), None)
    g.cor.clear()


# ---------------------------------------------------------------------
#  Pathfinding adicional
# ---------------------------------------------------------------------

def grade_dijkstra(g):
    s, t = g.inicio, g.fim
    dist = {s: 0}
    pai = {s: None}
    heap = [(0, s)]
    feito = set()
    while heap:
        d, u = heapq.heappop(heap)
        if u in feito:
            continue
        feito.add(u)
        if u == t:
            break
        for v in g.vizinhos(u):
            nd = d + g.custo(v)
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                pai[v] = u
                heapq.heappush(heap, (nd, v))
                g.cor[v] = AMARELO
        g.cor[u] = AZUL
        yield
    g.caminho(pai)


def grade_bidirecional(g):
    s, t = g.inicio, g.fim
    pai_a, pai_b = {s: None}, {t: None}
    fila_a, fila_b = deque([s]), deque([t])
    encontro = None
    while fila_a and fila_b and encontro is None:
        for fila, pai, outro, cor_f, cor_e in ((fila_a, pai_a, pai_b, AMARELO, AZUL),
                                               (fila_b, pai_b, pai_a, LARANJA, CIANO)):
            for _ in range(len(fila)):             # expande um nível inteiro
                u = fila.popleft()
                for v in g.vizinhos(u):
                    if v not in pai:
                        pai[v] = u
                        fila.append(v)
                        g.cor[v] = cor_f
                        if v in outro:
                            encontro = v
                            break
                g.cor[u] = cor_e
                yield
                if encontro is not None:
                    break
            if encontro is not None:
                break
    if encontro is None:
        g.info = "Sem caminho!"
        return
    rota, v = [], encontro
    while v is not None:
        rota.append(v)
        v = pai_a[v]
    rota.reverse()
    v = pai_b[encontro]
    while v is not None:
        rota.append(v)
        v = pai_b[v]
    for c in rota:
        g.cor[c] = VERDE
    g.caminho_len = len(rota) - 1
    g.info = f"Caminho com {len(rota) - 1} passos | células visitadas: {len(pai_a) + len(pai_b)}"


def grade_lee(g):
    """Algoritmo de Lee: frente de onda numerando as distâncias; depois volta pelo gradiente."""
    s, t = g.inicio, g.fim
    dist = {s: 0}
    fila = deque([s])
    while fila:
        u = fila.popleft()
        if u == t:
            break
        for v in g.vizinhos(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                fila.append(v)
                g.cor[v] = cor_hsv(dist[v] * 0.012, 0.7, 0.9)
        yield
    if t not in dist:
        g.info = "Sem caminho!"
        return
    v = t
    n = 0
    while v != s:
        g.cor[v] = VERDE
        v = next(w for w in g.vizinhos(v) if dist.get(w, -1) == dist[v] - 1)
        n += 1
        yield
    g.caminho_len = n
    g.info = f"Caminho com {n} passos (cada cor = uma distância)"


def _flood(g, fila_fifo):
    s = g.inicio
    visto = {s}
    estrutura = deque([s])
    g.cor[s] = AZUL
    while estrutura:
        u = estrutura.popleft() if fila_fifo else estrutura.pop()
        g.cor[u] = AZUL
        for v in g.vizinhos(u):
            if v not in visto:
                visto.add(v)
                estrutura.append(v)
                g.cor[v] = AMARELO
        yield
    g.preenchidas = len(visto)
    g.info = f"Região preenchida: {len(visto)} células (balde de tinta a partir do início)"


def grade_flood_bfs(g):
    return _flood(g, True)


def grade_flood_dfs(g):
    return _flood(g, False)


def grade_jps(g):
    """Jump Point Search em grade com 8 direções (diagonais permitidas quando a célula destino é livre).
    Em vez de visitar célula a célula, 'pula' em linha reta até achar um ponto de salto."""
    s, t = g.inicio, g.fim
    liv = g.livre
    R2 = math.sqrt(2)
    h = lambda c: (abs(c[0] - t[0]) + abs(c[1] - t[1])) + (R2 - 2) * min(abs(c[0] - t[0]), abs(c[1] - t[1]))
    ESCURO = (38, 48, 90)

    def forcado(r, c, dr, dc):
        if dr == 0:
            return (not liv(r - 1, c) and liv(r - 1, c + dc)) or (not liv(r + 1, c) and liv(r + 1, c + dc))
        if dc == 0:
            return (not liv(r, c - 1) and liv(r + dr, c - 1)) or (not liv(r, c + 1) and liv(r + dr, c + 1))
        return (not liv(r - dr, c) and liv(r - dr, c + dc)) or (not liv(r, c - dc) and liv(r + dr, c - dc))

    def pular(r, c, dr, dc):
        r, c = r + dr, c + dc
        while True:
            if not liv(r, c):
                return None
            g.cor.setdefault((r, c), ESCURO)
            if (r, c) == t or forcado(r, c, dr, dc):
                return (r, c)
            if dr != 0 and dc != 0:
                if pular(r, c, dr, 0) is not None or pular(r, c, 0, dc) is not None:
                    return (r, c)
            r, c = r + dr, c + dc

    custo = {s: 0.0}
    pai = {s: None}
    heap = [(h(s), 0.0, s)]
    fechado = set()
    while heap:
        _, gc, u = heapq.heappop(heap)
        if u in fechado:
            continue
        fechado.add(u)
        if u == t:
            break
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                j = pular(u[0], u[1], dr, dc)
                if j is None or j in fechado:
                    continue
                passos = max(abs(j[0] - u[0]), abs(j[1] - u[1]))
                novo = gc + passos * (R2 if dr and dc else 1)
                if j not in custo or novo < custo[j] - 1e-12:
                    custo[j] = novo
                    pai[j] = u
                    heapq.heappush(heap, (novo + h(j), novo, j))
                    g.cor[j] = AMARELO
        g.cor[u] = AZUL
        yield
    if t not in pai:
        g.info = "Sem caminho!"
        return
    v = t
    while v is not None:
        p = pai[v]
        if p is not None:
            dr = (v[0] > p[0]) - (v[0] < p[0])
            dc = (v[1] > p[1]) - (v[1] < p[1])
            r, c = p
            while (r, c) != v:
                g.cor[(r, c)] = VERDE
                r, c = r + dr, c + dc
        g.cor[v] = VERDE
        v = p
    g.custo_jps = custo[t]
    g.info = f"Custo octile {custo[t]:.2f} | pontos de salto expandidos: {len(fechado)} (cinza-azul = células varridas)"


# ---------------------------------------------------------------------
#  Geradores de labirinto (grade de células ímpares; paredes nas pares)
# ---------------------------------------------------------------------

DIRS4 = ((-1, 0), (1, 0), (0, -1), (0, 1))


def _tudo_parede(g):
    g.grade = [[1] * g.COLS for _ in range(g.LINS)]
    g.cor.clear()
    g.lama.clear()


def _celulas(g):
    return [(r, c) for r in range(1, g.LINS - 1, 2) for c in range(1, g.COLS - 1, 2)]


def labirinto_prim(g):
    _tudo_parede(g)
    visitados = {(1, 1)}
    g.grade[1][1] = 0
    fronteira = []

    def adicionar(r, c):
        for dr, dc in DIRS4:
            nr, nc = r + 2 * dr, c + 2 * dc
            if 0 < nr < g.LINS - 1 and 0 < nc < g.COLS - 1 and (nr, nc) not in visitados:
                fronteira.append(((nr, nc), (r + dr, c + dc)))

    adicionar(1, 1)
    ultimo = None
    while fronteira:
        i = random.randrange(len(fronteira))
        fronteira[i], fronteira[-1] = fronteira[-1], fronteira[i]
        cel, parede = fronteira.pop()
        if cel in visitados:
            continue
        visitados.add(cel)
        g.grade[parede[0]][parede[1]] = 0
        g.grade[cel[0]][cel[1]] = 0
        if ultimo:
            g.cor.pop(ultimo, None)
        g.cor[cel] = AMARELO
        ultimo = cel
        adicionar(*cel)
        yield
    g.cor.clear()


def labirinto_kruskal(g):
    _tudo_parede(g)
    celulas = _celulas(g)
    pai = {c: c for c in celulas}

    def achar(x):
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    for r, c in celulas:
        g.grade[r][c] = 0
    arestas = []
    for r, c in celulas:
        if c + 2 < g.COLS - 1:
            arestas.append(((r, c), (r, c + 2)))
        if r + 2 < g.LINS - 1:
            arestas.append(((r, c), (r + 2, c)))
    random.shuffle(arestas)
    for a, b in arestas:
        ra, rb = achar(a), achar(b)
        if ra != rb:
            pai[ra] = rb
            g.grade[(a[0] + b[0]) // 2][(a[1] + b[1]) // 2] = 0
            g.cor.clear()
            g.cor[a] = g.cor[b] = AMARELO
            yield
    g.cor.clear()


def labirinto_wilson(g):
    _tudo_parede(g)
    celulas = _celulas(g)
    no_labirinto = {random.choice(celulas)}
    g.grade[next(iter(no_labirinto))[0]][next(iter(no_labirinto))[1]] = 0
    while len(no_labirinto) < len(celulas):
        inicio = random.choice([c for c in celulas if c not in no_labirinto])
        caminho, idx = [inicio], {inicio: 0}
        atual = inicio
        while atual not in no_labirinto:
            viz = [(atual[0] + 2 * dr, atual[1] + 2 * dc) for dr, dc in DIRS4
                   if 0 < atual[0] + 2 * dr < g.LINS - 1 and 0 < atual[1] + 2 * dc < g.COLS - 1]
            prox = random.choice(viz)
            if prox in idx:                          # laço: apaga o ciclo (loop-erased random walk)
                k = idx[prox]
                for c in caminho[k + 1:]:
                    del idx[c]
                caminho = caminho[:k + 1]
            else:
                idx[prox] = len(caminho)
                caminho.append(prox)
            atual = prox
        for a, b in zip(caminho, caminho[1:]):
            g.grade[a[0]][a[1]] = 0
            g.grade[b[0]][b[1]] = 0
            g.grade[(a[0] + b[0]) // 2][(a[1] + b[1]) // 2] = 0
            no_labirinto.add(a)
            g.cor.clear()
            g.cor[b] = AMARELO
            yield
        no_labirinto.add(caminho[-1])
    g.cor.clear()


def labirinto_divisao(g):
    """Divisão recursiva: constrói paredes com uma passagem e subdivide as duas metades."""
    L, C = g.LINS, g.COLS
    g.grade = [[1 if r in (0, L - 1) or c in (0, C - 1) else 0 for c in range(C)] for r in range(L)]
    g.cor.clear()
    g.lama.clear()
    pilha = [(1, 1, L - 2, C - 2)]
    while pilha:
        r0, c0, r1, c1 = pilha.pop()
        h, w = r1 - r0 + 1, c1 - c0 + 1
        if h < 3 or w < 3:
            continue
        horizontal = h > w if h != w else random.random() < 0.5
        if horizontal:
            wr = random.choice(range(r0 + 1, r1, 2))
            gap = random.choice(range(c0, c1 + 1, 2))
            for c in range(c0, c1 + 1):
                if c != gap:
                    g.grade[wr][c] = 1
                    yield
            pilha.append((r0, c0, wr - 1, c1))
            pilha.append((wr + 1, c0, r1, c1))
        else:
            wc = random.choice(range(c0 + 1, c1, 2))
            gap = random.choice(range(r0, r1 + 1, 2))
            for r in range(r0, r1 + 1):
                if r != gap:
                    g.grade[r][wc] = 1
                    yield
            pilha.append((r0, c0, r1, wc - 1))
            pilha.append((r0, wc + 1, r1, c1))


# ---------------------------------------------------------------------
#  Cena
# ---------------------------------------------------------------------

class Grade(Cena):
    titulo = "Pathfinding em grade"
    CEL, COLS, LINS = 20, 49, 27
    X0 = (LARGURA - COLS * CEL) // 2
    Y0 = TOPO + 2
    vel_inicial = 7
    ajuda = ("Mouse: esq. desenha parede, dir. apaga   C: limpa paredes   R: limpa caminho   "
             "T: lama (custo 5)   M: labirinto",
             "Roxo = início, vermelho = fim, amarelo = fronteira, azul = explorado, verde = caminho. TAB: algoritmos.")
    algoritmos = [
        ("BFS", grade_bfs, "O(V + E)"),
        ("DFS", grade_dfs, "O(V + E)"),
        ("Dijkstra (considera lama)", grade_dijkstra, "O((V+E) log V)"),
        ("A* (Manhattan, considera lama)", grade_astar, "depende da heurística"),
        ("Busca gulosa (greedy best-first)", grade_gulosa, "não é ótima"),
        ("BFS bidirecional", grade_bidirecional, "O(b^(d/2))"),
        ("Jump Point Search (8 direções)", grade_jps, "A* com menos nós"),
        ("Algoritmo de Lee (frente de onda)", grade_lee, "O(V)"),
        ("Flood fill: BFS (balde de tinta)", grade_flood_bfs, "O(V)"),
        ("Flood fill: DFS (balde de tinta)", grade_flood_dfs, "O(V)"),
        ("Labirinto: DFS backtracker", grade_labirinto, "O(V)"),
        ("Labirinto: Prim aleatório", labirinto_prim, "O(V log V)"),
        ("Labirinto: Kruskal aleatório", labirinto_kruskal, "O(E log E)"),
        ("Labirinto: Wilson (passeio aleatório)", labirinto_wilson, "O(V) em média"),
        ("Labirinto: divisão recursiva", labirinto_divisao, "O(V)"),
    ]

    def reiniciar(self):
        self.inicio = (1, 1)
        self.fim = (self.LINS - 2, self.COLS - 2)
        self.cor = {}
        self.lama = set()
        self.grade = [[1 if random.random() < 0.25 else 0 for _ in range(self.COLS)]
                      for _ in range(self.LINS)]
        for r, c in (self.inicio, self.fim):
            self.grade[r][c] = 0
        self.gerador = None
        self.terminou = False

    def livre(self, r, c):
        return 0 <= r < self.LINS and 0 <= c < self.COLS and self.grade[r][c] == 0

    def custo(self, c):
        return 5 if c in self.lama else 1

    def vizinhos(self, u):
        r, c = u
        for dr, dc in DIRS4:
            nr, nc = r + dr, c + dc
            if self.livre(nr, nc):
                yield (nr, nc)

    def caminho(self, pai):
        t = self.fim
        if t not in pai:
            self.info = "Sem caminho!"
            return
        passos, custo, v = 0, 0, t
        while v is not None:
            self.cor[v] = VERDE
            if pai[v] is not None:
                passos += 1
                custo += self.custo(v)
            v = pai[v]
        self.caminho_len = passos
        self.custo_total = custo
        extra = f" | custo {custo}" if self.lama else ""
        self.info = f"Caminho com {passos} passos{extra} | células exploradas: {len(pai)}"

    def limpar_caminho(self):
        self.cor.clear()
        self.gerador = None
        self.terminou = False
        self.info = ""

    def iniciar(self, funcao):
        self.limpar_caminho()
        self.comecar(funcao(self))

    def espalhar_lama(self):
        self.lama.clear()
        for _ in range(9):
            cr, cc = random.randrange(self.LINS), random.randrange(self.COLS)
            raio = random.randint(2, 4)
            for r in range(cr - raio, cr + raio + 1):
                for c in range(cc - raio, cc + raio + 1):
                    if (r - cr) ** 2 + (c - cc) ** 2 <= raio * raio and self.livre(r, c) \
                            and (r, c) not in (self.inicio, self.fim):
                        self.lama.add((r, c))

    def evento_cena(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if e.key == pygame.K_m:
            self.limpar_caminho()
            self.nome = "Labirinto: DFS backtracker"
            self.comecar(grade_labirinto(self))
        elif e.key == pygame.K_c:
            self.limpar_caminho()
            self.grade = [[0] * self.COLS for _ in range(self.LINS)]
        elif e.key == pygame.K_r:
            self.limpar_caminho()
        elif e.key == pygame.K_t:
            self.limpar_caminho()
            self.espalhar_lama()

    def atualizar(self):
        super().atualizar()
        botoes = pygame.mouse.get_pressed()
        if (botoes[0] or botoes[2]) and self.gerador is None:
            x, y = pygame.mouse.get_pos()
            c, r = (x - self.X0) // self.CEL, (y - self.Y0) // self.CEL
            if 0 <= r < self.LINS and 0 <= c < self.COLS and (r, c) not in (self.inicio, self.fim):
                novo = 1 if botoes[0] else 0
                if self.grade[r][c] != novo:
                    self.grade[r][c] = novo
                    self.lama.discard((r, c))
                    self.cor.clear()

    def desenhar_cena(self, tela):
        cel = self.CEL
        for (r, c) in self.lama:
            pygame.draw.rect(tela, (70, 55, 25), (self.X0 + c * cel, self.Y0 + r * cel, cel - 1, cel - 1))
        for r in range(self.LINS):
            linha = self.grade[r]
            for c in range(self.COLS):
                if linha[c]:
                    pygame.draw.rect(tela, (75, 80, 115),
                                     (self.X0 + c * cel, self.Y0 + r * cel, cel - 1, cel - 1))
        for (r, c), cor in self.cor.items():
            pygame.draw.rect(tela, cor, (self.X0 + c * cel, self.Y0 + r * cel, cel - 1, cel - 1))
        for (r, c), cor in ((self.inicio, ROXO), (self.fim, VERMELHO)):
            pygame.draw.rect(tela, cor, (self.X0 + c * cel, self.Y0 + r * cel, cel - 1, cel - 1))
