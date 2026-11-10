from tu import *
from visualizador import strings as S
random.seed(13)
c = S.Strings(app)
def sel(i): c.selecionar(i); return rodar(c)
def ref(t, p): return [i for i in range(len(t) - len(p) + 1) if t[i:i + len(p)] == p]
for i, nome in enumerate(("KMP", "Rabin-Karp", "Boyer-Moore", "Z")):
    ok = True; total = 0
    for _ in range(60):
        sel(i); r = ref(c.texto, c.padrao); total += len(r)
        ok &= (c.achados == r) and len(r) >= 1
    checar(f"{nome}: ocorrências = referência (60 textos, {total} ocorrências)", ok)
    foto(f"s_str_{i}")
# casos extremos
for t, p in [("AAAAAAAA", "AAA"), ("ABABABAB", "ABAB"), ("ABCABC", "CAB"), ("AAAB", "B"), ("ABC", "ABC"), ("ABCD", "XYZ")]:
    for i, f in enumerate((S.kmp, S.rabin_karp, S.boyer_moore, S.z_algoritmo)):
        S._dados_busca_orig = S._dados_busca
        S._dados_busca = lambda g, t=t, p=p: (setattr(g, "texto", t), setattr(g, "padrao", p), setattr(g, "achados", []), (t, p))[-1]
        c.reiniciar(); c.comecar(f(c)); rodar(c)
        S._dados_busca = S._dados_busca_orig
        if c.achados != ref(t, p): checar(f"extremo {f.__name__} {t}/{p}: {c.achados} != {ref(t,p)}", False)
checar("Casos extremos (sobreposição, sem ocorrência, padrão = texto)", True)
ok = True
for _ in range(40):
    sel(4); ok &= S.rle_decodificar(c.codificado) == c.texto
checar("RLE: decodificar(codificar(x)) = x (40)", ok, c.info)
foto("s_rle")
ok = True
for _ in range(40):
    sel(5); ok &= S.lz77_decodificar(c.tokens) == c.texto
checar("LZ77: decodificar(tokens) = texto original (40)", ok, c.info)
foto("s_lz77")
fim()
