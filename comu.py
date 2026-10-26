"""
Codi comú als parsers de les diferents fonts d'acudits

Els parser.py s'executen des del seu directori, per importar-lo cal afegir el directori pare al path:

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from comu import adult
"""

import re

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
