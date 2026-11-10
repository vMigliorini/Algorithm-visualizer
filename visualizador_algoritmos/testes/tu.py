"""Utilitários compartilhados pelos testes (roda o pygame sem janela)."""
import os, sys, random
os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pygame
from visualizador import base
pygame.init()
tela = pygame.display.set_mode((base.LARGURA, base.ALTURA))
for k, s in (("p", 14), ("m", 17), ("g", 22), ("t", 36)):
    base.FONTES[k] = pygame.font.SysFont("consolas,dejavusansmono", s)
class AppFalso:
    tela = tela
app = AppFalso()
falhas = []
def checar(nome, ok, extra=""):
    print(("OK    " if ok else "FALHA ") + nome + (" | " + str(extra) if extra else ""))
    if not ok: falhas.append(nome)
def tecla(c, k, uni=""):
    c.evento(pygame.event.Event(pygame.KEYDOWN, key=k, unicode=uni))
def digitar(c, s):
    for ch in s: tecla(c, ord(ch), ch)
def rodar(c, limite=400000):
    n = 0
    while c.gerador is not None and n < limite:
        c.acum = 5000; c.atualizar(); n += 1
    c.desenhar(tela)
    return c.gerador is None
def foto(nome):
    """Salva uma captura em FOTOS=<pasta> (variável de ambiente); sem ela, não faz nada."""
    pasta = os.environ.get("FOTOS")
    if pasta:
        os.makedirs(pasta, exist_ok=True)
        pygame.image.save(tela, os.path.join(pasta, nome + ".png"))
def fim():
    print("\nFALHAS:", len(falhas), falhas if falhas else "")
