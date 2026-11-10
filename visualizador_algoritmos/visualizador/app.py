"""Menu principal e laço da aplicação."""
import pygame

from . import base
from .base import *
from .arvores import Arvores
from .automatos import Automatos
from .backtracking import Backtracking
from .classicos import Classicos
from .dp import ProgDinamica
from .estruturas import Estruturas
from .estruturas_arvore import BTree, Heap, Huffman, Trie, UnionFind
from .geometria import Geometria
from .grade import Grade
from .grafos import Grafos
from .grafos_avancados import GrafosAvancados
from .ia import IA, Caixeiro
from .matematica import Matematica
from .ordenacao import Busca, Ordenacao
from .strings import Strings

# (nome, classe, descrição curta)
MODULOS = [
    ("Ordenação", Ordenacao, "Quick, Merge, Radix, Tim, Heap..."),
    ("Busca", Busca, "Binária, salto, interpolação..."),
    ("Árvores de busca", Arvores, "BST, AVL, Red-Black, Splay..."),
    ("Heap binário", Heap, "Min-heap, max-heap, heapify"),
    ("Trie", Trie, "Inserir, buscar, autocompletar"),
    ("Huffman", Huffman, "Árvore e códigos de compressão"),
    ("B-Tree", BTree, "Divisão de nós, grau mínimo t"),
    ("Union-Find", UnionFind, "Rank e compressão de caminho"),
    ("Grafos", Grafos, "BFS, Dijkstra, A*, MST, cores"),
    ("Grafos avançados", GrafosAvancados, "Fluxo, SCC, topológica, Floyd"),
    ("Caixeiro viajante", Caixeiro, "2-opt, recozimento, genético"),
    ("Pathfinding em grade", Grade, "JPS, labirintos, flood fill..."),
    ("Backtracking", Backtracking, "Rainhas, Sudoku, cavalo, subset"),
    ("Programação dinâmica", ProgDinamica, "LCS, mochila, edição, troco"),
    ("Strings", Strings, "KMP, Rabin-Karp, Z, LZ77, RLE"),
    ("Geometria", Geometria, "Fecho convexo, Bresenham..."),
    ("Estruturas de dados", Estruturas, "Hash, lista, LRU, skip list..."),
    ("Autômatos e simulações", Automatos, "Vida, Langton, Mandelbrot..."),
    ("IA e aprendizado", IA, "k-means, k-NN, perceptron, MCTS"),
    ("Matemática", Matematica, "Euclides, Collatz, Miller-Rabin"),
    ("Clássicos", Classicos, "Hanói e Crivo de Eratóstenes"),
]
LINHAS_MENU = 7


class Menu:
    def __init__(self, app):
        self.app = app
        self.foco = 0

    def rect(self, i):
        c, r = divmod(i, LINHAS_MENU)
        return pygame.Rect(18 + c * 326, 112 + r * 66, 318, 58)

    def evento(self, e):
        n = len(MODULOS)
        if e.type == pygame.KEYDOWN:
            if pygame.K_1 <= e.key <= pygame.K_9 and e.key - pygame.K_1 < n:
                self.app.abrir(MODULOS[e.key - pygame.K_1][1])
            elif e.key == pygame.K_DOWN:
                self.foco = (self.foco + 1) % n
            elif e.key == pygame.K_UP:
                self.foco = (self.foco - 1) % n
            elif e.key == pygame.K_RIGHT:
                self.foco = min(self.foco + LINHAS_MENU, n - 1)
            elif e.key == pygame.K_LEFT:
                self.foco = max(self.foco - LINHAS_MENU, 0)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.app.abrir(MODULOS[self.foco][1])
        elif e.type == pygame.MOUSEMOTION:
            for i in range(n):
                if self.rect(i).collidepoint(e.pos):
                    self.foco = i
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i in range(n):
                if self.rect(i).collidepoint(e.pos):
                    self.app.abrir(MODULOS[i][1])

    def desenhar(self, tela):
        tela.fill(PRETO)
        total = sum(len(c.algoritmos) for _, c, _ in MODULOS)
        texto(tela, "Visualizador de Algoritmos", LARGURA // 2, 18, "t", BRANCO, centro=True)
        texto(tela, f"{len(MODULOS)} módulos  |  {total}+ algoritmos animados  |  clique, setas + ENTER ou teclas 1-9  |  ESC sai",
              LARGURA // 2, 70, "p", CINZA, centro=True)
        for i, (nome, classe, desc) in enumerate(MODULOS):
            r = self.rect(i)
            ativo = i == self.foco
            pygame.draw.rect(tela, (35, 35, 58) if ativo else (20, 20, 32), r, border_radius=10)
            pygame.draw.rect(tela, AZUL if ativo else CINZA_ESC, r, 2, border_radius=10)
            texto(tela, str(i + 1), r.x + 10, r.y + 16, "g", AMARELO)
            texto(tela, nome, r.x + 52, r.y + 6, "m", BRANCO)
            texto(tela, desc, r.x + 52, r.y + 32, "p", CINZA)
            n_alg = len(classe.algoritmos)
            texto(tela, str(n_alg), r.right - 10, r.y + 6, "p", CIANO, direita=True)


class App:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Visualizador de Algoritmos")
        nomes = "consolas,dejavusansmono,couriernew"
        FONTES["p"] = pygame.font.SysFont(nomes, 14)
        FONTES["m"] = pygame.font.SysFont(nomes, 17)
        FONTES["g"] = pygame.font.SysFont(nomes, 22, bold=True)
        FONTES["t"] = pygame.font.SysFont(nomes, 36, bold=True)
        self.relogio = pygame.time.Clock()
        self.menu = Menu(self)
        self.cena = None

    def abrir(self, classe):
        self.cena = classe(self)

    def rodar(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    if self.cena and self.cena.overlay:
                        self.cena.overlay = False
                    elif self.cena:
                        self.cena = None
                    else:
                        return
                    continue
                (self.cena or self.menu).evento(e)
            if self.cena:
                self.cena.atualizar()
                self.cena.desenhar(self.tela)
            else:
                self.menu.desenhar(self.tela)
            pygame.display.flip()
            self.relogio.tick(FPS)


def main():
    App().rodar()
