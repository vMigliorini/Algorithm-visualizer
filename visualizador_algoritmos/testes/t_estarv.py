from tu import *
import heapq
from collections import Counter
from visualizador import estruturas_arvore as E
random.seed(4)

# ---- Heap
for i, tipo in enumerate(("min", "max")):
    c = E.Heap(app); c.selecionar(i)
    ok = True
    for v in [random.randint(1, 99) for _ in range(25)]:
        digitar(c, str(v)); tecla(c, pygame.K_RETURN, "\r"); rodar(c)
        for k in range(1, len(c.a)):
            ok = ok and not c.melhor(c.a[k], c.a[(k - 1) // 2])
    checar(f"Heap {tipo}: propriedade após 25 inserções", ok)
    while c.a:
        tecla(c, pygame.K_e); rodar(c)
    esperado = sorted(c.extraidos, reverse=(tipo == "max"))
    checar(f"Heap {tipo}: extrações saem ordenadas", c.extraidos == esperado and len(c.extraidos) == 25)
    tecla(c, pygame.K_b); rodar(c)
    ok = all(not c.melhor(c.a[k], c.a[(k - 1) // 2]) for k in range(1, len(c.a)))
    checar(f"Heap {tipo}: heapify (15 valores)", ok and len(c.a) == 15)
    foto(f"s_heap_{tipo}")

# ---- Trie
c = E.Trie(app); c.selecionar(3); tecla(c, pygame.K_RETURN, "\r"); rodar(c)
def palavras(no, p=""):
    r = [p] if no.fim else []
    for ch in sorted(no.filhos): r += palavras(no.filhos[ch], p + ch)
    return r
checar("Trie: exemplo carregado", palavras(c.raiz) == sorted(E.PALAVRAS_EXEMPLO), palavras(c.raiz))
c.selecionar(1); digitar(c, "carro"); tecla(c, pygame.K_RETURN, "\r"); rodar(c); checar("Trie buscar carro: " + c.msg, "encontrada" in c.msg)
c.selecionar(1); digitar(c, "car"); tecla(c, pygame.K_RETURN, "\r"); rodar(c); checar("Trie buscar car: " + c.msg, "prefixo" in c.msg)
c.selecionar(1); digitar(c, "zebra"); tecla(c, pygame.K_RETURN, "\r"); rodar(c); checar("Trie buscar zebra: " + c.msg, "não existe" in c.msg)
c.selecionar(2); digitar(c, "ca"); tecla(c, pygame.K_RETURN, "\r"); rodar(c)
checar("Trie autocompletar 'ca': " + c.msg, set(c.msg.split("-> ")[1].split(", ")) == {"casa", "caso", "carro", "cara"})
c.selecionar(0); digitar(c, "carta"); tecla(c, pygame.K_RETURN, "\r"); rodar(c); checar("Trie inserir carta", "carta" in palavras(c.raiz))
foto("s_trie")

# ---- Huffman
def ref_bits(s):
    h = [f for f in Counter(s).values()]; heapq.heapify(h); tot = 0
    if len(h) == 1: return len(s)
    while len(h) > 1:
        a, b = heapq.heappop(h), heapq.heappop(h); tot += a + b; heapq.heappush(h, a + b)
    return tot
for s in ["abracadabra alakazam", "aaaa", "mississippi river", "the quick brown fox"]:
    c = E.Huffman(app); digitar(c, s.replace(" ", " ")); tecla(c, pygame.K_RETURN, "\r"); rodar(c)
    cod = c.codigos; texto_ = c.texto_atual
    bits = sum(len(cod[ch]) for ch in texto_)
    prefix_free = all(not b.startswith(a) for a in cod.values() for b in cod.values() if a is not b and a != b)
    # decodifica
    inv = {v: k for k, v in cod.items()}; buf = ""; out = ""
    for bit in "".join(cod[ch] for ch in texto_):
        buf += bit
        if buf in inv: out += inv[buf]; buf = ""
    checar(f"Huffman '{s}': decodifica, prefixo-livre, ótimo ({bits} bits)", out == texto_ and prefix_free and bits == ref_bits(texto_))
foto("s_huffman")

# ---- B-Tree
def bchecar(c):
    t = c.t; folhas = set()
    def rec(n, d, raiz):
        assert n.chaves == sorted(n.chaves)
        assert len(n.chaves) <= 2 * t - 1
        if not raiz: assert len(n.chaves) >= t - 1
        if n.folha: folhas.add(d); return list(n.chaves)
        assert len(n.filhos) == len(n.chaves) + 1
        r = []
        for i, f in enumerate(n.filhos):
            r += rec(f, d + 1, False)
            if i < len(n.chaves): r.append(n.chaves[i])
        return r
    r = rec(c.raiz, 0, True)
    assert len(folhas) == 1, "folhas em níveis diferentes"
    return r
for i in range(2):
    c = E.BTree(app); c.selecionar(i); vals = random.sample(range(1, 100), c.LIMITES[c.t])
    for v in vals:
        digitar(c, str(v)); tecla(c, pygame.K_RETURN, "\r"); rodar(c)
    try: r = bchecar(c); ok = r == sorted(vals)
    except AssertionError as e: ok = False; print(e)
    checar(f"B-Tree t={c.t}: invariantes com {len(vals)} chaves", ok)
    tecla(c, pygame.K_RETURN, "\r"); rodar(c)  # acima do limite
    foto(f"s_btree{c.t}")

# ---- Union-Find
for i in range(2):
    c = E.UnionFind(app); c.selecionar(i)
    conj = [{k} for k in range(c.N)]
    for _ in range(9):
        a, b = random.sample(range(c.N), 2)
        digitar(c, f"{a} {b}"); tecla(c, pygame.K_RETURN, "\r"); rodar(c)
        ca = next(s for s in conj if a in s); cb = next(s for s in conj if b in s)
        if ca is not cb: ca |= cb; conj.remove(cb)
    def raiz(x):
        while c.pai[x] != x: x = c.pai[x]
        return x
    grupos = {}
    for k in range(c.N): grupos.setdefault(raiz(k), set()).add(k)
    checar(f"Union-Find '{c.nome}': componentes corretos", sorted(map(sorted, grupos.values())) == sorted(map(sorted, conj)), f"altura máx {c.altura_max()}")
    foto(f"s_uf{i}")
c.selecionar(2); digitar(c, "3"); tecla(c, pygame.K_RETURN, "\r"); rodar(c); checar("Find: " + c.msg, "find(3)" in c.msg)
fim()
