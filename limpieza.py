"""Funciones puras de limpieza y normalización.

Separadas del script de orquestación (procesar_resenas.py) para poder
testearlas sin tocar disco ni CSV real.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

from stopwords_es import STOPWORDS_ES

RATING_MIN, RATING_MAX = 1, 5

# Mapeo de ratings escritos como palabra -> valor numérico. Es el truco más
# sutil del dataset: "cinco" es un rating válido, solo que mal formateado.
RATING_TEXTUAL_A_NUMERO = {
    "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
}

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"  # símbolos y pictogramas variados, emoticones
    "\U00002600-\U000027BF"  # símbolos misceláneos y dingbats
    "\U0001F1E6-\U0001F1FF"  # banderas
    "]+",
    flags=re.UNICODE,
)

# Se conservan letras (con tildes/ñ), dígitos y espacios; todo lo demás
# (puntuación, símbolos, emojis residuales) se reemplaza por espacio.
_CARACTERES_PERMITIDOS = re.compile(r"[^a-z0-9áéíóúñü\s]")
_ESPACIOS_MULTIPLES = re.compile(r"\s+")


def limpiar_texto(texto: Optional[str]) -> str:
    """minúsculas, sin emojis/caracteres especiales, sin espacios redundantes."""
    if texto is None:
        return ""
    t = unicodedata.normalize("NFC", texto).strip().lower()
    t = _EMOJI_PATTERN.sub(" ", t)
    t = _CARACTERES_PERMITIDOS.sub(" ", t)
    t = _ESPACIOS_MULTIPLES.sub(" ", t).strip()
    return t


def tokenizar_para_frecuencia(texto_limpio: str) -> list[str]:
    """Tokeniza texto ya limpio y descarta stopwords / tokens de 1 letra."""
    if not texto_limpio:
        return []
    return [
        tok for tok in texto_limpio.split(" ")
        if tok and tok not in STOPWORDS_ES and len(tok) > 1
    ]


@dataclass
class RatingNormalizado:
    valor: Optional[int]
    valido: bool
    recuperado_de_texto: bool = False
    valor_original: str = ""


def normalizar_rating(raw: Optional[str]) -> RatingNormalizado:
    """Convierte el rating crudo a int 1-5 o marca como inválido.

    Política:
    - "cinco" (y equivalentes uno..cinco) se recupera a su valor numérico.
    - vacío, "N/A", "?", o fuera de rango [1,5] (-1, 0, 6, 7...) -> inválido.
    """
    original = raw if raw is not None else ""
    limpio = original.strip().lower()

    if limpio in RATING_TEXTUAL_A_NUMERO:
        return RatingNormalizado(
            valor=RATING_TEXTUAL_A_NUMERO[limpio],
            valido=True,
            recuperado_de_texto=True,
            valor_original=original,
        )

    try:
        valor = int(limpio)
    except ValueError:
        return RatingNormalizado(valor=None, valido=False, valor_original=original)

    if RATING_MIN <= valor <= RATING_MAX:
        return RatingNormalizado(valor=valor, valido=True, valor_original=original)

    return RatingNormalizado(valor=None, valido=False, valor_original=original)


def clave_duplicado_exacto(usuario: str, fecha: str, rating_raw: str, texto: str) -> tuple:
    """Clave para detectar filas duplicadas (misma reseña re-ingresada).

    Se normaliza el texto (espacios/mayúsculas) antes de comparar, porque el
    truco del dataset incluye duplicados con espacios extra o distinto casing.
    """
    texto_normalizado = _ESPACIOS_MULTIPLES.sub(" ", (texto or "").strip().lower())
    return (usuario.strip(), fecha.strip(), rating_raw.strip(), texto_normalizado)
