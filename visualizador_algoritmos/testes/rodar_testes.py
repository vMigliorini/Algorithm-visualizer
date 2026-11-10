"""Roda todos os testes automáticos (sem abrir janela).

    python testes/rodar_testes.py            # testes por módulo (~1 minuto)
    python testes/rodar_testes.py --completo # inclui a varredura de todos os 158 algoritmos (~2 min)
    FOTOS=capturas python testes/rodar_testes.py   # também salva capturas de tela (PNG)
"""
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
TESTES = ["t_ord", "t_arv", "t_estarv", "t_graf", "t_grafav", "t_grade", "t_back", "t_dp", "t_str", "t_geo",
          "t_est", "t_auto", "t_ia", "t_mat"]
if "--completo" in sys.argv:
    TESTES.append("t_integra")

env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
total_ok = total_falha = 0
for nome in TESTES:
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(AQUI, nome + ".py")], capture_output=True, text=True, env=env)
    linhas = r.stdout.splitlines()
    ok = sum(1 for l in linhas if l.startswith("OK"))
    falhas = [l for l in linhas if l.startswith("FALHA ")]
    quebrou = r.returncode != 0
    total_ok += ok
    total_falha += len(falhas) + (1 if quebrou else 0)
    estado = "OK " if not falhas and not quebrou else "ERRO"
    print(f"[{estado}] {nome:10s} {ok:3d} verificações  ({time.time() - t0:5.1f}s)")
    for l in falhas:
        print("      ", l)
    if quebrou:
        print(r.stderr[-1500:])
print(f"\nTotal: {total_ok} verificações passaram, {total_falha} problema(s).")
sys.exit(1 if total_falha else 0)
