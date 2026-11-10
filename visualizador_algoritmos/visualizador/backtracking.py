"""Backtracking: N-Rainhas, Sudoku (simples e MRV), passeio do cavaleiro, soma de subconjuntos, permutações."""
import random

import pygame

from .base import *


def _rainhas(g, linha):
    n = g.NQ
    if linha == n:
        return True
    for col in range(n):
        ok = all(g.rainhas[i] != col and abs(g.rainhas[i] - col) != linha - i
                 for i in range(linha))
        g.rainhas[linha] = col
        g.atual = (linha, col, ok)
        yield
        if ok:
            if (yield from _rainhas(g, linha + 1)):
                return True
        g.rainhas[linha] = None
    return False


def n_rainhas(g):
    ok = yield from _rainhas(g, 0)
    g.atual = None
    g.info = "Solução encontrada!" if ok else "Sem solução"


def _sudoku(g):
    for r in range(9):
        for c in range(9):
            if g.sud[r][c] == 0:
                for v in range(1, 10):
                    if g.valido(r, c, v):
                        g.sud[r][c] = v
                        g.atual = (r, c)
                        yield
                        if (yield from _sudoku(g)):
                            return True
                        g.sud[r][c] = 0
                g.atual = (r, c)
                yield
                return False
    return True


def sudoku(g):
    ok = yield from _sudoku(g)
    g.atual = None
    g.info = "Resolvido!" if ok else "Sem solução"


# ---------------------------------------------------------------------
#  Problemas adicionais
# ---------------------------------------------------------------------

PUZZLE = ["53..7....",
          "6..195...",
          ".98....6.",
          "8...6...3",
          "4..8.3..1",
          "7...2...6",
          ".6....28.",
          "...419..5",
          "....8..79"]

MOVIMENTOS_CAVALO = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]


def _sudoku_mrv(g):
    """Sudoku com a heurística MRV: sempre preenche a célula com MENOS candidatos."""
    melhor = None
    for r in range(9):
        for c in range(9):
            if g.sud[r][c] == 0:
                cands = [v for v in range(1, 10) if g.valido(r, c, v)]
                if not cands:
                    g.atual = (r, c)
                    yield
                    return False
                if melhor is None or len(cands) < len(melhor[2]):
                    melhor = (r, c, cands)
    if melhor is None:
        return True
    r, c, cands = melhor
    for v in cands:
        g.sud[r][c] = v
        g.atual = (r, c)
        yield
        if (yield from _sudoku_mrv(g)):
            return True
    g.sud[r][c] = 0
    return False


def sudoku_mrv(g):
    ok = yield from _sudoku_mrv(g)
    g.atual = None
    g.info = f"Resolvido em {g.passos + 1} passos (compare com o backtracking simples)" if ok else "Sem solução"


def _cavalo(g, r, c):
    N = g.KN
    g.trilha.append((r, c))
    g.visitadas.add((r, c))
    yield
    if len(g.trilha) == N * N:
        return True
    for dr, dc in MOVIMENTOS_CAVALO:
        nr, nc = r + dr, c + dc
        if 0 <= nr < N and 0 <= nc < N and (nr, nc) not in g.visitadas:
            if (yield from _cavalo(g, nr, nc)):
                return True
    g.visitadas.discard((r, c))
    g.trilha.pop()
    yield
    return False


def cavalo_bruto(g):
    ok = yield from _cavalo(g, 0, 0)
    g.info = f"Passeio completo ({g.KN * g.KN} casas)" if ok else "Sem passeio a partir do canto"


def cavalo_warnsdorff(g):
    """Heurística de Warnsdorff: vá sempre para a casa com MENOS saídas livres (sem backtracking)."""
    N = g.KN
    r, c = 0, 0
    g.trilha.append((r, c))
    g.visitadas.add((r, c))
    yield

    def saidas(a, b):
        return [(a + dr, b + dc) for dr, dc in MOVIMENTOS_CAVALO
                if 0 <= a + dr < N and 0 <= b + dc < N and (a + dr, b + dc) not in g.visitadas]

    while len(g.trilha) < N * N:
        opcoes = saidas(r, c)
        if not opcoes:
            g.info = "Travou (a heurística não garante solução em todos os casos)"
            return
        r, c = min(opcoes, key=lambda p: (len(saidas(*p)), p))
        g.trilha.append((r, c))
        g.visitadas.add((r, c))
        yield
    g.info = f"Passeio completo em {N * N} movimentos, sem nenhum retrocesso"


def subset_sum(g):
    nums, alvo = g.nums, g.alvo_soma
    n = len(nums)
    g.sel = [None] * n

    def bt(i, soma):
        g.soma, g.pos_i = soma, i
        yield
        if soma == alvo:
            return True
        if i == n or soma > alvo:                 # poda: números positivos
            return False
        g.sel[i] = True
        if (yield from bt(i + 1, soma + nums[i])):
            return True
        g.sel[i] = False
        if (yield from bt(i + 1, soma)):
            return True
        g.sel[i] = None
        return False

    ok = yield from bt(0, 0)
    g.pos_i = None
    escolhidos = [nums[i] for i in range(n) if g.sel[i]]
    g.info = (f"Achou: {' + '.join(map(str, escolhidos))} = {alvo}" if ok else "Nenhum subconjunto soma o alvo")


def permutacoes(g):
    n = 4
    atual, usado = [], [False] * n

    def bt():
        g.perm_atual = list(atual)
        yield
        if len(atual) == n:
            g.perms.append(tuple(atual))
            return
        for x in range(n):
            if not usado[x]:
                usado[x] = True
                atual.append(x + 1)
                yield from bt()
                atual.pop()
                usado[x] = False

    yield from bt()
    g.perm_atual = []
    g.info = f"{len(g.perms)} permutações geradas (4! = 24)"


n_rainhas.modo = "rainhas"
sudoku.modo = "sudoku"
sudoku_mrv.modo = "sudoku"
cavalo_bruto.modo = "cavalo"
cavalo_bruto.tam = 5
cavalo_bruto.vel = 9
cavalo_warnsdorff.modo = "cavalo"
cavalo_warnsdorff.tam = 8
cavalo_warnsdorff.vel = 3
subset_sum.modo = "subset"
subset_sum.vel = 3
permutacoes.modo = "perm"
permutacoes.vel = 4
n_rainhas.vel = 7
sudoku.vel = 10
sudoku_mrv.vel = 10


# ---------------------------------------------------------------------
#  Cena
# ---------------------------------------------------------------------

class Backtracking(Cena):
    titulo = "Backtracking"
    NQ = 8
    vel_inicial = 7
    ajuda = ("Tenta uma escolha, avança, e DESFAZ (backtrack) quando bate em um beco sem saída.",
             "TAB: escolher o problema (N-Rainhas, Sudoku, cavalo, soma de subconjuntos, permutações).")
    algoritmos = [
        ("N-Rainhas (8x8)", n_rainhas, "O(n!)"),
        ("Sudoku: backtracking simples", sudoku, "exponencial"),
        ("Sudoku: heurística MRV", sudoku_mrv, "exponencial (bem menos passos)"),
        ("Passeio do cavaleiro 5x5: força bruta", cavalo_bruto, "exponencial"),
        ("Passeio do cavaleiro 8x8: Warnsdorff", cavalo_warnsdorff, "O(n²)"),
        ("Soma de subconjuntos", subset_sum, "O(2ⁿ)"),
        ("Permutações de 4 elementos", permutacoes, "O(n!)"),
    ]

    def reiniciar(self, modo="rainhas", tam=5):
        self.modo = modo
        self.rainhas = [None] * self.NQ
        self.sud = [[int(ch) if ch.isdigit() else 0 for ch in linha] for linha in PUZZLE]
        self.fixo = {(r, c) for r in range(9) for c in range(9) if self.sud[r][c]}
        self.atual = None
        self.KN = tam
        self.trilha, self.visitadas = [], set()
        n = 9
        self.nums = [random.randint(3, 30) for _ in range(n)]
        self.alvo_soma = sum(random.sample(self.nums, 4))
        self.sel, self.soma, self.pos_i = [None] * n, 0, None
        self.perms, self.perm_atual = [], []
        self.gerador = None
        self.terminou = False
        self.info = ""

    def valido(self, r, c, v):
        for i in range(9):
            if self.sud[r][i] == v or self.sud[i][c] == v:
                return False
        br, bc = 3 * (r // 3), 3 * (c // 3)
        return all(self.sud[i][j] != v for i in range(br, br + 3) for j in range(bc, bc + 3))

    def iniciar(self, funcao):
        self.reiniciar(funcao.modo, getattr(funcao, "tam", 5))
        self.vel = getattr(funcao, "vel", 7)
        self.comecar(funcao(self))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and self.alg_idx >= 0:
            self.selecionar(self.alg_idx)

    def desenhar_cena(self, tela):
        getattr(self, "_desenhar_" + self.modo)(tela)

    # ---------- N-Rainhas ----------
    def _desenhar_rainhas(self, tela):
        n, lado = self.NQ, 62
        x0 = (LARGURA - n * lado) // 2
        y0 = TOPO + (ALTURA - TOPO - n * lado) // 2
        for r in range(n):
            for c in range(n):
                cor = (190, 160, 120) if (r + c) % 2 == 0 else (110, 80, 55)
                pygame.draw.rect(tela, cor, (x0 + c * lado, y0 + r * lado, lado, lado))
        for r, c in enumerate(self.rainhas):
            if c is None:
                continue
            ruim = self.atual and (r, c) == self.atual[:2] and not self.atual[2]
            cx, cy = x0 + c * lado + lado // 2, y0 + r * lado + lado // 2
            pygame.draw.circle(tela, VERMELHO if ruim else AMARELO, (cx, cy), lado // 2 - 8)
            texto(tela, "Q", cx, cy - 10, "g", PRETO, centro=True)

    # ---------- Sudoku ----------
    def _desenhar_sudoku(self, tela):
        lado = 52
        x0 = (LARGURA - 9 * lado) // 2
        y0 = TOPO + (ALTURA - TOPO - 9 * lado) // 2
        if self.atual:
            r, c = self.atual
            pygame.draw.rect(tela, (110, 30, 30), (x0 + c * lado, y0 + r * lado, lado, lado))
        for r in range(9):
            for c in range(9):
                v = self.sud[r][c]
                if v:
                    cor = BRANCO if (r, c) in self.fixo else (VERDE if self.terminou else CIANO)
                    texto(tela, v, x0 + c * lado + lado // 2, y0 + r * lado + 12, "g", cor, centro=True)
        for i in range(10):
            esp = 3 if i % 3 == 0 else 1
            pygame.draw.line(tela, CINZA, (x0, y0 + i * lado), (x0 + 9 * lado, y0 + i * lado), esp)
            pygame.draw.line(tela, CINZA, (x0 + i * lado, y0), (x0 + i * lado, y0 + 9 * lado), esp)

    # ---------- Cavalo ----------
    def _desenhar_cavalo(self, tela):
        N = self.KN
        lado = min(70, (ALTURA - TOPO - 30) // N)
        x0 = (LARGURA - N * lado) // 2
        y0 = TOPO + (ALTURA - TOPO - N * lado) // 2
        for r in range(N):
            for c in range(N):
                cor = (190, 160, 120) if (r + c) % 2 == 0 else (110, 80, 55)
                pygame.draw.rect(tela, cor, (x0 + c * lado, y0 + r * lado, lado, lado))
        centro = lambda p: (x0 + p[1] * lado + lado // 2, y0 + p[0] * lado + lado // 2)
        for a, b in zip(self.trilha, self.trilha[1:]):
            pygame.draw.line(tela, AZUL, centro(a), centro(b), 3)
        for k, p in enumerate(self.trilha):
            cor = AMARELO if k == len(self.trilha) - 1 and not self.terminou else (VERDE if self.terminou else BRANCO)
            pygame.draw.circle(tela, cor, centro(p), lado // 3)
            texto(tela, k + 1, centro(p)[0], centro(p)[1] - 8, "p", PRETO, centro=True)
        self.info = self.info or f"Casas visitadas: {len(self.trilha)} de {N * N}"

    # ---------- Soma de subconjuntos ----------
    def _desenhar_subset(self, tela):
        n = len(self.nums)
        larg = 80
        x0 = (LARGURA - n * larg) // 2
        y = TOPO + 150
        texto(tela, f"Alvo: {self.alvo_soma}", LARGURA // 2, TOPO + 40, "t", AMARELO, centro=True)
        texto(tela, f"Soma atual: {self.soma}", LARGURA // 2, TOPO + 90, "g", BRANCO, centro=True)
        for i, v in enumerate(self.nums):
            r = pygame.Rect(x0 + i * larg + 4, y, larg - 8, 64)
            est = self.sel[i]
            fundo = VERDE if est is True else ((90, 40, 40) if est is False else (50, 50, 65))
            pygame.draw.rect(tela, fundo, r, border_radius=8)
            if i == self.pos_i:
                pygame.draw.rect(tela, AMARELO, r, 4, border_radius=8)
            texto(tela, v, r.centerx, r.y + 20, "g", PRETO if est is True else BRANCO, centro=True)
            texto(tela, {True: "inclui", False: "exclui", None: ""}[est], r.centerx, r.bottom + 6, "p", CINZA, centro=True)
        escolhidos = [self.nums[i] for i in range(n) if self.sel[i]]
        if escolhidos:
            texto(tela, " + ".join(map(str, escolhidos)) + f" = {self.soma}", LARGURA // 2, y + 120, "g", VERDE, centro=True)

    # ---------- Permutações ----------
    def _desenhar_perm(self, tela):
        texto(tela, "Construindo:", 60, TOPO + 40, "g", CINZA)
        for i in range(4):
            r = pygame.Rect(60 + i * 70, TOPO + 80, 60, 60)
            pygame.draw.rect(tela, (50, 50, 65), r, border_radius=8)
            if i < len(self.perm_atual):
                pygame.draw.rect(tela, AMARELO, r, border_radius=8)
                texto(tela, self.perm_atual[i], r.centerx, r.y + 17, "g", PRETO, centro=True)
        texto(tela, "Permutações completas:", 400, TOPO + 40, "g", CINZA)
        for k, p in enumerate(self.perms):
            col, lin = divmod(k, 8)
            texto(tela, "".join(map(str, p)), 400 + col * 90, TOPO + 80 + lin * 34, "g", VERDE)
