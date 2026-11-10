"""Estruturas em árvore: Heap binário, Trie, Huffman, B-Tree e Union-Find."""
import bisect
import heapq
import math
import random
from collections import Counter

import pygame

from .base import *


def layout_floresta(raizes, filhos, x0, x1, y0, dy, passo_max=70):
    """Layout de várias árvores lado a lado (largura proporcional ao número de folhas)."""
    def folhas(n):
        fs = [f for f in filhos(n) if f is not None]
        return 1 if not fs else sum(folhas(f) for f in fs)

    pesos = [folhas(r) for r in raizes]
    total = sum(pesos) or 1
    pos, x = {}, x0
    for r, p in zip(raizes, pesos):
        w = (x1 - x0) * p / total
        pos.update(layout_folhas(r, filhos, x, x + w, y0, dy, passo_max))
        x += w
    return pos


def _nomear(cena, i=0):
    cena.alg_idx = i
    item = cena.algoritmos[i]
    cena.nome = item[0]
    cena.complexidade = item[2] if len(item) > 2 else ""


# =====================================================================
#  HEAP BINÁRIO
# =====================================================================

class Heap(Cena):
    titulo = "Heap binário"
    digitos_algoritmo = False
    aceita = "num"
    max_entrada = 3
    LIMITE = 31
    ajuda = ("Número + ENTER: inserir (vazio = aleatório)   E: extrair a raiz   "
             "B: construir heap de 15 valores (heapify)   C: limpar",
             "TAB: Min-Heap ou Max-Heap. O vetor (embaixo) e a árvore são a mesma estrutura.")
    algoritmos = [("Min-Heap", "min", "inserir/extrair O(log n)"),
                  ("Max-Heap", "max", "inserir/extrair O(log n)")]

    def reiniciar(self):
        self.tipo = "min"
        self.a = []
        self.dest = {}
        self.msg = ""
        self.extraidos = []
        self.gerador = None
        _nomear(self)

    def iniciar(self, tipo):
        self.reiniciar()
        self.tipo = tipo
        _nomear(self, 0 if tipo == "min" else 1)

    def melhor(self, x, y):
        return x < y if self.tipo == "min" else x > y

    def _subir(self, i):
        a = self.a
        while i > 0:
            p = (i - 1) // 2
            self.dest = {i: AMARELO, p: AMARELO}
            yield
            if self.melhor(a[i], a[p]):
                a[i], a[p] = a[p], a[i]
                i = p
            else:
                break
        self.dest = {i: VERDE}

    def _descer(self, i):
        a = self.a
        n = len(a)
        while True:
            m, e, d = i, 2 * i + 1, 2 * i + 2
            if e < n and self.melhor(a[e], a[m]):
                m = e
            if d < n and self.melhor(a[d], a[m]):
                m = d
            self.dest = {j: AMARELO for j in (i, e, d) if j < n}
            yield
            if m == i:
                break
            a[i], a[m] = a[m], a[i]
            i = m
        self.dest = {}

    def _inserir(self, v):
        self.a.append(v)
        self.msg = f"{v} inserido (sobe enquanto for melhor que o pai)"
        yield from self._subir(len(self.a) - 1)

    def _extrair(self):
        a = self.a
        raiz = a[0]
        a[0] = a[-1]
        a.pop()
        self.extraidos.append(raiz)
        self.msg = f"{raiz} extraído (último sobe à raiz e desce)"
        if a:
            yield from self._descer(0)

    def _construir(self):
        self.a = random.sample(range(1, 100), 15)
        self.extraidos = []
        self.msg = "Heapify: peneira de n/2-1 até 0"
        yield
        for i in range(len(self.a) // 2 - 1, -1, -1):
            yield from self._descer(i)

    def ao_enter(self):
        if self.gerador is not None:
            return
        if len(self.a) >= self.LIMITE:
            self.msg = f"Limite de {self.LIMITE} elementos"
            return
        v = int(self.entrada) if self.entrada else random.randint(1, 99)
        self.entrada = ""
        self.comecar(self._inserir(v))

    def evento_cena(self, e):
        if e.type != pygame.KEYDOWN or self.gerador is not None:
            return
        if e.key == pygame.K_e and self.a:
            self.comecar(self._extrair())
        elif e.key == pygame.K_b:
            self.comecar(self._construir())
        elif e.key == pygame.K_c:
            self.reiniciar()
            _nomear(self, 0 if self.tipo == "min" else 1)

    def desenhar_cena(self, tela):
        a = self.a
        pos = []
        for i in range(len(a)):
            nivel = int(math.log2(i + 1))
            idx = i + 1 - 2 ** nivel
            pos.append((int(20 + (idx + 0.5) / 2 ** nivel * (LARGURA - 40)), TOPO + 40 + nivel * 66))
        for i in range(1, len(a)):
            pygame.draw.line(tela, CINZA, pos[i], pos[(i - 1) // 2], 2)
        for i, v in enumerate(a):
            desenhar_no(tela, pos[i], v, self.dest.get(i, BRANCO), 17)
        # vetor
        if a:
            larg = min(32, (LARGURA - 40) // len(a))
            x0 = (LARGURA - larg * len(a)) // 2
            for i, v in enumerate(a):
                r = pygame.Rect(x0 + i * larg, ALTURA - 70, larg - 2, 28)
                pygame.draw.rect(tela, self.dest.get(i, (50, 50, 65)), r, border_radius=4)
                texto(tela, v, r.centerx, r.y + 6, "p", PRETO if i in self.dest else BRANCO, centro=True)
                texto(tela, i, r.centerx, r.bottom + 2, "p", CINZA, centro=True)
        if self.extraidos:
            texto(tela, "Extraídos: " + " ".join(map(str, self.extraidos)), 10, ALTURA - 26, "m", CIANO)
        self.info = f"Valor: {self.entrada}_   {self.msg}"


# =====================================================================
#  TRIE
# =====================================================================

class TNo:
    def __init__(self, letra=""):
        self.letra = letra
        self.filhos = {}
        self.fim = False


def trie_inserir(g, p):
    no = g.raiz
    g.dest = {no: AMARELO}
    yield
    for ch in p:
        if ch not in no.filhos:
            no.filhos[ch] = TNo(ch)
        no = no.filhos[ch]
        g.dest[no] = AMARELO
        yield
    no.fim = True
    g.dest[no] = VERDE
    g.msg = f"'{p}' inserida"


def _trie_descer(g, p):
    """Desce pelo prefixo p; devolve o nó final ou None."""
    no = g.raiz
    g.dest = {no: AMARELO}
    yield
    for ch in p:
        if ch not in no.filhos:
            g.dest[no] = VERMELHO
            yield
            return None
        no = no.filhos[ch]
        g.dest[no] = AMARELO
        yield
    return no


def trie_buscar(g, p):
    no = yield from _trie_descer(g, p)
    if no is None:
        g.msg = f"'{p}' não existe"
    elif no.fim:
        g.dest[no] = VERDE
        g.msg = f"'{p}' encontrada"
    else:
        g.dest[no] = LARANJA
        g.msg = f"'{p}' é só um prefixo, não uma palavra"


def trie_autocompletar(g, p):
    no = yield from _trie_descer(g, p)
    if no is None:
        g.msg = f"nenhuma palavra começa com '{p}'"
        return
    achados = []

    def dfs(n, pref):
        if n.fim:
            achados.append(pref)
            g.dest[n] = VERDE
            yield
        for ch in sorted(n.filhos):
            g.dest[n.filhos[ch]] = AMARELO
            yield from dfs(n.filhos[ch], pref + ch)

    yield from dfs(no, p)
    g.msg = f"{p}* -> " + (", ".join(achados) or "(nada)")


PALAVRAS_EXEMPLO = ["casa", "caso", "carro", "cara", "corpo", "coro", "pato", "pote"]


def trie_exemplo(g, _=""):
    for w in PALAVRAS_EXEMPLO:
        yield from trie_inserir(g, w)
    g.dest = {}
    g.msg = "Palavras de exemplo carregadas"


class Trie(Cena):
    titulo = "Trie"
    digitos_algoritmo = False
    aceita = "letras"
    max_entrada = 10
    vel_inicial = 4
    ajuda = ("Escolha a operação com TAB; digite letras (a-z) e aperte ENTER para executar.",
             "Nós com borda verde marcam fim de palavra. Comece com 'Carregar palavras de exemplo'.")
    algoritmos = [("Inserir palavra", trie_inserir, "O(L)"),
                  ("Buscar palavra", trie_buscar, "O(L)"),
                  ("Autocompletar prefixo", trie_autocompletar, "O(L + k)"),
                  ("Carregar palavras de exemplo", trie_exemplo)]

    def reiniciar(self):
        self.raiz = TNo()
        self.dest = {}
        self.msg = ""
        self.gerador = None
        self.op = trie_inserir
        _nomear(self)

    def iniciar(self, funcao):
        self.op = funcao
        if funcao is trie_exemplo:
            self.dest = {}
            self.comecar(funcao(self))

    def ao_enter(self):
        if self.gerador is not None:
            return
        if self.op is trie_exemplo:
            self.comecar(trie_exemplo(self))
        elif self.entrada:
            p, self.entrada = self.entrada, ""
            self.comecar(self.op(self, p))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_DELETE:
            self.reiniciar()

    def desenhar_cena(self, tela):
        filhos = lambda n: [n.filhos[c] for c in sorted(n.filhos)]
        pos = layout_folhas(self.raiz, filhos, 20, LARGURA - 20, TOPO + 36, 54, passo_max=60)
        for no, (x, y) in pos.items():
            for f in filhos(no):
                pygame.draw.line(tela, CINZA, (x, y), pos[f], 2)
        for no, (x, y) in pos.items():
            cor = self.dest.get(no, BRANCO if no is not self.raiz else CINZA)
            pygame.draw.circle(tela, cor, (x, y), 14)
            if no.fim:
                pygame.draw.circle(tela, VERDE, (x, y), 14, 3)
            texto(tela, no.letra or "*", x, y - 7, "p", PRETO, centro=True)
        self.info = f"Texto: {self.entrada}_   {self.msg}"


# =====================================================================
#  HUFFMAN
# =====================================================================

class HNo:
    def __init__(self, freq, char=None, esq=None, dir_=None, ordem=0):
        self.freq, self.char, self.esq, self.dir, self.ordem = freq, char, esq, dir_, ordem


def huffman_codigos(raiz):
    codigos = {}

    def rec(n, c):
        if n.char is not None:
            codigos[n.char] = c or "0"
            return
        rec(n.esq, c + "0")
        rec(n.dir, c + "1")

    rec(raiz, "")
    return codigos


def huffman(g, s):
    freq = Counter(s)
    g.freq = dict(freq)
    g.raiz, g.codigos = None, {}
    ordem = 0
    floresta = []
    for c, f in sorted(freq.items(), key=lambda kv: (kv[1], kv[0])):
        floresta.append(HNo(f, c, ordem=ordem))
        ordem += 1
    g.floresta = list(floresta)
    g.dest = {}
    g.msg = "Frequências contadas: junte sempre os dois menores"
    yield
    while len(floresta) > 1:
        floresta.sort(key=lambda n: (n.freq, n.ordem))
        a, b = floresta[0], floresta[1]
        g.dest = {a: AMARELO, b: AMARELO}
        g.msg = f"Juntando {a.freq} + {b.freq} = {a.freq + b.freq}"
        yield
        pai = HNo(a.freq + b.freq, None, a, b, ordem)
        ordem += 1
        floresta = floresta[2:] + [pai]
        g.floresta = list(floresta)
        g.dest = {pai: VERDE}
        yield
    g.raiz = floresta[0]
    g.codigos = huffman_codigos(g.raiz)
    bits = sum(freq[c] * len(cod) for c, cod in g.codigos.items())
    g.dest = {}
    g.msg = f"Original: {8 * len(s)} bits   Huffman: {bits} bits   ({bits / (8 * len(s)):.0%})"


class Huffman(Cena):
    titulo = "Codificação de Huffman"
    digitos_algoritmo = False
    aceita = "texto"
    max_entrada = 24
    vel_inicial = 2
    ajuda = ("Digite um texto (letras e espaço) e aperte ENTER. Vazio = 'abracadabra alakazam'.",
             "O algoritmo junta repetidamente as duas árvores de menor frequência. Aresta esquerda = 0, direita = 1.")
    algoritmos = [("Árvore de Huffman", huffman, "O(n log n)")]

    def reiniciar(self):
        self.floresta, self.raiz, self.codigos, self.dest = [], None, {}, {}
        self.msg = ""
        self.texto_atual = ""
        self.gerador = None
        _nomear(self)

    def iniciar(self, funcao):
        pass

    def ao_enter(self):
        if self.gerador is not None:
            return
        s = self.entrada.strip() or "abracadabra alakazam"
        self.entrada = ""
        self.texto_atual = s
        self.comecar(huffman(self, s))

    def desenhar_cena(self, tela):
        filhos = lambda n: [n.esq, n.dir]
        raizes = [self.raiz] if self.raiz else self.floresta
        if raizes:
            pos = layout_floresta(raizes, filhos, 20, LARGURA - 20, TOPO + 36, 52, passo_max=64)
            for no, (x, y) in pos.items():
                for i, f in enumerate(filhos(no)):
                    if f is not None:
                        pygame.draw.line(tela, CINZA, (x, y), pos[f], 2)
                        if self.raiz:
                            mx, my = (x + pos[f][0]) // 2, (y + pos[f][1]) // 2
                            texto(tela, str(i), mx + (-9 if i == 0 else 3), my - 8, "p", AMARELO)
            for no, (x, y) in pos.items():
                cor = self.dest.get(no, BRANCO)
                if no.char is not None:
                    pygame.draw.rect(tela, cor, (x - 16, y - 14, 32, 28), border_radius=6)
                    texto(tela, "_" if no.char == " " else no.char, x, y - 13, "p", PRETO, centro=True)
                    texto(tela, no.freq, x, y - 1, "p", PRETO, centro=True)
                else:
                    desenhar_no(tela, (x, y), no.freq, cor, 15)
        if self.codigos:
            texto(tela, "Códigos:", 10, ALTURA - 112, "m", CIANO)
            itens = sorted(self.codigos.items(), key=lambda kv: (len(kv[1]), kv[0]))
            for k, (c, cod) in enumerate(itens):
                col, lin = divmod(k, 4)
                texto(tela, f"{'_' if c == ' ' else c}: {cod}", 10 + col * 130, ALTURA - 90 + lin * 20, "m", BRANCO)
        self.info = f"Texto: {self.entrada}_   {self.msg}"


# =====================================================================
#  B-TREE (inserção, estilo CLRS: divide nós cheios na descida)
# =====================================================================

class BNo:
    def __init__(self, folha=True):
        self.chaves = []
        self.filhos = []
        self.folha = folha


def b_contem(no, k):
    while True:
        i = bisect.bisect_left(no.chaves, k)
        if i < len(no.chaves) and no.chaves[i] == k:
            return True
        if no.folha:
            return False
        no = no.filhos[i]


def b_dividir(pai, i, t):
    y = pai.filhos[i]
    z = BNo(y.folha)
    mediana = y.chaves[t - 1]
    z.chaves = y.chaves[t:]
    y.chaves = y.chaves[:t - 1]
    if not y.folha:
        z.filhos = y.filhos[t:]
        y.filhos = y.filhos[:t]
    pai.filhos.insert(i + 1, z)
    pai.chaves.insert(i, mediana)


def _b_ins(no, k, t):
    yield {no: AMARELO}
    if no.folha:
        bisect.insort(no.chaves, k)
        yield {no: VERDE}
        return
    i = bisect.bisect_left(no.chaves, k)
    if len(no.filhos[i].chaves) == 2 * t - 1:
        yield {no.filhos[i]: VERMELHO}           # nó cheio: será dividido
        b_dividir(no, i, t)
        yield {no: VERDE}
        if k > no.chaves[i]:
            i += 1
    yield from _b_ins(no.filhos[i], k, t)


def btree_inserir(g, k):
    t = g.t
    if g.raiz is None:
        g.raiz = BNo(True)
    if b_contem(g.raiz, k):
        g.msg = f"{k} já existe"
        return
    raiz = g.raiz
    if len(raiz.chaves) == 2 * t - 1:
        yield {raiz: VERMELHO}
        nova = BNo(False)
        nova.filhos = [raiz]
        g.raiz = nova
        b_dividir(nova, 0, t)
        g.n_nos_altura += 1
        yield {nova: VERDE}
        raiz = nova
    yield from _b_ins(raiz, k, t)
    g.msg = f"{k} inserido"


class BTree(Cena):
    titulo = "B-Tree"
    digitos_algoritmo = False
    aceita = "num"
    max_entrada = 3
    ajuda = ("Número + ENTER: inserir (vazio = aleatório)   C: limpar   TAB: grau mínimo t",
             "Nós cheios (vermelhos) são divididos na descida; a mediana sobe para o pai. Todas as folhas ficam no mesmo nível.")
    algoritmos = [("B-Tree t=2 (2-3-4, até 3 chaves)", 2, "O(log n)"),
                  ("B-Tree t=3 (até 5 chaves)", 3, "O(log n)")]
    LIMITES = {2: 24, 3: 30}

    def reiniciar(self):
        self.t = 2
        self.raiz = None
        self.dest = {}
        self.msg = ""
        self.n_nos_altura = 1
        self.gerador = None
        self.chaves_total = 0
        _nomear(self)

    def iniciar(self, t):
        self.reiniciar()
        self.t = t
        _nomear(self, 0 if t == 2 else 1)

    def contar(self, no=None):
        if no is None:
            no = self.raiz
        if no is None:
            return 0
        return len(no.chaves) + sum(self.contar(f) for f in no.filhos)

    def ao_enter(self):
        if self.gerador is not None:
            return
        if self.contar() >= self.LIMITES[self.t]:
            self.msg = "Limite de chaves da demonstração"
            return
        if self.entrada:
            v = int(self.entrada)
        else:
            v = random.randint(1, 99)
            while self.raiz and b_contem(self.raiz, v):
                v = random.randint(1, 99)
        self.entrada = ""
        self.comecar(btree_inserir(self, v))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_c and self.gerador is None:
            self.iniciar(self.t)

    def _larg(self, no):
        return 10 + 24 * max(len(no.chaves), 1)

    def desenhar_cena(self, tela):
        if self.raiz is not None:
            pos = layout_folhas(self.raiz, lambda n: n.filhos, 20, LARGURA - 20, TOPO + 50, 90, passo_max=170)
            for no, (x, y) in pos.items():
                for f in no.filhos:
                    pygame.draw.line(tela, CINZA, (x, y + 14), (pos[f][0], pos[f][1] - 14), 2)
            for no, (x, y) in pos.items():
                w = self._larg(no)
                r = pygame.Rect(x - w // 2, y - 14, w, 28)
                pygame.draw.rect(tela, self.dest.get(no, (50, 50, 70)), r, border_radius=5)
                pygame.draw.rect(tela, BRANCO, r, 2, border_radius=5)
                cor_txt = PRETO if no in self.dest else BRANCO
                for i, k in enumerate(no.chaves):
                    texto(tela, k, r.x + 5 + 24 * i + 12, r.y + 6, "p", cor_txt, centro=True)
        self.info = f"Valor: {self.entrada}_   {self.msg}"


# =====================================================================
#  UNION-FIND (conjuntos disjuntos)
# =====================================================================

def uf_find(g, x, comprimir):
    caminho = [x]
    g.dest = {x: AMARELO}
    yield
    while g.pai[x] != x:
        x = g.pai[x]
        caminho.append(x)
        g.dest[x] = AMARELO
        yield
    raiz = x
    if comprimir:
        for n in caminho[:-1]:
            if g.pai[n] != raiz:
                g.pai[n] = raiz
                g.dest[n] = VERDE
                yield
    return raiz


def uf_uniao_otimizada(g, a, b):
    ra = yield from uf_find(g, a, True)
    rb = yield from uf_find(g, b, True)
    if ra == rb:
        g.msg = f"{a} e {b} já estão no mesmo conjunto"
        return
    if g.rank[ra] < g.rank[rb]:
        ra, rb = rb, ra
    g.pai[rb] = ra
    if g.rank[ra] == g.rank[rb]:
        g.rank[ra] += 1
    g.dest = {ra: VERDE, rb: VERDE}
    g.msg = f"União por rank: {rb} passa a apontar para {ra}"
    yield


def uf_uniao_ingenua(g, a, b):
    ra = yield from uf_find(g, a, False)
    rb = yield from uf_find(g, b, False)
    if ra == rb:
        g.msg = f"{a} e {b} já estão no mesmo conjunto"
        return
    g.pai[ra] = rb                       # sempre pendura a primeira raiz na segunda
    g.dest = {ra: VERDE, rb: VERDE}
    g.msg = f"União ingênua: {ra} passa a apontar para {rb}"
    yield


def uf_buscar(g, a, _=None):
    raiz = yield from uf_find(g, a, True)
    g.dest[raiz] = VERDE
    g.msg = f"find({a}) = {raiz} (caminho comprimido)"


class UnionFind(Cena):
    titulo = "Union-Find"
    digitos_algoritmo = False
    aceita = "numesp"
    max_entrada = 5
    N = 14
    vel_inicial = 3
    ajuda = (f"Digite 'a b' (0 a 13) + ENTER para unir; vazio = par aleatório. Em 'Find', digite só 'a'.   C: reiniciar",
             "TAB: com otimizações (rank + compressão) ou ingênuo. Compare a altura das árvores após várias uniões.")
    algoritmos = [("União por rank + compressão de caminho", uf_uniao_otimizada, "α(n) amortizado"),
                  ("União ingênua (sem otimização)", uf_uniao_ingenua, "O(n) por operação"),
                  ("Find com compressão de caminho", uf_buscar, "α(n) amortizado")]

    def reiniciar(self):
        self.pai = list(range(self.N))
        self.rank = [0] * self.N
        self.dest = {}
        self.msg = ""
        self.gerador = None
        self.op = uf_uniao_otimizada
        _nomear(self)

    def iniciar(self, funcao):
        self.op = funcao

    def altura_max(self):
        def h(x):
            n = 0
            while self.pai[x] != x:
                x = self.pai[x]
                n += 1
            return n
        return max(h(i) for i in range(self.N))

    def ao_enter(self):
        if self.gerador is not None:
            return
        nums = [int(x) for x in self.entrada.split() if x.isdigit()]
        self.entrada = ""
        if self.op is uf_buscar:
            a = nums[0] if nums else random.randrange(self.N)
            if a < self.N:
                self.comecar(uf_buscar(self, a))
            return
        if len(nums) >= 2:
            a, b = nums[0], nums[1]
        else:
            a, b = random.sample(range(self.N), 2)
        if a < self.N and b < self.N:
            self.comecar(self.op(self, a, b))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_c and self.gerador is None:
            self.reiniciar()
            _nomear(self, self.algoritmos.index(next(a for a in self.algoritmos if a[1] is self.op)))

    def desenhar_cena(self, tela):
        filhos_de = {i: [] for i in range(self.N)}
        for i, p in enumerate(self.pai):
            if p != i:
                filhos_de[p].append(i)
        raizes = [i for i in range(self.N) if self.pai[i] == i]
        pos = layout_floresta(raizes, lambda n: filhos_de[n], 20, LARGURA - 20, TOPO + 60, 62, passo_max=56)
        for i, p in enumerate(self.pai):
            if p != i:
                seta(tela, pos[i], pos[p], CINZA, 2, recuo=16, ponta=9)
        for i, (x, y) in pos.items():
            desenhar_no(tela, (x, y), i, self.dest.get(i, BRANCO), 15)
            if self.pai[i] == i:
                texto(tela, f"rank {self.rank[i]}", x, y - 34, "p", CINZA, centro=True)
        self.info = f"Entrada: {self.entrada}_   conjuntos: {len(raizes)}   altura máx: {self.altura_max()}   {self.msg}"
