#!/usr/bin/env python3

"""
Codi per extreure els acudits a partir del volcat de https://t.me/acudits
"""

import json

def adult(text):
    """Identifiquem si el text és o no per adults"""
    maturewords = ['sexe','cardar','polla','viagra']
    #FIXME detectar casos com ampolla on no és un problema
    if any(matureword.lower() in text.lower() for matureword in maturewords):
        return True
    else:
        return False

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

def es_separador(linia):
    """Una línia feta només d'asteriscs separa dos acudits dins del mateix missatge"""
    linia = linia.strip()
    return linia != '' and linia.strip('*') == ''

def es_peu(text):
    """Textos fixos del canal (avisos, peus, enllaços) que no formen part de l'acudit"""
    return ('Avís: ' in text or 'Acudits anglès' in text or '👉' in text
            or text.lstrip().startswith('Cada cop que comparteixes'))

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

    def tanca():
        acudit['part1'] = acudit['part1'].strip()
        if acudit['part1']:
            acudit['mature'] = acudit['mature'] or adult(acudit['part1'])
            acudits.append(acudit)

    def afegeix(contingut):
        nonlocal acudit, estat
        for linia in contingut.splitlines(keepends=True):
            if es_separador(linia):
                estat = 'nou'
            elif estat == 'meta' or (estat == 'nou' and not linia.strip()):
                pass
            else:
                if estat == 'nou' and acudit['part1'].strip():
                    tanca()
                    acudit = nou_acudit()
                estat = 'cos'
                acudit['part1'] += linia

    for linia in text:
        if isinstance(linia, str):
            if not es_peu(linia):
                afegeix(linia)
        elif isinstance(linia, dict):
            if linia['type'] == 'hashtag':
                acudit['tema'].append(linia['text'])
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
        if 'photo' in missatge:
            # Les imatges amb text al peu tampoc les guardem com a acudits (falta el context)
            pass
        elif 'media_type' in missatge and (missatge['media_type'] == "video_file" or missatge['media_type'] == "sticker" ):
            # El missatge és un gif o sticker, no el fem servir com a acudit
            pass
        else:
            text = missatge['text']
            acudits.extend(separa_text(text))
            #print(acudits)

# Exemple d'accés a les dades (si el JSON conté un diccionari)
print("Dades carregades:", missatges)

with open('sortida.json', 'w', encoding='utf-8') as f:
    json.dump(acudits, f, ensure_ascii=False, indent=4)

print("Tenim un total de {total} acudits".format(total=len(acudits)))
