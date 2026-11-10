from tu import *
from visualizador import arvores as A
random.seed(2)
def inord(n): return [] if n is None else inord(n.esq) + [n.valor] + inord(n.dir)
def alt(n): return 0 if n is None else 1 + max(alt(n.esq), alt(n.dir))
valores = [50, 30, 70, 20, 40, 60, 80, 10, 5, 1, 99, 98, 97, 3, 2, 45, 44, 43, 42, 41]
for i, (nome, f, _) in enumerate(A.Arvores.algoritmos):
    c = A.Arvores(app); c.selecionar(i)
    for v in valores:
        digitar(c, str(v)); tecla(c, pygame.K_RETURN, "\r"); rodar(c)
    ok = inord(c.raiz) == sorted(set(valores))
    extra = ""
    if c.tipo == "avl":
        bal = lambda n: True if n is None else abs(A.altura(n.esq) - A.altura(n.dir)) <= 1 and bal(n.esq) and bal(n.dir)
        hok = lambda n: True if n is None else n.h == alt(n) and hok(n.esq) and hok(n.dir)
        ok = ok and bal(c.raiz) and hok(c.raiz); extra = f"altura {alt(c.raiz)}"
    if c.tipo == "rb":
        def rb(n):
            if n is None: return 1
            assert not (n.vermelho and ((n.esq and n.esq.vermelho) or (n.dir and n.dir.vermelho))), "vermelho-vermelho"
            assert not (n.dir and n.dir.vermelho), "filho direito vermelho (LLRB)"
            a, b = rb(n.esq), rb(n.dir); assert a == b, "altura negra"
            return a + (0 if n.vermelho else 1)
        ok = ok and (not c.raiz.vermelho); rb(c.raiz); extra = f"altura {alt(c.raiz)}"
    if c.tipo == "treap":
        def hp(n): return True if n is None else all(f is None or f.prio <= n.prio for f in (n.esq, n.dir)) and hp(n.esq) and hp(n.dir)
        ok = ok and hp(c.raiz)
    if c.tipo == "splay":
        ok = ok and c.raiz.valor == valores[-1]; extra = f"raiz={c.raiz.valor}"
    checar(f"Árvore {nome}", ok, extra)
    # percursos
    c.ultimo = {}
    for k in (pygame.K_e, pygame.K_p, pygame.K_o, pygame.K_l):
        tecla(c, k); rodar(c)
        if k == pygame.K_e: ok2 = c.saida == sorted(set(valores))
        else: ok2 = sorted(c.saida) == sorted(set(valores)) and len(c.saida) == len(set(valores))
        checar(f"   percurso {pygame.key.name(k)}", ok2)
    digitar(c, "98"); tecla(c, pygame.K_s); rodar(c); checar("   buscar 98: " + c.msg, "não" not in c.msg)
    digitar(c, "55"); tecla(c, pygame.K_s); rodar(c); checar("   buscar 55: " + c.msg, "não encontrado" in c.msg)
    tecla(c, pygame.K_c)
    for v in range(1, 40):
        digitar(c, str(v)); tecla(c, pygame.K_RETURN, "\r"); rodar(c)
    checar("   limite 31 nós", A.contar(c.raiz) == 31, f"altura {alt(c.raiz)}")
    foto(f"s_arv_{c.tipo}")
    # sequência crescente: AVL/RB/Treap mantêm altura baixa
    if c.tipo in ("avl", "rb"): checar("   altura logarítmica após 31 inserções crescentes", alt(c.raiz) <= 10, alt(c.raiz))
# gerar aleatória em cada tipo
for i in range(5):
    c = A.Arvores(app); c.selecionar(i); tecla(c, pygame.K_g); c.desenhar(tela)
    checar(f"G gera 12 nós ({c.nome})", A.contar(c.raiz) == 12)
fim()
