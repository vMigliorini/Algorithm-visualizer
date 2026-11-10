"""IA e otimização: k-means, k-NN, perceptron, gradiente descendente, minimax com poda alfa-beta,
MCTS (jogo da velha) e o problema do caixeiro viajante (vizinho mais próximo, 2-opt, força bruta,
simulated annealing e algoritmo genético)."""
import itertools
import math
import random

import pygame

from .base import *

AREA_Y0, AREA_Y1 = TOPO + 20, ALTURA - 20


def _blob(cx, cy, sd, n):
    pts = []
    for _ in range(n):
        x = min(max(random.gauss(cx, sd), 20), LARGURA - 20)
        y = min(max(random.gauss(cy, sd), AREA_Y0), AREA_Y1)
        pts.append((x, y))
    return pts


def _centros_separados(k, sep):
    cs = []
    while len(cs) < k:
        p = (random.randint(170, LARGURA - 170), random.randint(TOPO + 110, ALTURA - 110))
        if all(math.dist(p, q) >= sep for q in cs):
            cs.append(p)
    return cs


# =====================================================================
#  k-means
# =====================================================================

def kmeans(g):
    k = 3
    g.pts = [p for c in _centros_separados(k, 230) for p in _blob(c[0], c[1], 48, 30)]
    pts, n = g.pts, len(g.pts)
    g.cent = [pts[i] for i in random.sample(range(n), k)]
    g.rot = [None] * n
    g.historico = []
    g.iteracoes = 0
    inercia = lambda: sum(math.dist(pts[i], g.cent[g.rot[i]]) ** 2 for i in range(n))
    g.info = "Centróides iniciais escolhidos ao acaso entre os pontos."
    yield
    while True:
        mudou = False
        for i, p in enumerate(pts):
            j = min(range(k), key=lambda c: math.dist(p, g.cent[c]))
            if g.rot[i] != j:
                mudou = True
                g.rot[i] = j
        g.historico.append(inercia())
        g.iteracoes += 1
        g.info = f"Iteração {g.iteracoes}: cada ponto vai para o centróide mais próximo (inércia {g.historico[-1]:.0f})"
        yield
        novos = []
        for j in range(k):
            m = [pts[i] for i in range(n) if g.rot[i] == j]
            novos.append((sum(p[0] for p in m) / len(m), sum(p[1] for p in m) / len(m)) if m else g.cent[j])
        g.cent = novos
        g.historico.append(inercia())
        g.info = f"Iteração {g.iteracoes}: cada centróide vai para a média do seu grupo (inércia {g.historico[-1]:.0f})"
        yield
        if not mudou:
            break
    g.info = f"Convergiu em {g.iteracoes} iterações (inércia final {g.historico[-1]:.0f})"


# =====================================================================
#  k-NN
# =====================================================================

def knn(g):
    c1, c2 = _centros_separados(2, 260)
    g.pts = _blob(c1[0], c1[1], 85, 30) + _blob(c2[0], c2[1], 85, 30)
    g.rot = [0] * 30 + [1] * 30
    g.consultas, g.viz, g.atual_q = [], [], None
    K = 5
    g.info = f"k-NN com k = {K}: o ponto novo recebe a classe da maioria dos {K} vizinhos mais próximos."
    yield
    for _ in range(7):
        q = (random.randint(180, LARGURA - 180), random.randint(TOPO + 80, ALTURA - 80))
        g.atual_q, g.viz = q, []
        yield
        ordem = sorted(range(len(g.pts)), key=lambda i: math.dist(q, g.pts[i]))[:K]
        for i in ordem:
            g.viz.append(i)
            yield
        votos = [sum(1 for i in ordem if g.rot[i] == c) for c in (0, 1)]
        pred = 0 if votos[0] > votos[1] else 1
        g.consultas.append((q, pred, list(ordem)))
        g.info = f"Votos: classe azul {votos[0]} x laranja {votos[1]} -> {'azul' if pred == 0 else 'laranja'}"
        g.atual_q, g.viz = None, []
        yield
    g.info = "Pronto. Anéis coloridos = pontos novos já classificados."


# =====================================================================
#  Perceptron
# =====================================================================

def perceptron(g):
    ang = random.uniform(0, math.pi)
    w_ver = (random.uniform(-0.3, 0.3), math.cos(ang), math.sin(ang))
    pts = []
    while len(pts) < 60:
        x, y = random.uniform(-0.95, 0.95), random.uniform(-0.95, 0.95)
        s = w_ver[0] + w_ver[1] * x + w_ver[2] * y
        if abs(s) >= 0.12:
            pts.append((x, y, 1 if s > 0 else -1))
    g.dados_p = pts
    g.w = [0.0, 0.0, 0.0]
    g.erros, atualizacoes = [], 0
    g.info = "Para cada ponto errado: w += classe * (1, x, y). Repete até não errar mais."
    yield
    for epoca in range(1000):
        erros = 0
        for x, y, c in pts:
            pred = 1 if g.w[0] + g.w[1] * x + g.w[2] * y > 0 else -1
            if pred != c:
                g.w = [g.w[0] + c, g.w[1] + c * x, g.w[2] + c * y]
                erros += 1
                atualizacoes += 1
                g.erros = [(a, b) for a, b, cc in pts
                           if (1 if g.w[0] + g.w[1] * a + g.w[2] * b > 0 else -1) != cc]
                g.info = f"Época {epoca + 1}: atualização nº {atualizacoes}, pontos errados agora: {len(g.erros)}"
                yield
        if erros == 0:
            break
    g.erros = []
    g.info = f"Convergiu: 100% de acerto após {atualizacoes} atualizações (dados linearmente separáveis)"


# =====================================================================
#  Gradiente descendente (função de Himmelblau, 4 mínimos)
# =====================================================================

def _himmelblau(x, y):
    return (x * x + y - 11) ** 2 + (x + y * y - 7) ** 2


def _grad_himmelblau(x, y):
    return (4 * x * (x * x + y - 11) + 2 * (x + y * y - 7), 2 * (x * x + y - 11) + 4 * y * (x + y * y - 7))


def _gd(g, momentum):
    x, y = random.uniform(-4, 4), random.uniform(-4, 4)
    vx = vy = 0.0
    lr = 0.0012 if momentum else 0.006
    g.caminho = [(x, y)]
    g.info = "Cada passo anda contra o gradiente: a função cai até um dos 4 mínimos."
    yield
    for k in range(900):
        gx, gy = _grad_himmelblau(x, y)
        if momentum:
            vx, vy = 0.9 * vx - lr * gx, 0.9 * vy - lr * gy
            dx, dy = vx, vy
        else:
            dx, dy = -lr * gx, -lr * gy
        n = math.hypot(dx, dy)
        if n > 0.4:
            dx, dy = dx / n * 0.4, dy / n * 0.4
        x, y = x + dx, y + dy
        g.caminho.append((x, y))
        g.info = f"Passo {k + 1}: ({x:.3f}, {y:.3f})  f = {_himmelblau(x, y):.4f}"
        yield
        if math.hypot(*_grad_himmelblau(x, y)) < 1e-3:
            break
    g.final = (x, y, _himmelblau(x, y))
    g.info = f"Parou em ({x:.3f}, {y:.3f}) com f = {_himmelblau(x, y):.5f}"


def gd_simples(g):
    return _gd(g, False)


def gd_momentum(g):
    return _gd(g, True)


# =====================================================================
#  Jogo da velha: minimax, alfa-beta e MCTS
# =====================================================================

LINHAS_V = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def vencedor(t):
    for a, b, c in LINHAS_V:
        if t[a] != " " and t[a] == t[b] == t[c]:
            return t[a]
    return None


def livres_v(t):
    return [i for i in range(9) if t[i] == " "]


def outro(j):
    return "O" if j == "X" else "X"


def posicao_aleatoria():
    while True:
        t = [" "] * 9
        vez = "X"
        for _ in range(random.choice([2, 3])):
            t[random.choice(livres_v(t))] = vez
            vez = outro(vez)
        if vencedor(t) is None:
            return t, vez


def _busca(g, vez, alfa, beta, poda):
    g.nos += 1
    yield
    v = vencedor(g.tab)
    if v:
        return 1 if v == "X" else -1
    livres = livres_v(g.tab)
    if not livres:
        return 0
    melhor = -2 if vez == "X" else 2
    for m in livres:
        g.tab[m] = vez
        g.hip.add(m)
        val = yield from _busca(g, outro(vez), alfa, beta, poda)
        g.tab[m] = " "
        g.hip.discard(m)
        if vez == "X":
            melhor = max(melhor, val)
            alfa = max(alfa, melhor)
        else:
            melhor = min(melhor, val)
            beta = min(beta, melhor)
        if poda and alfa >= beta:
            g.podas += 1
            break
    return melhor


def _ttt(g, poda):
    vez = g.vez
    g.nos, g.podas, g.hip = 0, 0, set()
    g.scores = {}
    alfa, beta = -2, 2
    melhor, mov = (-2 if vez == "X" else 2), None
    g.info = "Avalia todas as jogadas: X maximiza, O minimiza (+1 X vence, 0 empate, -1 O vence)."
    for m in livres_v(g.tab):
        g.tab[m] = vez
        g.hip = {m}
        val = yield from _busca(g, outro(vez), alfa, beta, poda)
        g.tab[m] = " "
        g.scores[m] = val
        if (vez == "X" and val > melhor) or (vez == "O" and val < melhor):
            melhor, mov = val, m
        if vez == "X":
            alfa = max(alfa, melhor)
        else:
            beta = min(beta, melhor)
    g.hip, g.melhor_mov, g.valor = set(), mov, melhor
    extra = f", {g.podas} podas" if poda else ""
    g.info = f"{vez} deve jogar na casa {mov + 1} (valor {melhor:+d}). Nós visitados: {g.nos}{extra}"


def minimax(g):
    return _ttt(g, False)


def alfa_beta(g):
    return _ttt(g, True)


class MNo:
    def __init__(self, tab, vez, pai=None, mov=None):
        self.tab, self.vez, self.pai, self.mov = tab, vez, pai, mov
        self.filhos = []
        self.pendentes = [] if vencedor(tab) else livres_v(tab)
        self.v, self.w = 0, 0.0


def _rollout(tab, vez):
    tab = list(tab)
    while True:
        w = vencedor(tab)
        if w:
            return w
        livres = livres_v(tab)
        if not livres:
            return None
        tab[random.choice(livres)] = vez
        vez = outro(vez)


def mcts(g, iteracoes=2000):
    raiz = MNo(list(g.tab), g.vez)
    g.stats = {}
    g.info = "Seleção (UCT) -> expansão -> simulação aleatória -> retropropagação, 2000 vezes."
    for it in range(iteracoes):
        no = raiz
        while not no.pendentes and no.filhos:
            no = max(no.filhos, key=lambda f: f.w / f.v + 1.41 * math.sqrt(math.log(no.v) / f.v))
        if no.pendentes:
            m = no.pendentes.pop(random.randrange(len(no.pendentes)))
            t = list(no.tab)
            t[m] = no.vez
            f = MNo(t, outro(no.vez), no, m)
            no.filhos.append(f)
            no = f
        res = _rollout(no.tab, no.vez)
        while no is not None:
            no.v += 1
            if res is None:
                no.w += 0.5
            elif no.pai is not None and res == outro(no.vez):      # quem jogou para chegar aqui venceu
                no.w += 1
            no = no.pai
        if it % 10 == 0 or it == iteracoes - 1:
            g.stats = {f.mov: (f.v, f.w / f.v) for f in raiz.filhos}
            g.info = f"Iteração {it + 1} de {iteracoes}"
            yield
    melhor = max(raiz.filhos, key=lambda f: f.v)
    g.melhor_mov = melhor.mov
    g.info = f"{g.vez} deve jogar na casa {melhor.mov + 1} (a mais visitada: {melhor.v} de {iteracoes} simulações)"


for _f, _m, _v in ((kmeans, "kmeans", 2), (knn, "knn", 3), (perceptron, "perceptron", 4), (gd_simples, "gd", 6),
                   (gd_momentum, "gd", 6), (minimax, "ttt", 8), (alfa_beta, "ttt", 8), (mcts, "ttt", 5)):
    _f.modo, _f.vel = _m, _v


class IA(Cena):
    titulo = "IA e aprendizado"
    vel_inicial = 3
    ajuda = ("TAB: escolher o algoritmo. R: nova instância aleatória do mesmo algoritmo.",
             "Jogo da velha: o computador analisa uma posição com 2 ou 3 jogadas já feitas.")
    algoritmos = [
        ("k-means (3 grupos)", kmeans, "O(n·k) por iteração"),
        ("k-NN (k = 5)", knn, "O(n) por consulta"),
        ("Perceptron", perceptron, "converge se separável"),
        ("Gradiente descendente", gd_simples, "O(passos)"),
        ("Gradiente com momentum", gd_momentum, "O(passos)"),
        ("Minimax (jogo da velha)", minimax, "O(b^d)"),
        ("Minimax com poda alfa-beta", alfa_beta, "O(b^(d/2)) no melhor caso"),
        ("MCTS / UCT (jogo da velha)", mcts, "O(iterações)"),
    ]

    def reiniciar(self):
        self.modo = "kmeans"
        self.pts, self.rot, self.cent, self.historico = [], [], [], []
        self.consultas, self.viz, self.atual_q = [], [], None
        self.dados_p, self.w, self.erros = [], [0, 0, 0], []
        self.caminho, self.mapa = [], getattr(self, "mapa", None)
        self.tab, self.vez, self.hip, self.stats, self.melhor_mov, self.scores = [" "] * 9, "X", set(), {}, None, {}
        self.gerador = None

    def iniciar(self, funcao):
        self.reiniciar()
        self.modo = funcao.modo
        self.vel = funcao.vel
        if self.modo == "ttt":
            self.tab, self.vez = posicao_aleatoria()
        self.comecar(funcao(self))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and self.alg_idx >= 0:
            self.selecionar(self.alg_idx)

    def desenhar_cena(self, tela):
        getattr(self, "_d_" + self.modo)(tela)

    def _d_kmeans(self, tela):
        for i, p in enumerate(self.pts):
            cor = PALETA[self.rot[i]] if self.rot and self.rot[i] is not None else BRANCO
            pygame.draw.circle(tela, cor, (int(p[0]), int(p[1])), 5)
        for j, c in enumerate(self.cent):
            pygame.draw.circle(tela, PALETA[j], (int(c[0]), int(c[1])), 13)
            pygame.draw.circle(tela, BRANCO, (int(c[0]), int(c[1])), 13, 3)

    def _d_knn(self, tela):
        cores = (AZUL, LARANJA)
        for p, c in zip(self.pts, self.rot):
            pygame.draw.circle(tela, cores[c], (int(p[0]), int(p[1])), 5)
        for q, pred, viz in self.consultas:
            pygame.draw.circle(tela, cores[pred], (int(q[0]), int(q[1])), 11, 3)
        if self.atual_q:
            for i in self.viz:
                pygame.draw.line(tela, AMARELO, self.atual_q, self.pts[i], 2)
            pygame.draw.circle(tela, BRANCO, (int(self.atual_q[0]), int(self.atual_q[1])), 11, 3)

    def _tela_xy(self, x, y):
        return (int((x + 1) / 2 * (LARGURA - 40) + 20), int(TOPO + 10 + (1 - (y + 1) / 2) * (ALTURA - TOPO - 20)))

    def _d_perceptron(self, tela):
        if not self.dados_p:
            return
        a, b, c = self.w
        if abs(c) > 1e-9:
            p1, p2 = self._tela_xy(-1.3, -(a - 1.3 * b) / c), self._tela_xy(1.3, -(a + 1.3 * b) / c)
            pygame.draw.line(tela, AMARELO, p1, p2, 3)
        elif abs(b) > 1e-9:
            x = -a / b
            pygame.draw.line(tela, AMARELO, self._tela_xy(x, -1.3), self._tela_xy(x, 1.3), 3)
        for x, y, cl in self.dados_p:
            p = self._tela_xy(x, y)
            pygame.draw.circle(tela, AZUL if cl > 0 else LARANJA, p, 6)
            if (x, y) in self.erros:
                pygame.draw.circle(tela, VERMELHO, p, 11, 2)

    def _mapa_himmelblau(self):
        W, H = 100, 54
        sup = pygame.Surface((W, H))
        for i in range(W):
            for j in range(H):
                x, y = -5 + 10 * i / W, 5 - 10 * j / H
                t = min(math.log(1 + _himmelblau(x, y)) / 7.5, 1)
                sup.set_at((i, j), cor_hsv(0.72 - 0.72 * t, 0.85, 0.35 + 0.5 * t))
        return pygame.transform.smoothscale(sup, (LARGURA, ALTURA - TOPO))

    def _d_gd(self, tela):
        if self.mapa is None:
            self.mapa = self._mapa_himmelblau()
        tela.blit(self.mapa, (0, TOPO))
        px = lambda x, y: (int((x + 5) / 10 * LARGURA), int(TOPO + (5 - y) / 10 * (ALTURA - TOPO)))
        for mx, my in ((3, 2), (-2.805, 3.131), (-3.779, -3.283), (3.584, -1.848)):
            pygame.draw.circle(tela, BRANCO, px(mx, my), 9, 2)
        if len(self.caminho) > 1:
            pygame.draw.lines(tela, BRANCO, False, [px(*p) for p in self.caminho], 2)
        if self.caminho:
            pygame.draw.circle(tela, AMARELO, px(*self.caminho[-1]), 7)

    def _d_ttt(self, tela):
        lado = 130
        x0, y0 = (LARGURA - 3 * lado) // 2, TOPO + (ALTURA - TOPO - 3 * lado) // 2
        for i in range(1, 3):
            pygame.draw.line(tela, CINZA, (x0 + i * lado, y0), (x0 + i * lado, y0 + 3 * lado), 3)
            pygame.draw.line(tela, CINZA, (x0, y0 + i * lado), (x0 + 3 * lado, y0 + i * lado), 3)
        for i in range(9):
            r, c = divmod(i, 3)
            cx, cy = x0 + c * lado + lado // 2, y0 + r * lado + lado // 2
            if self.melhor_mov == i and self.gerador is None:
                pygame.draw.rect(tela, (30, 90, 50), (x0 + c * lado + 4, y0 + r * lado + 4, lado - 8, lado - 8))
            if self.tab[i] != " ":
                cor = AMARELO if i in self.hip else BRANCO
                texto(tela, self.tab[i], cx, cy - 22, "t", cor, centro=True)
            elif i in self.stats:
                v, wr = self.stats[i]
                texto(tela, f"{v} visitas", cx, cy - 16, "p", CINZA, centro=True)
                texto(tela, f"{wr:.0%}", cx, cy + 2, "m", VERDE if wr > 0.6 else BRANCO, centro=True)
            elif i in self.scores:
                texto(tela, f"{self.scores[i]:+d}", cx, cy - 10, "m", VERDE if self.scores[i] * (1 if self.vez == 'X' else -1) > 0 else (BRANCO if self.scores[i] == 0 else VERMELHO), centro=True)
            else:
                texto(tela, i + 1, cx, cy - 8, "p", CINZA_ESC, centro=True)
        texto(tela, f"Vez de {self.vez}", x0 + 3 * lado + 30, y0 + 10, "g", BRANCO)


# =====================================================================
#  Caixeiro viajante
# =====================================================================

def comprimento(pts, tour):
    return sum(math.dist(pts[tour[i]], pts[tour[(i + 1) % len(tour)]]) for i in range(len(tour)))


def tsp_vizinho(g):
    pts = g.pts
    n = len(pts)
    tour, resto = [0], set(range(1, n))
    g.tour = list(tour)
    g.aberto = True
    g.info = "Sempre vai para a cidade não visitada mais próxima."
    yield
    while resto:
        prox = min(resto, key=lambda j: math.dist(pts[tour[-1]], pts[j]))
        resto.discard(prox)
        tour.append(prox)
        g.tour = list(tour)
        g.info = f"Visitadas {len(tour)} de {n} cidades, comprimento parcial {sum(math.dist(pts[tour[i]], pts[tour[i + 1]]) for i in range(len(tour) - 1)):.0f}"
        yield
    g.aberto = False
    g.melhor = list(tour)
    g.info = f"Rota completa: comprimento {comprimento(pts, tour):.0f} (rápida, mas pode ficar 25% acima do ótimo)"


def tsp_2opt(g):
    pts = g.pts
    n = len(pts)
    tour = list(range(n))
    random.shuffle(tour)
    g.tour = list(tour)
    g.aberto = False
    g.info = f"Rota aleatória: {comprimento(pts, tour):.0f}. 2-opt desfaz cruzamentos invertendo trechos."
    yield
    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(n - 1):
            for j in range(i + 2, n if i > 0 else n - 1):
                a, b = pts[tour[i]], pts[tour[i + 1]]
                c, d = pts[tour[j]], pts[tour[(j + 1) % n]]
                if math.dist(a, c) + math.dist(b, d) < math.dist(a, b) + math.dist(c, d) - 1e-9:
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    melhorou = True
                    g.tour = list(tour)
                    g.info = f"Troca arestas ({i},{i + 1}) e ({j},{(j + 1) % n}): comprimento {comprimento(pts, tour):.0f}"
                    yield
    g.melhor = list(tour)
    g.info = f"Ótimo local (nenhuma troca 2-opt melhora): {comprimento(pts, tour):.0f}"


def tsp_forca_bruta(g):
    pts = g.pts
    n = len(pts)
    melhor, melhor_l = None, math.inf
    g.aberto = False
    g.info = f"Testa as {math.factorial(n - 1)} ordens possíveis (cidade 0 fixa)."
    for perm in itertools.permutations(range(1, n)):
        tour = [0] + list(perm)
        l = comprimento(pts, tour)
        if l < melhor_l:
            melhor, melhor_l = tour, l
            g.melhor = list(melhor)
        g.tour = tour
        g.info = f"Melhor até agora: {melhor_l:.0f}   (testando rota {g.passos + 1} de {math.factorial(n - 1)})"
        yield
    g.tour = list(melhor)
    g.info = f"Ótimo global: {melhor_l:.0f}"


def tsp_recozimento(g):
    pts = g.pts
    n = len(pts)
    tour = list(range(n))
    random.shuffle(tour)
    atual = comprimento(pts, tour)
    g.melhor, melhor_l = list(tour), atual
    T = 250.0
    g.aberto = False
    g.tour = list(tour)
    for it in range(9000):
        i, j = sorted(random.sample(range(n), 2))
        novo = tour[:i] + tour[i:j + 1][::-1] + tour[j + 1:]
        l = comprimento(pts, novo)
        if l < atual or random.random() < math.exp((atual - l) / T):
            tour, atual = novo, l
            if atual < melhor_l:
                g.melhor, melhor_l = list(tour), atual
        T *= 0.9993
        if it % 10 == 0:
            g.tour = list(tour)
            g.info = f"Iteração {it}: T = {T:.1f}, atual {atual:.0f}, melhor {melhor_l:.0f} (aceita pioras com prob. e^(-Δ/T))"
            yield
    g.tour = list(g.melhor)
    g.info = f"Recozimento simulado terminou: melhor rota {melhor_l:.0f}"


def tsp_genetico(g):
    pts = g.pts
    n = len(pts)
    tam = 70
    pop = [random.sample(range(n), n) for _ in range(tam)]
    g.aberto = False
    fit = lambda t: comprimento(pts, t)

    def cruzar(a, b):                     # order crossover (OX)
        i, j = sorted(random.sample(range(n), 2))
        filho = [None] * n
        filho[i:j + 1] = a[i:j + 1]
        resto = [x for x in b if x not in filho[i:j + 1]]
        k = 0
        for p in range(n):
            if filho[p] is None:
                filho[p] = resto[k]
                k += 1
        return filho

    for ger in range(220):
        pop.sort(key=fit)
        g.melhor = list(pop[0])
        g.tour = list(pop[0])
        g.info = f"Geração {ger + 1}: melhor rota {fit(pop[0]):.0f}"
        yield
        nova = [list(p) for p in pop[:4]]                      # elitismo
        while len(nova) < tam:
            pa = min(random.sample(pop, 4), key=fit)           # torneio
            pb = min(random.sample(pop, 4), key=fit)
            f = cruzar(pa, pb)
            if random.random() < 0.3:
                x, y = random.sample(range(n), 2)
                f[x], f[y] = f[y], f[x]
            nova.append(f)
        pop = nova
    pop.sort(key=fit)
    g.melhor, g.tour = list(pop[0]), list(pop[0])
    g.info = f"Algoritmo genético terminou: melhor rota {fit(pop[0]):.0f}"


tsp_forca_bruta.n = 8
for _f in (tsp_vizinho, tsp_2opt, tsp_recozimento, tsp_genetico):
    _f.n = 22


class Caixeiro(Cena):
    titulo = "Caixeiro viajante"
    vel_inicial = 5
    ajuda = ("Visitar todas as cidades e voltar ao início pelo menor caminho. Azul = rota atual, verde = melhor rota.",
             "TAB: escolher o algoritmo. R: novas cidades.")
    algoritmos = [
        ("Vizinho mais próximo (guloso)", tsp_vizinho, "O(n²)"),
        ("2-opt (busca local)", tsp_2opt, "O(n²) por passada"),
        ("Força bruta (8 cidades)", tsp_forca_bruta, "O(n!)"),
        ("Recozimento simulado", tsp_recozimento, "heurística"),
        ("Algoritmo genético", tsp_genetico, "heurística"),
    ]

    def reiniciar(self, n=22):
        pts = []
        while len(pts) < n:
            p = (random.randint(50, LARGURA - 50), random.randint(TOPO + 40, ALTURA - 40))
            if all(math.dist(p, q) > 55 for q in pts):
                pts.append(p)
        self.pts = pts
        self.tour, self.melhor, self.aberto = [], [], False
        self.gerador = None

    def iniciar(self, funcao):
        self.reiniciar(getattr(funcao, "n", 22))
        self.comecar(funcao(self))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and self.alg_idx >= 0:
            self.selecionar(self.alg_idx)

    def desenhar_cena(self, tela):
        if len(self.melhor) > 2 and self.melhor != self.tour:
            pygame.draw.lines(tela, (40, 110, 60), True, [self.pts[i] for i in self.melhor], 2)
        if len(self.tour) > 1:
            pygame.draw.lines(tela, VERDE if self.terminou else AZUL, not self.aberto and len(self.tour) == len(self.pts),
                              [self.pts[i] for i in self.tour], 3)
        for i, p in enumerate(self.pts):
            pygame.draw.circle(tela, AMARELO if i == 0 else BRANCO, p, 7)
