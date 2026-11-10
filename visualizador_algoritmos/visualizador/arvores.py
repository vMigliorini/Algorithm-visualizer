"""Árvores de busca: BST, AVL, Red-Black, Splay e Treap (+ percursos)."""
import random
from collections import deque

import pygame

from .base import *


class No:
    def __init__(self, valor):
        self.valor = valor
        self.esq = None
        self.dir = None
        self.h = 1
        self.vermelho = True      # usado pela Red-Black
        self.prio = 0             # usado pela Treap


def altura(n):
    return n.h if n else 0


def atualizar_h(n):
    n.h = 1 + max(altura(n.esq), altura(n.dir))


def contar(no):
    return 0 if no is None else 1 + contar(no.esq) + contar(no.dir)


def achar(no, v):
    while no is not None and no.valor != v:
        no = no.esq if v < no.valor else no.dir
    return no


def bst_inserir(raiz, v, ctx=None):
    if raiz is None:
        return No(v)
    no = raiz
    while True:
        yield {no: AMARELO}
        if v == no.valor:
            return raiz
        lado = "esq" if v < no.valor else "dir"
        filho = getattr(no, lado)
        if filho is None:
            setattr(no, lado, No(v))
            yield {getattr(no, lado): VERDE}
            return raiz
        no = filho


def bst_buscar(raiz, v):
    no = raiz
    while no is not None:
        yield {no: AMARELO}
        if v == no.valor:
            yield {no: VERDE}
            return True
        no = no.esq if v < no.valor else no.dir
    return False


def rot_dir(y):
    x = y.esq
    yield {y: VERMELHO, x: VERMELHO}
    y.esq = x.dir
    x.dir = y
    atualizar_h(y)
    atualizar_h(x)
    return x


def rot_esq(x):
    y = x.dir
    yield {x: VERMELHO, y: VERMELHO}
    x.dir = y.esq
    y.esq = x
    atualizar_h(x)
    atualizar_h(y)
    return y


def avl_inserir(no, v, ctx=None):
    if no is None:
        return No(v)
    yield {no: AMARELO}
    if v < no.valor:
        no.esq = yield from avl_inserir(no.esq, v)
    elif v > no.valor:
        no.dir = yield from avl_inserir(no.dir, v)
    else:
        return no
    atualizar_h(no)
    bal = altura(no.esq) - altura(no.dir)
    if bal > 1:                                  # esquerda pesada
        if v > no.esq.valor:                     # caso esquerda-direita
            no.esq = yield from rot_esq(no.esq)
        return (yield from rot_dir(no))
    if bal < -1:                                 # direita pesada
        if v < no.dir.valor:                     # caso direita-esquerda
            no.dir = yield from rot_dir(no.dir)
        return (yield from rot_esq(no))
    return no


def visitar(no, saida, vis):
    saida.append(no.valor)
    vis[no] = VERDE


def em_ordem(no, saida, vis):
    if no:
        yield from em_ordem(no.esq, saida, vis)
        visitar(no, saida, vis)
        yield vis
        yield from em_ordem(no.dir, saida, vis)


def pre_ordem(no, saida, vis):
    if no:
        visitar(no, saida, vis)
        yield vis
        yield from pre_ordem(no.esq, saida, vis)
        yield from pre_ordem(no.dir, saida, vis)


def pos_ordem(no, saida, vis):
    if no:
        yield from pos_ordem(no.esq, saida, vis)
        yield from pos_ordem(no.dir, saida, vis)
        visitar(no, saida, vis)
        yield vis


def em_largura(no, saida, vis):
    if no is None:
        return
    fila = deque([no])
    while fila:
        u = fila.popleft()
        visitar(u, saida, vis)
        yield vis
        for f in (u.esq, u.dir):
            if f:
                fila.append(f)


# ---------------------------------------------------------------------
#  Red-Black (variante left-leaning, Sedgewick)
# ---------------------------------------------------------------------

def _vermelho(n):
    return n is not None and n.vermelho


def _rb_rot_esq(h):
    x = h.dir
    h.dir = x.esq
    x.esq = h
    x.vermelho = h.vermelho
    h.vermelho = True
    return x


def _rb_rot_dir(h):
    x = h.esq
    h.esq = x.dir
    x.dir = h
    x.vermelho = h.vermelho
    h.vermelho = True
    return x


def _rb_flip(h):
    h.vermelho = True
    h.esq.vermelho = False
    h.dir.vermelho = False


def rb_inserir(h, v, ctx=None):
    if h is None:
        n = No(v)
        n.vermelho = True
        return n
    yield {h: AMARELO}
    if v < h.valor:
        h.esq = yield from rb_inserir(h.esq, v)
    elif v > h.valor:
        h.dir = yield from rb_inserir(h.dir, v)
    else:
        return h
    precisa = ((_vermelho(h.dir) and not _vermelho(h.esq))
               or (_vermelho(h.esq) and _vermelho(h.esq.esq))
               or (_vermelho(h.esq) and _vermelho(h.dir)))
    if precisa:
        yield {h: VERMELHO}                     # destaca o nó que será consertado
        if _vermelho(h.dir) and not _vermelho(h.esq):
            h = _rb_rot_esq(h)
        if _vermelho(h.esq) and _vermelho(h.esq.esq):
            h = _rb_rot_dir(h)
        if _vermelho(h.esq) and _vermelho(h.dir):
            _rb_flip(h)
    return h


# ---------------------------------------------------------------------
#  Splay (bottom-up): o nó acessado/inserido sobe até a raiz
# ---------------------------------------------------------------------

def _subir(x, p, gp):
    """Rotaciona x sobre seu pai p (gp = pai de p, ou None)."""
    if p.esq is x:
        p.esq = x.dir
        x.dir = p
    else:
        p.dir = x.esq
        x.esq = p
    if gp is not None:
        if gp.esq is p:
            gp.esq = x
        else:
            gp.dir = x


def splay_inserir(raiz, v, ctx):
    if raiz is None:
        return No(v)
    caminho = []
    no = raiz
    while True:
        yield {no: AMARELO}
        caminho.append(no)
        if v == no.valor:
            break
        lado = "esq" if v < no.valor else "dir"
        filho = getattr(no, lado)
        if filho is None:
            novo = No(v)
            setattr(no, lado, novo)
            caminho.append(novo)
            yield {novo: VERDE}
            break
        no = filho
    while len(caminho) > 1:
        x, p = caminho[-1], caminho[-2]
        g = caminho[-3] if len(caminho) > 2 else None
        gg = caminho[-4] if len(caminho) > 3 else None
        if g is None:                                   # zig
            _subir(x, p, None)
            raiz = ctx.raiz = x
            caminho = [x]
        elif (g.esq is p) == (p.esq is x):              # zig-zig
            _subir(p, g, gg)
            _subir(x, p, gg)
            if gg is None:
                raiz = ctx.raiz = x
            caminho = caminho[:-3] + [x]
        else:                                           # zig-zag
            _subir(x, p, g)
            _subir(x, g, gg)
            if gg is None:
                raiz = ctx.raiz = x
            caminho = caminho[:-3] + [x]
        yield {x: VERDE}
    return raiz


# ---------------------------------------------------------------------
#  Treap: BST pelo valor + heap (máximo) por prioridade aleatória
# ---------------------------------------------------------------------

def treap_inserir(no, v, ctx=None):
    if no is None:
        n = No(v)
        n.prio = random.randint(1, 99)
        return n
    yield {no: AMARELO}
    if v < no.valor:
        no.esq = yield from treap_inserir(no.esq, v)
        if no.esq.prio > no.prio:
            no = yield from rot_dir(no)
    elif v > no.valor:
        no.dir = yield from treap_inserir(no.dir, v)
        if no.dir.prio > no.prio:
            no = yield from rot_esq(no)
    return no


# ---------------------------------------------------------------------
#  Cena
# ---------------------------------------------------------------------

class Arvores(Cena):
    titulo = "Árvores de busca"
    digitos_algoritmo = False
    aceita = "num"
    max_entrada = 3
    vel_inicial = 3
    LIMITE = 31
    ajuda = ("Digite um número + ENTER: inserir   S: buscar   G: gerar aleatória   C: limpar   "
             "TAB: escolher o tipo de árvore",
             "Percursos:  E em-ordem   P pré-ordem   O pós-ordem   L em largura")
    algoritmos = [
        ("BST (árvore binária de busca)", bst_inserir, "O(h), pior O(n)"),
        ("AVL (balanceada pela altura)", avl_inserir, "O(log n)"),
        ("Red-Black (left-leaning)", rb_inserir, "O(log n)"),
        ("Splay (auto-ajustável)", splay_inserir, "O(log n) amortizado"),
        ("Treap (BST + heap aleatória)", treap_inserir, "O(log n) esperado"),
    ]
    TIPOS = {bst_inserir: "bst", avl_inserir: "avl", rb_inserir: "rb",
             splay_inserir: "splay", treap_inserir: "treap"}

    def reiniciar(self):
        self.insercao = bst_inserir
        self.tipo = "bst"
        self.raiz = None
        self.saida = []
        self.msg = ""
        self.ultimo = {}
        self.gerador = None
        self.alg_idx = 0
        self.nome, _, self.complexidade = self.algoritmos[0]

    def limpar(self):
        self.raiz = None
        self.saida = []
        self.msg = ""
        self.ultimo = {}
        self.gerador = None

    def iniciar(self, funcao):
        self.insercao = funcao
        self.tipo = self.TIPOS[funcao]
        self.limpar()

    # --- operações (geradores) ---
    def _inserir(self, v):
        self.raiz = yield from self.insercao(self.raiz, v, self)
        if self.tipo == "rb":
            self.raiz.vermelho = False
        no = achar(self.raiz, v)
        self.ultimo = {no: VERDE} if no else {}
        self.msg = f"{v} inserido"

    def _buscar(self, v):
        ok = yield from bst_buscar(self.raiz, v)
        self.msg = f"{v} {'encontrado' if ok else 'não encontrado'}"

    def _percurso(self, f, nome):
        self.saida = []
        self.msg = nome
        yield from f(self.raiz, self.saida, {})

    def ao_enter(self):
        if not self.entrada or self.gerador is not None:
            return
        v = int(self.entrada)
        self.entrada = ""
        if contar(self.raiz) >= self.LIMITE:
            self.msg = f"Limite de {self.LIMITE} nós"
            return
        self.saida = []
        self.comecar(self._inserir(v))

    def evento_cena(self, e):
        if e.type != pygame.KEYDOWN:
            return
        livre = self.gerador is None
        if e.key == pygame.K_s and self.entrada and livre:
            v = int(self.entrada)
            self.entrada = ""
            self.saida = []
            self.comecar(self._buscar(v))
        elif e.key in (pygame.K_e, pygame.K_p, pygame.K_o, pygame.K_l) and livre and self.raiz:
            f, nome = {pygame.K_e: (em_ordem, "Em-ordem (esq, raiz, dir)"),
                       pygame.K_p: (pre_ordem, "Pré-ordem (raiz, esq, dir)"),
                       pygame.K_o: (pos_ordem, "Pós-ordem (esq, dir, raiz)"),
                       pygame.K_l: (em_largura, "Em largura (nível a nível)")}[e.key]
            self.comecar(self._percurso(f, nome))
        elif e.key == pygame.K_g and livre:
            self.limpar()
            for v in random.sample(range(1, 100), 12):
                for _ in self._inserir(v):
                    pass
            self.ultimo = {}
            self.msg = "Árvore aleatória gerada"
        elif e.key == pygame.K_c:
            self.limpar()

    # --- desenho ---
    def posicoes(self):
        pos, cont, prof_max = {}, [0], [0]

        def rec(no, p):
            if no is None:
                return
            rec(no.esq, p + 1)
            pos[no] = (cont[0], p)
            cont[0] += 1
            prof_max[0] = max(prof_max[0], p)
            rec(no.dir, p + 1)

        rec(self.raiz, 0)
        n = max(cont[0], 1)
        passo_x = min(60, (LARGURA - 80) / max(n - 1, 1))
        x0 = (LARGURA - passo_x * (n - 1)) / 2
        passo_y = min(70, (ALTURA - TOPO - 110) / max(prof_max[0], 1))
        return {no: (int(x0 + i * passo_x), int(TOPO + 45 + p * passo_y)) for no, (i, p) in pos.items()}

    def desenhar_cena(self, tela):
        pos = self.posicoes()
        for no, (x, y) in pos.items():
            for f in (no.esq, no.dir):
                if f:
                    pygame.draw.line(tela, CINZA, (x, y), pos[f], 2)
        dest = self.ultimo if isinstance(self.ultimo, dict) else {}
        for no, (x, y) in pos.items():
            if self.tipo == "rb":
                base_cor = (200, 40, 40) if no.vermelho else (25, 25, 25)
                cor = dest.get(no, base_cor)
                pygame.draw.circle(tela, cor, (x, y), 17)
                pygame.draw.circle(tela, BRANCO, (x, y), 17, 2)
                texto(tela, no.valor, x, y - 7, "p", BRANCO if cor == base_cor else PRETO, centro=True)
            else:
                pygame.draw.circle(tela, dest.get(no, BRANCO), (x, y), 17)
                texto(tela, no.valor, x, y - 7, "p", PRETO, centro=True)
            if self.tipo == "avl":
                texto(tela, f"{altura(no.esq) - altura(no.dir):+d}", x, y + 19, "p", CINZA, centro=True)
            elif self.tipo == "treap":
                texto(tela, f"p{no.prio}", x, y + 19, "p", CINZA, centro=True)
        self.info = f"Valor: {self.entrada}_   {self.msg}"
        if self.saida:
            texto(tela, "Visitados: " + " ".join(map(str, self.saida)), 10, ALTURA - 24, "m", CIANO)
