"""Programação dinâmica: a tabela é preenchida célula a célula, mostrando de quais
células anteriores cada valor depende, e no final o caminho (traceback) da solução."""
import random

import pygame

from .base import *

PARES_PALAVRAS = [("kitten", "sitting"), ("sunday", "saturday"), ("intention", "execution"),
                  ("horse", "ros"), ("flaw", "lawn"), ("graph", "giraffe")]


def lcs(g):
    """Maior subsequência comum."""
    g.a = "".join(random.choice("ABCD") for _ in range(8))
    g.b = "".join(random.choice("ABCD") for _ in range(7))
    a, b = g.a, g.b
    n, m = len(a), len(b)
    g.rot_lin, g.rot_col = [""] + list(a), [""] + list(b)
    T = g.tab = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        T[i][0] = 0
    for j in range(m + 1):
        T[0][j] = 0
    g.info = "Se os caracteres são iguais: diagonal + 1. Senão: o maior entre cima e esquerda."
    yield
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            g.atual = (i, j)
            if a[i - 1] == b[j - 1]:
                g.deps = [(i - 1, j - 1)]
                T[i][j] = T[i - 1][j - 1] + 1
            else:
                g.deps = [(i - 1, j), (i, j - 1)]
                T[i][j] = max(T[i - 1][j], T[i][j - 1])
            yield
    g.atual, g.deps = None, []
    i, j, seq = n, m, []
    while i > 0 and j > 0:
        g.caminho.add((i, j))
        if a[i - 1] == b[j - 1]:
            seq.append(a[i - 1])
            i, j = i - 1, j - 1
        elif T[i - 1][j] >= T[i][j - 1]:
            i -= 1
        else:
            j -= 1
        yield
    g.resposta = "".join(reversed(seq))
    g.info = f"LCS = '{g.resposta}' (tamanho {T[n][m]})"


def edicao(g):
    """Distância de edição (Levenshtein)."""
    g.a, g.b = random.choice(PARES_PALAVRAS)
    a, b = g.a, g.b
    n, m = len(a), len(b)
    g.rot_lin, g.rot_col = [""] + list(a), [""] + list(b)
    T = g.tab = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        T[i][0] = i
    for j in range(m + 1):
        T[0][j] = j
    g.info = f"'{a}' -> '{b}': inserir, remover ou trocar custam 1 cada"
    yield
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            g.atual = (i, j)
            g.deps = [(i - 1, j - 1), (i - 1, j), (i, j - 1)]
            custo = 0 if a[i - 1] == b[j - 1] else 1
            T[i][j] = min(T[i - 1][j - 1] + custo, T[i - 1][j] + 1, T[i][j - 1] + 1)
            yield
    g.atual, g.deps = None, []
    i, j = n, m
    while i > 0 or j > 0:
        g.caminho.add((i, j))
        if i > 0 and j > 0 and T[i][j] == T[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1):
            i, j = i - 1, j - 1
        elif i > 0 and T[i][j] == T[i - 1][j] + 1:
            i -= 1
        else:
            j -= 1
        yield
    g.caminho.add((0, 0))
    g.resposta = T[n][m]
    g.info = f"Distância de edição entre '{a}' e '{b}' = {T[n][m]}"


def mochila(g):
    """Mochila 0/1."""
    n, cap = 6, 10
    g.itens = [(random.randint(1, 6), random.randint(3, 15)) for _ in range(n)]
    g.cap = cap
    g.rot_lin = ["sem itens"] + [f"item {i + 1} (p{w},v{v})" for i, (w, v) in enumerate(g.itens)]
    g.rot_col = [str(c) for c in range(cap + 1)]
    T = g.tab = [[None] * (cap + 1) for _ in range(n + 1)]
    for c in range(cap + 1):
        T[0][c] = 0
    g.info = f"Capacidade {cap}. Cada célula: melhor valor usando os primeiros i itens com capacidade c."
    yield
    for i in range(1, n + 1):
        w, v = g.itens[i - 1]
        for c in range(cap + 1):
            g.atual = (i, c)
            g.deps = [(i - 1, c)] + ([(i - 1, c - w)] if c >= w else [])
            T[i][c] = max(T[i - 1][c], T[i - 1][c - w] + v) if c >= w else T[i - 1][c]
            yield
    g.atual, g.deps = None, []
    c, escolhidos = cap, []
    for i in range(n, 0, -1):
        g.caminho.add((i, c))
        if T[i][c] != T[i - 1][c]:
            escolhidos.append(i)
            c -= g.itens[i - 1][0]
        yield
    g.caminho.add((0, c))
    g.escolhidos = sorted(escolhidos)
    g.resposta = T[n][cap]
    g.info = f"Valor máximo {T[n][cap]} levando os itens {g.escolhidos}"


def troco(g):
    """Número mínimo de moedas (onde o guloso pode falhar)."""
    g.moedas, g.valor = random.choice([([1, 5, 6, 9], 11), ([1, 3, 4], 6), ([1, 7, 10], 14), ([2, 5, 10], 13),
                                       ([1, 5, 12], 15)])
    moedas, A = g.moedas, g.valor
    g.rot_lin = ["mín. moedas"]
    g.rot_col = [str(a) for a in range(A + 1)]
    T = g.tab = [[None] * (A + 1)]
    usada = [None] * (A + 1)
    T[0][0] = 0
    g.info = f"Moedas {moedas}, valor {A}: T[a] = 1 + min(T[a - moeda])"
    yield
    INF = 10 ** 9
    for a in range(1, A + 1):
        g.atual = (0, a)
        g.deps = [(0, a - m) for m in moedas if m <= a and T[0][a - m] is not None and T[0][a - m] < INF]
        melhor = INF
        for m in moedas:
            if m <= a and T[0][a - m] is not None and T[0][a - m] + 1 < melhor:
                melhor = T[0][a - m] + 1
                usada[a] = m
        T[0][a] = melhor
        yield
    g.atual, g.deps = None, []
    a, usadas = A, []
    while a > 0 and T[0][a] < INF:
        g.caminho.add((0, a))
        usadas.append(usada[a])
        a -= usada[a]
        yield
    g.caminho.add((0, 0))
    gul, resto = 0, A
    for m in sorted(moedas, reverse=True):
        gul += resto // m
        resto %= m
    g.resposta = T[0][A]
    g.usadas = usadas
    g.info = f"Mínimo: {T[0][A]} moedas {sorted(usadas, reverse=True)}   (o guloso usaria {gul})"


def lis(g):
    """Maior subsequência crescente (O(n²))."""
    n = 10
    g.arr = [random.randint(1, 30) for _ in range(n)]
    arr = g.arr
    g.rot_lin = ["valor", "LIS que termina aqui"]
    g.rot_col = [str(i) for i in range(n)]
    T = g.tab = [list(arr), [None] * n]
    prev = [-1] * n
    g.info = "LIS[i] = 1 + max(LIS[j]) para j < i com valor[j] < valor[i]"
    yield
    for i in range(n):
        g.atual = (1, i)
        g.deps = [(1, j) for j in range(i) if arr[j] < arr[i]]
        T[1][i] = 1
        for j in range(i):
            if arr[j] < arr[i] and T[1][j] + 1 > T[1][i]:
                T[1][i] = T[1][j] + 1
                prev[i] = j
        yield
    g.atual, g.deps = None, []
    i = max(range(n), key=lambda k: T[1][k])
    seq = []
    while i != -1:
        seq.append(arr[i])
        g.caminho.add((0, i))
        g.caminho.add((1, i))
        i = prev[i]
        yield
    g.resposta = list(reversed(seq))
    g.info = f"LIS = {g.resposta} (tamanho {len(seq)})"


def cadeia_matrizes(g):
    """Multiplicação de cadeia de matrizes: melhor ordem dos parênteses."""
    g.dims = [random.choice([10, 20, 30, 40, 50, 60]) for _ in range(6)]
    d = g.dims
    n = len(d) - 1
    g.rot_lin = [f"A{i + 1} ({d[i]}x{d[i + 1]})" for i in range(n)]
    g.rot_col = [f"A{j + 1}" for j in range(n)]
    T = g.tab = [[0 if i == j else None for j in range(n)] for i in range(n)]
    corte = [[0] * n for _ in range(n)]
    g.info = "m[i][j] = menor nº de multiplicações escalares para A_i..A_j"
    yield
    for tam in range(2, n + 1):
        for i in range(n - tam + 1):
            j = i + tam - 1
            g.atual = (i, j)
            melhor = None
            for k in range(i, j):
                g.deps = [(i, k), (k + 1, j)]
                c = T[i][k] + T[k + 1][j] + d[i] * d[k + 1] * d[j + 1]
                if melhor is None or c < melhor:
                    melhor, corte[i][j] = c, k
                yield
            T[i][j] = melhor
            yield

    def paren(i, j):
        return f"A{i + 1}" if i == j else "(" + paren(i, corte[i][j]) + " x " + paren(corte[i][j] + 1, j) + ")"

    g.atual, g.deps = None, []
    g.caminho.add((0, n - 1))
    g.resposta = T[0][n - 1]
    g.info = f"Mínimo: {T[0][n - 1]} multiplicações com {paren(0, n - 1)}"


class ProgDinamica(Cena):
    titulo = "Programação dinâmica"
    vel_inicial = 4
    ajuda = ("Amarelo = célula calculada agora, azul = células das quais ela depende, verde = caminho da solução.",
             "TAB: escolher o problema. R: novo exemplo aleatório do mesmo problema.")
    algoritmos = [
        ("LCS (maior subsequência comum)", lcs, "O(n·m)"),
        ("Distância de edição (Levenshtein)", edicao, "O(n·m)"),
        ("Mochila 0/1 (knapsack)", mochila, "O(n·W)"),
        ("Troco com mínimo de moedas", troco, "O(n·valor)"),
        ("LIS (maior subsequência crescente)", lis, "O(n²)"),
        ("Multiplicação de cadeia de matrizes", cadeia_matrizes, "O(n³)"),
    ]

    def reiniciar(self):
        self.tab, self.rot_lin, self.rot_col = None, [], []
        self.atual, self.deps, self.caminho = None, [], set()
        self.gerador = None

    def iniciar(self, funcao):
        self.reiniciar()
        self.comecar(funcao(self))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and self.alg_idx >= 0:
            self.selecionar(self.alg_idx)

    def desenhar_cena(self, tela):
        if not self.tab:
            texto(tela, "Aperte TAB (ou 1 a 6) para escolher o problema", LARGURA // 2, ALTURA // 2, "g", CINZA, centro=True)
            return
        linhas, colunas = len(self.tab), len(self.tab[0])
        larg_rot = 150
        lado = min(62, (LARGURA - larg_rot - 30) // colunas)
        alt = min(36, (ALTURA - TOPO - 60) // (linhas + 1))
        x0, y0 = 20 + larg_rot, TOPO + 24
        for j in range(colunas):
            rot = self.rot_col[j] if j < len(self.rot_col) else ""
            texto(tela, rot, x0 + j * lado + lado // 2, y0 + 8, "m", CINZA, centro=True)
        for i in range(linhas):
            rot = self.rot_lin[i] if i < len(self.rot_lin) else ""
            texto(tela, rot, x0 - 8, y0 + (i + 1) * alt + 8, "m" if len(rot) < 14 else "p", CINZA, direita=True)
            for j in range(colunas):
                r = pygame.Rect(x0 + j * lado, y0 + (i + 1) * alt, lado - 3, alt - 3)
                v = self.tab[i][j]
                fundo, cor = (30, 30, 42), BRANCO
                if (i, j) in self.caminho:
                    fundo, cor = VERDE, PRETO
                elif (i, j) == self.atual:
                    fundo, cor = AMARELO, PRETO
                elif (i, j) in self.deps:
                    fundo = (50, 85, 160)
                pygame.draw.rect(tela, fundo, r, border_radius=5)
                if v is not None:
                    texto(tela, "inf" if isinstance(v, int) and v >= 10 ** 9 else v, r.centerx, r.y + (alt - 22) // 2 + 1,
                          "m", cor, centro=True)
