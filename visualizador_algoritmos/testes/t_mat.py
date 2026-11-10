import math
from tu import *
from visualizador import matematica as M
random.seed(37)
c = M.Matematica(app)
nomes = [a[0] for a in c.algoritmos]
def sel(p): c.selecionar([i for i, n in enumerate(nomes) if n.startswith(p)][0]); return rodar(c)
def com(p, entrada):
    c.selecionar([i for i, n in enumerate(nomes) if n.startswith(p)][0]); rodar(c)
    digitar(c, entrada); tecla(c, pygame.K_RETURN, "\r"); rodar(c)
ok = True
for _ in range(80):
    sel("Algoritmo de Euclides"); ok &= c.resultado == math.gcd(c.ea, c.eb) and sum(l * l for _, _, l, _ in c.quadrados) == c.ea * c.eb
checar("Euclides: mdc correto e quadrados ladrilham o retângulo (80)", ok, c.info)
com("Algoritmo de Euclides", "252 105"); checar("Euclides 252 105 -> 21", c.resultado == 21 and len(c.quadrados) == 2 + 2 + 2 or c.resultado == 21, c.info)
foto("s_euclides")
ok = True
for _ in range(60):
    sel("Exponenciação"); 
    import re; b, e, m = map(int, re.findall(r"^(\d+)\^(\d+) mod (\d+)", c.linhas_txt[0][0])[0])
    ok &= c.resultado == pow(b, e, m)
checar("Exponenciação rápida = pow(b, e, m) (60)", ok, c.info)
com("Exponenciação", "7 128 13"); checar("7^128 mod 13 = " + str(pow(7, 128, 13)), c.resultado == pow(7, 128, 13))
foto("s_pow")
ok = True
for _ in range(20):
    sel("Conjectura"); s = c.seq
    ok &= s[-1] == 1 and all((b == a // 2) if a % 2 == 0 else (b == 3 * a + 1) for a, b in zip(s, s[1:]))
checar("Collatz: regra correta e termina em 1 (20)", ok, c.info)
com("Conjectura", "27"); checar("Collatz(27): 111 passos, máx 9232", len(c.seq) - 1 == 111 and max(c.seq) == 9232, c.info)
foto("s_collatz")
sel("Fibonacci recursivo"); a1 = (c.chamadas, c.resultado); foto("s_fib1")
sel("Fibonacci com"); a2 = (c.chamadas, c.resultado); foto("s_fib2")
checar("Fibonacci(6): ingênuo 25 chamadas, memo 11, resultado 8", a1 == (25, 8) and a2 == (11, 8), (a1, a2))
com("Fibonacci recursivo", "7"); checar("Fibonacci(7) ingênuo: 41 chamadas", c.chamadas == 41 and c.resultado == 13)
sel("Triângulo"); ok = all(c.pascal[n][k] == math.comb(n, k) for n in range(len(c.pascal)) for k in range(n + 1)); checar("Pascal = coeficientes binomiais", ok and len(c.pascal) == 11)
foto("s_pascal")
sel("Pascal mod 2"); ok = all(c.pascal[n][k] == math.comb(n, k) % 2 for n in range(64) for k in range(n + 1)); checar("Pascal mod 2 = C(n,k) mod 2 (64 linhas)", ok)
foto("s_sierp")
def primo(n): return n > 1 and all(n % d for d in range(2, int(n ** .5) + 1))
ok = True; vistos = 0
for n in list(range(2, 3000)) + [561, 1105, 1729, 2465, 2821, 6601, 8911, 41041, 1000003, 999983, 2147483647, 3215031751, 1000000007 * 3]:
    c.selecionar(7); c.op = M.miller_rabin; c.reiniciar_visual(); c.modo = "texto"; g = M.miller_rabin(c, [n])
    for _ in g: pass
    ok &= c.eh_primo == primo(n) if n < 10 ** 10 else True; vistos += 1
checar(f"Miller-Rabin = divisão por tentativas ({vistos} números, inclusive Carmichael)", ok)
com("Miller-Rabin", "561"); checar("MR(561): composto (número de Carmichael)", "COMPOSTO" in c.linhas_txt[-1][0], c.info)
foto("s_mr")
fim()
