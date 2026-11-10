"""Algoritmos de strings: busca de padrões (KMP, Rabin-Karp, Boyer-Moore, Z) e compressão (RLE, LZ77)."""
import random

import pygame

from .base import *

MARCA = (30, 120, 60)      # verde escuro: ocorrência já confirmada


def _linha(g, rot, itens, off=0):
    r = {"rot": rot, "itens": list(itens), "off": off, "cores": {}, "fixo": {}}
    g.linhas.append(r)
    return r


def _dados_busca(g):
    alfabeto = random.choice(["AB", "ABC", "ABC"])
    g.texto = "".join(random.choice(alfabeto) for _ in range(34))
    m = random.choice([3, 4, 4, 5])
    ini = random.randrange(len(g.texto) - m)
    g.padrao = g.texto[ini:ini + m]
    g.achados = []
    return g.texto, g.padrao


def _marcar_ocorrencia(g, linha_t, ini, m, achados):
    achados.append(ini)
    for k in range(ini, ini + m):
        linha_t["fixo"][k] = MARCA
    g.achados = list(achados)
    g.info = f"Ocorrências em: {achados}"


# ---------------------------------------------------------------------
#  Busca de padrões
# ---------------------------------------------------------------------

def kmp(g):
    t, p = _dados_busca(g)
    n, m = len(t), len(p)
    lt, lp = _linha(g, "texto", t), _linha(g, "padrão", p)
    ll = _linha(g, "lps", [""] * m)
    lps = [0] * m
    g.info = "1) Tabela lps: tamanho do maior prefixo que também é sufixo."
    yield
    k = 0
    for i in range(1, m):
        while k > 0 and p[i] != p[k]:
            k = lps[k - 1]
        if p[i] == p[k]:
            k += 1
        lps[i] = k
        ll["itens"][i] = str(k)
        ll["itens"][0] = "0"
        ll["cores"] = {i: AMARELO}
        yield
    ll["itens"][0] = "0"
    ll["cores"] = {}
    g.info = "2) Busca: em caso de erro o padrão salta usando lps, sem voltar no texto."
    achados, j = [], 0
    for i in range(n):
        while True:
            lp["off"] = i - j
            lt["cores"] = {i: AMARELO}
            lp["cores"] = {x: VERDE for x in range(j)}
            lp["cores"][j] = AMARELO
            yield
            if t[i] == p[j]:
                lt["cores"][i] = VERDE
                lp["cores"][j] = VERDE
                j += 1
                break
            lt["cores"][i] = VERMELHO
            lp["cores"][j] = VERMELHO
            yield
            if j == 0:
                break
            j = lps[j - 1]
        if j == m:
            _marcar_ocorrencia(g, lt, i - m + 1, m, achados)
            j = lps[j - 1]
            yield
    lt["cores"], lp["cores"] = {}, {}
    g.info = f"Ocorrências em: {achados}" if achados else "Nenhuma ocorrência"


def _h(s, q=97, d=26):
    v = 0
    for ch in s:
        v = (v * d + ord(ch) - 64) % q
    return v


def rabin_karp(g):
    t, p = _dados_busca(g)
    n, m = len(t), len(p)
    q, d = 97, 26
    lt, lp = _linha(g, "texto", t), _linha(g, "padrão", p)
    lh = _linha(g, "hash", [""] * n)
    hp, h = _h(p), _h(t[:m])
    alto = pow(d, m - 1, q)
    g.info = f"hash do padrão = {hp} (mod {q}). Hash da janela é atualizado em O(1) ao deslizar."
    achados = []
    yield
    for s in range(n - m + 1):
        lh["itens"][s] = str(h)
        lp["off"] = s
        lt["cores"] = {k: AZUL for k in range(s, s + m)}
        yield
        if h == hp:
            ok = True
            for k in range(m):
                lt["cores"][s + k] = AMARELO
                lp["cores"] = {k: AMARELO}
                yield
                if t[s + k] != p[k]:
                    ok = False
                    lt["cores"][s + k] = VERMELHO
                    lp["cores"] = {k: VERMELHO}
                    g.info = f"hash igual em {s}, mas é COLISÃO (falso positivo)"
                    yield
                    break
            lp["cores"] = {}
            if ok:
                _marcar_ocorrencia(g, lt, s, m, achados)
                yield
        if s < n - m:
            h = ((h - (ord(t[s]) - 64) * alto) * d + ord(t[s + m]) - 64) % q
    lt["cores"] = {}
    g.info = f"Ocorrências em: {achados}" if achados else "Nenhuma ocorrência"


def boyer_moore(g):
    t, p = _dados_busca(g)
    n, m = len(t), len(p)
    lt, lp = _linha(g, "texto", t), _linha(g, "padrão", p)
    ruim = {ch: i for i, ch in enumerate(p)}
    g.info = "Compara da DIREITA para a esquerda; no erro, alinha o caractere do texto com sua última ocorrência no padrão."
    achados, s = [], 0
    yield
    while s <= n - m:
        j = m - 1
        lp["off"] = s
        lt["cores"], lp["cores"] = {}, {}
        while j >= 0:
            lt["cores"][s + j] = AMARELO
            lp["cores"][j] = AMARELO
            yield
            if p[j] != t[s + j]:
                lt["cores"][s + j] = VERMELHO
                lp["cores"][j] = VERMELHO
                yield
                break
            lt["cores"][s + j] = VERDE
            lp["cores"][j] = VERDE
            j -= 1
        if j < 0:
            _marcar_ocorrencia(g, lt, s, m, achados)
            yield
            s += m - ruim.get(t[s + m], -1) if s + m < n else 1
        else:
            s += max(1, j - ruim.get(t[s + j], -1))
    lt["cores"], lp["cores"] = {}, {}
    g.info = f"Ocorrências em: {achados}" if achados else "Nenhuma ocorrência"


def z_algoritmo(g):
    t, p = _dados_busca(g)
    m = len(p)
    s = p + "$" + t
    n = len(s)
    ls = _linha(g, "P$T", s)
    lz = _linha(g, "Z", [""] * n)
    Z = [0] * n
    l = r = 0
    achados = []
    g.info = "Z[i] = comprimento do maior prefixo de P$T que começa em i. Z[i] = |P| indica ocorrência."
    yield
    for i in range(1, n):
        if i < r:
            Z[i] = min(r - i, Z[i - l])
        while i + Z[i] < n and s[Z[i]] == s[i + Z[i]]:
            Z[i] += 1
            ls["cores"] = {k: AMARELO for k in range(Z[i])}
            ls["cores"].update({i + k: AZUL for k in range(Z[i])})
            lz["itens"][i] = str(Z[i])
            yield
        if i + Z[i] > r:
            l, r = i, i + Z[i]
        lz["itens"][i] = str(Z[i])
        if Z[i] == m:
            achados.append(i - m - 1)
            for k in range(i, i + m):
                ls["fixo"][k] = MARCA
            g.achados = list(achados)
            g.info = f"Ocorrências em: {achados}"
        ls["cores"] = {i: AMARELO}
        yield
    ls["cores"] = {}
    g.achados = achados
    g.info = f"Ocorrências em: {achados}" if achados else "Nenhuma ocorrência"


# ---------------------------------------------------------------------
#  Compressão
# ---------------------------------------------------------------------

def rle(g):
    partes = []
    while sum(len(x) for x in partes) < 30:
        partes.append(random.choice("ABCD") * random.randint(1, 6))
    s = "".join(partes)
    g.texto = s
    n = len(s)
    le = _linha(g, "entrada", s)
    ls = _linha(g, "RLE", [""] * n)
    g.info = "Run-Length Encoding: cada sequência de letras iguais vira (quantidade)(letra)"
    yield
    saida, i = "", 0
    while i < n:
        j = i
        while j < n and s[j] == s[i]:
            j += 1
        le["cores"] = {k: AMARELO for k in range(i, j)}
        yield
        token = f"{j - i}{s[i]}"
        ls["itens"][i] = token
        for k in range(i, j):
            le["fixo"][k] = cor_hsv((len(saida) * 0.13) % 1, 0.45, 0.8)
        saida += token
        g.info = f"Saída parcial: {saida}"
        yield
        i = j
    le["cores"] = {}
    g.codificado = saida
    g.info = f"'{saida}': {len(saida)} caracteres no lugar de {n} ({len(saida) / n:.0%} do tamanho original)"


def lz77(g):
    chunk = "".join(random.choice("ABC") for _ in range(random.choice([3, 4])))
    s = ""
    while len(s) < 30:
        s += random.choice([chunk, chunk, random.choice("ABC")])
    s = s[:30]
    g.texto = s
    n, W, L = len(s), 12, 6
    lt = _linha(g, "texto", s)
    g.tokens = []
    g.info = "Cada token = (distância para trás, comprimento, próximo caractere). Janela = azul."
    yield
    i = 0
    while i < n:
        ini = max(0, i - W)
        melhor_l, melhor_o = 0, 0
        for j in range(ini, i):
            lt["cores"] = {k: AZUL for k in range(ini, i)}
            lt["cores"].update({k: AMARELO for k in range(i, min(i + L, n))})
            lt["cores"][j] = VERMELHO
            l = 0
            while l < L and i + l < n - 1 and s[j + l] == s[i + l]:
                l += 1
            if l > melhor_l:
                melhor_l, melhor_o = l, i - j
            g.rodape = [f"Procurando a maior repetição: candidato a {i - j} posições atrás casa {l} caracteres"]
            yield
        prox = s[i + melhor_l]
        g.tokens.append((melhor_o, melhor_l, prox))
        for k in range(i, i + melhor_l + 1):
            lt["fixo"][k] = MARCA if k < i + melhor_l else cor_hsv(0.1, 0.6, 0.85)
        g.rodape = ["Tokens: " + " ".join(f"({o},{l},{c})" for o, l, c in g.tokens[-9:])]
        yield
        i += melhor_l + 1
    lt["cores"] = {}
    g.rodape = ["Tokens: " + " ".join(f"({o},{l},{c})" for o, l, c in g.tokens)]
    g.info = f"{len(g.tokens)} tokens para {n} caracteres"


def lz77_decodificar(tokens):
    out = []
    for off, l, c in tokens:
        for _ in range(l):
            out.append(out[-off])
        out.append(c)
    return "".join(out)


def rle_decodificar(s):
    import re
    return "".join(ch * int(n) for n, ch in re.findall(r"(\d+)([A-Z])", s))


class Strings(Cena):
    titulo = "Strings"
    vel_inicial = 4
    ajuda = ("Verde = casou, vermelho = divergiu, amarelo = comparando, verde-escuro = ocorrência confirmada.",
             "TAB: escolher o algoritmo. R: novo texto/padrão.")
    algoritmos = [
        ("KMP (Knuth-Morris-Pratt)", kmp, "O(n + m)"),
        ("Rabin-Karp (hash rolante)", rabin_karp, "O(n + m) médio"),
        ("Boyer-Moore (mau caractere)", boyer_moore, "O(n/m) melhor caso"),
        ("Algoritmo Z", z_algoritmo, "O(n + m)"),
        ("RLE (compressão por repetição)", rle, "O(n)"),
        ("LZ77 (janela deslizante)", lz77, "O(n · janela)"),
    ]
    CEL, X0 = 21, 96

    def reiniciar(self):
        self.linhas, self.rodape = [], []
        self.texto = self.padrao = ""
        self.gerador = None

    def iniciar(self, funcao):
        self.reiniciar()
        self.comecar(funcao(self))

    def evento_cena(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r and self.alg_idx >= 0:
            self.selecionar(self.alg_idx)

    def desenhar_cena(self, tela):
        if not self.linhas:
            texto(tela, "Aperte TAB (ou 1 a 6) para escolher o algoritmo", LARGURA // 2, ALTURA // 2, "g", CINZA,
                  centro=True)
            return
        cw = self.CEL
        for k, lin in enumerate(self.linhas):
            y = TOPO + 40 + k * 56
            texto(tela, lin["rot"], 10, y + 5, "m", CINZA)
            for i, ch in enumerate(lin["itens"]):
                r = pygame.Rect(self.X0 + (i + lin["off"]) * cw, y, cw - 2, 26)
                cor = lin["cores"].get(i, lin["fixo"].get(i))
                pygame.draw.rect(tela, cor or (35, 35, 50), r, border_radius=3)
                texto(tela, ch, r.centerx, r.y + 5, "p", PRETO if cor in (AMARELO, VERDE, VERMELHO, AZUL) else BRANCO,
                      centro=True)
        for k, linha in enumerate(self.rodape):
            texto(tela, linha, 10, ALTURA - 40 + k * 18, "m", CIANO)
