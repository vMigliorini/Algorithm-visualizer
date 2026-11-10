from tu import *
from visualizador import ordenacao as O
random.seed(1)
c = O.Ordenacao(app)
for i, (nome, f, cx) in enumerate(c.algoritmos):
    c.selecionar(i)
    ok = rodar(c) and c.dados == sorted(c.dados)
    checar(f"Ordenação {nome} (n={len(c.dados)})", ok, c.passos)
# intro sort com fallback forçado para heap sort
for _ in range(20):
    d = random.sample(range(1000), 200); g = O._intro(d, 0, len(d) - 1, 0)
    for _ in g: pass
    assert d == sorted(d)
checar("Intro sort: fallback heap sort (prof=0) ordena", True)
c = O.Busca(app)
for i, (nome, f, cx) in enumerate(c.algoritmos):
    ok = True
    for _ in range(60):
        c.selecionar(i); rodar(c)
        ok = ok and any(v == base.VERDE for v in c.ultimo.values()) and \
             any(c.dados[k] == c.alvo and v == base.VERDE for k, v in c.ultimo.items())
        if not ok: break
    checar(f"Busca {nome} (60 alvos)", ok)
# todos os alvos possíveis (inclusive extremos) nos dois últimos
for i in (3, 4, 5, 6):
    ok = True
    for alvo in c.dados:
        c.alvo = alvo; c.ultimo = {}
        c.comecar(c.algoritmos[i][1](c.dados, alvo)); rodar(c)
        ok = ok and any(c.dados[k] == alvo and v == base.VERDE for k, v in c.ultimo.items())
    checar(f"Busca {c.algoritmos[i][0]} acha TODOS os 60 alvos", ok)
tecla(c, pygame.K_TAB); c.desenhar(tela); foto("s_ov")
fim()
