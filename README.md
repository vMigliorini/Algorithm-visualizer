# Visualizador de Algoritmos (pygame)

21 módulos e 158 algoritmos/variações animados passo a passo, em Python + pygame.

## Como rodar

```
pip install pygame
python executar.py            # ou: python -m visualizador
```

Requer Python 3.8+ e pygame 2.x.

## Controles

| Tecla | Ação |
|---|---|
| **TAB** | abre a lista de algoritmos da tela (CIMA/BAIXO + ENTER, ou clique) |
| **1-9, 0** | escolhe direto os 10 primeiros algoritmos (quando a tela não usa números como entrada) |
| **CIMA / BAIXO** | muda a velocidade (1 a 2560 passos por segundo) |
| **ESPAÇO** ou **F1** | pausa (nas telas com espaço no texto, use F1) |
| **.** (ponto) | executa UM passo (útil com a animação pausada) |
| **R** | novo exemplo aleatório do mesmo algoritmo (na maioria das telas) |
| **ESC** | fecha a lista / volta ao menu / sai |

No menu: clique, setas + ENTER ou teclas 1-9. Cada tela mostra, abaixo do título, a
complexidade do algoritmo selecionado e as teclas específicas daquela tela.

## Algoritmos

**1. Ordenação** (18): Bubble Sort; Selection Sort; Insertion Sort; Shell Sort; Merge Sort; Quick Sort; Heap Sort; Counting Sort; Radix Sort (LSD); Comb Sort; Cocktail Shaker Sort; Gnome Sort; Odd-Even Sort; Cycle Sort; Bitonic Sort (64 barras); Tim Sort (simplificado); Intro Sort; Bogo Sort (6 barras)

**2. Busca** (7): Busca Linear; Busca Binária; Busca por Salto (Jump); Busca por Interpolação; Busca Exponencial; Busca Ternária; Busca de Fibonacci

**3. Árvores de busca** (5): BST (árvore binária de busca); AVL (balanceada pela altura); Red-Black (left-leaning); Splay (auto-ajustável); Treap (BST + heap aleatória)

**4. Heap binário** (2): Min-Heap; Max-Heap

**5. Trie** (4): Inserir palavra; Buscar palavra; Autocompletar prefixo; Carregar palavras de exemplo

**6. Huffman** (1): Árvore de Huffman

**7. B-Tree** (2): B-Tree t=2 (2-3-4, até 3 chaves); B-Tree t=3 (até 5 chaves)

**8. Union-Find** (3): União por rank + compressão de caminho; União ingênua (sem otimização); Find com compressão de caminho

**9. Grafos** (10): BFS (largura); DFS (profundidade); Dijkstra; A*; Bellman-Ford; Prim (árvore geradora mínima); Kruskal (árvore geradora mínima); Borůvka (árvore geradora mínima); Coloração gulosa; Coloração ótima por backtracking

**10. Grafos avançados** (10): Floyd-Warshall (todos os pares); Ordenação topológica: Kahn; Ordenação topológica: DFS; Componentes fortemente conexas: Tarjan; Componentes fortemente conexas: Kosaraju; Pontes e pontos de articulação; Ciclo euleriano (Hierholzer); Fluxo máximo: Edmonds-Karp (BFS); Fluxo máximo: Ford-Fulkerson (DFS); Emparelhamento bipartido (Kuhn)

**11. Caixeiro viajante** (5): Vizinho mais próximo (guloso); 2-opt (busca local); Força bruta (8 cidades); Recozimento simulado; Algoritmo genético

**12. Pathfinding em grade** (15): BFS; DFS; Dijkstra (considera lama); A* (Manhattan, considera lama); Busca gulosa (greedy best-first); BFS bidirecional; Jump Point Search (8 direções); Algoritmo de Lee (frente de onda); Flood fill: BFS (balde de tinta); Flood fill: DFS (balde de tinta); Labirinto: DFS backtracker; Labirinto: Prim aleatório; Labirinto: Kruskal aleatório; Labirinto: Wilson (passeio aleatório); Labirinto: divisão recursiva

**13. Backtracking** (7): N-Rainhas (8x8); Sudoku: backtracking simples; Sudoku: heurística MRV; Passeio do cavaleiro 5x5: força bruta; Passeio do cavaleiro 8x8: Warnsdorff; Soma de subconjuntos; Permutações de 4 elementos

**14. Programação dinâmica** (6): LCS (maior subsequência comum); Distância de edição (Levenshtein); Mochila 0/1 (knapsack); Troco com mínimo de moedas; LIS (maior subsequência crescente); Multiplicação de cadeia de matrizes

**15. Strings** (6): KMP (Knuth-Morris-Pratt); Rabin-Karp (hash rolante); Boyer-Moore (mau caractere); Algoritmo Z; RLE (compressão por repetição); LZ77 (janela deslizante)

**16. Geometria** (7): Fecho convexo: Graham Scan; Fecho convexo: Jarvis March; Fecho convexo: QuickHull; Par de pontos mais próximo; Varredura de linha (interseções); Bresenham: reta; Bresenham: círculo (ponto médio)

**17. Estruturas de dados** (20): Hash encadeamento: inserir; Hash encadeamento: buscar; Hash sondagem linear: inserir; Hash sondagem linear: buscar; Hash duplo: inserir; Hash duplo: buscar; Lista ligada: inserir no início; Lista ligada: inserir no fim; Lista ligada: remover valor; Lista ligada: buscar; Lista ligada: INVERTER (animado); Pilha: push; Pilha: pop; Fila: enqueue; Fila: dequeue; Cache LRU (cap. 4): acessar; Skip list: inserir; Skip list: buscar; Bloom filter: adicionar; Bloom filter: consultar

**18. Autômatos e simulações** (10): Jogo da Vida: aleatório; Jogo da Vida: R-pentômino; Jogo da Vida: canhão de Gosper; Jogo da Vida: planadores; Formiga de Langton; Autômato 1D: Regra 30; Autômato 1D: Regra 110; Passeio aleatório 2D; Monte Carlo: estimando π; Conjunto de Mandelbrot

**19. IA e aprendizado** (8): k-means (3 grupos); k-NN (k = 5); Perceptron; Gradiente descendente; Gradiente com momentum; Minimax (jogo da velha); Minimax com poda alfa-beta; MCTS / UCT (jogo da velha)

**20. Matemática** (8): Algoritmo de Euclides (MDC); Exponenciação rápida (modular); Conjectura de Collatz; Fibonacci recursivo (ingênuo); Fibonacci com memoização; Triângulo de Pascal; Pascal mod 2 (Sierpiński); Miller-Rabin (primalidade)

**21. Clássicos** (4): Torre de Hanói (3 discos); Torre de Hanói (5 discos); Torre de Hanói (7 discos); Crivo de Eratóstenes (até 150)

## Como o código é organizado

```
executar.py                 ponto de entrada
visualizador/
  base.py                   constantes, helpers de desenho e a classe base Cena
  app.py                    menu principal e laço da aplicação
  ordenacao.py  arvores.py  estruturas_arvore.py  grafos.py  grafos_avancados.py
  grade.py  backtracking.py  dp.py  strings.py  geometria.py  estruturas.py
  automatos.py  ia.py  matematica.py  classicos.py
testes/                     testes automáticos (rodam sem abrir janela)
```

**Ideia central:** cada algoritmo é um *gerador* Python. Cada `yield` é um passo da animação; a
`Cena` decide quantos passos executar por segundo e desenha o estado. A lógica do algoritmo
não conhece o pygame.

### Adicionando um algoritmo

1. Escreva um gerador que altere o estado e faça `yield` a cada passo interessante.
2. Registre-o na lista `algoritmos` da cena: `("Meu algoritmo", minha_funcao, "O(n log n)")`.

## Testes

```
python testes/rodar_testes.py              # testes por módulo
python testes/rodar_testes.py --completo   # + varredura de todos os algoritmos pelo menu
```

Cada algoritmo é conferido contra uma referência independente: força bruta (mochila, emparelhamento,
coloração, corte mínimo do fluxo), implementações clássicas (`math.gcd`, `pow`, `math.comb`),
algoritmos alternativos (Floyd-Warshall x Dijkstra, Held-Karp x força bruta no caixeiro viajante,
monotone chain x os 3 fechos convexos) e propriedades conhecidas (rodovia da formiga de Langton,
canhão de Gosper, números de Carmichael no Miller-Rabin).

## Simplificações (por clareza didática)

- **Tim Sort**: versão simplificada (insertion sort em *runs* de 16 + merges), sem *galloping*.
- **Red-Black**: variante *left-leaning* (Sedgewick). Árvores de busca só têm inserção/busca/percursos.
- **Varredura de linha**: verifica pares de segmentos ativos (não mantém a ordem vertical de Bentley-Ottmann).
- **Jump Point Search**: grade com 8 direções; diagonais permitidas quando a célula destino está livre.
- **Passeio do cavaleiro por força bruta** usa tabuleiro 5x5 (8x8 só com a heurística de Warnsdorff).
