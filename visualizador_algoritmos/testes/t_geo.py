from tu import *
import itertools, math
from visualizador import geometria as G
random.seed(17)
c = G.Geometria(app)
def sel(i): c.selecionar(i); return rodar(c)
def monotone(pts):
    P = sorted(pts)
    def meia(P):
        h = []
        for p in P:
            while len(h) >= 2 and G.cross(h[-2], h[-1], p) <= 0: h.pop()
            h.append(p)
        return h
    m = [(x, -y) for x, y in P]
    inf, sup = meia(m), meia(m[::-1])
    return {(x, -y) for x, y in inf[:-1] + sup[:-1]}
for i, nome in enumerate(("Graham", "Jarvis", "QuickHull")):
    ok = True
    for _ in range(40):
        sel(i); ref = monotone(c.pts)
        ok &= {(x, y) for x, y in c.casco} == ref
    checar(f"{nome}: vértices do casco = monotone chain (40 conjuntos de 30 pontos)", ok, c.info)
    foto(f"s_geo_{i}")
ok = True
for _ in range(30):
    sel(3); brute = min(math.dist(a, b) for a, b in itertools.combinations(c.pts, 2))
    ok &= abs(c.distancia - brute) < 1e-9
checar("Par mais próximo = força bruta (30 conjuntos)", ok, c.info)
foto("s_geo_par")
ok = True; tot = 0
for _ in range(40):
    sel(4)
    ref = {(i, j) for i, j in itertools.combinations(range(len(c.segs)), 2)
           if (lambda s, t: (lambda d: d != 0 and 0 <= ((t[0][0]-s[0][0])*(t[1][1]-t[0][1]) - (t[0][1]-s[0][1])*(t[1][0]-t[0][0]))/d <= 1 and 0 <= ((t[0][0]-s[0][0])*(s[1][1]-s[0][1]) - (t[0][1]-s[0][1])*(s[1][0]-s[0][0]))/d <= 1)((s[1][0]-s[0][0])*(t[1][1]-t[0][1]) - (s[1][1]-s[0][1])*(t[1][0]-t[0][0])))(c.segs[i], c.segs[j])}
    got = {(a, b) for a, b, _ in c.cruzamentos}; tot += len(ref)
    ok &= got == ref
checar("Varredura: cruzamentos = verificação paramétrica por pares (40 instâncias)", ok, f"{tot} cruzamentos")
foto("s_geo_sweep")
ok = True
for _ in range(60):
    sel(5); (x0, y0), (x1, y1) = c.reta; px = c.pixels
    ok &= len(px) == max(abs(x1-x0), abs(y1-y0)) + 1 and px[0] == (x0, y0) and px[-1] == (x1, y1)
    ok &= all(max(abs(a[0]-b[0]), abs(a[1]-b[1])) == 1 for a, b in zip(px, px[1:]))
    # distância dos pixels à reta ideal <= 0.5 + eps na direção maior
    L = math.hypot(x1-x0, y1-y0) or 1
    ok &= all(abs((x1-x0)*(y-y0) - (y1-y0)*(x-x0)) / L <= 0.75 for x, y in px)
checar("Bresenham reta: extremos, vizinhança, contagem e distância à reta ideal (60)", ok)
foto("s_geo_bres")
ok = True
for _ in range(40):
    sel(6); (cx, cy), r = c.centro_circ, c.raio; P = set(c.pixels)
    ok &= all(abs(math.hypot(x-cx, y-cy) - r) < 1.0 for x, y in P)
    ok &= all(((2*cx-x), y) in P and (x, (2*cy-y)) in P for x, y in P)
    ok &= len(P) >= 4 * r
checar("Círculo ponto médio: distância ~ r e simetria (40)", ok, c.info)
foto("s_geo_circ")
fim()
