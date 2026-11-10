"""Matemática: Euclides (MDC), exponenciação rápida, Collatz, árvore de recursão do Fibonacci
(com e sem memoização), triângulo de Pascal (e Sierpiński) e teste de primalidade de Miller-Rabin.

Digite números separados por espaço + ENTER para usar seus valores; vazio = aleatório."""
import math
import random

import pygame

from .base import *


def _num(nums, i, padrao, lo, hi):
    if i < len(nums):
        return max(lo, min(hi, nums[i]))
    return padrao


# ---------------------------------------------------------------------
#  Euclides
# ---------------------------------------------------------------------

def euclides(g, nums):
    a = _num(nums, 0, random.randint(40, 120), 1, 300)
    b = _num(nums, 1, random.randint(15, 80), 1, 300)
    if a < b:
        a, b = b, a
    g.ea, g.eb = a, b
    g.quadrados, g.linhas_txt = [], []
    x = y = 0
    w, h = a, b
    cor_i = 0
    A, B = a, b
    g.info = f"mdc({a}, {b}): o retângulo {a}x{b} é recortado em quadrados cada vez menores"
    yield
    while w and h:
        q, r = divmod(A, B)
        g.linhas_txt.append((f"{A} = {q} x {B} + {r}", AMARELO if r else VERDE))
        cor = cor_hsv(cor_i * 0.17, 0.55, 0.85)
        if w >= h:
            n = w // h
            for k in range(n):
                g.quadrados.append((x + k * h, y, h, cor))
                yield
            x, w = x + n * h, w - n * h
            lado = h
        else:
            n = h // w
            for k in range(n):
                g.quadrados.append((x, y + k * w, w, cor))
                yield
            y, h = y + n * w, h - n * w
            lado = w
        A, B = B, r
        cor_i += 1
    g.resultado = lado
    g.info = f"mdc({a}, {b}) = {lado}  (o menor quadrado que ladrilha o retângulo inteiro)"


# ---------------------------------------------------------------------
#  Exponenciação rápida
# ---------------------------------------------------------------------

def pow_rapida(g, nums):
    b = _num(nums, 0, random.randint(2, 9), 1, 99)
    e0 = _num(nums, 1, random.randint(20, 80), 1, 10 ** 6)
    m = _num(nums, 2, random.choice([97, 1000, 10007]), 2, 10 ** 6)
    g.linhas_txt = [(f"{b}^{e0} mod {m}  (expoente em binário: {bin(e0)[2:]})", CIANO),
                    ("bit   resultado      base", CINZA)]
    res, base, e = 1, b % m, e0
    g.info = "Percorre o expoente bit a bit: bit 1 multiplica o resultado; a base é sempre elevada ao quadrado."
    yield
    while e:
        bit = e & 1
        if bit:
            res = res * base % m
        g.linhas_txt.append((f" {bit}     {res:<12}   {base}", VERDE if bit else BRANCO))
        base = base * base % m
        e >>= 1
        yield
    g.resultado = res
    g.info = f"{b}^{e0} mod {m} = {res}  (só {e0.bit_length()} passos em vez de {e0 - 1} multiplicações)"


# ---------------------------------------------------------------------
#  Collatz
# ---------------------------------------------------------------------

def collatz(g, nums):
    n = _num(nums, 0, random.choice([27, 97, 171, 231, 313, 327, 649, 703, 871]), 1, 100000)
    g.seq = [n]
    g.info = f"Começando em {n}: se par divide por 2, se ímpar faz 3n + 1."
    yield
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        g.seq.append(n)
        g.info = f"Passo {len(g.seq) - 1}: valor {n}   (máximo até agora {max(g.seq)})"
        yield
    g.info = f"Chegou a 1 em {len(g.seq) - 1} passos; valor máximo {max(g.seq)}"


# ---------------------------------------------------------------------
#  Fibonacci: árvore de chamadas
# ---------------------------------------------------------------------

class FNo:
    def __init__(self, n):
        self.n, self.filhos, self.cor, self.val = n, [], BRANCO, None


def _fib(g, no, cache):
    g.chamadas += 1
    no.cor = AMARELO
    g.info = f"fib({no.n}) chamado   total de chamadas: {g.chamadas}"
    yield
    if no.n <= 1:
        no.val = no.n
        no.cor = VERDE
        yield
        return no.val
    if cache is not None and no.n in cache:
        no.val = cache[no.n]
        no.cor = CIANO
        yield
        return no.val
    no.filhos = [FNo(no.n - 1), FNo(no.n - 2)]
    va = yield from _fib(g, no.filhos[0], cache)
    vb = yield from _fib(g, no.filhos[1], cache)
    no.val = va + vb
    if cache is not None:
        cache[no.n] = no.val
    no.cor = VERDE
    yield
    return no.val


def fib_ingenuo(g, nums):
    g.raiz_f, g.chamadas = FNo(_num(nums, 0, 6, 2, 7)), 0
    r = yield from _fib(g, g.raiz_f, None)
    g.resultado = r
    g.info = f"fib({g.raiz_f.n}) = {r} com {g.chamadas} chamadas (cresce exponencialmente)"


def fib_memo(g, nums):
    g.raiz_f, g.chamadas = FNo(_num(nums, 0, 6, 2, 7)), 0
    r = yield from _fib(g, g.raiz_f, {})
    g.resultado = r
    g.info = f"fib({g.raiz_f.n}) = {r} com {g.chamadas} chamadas (ciano = reaproveitado do cache)"


# ---------------------------------------------------------------------
#  Pascal
# ---------------------------------------------------------------------

def _pascal(g, linhas, mod2):
    g.pascal, g.mod2 = [], mod2
    linha = [1]
    for k in range(linhas):
        g.pascal.append(linha)
        g.info = f"Linha {k}: cada número é a soma dos dois acima" + ("  (cor = ímpar)" if mod2 else "")
        yield
        linha = [1] + [(linha[i] + linha[i + 1]) % (2 if mod2 else 10 ** 12) for i in range(len(linha) - 1)] + [1]
    if mod2:
        g.info = "Pascal módulo 2: o triângulo de Sierpiński (fractal) aparece sozinho"


def pascal(g, nums):
    return _pascal(g, _num(nums, 0, 11, 2, 14), False)


def sierpinski(g, nums):
    return _pascal(g, 64, True)


# ---------------------------------------------------------------------
#  Miller-Rabin
# ---------------------------------------------------------------------

TESTEMUNHAS = [2, 3, 5, 7, 11, 13, 17]
EXEMPLOS_MR = [561, 1105, 1729, 2047, 7919, 104729, 999983, 91, 221, 1000003, 3215031751, 2147483647]


def miller_rabin(g, nums):
    n = _num(nums, 0, random.choice(EXEMPLOS_MR), 2, 10 ** 12)
    g.numero_mr = n
    g.linhas_txt = []
    if n < 4 or n % 2 == 0:
        g.eh_primo = n in (2, 3)
        g.linhas_txt.append((f"{n} é {'primo' if g.eh_primo else 'composto'} (caso trivial)", VERDE if g.eh_primo else VERMELHO))
        g.info = g.linhas_txt[-1][0]
        yield
        return
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    g.linhas_txt.append((f"n = {n}:  n - 1 = 2^{s} x {d}", CIANO))
    g.info = "Para cada testemunha a: calcula a^d mod n e eleva ao quadrado até achar n-1 (ou provar que é composto)"
    yield
    for a in TESTEMUNHAS:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        g.linhas_txt.append((f"a = {a}:  {a}^{d} mod n = {x}", BRANCO))
        yield
        if x in (1, n - 1):
            g.linhas_txt.append(("   passa (1 ou n-1)", VERDE))
            yield
            continue
        for r in range(1, s):
            x = x * x % n
            g.linhas_txt.append((f"   x² mod n = {x}", BRANCO))
            yield
            if x == n - 1:
                g.linhas_txt.append(("   chegou a n-1: passa", VERDE))
                yield
                break
        else:
            g.linhas_txt.append((f"   a = {a} é TESTEMUNHA: {n} é COMPOSTO", VERMELHO))
            g.eh_primo = False
            g.info = f"{n} é composto (a = {a} provou)"
            yield
            return
    g.eh_primo = True
    g.linhas_txt.append((f"{n} passou em todas as testemunhas: PRIMO (exato para n < 3,4 x 10^14)", VERDE))
    g.info = f"{n} é primo"
    yield


for _f, _m in ((euclides, "euclides"), (pow_rapida, "texto"), (collatz, "collatz"), (fib_ingenuo, "fib"),
               (fib_memo, "fib"), (pascal, "pascal"), (sierpinski, "pascal"), (miller_rabin, "texto")):
    _f.modo = _m


class Matematica(Cena):
    titulo = "Matemática"
    digitos_algoritmo = False
    aceita = "numesp"
    max_entrada = 22
    vel_inicial = 4
    ajuda = ("Números + ENTER usam seus valores: Euclides 'a b', Potência 'base exp mod', os demais 'n'.",
             "TAB: escolher o algoritmo. Vazio + ENTER: novo exemplo aleatório. (Pausa: F1)")
    algoritmos = [
        ("Algoritmo de Euclides (MDC)", euclides, "O(log min(a, b))"),
        ("Exponenciação rápida (modular)", pow_rapida, "O(log e)"),
        ("Conjectura de Collatz", collatz, "aberto!"),
        ("Fibonacci recursivo (ingênuo)", fib_ingenuo, "O(φⁿ)"),
        ("Fibonacci com memoização", fib_memo, "O(n)"),
        ("Triângulo de Pascal", pascal, "O(n²)"),
        ("Pascal mod 2 (Sierpiński)", sierpinski, "O(n²)"),
        ("Miller-Rabin (primalidade)", miller_rabin, "O(k log³ n)"),
    ]

    def reiniciar(self):
        self.modo = "euclides"
        self.quadrados, self.linhas_txt, self.seq = [], [], []
        self.raiz_f, self.pascal, self.mod2 = None, [], False
        self.ea = self.eb = 1
        self.gerador = None
        self.op = euclides
        self.alg_idx = 0
        self.nome, _, self.complexidade = self.algoritmos[0]

    def iniciar(self, funcao):
        self.op = funcao
        self._rodar([])

    def _rodar(self, nums):
        self.reiniciar_visual()
        self.modo = self.op.modo
        self.comecar(self.op(self, nums))

    def reiniciar_visual(self):
        self.quadrados, self.linhas_txt, self.seq = [], [], []
        self.raiz_f, self.pascal = None, []

    def ao_enter(self):
        nums = [int(x) for x in self.entrada.split() if x.isdigit()]
        self.entrada = ""
        self._rodar(nums)

    def desenhar_cena(self, tela):
        if self.gerador is None and not self.terminou and self.passos == 0:
            texto(tela, "Aperte TAB para escolher o algoritmo (ou ENTER para rodar o Euclides)", LARGURA // 2, ALTURA // 2, "g", CINZA, centro=True)
            return
        getattr(self, "_d_" + self.modo)(tela)
        texto(tela, f"Entrada: {self.entrada}_", 10, ALTURA - 24, "m", CIANO)

    def _d_euclides(self, tela):
        a, b = self.ea, self.eb
        esc = min((LARGURA - 340) / a, (ALTURA - TOPO - 60) / b)
        x0, y0 = 20, TOPO + 30
        pygame.draw.rect(tela, CINZA, (x0, y0, a * esc, b * esc), 1)
        for x, y, lado, cor in self.quadrados:
            r = pygame.Rect(x0 + x * esc, y0 + y * esc, lado * esc, lado * esc)
            pygame.draw.rect(tela, cor, r)
            pygame.draw.rect(tela, PRETO, r, 1)
            if lado * esc > 22:
                texto(tela, lado, r.centerx, r.centery - 8, "m", PRETO, centro=True)
        for k, (t, cor) in enumerate(self.linhas_txt):
            texto(tela, t, LARGURA - 300, TOPO + 30 + k * 24, "m", cor)

    def _d_texto(self, tela):
        linhas = self.linhas_txt[-22:]
        for k, (t, cor) in enumerate(linhas):
            texto(tela, t, 40, TOPO + 24 + k * 24, "m", cor)

    def _d_collatz(self, tela):
        if len(self.seq) < 2:
            return
        x0, y0, w, h = 50, TOPO + 30, LARGURA - 100, ALTURA - TOPO - 90
        pygame.draw.line(tela, CINZA_ESC, (x0, y0 + h), (x0 + w, y0 + h), 1)
        pygame.draw.line(tela, CINZA_ESC, (x0, y0), (x0, y0 + h), 1)
        mx = max(self.seq)
        pts = [(x0 + i / max(len(self.seq) - 1, 1) * w, y0 + h - v / mx * h) for i, v in enumerate(self.seq)]
        pygame.draw.lines(tela, CIANO, False, pts, 2)
        pygame.draw.circle(tela, AMARELO, (int(pts[-1][0]), int(pts[-1][1])), 5)
        texto(tela, f"max {mx}", x0 + 6, y0, "p", CINZA)

    def _d_fib(self, tela):
        if self.raiz_f is None:
            return
        pos = layout_folhas(self.raiz_f, lambda n: n.filhos, 20, LARGURA - 20, TOPO + 36, 70, passo_max=80)
        for no, (x, y) in pos.items():
            for f in no.filhos:
                pygame.draw.line(tela, CINZA, (x, y), pos[f], 2)
        for no, (x, y) in pos.items():
            desenhar_no(tela, (x, y), no.n, no.cor, 17)
            if no.val is not None:
                texto(tela, f"={no.val}", x, y + 19, "p", CINZA, centro=True)

    def _d_pascal(self, tela):
        n = len(self.pascal)
        if not n:
            return
        if self.mod2:
            lado = 9
            x0, y0 = (LARGURA - 64 * lado) // 2, TOPO + 6
            for r, linha in enumerate(self.pascal):
                for k, v in enumerate(linha):
                    if v:
                        pygame.draw.rect(tela, cor_hsv(0.55 + r / 100, 0.6, 0.95),
                                         (x0 + 32 * lado - r * lado / 2 + k * lado, y0 + r * 8, lado - 1, 7))
            return
        for r, linha in enumerate(self.pascal):
            larg = 62
            x = LARGURA // 2 - len(linha) * larg // 2
            for k, v in enumerate(linha):
                texto(tela, v, x + k * larg + larg // 2, TOPO + 18 + r * 32, "m", AMARELO if k in (0, len(linha) - 1) else BRANCO,
                      centro=True)
