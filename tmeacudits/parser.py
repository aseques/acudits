#!/usr/bin/env python3

"""
Codi per extreure els acudits a partir del volcat de https://t.me/acudits
"""

import json
import os
import re
import unicodedata

# Paraules senceres (\b) per no confondre "polla" amb "ampolla" o "follar" amb "follet"
PARAULES_ADULTS = re.compile(
    r"\b("
    r"sex(e|es|ual\w*|y)|cardar\w*|foll(ar|ant|at|ada|en|es|o|a|em|eu)|polla|polles|viagra"
    r"|cond[oó]n?s?|preservatius?|p[eè]nis|vagin\w*|cony|collons|orgasm\w*|porno\w*|put[ao]s?"
    r"|masturb\w*|erecci\w*|mamad\w*|prostitu\w*|cl[ií]toris|testicles?|semen|esperma\w*"
    r")\b",
    re.IGNORECASE)

def adult(text):
    """Identifiquem si el text és o no per adults"""
    return PARAULES_ADULTS.search(text) is not None

def nou_acudit():
    """Retorna un acudit buit amb els valors per defecte"""
    return {
        'link': 'https://t.me/acudits',
        'mature': False,
        'author': 'Unknown',
        'part1': '',
        'part2': '',
        'tema': [],
    }

def es_asteriscs(linia):
    """Una línia feta només d'asteriscs separa dos acudits dins del mateix missatge"""
    linia = linia.strip()
    return linia != '' and linia.strip('*') == ''

def es_emojis(linia):
    """Línia feta només d'emojis (🎄, ⛄️...), separa acudits si va entre línies en blanc"""
    linia = linia.strip()
    # So: símbols i emojis, Mn/Cf: modificadors dels emojis (U+FE0F, ZWJ), Zs: espais entre emojis
    return linia != '' and all(unicodedata.category(c) in ('So', 'Sk', 'Mn', 'Cf', 'Zs') for c in linia)

def es_peu(text):
    """Textos fixos del canal (avisos, peus, enllaços) que no formen part de l'acudit"""
    return ('Avís: ' in text or 'Acudits anglès' in text or '👉' in text
            or text.lstrip().startswith('Cada cop que comparteixes')
            or 'Especial Acudits' in text or "Festival de l'humor" in text)

def separa_text(text):
    """A partir d'una llista amb cadenes de text ens torna un dict amb els acudits separats en el format que volem

    Telegram trenca el text d'un missatge en trossos cada cop que hi ha un format (cursiva, negreta, codi...),
    així que primer refem el text i només el tallem pels separadors d'asteriscs.
    """
    if isinstance(text, str):
        # Sempre esperem llistes, sinò ho forcem
        text = [text]

    acudits = []
    acudit = nou_acudit()
    # 'cos': afegim text a l'acudit, 'meta': ja han sortit hashtags/mencions i el text que ve és peu,
    # 'nou': hem trobat un separador i el següent text és un nou acudit
    estat = 'nou'
    # Última línia sencera que hem vist, per saber si un emoji va entre línies en blanc
    anterior = '\n'
    # Un 🔞 en una línia separadora marca com a adults l'acudit que ve
    pendent_adult = False
    # Els acudits dels especials de Cap d'any no porten hashtags, els marquem nosaltres
    text_pla = ''.join(tros if isinstance(tros, str) else tros['text'] for tros in text)
    especial_nadal = "Especial Acudits de Cap d'any" in text_pla

    def tanca():
        acudit['part1'] = acudit['part1'].strip()
        if acudit['part1']:
            acudit['mature'] = acudit['mature'] or adult(acudit['part1']) or '🔞' in acudit['part1']
            if especial_nadal and '#nadal' not in acudit['tema']:
                acudit['tema'].append('#nadal')
            acudits.append(acudit)

    def afegeix(contingut):
        nonlocal acudit, estat, anterior, pendent_adult
        linies = contingut.splitlines(keepends=True)
        for i, linia in enumerate(linies):
            entre_blanques = (anterior.endswith('\n') and not anterior.strip()
                              and i + 1 < len(linies) and not linies[i + 1].strip())
            if es_asteriscs(linia) or (es_emojis(linia) and entre_blanques):
                estat = 'nou'
                pendent_adult = pendent_adult or '🔞' in linia
            elif estat == 'meta' or (estat == 'nou' and not linia.strip()):
                pass
            else:
                if estat == 'nou' and acudit['part1'].strip():
                    tanca()
                    acudit = nou_acudit()
                if pendent_adult:
                    acudit['mature'] = True
                    pendent_adult = False
                estat = 'cos'
                acudit['part1'] += linia
            # Si el tros no acaba en salt de línia, la línia continua al següent tros
            anterior = linia if linia.endswith('\n') or i + 1 < len(linies) else anterior + linia

    for linia in text:
        if isinstance(linia, str):
            if not es_peu(linia):
                afegeix(linia)
        elif isinstance(linia, dict):
            if linia['type'] == 'hashtag':
                # Unifiquem les variants del mateix tema (#Nadal i #nadal)
                tema = '#nadal' if linia['text'].lower() == '#nadal' else linia['text']
                if tema not in acudit['tema']:
                    acudit['tema'].append(tema)
                if adult(linia['text']):
                    acudit['mature'] = True
                estat = 'meta' if estat == 'cos' else estat
            elif linia['type'] == 'mention':
                # Mencions a usuaris o canals
                estat = 'meta' if estat == 'cos' else estat
            elif linia['type'] == 'link':
                # Link cap a l'autor de l'acudit
                acudit['author'] = linia['text']
            elif linia['type'] == 'spoiler':
                # El text amagat és l'acudit, el que hi ha abans és l'avís de contingut per adults
                acudit['mature'] = True
                acudit['part1'] = ''
                estat = 'cos'
                afegeix(linia['text'])
            elif not es_peu(linia['text']):
                # Formats dins del text (cursiva, negreta, codi...)
                afegeix(linia['text'])
        else:
            print('Tipus no tractat')

    # Afegim l'acudit actual a la llista dels que guardem
    tanca()

    return acudits


def normalitza(text):
    """Text amb els espais i salts de línia reduïts a un sol espai, per comparar fragments"""
    return ' '.join(text.split())

def carrega_exclosos(fitxer):
    """Llegim el que no són acudits (una entrada per línia, # per comentaris)

    Un número és l'id d'un missatge sencer que descartem, qualsevol altre text és un fragment:
    descartem els acudits que el contenen (per missatges amb molts acudits on només en sobra un)
    """
    ids = set()
    textos = []
    with open(fitxer, 'r', encoding='utf-8') as f:
        for linia in f:
            linia = linia.split('#')[0].strip()
            if linia.isdigit():
                ids.add(int(linia))
            elif linia:
                textos.append(normalitza(linia))
    return ids, textos


exclosos, textos_exclosos = carrega_exclosos(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exclosos.txt'))

# Ruta al fitxer JSON amb el fitxer normalitzat (via comandes en bash)
file_path = '/home/aseques/src/acudits/tmeacudits/result-clean.json'
acudits = []

# Carregar el fitxer JSON en memòria
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print("Fitxer carregat correctament!")
except FileNotFoundError:
    print(f"El fitxer {file_path} no existeix.")
except json.JSONDecodeError as e:
    print(f"Error al parsejar el fitxer JSON: {e}")

missatges = data['messages']

for missatge in missatges:
    if missatge['type'] == 'message':
        if missatge['id'] in exclosos:
            # Missatges marcats a mà com a no acudits (publicitat, notícies...)
            pass
        elif 'photo' in missatge:
            # Les imatges amb text al peu tampoc les guardem com a acudits (falta el context)
            pass
        elif missatge.get('media_type') in ("video_file", "sticker", "animation"):
            # El missatge és un vídeo, sticker o gif, el text sense la imatge no s'entén
            pass
        else:
            text = missatge['text']
            acudits.extend(acudit for acudit in separa_text(text)
                           if not any(fragment in normalitza(acudit['part1']) for fragment in textos_exclosos))
            #print(acudits)

# Exemple d'accés a les dades (si el JSON conté un diccionari)
print("Dades carregades:", missatges)

with open('sortida.json', 'w', encoding='utf-8') as f:
    json.dump(acudits, f, ensure_ascii=False, indent=4)

print("Tenim un total de {total} acudits".format(total=len(acudits)))
