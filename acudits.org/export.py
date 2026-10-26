#!/usr/bin/env python3

"""
Descarreguem les pàgines de categories de https://www.acudits.org a html/ perquè el parser les pugui llegir

S'executa a mà quan volem actualitzar els acudits, uneix.py només executa el parser
"""

import os
import re
import time

import requests

URL_BASE = 'https://www.acudits.org'
# La categoria 5 (20 acudits aleatoris) repeteix acudits de les altres, no la descarreguem
CATEGORIES = [
    'b/2/acudits-per-a-nens/',
    'b/6/acudits-ximples/',
    'b/7/acudits-de-familia-i-nens/',
    'b/9/acudits-per-a-adults/',
]
DIRECTORI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html')
# Per no carregar el servidor, esperem entre peticions
ESPERA = 1

os.makedirs(DIRECTORI, exist_ok=True)

for categoria in CATEGORIES:
    nom = categoria.split('/')[2]
    pagina = 1
    while True:
        url = f'{URL_BASE}/{categoria}?pageNum={pagina}'
        resposta = requests.get(url, timeout=30)
        resposta.raise_for_status()
        if 'descripcionShortListLabel' not in resposta.text:
            # Hem passat de l'última pàgina
            break
        fitxer = os.path.join(DIRECTORI, f'{nom}-{pagina:03}.html')
        with open(fitxer, 'w', encoding='utf-8') as f:
            f.write(resposta.text)
        print(f'Desat {fitxer}')
        # Si no hi ha enllaç a la pàgina següent, era l'última
        if not re.search(rf'pageNum={pagina + 1}\b', resposta.text):
            break
        pagina += 1
        time.sleep(ESPERA)
