from tu import *
from collections import OrderedDict
from visualizador import estruturas as E
random.seed(23)
c = E.Estruturas(app)
nomes = [a[0] for a in c.algoritmos]
def op(nome, valor=""):
    c.selecionar([i for i, n in enumerate(nomes) if n == nome][0])
    digitar(c, valor); tecla(c, pygame.K_RETURN, "\r"); return rodar(c)
# --- hash encadeamento
chaves = random.sample(range(1, 200), 20)
for k in chaves: op("Hash encadeamento: inserir", str(k))
ok = all(str(k) in c.baldes[k % 8] for k in chaves) and sum(len(b) for b in c.baldes) == 20
for k in chaves[:5] + [999]:
    op("Hash encadeamento: buscar", str(k)); ok &= ("encontrado" in c.msg and "não" not in c.msg) == (k in chaves)
checar("Hash encadeamento: inserções e buscas corretas (20 chaves)", ok)
foto("s_hash_enc")
for nome, tab in (("Hash sondagem linear", "tab_lin"), ("Hash duplo", "tab_dup")):
    c._zerar("hash_lin"); c._zerar("hash_dup")
    chaves = random.sample(range(1, 200), 9)
    for k in chaves: op(nome + ": inserir", str(k))
    t = getattr(c, tab)
    ok = sorted(x for x in t if x) == sorted(map(str, chaves))
    for k in chaves + [998, 997]:
        op(nome + ": buscar", str(k)); ok &= ("encontrado" in c.msg and "não" not in c.msg) == (k in chaves)
    checar(f"{nome}: 9 inserções, buscas corretas e sem perder chaves", ok)
    foto("s_" + tab)
c._zerar("hash_dup")
for k in range(1, 12): op("Hash duplo: inserir", str(k * 11))   # todas colidem no slot 0 (h1)
checar("Hash duplo: tabela enche por completo (11 chaves colidentes)", all(x is not None for x in c.tab_dup))
op("Hash duplo: inserir", "5"); checar("Hash duplo: tabela cheia detectada", "cheia" in c.msg.lower())
# --- lista ligada
modelo = []
def lista_ok(): return [n.v for n in E.lista_nos(c)] == modelo
for v in (5, 7, 9): op("Lista ligada: inserir no início", str(v)); modelo.insert(0, str(v))
for v in (20, 30): op("Lista ligada: inserir no fim", str(v)); modelo.append(str(v))
ok = lista_ok()
op("Lista ligada: remover valor", "7"); modelo.remove("7"); ok &= lista_ok()
op("Lista ligada: remover valor", "5"); modelo.remove("5"); ok &= lista_ok()
op("Lista ligada: remover valor", "30"); modelo.remove("30"); ok &= lista_ok()
op("Lista ligada: remover valor", "77"); ok &= "não está" in c.msg and lista_ok()
op("Lista ligada: buscar", "20"); ok &= "encontrado" in c.msg and "não" not in c.msg
for v in (1, 2, 3): op("Lista ligada: inserir no fim", str(v)); modelo.append(str(v))
op("Lista ligada: INVERTER (animado)"); modelo.reverse(); ok &= lista_ok()
op("Lista ligada: INVERTER (animado)"); modelo.reverse(); ok &= lista_ok()
foto("s_lista")
checar("Lista ligada: inserir/remover/buscar/inverter = lista Python", ok, modelo)
# --- pilha / fila
m = []
for v in (3, 4, 5): op("Pilha: push", str(v)); m.append(str(v))
op("Pilha: pop"); m.pop(); ok = c.pilha == m
for v in (6, 7): op("Pilha: push", str(v)); m.append(str(v))
ok &= c.pilha == m; foto("s_pilha")
for _ in range(5): op("Pilha: pop")
ok &= c.pilha == [] and "vazia" in c.msg
checar("Pilha LIFO", ok)
m = []
for v in (3, 4, 5): op("Fila: enqueue", str(v)); m.append(str(v))
op("Fila: dequeue"); m.pop(0); ok = c.fila == m
op("Fila: enqueue", "8"); m.append("8"); ok &= c.fila == m; foto("s_fila")
for _ in range(5): op("Fila: dequeue")
ok &= c.fila == [] and "vazia" in c.msg
checar("Fila FIFO", ok)
# --- LRU
mod = OrderedDict(); ok = True
for w in random.choices(E.PALAVRAS[:6], k=40):
    op("Cache LRU (cap. 4): acessar", w)
    if w in mod: mod.move_to_end(w)
    else:
        mod[w] = 1
        if len(mod) > 4: mod.popitem(last=False)
    ok &= c.lru == list(reversed(mod.keys()))
foto("s_lru")
checar("LRU = OrderedDict (40 acessos)", ok)
# --- skip list
chaves = random.sample(range(1, 90), 12)
for k in chaves: op("Skip list: inserir", str(k))
ok = [k for k, _ in c.skip] == sorted(chaves) and all(1 <= nv <= 4 for _, nv in c.skip)
for k in chaves[:6] + [95]:
    op("Skip list: buscar", str(k)); ok &= ("encontrado" in c.msg and "não" not in c.msg) == (k in chaves)
op("Skip list: inserir", "50"); ok &= "limite" in c.msg.lower() or "cheia" in c.msg.lower()
foto("s_skip")
checar("Skip list: ordenada, alturas 1..4, buscas corretas", ok)
# --- bloom
adicionados = ["gato", "cao", "rato", "pato", "lobo"]
for w in adicionados: op("Bloom filter: adicionar", w)
ok = all(c.bits[p] for w in adicionados for p in E.bloom_posicoes(w))
for w in adicionados:
    op("Bloom filter: consultar", w); ok &= "possivelmente presente" in c.msg
fp = 0
for w in ["urso", "foca", "vaca", "peixe", "zebra", "tigre", "coala"]:
    op("Bloom filter: consultar", w)
    ok &= ("ausente" in c.msg) or ("FALSO POSITIVO" in c.msg)
    fp += "FALSO" in c.msg
foto("s_bloom")
checar("Bloom: sem falsos negativos; ausentes ou falso positivo sinalizado", ok, f"{fp} falsos positivos em 7")
# vazio = aleatório; C limpa
c.selecionar(0); tecla(c, pygame.K_RETURN, "\r"); rodar(c); checar("ENTER vazio insere valor aleatório", sum(len(b) for b in c.baldes) >= 1)
c.selecionar(0); tecla(c, pygame.K_c); checar("C limpa a estrutura atual", sum(len(b) for b in c.baldes) == 0)
fim()
