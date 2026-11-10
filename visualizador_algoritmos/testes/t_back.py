from tu import *
from visualizador import backtracking as B
random.seed(5)
c = B.Backtracking(app)
def sel(i): c.selecionar(i); return rodar(c, 3000000)
sel(0); r = c.rainhas
checar("N-Rainhas válida", all(r[i] is not None for i in range(8)) and all(r[i] != r[j] and abs(r[i]-r[j]) != j-i for i in range(8) for j in range(i+1,8)), c.passos)
def solido(g): 
    return all(sorted(l)==list(range(1,10)) for l in g) and all(sorted(g[r][k] for r in range(9))==list(range(1,10)) for k in range(9)) and all(sorted(g[3*a+i][3*b+j] for i in range(3) for j in range(3))==list(range(1,10)) for a in range(3) for b in range(3))
sel(1); p1 = c.passos; checar("Sudoku simples resolvido", solido(c.sud), p1)
sel(2); p2 = c.passos; checar("Sudoku MRV resolvido e com menos passos", solido(c.sud) and p2 < p1, f"{p2} vs {p1}")
foto("s_sudoku")
def valido_cavalo(c):
    N = c.KN; t = c.trilha
    return len(t) == N*N and len(set(t)) == N*N and all((abs(a[0]-b[0]), abs(a[1]-b[1])) in ((1,2),(2,1)) for a, b in zip(t, t[1:]))
sel(3); checar(f"Cavalo 5x5 força bruta: passeio válido", valido_cavalo(c), f"{c.passos} passos")
sel(4); checar(f"Cavalo 8x8 Warnsdorff: passeio válido", valido_cavalo(c), f"{c.passos} passos")
foto("s_cavalo")
ok = True
for _ in range(30):
    sel(5); inc = [c.nums[i] for i in range(9) if c.sel[i]]
    ok = ok and sum(inc) == c.alvo_soma
checar("Soma de subconjuntos: subconjunto soma o alvo (30 instâncias)", ok, c.info)
foto("s_subset")
sel(6); checar("Permutações: 24 distintas", len(set(c.perms)) == 24 and len(c.perms) == 24)
foto("s_perm")
fim()
