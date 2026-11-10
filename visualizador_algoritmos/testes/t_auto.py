from tu import *
from visualizador import automatos as A
random.seed(29)
c = A.Automatos(app)
nomes = [a[0] for a in c.algoritmos]
def sel(prefixo):
    c.selecionar([i for i, n in enumerate(nomes) if n.startswith(prefixo)][0])
def passos(n):
    for _ in range(n): c.ultimo = next(c.gerador)
# --- Jogo da Vida
gun = A.rle_para_celulas(A.GOSPER_RLE)
checar("RLE do canhão de Gosper tem 36 células", len(gun) == 36, len(gun))
sel("Jogo da Vida: canhão"); passos(1); p0 = len(c.vivas)
passos(30); checar("Canhão de Gosper: 36 células → 41 após 30 gerações (emitiu 1 planador)", p0 == 36 and len(c.vivas) == 41, f"{p0} → {len(c.vivas)}")
passos(30); checar("Canhão: 46 células após 60 gerações (2 planadores)", len(c.vivas) == 46, len(c.vivas))
c.desenhar(tela); foto("s_gun")
blink = {(5, 4), (5, 5), (5, 6)}
checar("Blinker: período 2", A.vida_passo(A.vida_passo(blink, 20, 20), 20, 20) == blink and A.vida_passo(blink, 20, 20) != blink)
gl = {(r + 3, c_ + 3) for r, c_ in A.PLANADOR}
g4 = gl
for _ in range(4): g4 = A.vida_passo(g4, 30, 30)
checar("Planador: após 4 gerações translada (+1,+1)", g4 == {(r + 1, c_ + 1) for r, c_ in gl})
bloco = {(1, 1), (1, 2), (2, 1), (2, 2)}
checar("Bloco é uma vida estável", A.vida_passo(bloco, 10, 10) == bloco)
for nome in ("Jogo da Vida: aleatório", "Jogo da Vida: R-pent", "Jogo da Vida: plan"):
    sel(nome); passos(60); c.desenhar(tela); checar(nome + " roda 60 gerações", c.geracao == 59 or c.geracao == 60, len(c.vivas))
sel("Jogo da Vida: R-pent"); passos(200); foto("s_rpent")
# --- Formiga de Langton (grade grande para observar a rodovia)
sel("Formiga"); c.R = c.C = 400
c.gerador = A.formiga(c); passos(1)
c.R = c.C = 400
pos, pret = [], []
for t in range(13000):
    passos(1)
    if t >= 12000 and (t - 12000) % 104 == 0: pos.append(c.formiga); pret.append(len(c.pretas))
dif = {(abs(b[0] - a[0]), abs(b[1] - a[1])) for a, b in zip(pos, pos[1:])}
dp = {b - a for a, b in zip(pret, pret[1:])}
checar("Langton: 'rodovia' após ~10.000 passos (desloca 2 casas na diagonal a cada 104 passos)", dif == {(2, 2)}, (dif, dp))
c.R, c.C = A.LINS, A.COLS
sel("Formiga"); passos(11000); c.desenhar(tela); foto("s_langton")
# --- Regras 1D
sel("Autômato 1D: Regra 30"); rodar(c)
W = c.largura_ca; m = W // 2
linha = lambda k: {i for i, v in enumerate(c.geracoes[k]) if v}
checar("Regra 30: linhas 1-3 = padrões conhecidos (1, 111, 11001)", linha(0) == {m} and linha(1) == {m-1, m, m+1} and linha(2) == {m-2, m-1, m+2}, sorted(linha(2)))
foto("s_r30")
sel("Autômato 1D: Regra 110"); rodar(c); checar("Regra 110: 1ª linha = {x-1, x}", linha(1) == {m - 1, m}, sorted(linha(1)))
foto("s_r110")
# --- Passeio aleatório
sel("Passeio"); c.n_walkers = 400; c.gerador = A.passeio(c); passos(500)
checar("Passeio aleatório: distância² média ≈ nº de passos (400 caminhantes, 500 passos)", 400 < c.msd < 600, f"{c.msd:.0f}")
c.n_walkers = 12; sel("Passeio"); passos(3000); foto("s_walk")
# --- Monte Carlo
sel("Monte Carlo"); passos(2500)
checar("Monte Carlo: π estimado com 50.000 pontos", abs(c.pi_est - 3.14159) < 0.05, c.info)
passos(2500); foto("s_mc")
# --- Mandelbrot
sel("Conjunto"); rodar(c); fr = c.dentro / (250 * 136)
checar("Mandelbrot: fração de pontos dentro do conjunto plausível", 0.15 < fr < 0.32, f"{fr:.2%}")
foto("s_mandel")
fim()
