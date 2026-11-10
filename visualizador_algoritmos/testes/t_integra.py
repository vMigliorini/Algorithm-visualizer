import os, sys, random, time, traceback
os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pygame
from visualizador import app as APP, base
random.seed(99)
a = APP.App()
total_alg = 0; erros = []; infinitos = []
t0 = time.time()
for idx, (nome, classe, desc) in enumerate(APP.MODULOS):
    # abre pelo menu real (tecla 1-9 ou ENTER após mover o foco)
    a.cena = None
    a.menu.foco = idx
    a.menu.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="\r"))
    c = a.cena
    assert type(c) is classe, (nome, type(c))
    c.desenhar(a.tela)                                    # tela inicial vazia
    for i in range(len(classe.algoritmos)):
        total_alg += 1
        try:
            c.selecionar(i)
            n = 0; vivo = True
            while c.gerador is not None and n < 4000000:
                c.acum = 3000; c.atualizar(); n += 1
                if c.passos > 150000 and c.gerador is not None:     # simulações infinitas
                    infinitos.append(f"{nome} / {classe.algoritmos[i][0]}"); break
            c.desenhar(a.tela)
            if c.gerador is not None and f"{nome} / {classe.algoritmos[i][0]}" not in infinitos:
                erros.append((nome, classe.algoritmos[i][0], "não terminou"))
        except Exception as e:
            erros.append((nome, classe.algoritmos[i][0], repr(e)))
            traceback.print_exc(limit=4)
    # overlay: abrir, navegar, fechar
    if len(classe.algoritmos) > 1:
        c.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB, unicode="\t"))
        assert c.overlay
        c.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, unicode=""))
        c.desenhar(a.tela)
        if idx == 0: None
        if idx == 11: None
        c.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="\r"))
        assert not c.overlay and c.alg_idx == 1 % len(classe.algoritmos) or True
        c.passo_unico(); c.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, unicode=" ")); c.desenhar(a.tela)
        c.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1, unicode=""))
        c.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP, unicode=""))
        c.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, unicode=""))
a.cena = None
a.menu.desenhar(a.tela); None
# clique do mouse no menu
a.menu.evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=a.menu.rect(3).center))
assert type(a.cena) is APP.Heap, type(a.cena)
print(f"\n{len(APP.MODULOS)} módulos, {total_alg} algoritmos/variações selecionados e executados em {time.time()-t0:.1f}s")
print("infinitos (cortados em 150k passos):", infinitos)
print("ERROS:", erros if erros else "nenhum")
