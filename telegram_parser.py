import json

def separa_text(text):
    """A partir d'una llista amb cadenes de text ens torna un dict amb els acudits separats en el format que volem"""
    acudits=[]
    acudit = {}
    acudit['link'] = 'https://t.me/acudits'
    acudit['mature'] = False
    acudit['author'] = 'Unknown'
    acudit['part1'] = ''
    acudit['part2'] = ''
    acudit['tema'] = []
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
        elif isinstance(linia, dict):
            if linia['type'] == 'hashtag':
                acudit['tema'].append(linia['text'])
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
            print('Descartem el text: {linia}'.format(linia=linia))
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


    return acudits

# Ruta al fitxer JSON
file_path = 'result-clean.json'

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
        text = missatge['text']
        acudits = separa_text(text)
        print(acudits)

# Exemple d'accés a les dades (si el JSON conté un diccionari)
print("Dades carregades:", missatges)
