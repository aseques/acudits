import json
import re
import sys
from operator import truediv

#FIXME això hauria d'estar en una classa comuna
def adult(text):
    """Identifiquem si el text és o no per adults"""
    maturewords = ['sexe','cardar','polla','viagra']
    #FIXME detectar casos com ampolla on no és un problema
    if any(matureword.lower() in text.lower() for matureword in maturewords):
        return True
    else:
        return False

def formata_text(text):
    """A partir d'un text corregim alguns temes de format que hem vist que estan malament en el text descarregat"""
    result = text.replace('_ ','')
    result = text.replace('\xa0', '')
    #patro = r"(?<=[a-zA-Z])\.(?=[a-zA-Z])" # patrò per detectar el . entre lletres
    #replacement = ".\n"
    #result=re.sub(patro, replacement, result)
    return result

def separa_text(text):
    """A partir d'una llista amb cadenes de text ens torna un dict amb els acudits separats en el format que volem"""
    acudits = []
    acudit = {}
    acudit['link'] = 'https://www.parlacatalana.com/'
    acudit['mature'] = False
    acudit['author'] = 'Unknown'
    acudit['part1'] = ''
    acudit['part2'] = ''
    acudit['tema'] = []

    if isinstance(text, str):
        # Sempre esperem llistes, sinò ho forcem
        text = [ text ]

    tipus_anterior = ''
    for linia in text:
        tipus_linia = None
        if '\n' == linia:
            if tipus_anterior == 'Part1':
                tipus_linia = 'NouAcudit'
            elif tipus_anterior == 'NouAcudit' or tipus_anterior == 'Descarta':
                tipus_linia = 'Descarta'
            else:
                print("Cas no contemplat")
                sys.exit(1)
        else:
            tipus_linia = 'Part1'

        if adult(linia):
            acudit['mature'] = True

        if tipus_linia == 'Descarta':
            # print('Descartem el text: {linia}'.format(linia=linia))
            pass
        elif tipus_linia == 'Part1':
            acudit['part1'] += formata_text(linia)
        elif tipus_linia == 'NouAcudit':
            acudits.append(acudit.copy())
            acudit['link'] = 'https://www.parlacatalana.com/'
            acudit['mature'] = False
            acudit['author'] = 'Unknown'
            acudit['part1'] = ''
            acudit['part2'] = ''
            acudit['tema'] = []
        tipus_anterior=tipus_linia
    # Afegim l'acudit actual a la llista dels que guardem
    if acudit['part1']:
        acudits.append(acudit.copy())

    return acudits


# Ruta al fitxer TXT
file_path = 'parlacat_out.txt'
acudits = []

# Carregar el fitxer en memòria

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        missatges = file.readlines()
        print("Fitxer carregat correctament!")
except FileNotFoundError:
    print(f"El fitxer {file_path} no existeix.")


acudits.extend(separa_text(missatges))

# Exemple d'accés a les dades (si el JSON conté un diccionari)
print("Dades carregades:", missatges)

with open('sortida.json', 'w', encoding='utf-8') as f:
    json.dump(acudits, f, ensure_ascii=False, indent=4)

print("Tenim un total de {total} acudits".format(total=len(acudits)))
