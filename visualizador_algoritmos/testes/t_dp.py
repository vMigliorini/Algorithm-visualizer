from tu import *
import itertools
from functools import lru_cache
from visualizador import dp as D
random.seed(8)
c = D.ProgDinamica(app)
def sel(i): c.selecionar(i); return rodar(c)
def lcs_ref(a, b):
    @lru_cache(None)
    def f(i, j): return 0 if i == 0 or j == 0 else (f(i-1, j-1) + 1 if a[i-1] == b[j-1] else max(f(i-1, j), f(i, j-1)))
    return f(len(a), len(b))
def sub_seq(s, t):
    it = iter(t); return all(ch in it for ch in s)
def ed_ref(a, b):
    @lru_cache(None)
    def f(i, j):
        if i == 0: return j
        if j == 0: return i
        return min(f(i-1, j) + 1, f(i, j-1) + 1, f(i-1, j-1) + (a[i-1] != b[j-1]))
    return f(len(a), len(b))
ok = True
for _ in range(30):
    sel(0); ok &= (c.tab[-1][-1] == lcs_ref(c.a, c.b) == len(c.resposta)) and sub_seq(c.resposta, c.a) and sub_seq(c.resposta, c.b)
checar("LCS: tamanho = referência e resposta é subsequência de ambas (30)", ok)
foto("s_lcs")
ok = True
for i in range(len(D.PARES_PALAVRAS) * 3):
    sel(1); ok &= c.resposta == ed_ref(c.a, c.b)
checar("Distância de edição = referência (18 pares)", ok, c.info)
ok = True
for _ in range(30):
    sel(2)
    melhor = max(sum(c.itens[i][1] for i in sub) for r in range(7) for sub in itertools.combinations(range(6), r) if sum(c.itens[i][0] for i in sub) <= c.cap)
    pesos = sum(c.itens[i - 1][0] for i in c.escolhidos); vals = sum(c.itens[i - 1][1] for i in c.escolhidos)
    ok &= c.resposta == melhor == vals and pesos <= c.cap
checar("Mochila 0/1: valor ótimo (força bruta) e itens cabem (30)", ok)
foto("s_mochila")
ok = True
for _ in range(25):
    sel(3)
    # referência BFS
    dist = {0: 0}; fila = [0]
    for a in fila:
        for m in c.moedas:
            if a + m <= c.valor and a + m not in dist: dist[a + m] = dist[a] + 1; fila.append(a + m)
    ok &= c.resposta == dist[c.valor] and sum(c.usadas) == c.valor and len(c.usadas) == c.resposta
checar("Troco: mínimo de moedas = BFS e soma bate (25)", ok, c.info)
foto("s_troco")
ok = True
for _ in range(30):
    sel(4); a = c.arr
    ref = max(len(s) for r in range(1, 11) for s in itertools.combinations(a, r) if all(x < y for x, y in zip(s, s[1:])))
    ok &= len(c.resposta) == ref and all(x < y for x, y in zip(c.resposta, c.resposta[1:])) and sub_seq(c.resposta, a)
checar("LIS: tamanho = força bruta e subsequência crescente válida (30)", ok, c.info)
foto("s_lis")
ok = True
for _ in range(20):
    sel(5); d = c.dims; n = len(d) - 1
    @lru_cache(None)
    def f(i, j): return 0 if i == j else min(f(i, k) + f(k+1, j) + d[i]*d[k+1]*d[j+1] for k in range(i, j))
    ok &= c.resposta == f(0, n - 1)
checar("Cadeia de matrizes = referência recursiva (20)", ok, c.info)
foto("s_mcm")
fim()
