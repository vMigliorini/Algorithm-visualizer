"""Núcleo compartilhado: constantes, helpers de desenho e a classe base `Cena`.

Cada algoritmo é um GERADOR: cada `yield` é um passo da animação. A `Cena` decide
quantos passos executar por segundo, desenha a faixa de texto (HUD) e oferece:
  TAB            lista de algoritmos da cena (setas + ENTER, ou clique)
  1-9, 0         escolhe direto os 10 primeiros algoritmos (quando a cena permite)
  CIMA / BAIXO   velocidade
  ESPAÇO ou F1   pausa            .  (ponto)  executa 1 passo
  ESC            volta ao menu
"""
import colorsys
import math

import pygame

LARGURA, ALTURA = 1000, 640
TOPO = 96                      # altura da faixa de texto (HUD)
FPS = 60
VELOCIDADES = [1, 2, 5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560]   # passos/segundo

PRETO = (0, 0, 0)
BRANCO = (235, 235, 235)
CINZA = (140, 140, 140)
CINZA_ESC = (60, 60, 70)
VERMELHO = (230, 70, 70)
VERDE = (70, 200, 100)
AZUL = (70, 130, 230)
AMARELO = (240, 200, 60)
LARANJA = (240, 140, 50)
ROXO = (170, 100, 230)
CIANO = (70, 200, 210)
ROSA = (255, 130, 200)
PALETA = [VERMELHO, AZUL, VERDE, AMARELO, ROXO, LARANJA, CIANO, ROSA]

FONTES = {}


def texto(tela, s, x, y, tam="m", cor=BRANCO, centro=False, direita=False):
    surf = FONTES[tam].render(str(s), True, cor)
    r = surf.get_rect()
    if centro:
        r.midtop = (x, y)
    elif direita:
        r.topright = (x, y)
    else:
        r.topleft = (x, y)
    tela.blit(surf, r)
    return r


def chave(u, v):
    """Chave canônica de uma aresta não direcionada."""
    return (u, v) if u < v else (v, u)


def cor_hsv(h, s=0.75, v=0.95):
    """Cor RGB a partir de matiz h em [0, 1)."""
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def seta(tela, a, b, cor=CINZA, larg=2, recuo=0, ponta=10):
    """Desenha uma seta de a até b; `recuo` encurta o final (para não cobrir um nó)."""
    ax, ay = a
    bx, by = b
    d = math.hypot(bx - ax, by - ay) or 1
    ux, uy = (bx - ax) / d, (by - ay) / d
    fim = (bx - ux * recuo, by - uy * recuo)
    pygame.draw.line(tela, cor, a, fim, larg)
    px, py = -uy, ux
    p1 = (fim[0] - ux * ponta + px * ponta * 0.45, fim[1] - uy * ponta + py * ponta * 0.45)
    p2 = (fim[0] - ux * ponta - px * ponta * 0.45, fim[1] - uy * ponta - py * ponta * 0.45)
    pygame.draw.polygon(tela, cor, [fim, p1, p2])


def desenhar_no(tela, centro, rotulo, cor=BRANCO, raio=17, cor_texto=PRETO, tam="p", borda=None):
    pygame.draw.circle(tela, cor, centro, raio)
    if borda:
        pygame.draw.circle(tela, borda, centro, raio, 2)
    texto(tela, rotulo, centro[0], centro[1] - (8 if tam == "m" else 7), tam, cor_texto, centro=True)


def layout_folhas(raiz, filhos, x0, x1, y0, dy, passo_max=90):
    """Layout simples de árvore: folhas igualmente espaçadas, pai centralizado sobre os filhos.
    `filhos(no)` devolve a lista de filhos (ignora None). Retorna {no: (x, y)}."""
    pos = {}
    contador = [0]

    def rec(no, p):
        fs = [f for f in filhos(no) if f is not None]
        if not fs:
            pos[no] = [contador[0], p]
            contador[0] += 1
        else:
            for f in fs:
                rec(f, p + 1)
            pos[no] = [(pos[fs[0]][0] + pos[fs[-1]][0]) / 2, p]

    if raiz is None:
        return {}
    rec(raiz, 0)
    n = max(contador[0], 1)
    passo = min(passo_max, (x1 - x0) / n)
    inicio = (x0 + x1) / 2 - passo * n / 2
    return {no: (int(inicio + (i + 0.5) * passo), int(y0 + p * dy)) for no, (i, p) in pos.items()}


class Cena:
    titulo = ""
    ajuda = ()
    algoritmos = []            # [(nome, funcao[, complexidade]), ...]
    vel_inicial = 3
    digitos_algoritmo = True   # teclas 1-9/0 escolhem algoritmo
    aceita = None              # None | 'num' | 'numesp' | 'letras' | 'alnum' | 'texto'
    max_entrada = 14

    def __init__(self, app):
        self.app = app
        self.vel = self.vel_inicial
        self.pausado = False
        self.gerador = None
        self.nome = "-"
        self.complexidade = ""
        self.alg_idx = -1
        self.info = ""
        self.passos = 0
        self.acum = 0.0
        self.terminou = False
        self.ultimo = None
        self.entrada = ""
        self.overlay = False
        self.sel = 0
        self.reiniciar()

    # ---------- a sobrescrever ----------
    def reiniciar(self):
        pass

    def iniciar(self, funcao):
        pass

    def ao_enter(self):
        pass

    def evento_cena(self, e):
        pass

    def desenhar_cena(self, tela):
        pass

    def ao_terminar(self):
        pass

    # ---------- comum ----------
    def selecionar(self, i):
        item = self.algoritmos[i]
        self.alg_idx = i
        self.nome = item[0]
        self.complexidade = item[2] if len(item) > 2 else ""
        self.iniciar(item[1])

    def comecar(self, gerador):
        self.gerador = gerador
        self.passos = 0
        self.acum = 0.0
        self.terminou = False

    def _aceitar(self, e):
        ch = e.unicode
        if not ch or not ch.isprintable():
            return None
        a = self.aceita
        if a == "num" and ch.isdigit():
            return ch
        if a == "numesp" and (ch.isdigit() or ch == " "):
            return ch
        if a in ("letras", "texto") and ch.isascii() and ch.isalpha():
            return ch.lower()
        if a == "texto" and ch == " ":
            return ch
        if a == "alnum" and ch.isascii() and ch.isalnum():
            return ch.lower()
        return None

    def evento(self, e):
        if self.overlay:
            self._evento_overlay(e)
            return
        if e.type == pygame.KEYDOWN:
            k = e.key
            if k == pygame.K_UP:
                self.vel = min(self.vel + 1, len(VELOCIDADES) - 1)
                return
            if k == pygame.K_DOWN:
                self.vel = max(self.vel - 1, 0)
                return
            if k == pygame.K_F1 or (k == pygame.K_SPACE and self.aceita not in ("texto", "numesp")):
                self.pausado = not self.pausado          # (nas cenas com espaço no texto, use F1)
                return
            if k == pygame.K_PERIOD:
                self.passo_unico()
                return
            if k == pygame.K_TAB and len(self.algoritmos) > 1:
                self.overlay = True
                self.sel = max(self.alg_idx, 0)
                return
            if self.digitos_algoritmo and pygame.K_0 <= k <= pygame.K_9:
                i = 9 if k == pygame.K_0 else k - pygame.K_1
                if 0 <= i < len(self.algoritmos):
                    self.selecionar(i)
                return
            if self.aceita:
                if k == pygame.K_BACKSPACE:
                    self.entrada = self.entrada[:-1]
                    return
                if k in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.ao_enter()
                    return
                ch = self._aceitar(e)
                if ch is not None:
                    if len(self.entrada) < self.max_entrada:
                        self.entrada += ch
                    return
        self.evento_cena(e)

    def passo_unico(self):
        if self.gerador is None:
            return
        try:
            self.ultimo = next(self.gerador)
            self.passos += 1
        except StopIteration:
            self.gerador = None
            self.terminou = True
            self.ao_terminar()

    def atualizar(self):
        if self.gerador is None or self.pausado:
            return
        self.acum += VELOCIDADES[self.vel] / FPS
        n = int(self.acum)
        self.acum -= n
        try:
            for _ in range(n):
                self.ultimo = next(self.gerador)
                self.passos += 1
        except StopIteration:
            self.gerador = None
            self.terminou = True
            self.ao_terminar()

    # ---------- lista de algoritmos (overlay) ----------
    def _geom_overlay(self):
        n = len(self.algoritmos)
        cols = 1 if n <= 12 else (2 if n <= 24 else 3)
        linhas = -(-n // cols)
        larg = min(470, (LARGURA - 40) // cols)
        x0 = (LARGURA - cols * larg) // 2
        return cols, linhas, larg, x0, TOPO + 24

    def _rect_item(self, i):
        _, linhas, larg, x0, y0 = self._geom_overlay()
        c, r = divmod(i, linhas)
        return pygame.Rect(x0 + c * larg, y0 + 36 + r * 30, larg - 8, 28)

    def _evento_overlay(self, e):
        n = len(self.algoritmos)
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_TAB):
                self.overlay = False
            elif e.key == pygame.K_UP:
                self.sel = (self.sel - 1) % n
            elif e.key == pygame.K_DOWN:
                self.sel = (self.sel + 1) % n
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.overlay = False
                self.selecionar(self.sel)
        elif e.type == pygame.MOUSEMOTION:
            for i in range(n):
                if self._rect_item(i).collidepoint(e.pos):
                    self.sel = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i in range(n):
                if self._rect_item(i).collidepoint(e.pos):
                    self.overlay = False
                    self.selecionar(i)
                    return
            self.overlay = False

    def _desenhar_overlay(self, tela):
        cols, linhas, larg, x0, y0 = self._geom_overlay()
        painel = pygame.Rect(x0 - 12, y0 - 8, cols * larg + 16, 36 + linhas * 30 + 20)
        fundo = pygame.Surface(painel.size)
        fundo.set_alpha(240)
        fundo.fill((14, 14, 26))
        tela.blit(fundo, painel)
        pygame.draw.rect(tela, AZUL, painel, 2, border_radius=8)
        texto(tela, "Escolha o algoritmo: CIMA/BAIXO + ENTER, clique do mouse, TAB/ESC fecha",
              x0, y0 + 4, "p", CINZA)
        for i, item in enumerate(self.algoritmos):
            r = self._rect_item(i)
            if i == self.sel:
                pygame.draw.rect(tela, (40, 50, 90), r, border_radius=5)
            texto(tela, f"{i + 1}. {item[0]}", r.x + 6, r.y + 4, "m", VERDE if i == self.alg_idx else BRANCO)
            if len(item) > 2:
                texto(tela, item[2], r.right - 6, r.y + 7, "p", CINZA, direita=True)

    # ---------- desenho ----------
    def desenhar(self, tela):
        tela.fill(PRETO)
        self.desenhar_cena(tela)
        pygame.draw.rect(tela, (12, 12, 20), (0, 0, LARGURA, TOPO))
        pygame.draw.line(tela, CINZA_ESC, (0, TOPO), (LARGURA, TOPO))
        texto(tela, f"{self.titulo}  >  {self.nome}", 10, 4, "g")
        extra = "  [PAUSADO]" if self.pausado else ""
        texto(tela, f"{VELOCIDADES[self.vel]} passos/s | passos: {self.passos}{extra}",
              LARGURA - 10, 10, "p", BRANCO, direita=True)
        for i, linha in enumerate(self.ajuda):
            texto(tela, linha, 10, 29 + i * 16, "p", CINZA)
        fonte_info = "m" if FONTES["m"].size(self.info)[0] < LARGURA - 20 else "p"
        texto(tela, self.info, 10, 62, fonte_info, AMARELO)
        if self.complexidade:
            texto(tela, f"Complexidade: {self.complexidade}", 10, 80, "p", CIANO)
        texto(tela, "TAB lista  ESPAÇO/F1 pausa  . passo  CIMA/BAIXO vel  ESC menu",
              LARGURA - 10, 80, "p", CINZA, direita=True)
        if self.overlay:
            self._desenhar_overlay(tela)
