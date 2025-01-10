import json
from operator import truediv


def adult(text):
    """Identifiquem si el text és o no per adults"""
    maturewords = ['sexe','cardar']
    if any(matureword.lower() in text.lower() for matureword in maturewords):
        return True
    else:
        return False

def separa_text(text):
    """A partir d'una llista amb cadenes de text ens torna un dict amb els acudits separats en el format que volem"""
    acudits = []
    acudit = {}
    acudit['link'] = 'https://t.me/acudits'
    acudit['mature'] = False
    acudit['author'] = 'Unknown'
    acudit['part1'] = ''
    acudit['part2'] = ''
    acudit['tema'] = []
    if isinstance(text, list) and len(text) > 1 and isinstance(text[1], dict) and text[1]['type'] and text[1]['type'] == 'spoiler':
        acudit['mature'] = True
        text[0] = text[1]['text']
    if isinstance(text, str):
        text = [ text ]
    for linia in text:
        tipus_linia = None
        if isinstance(linia, str):
            # La línia pot ser un string
            if 'Avís: ' in linia:
                tipus_linia = 'Descarta'
            elif acudit['part1'] == '':
                tipus_linia = 'Part1'
            elif acudit['part1'] != '':
                tipus_linia = 'NouAcudit'
            if adult(linia):
                acudit['mature'] = True
        elif isinstance(linia, dict):
            if linia['type'] == 'hashtag':
                acudit['tema'].append(linia['text'])
                if adult(linia['text']):
                    acudit['mature'] = True
            elif linia['type'] == 'bold':
                # negretes, normalment per marcar salts (encara que a vegades es fa servir per acudits multilingues),
                # de moment descartem sempre
                tipus_linia = 'Descarta'
            elif linia['type'] == 'link':
                # Link cap a l'autor de l'acudit
                acudit['author'] = linia['text']
            elif linia['type'] == 'mention':
                # Mencions a usuaris o canals
                tipus_linia = 'Descarta'
            else:
                print(linia['text'])
        else:
            print('Tipus no tractat')

        if tipus_linia == 'Descarta':
            # print('Descartem el text: {linia}'.format(linia=linia))
            pass
        elif tipus_linia == 'Part1':
            acudit['part1'] = linia.rstrip()
        elif tipus_linia == 'NouAcudit':
            acudits.append(acudit.copy())
            acudit['link'] = "https://t.me/acudits"
            acudit['mature'] = False
            acudit['author'] = 'Unknown'
            acudit['part1'] = ''
            acudit['part2'] = ''
            acudit['tema'] = []
    # Afegim l'acudit actual a la llista dels que guardem
    if acudit['part1']:
        acudits.append(acudit.copy())

    return acudits


# Ruta al fitxer JSON
file_path = 'result-clean.json'
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
        elif 'media_type' in missatge and missatge['media_type'] == "video_file":
            # El missatge és un gif, no el fem servir com a acudit
            pass
        else:
            text = missatge['text']
            acudits.extend(separa_text(text))
            #print(acudits)

# Exemple d'accés a les dades (si el JSON conté un diccionari)
print("Dades carregades:", missatges)

with open('sortida.json', 'w', encoding='utf-8') as f:
    json.dump(acudits, f, ensure_ascii=False, indent=4)
