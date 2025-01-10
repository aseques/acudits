Recopilatori d'acudits en català de lliure distribució, es poden fer servir amb utilitats
tipus un acudit al dia o amb assistents de veu.

Format ideas from [here|https://github.com/kylecs/jokes-dataset-json]


Els primers acudits els he tret del canal de telegram d'acudits https://t.me/acudits

Hem de treure el caràcter NSBP que apareix en el volcat de telegram

    perl -pe 's/\xc2\xa0//g' result.json > result-clean.json
    sed -r --in-place $'s/\u200e//g' result-clean.json

Per convertir des del format exportat del json del telegram al format que farem servir. Un manual força bo de jq [aquí|https://shapeshed.com/jq-json/]

    jq '.messages[]| select(.type == "message").text' result.json > filtre.json
