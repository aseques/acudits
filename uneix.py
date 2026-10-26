#!/usr/bin/env python3
"""
Preparem el fitxer de sortida unint les colleccions d'acudits que tenim
"""

import os
import re
import sys
import json
import subprocess


def executa_parsers(directori_principal):
    """Executem els parser.py dels subdirectoris perquè regenerin el seu sortida.json"""
    for arrel, subdirs, fitxers in os.walk(directori_principal):
        for fitxer in sorted(fitxers):
            if fitxer == "parser.py":
                print(f"Executant {os.path.join(arrel, fitxer)}")
                # Cada parser llegeix i escriu fitxers relatius al seu directori
                resultat = subprocess.run([sys.executable, fitxer], cwd=arrel, capture_output=True, text=True)
                if resultat.returncode != 0:
                    print(resultat.stdout[-2000:], resultat.stderr, sep="\n")
                    sys.exit(f"Ha fallat {os.path.join(arrel, fitxer)}")
                print(resultat.stdout.strip().splitlines()[-1])


# Atribucions a personatges: volem acudits, no cites
NOM = r"[A-ZÀ-Ú][\w'’-]+"
NOMS = rf"(?:{NOM}[ \t]+){{1,3}}{NOM}"
CITA = re.compile(
    rf"\({NOMS}\)"                          # (Gary Delaney)
    rf"|[\"”’']\.?\s*\({NOM}\)"             # "...". (Cantinflas)
    rf"|~\s*{NOMS}\.?\s*(?:\(.*\))?\s*$"    # ~ Abraham Lincoln
    rf"|[—–-]\s*{NOMS}\s*$"                 # —Mark Twain (sense punt final, els diàlegs en porten)
    rf"|[\"”’'](?:[.,][ \t]*|[ \t]+)(?:[—–-][ \t]*)?{NOMS}\.?[ \t]*$",  # "..." —Herbert Hoober. / '...', Mark Twain.
    re.M)


def treu_cites(acudits):
    """Eliminem els acudits que són cites atribuïdes a algun personatge"""
    sense_cites = [acudit for acudit in acudits if not CITA.search(acudit["part1"])]
    print(f"Hem tret {len(acudits) - len(sense_cites)} cites de personatges")
    return sense_cites


def clau_acudit(text):
    """Text normalitzat per comparar acudits: minúscules i sense puntuació, emojis ni espais repetits"""
    return re.sub(r"\W+", " ", text.lower()).strip()


def deduplica(acudits):
    """Treiem els acudits repetits, ens quedem el primer però ajuntem els temes i la marca d'adults"""
    unics = {}
    for acudit in acudits:
        clau = clau_acudit(acudit["part1"])
        if clau not in unics:
            unics[clau] = acudit
        else:
            original = unics[clau]
            original["mature"] = original["mature"] or acudit["mature"]
            original["tema"] += [tema for tema in acudit.get("tema", []) if tema not in original["tema"]]
    print(f"Hem tret {len(acudits) - len(unics)} acudits repetits")
    return list(unics.values())


def trobar_i_unir_json(directori_principal, fitxer_sortida="acudits.json"):
    dades_unificades = []

    for arrel, subdirs, fitxers in os.walk(directori_principal):
        if "sortida.json" in fitxers:
            cami_complet = os.path.join(arrel, "sortida.json")
            try:
                with open(cami_complet, "r", encoding="utf-8") as f:
                    dades = json.load(f)
                    if isinstance(dades, list):
                        dades_unificades.extend(dades)
                    else:
                        dades_unificades.append(dades)
            except Exception as e:
                print(f"No s'ha pogut llegir {cami_complet}: {e}")

    dades_unificades = treu_cites(dades_unificades)
    dades_unificades = deduplica(dades_unificades)

    with open(fitxer_sortida, "w", encoding="utf-8") as f_out:
        json.dump(dades_unificades, f_out, indent=4, ensure_ascii=False)

    print(f"Fitxer unificat creat: {fitxer_sortida}")
    return dades_unificades


def genera_txt(acudits, fitxer_sortida="acudits.txt"):
    """Fitxer de text amb els acudits que no són per adults, un per línia

    Una línia per acudit perquè es pugui triar un a l'atzar amb shuf -n 1 (ho fem servir des de Home Assistant)
    """
    # Unim les línies de cada acudit amb un espai i traiem els espais repetits
    aptes = [" ".join(acudit["part1"].split()) for acudit in acudits if not acudit["mature"]]
    with open(fitxer_sortida, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(aptes) + "\n")
    print(f"Fitxer de text creat: {fitxer_sortida} ({len(aptes)} acudits)")


# Exemple d'ús
directori_principal = "."  # Canvia això per la carpeta on buscar

# Executar les funcions
executa_parsers(directori_principal)
acudits = trobar_i_unir_json(directori_principal)
genera_txt(acudits)
