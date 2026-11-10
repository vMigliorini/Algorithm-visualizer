from tu import *
import itertools, math
from visualizador import ia as I
random.seed(31)
c = I.IA(app)
nomes = [a[0] for a in c.algoritmos]
def sel(p): c.selecionar([i for i, n in enumerate(nomes) if n.startswith(p)][0]); return rodar(c, 2000000)
# k-means: inércia monótona e convergência
ok = True
for _ in range(25):
    sel("k-means"); h = c.historico
    ok &= all(b <= a + 1e-6 for a, b in zip(h, h[1:])) and "Convergiu" in c.info
checar("k-means: inércia não aumenta e converge (25 execuções)", ok, c.info)
foto("s_kmeans")
# k-NN
ok = True
for _ in range(20):
    sel("k-NN")
    for q, pred, viz in c.consultas:
        ordem = sorted(range(len(c.pts)), key=lambda i: math.dist(q, c.pts[i]))[:5]
        votos = sum(c.rot[i] for i in ordem)
        ok &= set(viz) == set(ordem) and pred == (1 if votos >= 3 else 0)
    ok &= len(c.consultas) == 7
checar("k-NN: vizinhos e voto majoritário = força bruta (20 x 7 consultas)", ok)
foto("s_knn")
# Perceptron
ok = True
for _ in range(30):
    sel("Perceptron"); w = c.w
    ok &= all((1 if w[0] + w[1] * x + w[2] * y > 0 else -1) == cl for x, y, cl in c.dados_p) and "Convergiu" in c.info
checar("Perceptron: 100% de acerto em dados separáveis (30)", ok, c.info)
foto("s_perc")
# Gradiente
for nome in ("Gradiente descendente", "Gradiente com momentum"):
    ok = True; piores = 0
    for _ in range(40):
        sel(nome); f = c.final[2]; piores = max(piores, f)
        ok &= f < 0.05
    checar(f"{nome}: chega a um mínimo (40 inícios aleatórios)", ok, f"pior f = {piores:.4f}")
    foto("s_gd_" + nome.split()[-1])
# Minimax / alfa-beta
def mm(t, vez):
    w = I.vencedor(t)
    if w: return 1 if w == "X" else -1
    l = I.livres_v(t)
    if not l: return 0
    vals = []
    for m in l:
        t[m] = vez; vals.append(mm(t, I.outro(vez))); t[m] = " "
    return max(vals) if vez == "X" else min(vals)
ok = True; menos = 0
for _ in range(25):
    sel("Minimax (jogo"); n1, v1, mov1 = c.nos, c.valor, c.melhor_mov; tab0 = list(c.tab); vez = c.vez
    ref = mm(list(tab0), vez)
    c.tab = list(tab0); c.vez = vez; c.comecar(I.alfa_beta(c)); rodar(c); n2, v2, mov2 = c.nos, c.valor, c.melhor_mov
    t = list(tab0); t[mov2] = vez; val_mov2 = mm(t, I.outro(vez))
    ok &= v1 == v2 == ref and val_mov2 == ref and n2 <= n1; menos += n2 < n1
checar("Minimax = alfa-beta = referência; alfa-beta nunca visita mais nós (25 posições)", ok, f"alfa-beta visitou menos em {menos}/25; último: {n1} vs {n2} nós")
foto("s_ttt")
# MCTS acha vitória imediata e bloqueio
def mcts_em(tab, vez):
    c.reiniciar(); c.tab, c.vez = list(tab), vez; c.modo = "ttt"; c.comecar(I.mcts(c)); rodar(c); return c.melhor_mov
X, O, _ = "X", "O", " "
casos = [([X, X, _, O, O, _, _, _, _], X, 2, "vitória imediata"),
         ([O, O, _, X, _, _, _, _, X], X, 2, "bloquear a ameaça de O"),
         ([X, _, _, _, O, _, _, _, X], O, None, "qualquer jogada de borda (evitar perder)")]
ok = True
for tab, vez, esp, desc in casos[:2]:
    acertos = sum(mcts_em(tab, vez) == esp for _ in range(5)); ok &= acertos == 5
    checar(f"MCTS: {desc} (5/5 execuções)", acertos == 5, acertos)
mcts_em([X, _, _, _, O, _, _, _, X], O); foto("s_mcts")
# TSP
ct = I.Caixeiro(app)
def selt(i): ct.selecionar(i); return rodar(ct, 3000000)
def valido(ct): return sorted(ct.tour) == list(range(len(ct.pts)))
for i, nome in enumerate(("vizinho", "2-opt")):
    selt(i); checar(f"TSP {nome}: rota válida", valido(ct), ct.info)
    foto(f"s_tsp{i}")
# 2-opt: ótimo local
selt(1); n = len(ct.pts); t = ct.tour; ok = True
for i in range(n - 1):
    for j in range(i + 2, n if i > 0 else n - 1):
        a, b, cc, d = ct.pts[t[i]], ct.pts[t[i+1]], ct.pts[t[j]], ct.pts[t[(j+1) % n]]
        ok &= math.dist(a, cc) + math.dist(b, d) >= math.dist(a, b) + math.dist(cc, d) - 1e-6
checar("TSP 2-opt: nenhuma troca 2-opt ainda melhora (ótimo local)", ok)
# força bruta = Held-Karp
selt(2)
pts = ct.pts; n = len(pts)
INF = 1e18; dp = {(1, 0): 0.0}
for mask in range(1, 1 << n):
    if not mask & 1: continue
    for last in range(n):
        if (mask, last) not in dp: continue
        for nx in range(n):
            if mask >> nx & 1: continue
            k = (mask | 1 << nx, nx); v = dp[(mask, last)] + math.dist(pts[last], pts[nx])
            if v < dp.get(k, INF): dp[k] = v
ot = min(dp[((1 << n) - 1, l)] + math.dist(pts[l], pts[0]) for l in range(1, n))
checar("TSP força bruta = Held-Karp (ótimo exato, 8 cidades)", abs(I.comprimento(pts, ct.tour) - ot) < 1e-6 and valido(ct), f"{ot:.1f}")
foto("s_tsp2")
for i, nome in ((3, "recozimento"), (4, "genético")):
    ok = True
    for _ in range(3):
        selt(i); n = len(ct.pts)
        # rota aleatória típica ~ 0.5*n*área média; compara com vizinho mais próximo
        aleat = sum(I.comprimento(ct.pts, random.sample(range(n), n)) for _ in range(50)) / 50
        ok &= valido(ct) and I.comprimento(ct.pts, ct.tour) < 0.55 * aleat
    checar(f"TSP {nome}: rota válida e bem melhor que aleatória", ok, f"{I.comprimento(ct.pts, ct.tour):.0f} vs aleatória {aleat:.0f}")
    foto(f"s_tsp{i}")
fim()
