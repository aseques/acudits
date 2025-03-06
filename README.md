Recopilatori d'acudits en català de lliure distribució, es poden fer servir amb utilitats
tipus un acudit al dia o amb assistents de veu.

Format ideas from [here](https://github.com/kylecs/jokes-dataset-json)

Els primers acudits els he tret del canal de telegram d'acudits https://t.me/acudits, fent una exportació en format json
per poder tractar milllor els resultats, partim del fitxer result.json que genera el volcat del telegram

Hem de treure el caràcter NSBP que apareix en el volcat de telegram

    perl -pe 's/\xc2\xa0//g' result.json > result-clean.json
    sed -r --in-place $'s/\u200e//g' result-clean.json

Per convertir des del format exportat del json del telegram al format que farem servir. Un manual força bo de jq
[aquí](https://shapeshed.com/jq-json/)

    jq '.messages[]| select(.type == "message").text' result.json > filtre.json


Més acudits aquí
https://www.parlacatalana.com/2020/07/acudits-en-catala.html
https://www.facebook.com/groups/acuditsencatala/?locale=ca_ES
https://jozeiko.wordpress.com/acudits-dolents-de-collons/
https://www.racocatala.cat/forums/fil/64859/acudits-curts?pag=12