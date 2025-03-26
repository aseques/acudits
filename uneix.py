"""
Preparem el fitxer de sortida unint les colleccions d'acudits que tenim
"""

import os
import json


def trobar_i_unir_json(directori_principal, fitxer_sortida="unificat.json"):
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

    with open(fitxer_sortida, "w", encoding="utf-8") as f_out:
        json.dump(dades_unificades, f_out, indent=4, ensure_ascii=False)

    print(f"Fitxer unificat creat: {fitxer_sortida}")


# Exemple d'ús
directori_principal = "."  # Canvia això per la carpeta on buscar

# Executar la funció
trobar_i_unir_json(directori_principal)
