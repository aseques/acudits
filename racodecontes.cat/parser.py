#!/usr/bin/env python3

"""
Codi per extreure els acudits de la pàgina de https://racodecontes.cat descarregada per export.py
"""

import json
import os
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comu import adult  # noqa: E402

URL = 'https://racodecontes.cat/acudits-en-catala/'
fitxer = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html', 'acudits-en-catala.html')

if not os.path.exists(fitxer):
    sys.exit("No hi ha la pàgina descarregada, executa primer export.py")

with open(fitxer, 'r', encoding='utf-8') as f:
    sopa = BeautifulSoup(f.read(), 'html.parser')

acudits = []
# Els acudits són els paràgrafs del bloc de text de la pàgina, un acudit per <p> i un <br> per línia
for bloc in sopa.find_all('div', class_='wpb_text_column'):
    for paragraf in bloc.find_all('p'):
        for br in paragraf.find_all('br'):
            br.replace_with('\n')
        part1 = '\n'.join(linia.strip() for linia in paragraf.get_text().splitlines() if linia.strip())
        if not part1:
            continue
        acudits.append({
            'link': URL,
            'mature': adult(part1),
            'author': 'Unknown',
            'part1': part1,
            'part2': '',
            # La web és de recursos infantils, tots els acudits són per a nens
            'tema': ['#nens'],
        })

with open('sortida.json', 'w', encoding='utf-8') as f:
    json.dump(acudits, f, ensure_ascii=False, indent=4)

print("Tenim un total de {total} acudits".format(total=len(acudits)))
