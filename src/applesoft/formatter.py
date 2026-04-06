"""Formatage des nombres selon les conventions Applesoft BASIC (RG-0006).

- Espace avant les nombres positifs
- Pas de zéros inutiles
- Notation scientifique au-delà de 9 chiffres
- Pas d'espace avant les nombres négatifs
"""

import math


def format_number(n: float) -> str:
    """Formate un nombre selon les conventions Applesoft.

    Règles (RG-0006) :
    - Les nombres positifs sont précédés d'un espace (signe positif implicite)
    - Les nombres négatifs commencent par '-' sans espace
    - Pas de zéros inutiles après la virgule
    - Notation scientifique si >= 1E9 ou < 0.01 (sauf 0)
    - Le format scientifique utilise E+NN ou E-NN
    """
    if math.isnan(n):
        return " NAN"

    if math.isinf(n):
        return " INF" if n > 0 else "-INF"

    prefix = " " if n >= 0 else ""

    if n == 0:
        return " 0"

    abs_n = abs(n)

    # Notation scientifique pour les très grands ou très petits nombres
    if abs_n >= 1e9 or (abs_n < 0.01 and abs_n != 0):
        return prefix + _format_scientific(n)

    # Entier ?
    if n == int(n) and abs_n < 1e9:
        return prefix + str(int(n))

    # Flottant : pas de zéros inutiles
    result = f"{n:.9g}"
    return prefix + result


def _format_scientific(n: float) -> str:
    """Formate un nombre en notation scientifique Applesoft.

    Format : D.DDDDDDDDE+NN ou D.DDDDDDDDE-NN
    """
    if n == 0:
        return "0"

    sign = "-" if n < 0 else ""
    abs_n = abs(n)

    exp = math.floor(math.log10(abs_n))
    mantissa = abs_n / (10.0**exp)

    # Arrondir la mantisse à 9 chiffres significatifs
    mantissa = round(mantissa, 8)

    # Si l'arrondi fait passer la mantisse à 10
    if mantissa >= 10.0:
        mantissa /= 10.0
        exp += 1

    # Formater la mantisse sans zéros inutiles
    mantissa_str = f"{mantissa:.8f}".rstrip("0").rstrip(".")

    # Formater l'exposant
    exp_sign = "+" if exp >= 0 else "-"
    exp_str = f"{abs(exp):02d}"

    return f"{sign}{mantissa_str}E{exp_sign}{exp_str}"
