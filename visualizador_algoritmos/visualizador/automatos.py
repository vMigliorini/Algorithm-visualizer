"""Autômatos e simulações: Jogo da Vida, formiga de Langton, autômatos 1D (regras 30 e 110),
passeio aleatório, Monte Carlo para estimar π e o conjunto de Mandelbrot."""
import math
import random
import re
from collections import Counter

import pygame

from .base import *

CEL = 10
COLS, LINS = 100, 54
Y0 = TOPO + 2

GOSPER_RLE = "24bo$22bobo$12b2o6b2o12b2o$11bo3bo4b2o12b2o$2o8bo5bo3b2o$2o8bo3bob2o4bobo$10bo5bo7bo$11bo3bo$12b2o!"
RPENTOMINO = [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)]
PLANADOR = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]


def rle_para_celulas(rle):
    """Decodifica um padrão RLE (formato usado pela comunidade do Jogo da Vida)."""
    celulas, r, c = [], 0, 0
    for n, ch in re.findall(r"(\d*)([bo$])", rle):
        n = int(n) if n else 1
        if ch == "$":
            r, c = r + n, 0
        elif ch == "o":
            celulas += [(r, c + k) for k in range(n)]
            c += n
        else:
            c += n
    return celulas


def vida_passo(vivas, R, C, torus=True):
    cont = Counter()
    for r, c in vivas:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr or dc:
                    cont[((r + dr) % R, (c + dc) % C) if torus else (r + dr, c + dc)] += 1
    novo = {p for p, n in cont.items() if n == 3 or (n == 2 and p in vivas)}
    if not torus:
        novo = {(r, c) for r, c in novo if 0 <= r < R and 0 <= c < C}
    return novo


def _vida(g, inicial, torus=True):
    g.vivas = set(inicial)
    g.geracao = 0
    while True:
        g.info = f"Geração {g.geracao}   população {len(g.vivas)}"
        yield
        g.vivas = vida_passo(g.vivas, g.R, g.C, torus)
        g.geracao += 1


def vida_aleatoria(g):
    return _vida(g, {(r, c) for r in range(g.R) for c in range(g.C) if random.random() < 0.25})


def vida_rpentomino(g):
    return _vida(g, {(g.R // 2 + r - 1, g.C // 2 + c - 1) for r, c in RPENTOMINO})


def vida_canhao(g):
    return _vida(g, {(r + 3, c + 3) for r, c in rle_para_celulas(GOSPER_RLE)}, torus=False)


def vida_planadores(g):
    base = [(r + 3, c + 3) for r, c in PLANADOR]
    base += [(r + 30, c + 70) for r, c in PLANADOR]
    base += [(r + 15, c + 40) for r, c in PLANADOR]
    return _vida(g, base)


def formiga(g):
    """Formiga de Langton: em casa branca vira à direita; em preta, à esquerda; sempre inverte a cor e avança."""
    g.pretas = set()
    r, c, d = g.R // 2, g.C // 2, 0           # d: 0 cima, 1 direita, 2 baixo, 3 esquerda
    DR, DC = (-1, 0, 1, 0), (0, 1, 0, -1)
    n = 0
    while True:
        g.formiga = (r, c)
        g.info = f"Passo {n}   casas pretas: {len(g.pretas)}   (a 'rodovia' aparece perto do passo 10.000)"
        yield
        if (r, c) in g.pretas:
            g.pretas.discard((r, c))
            d = (d - 1) % 4
        else:
            g.pretas.add((r, c))
            d = (d + 1) % 4
        r, c = (r + DR[d]) % g.R, (c + DC[d]) % g.C
        n += 1


def _regra(g, numero):
    W = g.largura_ca
    g.sup = pygame.Surface((W * 5, g.linhas_ca * 4))
    g.sup.fill((8, 8, 14))
    linha = [0] * W
    linha[W // 2] = 1
    g.geracoes = [linha]
    for k in range(g.linhas_ca):
        for i, v in enumerate(linha):
            if v:
                g.sup.fill(cor_hsv(0.55 + k / g.linhas_ca * 0.4, 0.6, 0.95), (i * 5, k * 4, 5, 4))
        g.info = f"Regra {numero}: cada célula olha a si e aos 2 vizinhos da linha de cima. Linha {k + 1}"
        yield
        linha = [(numero >> (4 * linha[i - 1] + 2 * linha[i] + linha[(i + 1) % W])) & 1 for i in range(W)]
        g.geracoes.append(linha)
    g.info = f"Regra {numero} concluída"


def regra30(g):
    return _regra(g, 30)


def regra110(g):
    return _regra(g, 110)


def passeio(g):
    """Vários passeios aleatórios 2D: a distância típica cresce como a raiz de n."""
    n_w = g.n_walkers
    g.sup = pygame.Surface((LARGURA, ALTURA - TOPO))
    g.sup.fill((8, 8, 14))
    cx, cy = LARGURA // 2, (ALTURA - TOPO) // 2
    pos = [[0, 0] for _ in range(n_w)]
    g.walkers = pos
    cores = [cor_hsv(i / n_w) for i in range(n_w)]
    n = 0
    while True:
        for i, p in enumerate(pos):
            ox, oy = p
            dx, dy = random.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
            p[0], p[1] = ox + dx, oy + dy
            if abs(p[0]) * 6 > cx - 6 or abs(p[1]) * 6 > cy - 6:        # reflete nas bordas
                p[0], p[1] = ox, oy
            pygame.draw.line(g.sup, cores[i], (cx + ox * 6, cy + oy * 6), (cx + p[0] * 6, cy + p[1] * 6), 1)
        n += 1
        g.msd = sum(p[0] ** 2 + p[1] ** 2 for p in pos) / n_w
        g.info = f"Passo {n}   distância² média = {g.msd:.0f}   (teoria: = nº de passos)"
        g.cores_w = cores
        yield


def monte_carlo(g):
    """Estima π jogando pontos num quadrado e contando os que caem dentro do círculo."""
    lado = ALTURA - TOPO - 20
    g.lado_mc = lado
    g.sup = pygame.Surface((lado, lado))
    g.sup.fill((8, 8, 14))
    dentro = total = 0
    while True:
        for _ in range(20):
            x, y = random.random(), random.random()
            if x * x + y * y <= 1:
                dentro += 1
                cor = VERDE
            else:
                cor = VERMELHO
            total += 1
            g.sup.set_at((int(x * (lado - 1)), int((1 - y) * (lado - 1))), cor)
        g.pi_est = 4 * dentro / total
        g.info = f"{total} pontos   π ≈ {g.pi_est:.5f}   (erro {abs(g.pi_est - math.pi):.5f})"
        yield


def mandelbrot(g):
    W, H, MAXIT = 250, 136, 60
    g.sup = pygame.Surface((W, H))
    g.sup.fill((8, 8, 14))
    g.dentro = 0
    for px in range(W):
        for py in range(H):
            cr = -2.2 + px / W * 3.2
            ci = -0.87 + py / H * 1.74
            zr = zi = 0.0
            k = 0
            while k < MAXIT and zr * zr + zi * zi <= 4:
                zr, zi = zr * zr - zi * zi + cr, 2 * zr * zi + ci
                k += 1
            if k == MAXIT:
                g.dentro += 1
                g.sup.set_at((px, py), (0, 0, 0))
            else:
                g.sup.set_at((px, py), cor_hsv(0.65 + k / 22, 0.8, 0.95))
        g.info = f"Coluna {px + 1} de {W}: cada pixel itera z = z² + c até escapar (|z| > 2) ou atingir {MAXIT}"
        yield
    g.info = f"Concluído: {g.dentro / (W * H):.0%} dos pontos nunca escapam (preto = dentro do conjunto)"


for _f, _m, _v in ((vida_aleatoria, "vida", 4), (vida_rpentomino, "vida", 5), (vida_canhao, "vida", 5),
                   (vida_planadores, "vida", 4), (formiga, "formiga", 9), (regra30, "ca1d", 5), (regra110, "ca1d", 5),
                   (passeio, "passeio", 8), (monte_carlo, "mc", 6), (mandelbrot, "mandel", 6)):
    _f.modo, _f.vel = _m, _v


class Automatos(Cena):
    titulo = "Autômatos e simulações"
    vel_inicial = 4
    R, C = LINS, COLS
    largura_ca, linhas_ca = 200, 136
    n_walkers = 12
    ajuda = ("Simulações abertas: rodam até você trocar de algoritmo. Use CIMA/BAIXO para acelerar.",
             "TAB: escolher a simulação. R: reiniciar a mesma com novas condições iniciais.")
    algoritmos = [
        ("Jogo da Vida: aleatório", vida_aleatoria, "O(células vivas)"),
        ("Jogo da Vida: R-pentômino", vida_rpentomino, "caos a partir de 5 células"),
        ("Jogo da Vida: canhão de Gosper", vida_canhao, "emite um planador a cada 30 gerações"),
        ("Jogo da Vida: planadores", vida_planadores, "O(células vivas)"),
        ("Formiga de Langton", formiga, "O(1) por passo"),
        ("Autômato 1D: Regra 30", regra30, "O(n) por geração"),
        ("Autômato 1D: Regra 110", regra110, "Turing-completo"),
        ("Passeio aleatório 2D", passeio, "distância ~ √n"),
        ("Monte Carlo: estimando π", monte_carlo, "erro ~ 1/√n"),
        ("Conjunto de Mandelbrot", mandelbrot, "O(pixels · iterações)"),
    ]

    def reiniciar(self):
        self.modo = "vida"
        self.vivas, self.pretas, self.formiga = set(), set(), (0, 0)
        self.sup, self.geracao = None, 0
        self.gerador = None

    def iniciar(self, funcao):
        self.reiniciar()
        self.modo = funcao.modo
        self.vel = funcao.vel
        self.comecar(funcao(self))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and self.alg_idx >= 0:
            self.selecionar(self.alg_idx)

    def desenhar_cena(self, tela):
        getattr(self, "_d_" + self.modo)(tela)

    def _d_vida(self, tela):
        for r, c in self.vivas:
            pygame.draw.rect(tela, VERDE, (c * CEL, Y0 + r * CEL, CEL - 1, CEL - 1))

    def _d_formiga(self, tela):
        for r, c in self.pretas:
            pygame.draw.rect(tela, BRANCO, (c * CEL, Y0 + r * CEL, CEL - 1, CEL - 1))
        r, c = self.formiga
        pygame.draw.rect(tela, VERMELHO, (c * CEL, Y0 + r * CEL, CEL - 1, CEL - 1))

    def _d_ca1d(self, tela):
        if self.sup:
            tela.blit(self.sup, ((LARGURA - self.sup.get_width()) // 2, TOPO + 4))

    def _d_passeio(self, tela):
        if self.sup:
            tela.blit(self.sup, (0, TOPO))
            cx, cy = LARGURA // 2, TOPO + (ALTURA - TOPO) // 2
            for p, cor in zip(self.walkers, self.cores_w):
                pygame.draw.circle(tela, BRANCO, (cx + p[0] * 6, cy + p[1] * 6), 3)
            pygame.draw.circle(tela, BRANCO, (cx, cy), 6, 1)

    def _d_mc(self, tela):
        if self.sup:
            lado = self.lado_mc
            x0, y0 = (LARGURA - lado) // 2, TOPO + 10
            tela.blit(self.sup, (x0, y0))
            pygame.draw.rect(tela, CINZA, (x0, y0, lado, lado), 1)
            pygame.draw.circle(tela, AMARELO, (x0, y0 + lado), lado - 1, 2, draw_top_right=True)

    def _d_mandel(self, tela):
        if self.sup:
            tela.blit(pygame.transform.scale(self.sup, (LARGURA, ALTURA - TOPO)), (0, TOPO))
