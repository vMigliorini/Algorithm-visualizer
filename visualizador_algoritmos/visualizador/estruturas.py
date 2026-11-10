"""Estruturas de dados: tabelas hash (encadeamento, sondagem linear, hash duplo), lista ligada
(com inversão animada), pilha, fila, cache LRU, skip list e Bloom filter.

Cada estrutura mantém seu próprio estado: escolha a operação com TAB, digite um valor
e aperte ENTER (vazio = valor aleatório)."""
import math
import random

import pygame

from .base import *

PALAVRAS = ["gato", "cao", "rato", "pato", "lobo", "urso", "foca", "vaca", "peixe", "zebra", "tigre", "coala"]
M_ENC, M_OA, MAX_NIVEL = 8, 11, 4
LIMITES = {"lista": 10, "pilha": 10, "fila": 10, "skip": 12}


def _k(s):
    """Chave inteira de um texto (números valem eles mesmos)."""
    return int(s) if s.isdigit() else sum(ord(c) * (i + 1) for i, c in enumerate(s))


# ---------------------------------------------------------------------
#  Tabelas hash
# ---------------------------------------------------------------------

def hash_enc_inserir(g, s):
    k = _k(s)
    b = k % M_ENC
    g.dest = {(b, -1): AMARELO}
    g.msg = f"h({s}) = {k} mod {M_ENC} = {b}"
    yield
    cadeia = g.baldes[b]
    for i, x in enumerate(cadeia):
        g.dest = {(b, i): AMARELO}
        yield
        if x == s:
            g.dest = {(b, i): LARANJA}
            g.msg = f"{s} já existe"
            return
    cadeia.append(s)
    g.dest = {(b, len(cadeia) - 1): VERDE}
    g.msg = f"{s} inserido no balde {b}" + (" (colisão: entra na cadeia)" if len(cadeia) > 1 else "")


def hash_enc_buscar(g, s):
    b = _k(s) % M_ENC
    g.dest = {(b, -1): AMARELO}
    g.msg = f"h({s}) = {b}"
    yield
    for i, x in enumerate(g.baldes[b]):
        g.dest = {(b, i): AMARELO}
        yield
        if x == s:
            g.dest = {(b, i): VERDE}
            g.msg = f"{s} encontrado no balde {b}"
            return
    g.dest = {(b, -1): VERMELHO}
    g.msg = f"{s} não encontrado"


def _sondar(g, tab, s, passo, inserir):
    k = _k(s)
    for i in range(M_OA):
        idx = passo(k, i) % M_OA
        g.dest = {idx: AMARELO}
        g.msg = f"tentativa {i + 1}: posição {idx}"
        yield
        x = tab[idx]
        if inserir:
            if x is None:
                tab[idx] = s
                g.dest = {idx: VERDE}
                g.msg = f"{s} inserido na posição {idx} após {i} colisão(ões)"
                return True
            if x == s:
                g.dest = {idx: LARANJA}
                g.msg = f"{s} já existe"
                return False
        else:
            if x is None:
                g.dest = {idx: VERMELHO}
                g.msg = f"{s} não encontrado (casa vazia)"
                return False
            if x == s:
                g.dest = {idx: VERDE}
                g.msg = f"{s} encontrado na posição {idx}"
                return True
        g.dest = {idx: VERMELHO}
        yield
    g.msg = "Tabela cheia" if inserir else f"{s} não encontrado"
    return False


def _passo_linear(k, i):
    return k % M_OA + i


def _passo_duplo(k, i):
    return k % M_OA + i * (7 - k % 7)


def hash_lin_inserir(g, s):
    return _sondar(g, g.tab_lin, s, _passo_linear, True)


def hash_lin_buscar(g, s):
    return _sondar(g, g.tab_lin, s, _passo_linear, False)


def hash_dup_inserir(g, s):
    return _sondar(g, g.tab_dup, s, _passo_duplo, True)


def hash_dup_buscar(g, s):
    return _sondar(g, g.tab_dup, s, _passo_duplo, False)


# ---------------------------------------------------------------------
#  Lista ligada
# ---------------------------------------------------------------------

class LNo:
    def __init__(self, v):
        self.v = v
        self.prox = None


def lista_nos(g):
    n, out = g.cab, []
    while n is not None:
        out.append(n)
        n = n.prox
    return out


def _relayout(g):
    g.slot = {n: i for i, n in enumerate(lista_nos(g))}


def lista_inserir_inicio(g, s):
    if len(g.slot) >= LIMITES["lista"]:
        g.msg = "Lista cheia (limite da demonstração)"
        return
    novo = LNo(s)
    g.slot[novo] = -1
    g.dest = {novo: VERDE}
    g.msg = "Cria o nó e faz novo.prox = cabeça"
    yield
    novo.prox = g.cab
    g.cab = novo
    _relayout(g)
    g.msg = f"{s} inserido no início: O(1)"
    yield


def lista_inserir_fim(g, s):
    if len(g.slot) >= LIMITES["lista"]:
        g.msg = "Lista cheia (limite da demonstração)"
        return
    novo = LNo(s)
    if g.cab is None:
        g.cab = novo
        _relayout(g)
        g.dest = {novo: VERDE}
        yield
        return
    n = g.cab
    g.msg = "Percorre até o último nó: O(n)"
    while n.prox is not None:
        g.dest = {n: AMARELO}
        yield
        n = n.prox
    g.dest = {n: AMARELO}
    yield
    g.slot[novo] = len(lista_nos(g))
    g.dest = {novo: VERDE, n: AMARELO}
    yield
    n.prox = novo
    _relayout(g)
    g.msg = f"{s} inserido no fim"
    g.dest = {novo: VERDE}
    yield


def lista_remover(g, s):
    ant, n = None, g.cab
    while n is not None and n.v != s:
        g.dest = {n: AMARELO}
        yield
        ant, n = n, n.prox
    if n is None:
        g.dest = {}
        g.msg = f"{s} não está na lista"
        return
    g.dest = {n: VERMELHO}
    yield
    if ant is None:
        g.cab = n.prox
    else:
        ant.prox = n.prox
    _relayout(g)
    g.dest = {ant: VERDE} if ant is not None else {}
    g.msg = f"{s} removido (o nó anterior passa a apontar para o seguinte)"
    yield


def lista_buscar(g, s):
    n = g.cab
    while n is not None:
        g.dest = {n: AMARELO}
        yield
        if n.v == s:
            g.dest = {n: VERDE}
            g.msg = f"{s} encontrado"
            return
        n = n.prox
    g.dest = {}
    g.msg = f"{s} não encontrado"


def lista_inverter(g, _=None):
    ant, atual = None, g.cab
    g.msg = "Três ponteiros: ant, atual, prox. Cada seta é invertida, um nó por vez."
    while atual is not None:
        prox = atual.prox
        g.marc = {n: t for n, t in ((ant, "ant"), (atual, "atual"), (prox, "prox")) if n is not None}
        g.dest = {atual: AMARELO}
        yield
        atual.prox = ant
        yield
        ant, atual = atual, prox
    g.cab = ant
    g.marc = {}
    g.dest = {}
    yield
    _relayout(g)
    g.msg = "Lista invertida em O(n) e O(1) de memória extra"
    yield


# ---------------------------------------------------------------------
#  Pilha e fila
# ---------------------------------------------------------------------

def pilha_push(g, s):
    if len(g.pilha) >= LIMITES["pilha"]:
        g.msg = "Pilha cheia (overflow)"
        return
    g.pilha.append(s)
    g.dest = {len(g.pilha) - 1: VERDE}
    g.msg = f"push({s})"
    yield


def pilha_pop(g, _=None):
    if not g.pilha:
        g.msg = "Pilha vazia (underflow)"
        return
    g.dest = {len(g.pilha) - 1: VERMELHO}
    yield
    g.msg = f"pop() = {g.pilha.pop()}"
    g.dest = {}
    yield


def fila_enqueue(g, s):
    if len(g.fila) >= LIMITES["fila"]:
        g.msg = "Fila cheia"
        return
    g.fila.append(s)
    g.dest = {len(g.fila) - 1: VERDE}
    g.msg = f"enqueue({s})"
    yield


def fila_dequeue(g, _=None):
    if not g.fila:
        g.msg = "Fila vazia"
        return
    g.dest = {0: VERMELHO}
    yield
    g.msg = f"dequeue() = {g.fila.pop(0)}"
    g.dest = {}
    yield


# ---------------------------------------------------------------------
#  Cache LRU (capacidade 4)
# ---------------------------------------------------------------------

CAP_LRU = 4


def lru_acessar(g, s):
    if s in g.lru:
        i = g.lru.index(s)
        g.dest = {i: VERDE}
        g.msg = f"HIT: '{s}' já estava no cache; vai para a posição de mais recente"
        yield
        g.lru.remove(s)
        g.lru.insert(0, s)
        g.dest = {0: VERDE}
        yield
        return
    g.lru.insert(0, s)
    g.dest = {0: AMARELO}
    g.msg = f"MISS: '{s}' entra como o mais recente"
    yield
    if len(g.lru) > CAP_LRU:
        g.dest = {len(g.lru) - 1: VERMELHO}
        g.msg = f"Cache cheio: despeja '{g.lru[-1]}' (o menos recentemente usado)"
        yield
        g.lru.pop()
        g.dest = {0: AMARELO}
        yield


# ---------------------------------------------------------------------
#  Skip list
# ---------------------------------------------------------------------

def _skip_proximo(nos, idx, lvl):
    j = idx + 1
    while j < len(nos) and nos[j][1] <= lvl:
        j += 1
    return j


def _skip_caminho(g, k):
    nos = g.skip
    lvl, idx = MAX_NIVEL - 1, -1
    visit = {}
    while lvl >= 0:
        while True:
            nxt = _skip_proximo(nos, idx, lvl)
            g.dest = dict(visit)
            g.dest[(idx, lvl)] = AMARELO
            yield
            if nxt < len(nos) and nos[nxt][0] < k:
                visit[(idx, lvl)] = AZUL
                idx = nxt
                continue
            break
        visit[(idx, lvl)] = AZUL
        lvl -= 1
    return idx


def skip_inserir(g, s):
    k = _k(s)
    if len(g.skip) >= LIMITES["skip"]:
        g.msg = "Skip list cheia (limite da demonstração)"
        return
    g.msg = f"Desce de cima para baixo e vai para a direita enquanto a próxima chave for < {k}"
    pred = yield from _skip_caminho(g, k)
    if pred + 1 < len(g.skip) and g.skip[pred + 1][0] == k:
        g.msg = f"{k} já existe"
        return
    nivel = 1
    while nivel < MAX_NIVEL and random.random() < 0.5:
        nivel += 1
    g.skip.insert(pred + 1, (k, nivel))
    g.dest = {(pred + 1, l): VERDE for l in range(nivel)}
    g.msg = f"{k} inserido com altura {nivel} (cara ou coroa)"
    yield


def skip_buscar(g, s):
    k = _k(s)
    g.msg = "Mesma descida da inserção"
    pred = yield from _skip_caminho(g, k)
    if pred + 1 < len(g.skip) and g.skip[pred + 1][0] == k:
        g.dest = {(pred + 1, 0): VERDE}
        g.msg = f"{k} encontrado"
    else:
        g.msg = f"{k} não encontrado"
    yield


# ---------------------------------------------------------------------
#  Bloom filter (32 bits, 3 funções de hash)
# ---------------------------------------------------------------------

M_BLOOM, K_BLOOM = 32, 3


def bloom_posicoes(s):
    pos = []
    for i in range(K_BLOOM):
        v = 17 + i * 7919
        for ch in s:
            v = (v * 131 + ord(ch)) % 1000003
        pos.append(v % M_BLOOM)
    return pos


def bloom_adicionar(g, s):
    g.msg = f"'{s}' -> posições {bloom_posicoes(s)}"
    for p in bloom_posicoes(s):
        g.dest = {p: AMARELO}
        yield
        g.bits[p] = 1
        g.dest = {p: VERDE}
        yield
    if s not in g.elementos:
        g.elementos.append(s)
    g.dest = {p: VERDE for p in bloom_posicoes(s)}


def bloom_consultar(g, s):
    pos = bloom_posicoes(s)
    g.msg = f"'{s}' -> posições {pos}"
    g.dest = {}
    for p in pos:
        g.dest[p] = AMARELO if g.bits[p] else VERMELHO
        yield
        if not g.bits[p]:
            g.msg = f"'{s}': DEFINITIVAMENTE ausente (o bit {p} é 0)"
            return
    if s in g.elementos:
        g.msg = f"'{s}': possivelmente presente (e de fato foi adicionado)"
        g.dest = {p: VERDE for p in pos}
    else:
        g.msg = f"'{s}': possivelmente presente... mas FALSO POSITIVO (nunca foi adicionado!)"
        g.dest = {p: LARANJA for p in pos}


for _f, _e in ((hash_enc_inserir, "hash_enc"), (hash_enc_buscar, "hash_enc"), (hash_lin_inserir, "hash_lin"),
               (hash_lin_buscar, "hash_lin"), (hash_dup_inserir, "hash_dup"), (hash_dup_buscar, "hash_dup"),
               (lista_inserir_inicio, "lista"), (lista_inserir_fim, "lista"), (lista_remover, "lista"),
               (lista_buscar, "lista"), (lista_inverter, "lista"), (pilha_push, "pilha"), (pilha_pop, "pilha"),
               (fila_enqueue, "fila"), (fila_dequeue, "fila"), (lru_acessar, "lru"), (skip_inserir, "skip"),
               (skip_buscar, "skip"), (bloom_adicionar, "bloom"), (bloom_consultar, "bloom")):
    _f.estrutura = _e
for _f in (lista_inverter, pilha_pop, fila_dequeue):
    _f.sem_valor = True
for _f in (lru_acessar, bloom_adicionar, bloom_consultar):
    _f.palavra = True


class Estruturas(Cena):
    titulo = "Estruturas de dados"
    digitos_algoritmo = False
    aceita = "alnum"
    max_entrada = 8
    vel_inicial = 3
    ajuda = ("TAB: escolher a operação (cada estrutura guarda o próprio estado). Digite um valor + ENTER; vazio = aleatório.",
             "C: limpa a estrutura atual. Hash/skip/lista usam números; LRU e Bloom funcionam melhor com palavras.")
    algoritmos = [
        ("Hash encadeamento: inserir", hash_enc_inserir, "O(1) médio"),
        ("Hash encadeamento: buscar", hash_enc_buscar, "O(1) médio"),
        ("Hash sondagem linear: inserir", hash_lin_inserir, "O(1) médio, clusters"),
        ("Hash sondagem linear: buscar", hash_lin_buscar, "O(1) médio"),
        ("Hash duplo: inserir", hash_dup_inserir, "O(1) médio, poucos clusters"),
        ("Hash duplo: buscar", hash_dup_buscar, "O(1) médio"),
        ("Lista ligada: inserir no início", lista_inserir_inicio, "O(1)"),
        ("Lista ligada: inserir no fim", lista_inserir_fim, "O(n)"),
        ("Lista ligada: remover valor", lista_remover, "O(n)"),
        ("Lista ligada: buscar", lista_buscar, "O(n)"),
        ("Lista ligada: INVERTER (animado)", lista_inverter, "O(n)"),
        ("Pilha: push", pilha_push, "O(1)"),
        ("Pilha: pop", pilha_pop, "O(1)"),
        ("Fila: enqueue", fila_enqueue, "O(1)"),
        ("Fila: dequeue", fila_dequeue, "O(1)"),
        ("Cache LRU (cap. 4): acessar", lru_acessar, "O(1) com hash + lista dupla"),
        ("Skip list: inserir", skip_inserir, "O(log n) esperado"),
        ("Skip list: buscar", skip_buscar, "O(log n) esperado"),
        ("Bloom filter: adicionar", bloom_adicionar, "O(k)"),
        ("Bloom filter: consultar", bloom_consultar, "O(k)"),
    ]

    def reiniciar(self):
        self.est = "hash_enc"
        self.op = hash_enc_inserir
        for e in ("hash_enc", "hash_lin", "hash_dup", "lista", "pilha", "fila", "lru", "skip", "bloom"):
            self._zerar(e)
        self.dest, self.marc, self.msg = {}, {}, ""
        self.gerador = None
        self.alg_idx = 0
        self.nome, _, self.complexidade = self.algoritmos[0]

    def _zerar(self, e):
        if e == "hash_enc":
            self.baldes = [[] for _ in range(M_ENC)]
        elif e == "hash_lin":
            self.tab_lin = [None] * M_OA
        elif e == "hash_dup":
            self.tab_dup = [None] * M_OA
        elif e == "lista":
            self.cab, self.slot = None, {}
        elif e == "pilha":
            self.pilha = []
        elif e == "fila":
            self.fila = []
        elif e == "lru":
            self.lru = []
        elif e == "skip":
            self.skip = []
        elif e == "bloom":
            self.bits, self.elementos = [0] * M_BLOOM, []

    def iniciar(self, funcao):
        self.op = funcao
        self.est = funcao.estrutura
        self.dest, self.marc, self.msg = {}, {}, ""

    def ao_enter(self):
        if self.gerador is not None:
            return
        if self.entrada:
            v = self.entrada
        elif getattr(self.op, "palavra", False):
            v = random.choice(PALAVRAS)
        else:
            v = str(random.randint(1, 99))
        self.entrada = ""
        self.comecar(self.op(self, v))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_c and self.gerador is None:
            self._zerar(self.est)
            self.dest, self.marc, self.msg = {}, {}, ""

    # ---------- desenho ----------
    def desenhar_cena(self, tela):
        getattr(self, "_d_" + self.est)(tela)
        self.info = f"Valor: {self.entrada}_   {self.msg}"

    def _caixa(self, tela, r, rot, cor=None, borda=BRANCO):
        pygame.draw.rect(tela, cor or (35, 35, 50), r, border_radius=5)
        pygame.draw.rect(tela, borda, r, 1, border_radius=5)
        texto(tela, rot, r.centerx, r.y + (r.h - 17) // 2, "m", PRETO if cor else BRANCO, centro=True)

    def _d_hash_enc(self, tela):
        for b in range(M_ENC):
            y = TOPO + 30 + b * 56
            r = pygame.Rect(60, y, 50, 40)
            self._caixa(tela, r, b, self.dest.get((b, -1)))
            for i, x in enumerate(self.baldes[b]):
                rr = pygame.Rect(150 + i * 90, y, 64, 40)
                seta(tela, (r.right if i == 0 else rr.x - 26, y + 20), (rr.x, y + 20), CINZA, 2, ponta=8)
                self._caixa(tela, rr, x, self.dest.get((b, i)))
        n = sum(len(c) for c in self.baldes)
        texto(tela, f"fator de carga = {n}/{M_ENC} = {n / M_ENC:.2f}", LARGURA - 20, TOPO + 20, "m", CINZA, direita=True)

    def _d_oa(self, tela, tab, titulo):
        texto(tela, titulo, LARGURA // 2, TOPO + 50, "g", CINZA, centro=True)
        larg = 76
        x0 = (LARGURA - M_OA * larg) // 2
        for i, x in enumerate(tab):
            r = pygame.Rect(x0 + i * larg, TOPO + 140, larg - 6, 50)
            self._caixa(tela, r, x if x is not None else "", self.dest.get(i))
            texto(tela, i, r.centerx, r.bottom + 6, "m", CINZA, centro=True)
        n = sum(x is not None for x in tab)
        texto(tela, f"fator de carga = {n}/{M_OA} = {n / M_OA:.2f}", LARGURA // 2, TOPO + 270, "m", CINZA, centro=True)

    def _d_hash_lin(self, tela):
        self._d_oa(tela, self.tab_lin, "Sondagem linear: idx = (h + i) mod 11")

    def _d_hash_dup(self, tela):
        self._d_oa(tela, self.tab_dup, "Hash duplo: idx = (h1 + i·h2) mod 11,  h2 = 7 - k mod 7")

    def _d_lista(self, tela):
        SP, x0, y = 84, 80, TOPO + 200
        for n, s in self.slot.items():
            x = x0 + (s + 1) * SP
            r = pygame.Rect(x, y, 58, 44)
            self._caixa(tela, r, n.v, self.dest.get(n))
            if n.prox is not None and n.prox in self.slot:
                x2 = x0 + (self.slot[n.prox] + 1) * SP
                if x2 > x:
                    seta(tela, (r.right, y + 22), (x2, y + 22), CINZA, 2, ponta=9)
                else:
                    seta(tela, (r.x + 29, y + 44), (x2 + 29, y + 44), LARANJA, 2, ponta=9)
            elif n.prox is None:
                texto(tela, "null", r.right + 6, y + 14, "p", CINZA)
            if n in self.marc:
                texto(tela, self.marc[n], r.centerx, y + 56, "m", AMARELO, centro=True)
            if n is self.cab:
                texto(tela, "cabeça", r.centerx, y - 30, "m", CIANO, centro=True)
                pygame.draw.line(tela, CIANO, (r.centerx, y - 12), (r.centerx, y - 2), 2)

    def _d_pilha(self, tela):
        for i, x in enumerate(self.pilha):
            r = pygame.Rect(LARGURA // 2 - 70, ALTURA - 60 - (i + 1) * 46, 140, 42)
            self._caixa(tela, r, x, self.dest.get(i))
        if self.pilha:
            texto(tela, "topo", LARGURA // 2 + 90, ALTURA - 60 - len(self.pilha) * 46 + 10, "m", CIANO)

    def _d_fila(self, tela):
        for i, x in enumerate(self.fila):
            r = pygame.Rect(60 + i * 90, TOPO + 220, 80, 50)
            self._caixa(tela, r, x, self.dest.get(i))
        if self.fila:
            texto(tela, "frente", 60 + 40, TOPO + 190, "m", CIANO, centro=True)
            texto(tela, "fim", 60 + (len(self.fila) - 1) * 90 + 40, TOPO + 285, "m", CIANO, centro=True)

    def _d_lru(self, tela):
        texto(tela, "MAIS RECENTE", 80, TOPO + 110, "m", VERDE)
        texto(tela, "MENOS RECENTE", 80 + 4 * 150 - 20, TOPO + 110, "m", VERMELHO)
        for i, x in enumerate(self.lru):
            r = pygame.Rect(80 + i * 150, TOPO + 150, 130, 60)
            self._caixa(tela, r, x, self.dest.get(i))
        texto(tela, f"capacidade {CAP_LRU}: ao estourar, despeja o da direita", LARGURA // 2, TOPO + 260, "m", CINZA, centro=True)

    def _d_skip(self, tela):
        SPX, x0, base = 66, 110, ALTURA - 110
        nos = self.skip
        colx = lambda i: x0 + (i + 1) * SPX
        def caixa(i, l, rot):
            r = pygame.Rect(colx(i) - 24, base - l * 52 - 18, 48, 34)
            cor = self.dest.get((i, l))
            self._caixa(tela, r, rot, cor)
        for l in range(MAX_NIVEL):
            caixa(-1, l, "")
            cadeia = [-1] + [i for i, (k, nv) in enumerate(nos) if nv > l]
            for a, b in zip(cadeia, cadeia[1:]):
                seta(tela, (colx(a) + 24, base - l * 52 - 1), (colx(b) - 24, base - l * 52 - 1), CINZA, 2, ponta=8)
            for i, (k, nv) in enumerate(nos):
                if nv > l:
                    caixa(i, l, k)
        texto(tela, "início", colx(-1), base + 24, "m", CIANO, centro=True)
        for l in range(MAX_NIVEL):
            texto(tela, f"nível {l}", 10, base - l * 52 - 8, "p", CINZA)

    def _d_bloom(self, tela):
        larg = 28
        x0 = (LARGURA - M_BLOOM * larg) // 2
        texto(tela, f"Vetor de {M_BLOOM} bits, {K_BLOOM} funções de hash", LARGURA // 2, TOPO + 40, "g", CINZA, centro=True)
        for i, b in enumerate(self.bits):
            r = pygame.Rect(x0 + i * larg, TOPO + 120, larg - 3, 44)
            cor = self.dest.get(i) or (AZUL if b else None)
            self._caixa(tela, r, b, cor)
            texto(tela, i, r.centerx, r.bottom + 4, "p", CINZA, centro=True)
        usados = sum(self.bits)
        texto(tela, f"bits em 1: {usados}/{M_BLOOM}   (quanto mais cheio, mais falsos positivos)",
              LARGURA // 2, TOPO + 220, "m", CINZA, centro=True)
        texto(tela, "Adicionados: " + (", ".join(self.elementos) or "(nenhum)"), 20, TOPO + 270, "m", CIANO)
