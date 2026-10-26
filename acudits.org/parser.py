#!/usr/bin/env python3

"""
Codi per extreure els acudits de les pàgines de https://www.acudits.org descarregades per export.py
"""

import glob
import json
import os
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comu import adult  # noqa: E402

URL_BASE = 'https://www.acudits.org/'
# Tema que posem als acudits de cada categoria
TEMES = {
    'acudits-per-a-nens': '#nens',
    'acudits-ximples': '#ximples',
    'acudits-de-familia-i-nens': '#família',
    'acudits-per-a-adults': '#adults',
}

acudits = []
fitxers = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html', '*.html')))
if not fitxers:
    sys.exit("No hi ha pàgines descarregades, executa primer export.py")

for fitxer in fitxers:
    categoria = os.path.basename(fitxer).rsplit('-', 1)[0]
    with open(fitxer, 'r', encoding='utf-8') as f:
        sopa = BeautifulSoup(f.read(), 'html.parser')

    for article in sopa.find_all('article', class_='list-item'):
        text = article.find('span', class_='descripcionShortListLabel')
        if text is None:
            continue
        # Cada <br> és un salt de línia del diàleg, però l'HTML ja porta un salt abans del <br />,
        # així que ens quedem només amb les línies que tenen text
        for br in text.find_all('br'):
            br.replace_with('\n')
        part1 = '\n'.join(linia.strip() for linia in text.get_text().splitlines() if linia.strip())
        if not part1:
            continue
        enllac = article.find('a', class_='shareIconHyperlink')
        acudits.append({
            # Cada acudit té la seva pàgina, l'enllaç és relatiu (../../../c/...)
            'link': URL_BASE + enllac['href'].lstrip('./') if enllac else URL_BASE,
            'mature': categoria == 'acudits-per-a-adults' or adult(part1),
            'author': 'Unknown',
            'part1': part1,
            'part2': '',
            'tema': [TEMES[categoria]] if categoria in TEMES else [],
        })

with open('sortida.json', 'w', encoding='utf-8') as f:
    json.dump(acudits, f, ensure_ascii=False, indent=4)

print("Tenim un total de {total} acudits".format(total=len(acudits)))
