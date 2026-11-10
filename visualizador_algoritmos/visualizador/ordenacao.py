"""Ordenação e Busca: 18 algoritmos de ordenação e 7 de busca."""
import math
import random

import pygame

from .base import *


def bubble_sort(d):
    n = len(d)
    for i in range(n):
        trocou = False
        for j in range(n - i - 1):
            if d[j] > d[j + 1]:
                d[j], d[j + 1] = d[j + 1], d[j]
                trocou = True
            yield (j, j + 1)
        if not trocou:
            return


def selection_sort(d):
    n = len(d)
    for i in range(n):
        m = i
        for j in range(i + 1, n):
            yield (j, m)
            if d[j] < d[m]:
                m = j
        d[i], d[m] = d[m], d[i]
        yield (i, m)


def insertion_sort(d):
    for i in range(1, len(d)):
        j = i
        while j > 0 and d[j - 1] > d[j]:
            d[j - 1], d[j] = d[j], d[j - 1]
            yield (j - 1, j)
            j -= 1
        yield (j,)


def shell_sort(d):
    n = len(d)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = d[i]
            j = i
            while j >= gap and d[j - gap] > temp:
                d[j] = d[j - gap]
                yield (j, j - gap)
                j -= gap
            d[j] = temp
            yield (j,)
        gap //= 2


def merge_sort(d, lo=0, hi=None):
    if hi is None:
        hi = len(d)
    if hi - lo <= 1:
        return
    mid = (lo + hi) // 2
    yield from merge_sort(d, lo, mid)
    yield from merge_sort(d, mid, hi)
    esq, dir_ = d[lo:mid], d[mid:hi]
    i = j = 0
    k = lo
    while i < len(esq) and j < len(dir_):
        if esq[i] <= dir_[j]:
            d[k] = esq[i]
            i += 1
        else:
            d[k] = dir_[j]
            j += 1
        yield (k,)
        k += 1
    while i < len(esq):
        d[k] = esq[i]
        i += 1
        yield (k,)
        k += 1
    while j < len(dir_):
        d[k] = dir_[j]
        j += 1
        yield (k,)
        k += 1


def quick_sort(d, lo=0, hi=None):
    if hi is None:
        hi = len(d) - 1
    if lo < hi:
        pivo = d[hi]
        i = lo
        for j in range(lo, hi):
            yield (j, hi)
            if d[j] < pivo:
                d[i], d[j] = d[j], d[i]
                i += 1
        d[i], d[hi] = d[hi], d[i]
        yield (i, hi)
        yield from quick_sort(d, lo, i - 1)
        yield from quick_sort(d, i + 1, hi)


def heap_sort(d):
    def peneirar(n, i):
        while True:
            maior = i
            esq, dir_ = 2 * i + 1, 2 * i + 2
            if esq < n and d[esq] > d[maior]:
                maior = esq
            if dir_ < n and d[dir_] > d[maior]:
                maior = dir_
            yield (i, maior)
            if maior == i:
                return
            d[i], d[maior] = d[maior], d[i]
            i = maior

    n = len(d)
    for i in range(n // 2 - 1, -1, -1):
        yield from peneirar(n, i)
    for fim in range(n - 1, 0, -1):
        d[0], d[fim] = d[fim], d[0]
        yield (0, fim)
        yield from peneirar(fim, 0)


def counting_sort(d):
    mx = max(d)
    cont = [0] * (mx + 1)
    for i, v in enumerate(d):
        cont[v] += 1
        yield (i,)
    k = 0
    for v in range(mx + 1):
        while cont[v] > 0:
            d[k] = v
            cont[v] -= 1
            yield (k,)
            k += 1


# =====================================================================
#  ALGORITMOS DE BUSCA  (yield = dict {índice: cor})
# =====================================================================

def busca_linear(d, alvo):
    cores = {}
    for i, v in enumerate(d):
        cores[i] = VERMELHO
        yield cores
        if v == alvo:
            cores[i] = VERDE
            yield cores
            return
        cores[i] = CINZA_ESC


def busca_binaria(d, alvo):
    lo, hi = 0, len(d) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        cores = {i: CINZA_ESC for i in range(len(d)) if i < lo or i > hi}
        cores[lo] = AZUL
        cores[hi] = AZUL
        cores[mid] = VERMELHO
        yield cores
        if d[mid] == alvo:
            cores[mid] = VERDE
            yield cores
            return
        if d[mid] < alvo:
            lo = mid + 1
        else:
            hi = mid - 1


def busca_salto(d, alvo):
    n = len(d)
    passo = max(1, int(math.sqrt(n)))
    ant, atual = 0, passo
    cores = {}
    while ant < n and d[min(atual, n) - 1] < alvo:
        cores[min(atual, n) - 1] = AZUL
        yield cores
        ant, atual = atual, atual + passo
    for i in range(ant, min(atual, n)):
        cores[i] = VERMELHO
        yield cores
        if d[i] == alvo:
            cores[i] = VERDE
            yield cores
            return
        cores[i] = CINZA_ESC


# ---------------------------------------------------------------------
#  Novos algoritmos de ordenação
# ---------------------------------------------------------------------

def radix_sort(d):
    """Radix sort LSD (base 10): distribui em baldes dígito a dígito."""
    mx = max(d)
    exp = 1
    while mx // exp > 0:
        baldes = [[] for _ in range(10)]
        for i, v in enumerate(d):
            baldes[(v // exp) % 10].append(v)
            yield (i,)
        k = 0
        for b in baldes:
            for v in b:
                d[k] = v
                yield (k,)
                k += 1
        exp *= 10


def comb_sort(d):
    n = len(d)
    gap = n
    trocou = True
    while gap > 1 or trocou:
        gap = max(1, int(gap / 1.3))
        trocou = False
        for i in range(n - gap):
            if d[i] > d[i + gap]:
                d[i], d[i + gap] = d[i + gap], d[i]
                trocou = True
            yield (i, i + gap)


def cocktail_sort(d):
    ini, fim = 0, len(d) - 1
    trocou = True
    while trocou:
        trocou = False
        for i in range(ini, fim):
            if d[i] > d[i + 1]:
                d[i], d[i + 1] = d[i + 1], d[i]
                trocou = True
            yield (i, i + 1)
        if not trocou:
            break
        fim -= 1
        trocou = False
        for i in range(fim - 1, ini - 1, -1):
            if d[i] > d[i + 1]:
                d[i], d[i + 1] = d[i + 1], d[i]
                trocou = True
            yield (i, i + 1)
        ini += 1


def gnome_sort(d):
    i = 0
    while i < len(d):
        if i == 0 or d[i - 1] <= d[i]:
            i += 1
        else:
            d[i], d[i - 1] = d[i - 1], d[i]
            i -= 1
        yield (i,)


def odd_even_sort(d):
    n = len(d)
    ordenado = False
    while not ordenado:
        ordenado = True
        for ini in (1, 0):
            for i in range(ini, n - 1, 2):
                if d[i] > d[i + 1]:
                    d[i], d[i + 1] = d[i + 1], d[i]
                    ordenado = False
                yield (i, i + 1)


def cycle_sort(d):
    """Cycle sort: minimiza o número de ESCRITAS (cada elemento vai direto à posição final)."""
    n = len(d)
    for ini in range(n - 1):
        item = d[ini]
        pos = ini
        for i in range(ini + 1, n):
            yield (i, ini)
            if d[i] < item:
                pos += 1
        if pos == ini:
            continue
        while item == d[pos]:
            pos += 1
        d[pos], item = item, d[pos]
        yield (pos,)
        while pos != ini:
            pos = ini
            for i in range(ini + 1, n):
                yield (i,)
                if d[i] < item:
                    pos += 1
            while item == d[pos]:
                pos += 1
            d[pos], item = item, d[pos]
            yield (pos,)


def bitonic_sort(d):
    """Bitonic sort (rede de ordenação): exige tamanho potência de 2 (64 barras)."""
    n = len(d)
    k = 2
    while k <= n:
        j = k // 2
        while j > 0:
            for i in range(n):
                l = i ^ j
                if l > i:
                    if (i & k == 0 and d[i] > d[l]) or (i & k != 0 and d[i] < d[l]):
                        d[i], d[l] = d[l], d[i]
                    yield (i, l)
            j //= 2
        k *= 2


bitonic_sort.n = 64


def _inserir_faixa(d, lo, hi):
    """Insertion sort em d[lo:hi]."""
    for i in range(lo + 1, hi):
        j = i
        while j > lo and d[j - 1] > d[j]:
            d[j - 1], d[j] = d[j], d[j - 1]
            yield (j - 1, j)
            j -= 1


def _merge_faixa(d, lo, mid, hi):
    esq, dir_ = d[lo:mid], d[mid:hi]
    i = j = 0
    k = lo
    while i < len(esq) and j < len(dir_):
        if esq[i] <= dir_[j]:
            d[k] = esq[i]
            i += 1
        else:
            d[k] = dir_[j]
            j += 1
        yield (k,)
        k += 1
    for resto in (esq[i:], dir_[j:]):
        for v in resto:
            d[k] = v
            yield (k,)
            k += 1


def tim_sort(d):
    """Tim Sort simplificado: insertion sort em 'runs' de 16 + merges bottom-up."""
    n = len(d)
    run = 16
    for ini in range(0, n, run):
        yield from _inserir_faixa(d, ini, min(ini + run, n))
    tam = run
    while tam < n:
        for esq in range(0, n, 2 * tam):
            mid = min(esq + tam, n)
            dir_ = min(esq + 2 * tam, n)
            if mid < dir_:
                yield from _merge_faixa(d, esq, mid, dir_)
        tam *= 2


def _heap_faixa(d, lo, hi):
    """Heap sort em d[lo..hi] (inclusive)."""
    n = hi - lo + 1

    def peneirar(m, i):
        while True:
            maior = i
            e, r = 2 * i + 1, 2 * i + 2
            if e < m and d[lo + e] > d[lo + maior]:
                maior = e
            if r < m and d[lo + r] > d[lo + maior]:
                maior = r
            yield (lo + i, lo + maior)
            if maior == i:
                return
            d[lo + i], d[lo + maior] = d[lo + maior], d[lo + i]
            i = maior

    for i in range(n // 2 - 1, -1, -1):
        yield from peneirar(n, i)
    for fim in range(n - 1, 0, -1):
        d[lo], d[lo + fim] = d[lo + fim], d[lo]
        yield (lo, lo + fim)
        yield from peneirar(fim, 0)


def _intro(d, lo, hi, prof):
    while hi - lo > 16:
        if prof == 0:                      # recursão funda demais: troca para heap sort
            yield from _heap_faixa(d, lo, hi)
            return
        prof -= 1
        pivo = d[hi]
        i = lo
        for j in range(lo, hi):
            yield (j, hi)
            if d[j] < pivo:
                d[i], d[j] = d[j], d[i]
                i += 1
        d[i], d[hi] = d[hi], d[i]
        yield (i, hi)
        yield from _intro(d, lo, i - 1, prof)
        lo = i + 1
    yield from _inserir_faixa(d, lo, hi + 1)


def intro_sort(d):
    """Intro Sort: quick sort + heap sort (se a recursão ficar funda) + insertion (faixas pequenas)."""
    yield from _intro(d, 0, len(d) - 1, 2 * int(math.log2(len(d))))


def bogo_sort(d):
    """Bogo Sort: embaralha até ficar ordenado. Só pela graça (6 barras)."""
    while any(d[i] > d[i + 1] for i in range(len(d) - 1)):
        random.shuffle(d)
        yield ()


bogo_sort.n = 6


# ---------------------------------------------------------------------
#  Novos algoritmos de busca (yield = dict {índice: cor})
# ---------------------------------------------------------------------

def busca_interpolacao(d, alvo):
    lo, hi = 0, len(d) - 1
    while lo <= hi and d[lo] <= alvo <= d[hi]:
        if d[hi] == d[lo]:
            pos = lo
        else:
            pos = lo + (alvo - d[lo]) * (hi - lo) // (d[hi] - d[lo])
        cores = {i: CINZA_ESC for i in range(len(d)) if i < lo or i > hi}
        cores[lo] = AZUL
        cores[hi] = AZUL
        cores[pos] = VERMELHO
        yield cores
        if d[pos] == alvo:
            cores[pos] = VERDE
            yield cores
            return
        if d[pos] < alvo:
            lo = pos + 1
        else:
            hi = pos - 1


def busca_exponencial(d, alvo):
    n = len(d)
    cores = {}
    i = 1
    if d[0] == alvo:
        cores[0] = VERDE
        yield cores
        return
    while i < n and d[i] <= alvo:
        cores[i] = AZUL
        yield cores
        i *= 2
    lo, hi = i // 2, min(i, n - 1)
    while lo <= hi:
        mid = (lo + hi) // 2
        c = dict(cores)
        c[mid] = VERMELHO
        yield c
        if d[mid] == alvo:
            c[mid] = VERDE
            cores.clear()
            cores.update(c)
            yield cores
            return
        if d[mid] < alvo:
            lo = mid + 1
        else:
            hi = mid - 1


def busca_ternaria(d, alvo):
    lo, hi = 0, len(d) - 1
    while lo <= hi:
        m1 = lo + (hi - lo) // 3
        m2 = hi - (hi - lo) // 3
        cores = {i: CINZA_ESC for i in range(len(d)) if i < lo or i > hi}
        cores[m1] = VERMELHO
        cores[m2] = VERMELHO
        yield cores
        if d[m1] == alvo:
            cores[m1] = VERDE
            yield cores
            return
        if d[m2] == alvo:
            cores[m2] = VERDE
            yield cores
            return
        if alvo < d[m1]:
            hi = m1 - 1
        elif alvo > d[m2]:
            lo = m2 + 1
        else:
            lo, hi = m1 + 1, m2 - 1


def busca_fibonacci(d, alvo):
    n = len(d)
    f2, f1 = 0, 1
    f = f1 + f2
    while f < n:
        f2, f1 = f1, f
        f = f1 + f2
    offset = -1
    cores = {}
    while f > 1:
        i = min(offset + f2, n - 1)
        c = dict(cores)
        c[i] = VERMELHO
        yield c
        if d[i] < alvo:
            f, f1, f2 = f1, f2, f1 - f2
            offset = i
            for j in range(0, i + 1):
                cores[j] = CINZA_ESC
        elif d[i] > alvo:
            f, f1, f2 = f2, f1 - f2, f2 - (f1 - f2)
        else:
            c[i] = VERDE
            cores.clear()
            cores.update(c)
            yield cores
            return
    if f1 and offset + 1 < n and d[offset + 1] == alvo:
        cores[offset + 1] = VERDE
        yield cores


# ---------------------------------------------------------------------
#  Cenas
# ---------------------------------------------------------------------

class Barras(Cena):
    N = 80

    def desenhar_cena(self, tela):
        n = len(self.dados)
        larg = LARGURA / n
        maximo = max(self.dados)
        area = ALTURA - TOPO - 14
        for i, v in enumerate(self.dados):
            h = int(v / maximo * area)
            x = int(i * larg)
            w = max(1, int((i + 1) * larg) - x - 1)
            pygame.draw.rect(tela, self.cor_barra(i), (x, ALTURA - h, w, h))


class Ordenacao(Barras):
    titulo = "Ordenação"
    vel_inicial = 7
    ajuda = ("Vetor de 80 barras (bitonic usa 64, bogo usa 6). Vermelho = posições comparadas/escritas.",
             "R: embaralhar    TAB: lista com os 18 algoritmos e suas complexidades")
    algoritmos = [
        ("Bubble Sort", bubble_sort, "O(n²)"),
        ("Selection Sort", selection_sort, "O(n²)"),
        ("Insertion Sort", insertion_sort, "O(n²)"),
        ("Shell Sort", shell_sort, "~O(n^1.3)"),
        ("Merge Sort", merge_sort, "O(n log n)"),
        ("Quick Sort", quick_sort, "O(n log n) médio"),
        ("Heap Sort", heap_sort, "O(n log n)"),
        ("Counting Sort", counting_sort, "O(n + k)"),
        ("Radix Sort (LSD)", radix_sort, "O(d·(n + b))"),
        ("Comb Sort", comb_sort, "O(n²) pior"),
        ("Cocktail Shaker Sort", cocktail_sort, "O(n²)"),
        ("Gnome Sort", gnome_sort, "O(n²)"),
        ("Odd-Even Sort", odd_even_sort, "O(n²)"),
        ("Cycle Sort", cycle_sort, "O(n²), mín. escritas"),
        ("Bitonic Sort (64 barras)", bitonic_sort, "O(n log² n)"),
        ("Tim Sort (simplificado)", tim_sort, "O(n log n)"),
        ("Intro Sort", intro_sort, "O(n log n)"),
        ("Bogo Sort (6 barras)", bogo_sort, "O((n+1)!)"),
    ]

    def reiniciar(self, tam=None):
        self.tam = tam or self.N
        self.dados = random.sample(range(10, 500), self.tam)
        self.gerador = None
        self.terminou = False
        self.ultimo = ()
        self.passos = 0

    def iniciar(self, funcao):
        self.reiniciar(getattr(funcao, "n", None))
        self.comecar(funcao(self.dados))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
            self.reiniciar(self.tam)

    def cor_barra(self, i):
        if self.terminou:
            return VERDE
        return VERMELHO if self.ultimo and i in self.ultimo else BRANCO


class Busca(Barras):
    titulo = "Busca"
    N = 60
    vel_inicial = 3
    ajuda = ("Vetor ordenado de 60 barras. Amarelo = alvo, azul = limites, vermelho = posição testada, verde = achou.",
             "R: novo vetor e novo alvo")
    algoritmos = [
        ("Busca Linear", busca_linear, "O(n)"),
        ("Busca Binária", busca_binaria, "O(log n)"),
        ("Busca por Salto (Jump)", busca_salto, "O(√n)"),
        ("Busca por Interpolação", busca_interpolacao, "O(log log n) médio"),
        ("Busca Exponencial", busca_exponencial, "O(log n)"),
        ("Busca Ternária", busca_ternaria, "O(log₃ n)"),
        ("Busca de Fibonacci", busca_fibonacci, "O(log n)"),
    ]

    def reiniciar(self):
        self.dados = sorted(random.sample(range(10, 500), self.N))
        self.alvo = random.choice(self.dados)
        self.gerador = None
        self.terminou = False
        self.ultimo = {}
        self.passos = 0
        self.info = f"Alvo: {self.alvo} (barra amarela)"

    def iniciar(self, funcao):
        self.reiniciar()
        self.comecar(funcao(self.dados, self.alvo))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
            self.reiniciar()

    def cor_barra(self, i):
        if self.ultimo and i in self.ultimo:
            return self.ultimo[i]
        return AMARELO if self.dados[i] == self.alvo else BRANCO
