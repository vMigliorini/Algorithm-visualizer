"""Clássicos: Torre de Hanói (3, 5 e 7 discos) e Crivo de Eratóstenes."""
import pygame

from .base import *


def _hanoi(g, n, a, b, c):
    if n == 0:
        return
    yield from _hanoi(g, n - 1, a, c, b)
    g.pinos[c].append(g.pinos[a].pop())
    g.mov = (a, c)
    yield
    yield from _hanoi(g, n - 1, b, a, c)


def hanoi(g):
    yield from _hanoi(g, g.DISCOS, 0, 1, 2)
    g.mov = None
    g.info = f"Concluído em {2 ** g.DISCOS - 1} movimentos (2^n - 1)"


def crivo(g):
    n = g.NUM
    est = g.estado
    i = 2
    while i * i <= n:
        if est[i] == "?":
            est[i] = "primo"
            g.atual = i
            yield
            for m in range(i * i, n + 1, i):
                if est[m] != "composto":
                    est[m] = "composto"
                    yield
        i += 1
    for k in range(2, n + 1):
        if est[k] == "?":
            est[k] = "primo"
    g.atual = None
    yield
    g.info = f"{sum(1 for v in est.values() if v == 'primo')} primos até {n}"



def _hanoi_n(n):
    def f(g):
        return hanoi(g)
    f.discos = n
    f.modo = "hanoi"
    return f


hanoi3, hanoi5, hanoi7 = _hanoi_n(3), _hanoi_n(5), _hanoi_n(7)
crivo.modo = "crivo"
crivo.discos = 5


class Classicos(Cena):
    titulo = "Clássicos"
    DISCOS = 5
    NUM = 150
    COLS_CRIVO = 15
    vel_inicial = 2
    ajuda = ("Torre de Hanói: mova todos os discos de A para C, nunca um maior sobre um menor (2^n - 1 movimentos).",
             "Crivo de Eratóstenes: cada primo elimina seus múltiplos, a partir de p². TAB: escolher. R: reiniciar.")
    algoritmos = [
        ("Torre de Hanói (3 discos)", hanoi3, "O(2ⁿ)"),
        ("Torre de Hanói (5 discos)", hanoi5, "O(2ⁿ)"),
        ("Torre de Hanói (7 discos)", hanoi7, "O(2ⁿ)"),
        ("Crivo de Eratóstenes (até 150)", crivo, "O(n log log n)"),
    ]

    def reiniciar(self):
        self.modo = "hanoi"
        self.pinos = [list(range(self.DISCOS, 0, -1)), [], []]
        self.mov = None
        self.estado = {i: "?" for i in range(2, self.NUM + 1)}
        self.estado[1] = "composto"
        self.atual = None
        self.gerador = None
        self.terminou = False
        self.info = ""

    def iniciar(self, funcao):
        self.DISCOS = funcao.discos
        self.reiniciar()
        self.modo = funcao.modo
        self.vel = {"hanoi": {3: 2, 5: 3, 7: 5}.get(funcao.discos, 3), "crivo": 5}[self.modo]
        self.comecar(funcao(self))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and self.alg_idx >= 0:
            self.selecionar(self.alg_idx)

    def desenhar_cena(self, tela):
        if self.modo == "hanoi":
            self._desenhar_hanoi(tela)
        else:
            self._desenhar_crivo(tela)

    def _desenhar_hanoi(self, tela):
        base = ALTURA - 60
        pygame.draw.rect(tela, CINZA, (40, base, LARGURA - 80, 8))
        for p, cx in enumerate((200, 500, 800)):
            pygame.draw.rect(tela, CINZA, (cx - 5, base - 300, 10, 300))
            for k, d in enumerate(self.pinos[p]):
                larg = 40 + 28 * d
                cor = PALETA[(d - 1) % len(PALETA)]
                pygame.draw.rect(tela, cor, (cx - larg // 2, base - 26 * (k + 1), larg, 24), border_radius=6)
            texto(tela, "ABC"[p], cx, base + 14, "g", CINZA, centro=True)

    def _desenhar_crivo(self, tela):
        cols = self.COLS_CRIVO
        lado_x, lado_y = 64, 48
        x0 = (LARGURA - cols * lado_x) // 2
        y0 = TOPO + 14
        for n in range(1, self.NUM + 1):
            r, c = divmod(n - 1, cols)
            est = self.estado[n]
            if n == self.atual:
                cor, fonte = AMARELO, PRETO
            elif est == "primo":
                cor, fonte = VERDE, PRETO
            elif est == "composto":
                cor, fonte = (45, 45, 55), CINZA
            else:
                cor, fonte = (200, 200, 215), PRETO
            pygame.draw.rect(tela, cor, (x0 + c * lado_x + 2, y0 + r * lado_y + 2, lado_x - 4, lado_y - 4),
                             border_radius=6)
            texto(tela, n, x0 + c * lado_x + lado_x // 2, y0 + r * lado_y + 13, "m", fonte, centro=True)
