#!/usr/bin/env python3

"""
Descarreguem la pàgina d'acudits de https://racodecontes.cat a html/ perquè el parser la pugui llegir

S'executa a mà quan volem actualitzar els acudits, uneix.py només executa el parser
"""

import os

import requests

URL = 'https://racodecontes.cat/acudits-en-catala/'
DIRECTORI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html')

os.makedirs(DIRECTORI, exist_ok=True)

resposta = requests.get(URL, timeout=30)
resposta.raise_for_status()
fitxer = os.path.join(DIRECTORI, 'acudits-en-catala.html')
with open(fitxer, 'w', encoding='utf-8') as f:
    f.write(resposta.text)
print(f'Desat {fitxer}')
