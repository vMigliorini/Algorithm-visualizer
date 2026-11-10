"""Geometria computacional: fecho convexo (Graham, Jarvis, QuickHull), par de pontos mais
próximo (dividir e conquistar), varredura de linha (interseção de segmentos) e Bresenham."""
import math
import random

import pygame

from .base import *

CEL, COLS, LINS = 20, 49, 27


def cross(o, a, b):
    """Produto vetorial (a-o) x (b-o) em coordenadas matemáticas (y para cima)."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _m(p):
    """Converte de coordenadas de tela (y para baixo) para matemáticas (y para cima)."""
    return (p[0], -p[1])


def _gerar_pontos(n=30):
    pts = []
    while len(pts) < n:
        p = (random.randint(40, LARGURA - 40), random.randint(TOPO + 30, ALTURA - 30))
        if all(math.dist(p, q) > 22 for q in pts):
            pts.append(p)
    return pts


def _ordenar_casco(pts, indices):
    cx = sum(pts[i][0] for i in indices) / len(indices)
    cy = sum(pts[i][1] for i in indices) / len(indices)
    return sorted(indices, key=lambda i: math.atan2(pts[i][1] - cy, pts[i][0] - cx))


def _casco_estrito(pts, idx):
    """Remove pontos colineares de um casco (mantém só os vértices)."""
    k = len(idx)
    return [idx[i] for i in range(k)
            if cross(_m(pts[idx[i - 1]]), _m(pts[idx[i]]), _m(pts[idx[(i + 1) % k]])) != 0]


# ---------------------------------------------------------------------
#  Fecho convexo
# ---------------------------------------------------------------------

def graham(g):
    g.pts = _gerar_pontos()
    P = [_m(p) for p in g.pts]
    n = len(P)
    pivo = min(range(n), key=lambda i: (P[i][1], P[i][0]))
    g.dest = {pivo: ROXO}
    g.info = "Ordena por ângulo em torno do ponto mais baixo e mantém só curvas à esquerda."
    yield
    resto = sorted((i for i in range(n) if i != pivo),
                   key=lambda i: (math.atan2(P[i][1] - P[pivo][1], P[i][0] - P[pivo][0]),
                                  (P[i][0] - P[pivo][0]) ** 2 + (P[i][1] - P[pivo][1]) ** 2))
    pilha = [pivo]
    for i in resto:
        g.dest[i] = AMARELO
        g.linhas = [(g.pts[pivo], g.pts[i], CINZA_ESC)]
        g.casco_parcial = [g.pts[k] for k in pilha] + [g.pts[i]]
        yield
        while len(pilha) >= 2 and cross(P[pilha[-2]], P[pilha[-1]], P[i]) <= 0:
            g.dest[pilha[-1]] = VERMELHO
            g.casco_parcial = [g.pts[k] for k in pilha] + [g.pts[i]]
            yield
            g.dest.pop(pilha[-1], None)
            pilha.pop()
        pilha.append(i)
        g.dest[i] = VERDE
        g.casco_parcial = [g.pts[k] for k in pilha]
        yield
    pilha = _casco_estrito(g.pts, pilha)
    g.casco = [g.pts[i] for i in pilha]
    g.casco_idx = set(pilha)
    g.linhas, g.casco_parcial, g.fechado = [], [], True
    g.dest = {i: VERDE for i in pilha}
    g.info = f"Fecho convexo com {len(pilha)} vértices"


def jarvis(g):
    g.pts = _gerar_pontos()
    P = [_m(p) for p in g.pts]
    n = len(P)
    ini = min(range(n), key=lambda i: (P[i][0], P[i][1]))
    hull, p = [], ini
    g.info = "Embrulho de presente: a partir de um vértice, escolhe o ponto mais 'externo' e repete."
    d2 = lambda a, b: (P[a][0] - P[b][0]) ** 2 + (P[a][1] - P[b][1]) ** 2
    while True:
        hull.append(p)
        g.dest = {k: VERDE for k in hull}
        g.casco_parcial = [g.pts[k] for k in hull]
        q = (p + 1) % n
        for r in range(n):
            if r == p:
                continue
            g.linhas = [(g.pts[p], g.pts[q], VERDE), (g.pts[p], g.pts[r], AMARELO)]
            yield
            c = cross(P[p], P[q], P[r])
            if c < 0 or (c == 0 and d2(p, r) > d2(p, q)):
                q = r
        p = q
        if p == ini:
            break
    hull = _casco_estrito(g.pts, hull)
    g.casco = [g.pts[i] for i in hull]
    g.casco_idx = set(hull)
    g.linhas, g.casco_parcial, g.fechado = [], [], True
    g.dest = {i: VERDE for i in hull}
    g.info = f"Fecho convexo com {len(hull)} vértices"


def quickhull(g):
    g.pts = _gerar_pontos()
    P = [_m(p) for p in g.pts]
    n = len(P)
    A = min(range(n), key=lambda i: (P[i][0], P[i][1]))
    B = max(range(n), key=lambda i: (P[i][0], P[i][1]))
    hull = {A, B}
    g.dest = {A: VERDE, B: VERDE}
    g.linhas = [(g.pts[A], g.pts[B], AMARELO)]
    g.info = "Divide pelos extremos esquerdo/direito; o ponto mais distante da reta vira vértice."
    yield

    def achar(a, b, idx):
        if not idx:
            return
        c = max(idx, key=lambda i: cross(P[a], P[b], P[i]))
        hull.add(c)
        g.dest[c] = VERDE
        g.linhas = [(g.pts[a], g.pts[c], AMARELO), (g.pts[c], g.pts[b], AMARELO), (g.pts[a], g.pts[b], CINZA_ESC)]
        for i in idx:
            if i != c:
                g.dest.setdefault(i, AZUL)
        yield
        for i in idx:
            if g.dest.get(i) == AZUL:
                g.dest.pop(i)
        s1 = [i for i in idx if cross(P[a], P[c], P[i]) > 0]
        s2 = [i for i in idx if cross(P[c], P[b], P[i]) > 0]
        yield from achar(a, c, s1)
        yield from achar(c, b, s2)

    esq = [i for i in range(n) if cross(P[A], P[B], P[i]) > 0]
    dir_ = [i for i in range(n) if cross(P[B], P[A], P[i]) > 0]
    yield from achar(A, B, esq)
    yield from achar(B, A, dir_)
    ordem = _ordenar_casco(g.pts, list(hull))
    g.casco = [g.pts[i] for i in ordem]
    g.casco_idx = set(ordem)
    g.linhas, g.casco_parcial, g.fechado = [], [], True
    g.dest = {i: VERDE for i in ordem}
    g.info = f"Fecho convexo com {len(ordem)} vértices"


# ---------------------------------------------------------------------
#  Par de pontos mais próximo (dividir e conquistar)
# ---------------------------------------------------------------------

def par_mais_proximo(g):
    g.pts = _gerar_pontos(32)
    pts = g.pts
    ordem = sorted(range(len(pts)), key=lambda i: pts[i])
    melhor = [math.inf, None]
    g.info = "Divide ao meio por x, resolve cada lado e examina só a faixa central."

    def testar(a, b):
        d = math.dist(pts[a], pts[b])
        if d < melhor[0]:
            melhor[0], melhor[1] = d, (a, b)
            g.melhor_par = (pts[a], pts[b])

    def rec(lo, hi):
        if hi - lo <= 3:
            for a in range(lo, hi):
                for b in range(a + 1, hi):
                    g.linhas = [(pts[ordem[a]], pts[ordem[b]], AMARELO)]
                    testar(ordem[a], ordem[b])
                    yield
            return
        mid = (lo + hi) // 2
        xm = pts[ordem[mid]][0]
        g.divisoria, g.faixa = xm, None
        g.dest = {ordem[k]: (AZUL if k < mid else LARANJA) for k in range(lo, hi)}
        yield
        yield from rec(lo, mid)
        yield from rec(mid, hi)
        d = melhor[0]
        faixa = sorted((ordem[k] for k in range(lo, hi) if abs(pts[ordem[k]][0] - xm) < d), key=lambda i: pts[i][1])
        g.divisoria, g.faixa = xm, (xm - d, xm + d)
        g.dest = {i: AMARELO for i in faixa}
        yield
        for a in range(len(faixa)):
            for b in range(a + 1, len(faixa)):
                if pts[faixa[b]][1] - pts[faixa[a]][1] >= melhor[0]:
                    break
                g.linhas = [(pts[faixa[a]], pts[faixa[b]], AMARELO)]
                testar(faixa[a], faixa[b])
                yield

    yield from rec(0, len(pts))
    g.linhas, g.divisoria, g.faixa, g.dest = [], None, None, {}
    g.par_final = melhor[1]
    g.distancia = melhor[0]
    g.info = f"Par mais próximo a {melhor[0]:.1f} px de distância (linha verde)"


# ---------------------------------------------------------------------
#  Varredura de linha: interseções entre segmentos
# ---------------------------------------------------------------------

def _orient(a, b, c):
    v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return (v > 0) - (v < 0)


def segmentos_cruzam(s, t):
    a, b = s
    c, d = t
    o1, o2, o3, o4 = _orient(a, b, c), _orient(a, b, d), _orient(c, d, a), _orient(c, d, b)
    if o1 != o2 and o3 != o4:
        return True
    return False


def _ponto_cruzamento(s, t):
    (x1, y1), (x2, y2) = s
    (x3, y3), (x4, y4) = t
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return (x1, y1)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return (px, py)


def varredura(g):
    g.segs = []
    for _ in range(9):
        x1 = random.randint(40, 800)
        g.segs.append(((x1, random.randint(TOPO + 20, ALTURA - 20)),
                       (x1 + random.randint(80, 220), random.randint(TOPO + 20, ALTURA - 20))))
    eventos = sorted([(s[0][0], 0, i) for i, s in enumerate(g.segs)] + [(s[1][0], 1, i) for i, s in enumerate(g.segs)])
    ativos, g.cruzamentos = [], []
    g.estado_seg = {}
    g.info = "Uma reta vertical varre da esquerda p/ direita; só segmentos ativos ao mesmo tempo podem se cruzar."
    for x, tipo, i in eventos:
        g.x_varredura = x
        if tipo == 0:
            g.estado_seg[i] = AZUL
            for j in ativos:
                if segmentos_cruzam(g.segs[i], g.segs[j]):
                    g.cruzamentos.append((min(i, j), max(i, j), _ponto_cruzamento(g.segs[i], g.segs[j])))
                    g.estado_seg[i] = g.estado_seg[j] = VERMELHO
            ativos.append(i)
        else:
            ativos.remove(i)
            g.estado_seg[i] = CINZA_ESC
        g.info = f"Segmentos ativos: {len(ativos)}   cruzamentos encontrados: {len(g.cruzamentos)}"
        yield
    g.x_varredura = None
    g.info = f"{len(g.cruzamentos)} cruzamentos entre {len(g.segs)} segmentos"


# ---------------------------------------------------------------------
#  Rasterização (grade de pixels grandes)
# ---------------------------------------------------------------------

def bresenham(g):
    x0, y0 = random.randint(1, COLS - 2), random.randint(1, LINS - 2)
    x1, y1 = random.randint(1, COLS - 2), random.randint(1, LINS - 2)
    g.reta = ((x0, y0), (x1, y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    g.pixels = []
    g.info = f"De ({x0},{y0}) até ({x1},{y1}): só somas e comparações de inteiros, sem divisão."
    x, y = x0, y0
    while True:
        g.pixels.append((x, y))
        yield
        if (x, y) == (x1, y1):
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    g.info = f"{len(g.pixels)} pixels desenhados (= max(|dx|, |dy|) + 1)"


def circulo_ponto_medio(g):
    cx, cy = random.randint(14, COLS - 15), random.randint(8, LINS - 9)
    r = random.randint(5, 8)
    g.reta = None
    g.centro_circ, g.raio = (cx, cy), r
    g.pixels = []
    g.info = f"Círculo de raio {r}: calcula 1/8 do arco e espelha nos 8 octantes."
    x, y = r, 0
    d = 1 - r
    while x >= y:
        for px, py in ((x, y), (y, x), (-x, y), (-y, x), (-x, -y), (-y, -x), (x, -y), (y, -x)):
            g.pixels.append((cx + px, cy + py))
        yield
        y += 1
        if d < 0:
            d += 2 * y + 1
        else:
            x -= 1
            d += 2 * (y - x) + 1
    g.info = f"{len(set(g.pixels))} pixels distintos"


for _f, _m_ in ((graham, "casco"), (jarvis, "casco"), (quickhull, "casco"), (par_mais_proximo, "par"),
                (varredura, "varredura"), (bresenham, "raster"), (circulo_ponto_medio, "raster")):
    _f.modo = _m_


class Geometria(Cena):
    titulo = "Geometria computacional"
    vel_inicial = 4
    ajuda = ("Pontos novos a cada execução. Verde = faz parte do resultado, amarelo = em teste, vermelho = descartado.",
             "TAB: escolher o algoritmo. R: nova instância.")
    algoritmos = [
        ("Fecho convexo: Graham Scan", graham, "O(n log n)"),
        ("Fecho convexo: Jarvis March", jarvis, "O(n·h)"),
        ("Fecho convexo: QuickHull", quickhull, "O(n log n) médio"),
        ("Par de pontos mais próximo", par_mais_proximo, "O(n log n)"),
        ("Varredura de linha (interseções)", varredura, "O(n²) neste modelo simples"),
        ("Bresenham: reta", bresenham, "O(n)"),
        ("Bresenham: círculo (ponto médio)", circulo_ponto_medio, "O(r)"),
    ]

    def reiniciar(self):
        self.modo = "casco"
        self.pts, self.linhas, self.dest = [], [], {}
        self.casco, self.casco_parcial, self.fechado, self.casco_idx = [], [], False, set()
        self.divisoria, self.faixa, self.melhor_par, self.par_final = None, None, None, None
        self.segs, self.cruzamentos, self.estado_seg, self.x_varredura = [], [], {}, None
        self.pixels, self.reta, self.centro_circ, self.raio = [], None, None, 0
        self.gerador = None

    def iniciar(self, funcao):
        self.reiniciar()
        self.modo = funcao.modo
        self.comecar(funcao(self))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and self.alg_idx >= 0:
            self.selecionar(self.alg_idx)

    def desenhar_cena(self, tela):
        if self.modo == "raster":
            self._desenhar_raster(tela)
        elif self.modo == "varredura":
            self._desenhar_varredura(tela)
        else:
            self._desenhar_pontos(tela)

    def _desenhar_pontos(self, tela):
        if self.faixa:
            r = pygame.Rect(self.faixa[0], TOPO + 1, self.faixa[1] - self.faixa[0], ALTURA - TOPO)
            s = pygame.Surface(r.size)
            s.set_alpha(60)
            s.fill(AMARELO)
            tela.blit(s, r)
        if self.divisoria is not None:
            pygame.draw.line(tela, CINZA, (self.divisoria, TOPO), (self.divisoria, ALTURA), 1)
        if len(self.casco_parcial) > 1:
            pygame.draw.lines(tela, VERDE, self.fechado, self.casco_parcial, 2)
        if self.fechado and len(self.casco) > 2:
            pygame.draw.polygon(tela, VERDE, self.casco, 3)
        for a, b, cor in self.linhas:
            pygame.draw.line(tela, cor, a, b, 2)
        if self.melhor_par and not self.par_final:
            pygame.draw.line(tela, VERDE, *self.melhor_par, 3)
        if self.par_final:
            a, b = self.par_final
            pygame.draw.line(tela, VERDE, self.pts[a], self.pts[b], 4)
        for i, p in enumerate(self.pts):
            pygame.draw.circle(tela, self.dest.get(i, BRANCO), p, 6)

    def _desenhar_varredura(self, tela):
        for i, (a, b) in enumerate(self.segs):
            cor = self.estado_seg.get(i, (110, 110, 125))
            pygame.draw.line(tela, cor, a, b, 3)
            pygame.draw.circle(tela, cor, a, 4)
            pygame.draw.circle(tela, cor, b, 4)
        for _, _, p in self.cruzamentos:
            pygame.draw.circle(tela, VERMELHO, (int(p[0]), int(p[1])), 7, 3)
        if self.x_varredura is not None:
            pygame.draw.line(tela, AMARELO, (self.x_varredura, TOPO), (self.x_varredura, ALTURA), 2)

    def _desenhar_raster(self, tela):
        x0, y0 = (LARGURA - COLS * CEL) // 2, TOPO + 2
        for c in range(COLS + 1):
            pygame.draw.line(tela, (28, 28, 38), (x0 + c * CEL, y0), (x0 + c * CEL, y0 + LINS * CEL))
        for r in range(LINS + 1):
            pygame.draw.line(tela, (28, 28, 38), (x0, y0 + r * CEL), (x0 + COLS * CEL, y0 + r * CEL))
        centro = lambda p: (x0 + p[0] * CEL + CEL // 2, y0 + p[1] * CEL + CEL // 2)
        if self.reta:
            pygame.draw.line(tela, CINZA, centro(self.reta[0]), centro(self.reta[1]), 1)
        if self.centro_circ:
            pygame.draw.circle(tela, CINZA, centro(self.centro_circ), self.raio * CEL, 1)
        for k, (px, py) in enumerate(self.pixels):
            cor = AMARELO if k >= len(self.pixels) - 8 and self.gerador is not None else AZUL
            pygame.draw.rect(tela, cor, (x0 + px * CEL + 1, y0 + py * CEL + 1, CEL - 2, CEL - 2))
